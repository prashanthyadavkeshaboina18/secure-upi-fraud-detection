import { useState } from 'react'
import PageHeader from '../../components/layout/PageHeader.jsx'
import AlertList from '../../components/alerts/AlertList.jsx'
import useFetch from '../../hooks/useFetch.js'
import { listAllAlerts, updateAlertStatus } from '../../services/adminService.js'
import { useToast } from '../../context/ToastContext.jsx'

const TABS = [
  { value: 'NEW', label: 'Open' },
  { value: 'REVIEWED', label: 'Reviewed' },
  { value: 'DISMISSED', label: 'Dismissed' },
  { value: '', label: 'All' },
]

export default function AdminAlerts() {
  const [status, setStatus] = useState('NEW')
  const [updatingId, setUpdatingId] = useState(null)
  const { notify } = useToast()

  const { data, loading, error, reload } = useFetch(
    () => listAllAlerts(status ? { status } : {}),
    [status]
  )

  const changeStatus = async (alertId, nextStatus) => {
    setUpdatingId(alertId)
    try {
      await updateAlertStatus(alertId, nextStatus)
      notify(`Alert marked ${nextStatus.toLowerCase()}`, 'success')
      reload()
    } catch (err) {
      notify(err.message || 'Could not update the alert', 'error')
    } finally {
      setUpdatingId(null)
    }
  }

  return (
    <>
      <PageHeader
        title="Alert queue"
        description="Raised automatically whenever the model blocks a payment."
      />

      <div className="mb-4 flex flex-wrap gap-2">
        {TABS.map((tab) => (
          <button
            key={tab.label}
            onClick={() => setStatus(tab.value)}
            className={`rounded-md border px-3 py-1.5 text-sm ${
              status === tab.value
                ? 'border-brand bg-brand-light font-medium text-brand-dark'
                : 'border-line bg-white text-ink-soft hover:bg-canvas'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <AlertList
        alerts={data?.items || []}
        loading={loading}
        error={error}
        onRetry={reload}
        onStatusChange={changeStatus}
        updatingId={updatingId}
      />
    </>
  )
}
