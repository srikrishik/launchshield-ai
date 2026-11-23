import { useEffect, useState } from 'react'

import { getHealthStatus } from '../services/api'

const STATUS_CONTENT = {
  checking: {
    label: 'Checking backend',
    classes: 'border-amber-300 bg-amber-50 text-amber-800',
  },
  connected: {
    label: 'Backend connected',
    classes: 'border-emerald-300 bg-emerald-50 text-emerald-800',
  },
  disconnected: {
    label: 'Backend unavailable',
    classes: 'border-rose-300 bg-rose-50 text-rose-800',
  },
}

function BackendStatus() {
  const [status, setStatus] = useState('checking')

  useEffect(() => {
    let active = true

    getHealthStatus()
      .then(() => {
        if (active) setStatus('connected')
      })
      .catch(() => {
        if (active) setStatus('disconnected')
      })

    return () => {
      active = false
    }
  }, [])

  const content = STATUS_CONTENT[status]

  return (
    <div
      role="status"
      aria-live="polite"
      className={`inline-flex items-center rounded-full border px-4 py-2 text-sm font-semibold ${content.classes}`}
    >
      <span
        className="mr-2 h-2 w-2 rounded-full bg-current"
        aria-hidden="true"
      />
      {content.label}
    </div>
  )
}

export default BackendStatus
