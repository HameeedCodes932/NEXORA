import { Check, CopyCheck, FileWarning, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { api, formatBytes } from "../services/api";
import type { DuplicatesResponse, OrganizationPlan, PageKey } from "../types";

export function Duplicates({
  setPage,
  setPlan
}: {
  setPage: (page: PageKey) => void;
  setPlan: (plan: OrganizationPlan) => void;
}) {
  const [data, setData] = useState<DuplicatesResponse | null>(null);
  const [acknowledged, setAcknowledged] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [loadingPlan, setLoadingPlan] = useState(false);

  useEffect(() => {
    api.duplicates().then(setData).catch((err) => setError(err.message));
  }, []);

  async function prepareCleanup() {
    setLoadingPlan(true);
    setError("");
    try {
      const plan = await api.plan("Clean up duplicate files");
      setPlan(plan);
      setPage("organize");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to prepare cleanup.");
    } finally {
      setLoadingPlan(false);
    }
  }

  return (
    <div className="space-y-5">
      <section className="rounded-lg border border-white/10 bg-graphite-900 p-5 shadow-panel">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.16em] text-signal-400">Duplicate intelligence</p>
            <h2 className="mt-2 text-xl font-semibold text-stone-50">Exact duplicates are based on SHA-256 content hashes</h2>
            <p className="mt-2 text-sm text-stone-500">Related versions use semantic similarity and naming signals, but are not treated as exact duplicates.</p>
          </div>
          <button onClick={prepareCleanup} disabled={loadingPlan} className="inline-flex items-center gap-2 rounded-md bg-signal-500 px-4 py-2 font-medium text-graphite-950">
            <ShieldCheck className="h-4 w-4" />
            {loadingPlan ? "Preparing" : "Prepare Cleanup"}
          </button>
        </div>
      </section>

      {error && <p className="rounded-md border border-red-400/20 bg-red-400/10 px-3 py-2 text-sm text-red-200">{error}</p>}

      <section className="grid gap-4 xl:grid-cols-[1fr_0.8fr]">
        <div className="rounded-lg border border-white/10 bg-graphite-850">
          <div className="border-b border-white/10 p-4">
            <h3 className="text-lg font-semibold text-stone-50">Exact Duplicate Groups</h3>
          </div>
          <div className="divide-y divide-white/10">
            {(data?.exact_groups ?? []).map((group, index) => (
              <article key={group.id} className="p-4">
                <div className="mb-3 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                  <div>
                    <h4 className="font-semibold text-stone-50">Duplicate Group #{index + 1}</h4>
                    <p className="text-xs text-stone-500">Identical content · recovery {formatBytes(group.potential_recovery)}</p>
                  </div>
                  {acknowledged.includes(group.id) && <span className="inline-flex items-center gap-1 rounded-md border border-signal-400/20 bg-signal-400/10 px-2 py-1 text-xs text-signal-400"><Check className="h-3.5 w-3.5" /> Keep both noted</span>}
                </div>
                <div className="space-y-2">
                  {group.files.map((file) => (
                    <div key={file.id} className="rounded-md border border-white/10 bg-black/20 px-3 py-2 text-sm">
                      <p className="font-medium text-stone-200">{file.name}</p>
                      <p className="text-stone-500">{file.location}</p>
                    </div>
                  ))}
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  <button onClick={() => setAcknowledged((items) => [...new Set([...items, group.id])])} className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-stone-300">Keep Both</button>
                  <button onClick={prepareCleanup} className="rounded-md border border-signal-400/30 bg-signal-400/10 px-3 py-2 text-sm text-signal-400">Prepare Cleanup</button>
                </div>
              </article>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-white/10 bg-graphite-850">
          <div className="border-b border-white/10 p-4">
            <h3 className="text-lg font-semibold text-stone-50">Potentially Related Versions</h3>
          </div>
          <div className="divide-y divide-white/10">
            {(data?.related_versions ?? []).map((item) => (
              <article key={`${item.left.id}-${item.right.id}`} className="p-4">
                <div className="mb-3 flex items-center gap-2 text-amber-300">
                  <FileWarning className="h-4 w-4" />
                  <span className="text-sm">{Math.round(item.score * 100)}% related, not identical</span>
                </div>
                <div className="grid gap-2">
                  <p className="rounded-md border border-white/10 bg-black/20 px-3 py-2 text-sm text-stone-300">{item.left.name}</p>
                  <p className="rounded-md border border-white/10 bg-black/20 px-3 py-2 text-sm text-stone-300">{item.right.name}</p>
                </div>
                <p className="mt-3 text-xs leading-5 text-stone-500">{item.reason}</p>
              </article>
            ))}
            {data?.related_versions.length === 0 && (
              <div className="p-6 text-center text-stone-500">
                <CopyCheck className="mx-auto mb-3 h-8 w-8" />
                No related versions detected yet.
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
