import { useRef, useState, useEffect, useCallback } from 'react'
import { SearchBar } from './SearchBar'
import { AdventureSlider } from './AdventureSlider'
import { GlobalFiltersPanel } from './GlobalFilters'
import { WaypointList } from './WaypointList'
import { RouteStats } from './RouteStats'
import { ElevationChart } from './ElevationChart'
import { RoadTypeBreakdown } from './RoadTypeBreakdown'
import { ExtremeLog } from './ExtremeLog'
import { ExportButtons } from './ExportButtons'
import styles from './Sidebar.module.css'

const MIN_WIDTH = 220
const MAX_WIDTH = 520
const STORAGE_KEY = 'sidebar-width'

export function Sidebar() {
  const [width, setWidth] = useState<number>(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    const parsed = saved ? parseInt(saved, 10) : 300
    return Math.min(Math.max(parsed, MIN_WIDTH), MAX_WIDTH)
  })

  const dragging = useRef(false)
  const startX = useRef(0)
  const startWidth = useRef(0)

  const onMouseMove = useCallback((e: MouseEvent) => {
    if (!dragging.current) return
    const delta = e.clientX - startX.current
    const next = Math.min(Math.max(startWidth.current + delta, MIN_WIDTH), MAX_WIDTH)
    setWidth(next)
  }, [])

  const onMouseUp = useCallback(() => {
    if (!dragging.current) return
    dragging.current = false
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }, [])

  useEffect(() => {
    document.addEventListener('mousemove', onMouseMove)
    document.addEventListener('mouseup', onMouseUp)
    return () => {
      document.removeEventListener('mousemove', onMouseMove)
      document.removeEventListener('mouseup', onMouseUp)
    }
  }, [onMouseMove, onMouseUp])

  // Persisti la larghezza quando il drag finisce
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, String(width))
  }, [width])

  function onHandleMouseDown(e: React.MouseEvent) {
    e.preventDefault()
    dragging.current = true
    startX.current = e.clientX
    startWidth.current = width
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }

  return (
    <div className={styles.sidebar} style={{ width, minWidth: width }}>
      <div className={styles.logo}>open-gpx</div>
      <SearchBar />
      <AdventureSlider />
      <GlobalFiltersPanel />
      <RouteStats />
      <div className={styles.scrollArea}>
        <WaypointList />
        <ElevationChart />
        <RoadTypeBreakdown />
        <ExtremeLog />
      </div>
      <ExportButtons />
      <div className={styles.resizeHandle} onMouseDown={onHandleMouseDown} />
    </div>
  )
}
