'use client'

import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { formatDate, formatPrice, apiBase } from '@/lib/utils';
import { Users, DollarSign, ShoppingBag, Calendar, Loader2, AlertCircle, RefreshCw, User, Edit, Trash2, X, Save, Eye, ExternalLink } from 'lucide-react';
import { Kpi } from '@/components/ui/kpi';
import { StatusChip } from '@/components/ui/status-chip';
import { TableSkin, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table-skin';

type CustomerRow = {
  id: number;
  first_name: string;
  last_name: string;
  phone: string;
  address?: string;
  postal_code?: string;
  notes?: string;
  customer_code?: string;
  total_spent: number;
  orders_count: number;
  last_order_at?: string;
};

export default function AnalyticsCRMPage() {
  const [isClient, setIsClient] = useState(false);
  const [customers, setCustomers] = useState<CustomerRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [bestCustomer, setBestCustomer] = useState<CustomerRow | null>(null);
  
  // Edit and delete state
  const [editingCustomer, setEditingCustomer] = useState<CustomerRow | null>(null);
  const [editForm, setEditForm] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    address: '',
    postal_code: '',
    notes: ''
  });
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);
  
  // Customer detail modal state
  const [selectedCustomer, setSelectedCustomer] = useState<CustomerRow | null>(null);
  const [customerOrders, setCustomerOrders] = useState<any[]>([]);
  const [loadingOrders, setLoadingOrders] = useState(false);
  
  // Order detail modal state
  const [selectedOrder, setSelectedOrder] = useState<any>(null);
  const [loadingOrder, setLoadingOrder] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (isClient) {
      fetchCustomers();
    }
  }, [isClient]);

  const fetchCustomers = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiBase}/api/crm/customers`, {
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCustomers(data);
        if (data.length > 0) {
          setBestCustomer(data[0]); // First customer is the top spender
        }
      } else {
        setError('Failed to fetch customers');
      }
    } catch (err) {
      setError('Network error while fetching customers');
      console.error('Error fetching customers:', err);
    } finally {
      setLoading(false);
    }
  };

  const startEdit = (customer: CustomerRow) => {
    setEditingCustomer(customer);
    setEditForm({
      first_name: customer.first_name,
      last_name: customer.last_name,
      phone: customer.phone,
      address: customer.address || '',
      postal_code: customer.postal_code || '',
      notes: customer.notes || ''
    });
  };

  const cancelEdit = () => {
    setEditingCustomer(null);
    setEditForm({
      first_name: '',
      last_name: '',
      phone: '',
      address: '',
      postal_code: '',
      notes: ''
    });
  };

  const saveEdit = async () => {
    if (!editingCustomer) return;
    
    try {
      const response = await fetch(`${apiBase}/api/crm/customers/${editingCustomer.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editForm)
      });
      
      if (response.ok) {
        await fetchCustomers(); // Refresh the list
        setEditingCustomer(null);
        setEditForm({
          first_name: '',
          last_name: '',
          phone: '',
          address: '',
          postal_code: '',
          notes: ''
        });
      } else {
        const errorData = await response.json();
        setError(`Failed to update customer: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (err) {
      setError('Network error while updating customer');
      console.error('Error updating customer:', err);
    }
  };

  const deleteCustomer = async (customerId: number) => {
    try {
      const response = await fetch(`${apiBase}/api/crm/customers/${customerId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        await fetchCustomers(); // Refresh the list
        setDeleteConfirm(null);
        setError(null); // Clear any previous errors
      } else {
        const errorData = await response.json();
        setError(`خطا در حذف مشتری: ${errorData.detail || 'خطای نامشخص'}`);
        setDeleteConfirm(null); // Close the modal to show the error
      }
    } catch (err) {
      setError('خطا در شبکه هنگام حذف مشتری');
      setDeleteConfirm(null); // Close the modal to show the error
      console.error('Error deleting customer:', err);
    }
  };

  const handleCustomerClick = (customer: CustomerRow) => {
    setSelectedCustomer(customer);
    fetchCustomerOrders(customer.id);
  };

  const fetchCustomerOrders = async (customerId: number) => {
    setLoadingOrders(true);
    try {
      const response = await fetch(`${apiBase}/api/crm/customers/${customerId}/purchases`);
      if (response.ok) {
        const data = await response.json();
        setCustomerOrders(data.orders || []);
      } else {
        setCustomerOrders([]);
      }
    } catch (error) {
      console.error('Error fetching customer orders:', error);
      setCustomerOrders([]);
    } finally {
      setLoadingOrders(false);
    }
  };

  const handleEditOrder = async (orderId: number) => {
    setLoadingOrder(true);
    try {
      const response = await fetch(`${apiBase}/api/orders/${orderId}`);
      if (response.ok) {
        const orderData = await response.json();
        setSelectedOrder(orderData);
      } else {
        setError('خطا در بارگذاری جزئیات سفارش');
      }
    } catch (error) {
      console.error('Error fetching order details:', error);
      setError('خطا در بارگذاری جزئیات سفارش');
    } finally {
      setLoadingOrder(false);
    }
  };

  if (!isClient) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
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
            <h1 className="text-2xl font-bold text-text-strong">مدیریت مشتریان</h1>
            <p className="text-text-muted mt-1">مشاهده و مدیریت اطلاعات مشتریان</p>
          </div>
          <button
            onClick={fetchCustomers}
            disabled={loading}
            className="flex items-center px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 transition-all duration-200 zimmer-focus-ring"
          >
            <RefreshCw className={`h-4 w-4 ml-2 ${loading ? 'animate-spin' : ''}`} />
            بروزرسانی
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-danger/10 border border-danger/20 rounded-lg p-4 text-danger">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 ml-2" />
              <p>{error}</p>
            </div>
          </div>
        )}

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Kpi
            label="کل مشتریان"
            value={customers.length.toLocaleString('fa-IR')}
            icon={<Users className="h-5 w-5 text-primary-500" />}
            trend={{ value: 12, label: "+12%" }}
          />
          
          <Kpi
            label="بهترین مشتری"
            value={bestCustomer ? `${bestCustomer.first_name} ${bestCustomer.last_name}` : '—'}
            icon={<User className="h-5 w-5 text-success" />}
            trend={{ value: 0, label: "—" }}
          />
          
          <Kpi
            label="کل فروش"
            value={customers.reduce((sum, c) => sum + c.total_spent, 0).toLocaleString('fa-IR') + ' تومان'}
            icon={<DollarSign className="h-5 w-5 text-accent-500" />}
            trend={{ value: 8, label: "+8%" }}
          />
        </div>

        {/* Customers Table */}
        <div className="zimmer-card">
          <div className="p-6 border-b border-card/20">
            <h2 className="text-lg font-semibold text-text-strong">لیست مشتریان</h2>
            <p className="text-sm text-text-muted mt-1">مشاهده و مدیریت اطلاعات مشتریان</p>
          </div>
          
          <TableSkin>
            <TableHeader>
              <TableRow>
                <TableHead>نام مشتری</TableHead>
                <TableHead>کد مشتری</TableHead>
                <TableHead>تلفن</TableHead>
                <TableHead>تعداد سفارش‌ها</TableHead>
                <TableHead>مبلغ کل</TableHead>
                <TableHead>آخرین سفارش</TableHead>
                <TableHead>عملیات</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center">
                    <div className="flex items-center justify-center">
                      <Loader2 className="h-6 w-6 animate-spin text-primary-500 ml-2" />
                      <span className="text-text-muted">در حال بارگذاری مشتریان...</span>
                    </div>
                  </TableCell>
                </TableRow>
              ) : customers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-text-muted">
                    هیچ مشتری یافت نشد
                </TableCell>
              </TableRow>
                ) : (
                  customers.map((customer) => (
                <TableRow key={customer.id} className="hover:bg-bg-soft/30 cursor-pointer" onClick={() => handleCustomerClick(customer)}>
                  <TableCell className="font-medium text-text-strong">
                        {customer.first_name} {customer.last_name}
                  </TableCell>
                  <TableCell className="ltr font-mono text-text-muted">
                    {customer.customer_code || '—'}
                  </TableCell>
                  <TableCell className="ltr font-mono text-text-muted">
                    {customer.phone}
                  </TableCell>
                  <TableCell className="text-center text-text-strong">
                    {customer.orders_count}
                  </TableCell>
                  <TableCell className="ltr font-mono text-text-strong">
                    {formatPrice(customer.total_spent)}
                  </TableCell>
                  <TableCell className="text-text-muted">
                        {customer.last_order_at ? formatDate(new Date(customer.last_order_at)) : '—'}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2 space-x-reverse" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => handleCustomerClick(customer)}
                        className="text-success hover:text-success/80 p-1 rounded transition-colors zimmer-focus-ring"
                        title="مشاهده جزئیات"
                        aria-label="مشاهده جزئیات"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => startEdit(customer)}
                        className="text-primary-500 hover:text-primary-600 p-1 rounded transition-colors zimmer-focus-ring"
                        title="ویرایش مشتری"
                        aria-label="ویرایش مشتری"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => setDeleteConfirm(customer.id)}
                        className="text-danger hover:text-danger/80 p-1 rounded transition-colors zimmer-focus-ring"
                        title="حذف مشتری"
                        aria-label="حذف مشتری"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </TableCell>
                </TableRow>
                  ))
                )}
            </TableBody>
          </TableSkin>
        </div>

        {/* Edit Modal */}
        {editingCustomer && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-card rounded-xl p-6 w-full max-w-md mx-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-strong">ویرایش مشتری</h3>
                <button
                  onClick={cancelEdit}
                  className="text-text-muted hover:text-text-strong transition-colors zimmer-focus-ring"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-text-strong mb-2">نام</label>
                  <input
                    type="text"
                    value={editForm.first_name}
                    onChange={(e) => setEditForm({ ...editForm, first_name: e.target.value })}
                    className="w-full px-3 py-2 bg-bg-soft border border-card/20 rounded-lg text-text-strong focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-text-strong mb-2">نام خانوادگی</label>
                  <input
                    type="text"
                    value={editForm.last_name}
                    onChange={(e) => setEditForm({ ...editForm, last_name: e.target.value })}
                    className="w-full px-3 py-2 bg-bg-soft border border-card/20 rounded-lg text-text-strong focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-text-strong mb-2">تلفن</label>
                  <input
                    type="text"
                    value={editForm.phone}
                    onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })}
                    className="w-full px-3 py-2 bg-bg-soft border border-card/20 rounded-lg text-text-strong focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-text-strong mb-2">آدرس</label>
                  <textarea
                    value={editForm.address}
                    onChange={(e) => setEditForm({ ...editForm, address: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 bg-bg-soft border border-card/20 rounded-lg text-text-strong focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-text-strong mb-2">کد پستی</label>
                  <input
                    type="text"
                    value={editForm.postal_code}
                    onChange={(e) => setEditForm({ ...editForm, postal_code: e.target.value })}
                    className="w-full px-3 py-2 bg-bg-soft border border-card/20 rounded-lg text-text-strong focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-text-strong mb-2">یادداشت</label>
                  <textarea
                    value={editForm.notes}
                    onChange={(e) => setEditForm({ ...editForm, notes: e.target.value })}
                    rows={2}
                    className="w-full px-3 py-2 bg-bg-soft border border-card/20 rounded-lg text-text-strong focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>
              
              <div className="flex items-center justify-end space-x-3 space-x-reverse mt-6">
                <button
                  onClick={cancelEdit}
                  className="px-4 py-2 text-text-muted hover:text-text-strong transition-colors zimmer-focus-ring"
                >
                  انصراف
                </button>
                <button
                  onClick={saveEdit}
                  className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors zimmer-focus-ring"
                >
                  ذخیره
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {deleteConfirm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-card rounded-xl p-6 w-full max-w-md mx-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-text-strong">تأیید حذف</h3>
                <button
                  onClick={() => setDeleteConfirm(null)}
                  className="text-text-muted hover:text-text-strong transition-colors zimmer-focus-ring"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <p className="text-text-muted mb-6">
                آیا از حذف این مشتری اطمینان دارید؟ این عمل قابل بازگشت نیست.
              </p>
              
              <div className="flex items-center justify-end space-x-3 space-x-reverse">
                <button
                  onClick={() => setDeleteConfirm(null)}
                  className="px-4 py-2 text-text-muted hover:text-text-strong transition-colors zimmer-focus-ring"
                >
                  انصراف
                </button>
                <button
                  onClick={() => deleteCustomer(deleteConfirm)}
                  className="px-4 py-2 bg-danger text-white rounded-lg hover:bg-danger/90 transition-colors zimmer-focus-ring"
                >
                  حذف
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Customer Detail Modal */}
        {selectedCustomer && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-card rounded-xl p-6 w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-text-strong">
                  جزئیات مشتری: {selectedCustomer.first_name} {selectedCustomer.last_name}
                </h3>
                <button
                  onClick={() => setSelectedCustomer(null)} 
                  className="text-text-muted hover:text-text-strong transition-colors zimmer-focus-ring"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-text-muted mb-1">نام</label>
                    <p className="text-text-strong">{selectedCustomer.first_name}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-muted mb-1">نام خانوادگی</label>
                    <p className="text-text-strong">{selectedCustomer.last_name}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-muted mb-1">تلفن</label>
                    <p className="text-text-strong ltr font-mono">{selectedCustomer.phone}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-muted mb-1">کد مشتری</label>
                    <p className="text-text-strong ltr font-mono">{selectedCustomer.customer_code || '—'}</p>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-text-muted mb-1">آدرس</label>
                    <p className="text-text-strong">{selectedCustomer.address || '—'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-muted mb-1">کد پستی</label>
                    <p className="text-text-strong ltr font-mono">{selectedCustomer.postal_code || '—'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-muted mb-1">یادداشت</label>
                    <p className="text-text-strong">{selectedCustomer.notes || '—'}</p>
                  </div>
                </div>
              </div>
              
              <div className="border-t border-card/20 pt-6">
                <h4 className="text-md font-semibold text-text-strong mb-4">سفارش‌های مشتری</h4>
                
                {loadingOrders ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-6 w-6 animate-spin text-primary-500 ml-2" />
                    <span className="text-text-muted">در حال بارگذاری سفارش‌ها...</span>
                  </div>
                ) : customerOrders.length === 0 ? (
                  <div className="text-center py-8 text-text-muted">
                    <ShoppingBag className="h-12 w-12 mx-auto mb-4 text-text-muted/30" />
                    <p>هیچ سفارشی یافت نشد</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {customerOrders.map((order) => (
                      <div key={order.id} className="bg-bg-soft/50 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2 space-x-reverse">
                            <span className="text-sm font-medium text-text-strong">سفارش #{order.id}</span>
                            <StatusChip status={order.status} />
                          </div>
                          <div className="text-sm text-text-muted">
                            {formatDate(new Date(order.created_at))}
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                          <div>
                            <span className="text-text-muted">مبلغ کل:</span>
                            <span className="text-text-strong ltr font-mono mr-2">{formatPrice(order.final_amount)}</span>
                          </div>
                          <div>
                            <span className="text-text-muted">تعداد آیتم‌ها:</span>
                            <span className="text-text-strong mr-2">{order.items_count}</span>
                          </div>
                          <div>
                            <button
                              onClick={() => handleEditOrder(order.id)}
                              className="text-primary-500 hover:text-primary-600 transition-colors zimmer-focus-ring"
                            >
                              <ExternalLink className="h-4 w-4 inline ml-1" />
                              مشاهده جزئیات
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Order Detail Modal */}
        {selectedOrder && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-card rounded-xl p-6 w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-text-strong">
                  جزئیات سفارش #{selectedOrder.id}
                </h3>
                <button
                  onClick={() => setSelectedOrder(null)}
                  className="text-text-muted hover:text-text-strong transition-colors zimmer-focus-ring"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-text-muted mb-1">شماره سفارش</label>
                    <p className="text-text-strong ltr font-mono">{selectedOrder.order_number}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-muted mb-1">وضعیت</label>
                    <StatusChip status={selectedOrder.status} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-muted mb-1">تاریخ ایجاد</label>
                    <p className="text-text-strong">{formatDate(new Date(selectedOrder.created_at))}</p>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-text-muted mb-1">مبلغ کل</label>
                    <p className="text-text-strong ltr font-mono">{formatPrice(selectedOrder.final_amount)}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-muted mb-1">تعداد آیتم‌ها</label>
                    <p className="text-text-strong">{selectedOrder.items_count}</p>
                  </div>
                </div>
              </div>
              
              <div className="border-t border-card/20 pt-6">
                <h4 className="text-md font-semibold text-text-strong mb-4">آیتم‌های سفارش</h4>
                
                {selectedOrder.items && selectedOrder.items.length > 0 ? (
                  <div className="space-y-4">
                    {selectedOrder.items.map((item: any, index: number) => (
                      <div key={index} className="bg-bg-soft/50 rounded-lg p-4">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-text-muted">محصول:</span>
                            <span className="text-text-strong mr-2">{item.product_name}</span>
                          </div>
                          <div>
                            <span className="text-text-muted">کد محصول:</span>
                            <span className="text-text-strong ltr font-mono mr-2">{item.product_code}</span>
                          </div>
                          <div>
                            <span className="text-text-muted">تعداد:</span>
                            <span className="text-text-strong mr-2">{item.quantity}</span>
                          </div>
                          <div>
                            <span className="text-text-muted">قیمت:</span>
                            <span className="text-text-strong ltr font-mono mr-2">{formatPrice(item.unit_price)}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-text-muted">
                    <ShoppingBag className="h-12 w-12 mx-auto mb-4 text-text-muted/30" />
                    <p>هیچ آیتمی یافت نشد</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}