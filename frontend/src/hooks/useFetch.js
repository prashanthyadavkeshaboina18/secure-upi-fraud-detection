import { useCallback, useEffect, useRef, useState } from 'react'

/**
 * Standard {data, loading, error, reload} wrapper around a service call.
 * `deps` works like a useEffect dependency array — change a filter and the
 * request re-runs. A ref guards against setting state after unmount.
 */
export default function useFetch(fetcher, deps = [], { skip = false } = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(!skip)
  const [error, setError] = useState(null)
  const alive = useRef(true)

  useEffect(() => {
    alive.current = true
    return () => {
      alive.current = false
    }
  }, [])

  const run = useCallback(() => {
    if (skip) return
    setLoading(true)
    setError(null)
    fetcher()
      .then((result) => alive.current && setData(result))
      .catch((err) => alive.current && setError(err.message || 'Request failed'))
      .finally(() => alive.current && setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, skip])

  useEffect(() => {
    run()
  }, [run])

  return { data, loading, error, reload: run, setData }
}
