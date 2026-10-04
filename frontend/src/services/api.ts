import type {
  ActivityItem,
  DuplicatesResponse,
  FileDetail,
  OrganizationPlan,
  SearchResponse,
  SystemStatus,
  WorkspaceFile,
  WorkspaceStats
} from "../types";

const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? "http://localhost:8000" : "");
const TOKEN_KEY = "nexora_demo_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers ?? {})
    }
  });
  if (!response.ok) {
    let message = `Request failed with ${response.status}`;
    try {
      const payload = await response.json();
      message = payload.detail || message;
    } catch {
      // Keep the status message.
    }
    throw new Error(message);
  }
  return response.json();
}

export const api = {
  login(email: string, password: string) {
    return request<{ token: string; user: { email: string; name: string } }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
  },
  health() {
    return request<SystemStatus>("/api/health");
  },
  stats() {
    return request<WorkspaceStats>("/api/workspace/stats");
  },
  files(filters?: { type?: string; category?: string }) {
    const params = new URLSearchParams();
    if (filters?.type) params.set("type", filters.type);
    if (filters?.category) params.set("category", filters.category);
    const suffix = params.toString() ? `?${params}` : "";
    return request<WorkspaceFile[]>(`/api/files${suffix}`);
  },
  file(id: string) {
    return request<FileDetail>(`/api/files/${id}`);
  },
  search(query: string, limit = 8) {
    return request<SearchResponse>("/api/search", {
      method: "POST",
      body: JSON.stringify({ query, limit })
    });
  },
  duplicates() {
    return request<DuplicatesResponse>("/api/duplicates");
  },
  plan(instruction: string) {
    return request<OrganizationPlan>("/api/organize/plan", {
      method: "POST",
      body: JSON.stringify({ instruction })
    });
  },
  approve(planId: string) {
    return request<{ status: string; activity: ActivityItem[] }>("/api/organize/approve", {
      method: "POST",
      body: JSON.stringify({ plan_id: planId })
    });
  },
  reject(planId: string) {
    return request<{ status: string }>("/api/organize/reject", {
      method: "POST",
      body: JSON.stringify({ plan_id: planId })
    });
  },
  activity() {
    return request<ActivityItem[]>("/api/activity");
  },
  undo(activityId: string) {
    return request<ActivityItem>(`/api/activity/${activityId}/undo`, { method: "POST" });
  }
};

export function formatBytes(value: number) {
  if (value < 1024) return `${value} B`;
  const units = ["KB", "MB", "GB"];
  let size = value / 1024;
  let unit = 0;
  while (size >= 1024 && unit < units.length - 1) {
    size /= 1024;
    unit += 1;
  }
  return `${size.toFixed(size >= 10 ? 1 : 2)} ${units[unit]}`;
}
