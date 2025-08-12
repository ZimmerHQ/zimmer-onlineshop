'use client'

import { useEffect } from 'react'
import DashboardLayout from '@/components/DashboardLayout'
import { useDashboardStore, type Theme, type Language } from '@/lib/store'
import { Settings, Shield, Bell, Palette, Database, Sun, Moon, Globe, Check } from 'lucide-react'

// Translations
const translations = {
  fa: {
    title: 'تنظیمات',
    subtitle: 'پیکربندی تنظیمات داشبورد مدیریت',
    appearance: 'ظاهر',
    appearanceDesc: 'شخصی‌سازی ظاهر داشبورد',
    theme: 'تم',
    lightTheme: 'روشن',
    darkTheme: 'تاریک',
    language: 'زبان',
    persian: 'فارسی',
    english: 'انگلیسی',
    configure: 'پیکربندی',
    comingSoon: 'تنظیمات به زودی',
    comingSoonDesc: 'این صفحه تنظیمات در حال حاضر یک جایگزین است. گزینه‌های پیکربندی پیشرفته در به‌روزرسانی‌های آینده در دسترس خواهند بود.',
    accountSettings: 'تنظیمات حساب کاربری',
    accountDesc: 'مدیریت تنظیمات حساب کاربری مدیر',
    profileInfo: 'اطلاعات پروفایل',
    passwordSecurity: 'رمز عبور و امنیت',
    notifications: 'تنظیمات اعلان‌ها',
    languageRegion: 'زبان و منطقه',
    security: 'امنیت',
    securityDesc: 'پیکربندی امنیت و کنترل دسترسی',
    twoFactor: 'احراز هویت دو مرحله‌ای',
    sessionManagement: 'مدیریت نشست',
    apiKeys: 'کلیدهای API',
    accessReports: 'گزارش‌های دسترسی',
    notificationsTitle: 'اعلان‌ها',
    notificationsDesc: 'شخصی‌سازی تنظیمات اعلان',
    emailNotifications: 'اعلان‌های ایمیل',
    pushNotifications: 'اعلان‌های فوری',
    smsAlerts: 'هشدارهای پیامکی',
    webhookEndpoints: 'نقاط پایانی Webhook',
    dataManagement: 'مدیریت داده',
    dataDesc: 'مدیریت داده و پشتیبان‌گیری',
    dataExport: 'خروجی داده',
    backupSettings: 'تنظیمات پشتیبان‌گیری',
    dataRetention: 'نگهداری داده',
    privacyControls: 'کنترل‌های حریم خصوصی',
  },
  en: {
    title: 'Settings',
    subtitle: 'Configure dashboard management settings',
    appearance: 'Appearance',
    appearanceDesc: 'Customize dashboard appearance',
    theme: 'Theme',
    lightTheme: 'Light',
    darkTheme: 'Dark',
    language: 'Language',
    persian: 'Persian',
    english: 'English',
    configure: 'Configure',
    comingSoon: 'Settings Coming Soon',
    comingSoonDesc: 'This settings page is currently a placeholder. Advanced configuration options will be available in future updates.',
    accountSettings: 'Account Settings',
    accountDesc: 'Manage administrator account settings',
    profileInfo: 'Profile Information',
    passwordSecurity: 'Password & Security',
    notifications: 'Notification Settings',
    languageRegion: 'Language & Region',
    security: 'Security',
    securityDesc: 'Configure security and access control',
    twoFactor: 'Two-Factor Authentication',
    sessionManagement: 'Session Management',
    apiKeys: 'API Keys',
    accessReports: 'Access Reports',
    notificationsTitle: 'Notifications',
    notificationsDesc: 'Customize notification settings',
    emailNotifications: 'Email Notifications',
    pushNotifications: 'Push Notifications',
    smsAlerts: 'SMS Alerts',
    webhookEndpoints: 'Webhook Endpoints',
    dataManagement: 'Data Management',
    dataDesc: 'Manage data and backup',
    dataExport: 'Data Export',
    backupSettings: 'Backup Settings',
    dataRetention: 'Data Retention',
    privacyControls: 'Privacy Controls',
  },
}

