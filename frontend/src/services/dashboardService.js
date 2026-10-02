import api from './api.js'

export const getUserStats = () =>
  api.get('/api/dashboard/stats').then((r) => r.data)
