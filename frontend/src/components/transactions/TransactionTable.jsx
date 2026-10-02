import TransactionRow from './TransactionRow.jsx'
import Loader from '../common/Loader.jsx'
import EmptyState from '../common/EmptyState.jsx'
import ErrorState from '../common/ErrorState.jsx'

export default function TransactionTable({
  transactions = [],
  loading,
  error,
  onRetry,
  showUser = false,
  emptyTitle = 'No transactions yet',
  emptyDescription = 'Make your first payment and it will be analysed here.',
  emptyActionLabel,
  emptyActionTo,
}) {
  if (loading) return <div className="p-4"><Loader rows={5} /></div>
  if (error) return <ErrorState message={error} onRetry={onRetry} />
  if (!transactions.length)
    return (
      <EmptyState
        title={emptyTitle}
        description={emptyDescription}
        actionLabel={emptyActionLabel}
        actionTo={emptyActionTo}
      />
    )

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[840px]">
        <thead className="bg-canvas">
          <tr>
            <th className="table-head">Transaction</th>
            {showUser && <th className="table-head">User</th>}
            <th className="table-head">Amount</th>
            <th className="table-head">Receiver</th>
            <th className="table-head">Category</th>
            <th className="table-head">Risk</th>
            <th className="table-head">Decision</th>
            <th className="table-head">Time</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((t) => (
            <TransactionRow key={t.transaction_id} transaction={t} showUser={showUser} />
          ))}
        </tbody>
      </table>
    </div>
  )
}
