import { create } from 'zustand'
import type { Lang } from '../i18n/translations'

interface I18nStore {
  lang: Lang
  setLang: (lang: Lang) => void
}

export const useI18nStore = create<I18nStore>((set) => ({
  lang: (localStorage.getItem('lang') as Lang) ?? 'it',
  setLang: (lang) => {
    localStorage.setItem('lang', lang)
    set({ lang })
  },
}))
