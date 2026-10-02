import { MAX_TRANSACTION_AMOUNT } from './constants.js'

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/
const PHONE_RE = /^[6-9]\d{9}$/
const VPA_RE = /^[\w.-]{2,}@[a-zA-Z]{2,}$/

export function validateRegister(values) {
  const errors = {}
  if (!values.name?.trim()) errors.name = 'Enter your full name'
  if (!EMAIL_RE.test(values.email || '')) errors.email = 'Enter a valid email address'
  if (!PHONE_RE.test(values.phone || '')) errors.phone = 'Enter a 10-digit Indian mobile number'
  if ((values.password || '').length < 8)
    errors.password = 'Use at least 8 characters'
  if (values.password !== values.confirmPassword)
    errors.confirmPassword = 'Passwords do not match'
  return errors
}

export function validateLogin(values) {
  const errors = {}
  if (!EMAIL_RE.test(values.email || '')) errors.email = 'Enter a valid email address'
  if (!values.password) errors.password = 'Enter your password'
  return errors
}

export function validateTransaction(values) {
  const errors = {}
  const amount = Number(values.amount)

  if (!values.amount) errors.amount = 'Enter an amount'
  else if (Number.isNaN(amount) || amount <= 0) errors.amount = 'Amount must be more than 0'
  else if (amount > MAX_TRANSACTION_AMOUNT)
    errors.amount = `UPI allows up to ₹${MAX_TRANSACTION_AMOUNT.toLocaleString('en-IN')} per payment`

  if (!VPA_RE.test(values.receiver_vpa || ''))
    errors.receiver_vpa = 'Enter a UPI ID such as name@bank'

  if (!values.transaction_type) errors.transaction_type = 'Choose a payment type'
  if (!values.merchant_category) errors.merchant_category = 'Choose a category'
  if (!values.device_id?.trim()) errors.device_id = 'Device ID is required'
  if (!values.device_type) errors.device_type = 'Choose a device type'
  if (!values.location_city) errors.location_city = 'Choose a city'

  return errors
}

export const hasErrors = (errors) => Object.keys(errors).length > 0
