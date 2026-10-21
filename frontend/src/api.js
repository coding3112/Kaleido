import { mockReport } from './mock'
export { STAGES } from './mock'

// Set VITE_USE_MOCK=true only when you intentionally want the sample UI demo.
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

export async function generateReport(question, opts = {}, onStage = () => {}) {
  if (USE_MOCK) return mockReport(question, opts, onStage)

  onStage(0)
  const res = await fetch(`${API_BASE_URL}/api/report`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, ...opts }),
  })
  onStage(1)
  if (!res.ok) {
    let message = `Request failed (${res.status})`
    try {
      const payload = await res.json()
      message = payload.detail || payload.error || message
    } catch {}
    throw new Error(message)
  }
  const data = await res.json()
  onStage(4)
  return data
}
