import { Navigate, Outlet } from 'react-router-dom'
import useAuth from '../../hooks/useAuth.js'

export default function RoleRoute({ role }) {
  const { user } = useAuth()
  if (user?.role !== role) return <Navigate to="/dashboard" replace />
  return <Outlet />
}
