'use client'

import DashboardLayout from '@/components/DashboardLayout'
import { useDashboardStore, type Theme, type Language } from '@/lib/store'
import { Settings, Shield, Bell, Palette, Database, Sun, Moon, Globe, Check, Bot, Eye, EyeOff } from 'lucide-react'
import { integrationsApi, type TelegramConfig, type TelegramConfigRequest } from '@/lib/api/integrations'
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { toast } from 'sonner'

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

  // Telegram integrations state
  const [telegramConfig, setTelegramConfig] = useState<TelegramConfig | null>(null)
  const [telegramForm, setTelegramForm] = useState<TelegramConfigRequest>({
    bot_token: '',
    webhook_url: '',
    secret: ''
  })
  const [showToken, setShowToken] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isTesting, setIsTesting] = useState(false)
  const [isSettingWebhook, setIsSettingWebhook] = useState(false)

  // Load Telegram configuration
  useEffect(() => {
    loadTelegramConfig()
  }, [])

  const loadTelegramConfig = async () => {
    try {
      const config = await integrationsApi.getTelegramConfig()
      setTelegramConfig(config)
      setTelegramForm({
        bot_token: config.bot_token_exists ? '••••••••••••••••••••••••••••••••' : '',
        webhook_url: config.webhook_url || '',
        secret: config.secret_exists ? '••••••••••••••••••••••••••••••••' : ''
      })
    } catch (error) {
      console.error('Failed to load Telegram config:', error)
    }
  }

  const handleSaveTelegramConfig = async () => {
    setIsLoading(true)
    try {
      await integrationsApi.updateTelegramConfig(telegramForm)
      toast.success('تنظیمات تلگرام با موفقیت ذخیره شد')
      await loadTelegramConfig()
    } catch (error) {
      toast.error('خطا در ذخیره تنظیمات تلگرام')
    } finally {
      setIsLoading(false)
    }
  }

  const handleTestConnection = async () => {
    setIsTesting(true)
    try {
      const result = await integrationsApi.testTelegramConnection()
      if (result.ok) {
        toast.success(`اتصال موفق: ${result.info?.bot_name} (@${result.info?.username})`)
      } else {
        toast.error('خطا در اتصال به تلگرام')
      }
    } catch (error) {
      toast.error('خطا در تست اتصال')
    } finally {
      setIsTesting(false)
    }
  }

  const handleSetWebhook = async () => {
    setIsSettingWebhook(true)
    try {
      const result = await integrationsApi.setTelegramWebhook()
      if (result.ok) {
        toast.success('Webhook با موفقیت تنظیم شد')
      } else {
        toast.error('خطا در تنظیم Webhook')
      }
    } catch (error) {
      toast.error('خطا در تنظیم Webhook')
    } finally {
      setIsSettingWebhook(false)
    }
  }

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

        {/* Telegram Integrations */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Bot className="h-5 w-5 ml-2" />
              تنظیمات ربات تلگرام
            </CardTitle>
            <CardDescription>
              پیکربندی توکن ربات، آدرس Webhook و تست اتصال
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Bot Token */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">توکن ربات</label>
              <div className="flex items-center space-x-2 space-x-reverse">
                <Input
                  type={showToken ? "text" : "password"}
                  value={telegramForm.bot_token}
                  onChange={(e) => setTelegramForm({...telegramForm, bot_token: e.target.value})}
                  placeholder="توکن ربات تلگرام"
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowToken(!showToken)}
                  className="px-3"
                >
                  {showToken ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            {/* Webhook URL */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">آدرس Webhook</label>
              <Input
                type="url"
                value={telegramForm.webhook_url}
                onChange={(e) => setTelegramForm({...telegramForm, webhook_url: e.target.value})}
                placeholder="https://yourdomain.com/api/telegram/webhook"
              />
            </div>

            {/* Secret */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">کلید امنیتی (اختیاری)</label>
              <Input
                type="password"
                value={telegramForm.secret}
                onChange={(e) => setTelegramForm({...telegramForm, secret: e.target.value})}
                placeholder="کلید امنیتی برای تایید Webhook"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex items-center space-x-3 space-x-reverse pt-2">
              <Button
                onClick={handleSaveTelegramConfig}
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {isLoading ? 'در حال ذخیره...' : 'ذخیره تنظیمات'}
              </Button>
              
              <Button
                onClick={handleTestConnection}
                disabled={isTesting || !telegramForm.bot_token}
                variant="outline"
              >
                {isTesting ? 'در حال تست...' : 'تست اتصال'}
              </Button>
              
              <Button
                onClick={handleSetWebhook}
                disabled={isSettingWebhook || !telegramForm.bot_token || !telegramForm.webhook_url}
                variant="outline"
              >
                {isSettingWebhook ? 'در حال تنظیم...' : 'تنظیم Webhook'}
              </Button>
            </div>
          </CardContent>
        </Card>

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