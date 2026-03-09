import { useRouteStore } from '../../store/useRouteStore'
import { useT } from '../../i18n/useT'
import type { GlobalFilters } from '../../types'
import styles from './GlobalFilters.module.css'

const FILTERS: { key: keyof GlobalFilters; labelKey: string }[] = [
  { key: 'avoid_motorways', labelKey: 'filters.avoid_motorways' },
  { key: 'avoid_highways', labelKey: 'filters.avoid_highways' },
  { key: 'avoid_primary', labelKey: 'filters.avoid_primary' },
  { key: 'prefer_unpaved', labelKey: 'filters.prefer_unpaved' },
  { key: 'prefer_secondary', labelKey: 'filters.prefer_secondary' },
  { key: 'prefer_mountain_passes', labelKey: 'filters.prefer_mountain_passes' },
]

export function GlobalFiltersPanel() {
  const globalFilters = useRouteStore((s) => s.globalFilters)
  const setGlobalFilter = useRouteStore((s) => s.setGlobalFilter)
  const t = useT()

  return (
    <div className={styles.wrapper}>
      <div className={styles.title}>{t('filters.title')}</div>
      {FILTERS.map(({ key, labelKey }) => (
        <label key={key} className={styles.row}>
          <input
            type="checkbox"
            checked={globalFilters[key]}
            onChange={(e) => setGlobalFilter({ [key]: e.target.checked })}
          />
          {t(labelKey)}
        </label>
      ))}
    </div>
  )
}
