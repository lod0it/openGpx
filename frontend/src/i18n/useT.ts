import { useI18nStore } from '../store/useI18nStore'
import { translations } from './translations'

export function useT() {
  const lang = useI18nStore((s) => s.lang)
  return (key: string) => translations[lang][key] ?? key
}
