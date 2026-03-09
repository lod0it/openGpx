import { useState, useRef, useEffect } from 'react'
import { useRouteStore } from '../../store/useRouteStore'
import { useGeocoding } from '../../hooks/useGeocoding'
import { useT } from '../../i18n/useT'
import type { GeocodeResult } from '../../types'
import styles from './SearchBar.module.css'

export function SearchBar() {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const addWaypoint = useRouteStore((s) => s.addWaypoint)
  const { results, isSearching } = useGeocoding(query)
  const wrapperRef = useRef<HTMLDivElement>(null)
  const t = useT()

  useEffect(() => {
    setOpen(results.length > 0)
  }, [results])

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  function selectResult(r: GeocodeResult) {
    addWaypoint({ lat: r.lat, lng: r.lng, name: r.display_name.split(',')[0] })
    setQuery('')
    setOpen(false)
  }

  return (
    <div className={styles.wrapper} ref={wrapperRef}>
      <input
        className={styles.input}
        type="text"
        placeholder={t('search.placeholder')}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => results.length > 0 && setOpen(true)}
      />
      {isSearching && <div className={styles.spinner} />}
      {open && (
        <ul className={styles.dropdown}>
          {results.map((r, i) => (
            <li key={i} className={styles.item} onMouseDown={() => selectResult(r)}>
              {r.display_name}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
