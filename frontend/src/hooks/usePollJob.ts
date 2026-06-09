import { getJobStatus } from "@/services/api"
import type { JobStatus } from "@/services/types"

interface PollOptions {
  intervalMs?: number
  onProgress?: (status: JobStatus) => void
}

/**
 * Polls a background job until it completes or fails.
 * Resolves with the job result, rejects on failure.
 */
export const usePollJob = () => {
  const poll = async (jobId: string, options: PollOptions = {}): Promise<unknown> => {
    const { intervalMs = 1500, onProgress } = options

    // eslint-disable-next-line no-constant-condition
    while (true) {
      const data = await getJobStatus(jobId)
      onProgress?.(data)

      if (data.state === "completed") return data.result
      if (data.state === "failed") throw new Error(data.error || "Job failed")

      await new Promise((r) => setTimeout(r, intervalMs))
    }
  }

  return { poll }
}
