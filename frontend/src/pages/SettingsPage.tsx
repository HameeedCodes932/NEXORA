import { KeyRound, Server, ShieldCheck } from "lucide-react";
import type { WorkspaceStats } from "../types";

export function SettingsPage({ stats }: { stats: WorkspaceStats | null }) {
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <section className="rounded-lg border border-white/10 bg-graphite-850 p-5">
        <ShieldCheck className="mb-4 h-6 w-6 text-signal-400" />
        <h2 className="text-lg font-semibold text-stone-50">Safety Model</h2>
        <p className="mt-3 text-sm leading-6 text-stone-400">Read-only actions run immediately. Mutating actions are blocked until the user approves a structured plan. Delete recommendations move files into sandbox Trash.</p>
      </section>
      <section className="rounded-lg border border-white/10 bg-graphite-850 p-5">
        <Server className="mb-4 h-6 w-6 text-sky-300" />
        <h2 className="text-lg font-semibold text-stone-50">System</h2>
        <div className="mt-3 space-y-2 text-sm text-stone-400">
          <p>API: {stats?.status.api ?? "Unknown"}</p>
          <p>Workspace: {stats?.status.workspace ?? "Unknown"}</p>
          <p>Embedding Engine: {stats?.status.embedding_engine ?? "Unknown"}</p>
          <p>Mode: {stats?.status.embedding_mode ?? "Unknown"}</p>
        </div>
      </section>
      <section className="rounded-lg border border-white/10 bg-graphite-850 p-5">
        <KeyRound className="mb-4 h-6 w-6 text-amber-300" />
        <h2 className="text-lg font-semibold text-stone-50">Demo Login</h2>
        <div className="mt-3 space-y-2 text-sm text-stone-400">
          <p>Email: reviewer@nexora.ai</p>
          <p>Password: NexoraDemo2026!</p>
        </div>
      </section>
    </div>
  );
}
