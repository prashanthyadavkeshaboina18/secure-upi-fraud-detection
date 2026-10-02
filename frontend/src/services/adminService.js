import api from './api.js'

export const getFraudStatistics = (params = {}) =>
  api.get('/api/admin/fraud-statistics', { params }).then((r) => r.data)

export const listAllTransactions = (params = {}) =>
  api.get('/api/admin/transactions', { params }).then((r) => r.data)

export const listAllAlerts = (params = {}) =>
  api.get('/api/admin/alerts', { params }).then((r) => r.data)

export const updateAlertStatus = (alertId, status) =>
  api.patch(`/api/admin/alerts/${alertId}`, { status }).then((r) => r.data)

export const listUsers = (params = {}) =>
  api.get('/api/admin/users', { params }).then((r) => r.data)

export const getModelPerformance = () =>
  api.get('/api/model/performance').then((r) => r.data)
