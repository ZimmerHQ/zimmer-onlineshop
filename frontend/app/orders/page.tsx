'use client'

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';
import { useDashboardStore } from '@/lib/store';
import { formatDate, formatPrice } from '@/lib/utils';
import { StatusChip } from '@/components/ui/status-chip';
import { TableSkin, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table-skin';
import { Toolbar, ToolbarLeft, ToolbarRight } from '@/components/ui/toolbar';
import { PaginationPills } from '@/components/ui/pagination-pills';
import { Package, Eye, Trash2, Loader2, AlertCircle, RefreshCw, Search, Filter } from 'lucide-react';

// Status handling is now done by StatusChip component

export default function OrdersPage() {
  const [isClient, setIsClient] = useState(false);
  const router = useRouter();
  
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
      console.log('🔄 Orders page: Fetching orders...');
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

  const handleViewOrder = (orderId: string) => {
    router.push(`/orders/${orderId}`);
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
            <h1 className="text-2xl font-bold text-text-strong">مدیریت سفارش‌ها</h1>
            <p className="text-text-muted mt-1">مشاهده و مدیریت تمام سفارش‌های مشتریان</p>
          </div>
          <button
            onClick={() => fetchOrders()}
            disabled={isLoading}
            className="flex items-center px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 transition-all duration-200 zimmer-focus-ring"
          >
            <RefreshCw className={`h-4 w-4 ml-2 ${isLoading ? 'animate-spin' : ''}`} />
            بروزرسانی
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="zimmer-card p-6 zimmer-hover-lift">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Package className="h-8 w-8 text-primary-500" />
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-text-muted">کل سفارش‌ها</p>
                <p className="text-2xl font-semibold text-text-strong">{Array.isArray(orders) ? orders.length : 0}</p>
              </div>
            </div>
          </div>

          <div className="zimmer-card p-6 zimmer-hover-lift">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-warning/10 rounded-lg flex items-center justify-center">
                  <div className="h-3 w-3 bg-warning rounded-full"></div>
                </div>
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-text-muted">در انتظار</p>
                <p className="text-2xl font-semibold text-text-strong">
                  {Array.isArray(orders) ? orders.filter(o => o.status === 'pending').length : 0}
                </p>
              </div>
            </div>
          </div>

          <div className="zimmer-card p-6 zimmer-hover-lift">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-primary-500/10 rounded-lg flex items-center justify-center">
                  <div className="h-3 w-3 bg-primary-500 rounded-full"></div>
                </div>
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-text-muted">تأیید شده</p>
                <p className="text-2xl font-semibold text-text-strong">
                  {Array.isArray(orders) ? orders.filter(o => o.status === 'approved').length : 0}
                </p>
              </div>
            </div>
          </div>

          <div className="zimmer-card p-6 zimmer-hover-lift">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-danger/10 rounded-lg flex items-center justify-center">
                  <div className="h-3 w-3 bg-danger rounded-full"></div>
                </div>
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-text-muted">لغو شده</p>
                <p className="text-2xl font-semibold text-text-strong">
                  {Array.isArray(orders) ? orders.filter(o => o.status === 'cancelled').length : 0}
                </p>
              </div>
            </div>
          </div>

          <div className="zimmer-card p-6 zimmer-hover-lift">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-success/10 rounded-lg flex items-center justify-center">
                  <div className="h-3 w-3 bg-success rounded-full"></div>
                </div>
              </div>
              <div className="mr-4">
                <p className="text-sm font-medium text-text-muted">فروخته شده</p>
                <p className="text-2xl font-semibold text-text-strong">
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
        <TableSkin>
          <TableHeader>
            <TableRow>
              <TableHead>شماره سفارش</TableHead>
              <TableHead>نام مشتری</TableHead>
              <TableHead>اطلاعات مشتری</TableHead>
              <TableHead>تعداد آیتم‌ها</TableHead>
              <TableHead>مبلغ کل</TableHead>
              <TableHead>وضعیت</TableHead>
              <TableHead>تاریخ</TableHead>
              <TableHead>عملیات</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center">
                  <div className="flex items-center justify-center">
                    <Loader2 className="h-6 w-6 animate-spin text-primary-500 ml-2" />
                    <span className="text-text-muted">در حال بارگذاری سفارش‌ها...</span>
                  </div>
                </TableCell>
              </TableRow>
            ) : !Array.isArray(orders) || orders.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center text-text-muted">
                  هیچ سفارشی یافت نشد
                </TableCell>
              </TableRow>
            ) : Array.isArray(orders) ? (
              orders.map((order) => (
                <TableRow key={order.id}>
                  <TableCell className="font-medium">
                    <span className="ltr font-mono">{order.order_number}</span>
                  </TableCell>
                  <TableCell>{order.customer_name}</TableCell>
                  <TableCell>
                    {order.customer_snapshot ? (
                      <div className="text-xs">
                        <div className="text-success">✓ اطلاعات کامل</div>
                        <div className="text-text-muted ltr font-mono">{order.customer_snapshot.phone || 'تلفن نامشخص'}</div>
                      </div>
                    ) : (
                      <div className="text-xs text-text-muted">اطلاعات ناقص</div>
                    )}
                  </TableCell>
                  <TableCell className="text-center">{order.items_count}</TableCell>
                  <TableCell className="ltr font-mono">{formatPrice(order.final_amount)}</TableCell>
                  <TableCell>
                    <StatusChip status={order.status as any} />
                  </TableCell>
                  <TableCell className="text-text-muted">
                    {formatDate(new Date(order.created_at))}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2 space-x-reverse">
                      <button
                        onClick={() => handleViewOrder(order.id.toString())}
                        className="text-primary-500 hover:text-primary-600 transition-colors zimmer-focus-ring"
                        title="مشاهده جزئیات"
                        aria-label="مشاهده جزئیات"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                          
                      {/* Status-specific actions */}
                      {order.status === 'draft' && (
                        <>
                          <button
                            onClick={() => handleStatusUpdate(order.id.toString(), 'pending')}
                            className="text-warning hover:text-warning/80 px-2 py-1 text-xs rounded border border-warning/20 hover:bg-warning/10 transition-colors zimmer-focus-ring"
                            title="تأیید سفارش"
                            aria-label="تأیید سفارش"
                          >
                            تأیید
                          </button>
                          <button
                            onClick={() => handleCancelOrder(order.id.toString())}
                            className="text-danger hover:text-danger/80 px-2 py-1 text-xs rounded border border-danger/20 hover:bg-danger/10 transition-colors zimmer-focus-ring"
                            title="لغو سفارش"
                            aria-label="لغو سفارش"
                          >
                            لغو
                          </button>
                        </>
                      )}
                          
                      {order.status === 'pending' && (
                        <>
                          <button
                            onClick={() => handleApproveOrder(order.id.toString())}
                            className="text-primary-500 hover:text-primary-600 px-2 py-1 text-xs rounded border border-primary-500/20 hover:bg-primary-500/10 transition-colors zimmer-focus-ring"
                            title="تأیید ادمین"
                            aria-label="تأیید ادمین"
                          >
                            تأیید ادمین
                          </button>
                          <button
                            onClick={() => handleCancelOrder(order.id.toString())}
                            className="text-danger hover:text-danger/80 px-2 py-1 text-xs rounded border border-danger/20 hover:bg-danger/10 transition-colors zimmer-focus-ring"
                            title="لغو سفارش"
                            aria-label="لغو سفارش"
                          >
                            لغو
                          </button>
                        </>
                      )}
                      
                      {order.status === 'approved' && (
                        <>
                          <button
                            onClick={() => handleMarkAsSold(order.id.toString())}
                            className="text-success hover:text-success/80 px-2 py-1 text-xs rounded border border-success/20 hover:bg-success/10 transition-colors zimmer-focus-ring"
                            title="علامت‌گذاری به عنوان فروخته شده (کاهش موجودی)"
                            aria-label="علامت‌گذاری به عنوان فروخته شده"
                          >
                            فروخته شد
                          </button>
                          <button
                            onClick={() => handleCancelOrder(order.id.toString())}
                            className="text-danger hover:text-danger/80 px-2 py-1 text-xs rounded border border-danger/20 hover:bg-danger/10 transition-colors zimmer-focus-ring"
                            title="لغو سفارش"
                            aria-label="لغو سفارش"
                          >
                            لغو
                          </button>
                        </>
                      )}
                      
                      {order.status === 'sold' && (
                        <button
                          onClick={() => handleCancelOrder(order.id.toString())}
                          className="text-danger hover:text-danger/80 px-2 py-1 text-xs rounded border border-danger/20 hover:bg-danger/10 transition-colors zimmer-focus-ring"
                          title="لغو سفارش (بازگردانی موجودی)"
                          aria-label="لغو سفارش"
                        >
                          لغو
                        </button>
                      )}
                      
                      {order.status === 'cancelled' && (
                        <span className="text-text-muted text-xs">لغو شده</span>
                      )}
                      
                      <button
                        onClick={() => handleDeleteOrder(order.id.toString())}
                        className="text-danger hover:text-danger/80 transition-colors zimmer-focus-ring"
                        title="حذف سفارش"
                        aria-label="حذف سفارش"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            ) : null}
          </TableBody>
        </TableSkin>

      </div>
    </DashboardLayout>
  );
} 