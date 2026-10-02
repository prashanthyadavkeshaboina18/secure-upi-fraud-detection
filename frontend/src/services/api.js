import axios from 'axios'
import { TOKEN_KEY, USER_KEY } from '../utils/constants.js'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 20000,
})

// Attach the JWT to every outgoing request.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

/**
 * Normalise every failure into { status, message } so components never have to
 * dig through axios internals. A 401 means the token is gone or expired, so we
 * clear the session and send the person back to the login screen.
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status

    if (status === 401 && !window.location.pathname.startsWith('/login')) {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
      window.location.assign('/login?expired=1')
    }

    const detail = error.response?.data?.detail
    let message = 'Something went wrong. Try again.'

    if (typeof detail === 'string') message = detail
    else if (Array.isArray(detail) && detail[0]?.msg) message = detail[0].msg
    else if (status === 403) message = 'You do not have access to this page.'
    else if (status === 404) message = 'We could not find what you asked for.'
    else if (status === 429) message = 'Too many requests. Wait a moment and retry.'
    else if (status === 503) message = 'The fraud model is not available right now.'
    else if (error.code === 'ECONNABORTED') message = 'The request timed out.'
    else if (!error.response) message = 'Cannot reach the server. Is the backend running?'

    return Promise.reject({ status, message })
  }
)

export default api
