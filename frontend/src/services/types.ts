export interface User {
  email: string
  username: string
  avatar?: string
}

export interface SignupPayload {
  username: string
  email: string
  password: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface ChangePasswordPayload {
  user_id: string
  current_password: string
  new_password: string
}

/** Model + vector DB configuration captured in Setup / Settings. */
export interface SetupConfig {
  // Model
  ollama_flag: boolean // true = LOCAL (ollama), false = CLOUD
  modelName: string
  api_key: string
  // Ollama-only fields
  ollama_host: string
  ollama_port: string
  num_ctx: number
  num_predict: number
  temperature: number
  requests_per_second: number
  max_bucket_size: number
  // Vector DB
  db_flag: boolean // true = CLOUD, false = LOCAL
  CHROMA_API_KEY: string
  CHROMA_HOST: string
  CHROMA_TENANT: string
  CHROMA_DATABASE: string
  db_host: string
  db_port: string
  /** Set when the vector DB was changed in Settings; cleared after re-indexing. */
  dbChanged?: boolean
}

export interface UserSetupPayload extends SetupConfig {
  user_id: string
  repo_url: string
}

export interface IndexPayload {
  user_id: string
  repo_url: string
}

export interface RetrievePayload {
  user_id: string
  user_query: string
}

/** Response from POST endpoints that enqueue a background job. */
export interface JobResponse {
  jobID: string
}

export type JobState = "queued" | "active" | "processing" | "completed" | "failed"

export interface JobStatus {
  state: JobState
  result?: unknown
  error?: string
  progress?: number
}

export interface ModelNamesResponse {
  [key: string]: string | string[]
}

export interface ChatSource {
  path: string
  lines?: string
}

export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  error?: boolean
  pending?: boolean
  sources?: ChatSource[]
  timestamp?: number
}
