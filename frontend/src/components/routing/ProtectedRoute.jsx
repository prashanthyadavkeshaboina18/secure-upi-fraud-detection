import { Navigate, Outlet, useLocation } from 'react-router-dom'
import useAuth from '../../hooks/useAuth.js'
import Loader from '../common/Loader.jsx'

/**
 * Client-side gate. This is a usability measure only — the real protection is
 * the JWT dependency on every FastAPI route. Hiding a page does not secure it.
 */
export default function ProtectedRoute() {
  const { isAuthenticated, initialising } = useAuth()
  const location = useLocation()

  if (initialising) return <Loader fullscreen label="Checking your session" />

  if (!isAuthenticated)
    return <Navigate to="/login" replace state={{ from: location.pathname }} />

  return <Outlet />
}
