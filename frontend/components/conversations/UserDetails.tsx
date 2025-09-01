'use client'

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { conversationsApi } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ArrowRight, 
  Phone, 
  MapPin, 
  Calendar, 
  Eye, 
  ShoppingCart,
  MessageCircle,
  User,
  Loader2,
  Save,
  X,
  Edit3
} from 'lucide-react';

interface UserDetails {
  id: string;
  name: string;
  username: string;
  phone: string;
  address: string;
  visits_count: number;
  last_seen: string;
  total_orders: number;
  total_spent: number;
  orders: Order[];
  messages: Message[];
}

interface Order {
  id: string;
  order_number: string;
  status: string;
  total_amount: number;
  created_at: string;
}

interface Message {
  id: string;
  content: string;
  is_from_user: boolean;
  timestamp: string;
  type: 'incoming' | 'outgoing';
}

interface UserDetailsProps {
  userId: string;
}

export default function UserDetails({ userId }: UserDetailsProps) {
  const router = useRouter();
  const [user, setUser] = useState<UserDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingPhone, setEditingPhone] = useState(false);
  const [editingAddress, setEditingAddress] = useState(false);
  const [phoneValue, setPhoneValue] = useState('');
  const [addressValue, setAddressValue] = useState('');
  const [saving, setSaving] = useState(false);
  const [messageFilter, setMessageFilter] = useState<'all' | 'incoming' | 'outgoing'>('all');
  const [messageSearch, setMessageSearch] = useState('');

  // Fetch user details
  const fetchUserDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const userData = await conversationsApi.getUserDetails(userId);
      setUser(userData);
      setPhoneValue(userData.phone || '');
      setAddressValue(userData.address || '');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'خطا در بارگذاری اطلاعات کاربر');
      console.error('Error fetching user details:', err);
    } finally {
      setLoading(false);
    }
  };

  // Save phone
  const handleSavePhone = async () => {
    if (!user) return;
    
    try {
      setSaving(true);
      await conversationsApi.updateUser(userId, { phone: phoneValue });
      setUser(prev => prev ? { ...prev, phone: phoneValue } : null);
      setEditingPhone(false);
      // Show success toast (you can implement a toast system)
    } catch (err) {
      console.error('Error updating phone:', err);
      // Show error toast
    } finally {
      setSaving(false);
    }
  };

  // Save address
  const handleSaveAddress = async () => {
    if (!user) return;
    
    try {
      setSaving(true);
      await conversationsApi.updateUser(userId, { address: addressValue });
      setUser(prev => prev ? { ...prev, address: addressValue } : null);
      setEditingAddress(false);
      // Show success toast
    } catch (err) {
      console.error('Error updating address:', err);
      // Show error toast
    } finally {
      setSaving(false);
    }
  };

  // Cancel editing
  const handleCancelPhone = () => {
    setPhoneValue(user?.phone || '');
    setEditingPhone(false);
  };

  const handleCancelAddress = () => {
    setAddressValue(user?.address || '');
    setEditingAddress(false);
  };

  // Filter and search messages
  const filteredMessages = user?.messages?.filter(message => {
    const matchesFilter = messageFilter === 'all' || 
      (messageFilter === 'incoming' && message.type === 'incoming') ||
      (messageFilter === 'outgoing' && message.type === 'outgoing');
    
    const matchesSearch = !messageSearch || 
      message.content.toLowerCase().includes(messageSearch.toLowerCase());
    
    return matchesFilter && matchesSearch;
  }) || [];

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount) + ' تومان';
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR');
  };

  // Get status badge color
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Load user details
  useEffect(() => {
    fetchUserDetails();
  }, [userId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error || !user) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error || 'کاربر یافت نشد'}</p>
      </div>
    );
  }

  return (
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
            <h1 className="text-2xl font-bold text-gray-900">جزئیات کاربر</h1>
            <p className="text-gray-600 mt-1">مشاهده و ویرایش اطلاعات کاربر</p>
          </div>
        </div>
      </div>

      {/* Profile Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 space-x-reverse">
            <User className="h-5 w-5" />
            <span>پروفایل کاربر</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">نام</label>
              <p className="text-gray-900">{user.name || 'نامشخص'}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">نام کاربری</label>
              <p className="text-gray-900">@{user.username}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">شماره تلفن</label>
              {editingPhone ? (
                <div className="flex items-center space-x-2 space-x-reverse">
                  <Input
                    value={phoneValue}
                    onChange={(e) => setPhoneValue(e.target.value)}
                    placeholder="شماره تلفن"
                  />
                  <Button
                    size="sm"
                    onClick={handleSavePhone}
                    disabled={saving}
                  >
                    {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleCancelPhone}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <Phone className="h-4 w-4 text-gray-400" />
                    <span className="text-gray-900">{user.phone || 'نامشخص'}</span>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setEditingPhone(true)}
                  >
                    <Edit3 className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">آدرس</label>
              {editingAddress ? (
                <div className="flex items-center space-x-2 space-x-reverse">
                  <Input
                    value={addressValue}
                    onChange={(e) => setAddressValue(e.target.value)}
                    placeholder="آدرس"
                  />
                  <Button
                    size="sm"
                    onClick={handleSaveAddress}
                    disabled={saving}
                  >
                    {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleCancelAddress}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <MapPin className="h-4 w-4 text-gray-400" />
                    <span className="text-gray-900">{user.address || 'نامشخص'}</span>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setEditingAddress(true)}
                  >
                    <Edit3 className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">تعداد بازدید</label>
              <Badge variant="secondary">{user.visits_count}</Badge>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">آخرین بازدید</label>
              <div className="flex items-center space-x-2 space-x-reverse">
                <Calendar className="h-4 w-4 text-gray-400" />
                <span className="text-gray-900">
                  {user.last_seen ? formatDate(user.last_seen) : 'نامشخص'}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Orders and Messages Tabs */}
      <Tabs defaultValue="orders" className="space-y-4">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="orders" className="flex items-center space-x-2 space-x-reverse">
            <ShoppingCart className="h-4 w-4" />
            <span>سفارش‌ها ({user.orders?.length || 0})</span>
          </TabsTrigger>
          <TabsTrigger value="messages" className="flex items-center space-x-2 space-x-reverse">
            <MessageCircle className="h-4 w-4" />
            <span>پیام‌ها ({filteredMessages.length})</span>
          </TabsTrigger>
        </TabsList>

        {/* Orders Tab */}
        <TabsContent value="orders">
          <Card>
            <CardHeader>
              <CardTitle>سفارش‌های کاربر</CardTitle>
            </CardHeader>
            <CardContent>
              {user.orders && user.orders.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          شماره سفارش
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          وضعیت
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          مبلغ کل
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          تاریخ ایجاد
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          عملیات
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {user.orders.map((order) => (
                        <tr key={order.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {order.order_number}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <Badge className={getStatusColor(order.status)}>
                              {order.status}
                            </Badge>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatCurrency(order.total_amount)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatDate(order.created_at)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => router.push(`/orders/${order.id}`)}
                            >
                              <Eye className="h-4 w-4 ml-1" />
                              مشاهده
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  هیچ سفارشی یافت نشد
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Messages Tab */}
        <TabsContent value="messages">
          <Card>
            <CardHeader>
              <CardTitle>تاریخچه پیام‌ها</CardTitle>
              <div className="flex items-center space-x-4 space-x-reverse mt-4">
                <div className="flex items-center space-x-2 space-x-reverse">
                  <span className="text-sm text-gray-600">فیلتر:</span>
                  <select
                    value={messageFilter}
                    onChange={(e) => setMessageFilter(e.target.value as 'all' | 'incoming' | 'outgoing')}
                    className="border border-gray-300 rounded-md px-3 py-1 text-sm"
                  >
                    <option value="all">همه</option>
                    <option value="incoming">ورودی</option>
                    <option value="outgoing">خروجی</option>
                  </select>
                </div>
                <div className="flex items-center space-x-2 space-x-reverse">
                  <span className="text-sm text-gray-600">جستجو:</span>
                  <Input
                    type="text"
                    placeholder="جستجو در پیام‌ها..."
                    value={messageSearch}
                    onChange={(e) => setMessageSearch(e.target.value)}
                    className="w-64"
                  />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {filteredMessages.length > 0 ? (
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {filteredMessages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.is_from_user ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.is_from_user
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-200 text-gray-900'
                        }`}
                      >
                        <div className="flex items-center mb-1">
                          <span className="text-xs opacity-75">
                            {message.is_from_user ? 'کاربر' : 'ربات'}
                          </span>
                        </div>
                        <p className="text-sm">{message.content}</p>
                        <p className="text-xs opacity-75 mt-1">
                          {formatDate(message.timestamp)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  هیچ پیامی یافت نشد
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 