import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-3 px-4 text-center">
      <h1 className="text-2xl">This page does not exist</h1>
      <p className="text-sm text-ink-muted">The link may be out of date or mistyped.</p>
      <Link to="/dashboard" className="rounded-md bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark">
        Go to overview
      </Link>
    </div>
  )
}
