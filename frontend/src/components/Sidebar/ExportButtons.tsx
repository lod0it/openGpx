import { useState } from 'react'
import { useRouteStore } from '../../store/useRouteStore'
import { useT } from '../../i18n/useT'
import { downloadGpx } from '../../api/export'
import styles from './ExportButtons.module.css'

export function ExportButtons() {
  const waypoints = useRouteStore((s) => s.waypoints)
  const geometry = useRouteStore((s) => s.geometry)
  const [exporting, setExporting] = useState<'track' | 'route' | null>(null)
  const t = useT()

  const canExport = waypoints.length >= 2

  async function handleExport(type: 'track' | 'route') {
    if (!canExport) return
    setExporting(type)
    try {
      await downloadGpx(type, waypoints, geometry)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Export failed')
    } finally {
      setExporting(null)
    }
  }

  if (!canExport) return null

  return (
    <div className={styles.wrapper}>
      <button
        className={styles.btn}
        onClick={() => handleExport('track')}
        disabled={exporting !== null || geometry.length === 0}
        title="Detailed GPX with full route geometry — best for GPS devices"
      >
        {exporting === 'track' ? '…' : '⬇'} {t('export.track')}
      </button>
      <button
        className={`${styles.btn} ${styles.secondary}`}
        onClick={() => handleExport('route')}
        disabled={exporting !== null}
        title="Waypoints-only GPX — smaller file"
      >
        {exporting === 'route' ? '…' : '⬇'} {t('export.route')}
      </button>
    </div>
  )
}
