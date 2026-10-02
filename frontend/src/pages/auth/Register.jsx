import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Input from '../../components/common/Input.jsx'
import Button from '../../components/common/Button.jsx'
import useAuth from '../../hooks/useAuth.js'
import { useToast } from '../../context/ToastContext.jsx'
import { validateRegister, hasErrors } from '../../utils/validators.js'

const INITIAL = { name: '', email: '', phone: '', password: '', confirmPassword: '' }

export default function Register() {
  const [values, setValues] = useState(INITIAL)
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  const { register, login } = useAuth()
  const { notify } = useToast()
  const navigate = useNavigate()

  const change = (e) => {
    const { name, value } = e.target
    setValues((prev) => ({ ...prev, [name]: value }))
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: undefined }))
  }

  const submit = async (e) => {
    e.preventDefault()
    const found = validateRegister(values)
    setErrors(found)
    if (hasErrors(found)) return

    setSubmitting(true)
    try {
      await register({
        name: values.name,
        email: values.email,
        phone: values.phone,
        password: values.password,
      })
      await login(values.email, values.password)
      notify('Account created', 'success')
      navigate('/dashboard', { replace: true })
    } catch (err) {
      notify(err.message || 'Could not create the account', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="w-full max-w-sm">
        <h1 className="text-2xl">Create your account</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Takes a minute. Your password is stored only as a hash.
        </p>

        <form onSubmit={submit} className="card mt-5 space-y-4 p-5" noValidate>
          <Input label="Full name" name="name" value={values.name} onChange={change} error={errors.name} />
          <Input label="Email" name="email" type="email" autoComplete="email"
                 value={values.email} onChange={change} error={errors.email} />
          <Input label="Mobile number" name="phone" inputMode="numeric" maxLength={10}
                 value={values.phone} onChange={change} error={errors.phone} />
          <Input label="Password" name="password" type="password" autoComplete="new-password"
                 value={values.password} onChange={change} error={errors.password}
                 hint="At least 8 characters" />
          <Input label="Confirm password" name="confirmPassword" type="password"
                 autoComplete="new-password" value={values.confirmPassword}
                 onChange={change} error={errors.confirmPassword} />
          <Button type="submit" className="w-full" loading={submitting}>
            Create account
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-ink-muted">
          Already registered?{' '}
          <Link to="/login" className="font-medium text-brand hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
