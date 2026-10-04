import { ArrowRight, CheckCircle2, ShieldAlert, XCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../services/api";
import type { OrganizationPlan } from "../types";

export function Organize({
  seed,
  incomingPlan,
  onMutation
}: {
  seed: string;
  incomingPlan: OrganizationPlan | null;
  onMutation: () => void;
}) {
  const [instruction, setInstruction] = useState(seed || "Clean up my Downloads folder");
  const [plan, setPlan] = useState<OrganizationPlan | null>(incomingPlan);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (seed) setInstruction(seed);
  }, [seed]);

  useEffect(() => {
    if (incomingPlan) setPlan(incomingPlan);
  }, [incomingPlan]);

  async function generatePlan() {
    setLoading(true);
    setError("");
    setStatus("");
    try {
      const response = await api.plan(instruction);
      setPlan(response);
      setStatus("Plan generated. Nothing has been changed yet.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to generate plan.");
    } finally {
      setLoading(false);
    }
  }

  async function approve() {
    if (!plan) return;
    setLoading(true);
    setError("");
    try {
      const response = await api.approve(plan.id);
      setPlan({ ...plan, status: "approved" });
      setStatus(`${response.activity.length} sandbox action${response.activity.length === 1 ? "" : "s"} executed and recorded.`);
      onMutation();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Approval failed.");
    } finally {
      setLoading(false);
    }
  }

  async function reject() {
    if (!plan) return;
    setLoading(true);
    setError("");
    try {
      await api.reject(plan.id);
      setPlan({ ...plan, status: "rejected" });
      setStatus("Plan rejected. No workspace changes were made.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reject failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-5">
      <section className="rounded-lg border border-white/10 bg-graphite-900 p-5 shadow-panel">
        <div className="mb-4 flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-lg bg-amber-400/10 text-amber-300">
            <ShieldAlert className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-stone-50">Organize Workspace</h2>
            <p className="text-sm text-stone-500">Generate a plan first. Move, rename, trash, and overwrite operations require approval.</p>
          </div>
        </div>
        <div className="flex flex-col gap-3 lg:flex-row">
          <textarea value={instruction} onChange={(event) => setInstruction(event.target.value)} className="min-h-24 flex-1 rounded-md border border-white/10 bg-black/30 p-3 text-sm leading-6 text-stone-100 outline-none focus:border-signal-400/60" />
          <div className="flex w-full flex-col gap-2 lg:w-48">
            <button onClick={generatePlan} disabled={loading || instruction.trim().length < 3} className="rounded-md bg-signal-500 px-4 py-2.5 font-medium text-graphite-950">{loading ? "Working" : "Generate plan"}</button>
            <p className="rounded-md border border-amber-400/20 bg-amber-400/10 p-3 text-xs leading-5 text-amber-200">Nothing changes until the plan is approved.</p>
          </div>
        </div>
      </section>

      {error && <p className="rounded-md border border-red-400/20 bg-red-400/10 px-3 py-2 text-sm text-red-200">{error}</p>}
      {status && <p className="rounded-md border border-signal-400/20 bg-signal-400/10 px-3 py-2 text-sm text-signal-400">{status}</p>}

      {plan && (
        <section className="rounded-lg border border-white/10 bg-graphite-850">
          <div className="flex flex-col gap-2 border-b border-white/10 p-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.16em] text-stone-500">NEXORA organization plan</p>
              <h3 className="mt-1 text-lg font-semibold text-stone-50">{plan.actions.length} proposed actions</h3>
              <p className="text-sm text-stone-500">{plan.summary}</p>
            </div>
            <span className="rounded-md border border-white/10 px-2 py-1 text-xs uppercase tracking-[0.14em] text-stone-400">{plan.status}</span>
          </div>
          <div className="divide-y divide-white/10">
            {plan.actions.map((action) => (
              <article key={action.id} className="grid gap-4 p-4 lg:grid-cols-[120px_1fr_0.8fr]">
                <div>
                  <span className={`rounded-md border px-2 py-1 text-xs uppercase tracking-[0.14em] ${action.action_type === "trash" ? "border-amber-400/30 bg-amber-400/10 text-amber-300" : "border-signal-400/30 bg-signal-400/10 text-signal-400"}`}>{action.action_type}</span>
                </div>
                <div>
                  <p className="font-semibold text-stone-50">{action.filename}</p>
                  <div className="mt-2 flex flex-wrap items-center gap-2 text-sm text-stone-400">
                    <span>{action.source}</span>
                    <ArrowRight className="h-4 w-4 text-stone-600" />
                    <span>{action.destination}</span>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-stone-400">{action.reason}</p>
                </div>
                <div className="grid content-start gap-2 text-sm">
                  <p className="rounded-md border border-white/10 bg-black/20 px-3 py-2 text-stone-300">Confidence: {Math.round(action.confidence * 100)}%</p>
                  <p className="rounded-md border border-white/10 bg-black/20 px-3 py-2 text-stone-300">Risk: {action.risk}</p>
                </div>
              </article>
            ))}
            {plan.actions.length === 0 && <p className="p-5 text-sm text-stone-500">No safe organization actions were needed for this instruction.</p>}
          </div>
          <div className="flex flex-wrap justify-end gap-2 border-t border-white/10 p-4">
            <button onClick={reject} disabled={loading || plan.status !== "pending"} className="inline-flex items-center gap-2 rounded-md border border-white/10 bg-white/[0.03] px-4 py-2 text-sm text-stone-300">
              <XCircle className="h-4 w-4" />
              Reject Plan
            </button>
            <button onClick={approve} disabled={loading || plan.status !== "pending" || plan.actions.length === 0} className="inline-flex items-center gap-2 rounded-md bg-signal-500 px-4 py-2 text-sm font-medium text-graphite-950">
              <CheckCircle2 className="h-4 w-4" />
              Approve Plan
            </button>
          </div>
        </section>
      )}
    </div>
  );
}
