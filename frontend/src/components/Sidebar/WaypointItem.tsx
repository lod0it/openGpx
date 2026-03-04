import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { useRouteStore } from '../../store/useRouteStore'
import type { Waypoint } from '../../types'
import styles from './WaypointItem.module.css'

interface Props {
  waypoint: Waypoint
  index: number
}

export function WaypointItem({ waypoint, index }: Props) {
  const removeWaypoint = useRouteStore((s) => s.removeWaypoint)
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: waypoint.id,
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  const label = waypoint.name ?? `${waypoint.lat.toFixed(4)}, ${waypoint.lng.toFixed(4)}`

  return (
    <div ref={setNodeRef} style={style} className={styles.item}>
      <span className={styles.handle} {...attributes} {...listeners}>
        ⠿
      </span>
      <span className={styles.index}>{index + 1}</span>
      <span className={styles.label} title={label}>
        {label}
      </span>
      <button
        className={styles.deleteBtn}
        onClick={() => removeWaypoint(waypoint.id)}
        title="Remove waypoint"
      >
        ✕
      </button>
    </div>
  )
}
