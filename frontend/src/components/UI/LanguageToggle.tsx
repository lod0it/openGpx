import { useI18nStore } from '../../store/useI18nStore'
import { DarkThemeToggle } from './DarkThemeToggle'
import styles from './LanguageToggle.module.css'

export function LanguageToggle() {
  const lang = useI18nStore((s) => s.lang)
  const setLang = useI18nStore((s) => s.setLang)

  return (
    <div className={styles.wrapper}>
      <DarkThemeToggle />
      <span className={styles.sep}>|</span>
      <button
        className={`${styles.btn} ${lang === 'it' ? styles.active : ''}`}
        onClick={() => setLang('it')}
      >
        IT
      </button>
      <span className={styles.sep}>|</span>
      <button
        className={`${styles.btn} ${lang === 'en' ? styles.active : ''}`}
        onClick={() => setLang('en')}
      >
        EN
      </button>
    </div>
  )
}
