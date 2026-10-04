import type { LucideIcon } from "lucide-react";

export function StatCard({ label, value, icon: Icon, tone = "teal" }: { label: string; value: string; icon: LucideIcon; tone?: "teal" | "blue" | "amber" | "stone" }) {
  const tones = {
    teal: "text-signal-400 bg-signal-400/10 border-signal-400/20",
    blue: "text-sky-300 bg-sky-400/10 border-sky-400/20",
    amber: "text-amber-300 bg-amber-400/10 border-amber-400/20",
    stone: "text-stone-200 bg-stone-400/10 border-stone-400/20"
  };
  return (
    <div className="rounded-lg border border-white/10 bg-graphite-850 p-4 shadow-panel">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.16em] text-stone-500">{label}</p>
          <p className="mt-2 text-2xl font-semibold text-stone-50">{value}</p>
        </div>
        <div className={`grid h-10 w-10 place-items-center rounded-lg border ${tones[tone]}`}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </div>
  );
}
