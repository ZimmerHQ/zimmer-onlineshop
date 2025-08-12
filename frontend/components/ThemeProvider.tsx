'use client'

import { useEffect } from 'react'
import { useDashboardStore } from '@/lib/store'

export default function ThemeProvider({
  children,
}: {
  children: React.ReactNode
}) {
  const { theme, language } = useDashboardStore()

  // Apply theme and language on mount and when they change
  useEffect(() => {
    const root = document.documentElement
    const html = document.documentElement

    // Apply theme
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }

    // Apply language
    html.lang = language
    html.dir = language === 'fa' ? 'rtl' : 'ltr'
  }, [theme, language])

  return <>{children}</>
} 