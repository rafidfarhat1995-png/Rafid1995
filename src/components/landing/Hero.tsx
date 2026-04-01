import Link from "next/link";

export default function Hero() {
  return (
    <section className="bg-primary text-white">
      <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6 sm:py-28 lg:px-8 text-center">
        <p className="text-accent text-sm font-semibold tracking-widest uppercase mb-4">
          Canadian Personal Finance Tools
        </p>
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
          Make Sense of Your{" "}
          <span className="text-accent">Loonies</span>
        </h1>
        <p className="mt-6 text-lg text-white/70 max-w-2xl mx-auto">
          Free, easy-to-use financial calculators built specifically for
          Canadians. From mortgage pre-approvals to savings planning — take
          control of your financial future.
        </p>
        <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/tools/mortgage-preapproval"
            className="inline-flex items-center justify-center rounded-lg bg-accent px-6 py-3 text-sm font-semibold text-primary transition hover:bg-accent-light"
          >
            Try the Pre-Approval Estimator
          </Link>
          <a
            href="#tools"
            className="inline-flex items-center justify-center rounded-lg border border-white/30 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/10"
          >
            Explore All Tools
          </a>
        </div>
      </div>
    </section>
  );
}
