import { Link } from 'react-router-dom'
import RiskBadge from '../dashboard/RiskBadge.jsx'
import DecisionBadge from '../dashboard/DecisionBadge.jsx'
import { formatCurrency, formatDateTime, truncate } from '../../utils/formatters.js'

export default function TransactionRow({ transaction, showUser = false }) {
  return (
    <tr className="border-t border-line hover:bg-canvas/70">
      <td className="table-cell">
        <Link
          to={`/transactions/${transaction.transaction_id}`}
          className="font-mono text-xs text-brand hover:underline"
        >
          {transaction.transaction_id}
        </Link>
      </td>
      {showUser && <td className="table-cell">{transaction.user_name || `#${transaction.user_id}`}</td>}
      <td className="table-cell font-medium tabular-nums">{formatCurrency(transaction.amount)}</td>
      <td className="table-cell">{truncate(transaction.receiver_vpa, 22)}</td>
      <td className="table-cell text-ink-soft">{transaction.merchant_category}</td>
      <td className="table-cell">
        <RiskBadge level={transaction.risk_level} score={transaction.risk_score} />
      </td>
      <td className="table-cell">
        <DecisionBadge decision={transaction.decision} />
      </td>
      <td className="table-cell whitespace-nowrap text-ink-muted">
        {formatDateTime(transaction.created_at)}
      </td>
    </tr>
  )
}
