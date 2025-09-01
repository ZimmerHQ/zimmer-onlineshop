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
  HelpCircle
} from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Conversations', href: '/conversations', icon: MessageSquare },
  { name: 'Chatbot', href: '/dashboard/chat', icon: MessageCircle },
  { name: 'Products', href: '/products', icon: Package },
  { name: 'Orders', href: '/orders', icon: ShoppingCart },
  { name: 'Support', href: '/support', icon: Headphones },
  { name: 'FAQ', href: '/faq', icon: HelpCircle },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
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
      <div className="min-h-screen bg-white">
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
    <div className="min-h-screen bg-white">
      <div className="flex">
        {/* Sidebar - Always visible */}
        <div className="w-64 bg-gray-50 border-r border-gray-200 min-h-screen flex flex-col">
          {/* Header */}
          <div className="p-6 border-b border-gray-200">
            <h1 className="text-xl font-bold text-gray-900">Admin Panel</h1>
            <p className="text-sm text-gray-500 mt-1">Shopping Assistant</p>
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
                    "flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors duration-200",
                    isActive
                      ? "bg-black text-white shadow-sm"
                      : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                  )}
                >
                  <item.icon className={cn(
                    "mr-3 h-5 w-5",
                    isActive ? "text-white" : "text-gray-500"
                  )} />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <button
                  onClick={toggleTheme}
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  {theme === 'dark' ? (
                    <div className="w-5 h-5 bg-gray-300 rounded-full" />
                  ) : (
                    <div className="w-5 h-5 bg-gray-700 rounded-full" />
                  )}
                </button>
                <span className="text-xs text-gray-500">
                  {theme === 'dark' ? 'Dark' : 'Light'}
                </span>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={toggleLanguage}
                  className="px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
                >
                  {language === 'en' ? 'EN' : 'FA'}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Top Bar */}
          <header className="bg-white border-b border-gray-200 px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  {navigation.find(item => item.href === pathname)?.name || 'Dashboard'}
                </h2>
                <p className="text-sm text-gray-500 mt-1">
                  Manage your shopping assistant and customer interactions
                </p>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                    <Users className="w-4 h-4 text-gray-600" />
                  </div>
                  <div className="text-sm">
                    <div className="font-medium text-gray-900">Admin User</div>
                    <div className="text-gray-500">admin@example.com</div>
                  </div>
                </div>
              </div>
            </div>
          </header>

          {/* Page Content */}
          <main className="flex-1 p-6 bg-gray-50">
            <div className="max-w-7xl mx-auto">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
} 