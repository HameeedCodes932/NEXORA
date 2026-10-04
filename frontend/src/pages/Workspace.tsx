import { FileText, Folder, PanelRightOpen, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { api, formatBytes } from "../services/api";
import type { FileDetail, WorkspaceFile } from "../types";

const types = ["all", "pdf", "docx", "txt", "md"];

export function Workspace() {
  const [files, setFiles] = useState<WorkspaceFile[]>([]);
  const [selected, setSelected] = useState<FileDetail | null>(null);
  const [type, setType] = useState("all");
  const [category, setCategory] = useState("all");
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api.files().then(setFiles).catch((err) => setError(err.message));
  }, []);

  const categories = useMemo(() => ["all", ...Array.from(new Set(files.map((file) => file.category))).sort()], [files]);
  const folders = useMemo(() => Array.from(new Set(files.map((file) => file.location))).sort(), [files]);
  const filtered = files.filter((file) => {
    const byType = type === "all" || file.extension === type;
    const byCategory = category === "all" || file.category === category;
    const byQuery = !query || `${file.name} ${file.location} ${file.category}`.toLowerCase().includes(query.toLowerCase());
    return byType && byCategory && byQuery;
  });

  async function openFile(file: WorkspaceFile) {
    setSelected(await api.file(file.id));
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[260px_1fr_360px]">
      <aside className="rounded-lg border border-white/10 bg-graphite-850 p-4">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-[0.16em] text-stone-400">Folder tree</h2>
        <div className="space-y-2">
          {folders.map((folder) => (
            <div key={folder} className="flex items-center justify-between rounded-md border border-white/10 bg-black/20 px-3 py-2 text-sm text-stone-300">
              <span className="flex min-w-0 items-center gap-2">
                <Folder className="h-4 w-4 shrink-0 text-signal-400" />
                <span className="truncate">{folder || "Root"}</span>
              </span>
              <span className="text-xs text-stone-500">{files.filter((file) => file.location === folder).length}</span>
            </div>
          ))}
        </div>
      </aside>

      <section className="min-w-0 rounded-lg border border-white/10 bg-graphite-850">
        <div className="flex flex-col gap-3 border-b border-white/10 p-4 xl:flex-row xl:items-center xl:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-stone-50">Workspace Explorer</h2>
            <p className="text-sm text-stone-500">{filtered.length} files visible from the sandbox index</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <label className="relative">
              <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-stone-500" />
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Filter files" className="h-9 rounded-md border border-white/10 bg-black/30 pl-9 pr-3 text-sm outline-none focus:border-signal-400/60" />
            </label>
            <select value={type} onChange={(event) => setType(event.target.value)} className="h-9 rounded-md border border-white/10 bg-black/30 px-3 text-sm">
              {types.map((item) => <option key={item}>{item}</option>)}
            </select>
            <select value={category} onChange={(event) => setCategory(event.target.value)} className="h-9 rounded-md border border-white/10 bg-black/30 px-3 text-sm">
              {categories.map((item) => <option key={item}>{item}</option>)}
            </select>
          </div>
        </div>
        {error && <p className="p-4 text-sm text-red-300">{error}</p>}
        <div className="overflow-auto scrollbar">
          <table className="w-full min-w-[860px] text-left text-sm">
            <thead className="border-b border-white/10 text-xs uppercase tracking-[0.14em] text-stone-500">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Location</th>
                <th className="px-4 py-3">Size</th>
                <th className="px-4 py-3">Modified</th>
                <th className="px-4 py-3">AI Category</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((file) => (
                <tr key={file.id} onClick={() => openFile(file)} className="cursor-pointer border-b border-white/5 text-stone-300 hover:bg-white/[0.03]">
                  <td className="px-4 py-3">
                    <span className="flex items-center gap-2 font-medium text-stone-100">
                      <FileText className="h-4 w-4 text-signal-400" />
                      {file.name}
                    </span>
                  </td>
                  <td className="px-4 py-3 uppercase">{file.extension}</td>
                  <td className="px-4 py-3">{file.location}</td>
                  <td className="px-4 py-3">{formatBytes(file.size)}</td>
                  <td className="px-4 py-3">{new Date(file.modified_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3">{file.category}</td>
                  <td className="px-4 py-3 text-signal-400">{file.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <aside className="rounded-lg border border-white/10 bg-graphite-850 p-4">
        {selected ? (
          <div className="space-y-5">
            <div>
              <p className="text-xs uppercase tracking-[0.16em] text-stone-500">Intelligence panel</p>
              <h3 className="mt-2 break-words text-lg font-semibold text-stone-50">{selected.name}</h3>
            </div>
            <div className="grid gap-2 text-sm text-stone-400">
              <p>Location: <span className="text-stone-200">{selected.location}</span></p>
              <p>Type: <span className="text-stone-200 uppercase">{selected.extension}</span></p>
              <p>Size: <span className="text-stone-200">{formatBytes(selected.size)}</span></p>
              <p>SHA-256: <span className="break-all text-xs text-stone-300">{selected.sha256}</span></p>
            </div>
            <div>
              <p className="mb-2 text-sm font-medium text-stone-200">AI Category</p>
              <p className="rounded-md border border-signal-400/20 bg-signal-400/10 px-3 py-2 text-sm text-signal-400">{selected.category} ({Math.round(selected.confidence * 100)}%)</p>
            </div>
            <div>
              <p className="mb-2 text-sm font-medium text-stone-200">Content Preview</p>
              <p className="rounded-md border border-white/10 bg-black/20 p-3 text-sm leading-6 text-stone-400">{selected.preview}</p>
            </div>
            <div>
              <p className="mb-2 text-sm font-medium text-stone-200">Related Files</p>
              <div className="space-y-2">
                {selected.related_files.map((file) => (
                  <button key={file.id} onClick={() => openFile(file)} className="flex w-full items-center justify-between rounded-md border border-white/10 bg-black/20 px-3 py-2 text-left text-sm">
                    <span className="truncate text-stone-300">{file.name}</span>
                    <PanelRightOpen className="h-4 w-4 text-stone-500" />
                  </button>
                ))}
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <span className="rounded-md border border-white/10 px-2 py-1 text-xs text-stone-300">{selected.duplicate_status}</span>
              {selected.tags.map((tag) => <span key={tag} className="rounded-md border border-white/10 px-2 py-1 text-xs text-stone-300">{tag}</span>)}
            </div>
          </div>
        ) : (
          <div className="grid h-full min-h-[360px] place-items-center text-center text-stone-500">
            <div>
              <PanelRightOpen className="mx-auto mb-3 h-8 w-8" />
              <p>Select a file to inspect its content intelligence.</p>
            </div>
          </div>
        )}
      </aside>
    </div>
  );
}
