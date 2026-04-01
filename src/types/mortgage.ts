export interface MortgageInputs {
  annualGrossIncome: number;
  monthlyDebts: number;
  homePrice: number;
  downPayment: number;
  interestRate: number; // annual percentage, e.g. 5.5
  amortizationYears: number; // 25 or 30
}

export interface MortgageResults {
  maxHomePrice: number;
  qualifiesForRequestedPrice: boolean;
  monthlyMortgagePayment: number;
  monthlyPropertyTax: number;
  monthlyHeating: number;
  totalMonthlyHousingCost: number;
  gdsRatio: number;
  tdsRatio: number;
  gdsPass: boolean;
  tdsPass: boolean;
  cmhcRequired: boolean;
  cmhcPremiumPercent: number;
  cmhcPremiumAmount: number;
  totalMortgageWithInsurance: number;
  mortgageAmount: number;
  downPaymentPercent: number;
  minimumDownPayment: number;
  downPaymentSufficient: boolean;
  stressTestRate: number;
}
