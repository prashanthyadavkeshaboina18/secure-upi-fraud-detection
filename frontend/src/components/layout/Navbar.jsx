import { useNavigate } from 'react-router-dom'
import useAuth from '../../hooks/useAuth.js'

export default function Navbar({ onMenuClick }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const signOut = () => {
    logout()
    navigate('/login', { replace: true })
  }

  const initials = (user?.name || '?')
    .split(' ')
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()

  return (
    <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-line bg-white px-4">
      <button
        onClick={onMenuClick}
        aria-label="Open menu"
        className="rounded-md p-2 text-ink-soft hover:bg-canvas lg:hidden"
      >
        <svg viewBox="0 0 20 20" className="h-5 w-5" stroke="currentColor" strokeWidth="1.8">
          <path d="M3 6h14M3 10h14M3 14h14" strokeLinecap="round" />
        </svg>
      </button>

      <div className="ml-auto flex items-center gap-3">
        <div className="hidden text-right sm:block">
          <p className="text-sm font-medium leading-tight">{user?.name}</p>
          <p className="text-xs text-ink-muted">{user?.role === 'ADMIN' ? 'Administrator' : 'Account holder'}</p>
        </div>
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-light text-xs font-semibold text-brand-dark">
          {initials}
        </div>
        <button
          onClick={signOut}
          className="rounded-md border border-line px-3 py-1.5 text-sm text-ink-soft hover:bg-canvas"
        >
          Sign out
        </button>
      </div>
    </header>
  )
}
