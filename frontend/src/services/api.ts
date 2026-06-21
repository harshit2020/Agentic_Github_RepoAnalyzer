import axios from "axios"
import type {
  ChangePasswordPayload,
  IndexPayload,
  JobResponse,
  JobStatus,
  LoginPayload,
  ModelNamesResponse,
  RetrievePayload,
  SignupPayload,
  UserSetupPayload,
  RepoCheckPayload,
  RepoCheckResponse,
} from "./types"

export const API_BASE_URL = "http://localhost:3002"

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: false,
  headers: {
    "Content-Type": "application/json",
  },
})

/**
 * Attach the current user's email as `user_id` to every outgoing request.
 * We read from localStorage so this works outside of React render scope.
 */
api.interceptors.request.use((config) => {
  try {
    const raw = localStorage.getItem("ra_user")
    if (raw) {
      const user = JSON.parse(raw)
      if (user?.email) {
        if (config.method === "get") {
          config.params = { user_id: user.email, ...(config.params || {}) }
        } else if (config.data && typeof config.data === "object" && !Array.isArray(config.data)) {
          config.data = { user_id: user.email, ...config.data }
        }
      }
    }
  } catch {
    /* ignore parse errors */
  }
  return config
})

/* ---------------------------------- Auth --------------------------------- */

export async function signup(payload: SignupPayload) {
  const { data } = await api.post("/api/v1/users_nonVecDB/signup", payload)
  return data
}

export async function login(payload: LoginPayload) {
  console.log("Inside login ")
  console.log(payload)
  const { data } = await api.post("/api/v1/users_nonVecDB/login", payload)
  return data
}

export async function changePassword(payload: ChangePasswordPayload) {
  const { data } = await api.post("/api/v1/users_nonVecDB/change_password", payload)
  return data
}

export async function getSavedRepos(email: string): Promise<string[]> {
  const { data } = await api.get("/api/v1/users_nonVecDB/saved_repo", {
    params: { user_id: email },
  })
  // Normalize a few possible response shapes into a string[].
  if (Array.isArray(data?.savedRepos)) return data.savedRepos
  return []
}

/* --------------------------------- Models -------------------------------- */

export async function getModelNames(): Promise<ModelNamesResponse> {
  const { data } = await api.get<ModelNamesResponse>("/api/v1/models/getModelNames")
  return data
}

/* ---------------------------------- Setup -------------------------------- */

export async function getUserSetup(email: string) {
  const { data } = await api.get("/api/v1/users/user_setup", {
    params: { user_id: email },
  })
  return data
}

export async function saveUserSetup(payload: UserSetupPayload) {
  const { data } = await api.post("/api/v1/users/user_setup", payload)
  return data
}

/* ----------------------------- Repo operations --------------------------- */

export async function indexRepo(payload: IndexPayload): Promise<JobResponse> {
  const { data } = await api.post<JobResponse>("/api/v1/repo_operation/index", payload)
  return data
}

export async function retrieve(payload: RetrievePayload): Promise<JobResponse> {
  const { data } = await api.post<JobResponse>("/api/v1/repo_operation/retrieve", payload)
  return data
}

export async function getIndexedRepos(user_id: string) {
  console.log(`GETINDEXEDREPOS =${user_id}`)
  const { data } = await api.post("/api/v1/repo_operation/user_indexed_repos", {user_id})
  return data
}

export async function checkRepo(payload: RepoCheckPayload,): Promise<RepoCheckResponse> {
  const { data } = await api.post("/api/v1/repo_operation/checkExistingRepo", payload)
  return data
}


/* --------------------------------- Jobs ---------------------------------- */

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const { data } = await api.get<JobStatus>(`/api/v1/users/healthCheck/${jobId}`)
  return data
}

export function extractErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    return (
      (err.response?.data as { message?: string; error?: string })?.message ||
      (err.response?.data as { message?: string; error?: string })?.error ||
      err.message
    )
  }
  if (err instanceof Error) return err.message
  return "Something went wrong"
}
