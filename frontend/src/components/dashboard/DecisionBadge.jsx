import { decisionStyle } from '../../utils/riskHelpers.js'

export default function DecisionBadge({ decision }) {
  const style = decisionStyle(decision)
  return (
    <span
      className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-medium
                  ${style.bg} ${style.text} ${style.border}`}
    >
      {style.label}
    </span>
  )
}
