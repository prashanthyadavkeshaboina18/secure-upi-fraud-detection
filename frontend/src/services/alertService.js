import api from './api.js'

export const listMyAlerts = (params = {}) =>
  api.get('/api/alerts', { params }).then((r) => r.data)
