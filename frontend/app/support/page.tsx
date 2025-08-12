'use client'

import { useEffect } from 'react'
import DashboardLayout from '@/components/DashboardLayout'
import { useDashboardStore, type SupportRequest } from '@/lib/store'
import { formatDate } from '@/lib/utils'
import { Headphones, Phone, CheckCircle, Clock, User, AlertCircle, MessageSquare, Mail, Star } from 'lucide-react'

// Sample dummy support requests data
const dummySupportRequests: SupportRequest[] = [
  {
    id: '1',
    userId: 'user_001',
    phone: '09123456789',
    message: 'سلام، من دیروز یک سفارش ثبت کردم اما هنوز وضعیت آن تغییر نکرده. شماره سفارش: ORD-2024-001. لطفاً بررسی کنید.',
    status: 'pending',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
  },
  {
    id: '2',
    userId: 'user_002',
    phone: '09987654321',
    message: 'محصولی که دریافت کردم با تصویر سایت متفاوت است. کیفیت پایین‌تری دارد. می‌خواهم بازگشت کنم.',
    status: 'handled',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 1), // 1 day ago
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 12), // 12 hours ago
  },
  {
    id: '3',
    userId: 'user_003',
    phone: '09351234567',
    message: 'آیا امکان ارسال رایگان برای خریدهای بالای ۵۰۰ هزار تومان دارید؟ و آیا به شهرستان‌ها هم ارسال می‌کنید؟',
    status: 'pending',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 6), // 6 hours ago
  },
  {
    id: '4',
    userId: 'user_004',
    phone: '09111222333',
    message: 'سایت شما عالی است! محصولات با کیفیت و قیمت مناسب. فقط می‌خواستم تشکر کنم.',
    status: 'handled',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2), // 2 days ago
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 1), // 1 day ago
  },
  {
    id: '5',
    userId: 'user_005',
    phone: '09334445556',
    message: 'من سایز M سفارش دادم اما سایز L دریافت کردم. می‌خواهم تعویض کنم.',
    status: 'pending',
    createdAt: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
  },
  {
    id: '6',
    userId: 'user_006',
    phone: '09199888777',
    message: 'آیا امکان پرداخت در محل دارید؟ و آیا کارت‌های اعتباری خارجی را قبول می‌کنید؟',
    status: 'handled',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3), // 3 days ago
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2), // 2 days ago
  },
  {
    id: '7',
    userId: 'user_007',
    phone: '09376665554',
    message: 'محصولی که خریدم معیوب بود. در بسته‌بندی باز شده بود و آسیب دیده بود.',
    status: 'pending',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 4), // 4 hours ago
  },
  {
    id: '8',
    userId: 'user_008',
    phone: '09122334455',
    message: 'می‌خواستم بپرسم آیا امکان خرید عمده دارید؟ برای شرکت‌مان نیاز به ۵۰ عدد داریم.',
    status: 'handled',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5), // 5 days ago
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 4), // 4 days ago
  },
]

