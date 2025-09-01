"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import DashboardLayout from "@/components/DashboardLayout";
import { analyticsApi } from "@/lib/api";
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  MessageSquare, 
  ShoppingCart,
  BarChart3,
  Calendar,
  Activity,
  Loader2
} from "lucide-react";

interface AnalyticsData {
  total_revenue: number;
  total_orders: number;
  total_customers: number;
  total_messages: number;
  msg_order_ratio: number;
  top_products: Array<{
    name: string;
    product_id: number;
    sales: number;
    revenue: number;
  }>;
  top_categories: Array<{
    name: string;
    category_id: number;
    sales: number;
    revenue: number;
  }>;
  recent_activity: Array<{
    type: string;
    title: string;
    time_ago: string;
  }>;
}

export default function AnalyticsPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  
  const [data, setData] = useState<AnalyticsData>({
    total_revenue: 0,
    total_orders: 0,
    total_customers: 0,
    total_messages: 0,
    msg_order_ratio: 0,
    top_products: [],
    top_categories: [],
    recent_activity: []
  });
  
  const [isLoading, setIsLoading] = useState(true);
  const [startDate, setStartDate] = useState(searchParams.get('start_date') || '');
  const [endDate, setEndDate] = useState(searchParams.get('end_date') || '');

  // Set default dates to last 30 days if not in URL
  useEffect(() => {
    if (!startDate || !endDate) {
      const end = new Date();
      const start = new Date();
      start.setDate(start.getDate() - 30);
      
      const startStr = start.toISOString().split('T')[0];
      const endStr = end.toISOString().split('T')[0];
      
      setStartDate(startStr);
      setEndDate(endStr);
    }
  }, []);

  const fetchAnalyticsData = async (start?: string, end?: string) => {
    try {
      setIsLoading(true);
      
      const params = new URLSearchParams();
      if (start) params.append('start_date', start);
      if (end) params.append('end_date', end);
      
      const analyticsData = await analyticsApi.getSummary({
        start_date: start,
        end_date: end
      });
      
      setData(analyticsData);
    } catch (error) {
      console.error("Error loading analytics data:", error);
              // Fallback to empty data
        setData({
          total_revenue: 0,
          total_orders: 0,
          total_customers: 0,
          total_messages: 0,
          msg_order_ratio: 0,
          top_products: [],
          top_categories: [],
          recent_activity: []
        });
    } finally {
      setIsLoading(false);
    }
  };

  // Load data when component mounts or dates change
  useEffect(() => {
    if (startDate && endDate) {
      fetchAnalyticsData(startDate, endDate);
    }
  }, [startDate, endDate]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount) + ' تومان';
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('fa-IR').format(num);
  };

  const handleApplyFilter = () => {
    // Update URL params
    const params = new URLSearchParams();
    if (startDate) params.set('start_date', startDate);
    if (endDate) params.set('end_date', endDate);
    
    router.push(`/analytics?${params.toString()}`);
    
    // Fetch new data
    fetchAnalyticsData(startDate, endDate);
  };

  const handlePresetFilter = (days: number) => {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - days);
    
    const startStr = start.toISOString().split('T')[0];
    const endStr = end.toISOString().split('T')[0];
    
    setStartDate(startStr);
    setEndDate(endStr);
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-6">
          {[...Array(6)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="p-6">
                  <div className="h-8 bg-gray-200 rounded mb-2" />
                  <div className="h-4 bg-gray-200 rounded w-1/2" />
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center space-x-3">
            <BarChart3 className="h-8 w-8 text-gray-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">داشبورد تحلیلی</h1>
              <p className="text-gray-600">نظارت بر عملکرد کسب و کار و بینش مشتریان</p>
            </div>
          </div>
        </div>

        {/* Date Range Controls */}
        <Card>
          <CardHeader>
            <CardTitle>انتخاب بازه زمانی</CardTitle>
            <CardDescription>
              انتخاب بازه زمانی برای تحلیل داده‌ها
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={(e) => e.preventDefault()}>
              <div className="flex flex-col md:flex-row items-center space-y-4 md:space-y-0 md:space-x-4 space-x-reverse">
              <div className="flex items-center space-x-2 space-x-reverse">
                <label className="text-sm font-medium text-gray-700">از تاریخ:</label>
                <Input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-40"
                />
              </div>
              <div className="flex items-center space-x-2 space-x-reverse">
                <label className="text-sm font-medium text-gray-700">تا تاریخ:</label>
                <Input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-40"
                />
              </div>
              <div className="flex items-center space-x-2 space-x-reverse">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePresetFilter(7)}
                >
                  ۷ روز
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePresetFilter(30)}
                >
                  ۳۰ روز
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePresetFilter(90)}
                >
                  ۹۰ روز
                </Button>
              </div>
              <Button
                type="button"
                onClick={handleApplyFilter}
                className="bg-blue-600 hover:bg-blue-700"
              >
                اعمال فیلتر
              </Button>
            </div>
            </form>
          </CardContent>
        </Card>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-6">
          <Card className="bg-white border-gray-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">کل درآمد</p>
                  <p className="text-2xl font-bold text-gray-900">{formatCurrency(data.total_revenue)}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white border-gray-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">کل سفارشات</p>
                  <p className="text-2xl font-bold text-gray-900">{formatNumber(data.total_orders)}</p>
                </div>
                <ShoppingCart className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white border-gray-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">کل مشتریان</p>
                  <p className="text-2xl font-bold text-gray-900">{formatNumber(data.total_customers)}</p>
                </div>
                <Users className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white border-gray-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">کل پیام‌ها</p>
                  <p className="text-2xl font-bold text-gray-900">{formatNumber(data.total_messages)}</p>
                </div>
                <MessageSquare className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white border-gray-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">نسبت پیام به سفارش</p>
                  <p className="text-2xl font-bold text-gray-900">{data.msg_order_ratio || 0} : 1</p>
                </div>
                <div className="h-8 w-8 text-gray-400 flex items-center justify-center">
                  <span className="text-xs">نسبت</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Charts and Details */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Top Products */}
          <Card className="bg-white border-gray-200">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5" />
                <span>محصولات برتر</span>
              </CardTitle>
              <CardDescription>
                بهترین محصولات بر اساس حجم فروش
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data.top_products && data.top_products.length > 0 ? (
                  data.top_products.map((product, index) => (
                    <div key={index} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-sm font-bold text-gray-600">
                          {index + 1}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{product.name}</p>
                          <p className="text-sm text-gray-500">{product.sales} فروش</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-gray-900">{formatCurrency(product.revenue)}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    هیچ محصولی یافت نشد
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Top Categories */}
          <Card className="bg-white border-gray-200">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5" />
                <span>دسته‌بندی‌های برتر</span>
              </CardTitle>
              <CardDescription>
                بهترین دسته‌بندی‌ها بر اساس عملکرد
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data.top_categories && data.top_categories.length > 0 ? (
                  data.top_categories.map((category, index) => (
                    <div key={index} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-sm font-bold text-gray-600">
                          {index + 1}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{category.name}</p>
                          <p className="text-sm text-gray-500">{category.sales} فروش</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-gray-900">{formatCurrency(category.revenue)}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    هیچ دسته‌بندی یافت نشد
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card className="bg-white border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Calendar className="h-5 w-5" />
              <span>فعالیت‌های اخیر</span>
            </CardTitle>
            <CardDescription>
              آخرین فعالیت‌های کسب و کار و رویدادها
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.recent_activity && data.recent_activity.length > 0 ? (
                data.recent_activity.map((activity, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50">
                    <div className="flex-shrink-0">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                        <p className="text-xs text-gray-500">{activity.time_ago}</p>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{activity.type}</p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  هیچ فعالیتی یافت نشد
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
} 