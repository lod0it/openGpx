import { useRouteStore } from '../../store/useRouteStore'
import type { RouteProfile } from '../../types'
import styles from './ProfileSelector.module.css'

const PROFILES: { value: RouteProfile; label: string; icon: string }[] = [
  { value: 'standard', label: 'Standard', icon: '🛣️' },
  { value: 'avoid_tolls', label: 'No Tolls', icon: '🚫' },
  { value: 'scenic', label: 'Scenic', icon: '🏔️' },
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
          title={p.label}
        >
          <span>{p.icon}</span>
          <span>{p.label}</span>
        </button>
      ))}
    </div>
  )
}
