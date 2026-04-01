import type { MortgageResults } from "@/types/mortgage";

function formatCAD(value: number): string {
  return new Intl.NumberFormat("en-CA", {
    style: "currency",
    currency: "CAD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

export default function PaymentBreakdown({ results }: { results: MortgageResults }) {
  return (
    <div className="rounded-xl border border-border bg-white p-6">
      <h3 className="font-semibold text-foreground mb-4">Monthly Payment Breakdown</h3>
      <div className="space-y-3">
        <div className="flex justify-between text-sm">
          <span className="text-muted">Mortgage Payment (P+I)</span>
          <span className="font-medium">{formatCAD(results.monthlyMortgagePayment)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-muted">Est. Property Tax</span>
          <span className="font-medium">{formatCAD(results.monthlyPropertyTax)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-muted">Est. Heating</span>
          <span className="font-medium">{formatCAD(results.monthlyHeating)}</span>
        </div>
        <div className="border-t border-border pt-3 flex justify-between">
          <span className="font-semibold">Total Monthly Housing Cost</span>
          <span className="font-bold text-primary">
            {formatCAD(results.totalMonthlyHousingCost)}
          </span>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-border space-y-3">
        <h4 className="text-sm font-semibold text-foreground">Mortgage Summary</h4>
        <div className="flex justify-between text-sm">
          <span className="text-muted">Base Mortgage</span>
          <span className="font-medium">{formatCAD(results.mortgageAmount)}</span>
        </div>
        {results.cmhcRequired && (
          <div className="flex justify-between text-sm">
            <span className="text-muted">CMHC Insurance</span>
            <span className="font-medium">{formatCAD(results.cmhcPremiumAmount)}</span>
          </div>
        )}
        <div className="flex justify-between text-sm">
          <span className="text-muted">Total Mortgage</span>
          <span className="font-semibold">{formatCAD(results.totalMortgageWithInsurance)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-muted">Down Payment ({results.downPaymentPercent.toFixed(1)}%)</span>
          <span className="font-medium text-success">Provided by you</span>
        </div>
      </div>
    </div>
  );
}
