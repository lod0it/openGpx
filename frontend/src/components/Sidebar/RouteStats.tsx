import { useRouteStore } from '../../store/useRouteStore'
import styles from './RouteStats.module.css'

function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  if (h === 0) return `${m}m`
  return `${h}h ${m}m`
}

export function RouteStats() {
  const distanceM = useRouteStore((s) => s.distanceM)
  const durationS = useRouteStore((s) => s.durationS)
  const isLoading = useRouteStore((s) => s.isLoading)
  const error = useRouteStore((s) => s.error)

  if (error) {
    return <div className={styles.error}>⚠ {error}</div>
  }

  if (isLoading) {
    return <div className={styles.loading}>Calculating route…</div>
  }

  if (distanceM === null) return null

  return (
    <div className={styles.stats}>
      <div className={styles.stat}>
        <span className={styles.icon}>📍</span>
        <span className={styles.value}>{(distanceM / 1000).toFixed(1)} km</span>
      </div>
      <div className={styles.stat}>
        <span className={styles.icon}>⏱</span>
        <span className={styles.value}>{formatDuration(durationS!)}</span>
      </div>
    </div>
  )
}
