'use client'

import { useState, useEffect } from 'react'
import { useDashboardStore } from '@/lib/store'
import { cn } from '@/lib/utils'
import { 
  MessageSquare, 
  Package, 
  ShoppingCart, 
  Headphones, 
  Settings,
  MessageCircle,
  Bot,
  Home,
  Users,
  BarChart3,
  Hash,
  HelpCircle,
  Bell,
  User
} from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const navigation = [
  { name: 'داشبورد', href: '/', icon: Home },
  { name: 'مکالمات', href: '/conversations', icon: MessageSquare },
  { name: 'چت‌بات', href: '/dashboard/chat', icon: MessageCircle },
  { name: 'محصولات', href: '/products', icon: Package },
  { name: 'سفارش‌ها', href: '/orders', icon: ShoppingCart },
  { name: 'مدیریت مشتریان', href: '/analytics/crm', icon: Users },
  { name: 'پشتیبانی', href: '/support', icon: Headphones },
  { name: 'سوالات متداول', href: '/faq', icon: HelpCircle },
  { name: 'تحلیل‌ها', href: '/analytics', icon: BarChart3 },
  { name: 'تنظیمات', href: '/settings', icon: Settings },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const { theme, language, toggleTheme, toggleLanguage } = useDashboardStore()
  const [isClient, setIsClient] = useState(false)

  // Ensure client-side rendering to prevent hydration mismatch
  useEffect(() => {
    setIsClient(true)
  }, [])

  // Don't render anything until client-side hydration is complete
  if (!isClient) {
    return (
        <div className="min-h-screen bg-white" dir="rtl">
          <div className="flex">
            {/* Sidebar skeleton */}
            <div className="w-64 bg-gray-50 border-r border-gray-200 min-h-screen">
              <div className="p-6">
                <div className="h-8 bg-gray-200 rounded animate-pulse mb-8" />
                <div className="space-y-4">
                  {[...Array(8)].map((_, i) => (
                    <div key={i} className="h-10 bg-gray-200 rounded animate-pulse" />
                  ))}
                </div>
              </div>
            </div>
            
            {/* Main content skeleton */}
            <div className="flex-1">
              <div className="p-6">
                <div className="h-8 bg-gray-200 rounded animate-pulse mb-6" />
                <div className="space-y-4">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="h-20 bg-gray-200 rounded animate-pulse" />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
    )
  }

  return (
        <div className="min-h-screen bg-white" dir="rtl">
          <div className="flex">
            {/* Sidebar - Always visible */}
            <div className="w-64 bg-gray-50 border-r border-gray-200 min-h-screen flex flex-col hidden md:flex">
          {/* Header */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center space-x-3 space-x-reverse">
              <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">Z</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">zimmer</h1>
                <p className="text-sm text-gray-600">دستیار خرید</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {navigation.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 zimmer-focus-ring",
                        isActive
                          ? "bg-primary-500 text-white shadow-sm"
                          : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                  )}
                >
                  <item.icon className={cn(
                    "mr-3 h-5 w-5",
                    isActive ? "text-white" : "text-gray-600"
                  )} />
                  {item.name}
                </Link>
              )
            })}
          </nav>

              {/* Footer */}
              <div className="p-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <button
                    onClick={toggleTheme}
                    className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-600 hover:text-gray-900 zimmer-focus-ring"
                    aria-label={theme === 'light' ? 'تغییر به حالت تاریک' : 'تغییر به حالت روشن'}
                  >
                    {theme === 'light' ? '🌙' : '☀️'}
                  </button>
                  
                  <button
                    onClick={toggleLanguage}
                    className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-600 hover:text-gray-900 zimmer-focus-ring"
                    aria-label={language === 'fa' ? 'Switch to English' : 'تغییر به فارسی'}
                  >
                    {language === 'fa' ? 'EN' : 'فا'}
                  </button>
                </div>
              </div>
        </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col w-full md:w-auto">
              {/* Top Header */}
              <header className="bg-white border-b border-gray-200 px-4 md:px-6 py-4 sticky-mobile">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">
                      {navigation.find(item => item.href === pathname)?.name || 'داشبورد'}
                    </h2>
                    <p className="text-sm text-gray-600 hidden md:block">خوش آمدید</p>
                  </div>
              
              <div className="flex items-center space-x-2 md:space-x-4 space-x-reverse">
                {/* Quick Actions */}
                <div className="flex items-center space-x-2 space-x-reverse">
                  <button
                    className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-600 hover:text-gray-900 zimmer-focus-ring"
                    aria-label="اعلان‌ها"
                  >
                    <Bell className="h-5 w-5" />
                  </button>
                  
                  <button
                    className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-600 hover:text-gray-900 zimmer-focus-ring"
                    aria-label="پروفایل کاربر"
                  >
                    <User className="h-5 w-5" />
                  </button>
                  
                  <button
                    className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-600 hover:text-gray-900 zimmer-focus-ring"
                    aria-label="تنظیمات"
                  >
                    <Settings className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          </header>

              {/* Page Content */}
              <main className="flex-1 p-4 md:p-6 safe-area-padding">
                {children}
              </main>
        </div>
      </div>
    </div>
  )
} 