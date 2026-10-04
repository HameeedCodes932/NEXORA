import { CheckCircle2, CircleAlert } from "lucide-react";

export function StatusPill({ label, ok = true }: { label: string; ok?: boolean }) {
  const Icon = ok ? CheckCircle2 : CircleAlert;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-md border px-2 py-1 text-xs ${ok ? "border-signal-400/30 bg-signal-400/10 text-signal-400" : "border-amber-400/30 bg-amber-400/10 text-amber-300"}`}>
      <Icon className="h-3.5 w-3.5" />
      {label}
    </span>
  );
}
