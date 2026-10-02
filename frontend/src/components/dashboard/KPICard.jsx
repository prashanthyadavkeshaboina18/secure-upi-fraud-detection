export default function KPICard({ label, value, caption, tone = 'default' }) {
  const accent = {
    default: 'text-ink',
    approved: 'text-approved',
    review: 'text-review',
    blocked: 'text-blocked',
  }[tone]

  return (
    <div className="card p-4">
      <p className="text-sm text-ink-muted">{label}</p>
      <p className={`mt-2 text-2xl font-semibold tabular-nums ${accent}`}>{value}</p>
      {caption && <p className="mt-1 text-xs text-ink-muted">{caption}</p>}
    </div>
  )
}
