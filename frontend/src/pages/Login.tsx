import { useState, type FormEvent } from "react"
import { Link, useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { Loader2 } from "lucide-react"
import { useAuth } from "@/context/AuthContext"
import { extractErrorMessage, getUserSetup, login as loginApi } from "@/services/api"
import type { SetupConfig } from "@/services/types"
import { AuthShell } from "@/components/shared/AuthShell"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function Login() {
  const navigate = useNavigate()
  const { login, setSetupComplete, setConfig, setCurrentRepo, setIndexedRepos } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      toast.error("Please enter your email and password.")
      return
    }

    setLoading(true)
    try {
      const data = await loginApi({ email, password })
      const username: string = data?.username || data?.user?.username || email.split("@")[0]
      const avatar: string | undefined = data?.avatar || data?.user?.avatar
      login({ email, username, avatar })

      // Check if this user already has a saved setup.
      try {
        const setup = await getUserSetup(email)
        const config: SetupConfig | undefined = setup?.config || setup?.data || (setup && Object.keys(setup).length ? setup : undefined)
        const hasSetup = Boolean(config && (config.modelName || config.db_flag !== undefined))

        if (hasSetup) {

          setConfig(config as SetupConfig)
          if (setup?.repo_url) {
          
            setCurrentRepo(setup.repo_url)
            setIndexedRepos([setup.repo_url])
          }
          setSetupComplete(true)
          toast.success("Welcome back!")
          navigate("/chat")
          return
        }
      } catch {
        // No existing setup found — fall through to setup flow.
      }

      setSetupComplete(false)
      toast.success("Logged in. Let's set things up.")
      navigate("/setup")
    } catch (err) {
      toast.error(extractErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <AuthShell title="Welcome back" subtitle="Sign in to analyze and chat with your repositories.">
      <Card className="border border-border/50 bg-gradient-to-b from-card to-card/95 shadow-2xl backdrop-blur-xl w-full">
        <CardContent className="pt-10 pb-10 px-8">
          <form onSubmit={handleSubmit} className="grid gap-6">
            <div className="grid gap-3">
              <Label htmlFor="email" className="text-sm font-medium">Email address</Label>
              <Input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="h-10 text-sm"
              />
            </div>
            <div className="grid gap-3">
              <Label htmlFor="password" className="text-sm font-medium">Password</Label>
              <Input
                id="password"
                type="password"
                autoComplete="current-password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="h-10 text-sm"
              />
            </div>
            <Button type="submit" className="mt-2 h-10 w-full font-medium" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {loading ? "Signing in..." : "Sign in"}
            </Button>
          </form>

          <div className="mt-6 border-t border-border/30 pt-6">
            <p className="text-center text-sm text-muted-foreground">
              {"Don't have an account? "}
              <Link to="/signup" className="font-semibold text-primary hover:text-primary/80 transition-colors">
                Sign up
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </AuthShell>
  )
}
