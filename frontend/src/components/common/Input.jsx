export default function Input({ label, name, error, hint, ...rest }) {
  return (
    <div>
      {label && (
        <label htmlFor={name} className="label">
          {label}
        </label>
      )}
      <input
        id={name}
        name={name}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? `${name}-error` : undefined}
        className={`field ${error ? 'border-blocked focus:border-blocked focus:ring-blocked' : ''}`}
        {...rest}
      />
      {error ? (
        <p id={`${name}-error`} className="mt-1 text-xs text-blocked">
          {error}
        </p>
      ) : (
        hint && <p className="mt-1 text-xs text-ink-muted">{hint}</p>
      )}
    </div>
  )
}
