import { useEffect } from 'react'
import { Sidebar } from './components/Sidebar/Sidebar'
import { MapView } from './components/MapView/MapView'
import { MapPanel } from './components/MapView/MapPanel'
import { LanguageToggle } from './components/UI/LanguageToggle'
import { useRouteCalculation } from './hooks/useRouteCalculation'
import { useThemeStore } from './store/useThemeStore'
import './App.css'

function App() {
  useRouteCalculation()
  const theme = useThemeStore((s) => s.theme)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="map-wrapper">
        <MapView />
        <MapPanel />
      </div>
      <LanguageToggle />
    </div>
  )
}

export default App
