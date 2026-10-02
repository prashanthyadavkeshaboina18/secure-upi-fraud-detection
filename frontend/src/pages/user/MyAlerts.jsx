import PageHeader from '../../components/layout/PageHeader.jsx'
import AlertList from '../../components/alerts/AlertList.jsx'
import useFetch from '../../hooks/useFetch.js'
import { listMyAlerts } from '../../services/alertService.js'

export default function MyAlerts() {
  const { data, loading, error, reload } = useFetch(() => listMyAlerts(), [])

  return (
    <>
      <PageHeader
        title="My alerts"
        description="Raised whenever a payment on your account was scored as high risk."
      />
      <AlertList
        alerts={data?.items || []}
        loading={loading}
        error={error}
        onRetry={reload}
      />
    </>
  )
}
