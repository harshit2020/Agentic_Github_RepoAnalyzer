import { useState } from "react"
import { User, Bot, FileCode, ChevronDown, ChevronRight, Copy, Check } from "lucide-react"
import type { ChatMessage as ChatMessageType } from "@/services/types"
import { cn } from "@/lib/utils"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"


function CodeBlock({ code }: { code: string }) {
  const [copied, setCopied] = useState(false)
  const copy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }
  return (
    <div className="relative my-2 rounded-lg border border-border bg-[hsl(240_10%_8%)]">
      <button
        onClick={copy}
        className="absolute right-2 top-2 rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
        aria-label="Copy code"
      >
        {copied ? <Check className="h-3.5 w-3.5 text-primary" /> : <Copy className="h-3.5 w-3.5" />}
      </button>
      <pre className="overflow-x-auto p-4 pr-10 text-sm">
        <code className="font-mono text-foreground">{code}</code>
      </pre>
    </div>
  )
}

/**
 * Lightweight renderer: splits content on triple-backtick fences and renders
 * those as code blocks. Everything else is rendered as paragraphs.
 */
// function renderContent(content: string) {
//   const parts = content.split(/```/)
//   return parts.map((part, i) => {
//     if (i % 2 === 1) {
//       // strip an optional leading language identifier line
//       const cleaned = part.replace(/^[a-zA-Z0-9]*\n/, "")
//       return <CodeBlock key={i} code={cleaned.trimEnd()} />
//     }
//     return part.split("\n").map((line, j) =>
//       line.trim() === "" ? null : (
//         <p key={`${i}-${j}`} className="leading-relaxed">
//           {line}
//         </p>
//       ),
//     )
//   })
// }

export function ChatMessage({ message }: { message: ChatMessageType }) {
  const [showSources, setShowSources] = useState(false)
  const isUser = message.role === "user"

  return (
    <div className={cn("flex gap-3", isUser ? "flex-row-reverse" : "flex-row")}>
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
          isUser ? "bg-muted text-foreground" : "bg-primary text-primary-foreground",
        )}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      <div className={cn("flex max-w-[85%] flex-col gap-1", isUser ? "items-end" : "items-start")}>
        <div
          className={cn(
            "rounded-2xl px-4 py-2.5 text-sm",
            isUser
              ? "rounded-tr-sm bg-primary text-primary-foreground"
              : "rounded-tl-sm border border-border bg-card text-card-foreground",
          )}
        >
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code(props) {
                  const { children } = props

                  return (
                    <CodeBlock
                      code={String(children).replace(/\n$/, "")}
                    />
                  )
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        </div>

        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="w-full">
            <button
              onClick={() => setShowSources((s) => !s)}
              className="flex items-center gap-1 text-xs text-muted-foreground transition-colors hover:text-foreground"
            >
              {showSources ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
              {message.sources.length} source{message.sources.length > 1 ? "s" : ""}
            </button>
            {showSources && (
              <ul className="mt-1.5 flex flex-col gap-1">
                {message.sources.map((src, i) => (
                  <li
                    key={i}
                    className="flex items-center gap-2 rounded-md border border-border bg-card px-2.5 py-1.5 text-xs text-muted-foreground"
                  >
                    <FileCode className="h-3.5 w-3.5 shrink-0 text-primary" />
                    <span className="truncate font-mono">{src.path}</span>
                    {src.lines && <span className="shrink-0 text-muted-foreground/70">{src.lines}</span>}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {message.timestamp && (
          <span className="px-1 text-[10px] text-muted-foreground/60">
            {new Date(message.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </span>
        )}
      </div>
    </div>
  )
}
