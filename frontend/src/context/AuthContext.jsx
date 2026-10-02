import { createContext, useCallback, useEffect, useMemo, useState } from 'react'
import * as authService from '../services/authService.js'
import { TOKEN_KEY, USER_KEY } from '../utils/constants.js'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [initialising, setInitialising] = useState(true)

  // On a page refresh the token survives in localStorage but React state does
  // not, so we re-fetch the profile to confirm the token is still valid.
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) {
      setInitialising(false)
      return
    }

    const cached = localStorage.getItem(USER_KEY)
    if (cached) {
      try {
        setUser(JSON.parse(cached))
      } catch {
        localStorage.removeItem(USER_KEY)
      }
    }

    authService
      .getProfile()
      .then((profile) => {
        setUser(profile)
        localStorage.setItem(USER_KEY, JSON.stringify(profile))
      })
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(USER_KEY)
        setUser(null)
      })
      .finally(() => setInitialising(false))
  }, [])

  const login = useCallback(async (email, password) => {
    const data = await authService.login(email, password)
    localStorage.setItem(TOKEN_KEY, data.access_token)
    const profile = data.user ?? (await authService.getProfile())
    localStorage.setItem(USER_KEY, JSON.stringify(profile))
    setUser(profile)
    return profile
  }, [])

  const register = useCallback((payload) => authService.register(payload), [])

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({
      user,
      initialising,
      isAuthenticated: Boolean(user),
      isAdmin: user?.role === 'ADMIN',
      login,
      register,
      logout,
    }),
    [user, initialising, login, register, logout]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
