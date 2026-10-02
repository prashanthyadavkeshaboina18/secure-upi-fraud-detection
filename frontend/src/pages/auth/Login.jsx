import { useState } from 'react'
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router-dom'
import Input from '../../components/common/Input.jsx'
import Button from '../../components/common/Button.jsx'
import useAuth from '../../hooks/useAuth.js'
import { useToast } from '../../context/ToastContext.jsx'
import { validateLogin, hasErrors } from '../../utils/validators.js'

export default function Login() {
  const [values, setValues] = useState({ email: '', password: '' })
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  const { login } = useAuth()
  const { notify } = useToast()
  const navigate = useNavigate()
  const location = useLocation()
  const [params] = useSearchParams()

  const change = (e) => {
    const { name, value } = e.target
    setValues((prev) => ({ ...prev, [name]: value }))
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: undefined }))
  }

  const submit = async (e) => {
    e.preventDefault()
    const found = validateLogin(values)
    setErrors(found)
    if (hasErrors(found)) return

    setSubmitting(true)
    try {
      const profile = await login(values.email, values.password)
      const target = location.state?.from || (profile.role === 'ADMIN' ? '/admin' : '/dashboard')
      navigate(target, { replace: true })
    } catch (err) {
      notify(err.message || 'Could not sign you in', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="mb-6 flex items-center gap-2">
          <svg viewBox="0 0 32 32" className="h-8 w-8">
            <path d="M16 3 5 7.5v8.2C5 22.6 9.6 27.9 16 29c6.4-1.1 11-6.4 11-13.3V7.5L16 3z" fill="#0B6B62" />
            <path d="m11 16.2 3.4 3.4L21 13" fill="none" stroke="#fff" strokeWidth="2.4"
                  strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span className="text-lg font-semibold">Secure UPI</span>
        </div>

        <h1 className="text-2xl">Sign in</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Every payment you make here is scored by a fraud-detection model.
        </p>

        {params.get('expired') && (
          <p className="mt-4 rounded-md bg-review-light px-3 py-2 text-sm text-review">
            Your session ended. Sign in again to continue.
          </p>
        )}

        <form onSubmit={submit} className="card mt-5 space-y-4 p-5" noValidate>
          <Input
            label="Email"
            name="email"
            type="email"
            autoComplete="email"
            value={values.email}
            onChange={change}
            error={errors.email}
          />
          <Input
            label="Password"
            name="password"
            type="password"
            autoComplete="current-password"
            value={values.password}
            onChange={change}
            error={errors.password}
          />
          <Button type="submit" className="w-full" loading={submitting}>
            Sign in
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-ink-muted">
          No account yet?{' '}
          <Link to="/register" className="font-medium text-brand hover:underline">
            Create one
          </Link>
        </p>
      </div>
    </div>
  )
}
