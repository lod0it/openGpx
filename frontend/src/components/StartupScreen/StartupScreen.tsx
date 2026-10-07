import { useEffect, useState } from 'react'
import { useI18nStore } from '../../store/useI18nStore'
import { translations } from '../../i18n/translations'
import styles from './StartupScreen.module.css'

const POLL_MS = 2000
const ERROR_AFTER_MS = 90000

type Status = { backend: string; graphhopper: string }

export function StartupScreen() {
  const lang = useI18nStore((s) => s.lang)
  const t = (k: string) => translations[lang][k] ?? k

  const [ready, setReady] = useState(false)
  const [status, setStatus] = useState<Status | null>(null)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    let cancelled = false
    let timer: number | undefined
    const startedAt = Date.now()
    let lastBackendOk = startedAt

    async function poll() {
      try {
        const r = await fetch('/api/system/status')
        if (!r.ok) throw new Error(String(r.status))
        const data: Status = await r.json()
        if (cancelled) return
        lastBackendOk = Date.now()
        setFailed(false)
        setStatus(data)
        if (data.backend === 'ok' && data.graphhopper === 'ready') {
          setReady(true)
          return
        }
      } catch {
        if (cancelled) return
        setStatus(null)
        if (Date.now() - lastBackendOk >= ERROR_AFTER_MS) setFailed(true)
      }
      timer = window.setTimeout(poll, POLL_MS)
    }

    poll()
    return () => {
      cancelled = true
      window.clearTimeout(timer)
    }
  }, [])

  if (ready) return null

  const backendOk = status?.backend === 'ok'
  const ghOk = status?.graphhopper === 'ready'

  return (
    <div className={styles.overlay}>
      <div className={styles.card}>
        <h2 className={styles.title}>{failed ? t('startup.error.title') : t('startup.title')}</h2>
        <div className={styles.row}>
          <span>{t('startup.backend')}</span>
          <span className={backendOk ? styles.ok : styles.pending}>
            {backendOk ? t('startup.state.ok') : t('startup.state.waiting')}
          </span>
        </div>
        <div className={styles.row}>
          <span>{t('startup.graphhopper')}</span>
          <span className={ghOk ? styles.ok : styles.pending}>
            {ghOk
              ? t('startup.state.ok')
              : backendOk
                ? t('startup.state.starting')
                : t('startup.state.waiting')}
          </span>
        </div>
        {failed && <p className={styles.hint}>{t('startup.error.hint')}</p>}
      </div>
    </div>
  )
}
