import type { MortgageResults } from "@/types/mortgage";
import PaymentBreakdown from "./PaymentBreakdown";
import clsx from "clsx";

function formatCAD(value: number): string {
  return new Intl.NumberFormat("en-CA", {
    style: "currency",
    currency: "CAD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

function RatioBar({ label, value, max, pass }: { label: string; value: number; max: number; pass: boolean }) {
  const percentage = Math.min((value / (max * 100)) * 100, 100);

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="font-medium">{label}</span>
        <span className={clsx("font-semibold", pass ? "text-success" : "text-danger")}>
          {value.toFixed(1)}% / {(max * 100).toFixed(0)}%
        </span>
      </div>
      <div className="h-3 rounded-full bg-gray-200 overflow-hidden">
        <div
          className={clsx(
            "h-full rounded-full transition-all duration-500",
            pass ? "bg-success" : "bg-danger"
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export default function PreApprovalResults({ results }: { results: MortgageResults }) {
  return (
    <div className="space-y-6">
      {/* Qualification status */}
      <div
        className={clsx(
          "rounded-xl p-6 text-center",
          results.qualifiesForRequestedPrice
            ? "bg-green-50 border border-green-200"
            : "bg-red-50 border border-red-200"
        )}
      >
        <p
          className={clsx(
            "text-lg font-semibold",
            results.qualifiesForRequestedPrice ? "text-success" : "text-danger"
          )}
        >
          {results.qualifiesForRequestedPrice
            ? "You likely qualify for this home!"
            : "You may not qualify for this price"}
        </p>
        <p className="mt-2 text-sm text-muted">
          Maximum estimated home price you can afford:
        </p>
        <p className="mt-1 text-3xl font-bold text-primary">
          {formatCAD(results.maxHomePrice)}
        </p>
      </div>

      {/* Debt service ratios */}
      <div className="rounded-xl border border-border bg-white p-6 space-y-4">
        <h3 className="font-semibold text-foreground">Debt Service Ratios</h3>
        <p className="text-xs text-muted">
          Calculated at the stress test rate of {results.stressTestRate.toFixed(2)}%
        </p>
        <RatioBar label="GDS (Gross Debt Service)" value={results.gdsRatio} max={0.39} pass={results.gdsPass} />
        <RatioBar label="TDS (Total Debt Service)" value={results.tdsRatio} max={0.44} pass={results.tdsPass} />
      </div>

      {/* CMHC Insurance */}
      {results.cmhcRequired && (
        <div className="rounded-xl border border-accent/30 bg-amber-50 p-6">
          <h3 className="font-semibold text-foreground">CMHC Mortgage Insurance Required</h3>
          <p className="mt-1 text-sm text-muted">
            Your down payment is {results.downPaymentPercent.toFixed(1)}% (under 20%), so
            mortgage insurance is required.
          </p>
          <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted">Premium Rate</p>
              <p className="font-semibold">{results.cmhcPremiumPercent}%</p>
            </div>
            <div>
              <p className="text-muted">Premium Amount</p>
              <p className="font-semibold">{formatCAD(results.cmhcPremiumAmount)}</p>
            </div>
          </div>
        </div>
      )}

      {/* Down payment warning */}
      {!results.downPaymentSufficient && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-6">
          <h3 className="font-semibold text-danger">Insufficient Down Payment</h3>
          <p className="mt-1 text-sm text-muted">
            The minimum down payment required is{" "}
            <span className="font-semibold text-foreground">
              {formatCAD(results.minimumDownPayment)}
            </span>
            .
          </p>
        </div>
      )}

      {/* Payment breakdown */}
      <PaymentBreakdown results={results} />
    </div>
  );
}
