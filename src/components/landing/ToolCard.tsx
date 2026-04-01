import Link from "next/link";

interface ToolCardProps {
  title: string;
  description: string;
  href: string;
  icon: React.ReactNode;
  available?: boolean;
}

export default function ToolCard({
  title,
  description,
  href,
  icon,
  available = true,
}: ToolCardProps) {
  const content = (
    <div className="group relative rounded-xl border border-border bg-white p-6 transition hover:shadow-lg hover:border-accent/50">
      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary text-xl">
        {icon}
      </div>
      <h3 className="mt-4 text-lg font-semibold text-foreground group-hover:text-primary transition">
        {title}
      </h3>
      <p className="mt-2 text-sm text-muted">{description}</p>
      {!available && (
        <span className="mt-3 inline-block rounded-full bg-accent/10 px-3 py-1 text-xs font-medium text-accent">
          Coming Soon
        </span>
      )}
    </div>
  );

  if (!available) return content;

  return <Link href={href}>{content}</Link>;
}
