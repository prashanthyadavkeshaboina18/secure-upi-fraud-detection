import PageHeader from '../../components/layout/PageHeader.jsx'
import Loader from '../../components/common/Loader.jsx'
import ErrorState from '../../components/common/ErrorState.jsx'
import EmptyState from '../../components/common/EmptyState.jsx'
import useFetch from '../../hooks/useFetch.js'
import { getModelPerformance } from '../../services/adminService.js'
import { formatDateTime } from '../../utils/formatters.js'

const METRICS = [
  { key: 'precision', label: 'Precision', note: 'Of the payments we flagged, how many were really fraud' },
  { key: 'recall', label: 'Recall', note: 'Of all the real fraud, how much we caught' },
  { key: 'f1_score', label: 'F1-score', note: 'Balance between precision and recall' },
  { key: 'roc_auc', label: 'ROC-AUC', note: 'Ranking quality across every threshold' },
  { key: 'pr_auc', label: 'PR-AUC', note: 'Ranking quality on the rare fraud class' },
  { key: 'accuracy', label: 'Accuracy', note: 'Least useful here — fraud is rare' },
]

const show = (value) => (typeof value === 'number' ? value.toFixed(4) : '—')

function ConfusionMatrix({ matrix }) {
  if (!matrix) return null
  const { true_negative: tn, false_positive: fp, false_negative: fn, true_positive: tp } = matrix

  const cell = (value, label, tone) => (
    <div className={`rounded-md p-4 text-center ${tone}`}>
      <p className="text-xl font-semibold tabular-nums">{value ?? '—'}</p>
      <p className="mt-1 text-xs">{label}</p>
    </div>
  )

  return (
    <div className="card p-5">
      <h2 className="text-sm font-semibold">Confusion matrix</h2>
      <p className="mt-0.5 text-xs text-ink-muted">Counts on the held-out test set.</p>
      <div className="mt-4 grid grid-cols-2 gap-3">
        {cell(tn, 'Genuine, correctly allowed', 'bg-approved-light text-approved')}
        {cell(fp, 'Genuine, wrongly flagged', 'bg-review-light text-review')}
        {cell(fn, 'Fraud we missed', 'bg-blocked-light text-blocked')}
        {cell(tp, 'Fraud correctly caught', 'bg-approved-light text-approved')}
      </div>
      <p className="mt-4 text-xs text-ink-muted">
        False negatives cost money. False positives cost trust. The threshold is
        chosen to balance the two rather than to maximise accuracy.
      </p>
    </div>
  )
}

export default function ModelPerformance() {
  const { data, loading, error, reload } = useFetch(() => getModelPerformance(), [])

  if (loading) return <Loader label="Loading model metrics" />
  if (error) return <ErrorState message={error} onRetry={reload} />

  if (!data || !data.selected_model) {
    return (
      <>
        <PageHeader title="Model performance" />
        <div className="card">
          <EmptyState
            title="No metrics published yet"
            description="Run the training pipeline. It writes metrics.json, and this page reads that file — nothing here is hard-coded."
          />
        </div>
      </>
    )
  }

  const selected = data.selected_model
  const comparison = data.comparison || []

  return (
    <>
      <PageHeader
        title="Model performance"
        description="Read directly from the metrics file produced by the training run."
      />

      <div className="card mb-4 flex flex-wrap items-center justify-between gap-3 p-4">
        <div>
          <p className="text-sm font-medium">
            In production: {selected.model_name}{' '}
            <span className="font-mono text-xs text-ink-muted">{selected.model_version}</span>
          </p>
          <p className="mt-0.5 text-xs text-ink-muted">
            Trained {formatDateTime(data.trained_at)} · {data.imbalance_strategy || 'imbalance strategy not recorded'}
          </p>
        </div>
        <span className="rounded-full bg-brand-light px-3 py-1 text-xs font-medium text-brand-dark">
          Decision threshold {selected.threshold ?? '—'}
        </span>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {METRICS.map((metric) => (
          <div key={metric.key} className="card p-4">
            <p className="text-sm text-ink-muted">{metric.label}</p>
            <p className="mt-2 font-mono text-2xl font-semibold">{show(selected[metric.key])}</p>
            <p className="mt-1 text-xs text-ink-muted">{metric.note}</p>
          </div>
        ))}
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <ConfusionMatrix matrix={selected.confusion_matrix} />

        <div className="card">
          <div className="border-b border-line px-4 py-3">
            <h2 className="text-sm font-semibold">Model comparison</h2>
            <p className="mt-0.5 text-xs text-ink-muted">All candidates evaluated on the same test split.</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[520px]">
              <thead className="bg-canvas">
                <tr>
                  <th className="table-head">Model</th>
                  <th className="table-head">Precision</th>
                  <th className="table-head">Recall</th>
                  <th className="table-head">F1</th>
                  <th className="table-head">ROC-AUC</th>
                </tr>
              </thead>
              <tbody>
                {comparison.map((row) => (
                  <tr key={row.model_name}
                      className={`border-t border-line ${
                        row.model_name === selected.model_name ? 'bg-brand-light/40' : ''
                      }`}>
                    <td className="table-cell font-medium">{row.model_name}</td>
                    <td className="table-cell font-mono">{show(row.precision)}</td>
                    <td className="table-cell font-mono">{show(row.recall)}</td>
                    <td className="table-cell font-mono">{show(row.f1_score)}</td>
                    <td className="table-cell font-mono">{show(row.roc_auc)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  )
}
