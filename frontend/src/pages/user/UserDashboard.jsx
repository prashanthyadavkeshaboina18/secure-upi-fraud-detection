import { Link } from 'react-router-dom'
import PageHeader from '../../components/layout/PageHeader.jsx'
import KPICard from '../../components/dashboard/KPICard.jsx'
import RiskBadge from '../../components/dashboard/RiskBadge.jsx'
import TransactionTable from '../../components/transactions/TransactionTable.jsx'
import Loader from '../../components/common/Loader.jsx'
import ErrorState from '../../components/common/ErrorState.jsx'
import useFetch from '../../hooks/useFetch.js'
import useAuth from '../../hooks/useAuth.js'
import { getUserStats } from '../../services/dashboardService.js'
import { listTransactions } from '../../services/transactionService.js'
import { formatNumber } from '../../utils/formatters.js'

export default function UserDashboard() {
  const { user } = useAuth()
  const stats = useFetch(() => getUserStats(), [])
  const recent = useFetch(() => listTransactions({ limit: 5, skip: 0 }), [])

  if (stats.loading) return <Loader label="Loading your overview" />
  if (stats.error) return <ErrorState message={stats.error} onRetry={stats.reload} />

  const s = stats.data || {}

  return (
    <>
      <PageHeader
        title={`Hello, ${user?.name?.split(' ')[0] || 'there'}`}
        description="A summary of your payments and how the fraud model scored them."
        action={
          <Link to="/pay" className="rounded-md bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark">
            Make a payment
          </Link>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KPICard label="Total payments" value={formatNumber(s.total_transactions)} />
        <KPICard label="Approved" value={formatNumber(s.approved_transactions)} tone="approved" />
        <KPICard label="Needed verification" value={formatNumber(s.review_transactions)} tone="review" />
        <KPICard label="Blocked" value={formatNumber(s.blocked_transactions)} tone="blocked"
                 caption={s.open_alerts ? `${s.open_alerts} open alerts` : undefined} />
      </div>

      <div className="card mt-4 flex flex-wrap items-center justify-between gap-3 p-4">
        <div>
          <p className="text-sm font-medium">Your current account risk</p>
          <p className="mt-0.5 text-xs text-ink-muted">
            Based on the average risk score of your recent payments.
          </p>
        </div>
        <RiskBadge level={s.current_risk_level} score={s.current_risk_score} />
      </div>

      <section className="card mt-6">
        <div className="flex items-center justify-between border-b border-line px-4 py-3">
          <h2 className="text-sm font-semibold">Recent payments</h2>
          <Link to="/transactions" className="text-sm text-brand hover:underline">View all</Link>
        </div>
        <TransactionTable
          transactions={recent.data?.items || []}
          loading={recent.loading}
          error={recent.error}
          onRetry={recent.reload}
          emptyActionLabel="Make a payment"
          emptyActionTo="/pay"
        />
      </section>
    </>
  )
}
