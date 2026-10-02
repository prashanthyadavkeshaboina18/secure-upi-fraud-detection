import api from './api.js'

/** Core endpoint: the backend scores the transaction with the trained model. */
export const analyseTransaction = (payload) =>
  api.post('/api/transactions/predict', payload).then((r) => r.data)

/** Used by the REVIEW flow when the user confirms it really was them. */
export const confirmTransaction = (transactionId) =>
  api.post(`/api/transactions/${transactionId}/confirm`).then((r) => r.data)

export const cancelTransaction = (transactionId) =>
  api.post(`/api/transactions/${transactionId}/cancel`).then((r) => r.data)

export const listTransactions = (params = {}) =>
  api.get('/api/transactions', { params }).then((r) => r.data)

export const getTransaction = (transactionId) =>
  api.get(`/api/transactions/${transactionId}`).then((r) => r.data)
