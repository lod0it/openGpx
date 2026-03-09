import { useRouteStore } from '../../store/useRouteStore'
import { useT } from '../../i18n/useT'
import styles from './AdventureSlider.module.css'

function adventureLabelKey(v: number): string {
  if (v === 0) return 'adventure.fast'
  if (v <= 25) return 'adventure.light'
  if (v <= 50) return 'adventure.moderate'
  if (v <= 75) return 'adventure.adventurous'
  return 'adventure.extreme'
}

interface Props {
  value: number
  onChange: (v: number) => void
  label?: string
}

export function AdventureSliderControl({ value, onChange, label }: Props) {
  const t = useT()
  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <span className={styles.title}>{label ?? t('adventure')}</span>
        <span className={styles.badge}>{t(adventureLabelKey(value))}</span>
      </div>
      <div className={styles.trackWrapper}>
        <input
          type="range"
          min={0}
          max={100}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className={styles.slider}
          style={{ '--val': `${value}%` } as React.CSSProperties}
        />
      </div>
    </div>
  )
}

export function AdventureSlider() {
  const adventure = useRouteStore((s) => s.adventure)
  const setAdventure = useRouteStore((s) => s.setAdventure)

  return <AdventureSliderControl value={adventure} onChange={setAdventure} />
}
