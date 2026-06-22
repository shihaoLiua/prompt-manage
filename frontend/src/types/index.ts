export interface User {
  id: string; username: string; email: string
  is_admin: boolean; created_at: string
}
export interface Category {
  id: string; name: string; parent_id: string | null
  sort_order: number; created_at: string; children: Category[]
}
export interface Tag {
  id: string; name: string; color: string | null; created_at: string
}
export interface PromptVariable {
  name: string; label: string; default: string
  type: 'text' | 'select'; options?: string[]
}
export interface Prompt {
  id: string; title: string; content: string
  description: string | null; variables: PromptVariable[]
  category_id: string | null; is_favorite: boolean; rating: number | null
  current_version: number; tags: Tag[]
  created_at: string; updated_at: string
}
export interface PromptListItem {
  id: string; title: string; description: string | null
  category_id: string | null; is_favorite: boolean; rating: number | null
  current_version: number; tags: Tag[]
  created_at: string; updated_at: string
}
export interface PromptVersion {
  id: string; version: number; content: string; variables: PromptVariable[]
  changelog: string | null; created_at: string
}
export interface ApiConfig {
  id: string; name: string; api_base: string; default_model: string
  is_active: boolean; created_at: string
}
export interface TestRun {
  id: string; prompt_id: string; model: string
  variables_snapshot: Record<string, string>
  final_prompt: string | null; response_text: string | null
  tokens_prompt: number | null; tokens_completion: number | null
  latency_ms: number | null; status: 'running' | 'success' | 'error'
  error_message: string | null; created_at: string
}
export interface BatchTest {
  id: string; prompt_id: string; name: string
  status: 'pending' | 'running' | 'completed' | 'partial' | 'failed'
  total_count: number; completed_count: number; created_at: string
}
export interface BatchConfig {
  api_config_id: string; model: string
  temperature?: number; max_tokens?: number; label: string
}
export interface PaginatedResponse<T> {
  items: T[]; total: number; page: number; page_size: number
}
