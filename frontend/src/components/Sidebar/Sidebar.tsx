import { SearchBar } from './SearchBar'
import { ProfileSelector } from './ProfileSelector'
import { WaypointList } from './WaypointList'
import { RouteStats } from './RouteStats'
import { ExportButtons } from './ExportButtons'
import styles from './Sidebar.module.css'

export function Sidebar() {
  return (
    <div className={styles.sidebar}>
      <div className={styles.logo}>
        <span>🏍️</span>
        <span>open-gpx</span>
      </div>
      <SearchBar />
      <ProfileSelector />
      <RouteStats />
      <WaypointList />
      <ExportButtons />
    </div>
  )
}
