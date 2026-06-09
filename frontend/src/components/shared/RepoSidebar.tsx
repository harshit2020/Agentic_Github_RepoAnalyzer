import { useState } from "react"
import { toast } from "sonner"
import { AlertTriangle, Check, FolderGit2, Github, Loader2, RefreshCw } from "lucide-react"
import { useAuth } from "@/context/AuthContext"
import { usePollJob } from "@/hooks/usePollJob"
import { extractErrorMessage, indexRepo, saveUserSetup } from "@/services/api"
import type { JobStatus } from "@/services/types"
import { shortRepoName } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"

/** Sidebar showing the active repo + change/index controls. */
export function RepoSidebar() {
  const {
    user,
    config,
    currentRepo,
    indexedRepos,
    setCurrentRepo,
    addIndexedRepo,
    clearIndexedRepos,
  } = useAuth()
  const { poll } = usePollJob()

  const [mode, setMode] = useState<"idle" | "change">("idle")
  const [repoUrl, setRepoUrl] = useState("")
  const [indexing, setIndexing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [jobState, setJobState] = useState<JobStatus["state"] | null>(null)

  // Did the user change the vector DB in settings since these repos were indexed?
  const vectorDbChanged = Boolean(config?.dbChanged)

  const runIndex = async (url: string) => {
    if (!user) return
    setIndexing(true)
    setJobState("queued")
    setProgress(5)
    try {
      await saveUserSetup({ user_id: user.email, repo_url: url, ...(config as any) })
      const { jobID } = await indexRepo({ user_id: user.email, repo_url: url })
      await poll(jobID, {
        onProgress: (s) => {
          setJobState(s.state)
          if (typeof s.progress === "number") setProgress(Math.max(10, Math.min(95, s.progress)))
          else setProgress((p) => Math.min(90, p + 8))
        },
      })
      setProgress(100)
      setJobState("completed")

      // If DB changed, indexed repos were cleared server-side; start fresh.
      if (vectorDbChanged) {
        clearIndexedRepos()
      }
      addIndexedRepo(url)
      setCurrentRepo(url)
      toast.success("Repository indexed.")
      setMode("idle")
      setRepoUrl("")
    } catch (err) {
      setJobState("failed")
      toast.error(extractErrorMessage(err))
    } finally {
      setIndexing(false)
    }
  }

  const handleSubmit = () => {
    if (!repoUrl.trim()) {
      toast.error("Please enter a repository URL.")
      return
    }
    if (vectorDbChanged) {
      toast.warning("Vector DB was changed. All indexed repos will be cleared.", {
        action: {
          label: "Continue",
          onClick: () => runIndex(repoUrl.trim()),
        },
      })
      return
    }
    runIndex(repoUrl.trim())
  }

  const hasRepo = Boolean(currentRepo)

  return (
    <aside className="flex w-full flex-col gap-4 border-border bg-card/40 p-4 md:w-72 md:border-r">
      <div>
        <h2 className="flex items-center gap-2 text-sm font-semibold">
          <FolderGit2 className="h-4 w-4 text-primary" />
          Repository
        </h2>
        <p className="mt-0.5 text-xs text-muted-foreground">Indexed source for your queries.</p>
      </div>

      {hasRepo && mode === "idle" ? (
        <div className="grid gap-3">
          <div className="rounded-lg border border-border bg-secondary/40 p-3">
            <div className="flex items-center gap-2">
              <Github className="h-4 w-4 shrink-0 text-muted-foreground" />
              <span className="truncate text-sm font-medium" title={currentRepo ?? ""}>
                {shortRepoName(currentRepo ?? "")}
              </span>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={() => setMode("change")}>
            <RefreshCw />
            Change Repo
          </Button>
        </div>
      ) : (
        <div className="grid gap-3">
          {!hasRepo && (
            <p className="text-xs text-muted-foreground">No repository indexed yet. Add one to start chatting.</p>
          )}
          {vectorDbChanged && (
            <div className="flex items-start gap-2 rounded-lg border border-destructive/40 bg-destructive/10 p-2.5 text-xs text-destructive">
              <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
              <span>Vector DB changed. Indexing will clear all previously indexed repos.</span>
            </div>
          )}
          <div className="grid gap-1.5">
            <Label htmlFor="sidebar-repo" className="text-xs">
              GitHub URL
            </Label>
            <Input
              id="sidebar-repo"
              className="h-9 text-sm"
              placeholder="https://github.com/owner/repo"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              disabled={indexing}
            />
          </div>

          {jobState && (
            <div className="grid gap-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-1.5">
                  {jobState !== "completed" && jobState !== "failed" && (
                    <Loader2 className="h-3 w-3 animate-spin text-primary" />
                  )}
                  {jobState === "completed" && <Check className="h-3 w-3 text-primary" />}
                  {jobState === "completed" ? "Done" : "Indexing..."}
                </span>
                <span className="text-muted-foreground">{Math.round(progress)}%</span>
              </div>
              <Progress value={progress} />
            </div>
          )}

          <div className="flex gap-2">
            {hasRepo && (
              <Button
                variant="ghost"
                size="sm"
                className="flex-1"
                onClick={() => {
                  setMode("idle")
                  setRepoUrl("")
                  setJobState(null)
                }}
                disabled={indexing}
              >
                Cancel
              </Button>
            )}
            <Button size="sm" className="flex-1" onClick={handleSubmit} disabled={indexing}>
              {indexing && <Loader2 className="animate-spin" />}
              Index
            </Button>
          </div>
        </div>
      )}

      {indexedRepos.length > 1 && (
        <div className="grid gap-1.5">
          <span className="text-xs font-medium text-muted-foreground">All indexed</span>
          {indexedRepos.map((r) => (
            <button
              key={r}
              onClick={() => setCurrentRepo(r)}
              className={`truncate rounded-md px-2 py-1 text-left text-xs transition-colors ${
                r === currentRepo ? "bg-primary/15 text-primary" : "text-muted-foreground hover:bg-secondary"
              }`}
              title={r}
            >
              {shortRepoName(r)}
            </button>
          ))}
        </div>
      )}
    </aside>
  )
}
