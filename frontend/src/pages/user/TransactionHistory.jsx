import { useMemo, useState } from 'react'
import PageHeader from '../../components/layout/PageHeader.jsx'
import TransactionTable from '../../components/transactions/TransactionTable.jsx'
import TransactionFilters from '../../components/transactions/TransactionFilters.jsx'
import Pagination from '../../components/common/Pagination.jsx'
import useFetch from '../../hooks/useFetch.js'
import useDebounce from '../../hooks/useDebounce.js'
import usePagination from '../../hooks/usePagination.js'
import { listTransactions } from '../../services/transactionService.js'

const EMPTY_FILTERS = { search: '', risk_level: '', decision: '', date_from: '' }

export default function TransactionHistory() {
  const [filters, setFilters] = useState(EMPTY_FILTERS)
  const debouncedSearch = useDebounce(filters.search)
  const [total, setTotal] = useState(0)
  const pager = usePagination(total)

  const query = useMemo(
    () => ({
      search: debouncedSearch || undefined,
      risk_level: filters.risk_level || undefined,
      decision: filters.decision || undefined,
      date_from: filters.date_from || undefined,
      skip: pager.skip,
      limit: pager.pageSize,
    }),
    [debouncedSearch, filters.risk_level, filters.decision, filters.date_from, pager.skip, pager.pageSize]
  )

  const { data, loading, error, reload } = useFetch(
    () => listTransactions(query).then((res) => {
      setTotal(res.total ?? 0)
      return res
    }),
    [query]
  )

  const changeFilters = (next) => {
    setFilters(next)
    pager.reset()
  }

  return (
    <>
      <PageHeader
        title="My transactions"
        description="Every payment you made, with the risk score the model assigned."
      />
      <section className="card">
        <TransactionFilters
          filters={filters}
          onChange={changeFilters}
          onReset={() => changeFilters(EMPTY_FILTERS)}
        />
        <TransactionTable
          transactions={data?.items || []}
          loading={loading}
          error={error}
          onRetry={reload}
          emptyTitle="Nothing matches these filters"
          emptyDescription="Clear the filters or make a payment to see results here."
        />
        <Pagination
          page={pager.page}
          totalPages={pager.totalPages}
          onPrev={pager.prev}
          onNext={pager.next}
          total={total}
        />
      </section>
    </>
  )
}
