'use client'

import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useDashboardStore } from '@/lib/store';
import { formatDate, formatPrice } from '@/lib/utils';
import { Package, Eye, Trash2, Loader2, AlertCircle, RefreshCw } from 'lucide-react';

const statusColors = {
  draft: 'bg-gray-100 text-gray-800 border-gray-200',
  pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  approved: 'bg-blue-100 text-blue-800 border-blue-200',
  sold: 'bg-green-100 text-green-800 border-green-200',
  cancelled: 'bg-red-100 text-red-800 border-red-200',
};

const statusLabels = {
  draft: 'پیش‌نویس',
  pending: 'در انتظار تأیید',
  approved: 'تأیید شده',
  sold: 'فروخته شد',
  cancelled: 'لغو شده',
};

export default function OrdersPage() {
  const [isClient, setIsClient] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<import('@/lib/store').Order | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const { 
    orders, 
    loading: isLoading,
    errors: error,
    fetchOrders,
    updateOrder,
    deleteOrder,
    setOrders
  } = useDashboardStore();

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (isClient) {
      fetchOrders();
    }
  }, [fetchOrders, isClient]);

  const handleStatusUpdate = async (orderId: string, newStatus: string) => {
    try {
      await updateOrder(orderId, { status: newStatus as any });
    } catch (error) {
      console.error('Error updating order status:', error);
    }
  };

  const handleApproveOrder = async (orderId: string) => {
    try {
      await updateOrder(orderId, { status: 'approved' as any });
    } catch (error) {
      console.error('Error approving order:', error);
    }
  };

  const handleMarkAsSold = async (orderId: string) => {
    try {
      await updateOrder(orderId, { status: 'sold' as any });
      // Show success message for inventory update
      alert('سفارش به عنوان فروخته شده علامت‌گذاری شد و موجودی به‌روز شد');
    } catch (error) {
      console.error('Error marking order as sold:', error);
      alert('خطا در به‌روزرسانی موجودی. لطفاً دوباره تلاش کنید.');
    }
  };

  const handleCancelOrder = async (orderId: string) => {
    if (confirm('آیا مطمئن هستید که می‌خواهید این سفارش را لغو کنید؟')) {
      try {
        await updateOrder(orderId, { status: 'cancelled' as any });
      } catch (error) {
        console.error('Error cancelling order:', error);
      }
    }
  };

  const handleDeleteOrder = async (orderId: string) => {
    if (confirm('آیا مطمئن هستید که می‌خواهید این سفارش را حذف کنید؟')) {
      try {
        await deleteOrder(orderId);
      } catch (error) {
        console.error('Error deleting order:', error);
      }
    }
  };

  const handleViewDetails = (order: any) => {
    setSelectedOrder(order);
    setIsModalOpen(true);
  };

  if (!isClient) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">مدیریت سفارش‌ها</h1>
            <p className="text-gray-600 mt-1">مشاهده و مدیریت تمام سفارش‌های مشتریان</p>
          </div>
          <button
            onClick={() => fetchOrders()}
            disabled={isLoading}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ml-2 ${isLoading ? 'animate-spin' : ''}`} />
            بروزرسانی
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Package className="h-8 w-8 text-blue-600" />
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-500">کل سفارش‌ها</p>
                <p className="text-2xl font-semibold text-gray-900">{Array.isArray(orders) ? orders.length : 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <div className="h-3 w-3 bg-yellow-600 rounded-full"></div>
                </div>
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-500">در انتظار</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {Array.isArray(orders) ? orders.filter(o => o.status === 'pending').length : 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <div className="h-3 w-3 bg-blue-600 rounded-full"></div>
                </div>
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-500">تأیید شده</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {Array.isArray(orders) ? orders.filter(o => o.status === 'approved').length : 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-purple-100 rounded-lg flex items-center justify-center">
                  <div className="h-3 w-3 bg-purple-600 rounded-full"></div>
                </div>
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-500">لغو شده</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {Array.isArray(orders) ? orders.filter(o => o.status === 'cancelled').length : 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-green-100 rounded-lg flex items-center justify-center">
                  <div className="h-3 w-3 bg-green-600 rounded-full"></div>
                </div>
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-gray-500">فروخته شده</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {Array.isArray(orders) ? orders.filter(o => o.status === 'sold').length : 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-600 ml-2" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Orders Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    شماره سفارش
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    نام مشتری
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    تعداد آیتم‌ها
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    مبلغ کل
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    وضعیت
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    تاریخ
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    عملیات
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {isLoading ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center">
                        <Loader2 className="h-6 w-6 animate-spin text-blue-600 ml-2" />
                        <span className="text-gray-600">در حال بارگذاری سفارش‌ها...</span>
                      </div>
                    </td>
                  </tr>
                ) : !Array.isArray(orders) || orders.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                      هیچ سفارشی یافت نشد
                    </td>
                  </tr>
                ) : Array.isArray(orders) ? (
                  orders.map((order) => (
                    <tr key={order.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {order.order_number}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {order.customer_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-center">
                        {order.items_count}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatPrice(order.final_amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${statusColors[order.status]}`}>
                          {statusLabels[order.status]}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(new Date(order.created_at))}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2 space-x-reverse">
                          <button
                            onClick={() => handleViewDetails(order)}
                            className="text-blue-600 hover:text-blue-900"
                            title="مشاهده جزئیات"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          
                          {/* Status-specific actions */}
                          {order.status === 'draft' && (
                            <button
                              onClick={() => handleStatusUpdate(order.id.toString(), 'pending')}
                              className="text-yellow-600 hover:text-yellow-900 px-2 py-1 text-xs rounded border border-yellow-300 hover:bg-yellow-50"
                              title="تأیید سفارش"
                            >
                              تأیید
                            </button>
                          )}
                          
                          {order.status === 'pending' && (
                            <>
                              <button
                                onClick={() => handleApproveOrder(order.id.toString())}
                                className="text-blue-600 hover:text-blue-900 px-2 py-1 text-xs rounded border border-blue-300 hover:bg-blue-50"
                                title="تأیید ادمین"
                              >
                                تأیید ادمین
                              </button>
                              <button
                                onClick={() => handleCancelOrder(order.id.toString())}
                                className="text-red-600 hover:text-red-900 px-2 py-1 text-xs rounded border border-red-300 hover:bg-red-50"
                                title="لغو سفارش"
                              >
                                لغو
                              </button>
                            </>
                          )}
                          
                          {order.status === 'approved' && (
                            <>
                              <button
                                onClick={() => handleMarkAsSold(order.id.toString())}
                                className="text-green-600 hover:text-green-900 px-2 py-1 text-xs rounded border border-green-300 hover:bg-green-50"
                                title="علامت‌گذاری به عنوان فروخته شده (کاهش موجودی)"
                              >
                                فروخته شد
                              </button>
                              <button
                                onClick={() => handleCancelOrder(order.id.toString())}
                                className="text-red-600 hover:text-red-900 px-2 py-1 text-xs rounded border border-red-300 hover:bg-red-50"
                                title="لغو سفارش"
                              >
                                لغو
                              </button>
                            </>
                          )}
                          
                          {order.status === 'sold' && (
                            <button
                              onClick={() => handleCancelOrder(order.id.toString())}
                              className="text-red-600 hover:text-red-900 px-2 py-1 text-xs rounded border border-red-300 hover:bg-red-50"
                              title="لغو سفارش (بازگردانی موجودی)"
                            >
                              لغو
                            </button>
                          )}
                          
                          {order.status === 'cancelled' && (
                            <span className="text-gray-400 text-xs">لغو شده</span>
                          )}
                          
                          <button
                            onClick={() => handleDeleteOrder(order.id.toString())}
                            className="text-red-600 hover:text-red-900"
                            title="حذف سفارش"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : null}
              </tbody>
            </table>
          </div>
        </div>

        {/* Order Details Modal */}
        {isModalOpen && selectedOrder && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4">
              <div className="flex items-center justify-between p-6 border-b">
                <h2 className="text-xl font-semibold text-gray-900">جزئیات سفارش #{selectedOrder.id}</h2>
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="text-2xl">&times;</span>
                </button>
              </div>
              
              <div className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">شماره سفارش</label>
                    <p className="text-sm text-gray-900">{selectedOrder.order_number}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">نام مشتری</label>
                    <p className="text-sm text-gray-900">{selectedOrder.customer_name}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">تعداد آیتم‌ها</label>
                    <p className="text-sm text-gray-900">{selectedOrder.items_count}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">مبلغ کل</label>
                    <p className="text-sm text-gray-900">{formatPrice(selectedOrder.final_amount)}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">وضعیت</label>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full border ${statusColors[selectedOrder.status]}`}>
                      {statusLabels[selectedOrder.status]}
                    </span>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">وضعیت پرداخت</label>
                    <span className="px-2 py-1 text-xs font-medium rounded-full border bg-gray-100 text-gray-800 border-gray-200">
                      {selectedOrder.payment_status === 'pending' ? 'در انتظار' : 
                       selectedOrder.payment_status === 'paid' ? 'پرداخت شده' : 
                       selectedOrder.payment_status === 'failed' ? 'ناموفق' : 'بازگشت'}
                    </span>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">تاریخ سفارش</label>
                  <p className="text-sm text-gray-900">{formatDate(new Date(selectedOrder.created_at))}</p>
                </div>
              </div>
              
              <div className="flex items-center justify-end space-x-3 space-x-reverse p-6 border-t">
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  بستن
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
} 