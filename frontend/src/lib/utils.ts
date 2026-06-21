import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** Generate initials from a name or email, e.g. "John Doe" -> "JD". */
export function getInitials(nameOrEmail: string): string {
  if (!nameOrEmail) return "?"
  const cleaned = nameOrEmail.includes("@") ? nameOrEmail.split("@")[0] : nameOrEmail
  const parts = cleaned.replace(/[._-]+/g, " ").trim().split(/\s+/)
  if (parts.length === 1) {
    return parts[0].slice(0, 2).toUpperCase()
  }
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}

/** Extract a short repo name from a GitHub URL. */
export function shortRepoName(url: string): string {
  if (!url) return ""
  try {
    const cleaned = url.replace(/\.git$/, "").replace(/\/$/, "")
    const parts = cleaned.split("/")
    const repo = parts[parts.length - 1]
    const owner = parts[parts.length - 2]
    return owner && repo ? `${owner}/${repo}` : repo
  } catch {
    return url
  }
}