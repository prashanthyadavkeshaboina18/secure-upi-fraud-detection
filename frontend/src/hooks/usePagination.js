import { useMemo, useState } from 'react'
import { PAGE_SIZE } from '../utils/constants.js'

export default function usePagination(total = 0, pageSize = PAGE_SIZE) {
  const [page, setPage] = useState(1)

  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  const safePage = Math.min(page, totalPages)

  const controls = useMemo(
    () => ({
      page: safePage,
      pageSize,
      totalPages,
      skip: (safePage - 1) * pageSize,
      next: () => setPage((p) => Math.min(p + 1, totalPages)),
      prev: () => setPage((p) => Math.max(p - 1, 1)),
      goTo: (n) => setPage(Math.min(Math.max(n, 1), totalPages)),
      reset: () => setPage(1),
    }),
    [safePage, pageSize, totalPages]
  )

  return controls
}
