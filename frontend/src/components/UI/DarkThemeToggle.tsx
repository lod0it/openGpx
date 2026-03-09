import { useThemeStore } from '../../store/useThemeStore'
import styles from './LanguageToggle.module.css'

export function DarkThemeToggle() {
  const theme = useThemeStore((s) => s.theme)
  const toggle = useThemeStore((s) => s.toggle)

  return (
    <button
      className={styles.btn}
      onClick={toggle}
      title={theme === 'light' ? 'Dark mode' : 'Light mode'}
    >
      {theme === 'light' ? 'Dark' : 'Light'}
    </button>
  )
}
