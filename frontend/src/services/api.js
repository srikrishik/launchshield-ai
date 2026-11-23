const API_BASE_URL = '/api'

export async function getHealthStatus() {
  const response = await fetch(`${API_BASE_URL}/health`)

  if (!response.ok) {
    throw new Error(`Health request failed with status ${response.status}`)
  }

  const data = await response.json()

  if (data?.status !== 'healthy') {
    throw new Error('Unexpected health response')
  }

  return data
}
