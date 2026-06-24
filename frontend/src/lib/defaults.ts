import type { SetupConfig } from "@/services/types"

export const defaultConfig: SetupConfig = {
  // Model — default to CLOUD
  ollama_flag: false,
  modelName: "",
  api_key: "",
  // Ollama defaults
  ollama_host: "http://localhost",
  ollama_port: "11434",
  num_ctx: 4096,
  num_predict: 512,
  temperature: 0.2,
  requests_per_second: 1,
  max_bucket_size: 10,
  // Vector DB — default to CLOUD (false = CLOUD, true = LOCAL)
  db_flag: false,
  CHROMA_API_KEY: "",
  CHROMA_HOST: "",
  CHROMA_TENANT: "",
  CHROMA_DATABASE: "",
  db_host: "http://localhost",
  db_port: "8000",
}
