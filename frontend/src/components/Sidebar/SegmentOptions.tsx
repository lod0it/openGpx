import { useRouteStore } from '../../store/useRouteStore'
import type { SegmentOptions } from '../../types'
import { defaultSegmentOptions } from '../../types'
import { AdventureSliderControl } from './AdventureSlider'
import { useT } from '../../i18n/useT'
import styles from './SegmentOptions.module.css'

function PassSelector({
  index,
  passesFound,
  onChange,
}: {
  index: number
  passesFound: number
  onChange: (i: number) => void
}) {
  const t = useT()
  const max = passesFound > 0 ? passesFound : 3   // prima del primo calcolo assumiamo max 3

  function prev() { onChange(((index - 1) + max) % max) }
  function next() { onChange((index + 1) % max) }
  function rand() { onChange(Math.floor(Math.random() * max)) }

  return (
    <div className={styles.passSelector}>
      <span className={styles.passLabel}>{t('extreme.pass_label')}:</span>
      <button className={styles.dirBtn} onClick={prev}>{'<'}</button>
      <span className={styles.passIndex}>
        {index + 1}{passesFound > 0 ? ` ${t('extreme.pass_of')} ${passesFound}` : ''}
      </span>
      <button className={styles.dirBtn} onClick={next}>{'>'}</button>
      <button className={styles.dirBtn} onClick={rand} title="Random">{t('extreme.pass_random')}</button>
    </div>
  )
}

interface Props {
  waypointId: string
}

const FILTERS: { key: keyof SegmentOptions; labelKey: string }[] = [
  { key: 'avoid_motorways', labelKey: 'filters.avoid_motorways' },
  { key: 'avoid_highways', labelKey: 'filters.avoid_highways' },
  { key: 'avoid_primary', labelKey: 'filters.avoid_primary' },
  { key: 'prefer_unpaved', labelKey: 'filters.prefer_unpaved' },
  { key: 'prefer_secondary', labelKey: 'filters.prefer_secondary' },
]

export function SegmentOptionsPanel({ waypointId }: Props) {
  const segmentOptions = useRouteStore((s) => s.segmentOptions)
  const setSegmentOption = useRouteStore((s) => s.setSegmentOption)
  const globalAdventure = useRouteStore((s) => s.adventure)
  const extremeLog = useRouteStore((s) => s.extremeLog)
  const t = useT()

  const opts: SegmentOptions = segmentOptions[waypointId] ?? defaultSegmentOptions
  const hasCustomAdventure = opts.adventure !== undefined

  // Recupera quanti passi sono stati trovati per questo segmento nell'ultimo calcolo
  const waypoints = useRouteStore((s) => s.waypoints)
  const segIndex = waypoints.findIndex((w) => w.id === waypointId)
  const logEntry = extremeLog.find((e) => e.segment === segIndex)
  const passesFound = logEntry?.passes_found ?? 0

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

      <div className={styles.extremeSection}>
        <label className={styles.extremeToggle}>
          <input
            type="checkbox"
            checked={opts.extreme}
            onChange={(e) => update({ extreme: e.target.checked })}
          />
          <span>{t('extreme.section_title')}</span>
          {opts.extreme && (
            <span className={styles.overrideNote}>{t('extreme.override_note')}</span>
          )}
        </label>

        {opts.extreme && (
          <>
            <div className={styles.extremeParam}>
              <label>
                {t('extreme.radius_label')}: {opts.extreme_radius_km} km
              </label>
              <input
                type="range"
                min={10}
                max={200}
                step={5}
                value={opts.extreme_radius_km}
                onChange={(e) => update({ extreme_radius_km: Number(e.target.value) })}
              />
            </div>
            <div className={styles.extremeParam}>
              <label>{t('extreme.direction_label')}</label>
              <div className={styles.directionButtons}>
                {(['N', 'S', 'E', 'O'] as const).map((d) => (
                  <button
                    key={d}
                    className={opts.extreme_direction === d ? styles.dirActive : styles.dirBtn}
                    onClick={() =>
                      update({ extreme_direction: opts.extreme_direction === d ? undefined : d })
                    }
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>
            <label className={styles.loopToggle}>
              <input
                type="checkbox"
                checked={opts.extreme_loop}
                onChange={(e) => update({ extreme_loop: e.target.checked })}
              />
              {t('extreme.loop_label')}
            </label>
            <PassSelector
              index={opts.extreme_pass_index}
              passesFound={passesFound}
              onChange={(i) => update({ extreme_pass_index: i })}
            />
          </>
        )}
      </div>
    </div>
  )
}
