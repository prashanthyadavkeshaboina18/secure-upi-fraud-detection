export const TOKEN_KEY = 'secure_upi_token'
export const USER_KEY = 'secure_upi_user'

export const ROLES = { USER: 'USER', ADMIN: 'ADMIN' }

export const RISK_LEVELS = { LOW: 'LOW', MEDIUM: 'MEDIUM', HIGH: 'HIGH' }

export const DECISIONS = {
  APPROVED: 'APPROVED',
  REVIEW: 'REVIEW',
  BLOCKED: 'BLOCKED',
}

export const TRANSACTION_TYPES = [
  { value: 'P2P', label: 'Send to person' },
  { value: 'P2M', label: 'Pay a merchant' },
  { value: 'BILL', label: 'Bill payment' },
  { value: 'RECHARGE', label: 'Mobile recharge' },
]

export const MERCHANT_CATEGORIES = [
  'Groceries',
  'Fuel',
  'Food & Dining',
  'Shopping',
  'Utilities',
  'Travel',
  'Entertainment',
  'Healthcare',
  'Education',
  'Transfer',
]

export const DEVICE_TYPES = [
  { value: 'ANDROID', label: 'Android phone' },
  { value: 'IOS', label: 'iPhone' },
  { value: 'WEB', label: 'Web browser' },
]

export const CITIES = [
  'Hyderabad', 'Bengaluru', 'Mumbai', 'Delhi', 'Chennai',
  'Pune', 'Kolkata', 'Jaipur', 'Lucknow', 'Kochi',
]

// UPI per-transaction ceiling used for client-side validation.
// The backend enforces the same limit; this is only for fast feedback.
export const MAX_TRANSACTION_AMOUNT = 100000

export const PAGE_SIZE = 10