export default function SupportPage() {
  const { supportRequests, loading, errors, fetchSupportRequests, markSupportRequestHandled, setSupportRequests } = useDashboardStore()

  useEffect(() => {
    // For demo purposes, set dummy data instead of fetching from API
    setSupportRequests(dummySupportRequests)
  }, [setSupportRequests])

  const pendingRequests = supportRequests.filter(request => request.status === 'pending')
  const handledRequests = supportRequests.filter(request => request.status === 'handled')

  const handleMarkHandled = (id: string) => {
    markSupportRequestHandled(id)
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">درخواست‌های پشتیبانی انسانی</h1>
            <p className="text-gray-600 mt-1">مدیریت درخواست‌های پشتیبانی مشتریان که نیاز به کمک انسانی دارند</p>
          </div>
          
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-600 mt-2">در حال بارگذاری درخواست‌های پشتیبانی...</p>
            </div>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (errors) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">درخواست‌های پشتیبانی انسانی</h1>
            <p className="text-gray-600 mt-1">مدیریت درخواست‌های پشتیبانی مشتریان که نیاز به کمک انسانی دارند</p>
          </div>
          
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <p className="text-red-600 font-medium">خطا در بارگذاری درخواست‌های پشتیبانی</p>
              <p className="text-gray-600 mt-1">{errors}</p>
              <button 
                onClick={() => fetchSupportRequests()}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                تلاش مجدد
              </button>
            </div>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">درخواست‌های پشتیبانی انسانی</h1>
          <p className="text-gray-600 mt-1">مدیریت درخواست‌های پشتیبانی مشتریان که نیاز به کمک انسانی دارند</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Headphones className="h-8 w-8 text-blue-600" />
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-500">کل درخواست‌ها</p>
                <p className="text-2xl font-semibold text-gray-900">{supportRequests.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Clock className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-500">در انتظار</p>
                <p className="text-2xl font-semibold text-gray-900">{pendingRequests.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-500">رسیدگی شده</p>
                <p className="text-2xl font-semibold text-gray-900">{handledRequests.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Star className="h-8 w-8 text-purple-600" />
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-500">رضایت مشتری</p>
                <p className="text-2xl font-semibold text-gray-900">4.8</p>
              </div>
            </div>
          </div>
        </div>

        {/* Pending Requests */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">درخواست‌های در انتظار</h2>
                <p className="text-sm text-gray-500 mt-1">
                  {pendingRequests.length} درخواست در انتظار پاسخ
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <MessageSquare className="h-5 w-5 text-yellow-600" />
                <span className="text-sm font-medium text-yellow-600">نیاز به رسیدگی</span>
              </div>
            </div>
          </div>
          
          <div className="divide-y divide-gray-200">
            {pendingRequests.map((request) => (
              <div key={request.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <User className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <span className="text-sm font-medium text-gray-900">
                          کاربر {request.userId}
                        </span>
                        {request.phone && (
                          <div className="flex items-center space-x-1 text-sm text-gray-500 mt-1">
                            <Phone className="h-4 w-4" />
                            <span>{request.phone}</span>
                          </div>
                        )}
                      </div>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 border border-yellow-200">
                        <Clock className="h-3 w-3 ml-1" />
                        در انتظار
                      </span>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-4 mb-3">
                      <p className="text-sm text-gray-700 leading-relaxed">
                        {request.message}
                      </p>
                    </div>
                    
                    <div className="flex items-center space-x-4 text-xs text-gray-400">
                      <span>درخواست شده {formatDate(request.createdAt)}</span>
                      {request.updatedAt && (
                        <span>رسیدگی شده {formatDate(request.updatedAt)}</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 mr-4">
                    <button className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors">
                      <Mail className="h-4 w-4" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded transition-colors">
                      <Phone className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleMarkHandled(request.id)}
                      disabled={loading}
                      className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <CheckCircle className="h-4 w-4 ml-1" />
                                              {loading ? 'در حال پردازش...' : 'رسیدگی شده'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
            
            {pendingRequests.length === 0 && (
              <div className="text-center py-12">
                <CheckCircle className="h-12 w-12 text-green-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">هیچ درخواست در انتظاری وجود ندارد</h3>
                <p className="text-gray-500">
                  تمام درخواست‌های پشتیبانی رسیدگی شده‌اند
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Handled Requests */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">درخواست‌های رسیدگی شده</h2>
                <p className="text-sm text-gray-500 mt-1">
                  {handledRequests.length} درخواست تکمیل شده
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="text-sm font-medium text-green-600">تکمیل شده</span>
              </div>
            </div>
          </div>
          
          <div className="divide-y divide-gray-200">
            {handledRequests.map((request) => (
              <div key={request.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                        <User className="h-5 w-5 text-green-600" />
                      </div>
                      <div>
                        <span className="text-sm font-medium text-gray-900">
                          کاربر {request.userId}
                        </span>
                        {request.phone && (
                          <div className="flex items-center space-x-1 text-sm text-gray-500 mt-1">
                            <Phone className="h-4 w-4" />
                            <span>{request.phone}</span>
                          </div>
                        )}
                      </div>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
                        <CheckCircle className="h-3 w-3 ml-1" />
                        رسیدگی شده
                      </span>
                    </div>
                    
                    <div className="bg-green-50 rounded-lg p-4 mb-3">
                      <p className="text-sm text-gray-700 leading-relaxed">
                        {request.message}
                      </p>
                    </div>
                    
                    <div className="flex items-center space-x-4 text-xs text-gray-400">
                      <span>درخواست شده {formatDate(request.createdAt)}</span>
                      {request.updatedAt && (
                        <span>رسیدگی شده {formatDate(request.updatedAt)}</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {handledRequests.length === 0 && (
              <div className="text-center py-12">
                <Headphones className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">هیچ درخواست رسیدگی شده‌ای وجود ندارد</h3>
                <p className="text-gray-500">
                  درخواست‌های پشتیبانی هنوز رسیدگی نشده‌اند
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
} 