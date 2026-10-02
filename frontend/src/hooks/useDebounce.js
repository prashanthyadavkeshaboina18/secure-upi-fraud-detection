import { useEffect, useState } from 'react'

/** Delays a fast-changing value (like a search box) so we do not hit the API on every keystroke. */
export default function useDebounce(value, delay = 400) {
  const [debounced, setDebounced] = useState(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return debounced
}
