import type { ReactNode } from "react"
import { Boxes } from "lucide-react"

/** Shared auth shell with the subtle violet radial gradient backdrop. */
export function AuthShell({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) {
  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-10">
      {/* Background gradient accents */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/2 top-[-10%] h-[480px] w-[480px] -translate-x-1/2 rounded-full bg-primary/20 blur-[120px]" />
        <div className="absolute bottom-[-15%] right-[5%] h-[360px] w-[360px] rounded-full bg-primary/10 blur-[120px]" />
      </div>

      <div className="relative w-full max-w-lg">
        <div className="mb-12 flex flex-col items-center text-center">
          <span className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/20 to-primary/10 text-primary">
            <Boxes className="h-8 w-8" />
          </span>
          <h1 className="text-4xl font-bold tracking-tight text-balance text-foreground">{title}</h1>
          <p className="mt-3 text-base text-muted-foreground text-pretty leading-relaxed">{subtitle}</p>
        </div>
        {children}
      </div>
    </div>
  )
}
