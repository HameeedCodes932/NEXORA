import { ArrowRight, Database, Files, HardDrive, Layers3, Search, ShieldCheck, SplitSquareHorizontal } from "lucide-react";
import { formatBytes } from "../services/api";
import type { PageKey, WorkspaceStats } from "../types";
import { StatCard } from "../components/StatCard";

export function Overview({
  stats,
  setPage,
  setSearchSeed,
  setOrganizeSeed
}: {
  stats: WorkspaceStats | null;
  setPage: (page: PageKey) => void;
  setSearchSeed: (query: string) => void;
  setOrganizeSeed: (query: string) => void;
}) {
  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-white/10 bg-graphite-900 p-5 shadow-panel">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-signal-400">Workspace intelligence</p>
            <h2 className="mt-2 text-2xl font-semibold text-stone-50">A semantic map of a messy demo workspace</h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-stone-400">NEXORA indexes a sandbox of realistic documents, detects exact duplicates by content hash, retrieves by meaning, proposes safe organization actions, and records every approved mutation.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button onClick={() => { setSearchSeed("Find my machine learning research"); setPage("search"); }} className="inline-flex items-center gap-2 rounded-md bg-signal-500 px-3 py-2 text-sm font-medium text-graphite-950">
              <Search className="h-4 w-4" />
              Try semantic search
            </button>
            <button onClick={() => setPage("duplicates")} className="inline-flex items-center gap-2 rounded-md border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-stone-200">
              <SplitSquareHorizontal className="h-4 w-4" />
              Review duplicates
            </button>
            <button onClick={() => { setOrganizeSeed("Clean up my Downloads folder"); setPage("organize"); }} className="inline-flex items-center gap-2 rounded-md border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-stone-200">
              <ShieldCheck className="h-4 w-4" />
              Plan cleanup
            </button>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <StatCard label="Total files" value={String(stats?.total_files ?? 0)} icon={Files} tone="teal" />
        <StatCard label="Storage used" value={formatBytes(stats?.storage_used ?? 0)} icon={HardDrive} tone="blue" />
        <StatCard label="Duplicate files" value={String(stats?.duplicate_files ?? 0)} icon={SplitSquareHorizontal} tone="amber" />
        <StatCard label="Recovery" value={formatBytes(stats?.potential_recovery ?? 0)} icon={Database} tone="stone" />
        <StatCard label="AI indexed" value={String(stats?.indexed_files ?? 0)} icon={Layers3} tone="teal" />
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-lg border border-white/10 bg-graphite-850 p-5">
          <h3 className="mb-4 text-lg font-semibold text-stone-50">Workspace Intelligence</h3>
          <div className="grid gap-3 md:grid-cols-2">
            {(stats?.insights ?? []).map((insight) => (
              <div key={insight} className="rounded-lg border border-white/10 bg-black/20 p-4">
                <p className="text-sm text-stone-200">{insight}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-lg border border-white/10 bg-graphite-850 p-5">
          <h3 className="mb-4 text-lg font-semibold text-stone-50">Recent AI Activity</h3>
          <div className="space-y-3">
            {(stats?.recent_activity ?? []).map((item) => (
              <div key={item.id} className="flex items-start justify-between gap-3 rounded-md border border-white/10 bg-black/20 p-3">
                <div>
                  <p className="text-sm font-medium text-stone-100">{item.action}</p>
                  <p className="text-xs text-stone-500">{item.reason}</p>
                </div>
                <ArrowRight className="mt-1 h-4 w-4 text-stone-500" />
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
