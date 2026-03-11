import { useEffect } from 'react'

const INTERVAL_MS = 5_000

export function useHeartbeat() {
  useEffect(() => {
    const send = () =>
      fetch('/api/system/heartbeat', { method: 'POST' }).catch(() => {})

    send()
    const id = setInterval(send, INTERVAL_MS)
    return () => clearInterval(id)
  }, [])
}
