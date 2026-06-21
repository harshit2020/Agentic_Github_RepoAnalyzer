import { Cloud, Server } from "lucide-react"
import type { SetupConfig } from "@/services/types"
import { cn } from "@/lib/utils"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface ConfigFormProps {
  config: SetupConfig
  onChange: (patch: Partial<SetupConfig>) => void
  modelNames: string[]
  loadingModels?: boolean
}

function ModeToggle({
  idPrefix,
  value,
  onChange,
  cloudLabel = "Cloud",
  localLabel = "Local",
}: {
  idPrefix: string
  value: "cloud" | "local"
  onChange: (v: "cloud" | "local") => void
  cloudLabel?: string
  localLabel?: string
}) {
  return (
    <RadioGroup
      value={value}
      onValueChange={(v) => onChange(v as "cloud" | "local")}
      className="grid grid-cols-2 gap-3"
    >
      {(
        [
          { v: "cloud", label: cloudLabel, icon: Cloud },
          { v: "local", label: localLabel, icon: Server },
        ] as const
      ).map(({ v, label, icon: Icon }) => (
        <Label
          key={v}
          htmlFor={`${idPrefix}-${v}`}
          className={cn(
            "flex cursor-pointer items-center gap-3 rounded-xl border-2 p-4 transition-all font-medium",
            value === v ? "border-primary bg-primary/10 shadow-md" : "border-border/50 hover:border-border hover:bg-muted/50",
          )}
        >
          <RadioGroupItem value={v} id={`${idPrefix}-${v}`} className="sr-only" />
          <Icon className={cn("h-5 w-5", value === v ? "text-primary" : "text-muted-foreground")} />
          <span className="text-sm">{label}</span>
        </Label>
      ))}
    </RadioGroup>
  )
}

function Field({
  label,
  children,
}: {
  label: string
  children: React.ReactNode
}) {
  return (
    <div className="grid gap-3">
      <Label className="text-sm font-medium">{label}</Label>
      {children}
    </div>
  )
}

export function ConfigForm({ config, onChange, modelNames, loadingModels }: ConfigFormProps) {
  const modelMode: "cloud" | "local" = config.ollama_flag ? "local" : "cloud"
  const dbMode: "cloud" | "local" = config.db_flag ? "cloud" : "local"

  const num = (v: string) => (v === "" ? 0 : Number(v))

  return (
    <div className="grid gap-10">
      {/* Section A — Model */}
      <section className="grid gap-5">
        <div>
          <h3 className="text-base font-bold text-foreground">Model Configuration</h3>
          <p className="mt-1.5 text-sm text-muted-foreground">Choose a hosted cloud model or a local Ollama instance.</p>
        </div>

        <ModeToggle
          idPrefix="model"
          value={modelMode}
          cloudLabel="Cloud"
          localLabel="Local (Ollama)"
          onChange={(v) => onChange({ ollama_flag: v === "local" })}
        />

        {modelMode === "cloud" ? (
          <div className="grid gap-4 sm:grid-cols-2 w-full">
            <Field label="Model Name">
              <Select value={config.modelName} onValueChange={(v) => onChange({ modelName: v })}>
                <SelectTrigger>
                  <SelectValue placeholder={loadingModels ? "Loading models..." : "Select a model"} />
                </SelectTrigger>
                <SelectContent>
                  {modelNames.map((m) => (
                    <SelectItem key={m} value={m}>
                      {m}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </Field>
            <Field label="LLM API Key">
              <Input
                type="password"
                placeholder="sk-..."
                value={config.api_key}
                onChange={(e) => onChange({ api_key: e.target.value })}
              />
            </Field>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 w-full">
            <Field label="Model Name">
              <Select value={config.modelName} onValueChange={(v) => onChange({ modelName: v })}>
                <SelectTrigger>
                  <SelectValue placeholder={loadingModels ? "Loading models..." : "Select a model"} />
                </SelectTrigger>
                <SelectContent>
                  {modelNames.map((m) => (
                    <SelectItem key={m} value={m}>
                      {m}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </Field>
            <Field label="Ollama Host">
              <Input
                placeholder="http://localhost"
                value={config.ollama_host}
                onChange={(e) => onChange({ ollama_host: e.target.value })}
              />
            </Field>
            <Field label="Ollama Port">
              <Input
                placeholder="11434"
                value={config.ollama_port}
                onChange={(e) => onChange({ ollama_port: e.target.value })}
              />
            </Field>
            <Field label="Num Context (num_ctx)">
              <Input
                type="number"
                value={config.num_ctx}
                onChange={(e) => onChange({ num_ctx: num(e.target.value) })}
              />
            </Field>
            <Field label="Num Predict (num_predict)">
              <Input
                type="number"
                value={config.num_predict}
                onChange={(e) => onChange({ num_predict: num(e.target.value) })}
              />
            </Field>
            <Field label="Temperature">
              <Input
                type="number"
                min={0}
                max={1}
                step={0.1}
                value={config.temperature}
                onChange={(e) => onChange({ temperature: num(e.target.value) })}
              />
            </Field>
            <Field label="Requests / second">
              <Input
                type="number"
                value={config.requests_per_second}
                onChange={(e) => onChange({ requests_per_second: num(e.target.value) })}
              />
            </Field>
            <Field label="Max Bucket Size">
              <Input
                type="number"
                value={config.max_bucket_size}
                onChange={(e) => onChange({ max_bucket_size: num(e.target.value) })}
              />
            </Field>
          </div>
        )}
      </section>

      <div className="h-px bg-border/20" />

      {/* Section B — Vector DB */}
      <section className="grid gap-5">
        <div>
          <h3 className="text-base font-bold text-foreground">Vector DB Configuration</h3>
          <p className="mt-1.5 text-sm text-muted-foreground">Where your repository embeddings are stored.</p>
        </div>

        <ModeToggle idPrefix="db" value={dbMode} onChange={(v) => onChange({ db_flag: v === "cloud" })} />

        {dbMode === "cloud" ? (
          <div className="grid gap-4 sm:grid-cols-2 w-full">
            <Field label="Chroma API Key">
              <Input
                type="password"
                value={config.CHROMA_API_KEY}
                onChange={(e) => onChange({ CHROMA_API_KEY: e.target.value })}
              />
            </Field>
            <Field label="Chroma Host">
              <Input value={config.CHROMA_HOST} onChange={(e) => onChange({ CHROMA_HOST: e.target.value })} />
            </Field>
            <Field label="Chroma Tenant">
              <Input value={config.CHROMA_TENANT} onChange={(e) => onChange({ CHROMA_TENANT: e.target.value })} />
            </Field>
            <Field label="Chroma Database">
              <Input
                value={config.CHROMA_DATABASE}
                onChange={(e) => onChange({ CHROMA_DATABASE: e.target.value })}
              />
            </Field>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 w-full">
            <Field label="DB Host">
              <Input value={config.db_host} onChange={(e) => onChange({ db_host: e.target.value })} />
            </Field>
            <Field label="DB Port">
              <Input value={config.db_port} onChange={(e) => onChange({ db_port: e.target.value })} />
            </Field>
          </div>
        )}
      </section>
    </div>
  )
}
