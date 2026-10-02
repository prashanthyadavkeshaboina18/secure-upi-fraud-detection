const STATUSES = ['NEW', 'REVIEWED', 'DISMISSED']

export default function AlertStatusSelect({ value, onChange, disabled }) {
  return (
    <select
      value={value}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value)}
      aria-label="Alert status"
      className="field w-36 py-1.5 text-xs"
    >
      {STATUSES.map((status) => (
        <option key={status} value={status}>{status}</option>
      ))}
    </select>
  )
}
