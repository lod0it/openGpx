import { Sidebar } from './components/Sidebar/Sidebar'
import { MapView } from './components/MapView/MapView'
import { useRouteCalculation } from './hooks/useRouteCalculation'
import './App.css'

function App() {
  useRouteCalculation()

  return (
    <div className="app-layout">
      <Sidebar />
      <MapView />
    </div>
  )
}

export default App
