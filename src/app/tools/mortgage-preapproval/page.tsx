import type { Metadata } from "next";
import PreApprovalForm from "@/components/tools/mortgage-preapproval/PreApprovalForm";

export const metadata: Metadata = {
  title: "Mortgage Pre-Approval Estimator — Loonie Sense",
  description:
    "Estimate how much mortgage you can qualify for based on Canadian rules: stress test, GDS/TDS ratios, CMHC insurance, and more.",
};

export default function MortgagePreApprovalPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-primary">
          Mortgage Pre-Approval Estimator
        </h1>
        <p className="mt-2 text-muted">
          See how much home you can afford based on Canadian mortgage rules,
          including the stress test, CMHC insurance, and debt service ratio
          limits.
        </p>
      </div>

      <PreApprovalForm />

      <div className="mt-10 rounded-xl border border-border bg-white p-6 text-sm text-muted space-y-2">
        <h3 className="font-semibold text-foreground">How it works</h3>
        <ul className="list-disc pl-5 space-y-1">
          <li>
            <strong>Stress Test:</strong> You must qualify at the higher of your
            contract rate + 2% or 5.25%.
          </li>
          <li>
            <strong>GDS Ratio:</strong> Your housing costs (mortgage + property
            tax + heating) must be under 39% of gross income.
          </li>
          <li>
            <strong>TDS Ratio:</strong> All debts combined must be under 44% of
            gross income.
          </li>
          <li>
            <strong>CMHC Insurance:</strong> Required if your down payment is
            less than 20% (homes under $1M only).
          </li>
          <li>
            <strong>Semi-Annual Compounding:</strong> Canadian mortgages compound
            semi-annually, which this calculator accounts for.
          </li>
        </ul>
      </div>
    </div>
  );
}
