// Bank of Canada stress test parameters
export const STRESS_TEST_FLOOR = 5.25; // %
export const STRESS_TEST_BUFFER = 2.0; // % added to contract rate

// Debt service ratio limits
export const MAX_GDS_RATIO = 0.39; // 39%
export const MAX_TDS_RATIO = 0.44; // 44%

// Default monthly estimates (used when user doesn't provide)
export const DEFAULT_MONTHLY_PROPERTY_TAX = 350;
export const DEFAULT_MONTHLY_HEATING = 175;

// CMHC mortgage insurance
export const CMHC_PRICE_CEILING = 1_000_000;

export const CMHC_PREMIUM_TIERS = [
  { minPercent: 5, maxPercent: 9.99, premium: 4.0 },
  { minPercent: 10, maxPercent: 14.99, premium: 3.1 },
  { minPercent: 15, maxPercent: 19.99, premium: 2.8 },
] as const;

// Down payment rules
export const DOWN_PAYMENT_FIRST_TIER_LIMIT = 500_000;
export const DOWN_PAYMENT_FIRST_TIER_RATE = 0.05; // 5%
export const DOWN_PAYMENT_SECOND_TIER_RATE = 0.1; // 10% on portion above $500K
export const DOWN_PAYMENT_CONVENTIONAL_RATE = 0.2; // 20% required above $1M
