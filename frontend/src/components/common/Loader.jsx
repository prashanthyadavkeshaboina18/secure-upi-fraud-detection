export default function Loader({ label = 'Loading', fullscreen = false, rows = 0 }) {
  if (rows > 0) {
    return (
      <div className="space-y-2" aria-busy="true" aria-label={label}>
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="h-12 animate-pulse rounded-md bg-line/60" />
        ))}
      </div>
    )
  }

  const spinner = (
    <div className="flex flex-col items-center gap-3 text-ink-muted">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-line border-t-brand" />
      <p className="text-sm">{label}</p>
    </div>
  )

  if (fullscreen)
    return <div className="flex min-h-screen items-center justify-center">{spinner}</div>

  return <div className="flex justify-center py-12">{spinner}</div>
}
