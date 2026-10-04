import { Activity, BrainCircuit, Files, FolderKanban, Gauge, LogOut, Search, Settings, ShieldCheck, SplitSquareHorizontal } from "lucide-react";
import type { ReactNode } from "react";
import type { PageKey, WorkspaceStats } from "../types";
import { StatusPill } from "./StatusPill";

const navItems: Array<{ key: PageKey; label: string; icon: typeof Gauge }> = [
  { key: "overview", label: "Overview", icon: Gauge },
  { key: "workspace", label: "Workspace", icon: Files },
  { key: "search", label: "AI Search", icon: Search },
  { key: "duplicates", label: "Duplicates", icon: SplitSquareHorizontal },
  { key: "organize", label: "Organize", icon: FolderKanban },
  { key: "activity", label: "Activity", icon: Activity }
];

export function Layout({
  children,
  page,
  setPage,
  stats,
  onLogout
}: {
  children: ReactNode;
  page: PageKey;
  setPage: (page: PageKey) => void;
  stats: WorkspaceStats | null;
  onLogout: () => void;
}) {
  return (
    <div className="flex min-h-screen bg-graphite-950/75 text-stone-100">
      <aside className="fixed inset-y-0 left-0 z-20 flex w-72 flex-col border-r border-white/10 bg-graphite-900/95 p-4 backdrop-blur md:sticky">
        <button onClick={() => setPage("overview")} className="mb-8 flex items-center gap-3 rounded-lg border border-white/10 bg-white/[0.03] p-3 text-left">
          <div className="grid h-10 w-10 place-items-center rounded-lg bg-signal-400/12 text-signal-400">
            <BrainCircuit className="h-5 w-5" />
          </div>
          <div>
            <p className="text-base font-semibold tracking-[0.16em] text-stone-50">NEXORA</p>
            <p className="text-xs text-stone-500">AI Workspace Intelligence</p>
          </div>
        </button>
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = page === item.key;
            return (
              <button
                key={item.key}
                onClick={() => setPage(item.key)}
                className={`flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-sm ${active ? "border border-signal-400/30 bg-signal-400/10 text-stone-50" : "text-stone-400 hover:bg-white/[0.04] hover:text-stone-100"}`}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </button>
            );
          })}
        </nav>
        <div className="mt-auto space-y-2 border-t border-white/10 pt-4">
          <button onClick={() => setPage("settings")} className="flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-sm text-stone-400 hover:bg-white/[0.04] hover:text-stone-100">
            <Settings className="h-4 w-4" />
            Settings
          </button>
          <button onClick={onLogout} className="flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-sm text-stone-400 hover:bg-white/[0.04] hover:text-stone-100">
            <LogOut className="h-4 w-4" />
            Logout
          </button>
          <div className="rounded-lg border border-white/10 bg-black/20 p-3">
            <p className="mb-2 text-xs uppercase tracking-[0.16em] text-stone-500">System Status</p>
            <div className="flex flex-wrap gap-2">
              <StatusPill label={stats?.status.api ?? "API"} />
              <StatusPill label={stats?.status.workspace ?? "Workspace"} />
              <StatusPill label="Safety Active" />
            </div>
          </div>
        </div>
      </aside>
      <main className="ml-72 flex min-h-screen flex-1 flex-col md:ml-0">
        <header className="sticky top-0 z-10 border-b border-white/10 bg-graphite-950/82 px-6 py-4 backdrop-blur">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h1 className="text-lg font-semibold tracking-[0.12em] text-stone-50">NEXORA</h1>
              <p className="text-sm text-stone-500">Traditional file managers know where your files are. NEXORA understands what they mean.</p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <StatusPill label={`${stats?.indexed_files ?? 0} indexed files`} />
              <StatusPill label={stats?.status.embedding_engine ?? "Semantic engine"} ok={(stats?.status.embedding_mode ?? "fallback") !== "offline"} />
              <span className="inline-flex items-center gap-1.5 rounded-md border border-white/10 bg-white/[0.03] px-2 py-1 text-xs text-stone-400">
                <ShieldCheck className="h-3.5 w-3.5 text-signal-400" />
                Human approval required
              </span>
            </div>
          </div>
        </header>
        <section className="flex-1 p-6">{children}</section>
      </main>
    </div>
  );
}
