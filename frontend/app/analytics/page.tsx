"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import DashboardLayout from "@/components/DashboardLayout";
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  MessageSquare, 
  ShoppingCart,
  BarChart3,
  Calendar,
  Activity
} from "lucide-react";

interface AnalyticsData {
  totalRevenue: number;
  totalOrders: number;
  totalCustomers: number;
  totalMessages: number;
  revenueChange: number;
  ordersChange: number;
  customersChange: number;
  messagesChange: number;
  topProducts: Array<{
    name: string;
    sales: number;
    revenue: number;
  }>;
  recentActivity: Array<{
    type: string;
    description: string;
    timestamp: string;
    amount?: number;
  }>;
}

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData>({
    totalRevenue: 0,
    totalOrders: 0,
    totalCustomers: 0,
    totalMessages: 0,
    revenueChange: 0,
    ordersChange: 0,
    customersChange: 0,
    messagesChange: 0,
    topProducts: [],
    recentActivity: []
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading analytics data
    const loadAnalyticsData = async () => {
      try {
        // In a real app, you would fetch this data from your API
        const mockData: AnalyticsData = {
          totalRevenue: 12500000,
          totalOrders: 89,
          totalCustomers: 156,
          totalMessages: 1247,
          revenueChange: 12.5,
          ordersChange: 8.2,
          customersChange: 15.7,
          messagesChange: 23.1,
          topProducts: [
            { name: "شلوار جین مردانه", sales: 15, revenue: 2250000 },
            { name: "پیراهن رسمی", sales: 12, revenue: 1800000 },
            { name: "کت ورزشی", sales: 8, revenue: 1200000 },
            { name: "کفش کتانی", sales: 6, revenue: 900000 }
          ],
          recentActivity: [
            { type: "order", description: "سفارش جدید از احمد محمدی", timestamp: "2 minutes ago", amount: 450000 },
            { type: "message", description: "پیام جدید از فاطمه احمدی", timestamp: "5 minutes ago" },
            { type: "order", description: "سفارش تایید شد", timestamp: "10 minutes ago", amount: 320000 },
            { type: "customer", description: "مشتری جدید ثبت شد", timestamp: "15 minutes ago" },
            { type: "message", description: "پیام جدید از علی رضایی", timestamp: "20 minutes ago" }
          ]
        };
        
        setData(mockData);
      } catch (error) {
        console.error("Error loading analytics data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    loadAnalyticsData();
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount) + ' تومان';
  };

  const getChangeIcon = (change: number) => {
    return change >= 0 ? (
      <TrendingUp className="h-4 w-4 text-green-600" />
    ) : (
      <TrendingDown className="h-4 w-4 text-red-600" />
    );
  };

  const getChangeColor = (change: number) => {
    return change >= 0 ? "text-green-600" : "text-red-600";
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-8 bg-gray-200 rounded mb-2" />
                <div className="h-4 bg-gray-200 rounded w-1/2" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
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
            <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="text-gray-600">Monitor your business performance and customer insights</p>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-white border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Revenue</p>
                <p className="text-2xl font-bold text-gray-900">{formatCurrency(data.totalRevenue)}</p>
                <div className="flex items-center space-x-1 mt-1">
                  {getChangeIcon(data.revenueChange)}
                  <span className={`text-sm font-medium ${getChangeColor(data.revenueChange)}`}>
                    {data.revenueChange >= 0 ? '+' : ''}{data.revenueChange}%
                  </span>
                </div>
              </div>
              <TrendingUp className="h-8 w-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Orders</p>
                <p className="text-2xl font-bold text-gray-900">{data.totalOrders}</p>
                <div className="flex items-center space-x-1 mt-1">
                  {getChangeIcon(data.ordersChange)}
                  <span className={`text-sm font-medium ${getChangeColor(data.ordersChange)}`}>
                    {data.ordersChange >= 0 ? '+' : ''}{data.ordersChange}%
                  </span>
                </div>
              </div>
              <ShoppingCart className="h-8 w-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Customers</p>
                <p className="text-2xl font-bold text-gray-900">{data.totalCustomers}</p>
                <div className="flex items-center space-x-1 mt-1">
                  {getChangeIcon(data.customersChange)}
                  <span className={`text-sm font-medium ${getChangeColor(data.customersChange)}`}>
                    {data.customersChange >= 0 ? '+' : ''}{data.customersChange}%
                  </span>
                </div>
              </div>
              <Users className="h-8 w-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Messages</p>
                <p className="text-2xl font-bold text-gray-900">{data.totalMessages.toLocaleString()}</p>
                <div className="flex items-center space-x-1 mt-1">
                  {getChangeIcon(data.messagesChange)}
                  <span className={`text-sm font-medium ${getChangeColor(data.messagesChange)}`}>
                    {data.messagesChange >= 0 ? '+' : ''}{data.messagesChange}%
                  </span>
                </div>
              </div>
              <MessageSquare className="h-8 w-8 text-gray-400" />
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
              <span>Top Products</span>
            </CardTitle>
            <CardDescription>
              Best performing products by sales volume
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.topProducts.map((product, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-sm font-bold text-gray-600">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{product.name}</p>
                      <p className="text-sm text-gray-500">{product.sales} sales</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900">{formatCurrency(product.revenue)}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="bg-white border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Calendar className="h-5 w-5" />
              <span>Recent Activity</span>
            </CardTitle>
            <CardDescription>
              Latest business activities and events
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.recentActivity.map((activity, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50">
                  <div className="flex-shrink-0">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900">{activity.description}</p>
                      <p className="text-xs text-gray-500">{activity.timestamp}</p>
                    </div>
                    {activity.amount && (
                      <p className="text-sm text-gray-600 mt-1">{formatCurrency(activity.amount)}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Stats */}
      <Card className="bg-white border-gray-200">
        <CardHeader>
          <CardTitle>Performance Summary</CardTitle>
          <CardDescription>
            Key performance indicators and trends
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{formatCurrency(data.totalRevenue / data.totalOrders)}</div>
              <div className="text-sm text-gray-500">Average Order Value</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{Math.round(data.totalMessages / data.totalCustomers)}</div>
              <div className="text-sm text-gray-500">Messages per Customer</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{Math.round((data.totalOrders / data.totalCustomers) * 100)}%</div>
              <div className="text-sm text-gray-500">Conversion Rate</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{data.topProducts.length}</div>
              <div className="text-sm text-gray-500">Active Products</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
    </DashboardLayout>
  );
} 