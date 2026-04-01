import type { MortgageInputs, MortgageResults } from "@/types/mortgage";
import {
  STRESS_TEST_FLOOR,
  STRESS_TEST_BUFFER,
  MAX_GDS_RATIO,
  MAX_TDS_RATIO,
  DEFAULT_MONTHLY_PROPERTY_TAX,
  DEFAULT_MONTHLY_HEATING,
  CMHC_PRICE_CEILING,
  CMHC_PREMIUM_TIERS,
  DOWN_PAYMENT_FIRST_TIER_LIMIT,
  DOWN_PAYMENT_FIRST_TIER_RATE,
  DOWN_PAYMENT_SECOND_TIER_RATE,
  DOWN_PAYMENT_CONVENTIONAL_RATE,
} from "@/lib/constants/canadian-mortgage";

/**
 * Convert annual rate to effective monthly rate using Canadian semi-annual compounding.
 */
function toMonthlyRate(annualRatePercent: number): number {
  const semiAnnualRate = annualRatePercent / 100 / 2;
  const effectiveAnnual = Math.pow(1 + semiAnnualRate, 2) - 1;
  return Math.pow(1 + effectiveAnnual, 1 / 12) - 1;
}

/**
 * Get the stress test qualifying rate.
 */
function getStressTestRate(contractRate: number): number {
  return Math.max(contractRate + STRESS_TEST_BUFFER, STRESS_TEST_FLOOR);
}

/**
 * Calculate the minimum required down payment for a given home price.
 */
function calcMinimumDownPayment(homePrice: number): number {
  if (homePrice > 1_000_000) {
    return homePrice * DOWN_PAYMENT_CONVENTIONAL_RATE;
  }
  if (homePrice <= DOWN_PAYMENT_FIRST_TIER_LIMIT) {
    return homePrice * DOWN_PAYMENT_FIRST_TIER_RATE;
  }
  return (
    DOWN_PAYMENT_FIRST_TIER_LIMIT * DOWN_PAYMENT_FIRST_TIER_RATE +
    (homePrice - DOWN_PAYMENT_FIRST_TIER_LIMIT) * DOWN_PAYMENT_SECOND_TIER_RATE
  );
}

/**
 * Calculate CMHC insurance premium.
 */
function calcCMHCPremium(
  homePrice: number,
  downPayment: number
): { rate: number; amount: number } {
  const downPaymentPercent = (downPayment / homePrice) * 100;

  if (downPaymentPercent >= 20 || homePrice > CMHC_PRICE_CEILING) {
    return { rate: 0, amount: 0 };
  }

  const tier = CMHC_PREMIUM_TIERS.find(
    (t) => downPaymentPercent >= t.minPercent && downPaymentPercent <= t.maxPercent
  );

  const mortgageAmount = homePrice - downPayment;
  const premiumRate = tier?.premium ?? 0;
  return { rate: premiumRate, amount: mortgageAmount * (premiumRate / 100) };
}

/**
 * Calculate monthly mortgage payment.
 */
function calcMonthlyPayment(
  principal: number,
  annualRatePercent: number,
  amortizationYears: number
): number {
  const monthlyRate = toMonthlyRate(annualRatePercent);
  const numPayments = amortizationYears * 12;

  if (monthlyRate === 0) return principal / numPayments;

  return (
    (principal * monthlyRate * Math.pow(1 + monthlyRate, numPayments)) /
    (Math.pow(1 + monthlyRate, numPayments) - 1)
  );
}

/**
 * Back-calculate the max mortgage principal from a max monthly payment.
 */
function calcMaxPrincipal(
  maxMonthlyPayment: number,
  annualRatePercent: number,
  amortizationYears: number
): number {
  const monthlyRate = toMonthlyRate(annualRatePercent);
  const numPayments = amortizationYears * 12;

  if (monthlyRate === 0) return maxMonthlyPayment * numPayments;

  return (
    (maxMonthlyPayment * (Math.pow(1 + monthlyRate, numPayments) - 1)) /
    (monthlyRate * Math.pow(1 + monthlyRate, numPayments))
  );
}

/**
 * Calculate the maximum affordable home price using iterative approach.
 */
