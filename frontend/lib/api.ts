// Utility functions for API calls using native fetch
// Replaces axios with lightweight fetch API

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface FetchOptions extends RequestInit {
  timeout?: number
}

/**
 * Enhanced fetch with timeout and error handling
 */
async function fetchWithTimeout(
  url: string,
  options: FetchOptions = {}
): Promise<Response> {
  const { timeout = 30000, ...fetchOptions } = options

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal,
    })
    clearTimeout(timeoutId)
    return response
  } catch (error) {
    clearTimeout(timeoutId)
    throw error
  }
}

/**
 * API client using native fetch
 */
export const api = {
  async get<T = any>(endpoint: string): Promise<T> {
    const response = await fetchWithTimeout(`${API_BASE_URL}${endpoint}`)
    if (!response.ok) throw new Error(response.statusText)
    return response.json()
  },

  async post<T = any>(endpoint: string, data?: any): Promise<T> {
    const response = await fetchWithTimeout(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: data ? JSON.stringify(data) : undefined,
    })
    if (!response.ok) throw new Error(response.statusText)
    return response.json()
  },
}

/**
 * Poll for job status until completion
 */
export async function pollJobStatus(
  jobId: string,
  onUpdate: (status: any) => void,
  interval = 2000
): Promise<any> {
  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const status = await api.get(`/api/scrape/${jobId}`)
        onUpdate(status)

        if (status.status === "COMPLETED") {
          resolve(status)
        } else if (status.status === "FAILED_FINAL") {
          reject(new Error(status.error || "Job failed"))
        } else {
          setTimeout(poll, interval)
        }
      } catch (err) {
        reject(err)
      }
    }
    poll()
  })
}
