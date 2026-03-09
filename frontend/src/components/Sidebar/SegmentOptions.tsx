import { useRouteStore } from '../../store/useRouteStore'
import type { SegmentOptions } from '../../types'
import { defaultSegmentOptions } from '../../types'
import { AdventureSliderControl } from './AdventureSlider'
import { useT } from '../../i18n/useT'
import styles from './SegmentOptions.module.css'

interface Props {
  waypointId: string
}

const FILTERS: { key: keyof SegmentOptions; labelKey: string }[] = [
  { key: 'avoid_motorways', labelKey: 'filters.avoid_motorways' },
  { key: 'avoid_highways', labelKey: 'filters.avoid_highways' },
  { key: 'avoid_primary', labelKey: 'filters.avoid_primary' },
  { key: 'prefer_unpaved', labelKey: 'filters.prefer_unpaved' },
  { key: 'prefer_secondary', labelKey: 'filters.prefer_secondary' },
  { key: 'prefer_mountain_passes', labelKey: 'filters.prefer_mountain_passes' },
]

export function SegmentOptionsPanel({ waypointId }: Props) {
  const segmentOptions = useRouteStore((s) => s.segmentOptions)
  const setSegmentOption = useRouteStore((s) => s.setSegmentOption)
  const globalAdventure = useRouteStore((s) => s.adventure)
  const t = useT()

  const opts: SegmentOptions = segmentOptions[waypointId] ?? defaultSegmentOptions
  const hasCustomAdventure = opts.adventure !== undefined

  function update(patch: Partial<SegmentOptions>) {
    setSegmentOption(waypointId, { ...opts, ...patch })
  }

  return (
    <div className={styles.panel}>
      <div className={styles.adventureRow}>
        <label className={styles.customLabel}>
          <input
            type="checkbox"
            checked={hasCustomAdventure}
            onChange={(e) => update({ adventure: e.target.checked ? globalAdventure : undefined })}
          />
          {t('filters.segment_custom')}
        </label>
      </div>
      {hasCustomAdventure && (
        <AdventureSliderControl
          value={opts.adventure!}
          onChange={(v) => update({ adventure: v })}
          label={t('filters.segment_label')}
        />
      )}
      <div className={styles.filters}>
        {FILTERS.map(({ key, labelKey }) => (
          <label key={key} className={styles.filterRow}>
            <input
              type="checkbox"
              checked={!!opts[key]}
              onChange={(e) => update({ [key]: e.target.checked })}
            />
            {t(labelKey)}
          </label>
        ))}
      </div>
    </div>
  )
}
