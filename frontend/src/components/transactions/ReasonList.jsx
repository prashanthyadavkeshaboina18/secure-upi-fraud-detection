export default function ReasonList({ reasons = [], tone = 'review' }) {
  if (!reasons.length) return null

  const dot = tone === 'blocked' ? 'bg-blocked' : 'bg-review'

  return (
    <div>
      <h3 className="text-sm font-semibold text-ink">Why this was flagged</h3>
      <ul className="mt-2 space-y-2">
        {reasons.map((reason, index) => (
          <li key={index} className="flex gap-2.5 text-sm text-ink-soft">
            <span className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${dot}`} />
            <span>{reason}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