const settingsSections = (t: typeof translations.fa) => [
  {
    title: t.accountSettings,
    description: t.accountDesc,
    icon: Settings,
    items: [
      t.profileInfo,
      t.passwordSecurity,
      t.notifications,
      t.languageRegion,
    ],
  },
  {
    title: t.security,
    description: t.securityDesc,
    icon: Shield,
    items: [
      t.twoFactor,
      t.sessionManagement,
      t.apiKeys,
      t.accessReports,
    ],
  },
  {
    title: t.notificationsTitle,
    description: t.notificationsDesc,
    icon: Bell,
    items: [
      t.emailNotifications,
      t.pushNotifications,
      t.smsAlerts,
      t.webhookEndpoints,
    ],
  },
  {
    title: t.appearance,
    description: t.appearanceDesc,
    icon: Palette,
    items: [
      t.theme,
      'رنگ‌بندی',
      'گزینه‌های چیدمان',
      'پیکربندی نوار کناری',
    ],
  },
  {
    title: t.dataManagement,
    description: t.dataDesc,
    icon: Database,
    items: [
      t.dataExport,
      t.backupSettings,
      t.dataRetention,
      t.privacyControls,
    ],
  },
]

export default function SettingsPage() {
  const { theme, language, setTheme, setLanguage, toggleTheme, toggleLanguage } = useDashboardStore()
  const t = translations[language]

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  }, [theme])

  // Apply language direction to document
  useEffect(() => {
    const html = document.documentElement
    html.lang = language
    html.dir = language === 'fa' ? 'rtl' : 'ltr'
  }, [language])

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t.title}</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">{t.subtitle}</p>
        </div>

        {/* Theme and Language Toggles */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Theme Toggle */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <Palette className="h-6 w-6 text-blue-600 dark:text-blue-400 ml-3" />
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{t.theme}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{t.appearanceDesc}</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setTheme('light')}
                  className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    theme === 'light'
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  <Sun className="h-4 w-4 ml-2" />
                  {t.lightTheme}
                  {theme === 'light' && <Check className="h-4 w-4 mr-2" />}
                </button>
                
                <button
                  onClick={() => setTheme('dark')}
                  className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    theme === 'dark'
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  <Moon className="h-4 w-4 ml-2" />
                  {t.darkTheme}
                  {theme === 'dark' && <Check className="h-4 w-4 mr-2" />}
                </button>
              </div>
              
              <button
                onClick={toggleTheme}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                {theme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
              </button>
            </div>
          </div>

          {/* Language Toggle */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <Globe className="h-6 w-6 text-blue-600 dark:text-blue-400 ml-3" />
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{t.language}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">انتخاب زبان / Choose Language</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setLanguage('fa')}
                  className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    language === 'fa'
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  🇮🇷 {t.persian}
                  {language === 'fa' && <Check className="h-4 w-4 mr-2" />}
                </button>
                
                <button
                  onClick={() => setLanguage('en')}
                  className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    language === 'en'
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  🇺🇸 {t.english}
                  {language === 'en' && <Check className="h-4 w-4 mr-2" />}
                </button>
              </div>
              
              <button
                onClick={toggleLanguage}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Globe className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Settings Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {settingsSections(t).map((section) => {
            const Icon = section.icon
            return (
              <div key={section.title} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex items-center mb-4">
                  <div className="flex-shrink-0">
                    <Icon className="h-8 w-8 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div className="mr-3">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{section.title}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{section.description}</p>
                  </div>
                </div>
                
                <ul className="space-y-2">
                  {section.items.map((item) => (
                    <li key={item} className="flex items-center">
                      <div className="w-2 h-2 bg-gray-300 dark:bg-gray-600 rounded-full ml-3" />
                      <span className="text-sm text-gray-700 dark:text-gray-300">{item}</span>
                    </li>
                  ))}
                </ul>
                
                <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button className="w-full inline-flex items-center justify-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                    {t.configure}
                  </button>
                </div>
              </div>
            )
          })}
        </div>

        {/* Coming Soon Notice */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <Settings className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="mr-3">
              <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">{t.comingSoon}</h3>
              <div className="mt-2 text-sm text-blue-700 dark:text-blue-300">
                <p>{t.comingSoonDesc}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
} 