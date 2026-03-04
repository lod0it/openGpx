import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core'
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { useRouteStore } from '../../store/useRouteStore'
import { WaypointItem } from './WaypointItem'
import styles from './WaypointList.module.css'

export function WaypointList() {
  const waypoints = useRouteStore((s) => s.waypoints)
  const reorderWaypoints = useRouteStore((s) => s.reorderWaypoints)
  const clearAll = useRouteStore((s) => s.clearAll)

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  )

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event
    if (over && active.id !== over.id) {
      const oldIndex = waypoints.findIndex((w) => w.id === active.id)
      const newIndex = waypoints.findIndex((w) => w.id === over.id)
      reorderWaypoints(oldIndex, newIndex)
    }
  }

  if (waypoints.length === 0) {
    return (
      <div className={styles.empty}>
        Click on the map to add waypoints
      </div>
    )
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <span className={styles.count}>{waypoints.length} point{waypoints.length !== 1 ? 's' : ''}</span>
        <button className={styles.clearBtn} onClick={clearAll}>Clear all</button>
      </div>
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={waypoints.map((w) => w.id)} strategy={verticalListSortingStrategy}>
          {waypoints.map((wp, index) => (
            <WaypointItem key={wp.id} waypoint={wp} index={index} />
          ))}
        </SortableContext>
      </DndContext>
    </div>
  )
}
