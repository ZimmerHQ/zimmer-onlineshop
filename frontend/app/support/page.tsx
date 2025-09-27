'use client'

import { useEffect } from 'react'
import DashboardLayout from '@/components/DashboardLayout'
import { useDashboardStore, type SupportRequest } from '@/lib/store'
import { formatDate } from '@/lib/utils'
import { Headphones, Phone, CheckCircle, Clock, User, AlertCircle, MessageSquare, Mail, Star } from 'lucide-react'

export default function SupportPage() {
  const { supportRequests, loading, errors, fetchSupportRequests, markSupportRequestHandled } = useDashboardStore()

  useEffect(() => {
    fetchSupportRequests()
  }, [fetchSupportRequests])

  const pendingRequests = supportRequests.filter(request => request.status === 'pending')
  const inProgressRequests = supportRequests.filter(request => request.status === 'in_progress')
  const resolvedRequests = supportRequests.filter(request => request.status === 'resolved')
  const closedRequests = supportRequests.filter(request => request.status === 'closed')

  const handleMarkHandled = (id: number) => {
    markSupportRequestHandled(id.toString())
  }

  const getStatusDisplay = (status: string) => {
    switch (status) {
      case 'pending':
        return { text: 'در انتظار', bg: 'bg-yellow-100', textColor: 'text-yellow-800', border: 'border-yellow-200' }
      case 'in_progress':
        return { text: 'در حال بررسی', bg: 'bg-blue-100', textColor: 'text-blue-800', border: 'border-blue-200' }
      case 'resolved':
        return { text: 'حل شده', bg: 'bg-green-100', textColor: 'text-green-800', border: 'border-green-200' }
      case 'closed':
        return { text: 'بسته شده', bg: 'bg-gray-100', textColor: 'text-gray-800', border: 'border-gray-200' }
      default:
        return { text: 'نامشخص', bg: 'bg-gray-100', textColor: 'text-gray-800', border: 'border-gray-200' }
    }
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
                <p className="text-sm font-medium text-gray-500">حل شده</p>
                <p className="text-2xl font-semibold text-gray-900">{resolvedRequests.length}</p>
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
                          {request.customer_name}
                        </span>
                        <div className="flex items-center space-x-1 text-sm text-gray-500 mt-1">
                          <Phone className="h-4 w-4" />
                          <span>{request.customer_phone}</span>
                        </div>
                      </div>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusDisplay(request.status).bg} ${getStatusDisplay(request.status).textColor} border ${getStatusDisplay(request.status).border}`}>
                        <Clock className="h-3 w-3 ml-1" />
                        {getStatusDisplay(request.status).text}
                      </span>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-4 mb-3">
                      <p className="text-sm text-gray-700 leading-relaxed">
                        {request.message}
                      </p>
                    </div>
                    
                    <div className="flex items-center space-x-4 text-xs text-gray-400">
                      <span>درخواست شده {formatDate(new Date(request.created_at))}</span>
                      {request.updated_at && (
                        <span>رسیدگی شده {formatDate(request.updated_at)}</span>
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
                <h2 className="text-lg font-semibold text-gray-900">درخواست‌های حل شده</h2>
                <p className="text-sm text-gray-500 mt-1">
                  {resolvedRequests.length} درخواست حل شده
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="text-sm font-medium text-green-600">تکمیل شده</span>
              </div>
            </div>
          </div>
          
          <div className="divide-y divide-gray-200">
            {resolvedRequests.map((request) => (
              <div key={request.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                        <User className="h-5 w-5 text-green-600" />
                      </div>
                      <div>
                        <span className="text-sm font-medium text-gray-900">
                          {request.customer_name}
                        </span>
                        <div className="flex items-center space-x-1 text-sm text-gray-500 mt-1">
                          <Phone className="h-4 w-4" />
                          <span>{request.customer_phone}</span>
                        </div>
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
                      <span>درخواست شده {formatDate(new Date(request.created_at))}</span>
                      {request.updated_at && (
                        <span>رسیدگی شده {formatDate(request.updated_at)}</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {resolvedRequests.length === 0 && (
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