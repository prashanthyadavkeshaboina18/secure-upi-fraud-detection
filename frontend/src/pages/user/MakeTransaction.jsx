import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../../components/layout/PageHeader.jsx'
import TransactionForm from '../../components/transactions/TransactionForm.jsx'
import { analyseTransaction } from '../../services/transactionService.js'
import { useToast } from '../../context/ToastContext.jsx'

export default function MakeTransaction() {
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()
  const { notify } = useToast()

  const submit = async (payload) => {
    setSubmitting(true)
    try {
      const result = await analyseTransaction(payload)
      // Pass the result through router state so the result screen renders
      // instantly; it re-fetches by ID if the page is reloaded directly.
      navigate(`/pay/result/${result.transaction_id}`, { state: { result } })
    } catch (err) {
      notify(err.message || 'The payment could not be analysed', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader
        title="Make a payment"
        description="Fill in the details and the model will score the payment before it completes."
      />
      <div className="card p-5">
        <TransactionForm onSubmit={submit} submitting={submitting} />
      </div>
      <p className="mt-4 text-xs text-ink-muted">
        This is a simulation built for academic evaluation. No bank, PSP or UPI
        network is connected, and no money is transferred.
      </p>
    </div>
  )
}
