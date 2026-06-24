import { useState, type FormEvent, useRef } from "react"
import { Link, useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { Loader2, Upload, X } from "lucide-react"
import { extractErrorMessage, signup as signupApi } from "@/services/api"
import { AuthShell } from "@/components/shared/AuthShell"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function Signup() {
  const navigate = useNavigate()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [username, setUsername] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [avatar, setAvatar] = useState<File | null>(null)
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const passwordMismatch = confirmPassword.length > 0 && password !== confirmPassword

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        toast.error("Image size must be less than 5MB")
        return
      }
      // Validate file type
      if (!file.type.startsWith("image/")) {
        toast.error("Please upload an image file")
        return
      }
      setAvatar(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const removeAvatar = () => {
    setAvatar(null)
    setAvatarPreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!username || !email || !password || !avatar) {
      toast.error("Please fill in all fields including avatar.")
      return
    }
    if (password !== confirmPassword) {
      toast.error("Passwords do not match.")
      return
    }

    setLoading(true)
    try {
      await signupApi({ username, email, password, avatar })
      toast.success("Account created. Please sign in.")
      navigate("/login")
    } catch (err) {
      toast.error(extractErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell title="Create your account" subtitle="Start indexing repositories and chatting with your code.">
      <Card className="border border-border/50 bg-gradient-to-b from-card to-card/95 shadow-2xl backdrop-blur-xl w-full">
        <CardContent className="pt-10 pb-10 px-8">
          <form onSubmit={handleSubmit} className="grid gap-6">
            <div className="grid gap-3">
              <Label htmlFor="avatar" className="text-sm font-medium">Profile Picture</Label>
              <div className="border-2 border-dashed border-border/50 rounded-lg p-4 text-center hover:border-border/80 transition-colors cursor-pointer">
                {avatarPreview ? (
                  <div className="relative inline-block">
                    <img src={avatarPreview} alt="Avatar preview" className="h-32 w-32 rounded-lg object-cover" />
                    <button
                      type="button"
                      onClick={removeAvatar}
                      className="absolute -top-2 -right-2 bg-destructive text-white rounded-full p-1 hover:bg-destructive/80"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ) : (
                  <div
                    onClick={() => fileInputRef.current?.click()}
                    className="flex flex-col items-center gap-2 py-4"
                  >
                    <Upload className="h-6 w-6 text-muted-foreground" />
                    <div className="text-sm text-muted-foreground">
                      <p className="font-medium">Click to upload</p>
                      <p className="text-xs">PNG, JPG, GIF up to 5MB</p>
                    </div>
                  </div>
                )}
              </div>
              <input
                ref={fileInputRef}
                id="avatar"
                type="file"
                accept="image/*"
                onChange={handleAvatarChange}
                className="hidden"
              />
            </div>
            <div className="grid gap-3">
              <Label htmlFor="username" className="text-sm font-medium">Username</Label>
              <Input
                id="username"
                placeholder="janedoe"
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="h-10 text-sm"
              />
            </div>
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
                autoComplete="new-password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="h-10 text-sm"
              />
            </div>
            <div className="grid gap-3">
              <Label htmlFor="confirm" className="text-sm font-medium">Confirm Password</Label>
              <Input
                id="confirm"
                type="password"
                autoComplete="new-password"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                aria-invalid={passwordMismatch}
                className="h-10 text-sm"
              />
              {passwordMismatch && <p className="text-xs text-destructive mt-2">Passwords do not match.</p>}
            </div>
            <Button type="submit" className="mt-2 h-10 w-full font-medium" disabled={loading || passwordMismatch || !avatar}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {loading ? "Creating account..." : "Sign up"}
            </Button>
          </form>

          <div className="mt-6 border-t border-border/30 pt-6">
            <p className="text-center text-sm text-muted-foreground">
              {"Already have an account? "}
              <Link to="/login" className="font-semibold text-primary hover:text-primary/80 transition-colors">
                Sign in
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </AuthShell>
  )
}
