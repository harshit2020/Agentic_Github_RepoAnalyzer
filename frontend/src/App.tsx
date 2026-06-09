import { Navigate, Route, Routes } from "react-router-dom"
import { Toaster } from "sonner"
import { AuthProvider, useAuth } from "@/context/AuthContext"
import type { ReactNode } from "react"
import Login from "@/pages/Login"
import Signup from "@/pages/Signup"
import Setup from "@/pages/Setup"
import Chat from "@/pages/Chat"
import Settings from "@/pages/Settings"
import Profile from "@/pages/Profile"

/**
 * Protected route:
 * - no user                       -> /login
 * - user but setup not complete    -> /setup
 * - user and setup complete        -> render
 * `allowIncompleteSetup` lets the /setup route itself render for logged-in users.
 */
function Protected({
  children,
  allowIncompleteSetup = false,
}: {
  children: ReactNode
  allowIncompleteSetup?: boolean
}) {
  const { user, isSetupComplete } = useAuth()

  if (!user) return <Navigate to="/login" replace />
  if (!isSetupComplete && !allowIncompleteSetup) return <Navigate to="/setup" replace />
  return <>{children}</>
}

function PublicOnly({ children }: { children: ReactNode }) {
  const { user, isSetupComplete } = useAuth()
  if (user) return <Navigate to={isSetupComplete ? "/chat" : "/setup"} replace />
  return <>{children}</>
}

function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <PublicOnly>
            <Login />
          </PublicOnly>
        }
      />
      <Route
        path="/login"
        element={
          <PublicOnly>
            <Login />
          </PublicOnly>
        }
      />
      <Route
        path="/signup"
        element={
          <PublicOnly>
            <Signup />
          </PublicOnly>
        }
      />
      <Route
        path="/setup"
        element={
          <Protected allowIncompleteSetup>
            <Setup />
          </Protected>
        }
      />
      <Route
        path="/chat"
        element={
          <Protected>
            <Chat />
          </Protected>
        }
      />
      <Route
        path="/settings"
        element={
          <Protected>
            <Settings />
          </Protected>
        }
      />
      <Route
        path="/profile"
        element={
          <Protected>
            <Profile />
          </Protected>
        }
      />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
      <Toaster theme="dark" position="top-right" richColors closeButton />
    </AuthProvider>
  )
}
