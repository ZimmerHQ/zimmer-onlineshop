"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Kpi } from "@/components/ui/kpi";
import DashboardLayout from "@/components/DashboardLayout";
import { analyticsApi } from "@/lib/api";
import { useDashboardStore, type ProductAnalytics, type ProductAnalyticsDetails } from "@/lib/store";
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  MessageSquare, 
  ShoppingCart,
  BarChart3,
  Calendar,
  Activity,
  Loader2,
  Search,
  Package,
  Eye,
  DollarSign,
  Hash,
  TrendingUp as TrendingUpIcon,
  XCircle
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
  
  // Product search state
  const [productSearchQuery, setProductSearchQuery] = useState('');
  const [selectedProduct, setSelectedProduct] = useState<ProductAnalyticsDetails | null>(null);
  const [showProductDetails, setShowProductDetails] = useState(false);
  
  // Get product analytics from store
  const { 
    productAnalytics, 
    productAnalyticsDetails, 
    productAnalyticsLoading, 
    productAnalyticsError,
    searchProductAnalytics,
    getProductAnalyticsDetails 
  } = useDashboardStore();

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

  // Product search functions
  const handleProductSearch = async () => {
    if (productSearchQuery.trim()) {
      await searchProductAnalytics(productSearchQuery.trim(), startDate, endDate);
    }
  };

  const handleProductDetails = async (productId: number) => {
    await getProductAnalyticsDetails(productId, startDate, endDate);
    setShowProductDetails(true);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fa-IR');
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
        <div className="zimmer-card p-6">
          <div className="flex items-center space-x-3 space-x-reverse">
            <BarChart3 className="h-8 w-8 text-primary-500" />
            <div>
              <h1 className="text-2xl font-bold text-text-strong">داشبورد تحلیلی</h1>
              <p className="text-text-muted">نظارت بر عملکرد کسب و کار و بینش مشتریان</p>
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
          <Kpi
            label="کل درآمد"
            value={formatCurrency(data.total_revenue)}
            icon={<TrendingUp className="h-5 w-5 text-success" />}
          />
          
          <Kpi
            label="کل سفارشات"
            value={formatNumber(data.total_orders)}
            icon={<ShoppingCart className="h-5 w-5 text-primary-500" />}
          />
          
          <Kpi
            label="کل مشتریان"
            value={formatNumber(data.total_customers)}
            icon={<Users className="h-5 w-5 text-info" />}
          />
          
          <Kpi
            label="کل پیام‌ها"
            value={formatNumber(data.total_messages)}
            icon={<MessageSquare className="h-5 w-5 text-accent-500" />}
          />
          
          <Kpi
            label="نسبت پیام به سفارش"
            value={`${data.msg_order_ratio || 0} : 1`}
            icon={<Activity className="h-5 w-5 text-warning" />}
          />
        </div>

        {/* Charts and Details */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Top Products */}
          <Card variant="glass">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 space-x-reverse">
                <Activity className="h-5 w-5 text-primary-500" />
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
                    <div key={index} className="flex items-center justify-between p-3 rounded-lg hover:bg-bg-soft/30 transition-colors">
                      <div className="flex items-center space-x-3 space-x-reverse">
                        <div className="w-8 h-8 bg-primary-500/10 rounded-full flex items-center justify-center text-sm font-bold text-primary-500">
                          {index + 1}
                        </div>
                        <div>
                          <p className="font-medium text-text-strong">{product.name}</p>
                          <p className="text-sm text-text-muted">{product.sales} فروش</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-text-strong ltr font-mono">{formatCurrency(product.revenue)}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-text-muted">
                    هیچ محصولی یافت نشد
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Top Categories */}
          <Card variant="glass">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 space-x-reverse">
                <BarChart3 className="h-5 w-5 text-accent-500" />
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
                    <div key={index} className="flex items-center justify-between p-3 rounded-lg hover:bg-bg-soft/30 transition-colors">
                      <div className="flex items-center space-x-3 space-x-reverse">
                        <div className="w-8 h-8 bg-accent-500/10 rounded-full flex items-center justify-center text-sm font-bold text-accent-500">
                          {index + 1}
                        </div>
                        <div>
                          <p className="font-medium text-text-strong">{category.name}</p>
                          <p className="text-sm text-text-muted">{category.sales} فروش</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-text-strong ltr font-mono">{formatCurrency(category.revenue)}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-text-muted">
                    هیچ دسته‌بندی یافت نشد
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card variant="glass">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 space-x-reverse">
              <Calendar className="h-5 w-5 text-info" />
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

        {/* Product Analytics Search */}
        <Card className="bg-white border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Search className="h-5 w-5" />
              <span>جستجوی محصولات</span>
            </CardTitle>
            <CardDescription>
              جستجو و تحلیل فروش محصولات بر اساس نام یا کد محصول
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Search Input */}
              <div className="flex items-center space-x-2 space-x-reverse">
                <Input
                  type="text"
                  placeholder="جستجو بر اساس نام یا کد محصول..."
                  value={productSearchQuery}
                  onChange={(e) => setProductSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleProductSearch()}
                  className="flex-1"
                />
                <Button
                  onClick={handleProductSearch}
                  disabled={!productSearchQuery.trim() || productAnalyticsLoading}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {productAnalyticsLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Search className="h-4 w-4" />
                  )}
                </Button>
              </div>

              {/* Search Results */}
              {productAnalyticsError && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                  {productAnalyticsError}
                </div>
              )}

              {productAnalytics && productAnalytics.products && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-gray-900">
                      نتایج جستجو ({productAnalytics.total_found} محصول)
                    </h3>
                    <p className="text-sm text-gray-500">
                      بازه زمانی: {formatDate(productAnalytics.date_range.start_date)} تا {formatDate(productAnalytics.date_range.end_date)}
                    </p>
                  </div>

                  {productAnalytics.products.length > 0 ? (
                    <div className="grid gap-4">
                      {productAnalytics.products.map((product: ProductAnalytics) => (
                        <div key={product.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 space-x-reverse">
                                <Package className="h-5 w-5 text-gray-400" />
                                <div>
                                  <h4 className="font-medium text-gray-900">{product.name}</h4>
                                  <div className="flex items-center space-x-4 space-x-reverse text-sm text-gray-500 mt-1">
                                    <span className="flex items-center space-x-1 space-x-reverse">
                                      <Hash className="h-4 w-4" />
                                      <span>{product.code}</span>
                                    </span>
                                    <span>{product.category_name}</span>
                                    <span>موجودی: {product.stock}</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                            
                            <div className="flex items-center space-x-6 space-x-reverse text-right">
                              <div>
                                <p className="text-sm text-gray-500">فروش کل</p>
                                <p className="font-semibold text-gray-900">{formatNumber(product.total_sold)}</p>
                              </div>
                              <div>
                                <p className="text-sm text-gray-500">درآمد کل</p>
                                <p className="font-semibold text-green-600">{formatCurrency(product.total_revenue)}</p>
                              </div>
                              <div>
                                <p className="text-sm text-gray-500">تعداد سفارش</p>
                                <p className="font-semibold text-gray-900">{formatNumber(product.order_count)}</p>
                              </div>
                              <div>
                                <p className="text-sm text-gray-500">قیمت متوسط</p>
                                <p className="font-semibold text-gray-900">{formatCurrency(product.avg_price_sold)}</p>
                              </div>
                              <Button
                                onClick={() => handleProductDetails(product.id)}
                                variant="outline"
                                size="sm"
                                className="flex items-center space-x-1 space-x-reverse"
                              >
                                <Eye className="h-4 w-4" />
                                <span>جزئیات</span>
                              </Button>
                            </div>
                          </div>
                          
                          {product.last_sale_date && (
                            <div className="mt-2 text-xs text-gray-500">
                              آخرین فروش: {formatDate(product.last_sale_date)}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <Package className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>هیچ محصولی یافت نشد</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Product Details Modal */}
        {showProductDetails && productAnalyticsDetails && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex justify-center items-center">
            <div className="bg-white p-8 rounded-lg shadow-xl max-w-4xl w-full m-4 max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-gray-900">
                  جزئیات فروش محصول: {productAnalyticsDetails.product.name}
                </h3>
                <button
                  onClick={() => setShowProductDetails(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>

              <div className="space-y-6">
                {/* Product Info */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-gray-900 mb-3">اطلاعات محصول</h4>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">نام:</span> {productAnalyticsDetails.product.name}</p>
                      <p><span className="font-medium">کد:</span> {productAnalyticsDetails.product.code}</p>
                      <p><span className="font-medium">قیمت فعلی:</span> {formatCurrency(productAnalyticsDetails.product.price)}</p>
                      <p><span className="font-medium">موجودی:</span> {productAnalyticsDetails.product.stock}</p>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-gray-900 mb-3">آمار فروش</h4>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">فروش کل:</span> {formatNumber(productAnalyticsDetails.analytics.total_sold)}</p>
                      <p><span className="font-medium">درآمد کل:</span> {formatCurrency(productAnalyticsDetails.analytics.total_revenue)}</p>
                      <p><span className="font-medium">تعداد سفارش:</span> {formatNumber(productAnalyticsDetails.analytics.order_count)}</p>
                      <p><span className="font-medium">قیمت متوسط:</span> {formatCurrency(productAnalyticsDetails.analytics.avg_sale_price)}</p>
                    </div>
                  </div>
                </div>

                {/* Price Range */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-3">محدوده قیمت فروش</h4>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-sm text-gray-500">کمترین قیمت</p>
                      <p className="font-semibold text-red-600">{formatCurrency(productAnalyticsDetails.analytics.min_sale_price)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">متوسط قیمت</p>
                      <p className="font-semibold text-blue-600">{formatCurrency(productAnalyticsDetails.analytics.avg_sale_price)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">بیشترین قیمت</p>
                      <p className="font-semibold text-green-600">{formatCurrency(productAnalyticsDetails.analytics.max_sale_price)}</p>
                    </div>
                  </div>
                </div>

                {/* Daily Sales */}
                {productAnalyticsDetails.daily_sales.length > 0 && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-gray-900 mb-3">فروش روزانه</h4>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {productAnalyticsDetails.daily_sales.map((day, index) => (
                        <div key={index} className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                          <span className="text-sm text-gray-600">{formatDate(day.date)}</span>
                          <div className="flex items-center space-x-4 space-x-reverse text-sm">
                            <span className="text-gray-600">{formatNumber(day.sold)} فروش</span>
                            <span className="font-medium text-green-600">{formatCurrency(day.revenue)}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recent Orders */}
                {productAnalyticsDetails.recent_orders.length > 0 && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-gray-900 mb-3">سفارشات اخیر</h4>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {productAnalyticsDetails.recent_orders.map((order, index) => (
                        <div key={index} className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                          <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900">سفارش #{order.order_number}</p>
                            <p className="text-xs text-gray-500">{order.customer_name} - {formatDate(order.created_at)}</p>
                          </div>
                          <div className="text-right text-sm">
                            <p className="text-gray-600">{formatNumber(order.quantity)} × {formatCurrency(order.unit_price)}</p>
                            <p className="font-medium text-green-600">{formatCurrency(order.total_price)}</p>
                          </div>
                        </div>
                      ))}
                    </div>
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