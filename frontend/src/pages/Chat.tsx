import { useState, useRef, useEffect, useCallback } from "react"
import { Send, Loader2, MessageSquare, Trash2, Github, Zap } from "lucide-react"
import { Layout } from "@/components/shared/Layout"
import { RepoSidebar } from "@/components/shared/RepoSidebar"
import { ChatMessage } from "@/components/shared/ChatMessage"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/context/AuthContext"
import { retrieve, extractErrorMessage } from "@/services/api"
import { usePollJob } from "@/hooks/usePollJob"
import { shortRepoName } from "@/lib/utils"
import type { ChatMessage as ChatMessageType, ChatSource } from "@/services/types"
import { toast } from "sonner"

const SUGGESTIONS = [
  "What does this codebase do?",
  "Explain the authentication flow",
  "Where is the database schema defined?",
  "How do I run the project locally?",
]

export default function Chat() {
  const { user, currentRepo, config } = useAuth()
  const { poll } = usePollJob()
  const [messages, setMessages] = useState<ChatMessageType[]>([])
  const [input, setInput] = useState("")
  const [sending, setSending] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Reset the conversation when switching repos.
  useEffect(() => {
    setMessages([])
  }, [currentRepo])

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" })
  }, [messages])

  const autoGrow = useCallback(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = "auto"
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`
  }, [])

  const send = async () => {
    const query = input.trim()
    if (!query || sending || !user) return
    if (!currentRepo) {
      toast.error("Select an indexed repository first")
      return
    }

    const userMsg: ChatMessageType = {
      id: crypto.randomUUID(),
      role: "user",
      content: query,
      timestamp: Date.now(),
    }
    const pendingMsg: ChatMessageType = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: "",
      pending: true,
    }
    setMessages((m) => [...m, userMsg, pendingMsg])
    setInput("")
    setSending(true)
    requestAnimationFrame(autoGrow)

    try {
      const { jobID } = await retrieve({ user_id: user.email, user_query: query, repo_url: currentRepo })
      const result = (await poll(jobID)) as { answer?: string; sources?: ChatSource[] } | string

      const answer =
        typeof result === "string" ? result : result?.answer ?? "I couldn't find an answer for that."
      const sources = typeof result === "string" ? undefined : result?.sources

      setMessages((m) =>
        m.map((msg) =>
          msg.id === pendingMsg.id
            ? { ...msg, content: answer, sources, pending: false, timestamp: Date.now() }
            : msg,
        ),
      )
    } catch (err) {
      const message = extractErrorMessage(err)
      setMessages((m) =>
        m.map((msg) =>
          msg.id === pendingMsg.id
            ? { ...msg, content: message, error: true, pending: false, timestamp: Date.now() }
            : msg,
        ),
      )
      toast.error(message)
    } finally {
      setSending(false)
    }
  }

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <Layout fill>
      <div className="flex min-h-0 flex-1 flex-col md:flex-row">
        <RepoSidebar />

        <section className="flex min-h-0 min-w-0 flex-1 flex-col">
          {/* Active repo bar */}
          <div className="flex items-center gap-3 border-b border-border/50 bg-background/50 backdrop-blur-sm px-6 py-3 text-sm">
            <Github className="h-4 w-4 text-primary" />
            {currentRepo ? (
              <span className="truncate font-medium text-foreground">{shortRepoName(currentRepo)}</span>
            ) : (
              <span className="text-muted-foreground">No repository selected</span>
            )}
            
            {config?.modelName && (
              <div className="ml-auto flex items-center gap-2 text-xs text-muted-foreground">
                <Zap className="h-3 w-3" />
                <span>Using: <span className="font-medium text-foreground">{config.modelName}</span></span>
              </div>
            )}
            
            {messages.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                className="ml-auto h-8 gap-2 text-xs text-muted-foreground hover:text-foreground"
                onClick={() => setMessages([])}
              >
                <Trash2 className="h-4 w-4" />
                Clear
              </Button>
            )}
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="min-h-0 flex-1 overflow-y-auto bg-gradient-to-b from-background via-background to-background/95">
            {messages.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center gap-8 px-6 py-12 text-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-3xl bg-gradient-to-br from-primary/20 to-primary/10">
                  <MessageSquare className="h-8 w-8 text-primary" />
                </div>
                <div className="max-w-md space-y-3">
                  <h2 className="text-balance text-2xl font-bold text-foreground">
                    Ask anything about your codebase
                  </h2>
                  <p className="text-pretty text-base leading-relaxed text-muted-foreground">
                    {currentRepo
                      ? "Your repository is indexed and ready. Start with a question below or type your own."
                      : "Index a repository from the sidebar to get started."}
                  </p>
                </div>
                {currentRepo && (
                  <div className="grid w-full max-w-lg grid-cols-1 gap-3 sm:grid-cols-2">
                    {SUGGESTIONS.map((s) => (
                      <button
                        key={s}
                        onClick={() => {
                          setInput(s)
                          textareaRef.current?.focus()
                        }}
                        className="rounded-xl border border-border/50 bg-card/50 backdrop-blur px-4 py-3.5 text-left text-sm font-medium text-card-foreground transition-all hover:border-primary/50 hover:bg-card hover:shadow-lg"
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="mx-auto flex max-w-3xl flex-col gap-6 px-6 py-8">
                {messages.map((msg) =>
                  msg.pending ? (
                    <div key={msg.id} className="flex gap-4">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg">
                        <Loader2 className="h-4 w-4 animate-spin" />
                      </div>
                      <div className="flex items-center rounded-2xl rounded-tl-sm border border-border/50 bg-card/70 backdrop-blur px-5 py-4 shadow-sm">
                        <span className="flex gap-1.5">
                          <span className="h-2.5 w-2.5 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.3s]" />
                          <span className="h-2.5 w-2.5 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.15s]" />
                          <span className="h-2.5 w-2.5 animate-bounce rounded-full bg-muted-foreground" />
                        </span>
                      </div>
                    </div>
                  ) : (
                    <ChatMessage key={msg.id} message={msg} />
                  ),
                )}
              </div>
            )}
          </div>

          {/* Composer */}
          <div className="border-t border-border/50 bg-gradient-to-t from-background to-background/95 px-6 py-5">
            <div className="mx-auto flex max-w-3xl items-end gap-3 rounded-2xl border border-border/50 bg-card/70 backdrop-blur p-4 focus-within:border-primary/50 transition-all focus-within:shadow-lg focus-within:ring-1 focus-within:ring-primary/20">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => {
                  setInput(e.target.value)
                  autoGrow()
                }}
                onKeyDown={onKeyDown}
                rows={1}
                placeholder={currentRepo ? "Ask about your code..." : "Select a repository first"}
                disabled={!currentRepo || sending}
                className="max-h-[200px] flex-1 resize-none bg-transparent px-2 py-2.5 text-sm text-foreground outline-none placeholder:text-muted-foreground disabled:opacity-50"
              />
              <Button
                size="icon"
                onClick={send}
                disabled={!input.trim() || sending || !currentRepo}
                className="h-10 w-10 shrink-0 rounded-lg shadow-md"
                aria-label="Send message"
              >
                {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              </Button>
            </div>
            <p className="mx-auto mt-3 max-w-3xl px-4 text-xs leading-relaxed text-muted-foreground/60">
              Responses are generated from your indexed repository. Press Enter to send, Shift+Enter for a new
              line.
            </p>
          </div>
        </section>
      </div>
    </Layout>
  )
}
