import { useRouteStore } from '../../store/useRouteStore'
import type { RouteProfile } from '../../types'
import styles from './ProfileSelector.module.css'

const PROFILES: { value: RouteProfile; label: string }[] = [
  { value: 'standard', label: 'Standard' },
  { value: 'avoid_tolls', label: 'No Tolls' },
  { value: 'scenic', label: 'Scenic' },
]

export function ProfileSelector() {
  const profile = useRouteStore((s) => s.profile)
  const setProfile = useRouteStore((s) => s.setProfile)

  return (
    <div className={styles.wrapper}>
      {PROFILES.map((p) => (
        <button
          key={p.value}
          className={`${styles.btn} ${profile === p.value ? styles.active : ''}`}
          onClick={() => setProfile(p.value)}
        >
          {p.label}
        </button>
      ))}
    </div>
  )
}
