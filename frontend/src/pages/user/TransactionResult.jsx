import { useState } from 'react'
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import RiskGauge from '../../components/dashboard/RiskGauge.jsx'
import ReasonList from '../../components/transactions/ReasonList.jsx'
import Button from '../../components/common/Button.jsx'
import Loader from '../../components/common/Loader.jsx'
import ErrorState from '../../components/common/ErrorState.jsx'
import useFetch from '../../hooks/useFetch.js'
import { useToast } from '../../context/ToastContext.jsx'
import {
  getTransaction,
  confirmTransaction,
  cancelTransaction,
} from '../../services/transactionService.js'
import { formatCurrency } from '../../utils/formatters.js'
import { DECISIONS } from '../../utils/constants.js'
import { decisionHeadline, decisionSubline, riskStyle } from '../../utils/riskHelpers.js'

export default function TransactionResult() {
  const { transactionId } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const { notify } = useToast()

  const passed = location.state?.result
  const [result, setResult] = useState(passed || null)
  const [working, setWorking] = useState(false)

  const fetched = useFetch(
    () => getTransaction(transactionId),
    [transactionId],
    { skip: Boolean(passed) }
  )

  const data = result || fetched.data

  if (!data && fetched.loading) return <Loader label="Loading the result" />
  if (!data && fetched.error)
    return <ErrorState message={fetched.error} onRetry={fetched.reload} />
  if (!data) return null

  const style = riskStyle(data.risk_level)
  const blocked = data.decision === DECISIONS.BLOCKED
  const needsReview = data.decision === DECISIONS.REVIEW

  const confirm = async () => {
    setWorking(true)
    try {
      const updated = await confirmTransaction(data.transaction_id)
      setResult(updated)
      notify('Payment confirmed', 'success')
    } catch (err) {
      notify(err.message || 'Could not confirm the payment', 'error')
    } finally {
      setWorking(false)
    }
  }

  const cancel = async () => {
    setWorking(true)
    try {
      await cancelTransaction(data.transaction_id)
      notify('Payment cancelled', 'info')
      navigate('/transactions')
    } catch (err) {
      notify(err.message || 'Could not cancel the payment', 'error')
    } finally {
      setWorking(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <div className={`card border-t-4 p-6 ${style.border}`}>
        <div className="flex flex-col items-center text-center">
          <RiskGauge score={data.risk_score} level={data.risk_level} />
          <h1 className={`mt-4 text-xl ${style.text}`}>{decisionHeadline(data.decision)}</h1>
          <p className="mt-1 max-w-sm text-sm text-ink-muted">{decisionSubline(data.decision)}</p>
        </div>

        <dl className="mt-6 grid gap-x-6 gap-y-3 border-t border-line pt-5 sm:grid-cols-2">
          <div>
            <dt className="text-xs text-ink-muted">Amount</dt>
            <dd className="text-sm font-medium tabular-nums">{formatCurrency(data.amount)}</dd>
          </div>
          <div>
            <dt className="text-xs text-ink-muted">Receiver</dt>
            <dd className="text-sm">{data.receiver_vpa}</dd>
          </div>
          <div>
            <dt className="text-xs text-ink-muted">Transaction ID</dt>
            <dd className="font-mono text-sm">{data.transaction_id}</dd>
          </div>
          <div>
            <dt className="text-xs text-ink-muted">Model</dt>
            <dd className="text-sm">{data.model_version || '—'}</dd>
          </div>
        </dl>

        {(blocked || needsReview) && (
          <div className="mt-5 border-t border-line pt-5">
            <ReasonList reasons={data.reasons} tone={blocked ? 'blocked' : 'review'} />
          </div>
        )}

        <div className="mt-6 flex flex-wrap gap-3 border-t border-line pt-5">
          {needsReview && (
            <>
              <Button onClick={confirm} loading={working}>Yes, this was me</Button>
              <Button variant="secondary" onClick={cancel} disabled={working}>
                Cancel the payment
              </Button>
            </>
          )}
          {!needsReview && (
            <>
              <Link
                to="/pay"
                className="rounded-md bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark"
              >
                Make another payment
              </Link>
              <Link
                to="/transactions"
                className="rounded-md border border-line px-4 py-2 text-sm font-medium hover:bg-canvas"
              >
                View all payments
              </Link>
            </>
          )}
        </div>

        {blocked && (
          <p className="mt-4 rounded-md bg-blocked-light px-3 py-2 text-xs text-blocked">
            An alert has been raised and sent to the monitoring team. If this was
            you, contact support to release the payment.
          </p>
        )}
      </div>
    </div>
  )
}
