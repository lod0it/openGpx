import { SearchBar } from './SearchBar'
import { AdventureSlider } from './AdventureSlider'
import { GlobalFiltersPanel } from './GlobalFilters'
import { WaypointList } from './WaypointList'
import { RouteStats } from './RouteStats'
import { ElevationChart } from './ElevationChart'
import { RoadTypeBreakdown } from './RoadTypeBreakdown'
import { ExportButtons } from './ExportButtons'
import styles from './Sidebar.module.css'

export function Sidebar() {
  return (
    <div className={styles.sidebar}>
      <div className={styles.logo}>
        open-gpx
      </div>
      <SearchBar />
      <AdventureSlider />
      <GlobalFiltersPanel />
      <RouteStats />
      <div className={styles.scrollArea}>
        <WaypointList />
        <ElevationChart />
        <RoadTypeBreakdown />
      </div>
      <ExportButtons />
    </div>
  )
}
