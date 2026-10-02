import { NavLink } from 'react-router-dom'
import useAuth from '../../hooks/useAuth.js'

const linkClass = ({ isActive }) =>
  `block rounded-md px-3 py-2 text-sm transition-colors ${
    isActive ? 'bg-brand-light font-medium text-brand-dark' : 'text-ink-soft hover:bg-canvas'
  }`

export default function Sidebar({ open, onNavigate }) {
  const { isAdmin } = useAuth()

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 z-30 bg-ink/30 lg:hidden"
          onClick={onNavigate}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 w-60 shrink-0 border-r border-line bg-white
                    px-3 py-4 transition-transform lg:static lg:translate-x-0
                    ${open ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="mb-6 flex items-center gap-2 px-2">
          <svg viewBox="0 0 32 32" className="h-7 w-7">
            <path d="M16 3 5 7.5v8.2C5 22.6 9.6 27.9 16 29c6.4-1.1 11-6.4 11-13.3V7.5L16 3z" fill="#0B6B62" />
            <path d="m11 16.2 3.4 3.4L21 13" fill="none" stroke="#fff" strokeWidth="2.4"
                  strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span className="font-semibold">Secure UPI</span>
        </div>

        <nav className="space-y-1" onClick={onNavigate}>
          <NavLink to="/dashboard" className={linkClass}>Overview</NavLink>
          <NavLink to="/pay" className={linkClass}>Make a payment</NavLink>
          <NavLink to="/transactions" className={linkClass}>My transactions</NavLink>
          <NavLink to="/alerts" className={linkClass}>My alerts</NavLink>

          {isAdmin && (
            <div className="pt-5">
              <p className="px-3 pb-1 text-xs font-semibold text-ink-muted">Administration</p>
              <NavLink to="/admin" end className={linkClass}>Fraud overview</NavLink>
              <NavLink to="/admin/transactions" className={linkClass}>All transactions</NavLink>
              <NavLink to="/admin/alerts" className={linkClass}>Alert queue</NavLink>
              <NavLink to="/admin/users" className={linkClass}>Users</NavLink>
              <NavLink to="/admin/model" className={linkClass}>Model performance</NavLink>
            </div>
          )}
        </nav>

        <p className="absolute bottom-4 left-3 right-3 rounded-md bg-canvas px-3 py-2 text-xs text-ink-muted">
          Academic prototype. No real money moves and no bank system is connected.
        </p>
      </aside>
    </>
  )
}
