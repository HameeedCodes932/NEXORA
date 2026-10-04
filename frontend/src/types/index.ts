export type PageKey = "overview" | "workspace" | "search" | "duplicates" | "organize" | "activity" | "settings";

export interface SystemStatus {
  api: string;
  workspace: string;
  semantic_engine: string;
  safety_layer: string;
  embedding_engine: string;
  embedding_mode: string;
}

export interface WorkspaceStats {
  total_files: number;
  storage_used: number;
  duplicate_files: number;
  potential_recovery: number;
  indexed_files: number;
  insights: string[];
  recent_activity: ActivityItem[];
  status: SystemStatus;
}

export interface WorkspaceFile {
  id: string;
  name: string;
  location: string;
  extension: string;
  file_type: string;
  size: number;
  modified_at: string;
  sha256: string;
  category: string;
  confidence: number;
  reason: string;
  preview: string;
  tags: string[];
  status: string;
}

export interface FileDetail extends WorkspaceFile {
  related_files: WorkspaceFile[];
  duplicate_status: string;
}

export interface SearchResult {
  file: WorkspaceFile;
  score: number;
  excerpt: string;
  reason: string;
}

export interface SearchResponse {
  query: string;
  engine: string;
  mode: string;
  results: SearchResult[];
}

export interface DuplicateGroup {
  id: string;
  hash: string;
  files: WorkspaceFile[];
  potential_recovery: number;
}

export interface DuplicatesResponse {
  exact_groups: DuplicateGroup[];
  related_versions: Array<{
    left: WorkspaceFile;
    right: WorkspaceFile;
    score: number;
    reason: string;
  }>;
}

export interface ProposedAction {
  id: string;
  action_type: "move" | "trash" | string;
  file_id: string;
  filename: string;
  source: string;
  destination: string;
  reason: string;
  confidence: number;
  risk: string;
}

export interface OrganizationPlan {
  id: string;
  created_at: string;
  query: string;
  status: string;
  summary: string;
  actions: ProposedAction[];
}

export interface ActivityItem {
  id: string;
  timestamp: string;
  action: string;
  file_id?: string | null;
  filename: string;
  source: string;
  destination: string;
  reason: string;
  status: string;
  approved_by: string;
}
