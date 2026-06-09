import { useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { AlertTriangle, Loader2, Save } from "lucide-react"
import { useAuth } from "@/context/AuthContext"
import { extractErrorMessage, getModelNames, saveUserSetup } from "@/services/api"
import type { SetupConfig } from "@/services/types"
import { defaultConfig } from "@/lib/defaults"
import { Layout } from "@/components/shared/Layout"
import { ConfigForm } from "@/components/shared/ConfigForm"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

/** Compares the vector DB portion of two configs to detect a change. */
function vectorDbDiffers(a: SetupConfig, b: SetupConfig): boolean {
  const keys: (keyof SetupConfig)[] = [
    "db_flag",
    "CHROMA_API_KEY",
    "CHROMA_HOST",
    "CHROMA_TENANT",
    "CHROMA_DATABASE",
    "db_host",
    "db_port",
  ]
  return keys.some((k) => a[k] !== b[k])
}

export default function Settings() {
  const navigate = useNavigate()
  const { user, config: savedConfig, currentRepo, setConfig, clearIndexedRepos } = useAuth()

  const initial = savedConfig ?? defaultConfig
  const [config, setLocalConfig] = useState<SetupConfig>(initial)
  const [modelNames, setModelNames] = useState<string[]>([])
  const [loadingModels, setLoadingModels] = useState(false)
  const [saving, setSaving] = useState(false)

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

  const dbWillChange = useMemo(() => vectorDbDiffers(config, initial), [config, initial])

  const persist = async () => {
    if (!user) return
    setSaving(true)
    try {
      // Flag the config so the chat sidebar knows indexed repos are stale.
      const nextConfig: SetupConfig = { ...config, dbChanged: dbWillChange ? true : config.dbChanged }
      await saveUserSetup({
        user_id: user.email,
        repo_url: currentRepo ?? "",
        ...nextConfig,
      })

      if (dbWillChange) {
        clearIndexedRepos()
        toast.warning("Vector DB changed — your indexed repositories were cleared. Re-index to continue.")
      } else {
        toast.success("Settings saved.")
      }
      setConfig(nextConfig)
    } catch (err) {
      toast.error(extractErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  const handleSave = () => {
    if (dbWillChange) {
      toast.warning("Changing the vector DB will clear all indexed repositories.", {
        action: { label: "Save anyway", onClick: persist },
      })
      return
    }
    persist()
  }

  return (
    <Layout>
      <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
          <p className="text-sm text-muted-foreground">Update your model and vector database configuration.</p>
        </div>

        {dbWillChange && (
          <div className="mb-6 flex items-start gap-3 rounded-lg border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            <p className="leading-relaxed">
              You&apos;ve modified the vector database configuration. Saving will clear all indexed repositories,
              and you&apos;ll need to re-index before chatting again.
            </p>
          </div>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Configuration</CardTitle>
            <CardDescription>These settings apply to all future indexing and retrieval.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-8">
            <ConfigForm
              config={config}
              onChange={onChange}
              modelNames={modelNames}
              loadingModels={loadingModels}
            />
            <div className="flex items-center justify-between">
              <Button variant="ghost" onClick={() => navigate("/chat")} disabled={saving}>
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={saving}>
                {saving ? <Loader2 className="animate-spin" /> : <Save />}
                Save changes
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  )
}
