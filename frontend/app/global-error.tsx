'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body>
        <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
          <div className="max-w-md w-full bg-white rounded-2xl border border-slate-200 shadow-lg p-8 text-center space-y-4">
            <div className="text-5xl">💥</div>
            <h2 className="text-2xl font-bold text-slate-900">Critical Error</h2>
            <p className="text-sm text-slate-600">
              A critical error occurred. Please refresh the page or try again later.
            </p>
            {error.digest && (
              <p className="text-xs text-slate-400 font-mono">Error ID: {error.digest}</p>
            )}
            <button
              onClick={reset}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold rounded-lg transition"
            >
              Refresh Page
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
