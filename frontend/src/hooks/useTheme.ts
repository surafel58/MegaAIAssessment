import { useEffect, useState } from 'react'

export type ThemePreference = 'light' | 'dark' | 'system'
type ResolvedTheme = 'light' | 'dark'

function getSystemTheme(): ResolvedTheme {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function resolveTheme(pref: ThemePreference): ResolvedTheme {
  return pref === 'system' ? getSystemTheme() : pref
}

function applyTheme(resolved: ResolvedTheme) {
  document.documentElement.setAttribute('data-theme', resolved)
}

export function useTheme() {
  const [preference, setPreferenceState] = useState<ThemePreference>(() => {
    return (localStorage.getItem('theme-preference') as ThemePreference) ?? 'system'
  })

  const setPreference = (pref: ThemePreference) => {
    localStorage.setItem('theme-preference', pref)
    setPreferenceState(pref)
    applyTheme(resolveTheme(pref))
  }

  // Apply on mount in case the inline script wasn't present
  useEffect(() => {
    applyTheme(resolveTheme(preference))
  }, [])

  // Track system preference changes when in system mode
  useEffect(() => {
    if (preference !== 'system') return
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = () => applyTheme(getSystemTheme())
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [preference])

  return { preference, setPreference }
}
