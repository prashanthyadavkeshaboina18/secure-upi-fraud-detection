import { ResponsiveContainer } from 'recharts'
import EmptyState from '../common/EmptyState.jsx'

export default function ChartCard({ title, description, height = 260, isEmpty, children }) {
  return (
    <div className="card p-4">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-ink">{title}</h3>
        {description && <p className="mt-0.5 text-xs text-ink-muted">{description}</p>}
      </div>

      {isEmpty ? (
        <EmptyState title="No data yet" description="Run a few transactions and this chart will fill in." />
      ) : (
        <div style={{ height }}>
          <ResponsiveContainer width="100%" height="100%">
            {children}
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
