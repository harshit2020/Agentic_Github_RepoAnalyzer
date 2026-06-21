export function Footer() {
  return (
    <footer className="border-t border-border py-6">
      <div className="mx-auto flex max-w-7xl items-center justify-center px-4 text-xs text-muted-foreground sm:px-6">
        <p>&copy; {new Date().getFullYear()} RepoAnalyzer. Built for developers.</p>
      </div>
    </footer>
  )
}
