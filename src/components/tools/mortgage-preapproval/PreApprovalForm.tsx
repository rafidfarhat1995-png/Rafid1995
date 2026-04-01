"use client";

import { useState } from "react";
import type { MortgageInputs, MortgageResults } from "@/types/mortgage";
import { calculatePreApproval } from "@/lib/calculators/mortgage-preapproval";
import PreApprovalResults from "./PreApprovalResults";

const defaultInputs: MortgageInputs = {
  annualGrossIncome: 100000,
  monthlyDebts: 500,
  homePrice: 500000,
  downPayment: 50000,
  interestRate: 5.5,
  amortizationYears: 25,
};

function formatCurrency(value: number): string {
  return value.toLocaleString("en-CA");
}

function parseCurrency(value: string): number {
  return Number(value.replace(/[^0-9.]/g, "")) || 0;
}

export default function PreApprovalForm() {
  const [inputs, setInputs] = useState<MortgageInputs>(defaultInputs);
  const [results, setResults] = useState<MortgageResults | null>(null);
  const [displayValues, setDisplayValues] = useState({
    annualGrossIncome: formatCurrency(defaultInputs.annualGrossIncome),
    monthlyDebts: formatCurrency(defaultInputs.monthlyDebts),
    homePrice: formatCurrency(defaultInputs.homePrice),
    downPayment: formatCurrency(defaultInputs.downPayment),
  });

  function handleCurrencyChange(
    field: "annualGrossIncome" | "monthlyDebts" | "homePrice" | "downPayment",
    raw: string
  ) {
    const num = parseCurrency(raw);
    setInputs((prev) => ({ ...prev, [field]: num }));
    setDisplayValues((prev) => ({ ...prev, [field]: raw.replace(/[^0-9.]/g, "") }));
  }

  function handleCurrencyBlur(
    field: "annualGrossIncome" | "monthlyDebts" | "homePrice" | "downPayment"
  ) {
    setDisplayValues((prev) => ({
      ...prev,
      [field]: formatCurrency(inputs[field]),
    }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const result = calculatePreApproval(inputs);
    setResults(result);
  }

  return (
    <div className="space-y-8">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid gap-6 sm:grid-cols-2">
          {/* Annual Gross Income */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Annual Gross Income
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted">$</span>
              <input
                type="text"
                inputMode="numeric"
                value={displayValues.annualGrossIncome}
                onChange={(e) => handleCurrencyChange("annualGrossIncome", e.target.value)}
                onBlur={() => handleCurrencyBlur("annualGrossIncome")}
                className="w-full rounded-lg border border-border bg-white py-2.5 pl-8 pr-3 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
          </div>

          {/* Monthly Debts */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Monthly Debts
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted">$</span>
              <input
                type="text"
                inputMode="numeric"
                value={displayValues.monthlyDebts}
                onChange={(e) => handleCurrencyChange("monthlyDebts", e.target.value)}
                onBlur={() => handleCurrencyBlur("monthlyDebts")}
                className="w-full rounded-lg border border-border bg-white py-2.5 pl-8 pr-3 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
            <p className="mt-1 text-xs text-muted">Car payments, credit cards, loans, etc.</p>
          </div>

          {/* Home Price */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Home Price
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted">$</span>
              <input
                type="text"
                inputMode="numeric"
                value={displayValues.homePrice}
                onChange={(e) => handleCurrencyChange("homePrice", e.target.value)}
                onBlur={() => handleCurrencyBlur("homePrice")}
                className="w-full rounded-lg border border-border bg-white py-2.5 pl-8 pr-3 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
          </div>

          {/* Down Payment */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Down Payment
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted">$</span>
              <input
                type="text"
                inputMode="numeric"
                value={displayValues.downPayment}
                onChange={(e) => handleCurrencyChange("downPayment", e.target.value)}
                onBlur={() => handleCurrencyBlur("downPayment")}
                className="w-full rounded-lg border border-border bg-white py-2.5 pl-8 pr-3 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
          </div>

          {/* Interest Rate */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Interest Rate (%)
            </label>
            <input
              type="number"
              step="0.01"
              min="0.5"
              max="15"
              value={inputs.interestRate}
              onChange={(e) =>
                setInputs((prev) => ({
                  ...prev,
                  interestRate: parseFloat(e.target.value) || 0,
                }))
              }
              className="w-full rounded-lg border border-border bg-white py-2.5 px-3 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>

          {/* Amortization Period */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Amortization Period
            </label>
            <select
              value={inputs.amortizationYears}
              onChange={(e) =>
                setInputs((prev) => ({
                  ...prev,
                  amortizationYears: parseInt(e.target.value),
                }))
              }
              className="w-full rounded-lg border border-border bg-white py-2.5 px-3 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            >
              <option value={25}>25 years</option>
              <option value={30}>30 years</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          className="w-full rounded-lg bg-primary py-3 text-sm font-semibold text-white transition hover:bg-primary-light focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 cursor-pointer"
        >
          Calculate Pre-Approval
        </button>
      </form>

      {results && <PreApprovalResults results={results} />}
    </div>
  );
}
