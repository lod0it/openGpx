import { useRouteStore } from '../../store/useRouteStore'
import { useT } from '../../i18n/useT'
import styles from './RoadTypeBreakdown.module.css'

const ROAD_COLORS: Record<string, string> = {
  MOTORWAY: '#ef4444',
  TRUNK: '#f97316',
  PRIMARY: '#eab308',
  SECONDARY: '#22c55e',
  TERTIARY: '#3b82f6',
  RESIDENTIAL: '#8b5cf6',
  TRACK: '#92400e',
  UNCLASSIFIED: '#9ca3af',
  SERVICE: '#d1d5db',
}

const SURFACE_COLORS: Record<string, string> = {
  ASPHALT: '#374151',
  PAVED: '#4b5563',
  CONCRETE: '#6b7280',
  COBBLESTONE: '#9ca3af',
  UNPAVED: '#92400e',
  GRAVEL: '#b45309',
  DIRT: '#a16207',
  GROUND: '#854d0e',
  GRASS: '#15803d',
  SAND: '#ca8a04',
}

function BreakdownSection({
  title,
  data,
  keyPrefix,
  colors,
}: {
  title: string
  data: Record<string, number>
  keyPrefix: string
  colors: Record<string, string>
}) {
  const t = useT()
  const sorted = Object.entries(data)
    .filter(([, v]) => v >= 0.5)
    .sort(([, a], [, b]) => b - a)

  if (sorted.length === 0) return null

  return (
    <div className={styles.section}>
      <div className={styles.sectionTitle}>{title}</div>
      {sorted.map(([key, pct]) => {
        const label = t(`${keyPrefix}.${key}`)
        return (
          <div key={key} className={styles.row}>
            <div className={styles.rowLabel}>{label !== `${keyPrefix}.${key}` ? label : key}</div>
            <div className={styles.barTrack}>
              <div
                className={styles.barFill}
                style={{ width: `${pct}%`, background: colors[key] ?? '#9ca3af' }}
              />
            </div>
            <div className={styles.pct}>{pct.toFixed(0)}%</div>
          </div>
        )
      })}
    </div>
  )
}

export function RoadTypeBreakdown() {
  const roadStats = useRouteStore((s) => s.roadStats)
  const t = useT()

  if (!roadStats) return null

  return (
    <div className={styles.wrapper}>
      <div className={styles.title}>{t('road.title')}</div>
      <BreakdownSection
        title={t('road.section_type')}
        data={roadStats.road_class}
        keyPrefix="road"
        colors={ROAD_COLORS}
      />
      <BreakdownSection
        title={t('road.section_surface')}
        data={roadStats.surface}
        keyPrefix="surface"
        colors={SURFACE_COLORS}
      />
    </div>
  )
}
