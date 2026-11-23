import BackendStatus from './components/BackendStatus'

function App() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-12">
      <section className="w-full max-w-3xl rounded-3xl border border-slate-200 bg-white p-8 shadow-xl shadow-slate-200/50 sm:p-12">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="mb-2 text-sm font-semibold uppercase tracking-[0.24em] text-blue-700">
              LaunchShield AI
            </p>
            <h1 className="text-3xl font-bold tracking-tight text-slate-950 sm:text-5xl">
              Security findings made actionable
            </h1>
          </div>
          <BackendStatus />
        </div>

        <p className="max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">
          A practical cybersecurity assessment assistant for understanding real scanner
          evidence, prioritizing weaknesses, and planning verified remediation.
        </p>

        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          <article className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
            <h2 className="font-semibold text-slate-900">Assess</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Review website, source, and dependency scanner evidence.
            </p>
          </article>
          <article className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
            <h2 className="font-semibold text-slate-900">Understand</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Learn what matters and which evidence supports it.
            </p>
          </article>
          <article className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
            <h2 className="font-semibold text-slate-900">Remediate</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Follow clear fixes and verify improvements with rescans.
            </p>
          </article>
        </div>
      </section>
    </main>
  )
}

export default App
