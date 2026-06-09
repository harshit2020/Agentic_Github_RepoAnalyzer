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
        if (!active) return
        const names = new Set<string>()
        Object.values(data).forEach((v) => {
          if (Array.isArray(v)) v.forEach((x) => names.add(String(x)))
          else if (typeof v === "string") names.add(v)
        })
        setModelNames(Array.from(names))
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

        <div className="relative mx-auto max-w-3xl px-4 py-10 sm:px-6">
          {/* Step indicator */}
          <div className="mb-8">
            <div className="mb-3 flex items-center justify-center gap-3">
              {STEPS.map((label, i) => (
                <div key={label} className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <span
                      className={cn(
                        "flex h-7 w-7 items-center justify-center rounded-full border text-xs font-semibold transition-colors",
                        i < step
                          ? "border-primary bg-primary text-primary-foreground"
                          : i === step
                            ? "border-primary text-primary"
                            : "border-border text-muted-foreground",
                      )}
                    >
                      {i < step ? <Check className="h-3.5 w-3.5" /> : i + 1}
                    </span>
                    <span
                      className={cn(
                        "text-sm font-medium",
                        i === step ? "text-foreground" : "text-muted-foreground",
                      )}
                    >
                      {label}
                    </span>
                  </div>
                  {i < STEPS.length - 1 && <div className="h-px w-10 bg-border" />}
                </div>
              ))}
            </div>
            <Progress value={((step + 1) / STEPS.length) * 100} />
          </div>

          {step === 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>Configure your environment</CardTitle>
                <CardDescription>Set up your model and vector database before indexing a repo.</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-8">
                <ConfigForm
                  config={config}
                  onChange={onChange}
                  modelNames={modelNames}
                  loadingModels={loadingModels}
                />
                <div className="flex justify-end">
                  <Button onClick={handleNext}>
                    Next
                    <ArrowRight />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Index a repository</CardTitle>
                <CardDescription>Paste a public GitHub repository URL to analyze.</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-6">
                <div className="grid gap-1.5">
                  <Label htmlFor="repo">GitHub Repository URL</Label>
                  <div className="relative">
                    <Github className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="repo"
                      className="pl-9"
                      placeholder="https://github.com/owner/repo"
                      value={repoUrl}
                      onChange={(e) => setRepoUrl(e.target.value)}
                      disabled={indexing}
                    />
                  </div>
                </div>

                {jobState && (
                  <div className="grid gap-2 rounded-lg border border-border bg-secondary/30 p-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-2 font-medium">
                        {jobState !== "completed" && jobState !== "failed" && (
                          <Loader2 className="h-4 w-4 animate-spin text-primary" />
                        )}
                        {jobState === "completed" && <Check className="h-4 w-4 text-primary" />}
                        {statusLabel(jobState)}
                      </span>
                      <span className="text-muted-foreground">{Math.round(progress)}%</span>
                    </div>
                    <Progress value={progress} />
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <Button variant="ghost" onClick={() => setStep(0)} disabled={indexing}>
                    <ArrowLeft />
                    Back
                  </Button>
                  <Button onClick={handleIndex} disabled={indexing}>
                    {indexing && <Loader2 className="animate-spin" />}
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
