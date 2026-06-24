import { useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { ArrowLeft, ArrowRight, Check, Github, Loader2 } from "lucide-react"
import { useAuth } from "@/context/AuthContext"
import { usePollJob } from "@/hooks/usePollJob"
import {
  extractErrorMessage,
  getModelNames,
  indexRepo,
  saveUserSetup,
} from "@/services/api"
import type { JobStatus, SetupConfig } from "@/services/types"
import { defaultConfig } from "@/lib/defaults"
import { Layout } from "@/components/shared/Layout"
import { ConfigForm } from "@/components/shared/ConfigForm"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"

const STEPS = ["Configuration", "Repository"]

function statusLabel(state: JobStatus["state"]): string {
  switch (state) {
    case "queued":
      return "Queued..."
    case "active":
    case "processing":
      return "Processing repository..."
    case "completed":
      return "Complete!"
    case "failed":
      return "Failed"
    default:
      return "Working..."
  }
}

export default function Setup() {
  const navigate = useNavigate()
  const { user, config: savedConfig, setConfig, setSetupComplete, setCurrentRepo, addIndexedRepo } = useAuth()
  const { poll } = usePollJob()

  const [step, setStep] = useState(0)
  const [config, setLocalConfig] = useState<SetupConfig>(savedConfig ?? defaultConfig)
  const [modelNames, setModelNames] = useState<string[]>([])
  const [loadingModels, setLoadingModels] = useState(false)
  const [repoUrl, setRepoUrl] = useState("")

  const [indexing, setIndexing] = useState(false)
  const [jobState, setJobState] = useState<JobStatus["state"] | null>(null)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    let active = true
    setLoadingModels(true)
    getModelNames()
      .then((data) => {
        setModelNames(Object.keys(data.ModelList))
      })
      .catch((err) => toast.error(extractErrorMessage(err)))
      .finally(() => active && setLoadingModels(false))
    return () => {
      active = false
    }
  }, [])

  const onChange = (patch: Partial<SetupConfig>) => setLocalConfig((prev) => ({ ...prev, ...patch }))

  const canProceed = useMemo(() => {
    if (config.ollama_flag) {
      return Boolean(config.modelName && config.ollama_host && config.ollama_port)
    }
    return Boolean(config.modelName && config.api_key)
  }, [config])

  const handleNext = () => {
    if (!canProceed) {
      toast.error("Please complete the model configuration.")
      return
    }
    setStep(1)
  }

  const handleIndex = async () => {
    if (!user) return
    if (!repoUrl.trim()) {
      toast.error("Please enter a GitHub repository URL.")
      return
    }

    setIndexing(true)
    setJobState("queued")
    setProgress(5)

    try {
      // 1. Save the user setup (config + repo).
      await saveUserSetup({
        user_id: user.email,
        repo_url: repoUrl.trim(),
        ...config,
      })

      // 2. Kick off the index job.
      const { jobID } = await indexRepo({ user_id: user.email, repo_url: repoUrl.trim() })

      // 3. Poll until complete.
      await poll(jobID, {
        onProgress: (s) => {
          setJobState(s.state)
          if (typeof s.progress === "number") setProgress(Math.max(10, Math.min(95, s.progress)))
          else setProgress((p) => Math.min(90, p + 8))
        },
      })

      setProgress(100)
      setJobState("completed")
      setConfig(config)
      setCurrentRepo(repoUrl.trim())
      addIndexedRepo(repoUrl.trim())
      setSetupComplete(true)
      toast.success("Repository indexed successfully!")
      navigate("/chat")
    } catch (err) {
      setJobState("failed")
      toast.error(extractErrorMessage(err))
    } finally {
      setIndexing(false)
    }
  }

  return (
    <Layout>
      <div className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute left-1/2 top-[-20%] h-[420px] w-[640px] -translate-x-1/2 rounded-full bg-primary/10 blur-[120px]" />
        </div>

        <div className="relative mx-auto max-w-3xl px-6 py-14 sm:px-8">
          {/* Step indicator */}
          <div className="mb-12">
            <div className="mb-4 flex items-center justify-center gap-4">
              {STEPS.map((label, i) => (
                <div key={label} className="flex items-center gap-4">
                  <div className="flex items-center gap-3">
                    <span
                      className={cn(
                        "flex h-8 w-8 items-center justify-center rounded-full border-2 text-xs font-semibold transition-all",
                        i < step
                          ? "border-primary bg-primary text-primary-foreground shadow-lg"
                          : i === step
                            ? "border-primary bg-primary/10 text-primary ring-2 ring-primary/20"
                            : "border-border/50 text-muted-foreground",
                      )}
                    >
                      {i < step ? <Check className="h-4 w-4" /> : i + 1}
                    </span>
                    <span
                      className={cn(
                        "text-sm font-semibold",
                        i === step ? "text-foreground" : "text-muted-foreground",
                      )}
                    >
                      {label}
                    </span>
                  </div>
                  {i < STEPS.length - 1 && <div className="h-px w-12 bg-border/30" />}
                </div>
              ))}
            </div>
            <Progress value={((step + 1) / STEPS.length) * 100} className="h-1.5" />
          </div>

          {step === 0 ? (
            <Card className="border border-border/50 bg-gradient-to-b from-card to-card/95 shadow-xl">
              <CardHeader className="border-b border-border/30 px-8 pt-8 pb-6">
                <CardTitle className="text-2xl">Configure your environment</CardTitle>
                <CardDescription className="mt-2 text-base">Set up your model and vector database before indexing a repo.</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-8 px-8 pt-8 pb-8">
                <ConfigForm
                  config={config}
                  onChange={onChange}
                  modelNames={modelNames}
                  loadingModels={loadingModels}
                />
                <div className="flex justify-end pt-4 border-t border-border/20">
                  <Button onClick={handleNext} className="h-10 px-6 font-medium">
                    Next
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="border border-border/50 bg-gradient-to-b from-card to-card/95 shadow-xl">
              <CardHeader className="border-b border-border/30 px-8 pt-8 pb-6">
                <CardTitle className="text-2xl">Index a repository</CardTitle>
                <CardDescription className="mt-2 text-base">Paste a public GitHub repository URL to analyze.</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-8 px-8 pt-8 pb-8">
                <div className="grid gap-3">
                  <Label htmlFor="repo" className="text-sm font-semibold">GitHub Repository URL</Label>
                  <div className="relative">
                    <Github className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="repo"
                      className="pl-11 h-10 text-sm"
                      placeholder="https://github.com/owner/repo"
                      value={repoUrl}
                      onChange={(e) => setRepoUrl(e.target.value)}
                      disabled={indexing}
                    />
                  </div>
                </div>

                {jobState && (
                  <div className="grid gap-3">
                    <div className="rounded-xl border border-border/50 bg-muted/30 p-5">
                      <div className="flex items-center justify-between text-sm">
                        <span className="flex items-center gap-2.5 font-semibold text-foreground">
                          {jobState !== "completed" && jobState !== "failed" && (
                            <Loader2 className="h-4 w-4 animate-spin text-primary" />
                          )}
                          {jobState === "completed" && <Check className="h-4 w-4 text-primary" />}
                          {statusLabel(jobState)}
                        </span>
                        <span className="text-muted-foreground font-medium">{Math.round(progress)}%</span>
                      </div>
                      <Progress value={progress} className="h-2" />
                    </div>
                    {jobState === "failed" && (
                      <div className="rounded-lg border border-amber-200/50 bg-amber-50/50 p-4 dark:border-amber-900/30 dark:bg-amber-950/20">
                        <p className="text-sm text-amber-900 dark:text-amber-200">
                          <span className="font-semibold">Indexing failed.</span> Please check your model and vector database configurations. If the issue persists, try using a different API key.
                        </p>
                      </div>
                    )}
                  </div>
                )}

                <div className="flex items-center justify-between pt-4 border-t border-border/20">
                  <Button variant="outline" onClick={() => setStep(0)} disabled={indexing} className="h-10">
                    <ArrowLeft className="h-4 w-4" />
                    Back
                  </Button>
                  <Button onClick={handleIndex} disabled={indexing} className="h-10 px-6 font-medium">
                    {indexing && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
                    {indexing ? "Indexing..." : "Index repository"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </Layout>
  )
}
