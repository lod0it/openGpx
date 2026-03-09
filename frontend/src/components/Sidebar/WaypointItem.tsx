import { useState } from 'react'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { useRouteStore } from '../../store/useRouteStore'
import { SegmentOptionsPanel } from './SegmentOptions'
import type { Waypoint } from '../../types'
import styles from './WaypointItem.module.css'

interface Props {
  waypoint: Waypoint
  index: number
  isLast: boolean
}

export function WaypointItem({ waypoint, index, isLast }: Props) {
  const removeWaypoint = useRouteStore((s) => s.removeWaypoint)
  const [expanded, setExpanded] = useState(false)
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
    <div ref={setNodeRef} style={style}>
      <div className={`${styles.item} ${!isLast && expanded ? styles.itemExpanded : ''}`}>
        <span className={styles.handle} {...attributes} {...listeners}>
          ::
        </span>
        <span className={styles.index}>{index + 1}</span>
        <span className={styles.label} title={label}>
          {label}
        </span>
        {!isLast && (
          <button
            className={`${styles.optBtn} ${expanded ? styles.optBtnActive : ''}`}
            onClick={() => setExpanded((v) => !v)}
            title="Opzioni segmento"
          >
            opt
          </button>
        )}
        <button
          className={styles.deleteBtn}
          onClick={() => removeWaypoint(waypoint.id)}
          title="Rimuovi waypoint"
        >
          x
        </button>
      </div>
      {!isLast && expanded && <SegmentOptionsPanel waypointId={waypoint.id} />}
    </div>
  )
}
