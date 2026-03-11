import { useRef, useState } from 'react'
import { streamUpdate } from '../../api/system'
import { useI18nStore } from '../../store/useI18nStore'
import { translations } from '../../i18n/translations'
import styles from './UpdateButton.module.css'

export function UpdateButton() {
  const lang = useI18nStore((s) => s.lang)
  const t = (k: string) => translations[lang][k] ?? k

  const [open, setOpen] = useState(false)
  const [running, setRunning] = useState(false)
  const [lines, setLines] = useState<string[]>([])
  const outputRef = useRef<HTMLDivElement>(null)

  function scrollToBottom() {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight
    }
  }

  async function handleRun() {
    setLines([])
    setRunning(true)
    try {
      await streamUpdate((line) => {
        setLines((prev) => {
          const next = [...prev, line]
          setTimeout(scrollToBottom, 0)
          return next
        })
      })
    } catch (e) {
      setLines((prev) => [...prev, `Errore: ${e}`])
    } finally {
      setRunning(false)
      setTimeout(scrollToBottom, 0)
    }
  }

  return (
    <>
      <div className={styles.container}>
        <button
          className={styles.triggerBtn}
          onClick={() => setOpen(true)}
          data-tooltip={t('update.tooltip')}
        >
          {t('update.btn')}
        </button>
      </div>

      {open && (
        <div className={styles.modal}>
          <div className={styles.header}>
            <span className={styles.title}>{t('update.title')}</span>
            <button className={styles.closeBtn} onClick={() => setOpen(false)} disabled={running}>
              x
            </button>
          </div>

          <div className={styles.output} ref={outputRef}>
            {lines.length === 0 ? (
              <span className={styles.empty}>{t('update.idle')}</span>
            ) : (
              lines.map((l, i) => <div key={i}>{l}</div>)
            )}
          </div>

          <div className={styles.footer}>
            <button className={styles.runBtn} onClick={handleRun} disabled={running}>
              {running ? t('update.running') : t('update.run')}
            </button>
          </div>
        </div>
      )}
    </>
  )
}
