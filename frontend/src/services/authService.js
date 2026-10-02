import api from './api.js'

export const register = (payload) =>
  api.post('/api/auth/register', payload).then((r) => r.data)

export const login = (email, password) =>
  api.post('/api/auth/login', { email, password }).then((r) => r.data)

export const getProfile = () => api.get('/api/auth/me').then((r) => r.data)
