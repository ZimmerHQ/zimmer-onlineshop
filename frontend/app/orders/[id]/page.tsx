'use client'

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';
import { useDashboardStore } from '@/lib/store';
import { formatDate, formatPrice } from '@/lib/utils';
import { ArrowRight, Package, User, Phone, MapPin, Calendar, Loader2, AlertCircle } from 'lucide-react';

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

export default function OrderDetailsPage() {
  const router = useRouter();
  const params = useParams();
  const orderId = params.id as string;
  
  const { orders, loading, fetchOrders } = useDashboardStore();
  const [order, setOrder] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadOrder = async () => {
      try {
        setIsLoading(true);
        await fetchOrders();
        
        // Find the order by ID
        const foundOrder = orders.find(o => o.id.toString() === orderId);
        if (foundOrder) {
          setOrder(foundOrder);
        } else {
          // If not found in current orders, try to fetch from API
          const response = await fetch(`/api/orders/${orderId}`);
          if (response.ok) {
            const orderData = await response.json();
            setOrder(orderData);
          } else {
            console.error('Order not found');
          }
        }
      } catch (error) {
        console.error('Error loading order:', error);
      } finally {
        setIsLoading(false);
      }
    };

    if (orderId) {
      loadOrder();
    }
  }, [orderId, fetchOrders, orders]);

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      </DashboardLayout>
    );
  }

  if (!order) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <div className="flex items-center space-x-3 space-x-reverse">
            <button
              onClick={() => router.back()}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <ArrowRight className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">جزئیات سفارش</h1>
            </div>
          </div>
          
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-600 ml-2" />
              <p className="text-red-800">سفارش یافت نشد</p>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3 space-x-reverse">
            <button
              onClick={() => router.back()}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <ArrowRight className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">جزئیات سفارش #{order.id}</h1>
              <p className="text-gray-600 mt-1">شماره سفارش: {order.order_number}</p>
            </div>
          </div>
        </div>

        {/* Order Status */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 space-x-reverse">
              <Package className="h-6 w-6 text-blue-600" />
              <div>
                <h2 className="text-lg font-semibold text-gray-900">وضعیت سفارش</h2>
                <p className="text-sm text-gray-600">وضعیت فعلی سفارش</p>
              </div>
            </div>
            <span className={`px-3 py-1 text-sm font-medium rounded-full border ${statusColors[order.status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800 border-gray-200'}`}>
              {statusLabels[order.status as keyof typeof statusLabels] || 'نامشخص'}
            </span>
          </div>
        </div>

        {/* Order Information */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Customer Information */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 space-x-reverse mb-4">
              <User className="h-5 w-5 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900">اطلاعات مشتری</h3>
            </div>
            
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">نام مشتری</label>
                <p className="text-sm text-gray-900">{order.customer_name}</p>
              </div>
              
              {order.customer_snapshot && (
                <>
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <Phone className="h-4 w-4 text-gray-400" />
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">شماره تلفن</label>
                      <p className="text-sm text-gray-900">{order.customer_snapshot.phone || 'نامشخص'}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <MapPin className="h-4 w-4 text-gray-400" />
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">آدرس</label>
                      <p className="text-sm text-gray-900">{order.customer_snapshot.address || 'نامشخص'}</p>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">کد پستی</label>
                    <p className="text-sm text-gray-900">{order.customer_snapshot.postal_code || 'نامشخص'}</p>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Order Summary */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 space-x-reverse mb-4">
              <Package className="h-5 w-5 text-green-600" />
              <h3 className="text-lg font-semibold text-gray-900">خلاصه سفارش</h3>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm font-medium text-gray-700">تعداد آیتم‌ها:</span>
                <span className="text-sm text-gray-900">{order.items_count}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-sm font-medium text-gray-700">مبلغ کل:</span>
                <span className="text-sm font-semibold text-green-600">{formatPrice(order.final_amount)}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-sm font-medium text-gray-700">وضعیت پرداخت:</span>
                <span className="text-sm text-gray-900">
                  {order.payment_status === 'pending' ? 'در انتظار' : 
                   order.payment_status === 'paid' ? 'پرداخت شده' : 
                   order.payment_status === 'failed' ? 'ناموفق' : 'بازگشت'}
                </span>
              </div>
              
              <div className="flex items-center space-x-2 space-x-reverse">
                <Calendar className="h-4 w-4 text-gray-400" />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">تاریخ سفارش</label>
                  <p className="text-sm text-gray-900">{formatDate(new Date(order.created_at))}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Order Items */}
        {order.items && order.items.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">آیتم‌های سفارش</h3>
            <div className="space-y-4">
              {order.items.map((item: any, index: number) => (
                <div key={index} className="bg-gray-50 rounded-lg p-4 border">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{item.product_name}</h4>
                      <div className="mt-2 text-sm text-gray-600 space-y-1">
                        <p>کد محصول: {item.product_code || item.product_id}</p>
                        <p>تعداد: {item.quantity}</p>
                        {item.variant_size && <p>سایز: {item.variant_size}</p>}
                        {item.variant_color && <p>رنگ: {item.variant_color}</p>}
                      </div>
                    </div>
                    <div className="text-left">
                      <p className="text-sm font-medium text-gray-900">
                        {formatPrice(item.unit_price)} × {item.quantity}
                      </p>
                      <p className="text-sm font-semibold text-green-600">
                        = {formatPrice(item.total_price)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Admin Notes */}
        {order.admin_notes && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">یادداشت‌های ادمین</h3>
            <p className="text-sm text-gray-700 bg-gray-50 rounded-lg p-3">
              {order.admin_notes}
            </p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
