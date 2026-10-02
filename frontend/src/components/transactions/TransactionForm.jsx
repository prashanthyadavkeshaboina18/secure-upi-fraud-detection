import { useState } from 'react'
import Input from '../common/Input.jsx'
import Select from '../common/Select.jsx'
import Button from '../common/Button.jsx'
import {
  TRANSACTION_TYPES,
  MERCHANT_CATEGORIES,
  DEVICE_TYPES,
  CITIES,
} from '../../utils/constants.js'
import { validateTransaction, hasErrors } from '../../utils/validators.js'

const INITIAL = {
  amount: '',
  receiver_vpa: '',
  merchant_name: '',
  transaction_type: 'P2P',
  merchant_category: 'Transfer',
  device_id: 'DEV-PRIMARY-01',
  device_type: 'ANDROID',
  location_city: 'Hyderabad',
}

export default function TransactionForm({ onSubmit, submitting }) {
  const [values, setValues] = useState(INITIAL)
  const [errors, setErrors] = useState({})

  const change = (e) => {
    const { name, value } = e.target
    setValues((prev) => ({ ...prev, [name]: value }))
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: undefined }))
  }

  const submit = (e) => {
    e.preventDefault()
    const found = validateTransaction(values)
    setErrors(found)
    if (hasErrors(found)) return
    onSubmit({ ...values, amount: Number(values.amount) })
  }

  return (
    <form onSubmit={submit} className="space-y-5" noValidate>
      <div className="grid gap-4 sm:grid-cols-2">
        <Input
          label="Amount"
          name="amount"
          type="number"
          inputMode="decimal"
          min="1"
          step="0.01"
          placeholder="0.00"
          value={values.amount}
          onChange={change}
          error={errors.amount}
          hint="UPI allows up to ₹1,00,000 per payment"
        />
        <Input
          label="Receiver UPI ID"
          name="receiver_vpa"
          placeholder="name@bank"
          value={values.receiver_vpa}
          onChange={change}
          error={errors.receiver_vpa}
        />
        <Input
          label="Receiver name"
          name="merchant_name"
          placeholder="Optional"
          value={values.merchant_name}
          onChange={change}
        />
        <Select
          label="Payment type"
          name="transaction_type"
          options={TRANSACTION_TYPES}
          value={values.transaction_type}
          onChange={change}
          error={errors.transaction_type}
        />
        <Select
          label="Category"
          name="merchant_category"
          options={MERCHANT_CATEGORIES}
          value={values.merchant_category}
          onChange={change}
          error={errors.merchant_category}
        />
        <Select
          label="City"
          name="location_city"
          options={CITIES}
          value={values.location_city}
          onChange={change}
          error={errors.location_city}
        />
        <Input
          label="Device ID"
          name="device_id"
          value={values.device_id}
          onChange={change}
          error={errors.device_id}
          hint="Change this to simulate paying from a new phone"
        />
        <Select
          label="Device type"
          name="device_type"
          options={DEVICE_TYPES}
          value={values.device_type}
          onChange={change}
          error={errors.device_type}
        />
      </div>

      <div className="flex items-center gap-3 border-t border-line pt-4">
        <Button type="submit" size="lg" loading={submitting}>
          {submitting ? 'Analysing' : 'Pay now'}
        </Button>
        <p className="text-xs text-ink-muted">
          Every payment is scored by the fraud model before it is completed.
        </p>
      </div>
    </form>
  )
}
