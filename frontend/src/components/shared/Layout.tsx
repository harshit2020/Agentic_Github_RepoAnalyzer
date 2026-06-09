import type { ReactNode } from "react"
import { Header } from "./Header"
import { Footer } from "./Footer"
import { cn } from "@/lib/utils"

interface LayoutProps {
  children: ReactNode
  /** When true, the main content fills available height (e.g. chat). */
  fill?: boolean
}

export function Layout({ children, fill = false }: LayoutProps) {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Header />
      <main className={cn("flex-1", fill ? "flex min-h-0 flex-col" : "")}>{children}</main>
      <Footer />
    </div>
  )
}
