export default function SearchBar({ value, onChange, placeholder = 'Search' }) {
  return (
    <div className="relative w-full sm:w-72">
      <input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        aria-label={placeholder}
        className="field pl-9"
      />
      <svg
        className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-ink-muted"
        viewBox="0 0 20 20"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
      >
        <circle cx="9" cy="9" r="6" />
        <path d="m14 14 4 4" strokeLinecap="round" />
      </svg>
    </div>
  )
}
