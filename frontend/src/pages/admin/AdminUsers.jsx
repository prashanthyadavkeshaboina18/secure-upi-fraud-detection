import { useState } from 'react'
import PageHeader from '../../components/layout/PageHeader.jsx'
import SearchBar from '../../components/common/SearchBar.jsx'
import Loader from '../../components/common/Loader.jsx'
import EmptyState from '../../components/common/EmptyState.jsx'
import ErrorState from '../../components/common/ErrorState.jsx'
import useFetch from '../../hooks/useFetch.js'
import useDebounce from '../../hooks/useDebounce.js'
import { listUsers } from '../../services/adminService.js'
import { formatDate, formatNumber } from '../../utils/formatters.js'

export default function AdminUsers() {
  const [search, setSearch] = useState('')
  const debounced = useDebounce(search)

  const { data, loading, error, reload } = useFetch(
    () => listUsers(debounced ? { search: debounced } : {}),
    [debounced]
  )

  const users = data?.items || []

  return (
    <>
      <PageHeader title="Users" description="Accounts registered on the platform." />

      <section className="card">
        <div className="border-b border-line p-4">
          <SearchBar value={search} onChange={setSearch} placeholder="Search by name or email" />
        </div>

        {loading ? (
          <div className="p-4"><Loader rows={5} /></div>
        ) : error ? (
          <ErrorState message={error} onRetry={reload} />
        ) : !users.length ? (
          <EmptyState title="No users found" description="Try a different search term." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px]">
              <thead className="bg-canvas">
                <tr>
                  <th className="table-head">Name</th>
                  <th className="table-head">Email</th>
                  <th className="table-head">Phone</th>
                  <th className="table-head">Role</th>
                  <th className="table-head">Payments</th>
                  <th className="table-head">Blocked</th>
                  <th className="table-head">Joined</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-t border-line hover:bg-canvas/70">
                    <td className="table-cell font-medium">{user.name}</td>
                    <td className="table-cell text-ink-soft">{user.email}</td>
                    <td className="table-cell text-ink-soft">{user.phone}</td>
                    <td className="table-cell">
                      <span className="rounded-full bg-canvas px-2 py-0.5 text-xs">{user.role}</span>
                    </td>
                    <td className="table-cell tabular-nums">{formatNumber(user.transaction_count)}</td>
                    <td className="table-cell tabular-nums text-blocked">
                      {formatNumber(user.blocked_count)}
                    </td>
                    <td className="table-cell whitespace-nowrap text-ink-muted">
                      {formatDate(user.account_created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  )
}
