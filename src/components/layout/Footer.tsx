export default function Footer() {
  return (
    <footer className="mt-auto border-t border-border bg-white py-8">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
          <p className="text-sm font-medium text-primary">
            <span className="text-accent">$</span> Loonie Sense
          </p>
          <p className="text-xs text-muted text-center max-w-md">
            For educational purposes only. This is not financial advice. Always
            consult a qualified mortgage professional before making financial
            decisions.
          </p>
          <p className="text-xs text-muted">
            &copy; {new Date().getFullYear()} Loonie Sense
          </p>
        </div>
      </div>
    </footer>
  );
}
