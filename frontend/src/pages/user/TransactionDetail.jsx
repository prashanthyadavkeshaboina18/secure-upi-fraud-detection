import { Link, useParams } from 'react-router-dom'
import PageHeader from '../../components/layout/PageHeader.jsx'
import RiskGauge from '../../components/dashboard/RiskGauge.jsx'
import DecisionBadge from '../../components/dashboard/DecisionBadge.jsx'
import ReasonList from '../../components/transactions/ReasonList.jsx'
import Loader from '../../components/common/Loader.jsx'
import ErrorState from '../../components/common/ErrorState.jsx'
import useFetch from '../../hooks/useFetch.js'
import { getTransaction } from '../../services/transactionService.js'
import { formatCurrency, formatDateTime } from '../../utils/formatters.js'

function Detail({ term, value, mono = false }) {
  return (
    <div>
      <dt className="text-xs text-ink-muted">{term}</dt>
      <dd className={`text-sm ${mono ? 'font-mono' : ''}`}>{value ?? '—'}</dd>
    </div>
  )
}

export default function TransactionDetail() {
  const { transactionId } = useParams()
  const { data, loading, error, reload } = useFetch(
    () => getTransaction(transactionId),
    [transactionId]
  )

  if (loading) return <Loader label="Loading the transaction" />
  if (error) return <ErrorState message={error} onRetry={reload} />
  if (!data) return null

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader
        title="Transaction detail"
        description={data.transaction_id}
        action={
          <Link to="/transactions" className="rounded-md border border-line px-3 py-2 text-sm hover:bg-canvas">
            Back to list
          </Link>
        }
      />

      <div className="grid gap-4 md:grid-cols-[minmax(0,1fr)_16rem]">
        <section className="card p-5">
          <dl className="grid gap-x-6 gap-y-4 sm:grid-cols-2">
            <Detail term="Amount" value={formatCurrency(data.amount)} />
            <Detail term="Receiver UPI ID" value={data.receiver_vpa} />
            <Detail term="Receiver name" value={data.merchant_name} />
            <Detail term="Category" value={data.merchant_category} />
            <Detail term="Payment type" value={data.transaction_type} />
            <Detail term="City" value={data.location_city} />
            <Detail term="Device" value={`${data.device_type} · ${data.device_id}`} />
            <Detail term="Time" value={formatDateTime(data.created_at)} />
            <Detail term="Fraud probability"
                    value={data.fraud_probability?.toFixed(4)} mono />
            <Detail term="Model version" value={data.model_version} mono />
          </dl>

          {data.reasons?.length > 0 && (
            <div className="mt-6 border-t border-line pt-5">
              <ReasonList reasons={data.reasons} tone={data.decision === 'BLOCKED' ? 'blocked' : 'review'} />
            </div>
          )}
        </section>

        <aside className="card flex flex-col items-center gap-4 p-5">
          <RiskGauge score={data.risk_score} level={data.risk_level} />
          <DecisionBadge decision={data.decision} />
        </aside>
      </div>
    </div>
  )
}
