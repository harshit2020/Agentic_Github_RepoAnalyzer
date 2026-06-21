import { Link, useNavigate } from "react-router-dom"
import { LogOut, Settings as SettingsIcon, User as UserIcon, Boxes } from "lucide-react"
import { useAuth } from "@/context/AuthContext"
import { getInitials } from "@/lib/utils"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function Header() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6">
        <Link to="/chat" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/15 text-primary">
            <Boxes className="h-5 w-5" />
          </span>
          <span className="text-base font-semibold tracking-tight">
            Repo<span className="text-primary">Analyzer</span>
          </span>
        </Link>

        {user && (
          <DropdownMenu>
            <DropdownMenuTrigger className="rounded-full outline-none ring-offset-background focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
              <Avatar className="h-9 w-9 border border-border">
                {user.avatar && <AvatarImage src={user.avatar || "/placeholder.svg"} alt={user.username} />}
                <AvatarFallback className="bg-primary text-primary-foreground">
                  {getInitials(user.username || user.email)}
                </AvatarFallback>
              </Avatar>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel className="px-3 py-3">
                <div className="flex flex-col">
                  <span className="truncate text-sm font-medium">{user.username}</span>
                  <span className="truncate text-xs font-normal text-muted-foreground">{user.email}</span>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="px-3 py-2" onSelect={() => navigate("/profile")}>
                <UserIcon className="text-muted-foreground" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem className="px-3 py-2" onSelect={() => navigate("/settings")}>
                <SettingsIcon className="text-muted-foreground" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="px-3 py-2 text-destructive focus:bg-destructive/10 focus:text-destructive"
                onSelect={handleLogout}
              >
                <LogOut />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
    </header>
  )
}
