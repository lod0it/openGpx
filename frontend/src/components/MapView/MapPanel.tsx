import { useState } from 'react'
import { useMapStore, type BaseLayer } from '../../store/useMapStore'
import { useT } from '../../i18n/useT'
import styles from './MapPanel.module.css'

const BASE_LAYERS: { key: BaseLayer; labelKey: string }[] = [
  { key: 'osm', labelKey: 'map.layer.osm' },
  { key: 'topo', labelKey: 'map.layer.topo' },
  { key: 'cyclosm', labelKey: 'map.layer.cyclosm' },
]

export function MapPanel() {
  const [open, setOpen] = useState(false)
  const baseLayer = useMapStore((s) => s.baseLayer)
  const trailsOverlay = useMapStore((s) => s.trailsOverlay)
  const setBaseLayer = useMapStore((s) => s.setBaseLayer)
  const setTrailsOverlay = useMapStore((s) => s.setTrailsOverlay)
  const t = useT()

  return (
    <div className={`${styles.panel} ${open ? styles.open : ''}`}>
      <button
        className={styles.toggle}
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? 'Chiudi pannello layer' : 'Apri pannello layer'}
      >
        <span className={styles.toggleLabel}>{t('map.panel.label')}</span>
      </button>

      <div className={styles.content}>
        <div className={styles.section}>
          <div className={styles.sectionTitle}>{t('map.panel.base')}</div>
          {BASE_LAYERS.map(({ key, labelKey }) => (
            <label key={key} className={styles.row}>
              <input
                type="radio"
                name="baseLayer"
                value={key}
                checked={baseLayer === key}
                onChange={() => setBaseLayer(key)}
              />
              {t(labelKey)}
            </label>
          ))}
        </div>

        <div className={styles.section}>
          <div className={styles.sectionTitle}>{t('map.panel.overlay')}</div>
          <label className={styles.row}>
            <input
              type="checkbox"
              checked={trailsOverlay}
              onChange={(e) => setTrailsOverlay(e.target.checked)}
            />
            {t('map.layer.trails')}
          </label>
        </div>
      </div>
    </div>
  )
}
