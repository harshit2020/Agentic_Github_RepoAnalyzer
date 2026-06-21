import { useRef, useState } from "react"
import { toast } from "sonner"
import { Camera, KeyRound, Loader2, Mail, Trash2, User as UserIcon } from "lucide-react"
import { useAuth } from "@/context/AuthContext"
import { changePassword, extractErrorMessage } from "@/services/api"
import { getInitials } from "@/lib/utils"
import { Layout } from "@/components/shared/Layout"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

const MAX_AVATAR_BYTES = 2 * 1024 * 1024 // 2MB

export default function Profile() {
  const { user, updateUser } = useAuth()
  const [current, setCurrent] = useState("")
  const [next, setNext] = useState("")
  const [confirm, setConfirm] = useState("")
  const [saving, setSaving] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  if (!user) return null

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    e.target.value = "" // allow re-selecting the same file
    if (!file) return
    if (!file.type.startsWith("image/")) {
      toast.error("Please choose an image file.")
      return
    }
    if (file.size > MAX_AVATAR_BYTES) {
      toast.error("Image is too large. Please choose one under 2MB.")
      return
    }
    const reader = new FileReader()
    reader.onload = () => {
      updateUser({ avatar: reader.result as string })
      toast.success("Profile photo updated.")
    }
    reader.onerror = () => toast.error("Could not read the selected image.")
    reader.readAsDataURL(file)
  }

  const removePhoto = () => {
    updateUser({ avatar: undefined })
    toast.success("Profile photo removed.")
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!current || !next || !confirm) {
      toast.error("Please fill in all password fields.")
      return
    }
    if (next.length < 6) {
      toast.error("New password must be at least 6 characters.")
      return
    }
    if (next !== confirm) {
      toast.error("New passwords do not match.")
      return
    }

    setSaving(true)
    try {
      await changePassword({
        user_id: user.email,
        current_password: current,
        new_password: next,
      })
      toast.success("Password updated successfully.")
      setCurrent("")
      setNext("")
      setConfirm("")
    } catch (err) {
      toast.error(extractErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <Layout>
      <div className="mx-auto max-w-2xl px-6 py-12 sm:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Profile</h1>
          <p className="mt-2 text-base text-muted-foreground">Manage your account information and security.</p>
        </div>

        <div className="grid gap-6">
          {/* Account info */}
          <Card className="border border-border/50 bg-gradient-to-b from-card to-card/95 shadow-lg">
            <CardHeader className="border-b border-border/30 px-8 pt-8 pb-5">
              <CardTitle>Account</CardTitle>
              <CardDescription className="mt-1">Your profile details.</CardDescription>
            </CardHeader>
            <CardContent className="px-8 pt-8 pb-8">
              <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center">
                <div className="relative">
                  <Avatar className="h-16 w-16 border border-border">
                    {user.avatar && <AvatarImage src={user.avatar || "/placeholder.svg"} alt={user.username} />}
                    <AvatarFallback className="bg-primary text-lg text-primary-foreground">
                      {getInitials(user.username || user.email)}
                    </AvatarFallback>
                  </Avatar>
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="absolute -bottom-1 -right-1 flex h-6 w-6 items-center justify-center rounded-full border border-border bg-secondary text-secondary-foreground transition-colors hover:bg-muted"
                    aria-label="Upload profile photo"
                  >
                    <Camera className="h-3.5 w-3.5" />
                  </button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handlePhotoChange}
                  />
                </div>
                <div className="grid gap-2">
                  <div className="flex items-center gap-2 text-sm">
                    <UserIcon className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">{user.username}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Mail className="h-4 w-4" />
                    {user.email}
                  </div>
                  <div className="mt-1 flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => fileInputRef.current?.click()}>
                      <Camera className="h-3.5 w-3.5" />
                      {user.avatar ? "Change photo" : "Upload photo"}
                    </Button>
                    {user.avatar && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-muted-foreground hover:text-destructive"
                        onClick={removePhoto}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                        Remove
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Change password */}
          <Card className="border border-border/50 bg-gradient-to-b from-card to-card/95 shadow-lg">
            <CardHeader className="border-b border-border/30 px-8 pt-8 pb-5">
              <CardTitle className="flex items-center gap-2">
                <KeyRound className="h-4 w-4 text-primary" />
                Change Password
              </CardTitle>
              <CardDescription className="mt-1">Use a strong password you don&apos;t reuse elsewhere.</CardDescription>
            </CardHeader>
            <CardContent className="px-8 pt-8 pb-8">
              <form onSubmit={submit} className="grid gap-5">
                <div className="grid gap-2">
                  <Label htmlFor="current">Current password</Label>
                  <Input
                    id="current"
                    type="password"
                    value={current}
                    onChange={(e) => setCurrent(e.target.value)}
                    autoComplete="current-password"
                  />
                </div>
                <div className="grid gap-5 sm:grid-cols-2 w-full">
                  <div className="grid gap-2 w-full">
                    <Label htmlFor="next">New password</Label>
                    <Input
                      id="next"
                      type="password"
                      value={next}
                      onChange={(e) => setNext(e.target.value)}
                      autoComplete="new-password"
                    />
                  </div>
                  <div className="grid gap-2 w-full">
                    <Label htmlFor="confirm">Confirm new password</Label>
                    <Input
                      id="confirm"
                      type="password"
                      value={confirm}
                      onChange={(e) => setConfirm(e.target.value)}
                      autoComplete="new-password"
                    />
                  </div>
                </div>
                <div className="flex justify-end">
                  <Button type="submit" disabled={saving}>
                    {saving && <Loader2 className="animate-spin" />}
                    Update password
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  )
}
