import { History, RotateCcw } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../services/api";
import type { ActivityItem } from "../types";

export function ActivityPage({ refreshKey }: { refreshKey: number }) {
  const [items, setItems] = useState<ActivityItem[]>([]);
  const [error, setError] = useState("");
  const [working, setWorking] = useState("");

  async function load() {
    try {
      setItems(await api.activity());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load activity.");
    }
  }

  useEffect(() => {
    load();
  }, [refreshKey]);

  async function undo(item: ActivityItem) {
    setWorking(item.id);
    setError("");
    try {
      await api.undo(item.id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Undo failed.");
    } finally {
      setWorking("");
    }
  }

  return (
    <div className="space-y-5">
      <section className="rounded-lg border border-white/10 bg-graphite-900 p-5 shadow-panel">
        <div className="flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-lg bg-signal-400/10 text-signal-400">
            <History className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-stone-50">Action History + Rollback</h2>
            <p className="text-sm text-stone-500">Approved sandbox actions are logged. Move and trash actions can be undone.</p>
          </div>
        </div>
      </section>
      {error && <p className="rounded-md border border-red-400/20 bg-red-400/10 px-3 py-2 text-sm text-red-200">{error}</p>}
      <section className="rounded-lg border border-white/10 bg-graphite-850">
        <div className="divide-y divide-white/10">
          {items.map((item) => {
            const canUndo = ["Moved", "Moved to Trash"].includes(item.action) && item.status === "complete";
            return (
              <article key={item.id} className="grid gap-4 p-4 lg:grid-cols-[1fr_160px]">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-semibold text-stone-50">{item.action}: {item.filename}</h3>
                    <span className="rounded-md border border-white/10 px-2 py-1 text-xs text-stone-400">{item.status}</span>
                  </div>
                  <p className="mt-2 text-sm text-stone-400">{item.source} → {item.destination}</p>
                  <p className="mt-2 text-sm leading-6 text-stone-500">{item.reason}</p>
                  <p className="mt-2 text-xs text-stone-600">{new Date(item.timestamp).toLocaleString()} · {item.approved_by}</p>
                </div>
                <div className="flex items-start justify-end">
                  {canUndo && (
                    <button onClick={() => undo(item)} disabled={working === item.id} className="inline-flex items-center gap-2 rounded-md border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-stone-300">
                      <RotateCcw className="h-4 w-4" />
                      {working === item.id ? "Undoing" : "Undo"}
                    </button>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      </section>
    </div>
  );
}
