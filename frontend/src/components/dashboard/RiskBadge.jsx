import { riskStyle } from '../../utils/riskHelpers.js'

export default function RiskBadge({ level, score }) {
  const style = riskStyle(level)
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1
                  text-xs font-medium ${style.bg} ${style.text} ${style.border}`}
    >
      {style.label}
      {typeof score === 'number' && <span className="font-mono">{score}</span>}
    </span>
  )
}
