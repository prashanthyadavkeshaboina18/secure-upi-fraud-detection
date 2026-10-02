import { Link } from 'react-router-dom'
import AlertStatusSelect from './AlertStatusSelect.jsx'
import { formatDateTime } from '../../utils/formatters.js'
import { riskStyle } from '../../utils/riskHelpers.js'

export default function AlertCard({ alert, onStatusChange, updating }) {
  const style = riskStyle(alert.severity)

  return (
    <article className={`card border-l-4 p-4 ${style.border}`}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${style.bg} ${style.text}`}>
              {alert.severity}
            </span>
            <h3 className="truncate text-sm font-semibold text-ink">{alert.alert_type}</h3>
          </div>
          <p className="mt-1.5 text-sm text-ink-soft">{alert.message}</p>
          <p className="mt-2 text-xs text-ink-muted">
            {formatDateTime(alert.created_at)}
            {alert.user_name && ` · ${alert.user_name}`}
          </p>
        </div>

        <div className="flex shrink-0 flex-col items-end gap-2">
          {onStatusChange ? (
            <AlertStatusSelect
              value={alert.status}
              disabled={updating}
              onChange={(status) => onStatusChange(alert.id, status)}
            />
          ) : (
            <span className="text-xs text-ink-muted">{alert.status}</span>
          )}
          {alert.transaction_id && (
            <Link
              to={`/transactions/${alert.transaction_id}`}
              className="font-mono text-xs text-brand hover:underline"
            >
              {alert.transaction_id}
            </Link>
          )}
        </div>
      </div>
    </article>
  )
}
