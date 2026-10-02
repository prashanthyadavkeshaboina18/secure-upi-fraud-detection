import { riskStyle } from '../../utils/riskHelpers.js'

/**
 * Semicircular gauge for the 0-100 risk score.
 * Drawn as a single SVG arc whose stroke-dashoffset encodes the score, so there
 * is no chart library dependency on the most important screen in the app.
 */
export default function RiskGauge({ score = 0, level }) {
  const style = riskStyle(level)
  const radius = 80
  const arcLength = Math.PI * radius
  const clamped = Math.max(0, Math.min(100, score))
  const offset = arcLength - (clamped / 100) * arcLength

  return (
    <figure className="flex flex-col items-center">
      <svg viewBox="0 0 200 116" className="w-56" role="img"
           aria-label={`Risk score ${clamped} out of 100, ${style.label}`}>
        <path d="M20 100 A80 80 0 0 1 180 100" fill="none" stroke="#E2E7EE" strokeWidth="14"
              strokeLinecap="round" />
        <path
          d="M20 100 A80 80 0 0 1 180 100"
          fill="none"
          stroke={style.stroke}
          strokeWidth="14"
          strokeLinecap="round"
          strokeDasharray={arcLength}
          strokeDashoffset={offset}
        />
        <text x="100" y="92" textAnchor="middle" className="fill-ink"
              style={{ fontSize: 34, fontWeight: 700 }}>
          {clamped}
        </text>
      </svg>
      <figcaption className={`-mt-1 text-sm font-medium ${style.text}`}>
        {style.label} · {clamped}/100
      </figcaption>
    </figure>
  )
}
