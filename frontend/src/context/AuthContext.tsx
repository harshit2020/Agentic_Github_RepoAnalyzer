import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react"
import type { SetupConfig, User } from "@/services/types"

interface AuthContextValue {
  user: User | null
  isSetupComplete: boolean
  currentRepo: string | null
  indexedRepos: string[]
  config: SetupConfig | null
  login: (userData: User) => void
  logout: () => void
  setSetupComplete: (flag: boolean) => void
  setCurrentRepo: (url: string | null) => void
  setIndexedRepos: (repos: string[]) => void
  addIndexedRepo: (url: string) => void
  clearIndexedRepos: () => void
  updateUser: (patch: Partial<User>) => void
  setConfig: (config: SetupConfig | null) => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

const STORAGE = {
  user: "ra_user",
  setup: "ra_setup_complete",
  currentRepo: "ra_current_repo",
  indexedRepos: "ra_indexed_repos",
  config: "ra_config",
}

function readJSON<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    return raw ? (JSON.parse(raw) as T) : fallback
  } catch {
    return fallback
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => readJSON<User | null>(STORAGE.user, null))
  const [isSetupComplete, setIsSetupComplete] = useState<boolean>(
    () => readJSON<boolean>(STORAGE.setup, false),
  )
  const [currentRepo, setCurrentRepoState] = useState<string | null>(
    () => readJSON<string | null>(STORAGE.currentRepo, null),
  )
  const [indexedRepos, setIndexedReposState] = useState<string[]>(
    () => readJSON<string[]>(STORAGE.indexedRepos, []),
  )
  const [config, setConfigState] = useState<SetupConfig | null>(
    () => readJSON<SetupConfig | null>(STORAGE.config, null),
  )

  // Persist to localStorage on change.
  useEffect(() => {
    if (user) localStorage.setItem(STORAGE.user, JSON.stringify(user))
    else localStorage.removeItem(STORAGE.user)
  }, [user])

  useEffect(() => {
    localStorage.setItem(STORAGE.setup, JSON.stringify(isSetupComplete))
  }, [isSetupComplete])

  useEffect(() => {
    if (currentRepo) localStorage.setItem(STORAGE.currentRepo, JSON.stringify(currentRepo))
    else localStorage.removeItem(STORAGE.currentRepo)
  }, [currentRepo])

  useEffect(() => {
    localStorage.setItem(STORAGE.indexedRepos, JSON.stringify(indexedRepos))
  }, [indexedRepos])

  useEffect(() => {
    if (config) localStorage.setItem(STORAGE.config, JSON.stringify(config))
    else localStorage.removeItem(STORAGE.config)
  }, [config])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isSetupComplete,
      currentRepo,
      indexedRepos,
      config,
      login: (userData) => setUser(userData),
      logout: () => {
        setUser(null)
        setIsSetupComplete(false)
        setCurrentRepoState(null)
        setIndexedReposState([])
        setConfigState(null)
        Object.values(STORAGE).forEach((k) => localStorage.removeItem(k))
      },
      setSetupComplete: (flag) => setIsSetupComplete(flag),
      setCurrentRepo: (url) => setCurrentRepoState(url),
      setIndexedRepos: (repos) => setIndexedReposState(repos),
      addIndexedRepo: (url) =>
        setIndexedReposState((prev) => (prev.includes(url) ? prev : [...prev, url])),
      clearIndexedRepos: () => {
        setIndexedReposState([])
        setCurrentRepoState(null)
      },
      updateUser: (patch) => setUser((prev) => (prev ? { ...prev, ...patch } : prev)),
      setConfig: (c) => setConfigState(c),
    }),
    [user, isSetupComplete, currentRepo, indexedRepos, config],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider")
  return ctx
}
