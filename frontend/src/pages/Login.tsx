import { BrainCircuit, LogIn } from "lucide-react";
import { useState, type FormEvent } from "react";
import { api, setToken } from "../services/api";

export function Login({ onLogin }: { onLogin: () => void }) {
  const [email, setEmail] = useState("reviewer@nexora.ai");
  const [password, setPassword] = useState("NexoraDemo2026!");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await api.login(email, password);
      setToken(response.token);
      onLogin();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-screen place-items-center px-4">
      <div className="w-full max-w-md rounded-lg border border-white/10 bg-graphite-900 p-6 shadow-panel">
        <div className="mb-8 flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-lg bg-signal-400/12 text-signal-400">
            <BrainCircuit className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-[0.18em] text-stone-50">NEXORA</h1>
            <p className="text-sm text-stone-500">AI Workspace Intelligence</p>
          </div>
        </div>
        <p className="mb-6 text-lg text-stone-200">Your files finally understand each other.</p>
        <form onSubmit={submit} className="space-y-4">
          <label className="block">
            <span className="text-sm text-stone-400">Email</span>
            <input value={email} onChange={(event) => setEmail(event.target.value)} className="mt-2 w-full rounded-md border border-white/10 bg-black/30 px-3 py-2 text-stone-100 outline-none focus:border-signal-400/60" />
          </label>
          <label className="block">
            <span className="text-sm text-stone-400">Password</span>
            <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" className="mt-2 w-full rounded-md border border-white/10 bg-black/30 px-3 py-2 text-stone-100 outline-none focus:border-signal-400/60" />
          </label>
          {error && <p className="rounded-md border border-red-400/20 bg-red-400/10 px-3 py-2 text-sm text-red-200">{error}</p>}
          <button disabled={loading} className="flex w-full items-center justify-center gap-2 rounded-md bg-signal-500 px-4 py-2.5 font-medium text-graphite-950">
            <LogIn className="h-4 w-4" />
            {loading ? "Signing in" : "Enter workspace"}
          </button>
        </form>
        <div className="mt-6 rounded-lg border border-white/10 bg-white/[0.03] p-4 text-sm">
          <p className="mb-2 font-medium text-stone-200">Demo credentials</p>
          <p className="text-stone-400">Email: reviewer@nexora.ai</p>
          <p className="text-stone-400">Password: NexoraDemo2026!</p>
        </div>
      </div>
    </div>
  );
}
