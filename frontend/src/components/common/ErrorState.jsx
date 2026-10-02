export default function ErrorState({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center gap-3 px-6 py-12 text-center">
      <h3 className="text-base font-semibold text-blocked">That request failed</h3>
      <p className="max-w-sm text-sm text-ink-muted">
        {message || 'The server did not respond as expected.'}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="rounded-md border border-line px-4 py-2 text-sm font-medium text-ink hover:bg-canvas"
        >
          Try again
        </button>
      )}
    </div>
  )
}
