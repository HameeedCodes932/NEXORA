import { Search, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../services/api";
import type { SearchResponse } from "../types";

const suggestions = [
  "Find everything related to machine learning",
  "Show documents related to my final-year project",
  "Find my internship documents",
  "Which files discuss computer vision?",
  "Find files related to finances"
];

export function SearchPage({ seed }: { seed: string }) {
  const [query, setQuery] = useState(seed || "");
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (seed) setQuery(seed);
  }, [seed]);

  async function submit(nextQuery = query) {
    if (!nextQuery.trim()) return;
    setLoading(true);
    setError("");
    try {
      const response = await api.search(nextQuery, 8);
      setResults(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-5">
      <section className="rounded-lg border border-white/10 bg-graphite-900 p-5 shadow-panel">
        <div className="mb-5 flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-lg bg-signal-400/10 text-signal-400">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-stone-50">AI Semantic Search</h2>
            <p className="text-sm text-stone-500">Search by meaning over extracted document content, not filenames.</p>
          </div>
        </div>
        <form
          onSubmit={(event) => {
            event.preventDefault();
            submit();
          }}
          className="flex flex-col gap-3 lg:flex-row"
        >
          <label className="relative flex-1">
            <Search className="pointer-events-none absolute left-4 top-3.5 h-5 w-5 text-stone-500" />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Ask NEXORA about your workspace..." className="h-12 w-full rounded-md border border-white/10 bg-black/30 pl-12 pr-4 text-stone-100 outline-none focus:border-signal-400/60" />
          </label>
          <button disabled={loading || query.trim().length < 2} className="rounded-md bg-signal-500 px-5 py-3 font-medium text-graphite-950">
            {loading ? "Searching" : "Search workspace"}
          </button>
        </form>
        <div className="mt-4 flex flex-wrap gap-2">
          {suggestions.map((item) => (
            <button
              key={item}
              onClick={() => {
                setQuery(item);
                submit(item);
              }}
              className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-stone-300"
            >
              {item}
            </button>
          ))}
        </div>
      </section>

      {error && <p className="rounded-md border border-red-400/20 bg-red-400/10 px-3 py-2 text-sm text-red-200">{error}</p>}

      {results && (
        <section className="rounded-lg border border-white/10 bg-graphite-850">
          <div className="flex flex-col gap-2 border-b border-white/10 p-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h3 className="text-lg font-semibold text-stone-50">Ranked Results</h3>
              <p className="text-sm text-stone-500">Engine: {results.engine} ({results.mode})</p>
            </div>
            <span className="rounded-md border border-white/10 px-2 py-1 text-xs text-stone-400">{results.results.length} matches</span>
          </div>
          <div className="divide-y divide-white/10">
            {results.results.map((result) => (
              <article key={result.file.id} className="p-4">
                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div>
                    <h4 className="text-base font-semibold text-stone-50">{result.file.name}</h4>
                    <p className="text-sm text-stone-500">{result.file.location} · {result.file.category}</p>
                  </div>
                  <span className="rounded-md border border-signal-400/20 bg-signal-400/10 px-2 py-1 text-sm text-signal-400">{Math.round(result.score * 100)}% relevant</span>
                </div>
                <p className="mt-3 text-sm leading-6 text-stone-300">{result.excerpt}</p>
                <p className="mt-3 text-xs text-stone-500">{result.reason}</p>
              </article>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
