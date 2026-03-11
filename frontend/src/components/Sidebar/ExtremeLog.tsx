import { useRouteStore } from '../../store/useRouteStore'
import { useT } from '../../i18n/useT'
import styles from './RoadTypeBreakdown.module.css'
import localStyles from './ExtremeLog.module.css'

export function ExtremeLog() {
  const extremeLog = useRouteStore((s) => s.extremeLog)
  const t = useT()

  if (!extremeLog || extremeLog.length === 0) return null

  return (
    <div className={styles.wrapper}>
      <div className={styles.title}>{t('extreme.title')}</div>
      {extremeLog.map((entry, idx) => (
        <div key={idx} className={localStyles.row}>
          <div className={localStyles.status} data-status={entry.status} />
          <div className={localStyles.name}>
            {entry.name || `${entry.lat.toFixed(4)}, ${entry.lng.toFixed(4)}`}
          </div>
          <div className={localStyles.meta}>
            {entry.status !== 'no_passes' && `${entry.ele}m · `}
            {t(`extreme.status.${entry.status}`)}
            {entry.mode ? ` · ${t(`extreme.mode.${entry.mode}`)}` : ''}
          </div>
        </div>
      ))}
    </div>
  )
}
