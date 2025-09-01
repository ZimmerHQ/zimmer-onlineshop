'use client'

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { conversationsApi } from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Search, 
  ChevronLeft, 
  ChevronRight, 
  Users, 
  Phone, 
  Calendar,
  ShoppingCart,
  Loader2,
  User
} from 'lucide-react';
import { useDebounce } from '@/lib/hooks/useDebounce';

interface User {
  id: string;
  name: string;
  username: string;
  phone: string;
  visits_count: number;
  last_seen: string;
  total_orders: number;
  total_spent: number;
}

interface UsersResponse {
  users: User[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export default function UsersList() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const debouncedSearchQuery = useDebounce(searchQuery, 400);
  
  const pageSize = 20;

  // Fetch users
  const fetchUsers = async (page: number = 1, query: string = '') => {
    try {
      setLoading(true);
      setError(null);
      
      const response: UsersResponse = await conversationsApi.getUsers({
        page,
        page_size: pageSize,
        query: query.trim() || undefined,
      });
      
      setUsers(response.users);
      setTotal(response.total);
      setCurrentPage(response.page);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'خطا در بارگذاری کاربران');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  // Update URL params
  const updateUrlParams = (page: number, query: string) => {
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (page > 1) params.set('page', page.toString());
    
    const newUrl = `/conversations/users?${params.toString()}`;
    router.push(newUrl);
  };

  // Handle search
  useEffect(() => {
    setCurrentPage(1);
    updateUrlParams(1, debouncedSearchQuery);
    fetchUsers(1, debouncedSearchQuery);
  }, [debouncedSearchQuery]);

  // Handle page change
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    updateUrlParams(page, searchQuery);
    fetchUsers(page, searchQuery);
  };

  // Handle user row click
  const handleUserClick = (userId: string) => {
    router.push(`/conversations/users/${userId}`);
  };

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount) + ' تومان';
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR');
  };

  // Initial load
  useEffect(() => {
    const page = parseInt(searchParams.get('page') || '1');
    const query = searchParams.get('q') || '';
    setCurrentPage(page);
    setSearchQuery(query);
    fetchUsers(page, query);
  }, []);

  if (loading && users.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">کاربران</h1>
          <p className="text-gray-600 mt-1">مدیریت کاربران و گفتگوها</p>
        </div>
        <div className="flex items-center space-x-2 space-x-reverse">
          <Users className="h-5 w-5 text-gray-400" />
          <span className="text-sm text-gray-500">
            {total} کاربر
          </span>
        </div>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center space-x-4 space-x-reverse">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="جستجو در نام، نام کاربری یا شماره تلفن..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pr-10"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>لیست کاربران</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    شناسه
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    نام
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    نام کاربری
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    تلفن
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    آخرین بازدید
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    تعداد بازدید
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    سفارش‌ها
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    مجموع خرید
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center">
                        <Loader2 className="h-6 w-6 animate-spin text-blue-600 ml-2" />
                        <span className="text-gray-600">در حال بارگذاری...</span>
                      </div>
                    </td>
                  </tr>
                ) : users.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-4 text-center text-gray-500">
                      هیچ کاربری یافت نشد
                    </td>
                  </tr>
                ) : (
                  users.map((user) => (
                    <tr 
                      key={user.id} 
                      className="hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => handleUserClick(user.id)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        <div className="flex items-center">
                          <User className="h-4 w-4 text-gray-400 ml-2" />
                          {user.id}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {user.name || 'نامشخص'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        @{user.username}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex items-center">
                          <Phone className="h-4 w-4 text-gray-400 ml-1" />
                          {user.phone || 'نامشخص'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 text-gray-400 ml-1" />
                          {user.last_seen ? formatDate(user.last_seen) : 'نامشخص'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-center">
                        <Badge variant="secondary">
                          {user.visits_count}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-center">
                        <div className="flex items-center justify-center">
                          <ShoppingCart className="h-4 w-4 text-gray-400 ml-1" />
                          {user.total_orders}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {user.total_spent > 0 ? formatCurrency(user.total_spent) : '0 تومان'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6">
              <div className="text-sm text-gray-700">
                نمایش {((currentPage - 1) * pageSize) + 1} تا {Math.min(currentPage * pageSize, total)} از {total} کاربر
              </div>
              <div className="flex items-center space-x-2 space-x-reverse">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  <ChevronRight className="h-4 w-4" />
                  قبلی
                </Button>
                <span className="text-sm text-gray-700">
                  صفحه {currentPage} از {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  بعدی
                  <ChevronLeft className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 