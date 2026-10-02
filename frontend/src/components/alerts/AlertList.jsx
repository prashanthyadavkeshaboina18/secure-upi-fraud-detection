import AlertCard from './AlertCard.jsx'
import Loader from '../common/Loader.jsx'
import EmptyState from '../common/EmptyState.jsx'
import ErrorState from '../common/ErrorState.jsx'

export default function AlertList({ alerts = [], loading, error, onRetry, onStatusChange, updatingId }) {
  if (loading) return <Loader rows={3} />
  if (error) return <ErrorState message={error} onRetry={onRetry} />
  if (!alerts.length)
    return (
      <div className="card">
        <EmptyState
          title="No alerts"
          description="Alerts appear here when the model blocks a high-risk payment."
        />
      </div>
    )

  return (
    <div className="space-y-3">
      {alerts.map((alert) => (
        <AlertCard
          key={alert.id}
          alert={alert}
          onStatusChange={onStatusChange}
          updating={updatingId === alert.id}
        />
      ))}
    </div>
  )
}
