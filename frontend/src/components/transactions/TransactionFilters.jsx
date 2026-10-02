import SearchBar from '../common/SearchBar.jsx'
import { RISK_LEVELS, DECISIONS } from '../../utils/constants.js'

export default function TransactionFilters({ filters, onChange, onReset, showSearch = true }) {
  const update = (key) => (e) => onChange({ ...filters, [key]: e.target.value })

  return (
    <div className="flex flex-wrap items-end gap-3 border-b border-line p-4">
      {showSearch && (
        <SearchBar
          value={filters.search || ''}
          onChange={(value) => onChange({ ...filters, search: value })}
          placeholder="Search by transaction ID or receiver"
        />
      )}

      <div>
        <label htmlFor="risk_level" className="label">Risk level</label>
        <select id="risk_level" value={filters.risk_level || ''} onChange={update('risk_level')} className="field w-40">
          <option value="">All levels</option>
          {Object.values(RISK_LEVELS).map((level) => (
            <option key={level} value={level}>{level}</option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="decision" className="label">Decision</label>
        <select id="decision" value={filters.decision || ''} onChange={update('decision')} className="field w-44">
          <option value="">All decisions</option>
          {Object.values(DECISIONS).map((decision) => (
            <option key={decision} value={decision}>{decision}</option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="date_from" className="label">From</label>
        <input id="date_from" type="date" value={filters.date_from || ''} onChange={update('date_from')} className="field w-40" />
      </div>

      <button onClick={onReset} className="rounded-md px-3 py-2 text-sm text-ink-soft hover:bg-canvas">
        Clear filters
      </button>
    </div>
  )
}
