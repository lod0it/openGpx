import { useRouteStore } from '../../store/useRouteStore'
import { useT } from '../../i18n/useT'
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
  const maxElevation = useRouteStore((s) => s.maxElevation)
  const isLoading = useRouteStore((s) => s.isLoading)
  const error = useRouteStore((s) => s.error)
  const t = useT()

  if (error) {
    return <div className={styles.error}>{error}</div>
  }

  if (isLoading) {
    return <div className={styles.loading}>{t('stats.loading')}</div>
  }

  if (distanceM === null) return null

  return (
    <div className={styles.stats}>
      <div className={styles.stat}>
        <span className={styles.label}>km</span>
        <span className={styles.value}>{(distanceM / 1000).toFixed(1)}</span>
      </div>
      <div className={styles.stat}>
        <span className={styles.label}>t</span>
        <span className={styles.value}>{formatDuration(durationS!)}</span>
      </div>
      {maxElevation !== null && (
        <div className={styles.stat}>
          <span className={styles.label}>{t('stats.max_elevation')}</span>
          <span className={styles.value}>{Math.round(maxElevation)}m</span>
        </div>
      )}
    </div>
  )
}
