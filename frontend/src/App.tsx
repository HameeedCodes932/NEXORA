import { useEffect, useState } from "react";
import { Layout } from "./components/Layout";
import { clearToken, getToken, api } from "./services/api";
import type { OrganizationPlan, PageKey, WorkspaceStats } from "./types";
import { ActivityPage } from "./pages/ActivityPage";
import { Duplicates } from "./pages/Duplicates";
import { Login } from "./pages/Login";
import { Organize } from "./pages/Organize";
import { Overview } from "./pages/Overview";
import { SearchPage } from "./pages/SearchPage";
import { SettingsPage } from "./pages/SettingsPage";
import { Workspace } from "./pages/Workspace";

function pageFromHash(): PageKey {
  const value = window.location.hash.replace("#", "");
  const allowed: PageKey[] = ["overview", "workspace", "search", "duplicates", "organize", "activity", "settings"];
  return allowed.includes(value as PageKey) ? (value as PageKey) : "overview";
}

export default function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(getToken()));
  const [page, setPageState] = useState<PageKey>(pageFromHash());
  const [stats, setStats] = useState<WorkspaceStats | null>(null);
  const [searchSeed, setSearchSeed] = useState("");
  const [organizeSeed, setOrganizeSeed] = useState("");
  const [incomingPlan, setIncomingPlan] = useState<OrganizationPlan | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  function setPage(next: PageKey) {
    window.location.hash = next;
    setPageState(next);
  }

  async function loadStats() {
    if (!authenticated) return;
    try {
      setStats(await api.stats());
    } catch {
      clearToken();
      setAuthenticated(false);
    }
  }

  useEffect(() => {
    const onHash = () => setPageState(pageFromHash());
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  useEffect(() => {
    loadStats();
  }, [authenticated, refreshKey]);

  if (!authenticated) {
    return <Login onLogin={() => setAuthenticated(true)} />;
  }

  const pageBody = {
    overview: <Overview stats={stats} setPage={setPage} setSearchSeed={setSearchSeed} setOrganizeSeed={setOrganizeSeed} />,
    workspace: <Workspace />,
    search: <SearchPage seed={searchSeed} />,
    duplicates: <Duplicates setPage={setPage} setPlan={setIncomingPlan} />,
    organize: <Organize seed={organizeSeed} incomingPlan={incomingPlan} onMutation={() => setRefreshKey((key) => key + 1)} />,
    activity: <ActivityPage refreshKey={refreshKey} />,
    settings: <SettingsPage stats={stats} />
  }[page];

  return (
    <Layout
      page={page}
      setPage={setPage}
      stats={stats}
      onLogout={() => {
        clearToken();
        setAuthenticated(false);
      }}
    >
      {pageBody}
    </Layout>
  );
}
