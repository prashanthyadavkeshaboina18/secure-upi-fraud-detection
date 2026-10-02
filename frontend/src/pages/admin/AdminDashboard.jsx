import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Legend,
  Pie, PieChart, Tooltip, XAxis, YAxis,
} from 'recharts'
import PageHeader from '../../components/layout/PageHeader.jsx'
import KPICard from '../../components/dashboard/KPICard.jsx'
import ChartCard from '../../components/dashboard/ChartCard.jsx'
import TransactionTable from '../../components/transactions/TransactionTable.jsx'
import Loader from '../../components/common/Loader.jsx'
import ErrorState from '../../components/common/ErrorState.jsx'
import useFetch from '../../hooks/useFetch.js'
import { getFraudStatistics, listAllTransactions } from '../../services/adminService.js'
import { formatNumber, formatPercent } from '../../utils/formatters.js'

const AXIS = { fontSize: 12, fill: '#6B7789' }
const GRID = '#E2E7EE'
const SERIES = ['#0B6B62', '#B32B2B', '#B26A00', '#3A4657', '#6B7789']

export default function AdminDashboard() {
  const stats = useFetch(() => getFraudStatistics(), [])
  const highRisk = useFetch(
    () => listAllTransactions({ risk_level: 'HIGH', limit: 8, skip: 0 }),
    []
  )

  if (stats.loading) return <Loader label="Loading fraud statistics" />
  if (stats.error) return <ErrorState message={stats.error} onRetry={stats.reload} />

  const s = stats.data || {}
  const overTime = s.transactions_over_time || []
  const byType = s.fraud_by_transaction_type || []
  const byLocation = s.fraud_by_location || []
  const byDevice = s.fraud_by_device || []
  const riskSplit = s.risk_distribution || []

  return (
    <>
      <PageHeader
        title="Fraud overview"
        description="Aggregated across every account on the platform."
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <KPICard label="Transactions" value={formatNumber(s.total_transactions)} />
        <KPICard label="Flagged as fraud" value={formatNumber(s.fraud_transactions)} tone="blocked" />
        <KPICard label="Fraud rate" value={formatPercent(s.fraud_rate, 2)}
                 caption="Share of payments the model flagged" />
        <KPICard label="Blocked" value={formatNumber(s.blocked_transactions)} tone="blocked" />
        <KPICard label="High risk" value={formatNumber(s.high_risk_transactions)} tone="review" />
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <ChartCard
          title="Transactions over time"
          description="Total payments against those the model flagged"
          isEmpty={!overTime.length}
        >
          <AreaChart data={overTime} margin={{ top: 4, right: 8, bottom: 0, left: -18 }}>
            <CartesianGrid stroke={GRID} vertical={false} />
            <XAxis dataKey="date" tick={AXIS} tickLine={false} axisLine={{ stroke: GRID }} />
            <YAxis tick={AXIS} tickLine={false} axisLine={false} />
            <Tooltip />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Area type="monotone" dataKey="total" name="All payments"
                  stroke={SERIES[0]} fill={SERIES[0]} fillOpacity={0.12} />
            <Area type="monotone" dataKey="fraud" name="Flagged"
                  stroke={SERIES[1]} fill={SERIES[1]} fillOpacity={0.18} />
          </AreaChart>
        </ChartCard>

        <ChartCard
          title="Risk distribution"
          description="How the model scored every payment"
          isEmpty={!riskSplit.length}
        >
          <PieChart>
            <Pie data={riskSplit} dataKey="count" nameKey="risk_level"
                 innerRadius={55} outerRadius={90} paddingAngle={2}>
              {riskSplit.map((entry, index) => (
                <Cell key={entry.risk_level} fill={SERIES[index % SERIES.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend wrapperStyle={{ fontSize: 12 }} />
          </PieChart>
        </ChartCard>

        <ChartCard title="Flagged payments by type" isEmpty={!byType.length}>
          <BarChart data={byType} margin={{ top: 4, right: 8, bottom: 0, left: -18 }}>
            <CartesianGrid stroke={GRID} vertical={false} />
            <XAxis dataKey="transaction_type" tick={AXIS} tickLine={false} axisLine={{ stroke: GRID }} />
            <YAxis tick={AXIS} tickLine={false} axisLine={false} />
            <Tooltip />
            <Bar dataKey="fraud_count" name="Flagged" fill={SERIES[1]} radius={[3, 3, 0, 0]} />
          </BarChart>
        </ChartCard>

        <ChartCard title="Flagged payments by city" isEmpty={!byLocation.length}>
          <BarChart data={byLocation} layout="vertical" margin={{ top: 4, right: 12, bottom: 0, left: 24 }}>
            <CartesianGrid stroke={GRID} horizontal={false} />
            <XAxis type="number" tick={AXIS} tickLine={false} axisLine={{ stroke: GRID }} />
            <YAxis type="category" dataKey="location_city" tick={AXIS} tickLine={false} axisLine={false} width={80} />
            <Tooltip />
            <Bar dataKey="fraud_count" name="Flagged" fill={SERIES[3]} radius={[0, 3, 3, 0]} />
          </BarChart>
        </ChartCard>

        <ChartCard title="Flagged payments by device type" isEmpty={!byDevice.length}>
          <BarChart data={byDevice} margin={{ top: 4, right: 8, bottom: 0, left: -18 }}>
            <CartesianGrid stroke={GRID} vertical={false} />
            <XAxis dataKey="device_type" tick={AXIS} tickLine={false} axisLine={{ stroke: GRID }} />
            <YAxis tick={AXIS} tickLine={false} axisLine={false} />
            <Tooltip />
            <Bar dataKey="fraud_count" name="Flagged" fill={SERIES[2]} radius={[3, 3, 0, 0]} />
          </BarChart>
        </ChartCard>
      </div>

      <section className="card mt-6">
        <div className="border-b border-line px-4 py-3">
          <h2 className="text-sm font-semibold">Latest high-risk payments</h2>
        </div>
        <TransactionTable
          transactions={highRisk.data?.items || []}
          loading={highRisk.loading}
          error={highRisk.error}
          onRetry={highRisk.reload}
          showUser
          emptyTitle="No high-risk payments"
          emptyDescription="Nothing has crossed the high-risk threshold yet."
        />
      </section>
    </>
  )
}
