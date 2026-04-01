import Hero from "@/components/landing/Hero";
import ToolCard from "@/components/landing/ToolCard";

export default function HomePage() {
  return (
    <>
      <Hero />

      <section id="tools" className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
        <h2 className="text-2xl font-bold text-primary text-center mb-2">
          Financial Tools
        </h2>
        <p className="text-center text-muted mb-10">
          Free calculators designed for the Canadian market
        </p>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <ToolCard
            title="Mortgage Pre-Approval Estimator"
            description="Find out how much mortgage you can qualify for based on your income, debts, and Canadian lending rules."
            href="/tools/mortgage-preapproval"
            icon={<span>🏠</span>}
          />
          <ToolCard
            title="Mortgage Amortization Calculator"
            description="Generate a full amortization schedule showing your monthly principal and interest breakdown over time."
            href="/tools/mortgage-amortization"
            icon={<span>📊</span>}
            available={false}
          />
          <ToolCard
            title="RRSP vs TFSA Optimizer"
            description="Compare the tax advantages of contributing to an RRSP versus a TFSA based on your income and tax bracket."
            href="/tools/rrsp-vs-tfsa"
            icon={<span>💰</span>}
            available={false}
          />
        </div>
      </section>
    </>
  );
}