function calcMaxHomePrice(
  inputs: MortgageInputs,
  monthlyPropertyTax: number,
  monthlyHeating: number
): number {
  const monthlyGrossIncome = inputs.annualGrossIncome / 12;
  const stressTestRate = getStressTestRate(inputs.interestRate);

  // Max payment from GDS constraint
  const maxGDSPayment =
    monthlyGrossIncome * MAX_GDS_RATIO - monthlyPropertyTax - monthlyHeating;

  // Max payment from TDS constraint
  const maxTDSPayment =
    monthlyGrossIncome * MAX_TDS_RATIO -
    monthlyPropertyTax -
    monthlyHeating -
    inputs.monthlyDebts;

  const maxPayment = Math.min(maxGDSPayment, maxTDSPayment);

  if (maxPayment <= 0) return 0;

  // Back-calculate max principal at stress test rate
  const maxPrincipal = calcMaxPrincipal(
    maxPayment,
    stressTestRate,
    inputs.amortizationYears
  );

  // Iterative solver to account for CMHC premium
  let maxHome = maxPrincipal + inputs.downPayment;

  for (let i = 0; i < 10; i++) {
    const cmhc = calcCMHCPremium(maxHome, inputs.downPayment);
    const effectivePrincipal =
      cmhc.rate > 0 ? maxPrincipal / (1 + cmhc.rate / 100) : maxPrincipal;
    const newMaxHome = effectivePrincipal + inputs.downPayment;

    if (Math.abs(newMaxHome - maxHome) < 1) break;
    maxHome = newMaxHome;
  }

  return Math.floor(maxHome);
}

/**
 * Main pre-approval calculation.
 */
export function calculatePreApproval(inputs: MortgageInputs): MortgageResults {
  const monthlyPropertyTax = DEFAULT_MONTHLY_PROPERTY_TAX;
  const monthlyHeating = DEFAULT_MONTHLY_HEATING;
  const monthlyGrossIncome = inputs.annualGrossIncome / 12;
  const stressTestRate = getStressTestRate(inputs.interestRate);

  // Down payment checks
  const minimumDownPayment = calcMinimumDownPayment(inputs.homePrice);
  const downPaymentSufficient = inputs.downPayment >= minimumDownPayment;
  const downPaymentPercent = (inputs.downPayment / inputs.homePrice) * 100;

  // Mortgage amount and CMHC
  const baseMortgage = inputs.homePrice - inputs.downPayment;
  const cmhc = calcCMHCPremium(inputs.homePrice, inputs.downPayment);
  const totalMortgageWithInsurance = baseMortgage + cmhc.amount;

  // Monthly payment at actual contract rate (what they'd actually pay)
  const monthlyMortgagePayment = calcMonthlyPayment(
    totalMortgageWithInsurance,
    inputs.interestRate,
    inputs.amortizationYears
  );

  // Qualification check at stress test rate
  const stressTestMonthlyPayment = calcMonthlyPayment(
    totalMortgageWithInsurance,
    stressTestRate,
    inputs.amortizationYears
  );

  // GDS and TDS at stress test rate
  const gdsRatio =
    (stressTestMonthlyPayment + monthlyPropertyTax + monthlyHeating) /
    monthlyGrossIncome;

  const tdsRatio =
    (stressTestMonthlyPayment +
      monthlyPropertyTax +
      monthlyHeating +
      inputs.monthlyDebts) /
    monthlyGrossIncome;

  const gdsPass = gdsRatio <= MAX_GDS_RATIO;
  const tdsPass = tdsRatio <= MAX_TDS_RATIO;

  // Max affordable home
  const maxHomePrice = calcMaxHomePrice(inputs, monthlyPropertyTax, monthlyHeating);

  const totalMonthlyHousingCost =
    monthlyMortgagePayment + monthlyPropertyTax + monthlyHeating;

  return {
    maxHomePrice,
    qualifiesForRequestedPrice: gdsPass && tdsPass && downPaymentSufficient,
    monthlyMortgagePayment: Math.round(monthlyMortgagePayment * 100) / 100,
    monthlyPropertyTax,
    monthlyHeating,
    totalMonthlyHousingCost: Math.round(totalMonthlyHousingCost * 100) / 100,
    gdsRatio: Math.round(gdsRatio * 10000) / 100, // as percentage
    tdsRatio: Math.round(tdsRatio * 10000) / 100,
    gdsPass,
    tdsPass,
    cmhcRequired: cmhc.rate > 0,
    cmhcPremiumPercent: cmhc.rate,
    cmhcPremiumAmount: Math.round(cmhc.amount * 100) / 100,
    totalMortgageWithInsurance: Math.round(totalMortgageWithInsurance * 100) / 100,
    mortgageAmount: baseMortgage,
    downPaymentPercent: Math.round(downPaymentPercent * 100) / 100,
    minimumDownPayment,
    downPaymentSufficient,
    stressTestRate,
  };
}
