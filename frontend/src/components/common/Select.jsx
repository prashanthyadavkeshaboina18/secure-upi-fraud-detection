export default function Select({ label, name, error, options = [], placeholder, ...rest }) {
  return (
    <div>
      {label && (
        <label htmlFor={name} className="label">
          {label}
        </label>
      )}
      <select
        id={name}
        name={name}
        aria-invalid={Boolean(error)}
        className={`field ${error ? 'border-blocked focus:border-blocked focus:ring-blocked' : ''}`}
        {...rest}
      >
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((option) => {
          const value = typeof option === 'string' ? option : option.value
          const text = typeof option === 'string' ? option : option.label
          return (
            <option key={value} value={value}>
              {text}
            </option>
          )
        })}
      </select>
      {error && <p className="mt-1 text-xs text-blocked">{error}</p>}
    </div>
  )
}
