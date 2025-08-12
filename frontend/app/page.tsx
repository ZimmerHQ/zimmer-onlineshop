"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import DashboardLayout from "@/components/DashboardLayout";
import { 
  MessageSquare, 
  ShoppingCart, 
  Package, 
  Users, 
  TrendingUp,
  Bot,
  Clock,
  CheckCircle
} from "lucide-react";

interface DashboardStats {
  totalMessages: number;
  totalOrders: number;
  totalProducts: number;
  totalUsers: number;
  recentMessages: Array<{
    id: string;
    user: string;
    message: string;
    timestamp: string;
    status: 'read' | 'unread';
  }>;
  recentOrders: Array<{
    id: string;
    customer: string;
    amount: number;
    status: 'pending' | 'confirmed' | 'shipped' | 'delivered';
    timestamp: string;
  }>;
}

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats>({
    totalMessages: 0,
    totalOrders: 0,
    totalProducts: 0,
    totalUsers: 0,
    recentMessages: [],
    recentOrders: []
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading dashboard data
    const loadDashboardData = async () => {
      try {
        // In a real app, you would fetch this data from your API
        const mockStats: DashboardStats = {
          totalMessages: 1247,
          totalOrders: 89,
          totalProducts: 24,
          totalUsers: 156,
          recentMessages: [
            {
              id: "1",
              user: "احمد محمدی",
              message: "سلام، شلوار دارین؟",
              timestamp: "2 minutes ago",
              status: "unread"
            },
            {
              id: "2",
              user: "فاطمه احمدی",
              message: "قیمت پیراهن چقدره؟",
              timestamp: "5 minutes ago",
              status: "read"
            },
            {
              id: "3",
              user: "علی رضایی",
              message: "سفارش من کجاست؟",
              timestamp: "10 minutes ago",
              status: "read"
            }
          ],
          recentOrders: [
            {
              id: "ORD-2025-001",
              customer: "احمد محمدی",
              amount: 450000,
              status: "confirmed",
              timestamp: "1 hour ago"
            },
            {
              id: "ORD-2025-002",
              customer: "فاطمه احمدی",
              amount: 320000,
              status: "pending",
              timestamp: "2 hours ago"
            },
            {
              id: "ORD-2025-003",
              customer: "علی رضایی",
              amount: 780000,
              status: "shipped",
              timestamp: "3 hours ago"
            }
          ]
        };
        
        setStats(mockStats);
      } catch (error) {
        console.error("Error loading dashboard data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'confirmed': return 'bg-blue-100 text-blue-800';
      case 'shipped': return 'bg-purple-100 text-purple-800';
      case 'delivered': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('fa-IR').format(amount) + ' تومان';
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
      {/* Welcome Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Welcome to your Shopping Assistant Dashboard
        </h1>
        <p className="text-gray-600">
          Monitor your customer interactions, orders, and bot performance in real-time.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-white border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Messages</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalMessages.toLocaleString()}</p>
              </div>
              <MessageSquare className="h-8 w-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Orders</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalOrders}</p>
              </div>
              <ShoppingCart className="h-8 w-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Products</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalProducts}</p>
              </div>
              <Package className="h-8 w-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Users</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalUsers}</p>
              </div>
              <Users className="h-8 w-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Messages */}
        <Card className="bg-white border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MessageSquare className="h-5 w-5" />
              <span>Recent Messages</span>
            </CardTitle>
            <CardDescription>
              Latest customer interactions with your shopping assistant
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.recentMessages.map((message) => (
                <div key={message.id} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50">
                  <div className="flex-shrink-0">
                    {message.status === 'unread' ? (
                      <div className="w-2 h-2 bg-blue-500 rounded-full" />
                    ) : (
                      <div className="w-2 h-2 bg-gray-300 rounded-full" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900">{message.user}</p>
                      <p className="text-xs text-gray-500">{message.timestamp}</p>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{message.message}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Orders */}
        <Card className="bg-white border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <ShoppingCart className="h-5 w-5" />
              <span>Recent Orders</span>
            </CardTitle>
            <CardDescription>
              Latest customer orders and their status
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.recentOrders.map((order) => (
                <div key={order.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50">
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900">{order.customer}</p>
                      <p className="text-xs text-gray-500">{order.timestamp}</p>
                    </div>
                    <div className="flex items-center space-x-2 mt-1">
                      <p className="text-sm text-gray-600">{order.id}</p>
                      <Badge className={getStatusColor(order.status)}>
                        {order.status}
                      </Badge>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      {formatCurrency(order.amount)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="bg-white border-gray-200">
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common tasks and shortcuts for managing your store
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button 
              onClick={() => router.push('/webhook')}
              className="flex flex-col items-center p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors cursor-pointer"
            >
              <Bot className="h-6 w-6 text-gray-600 mb-2" />
              <span className="text-sm font-medium text-gray-900">Setup Bot</span>
            </button>
            <button 
              onClick={() => router.push('/products')}
              className="flex flex-col items-center p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors cursor-pointer"
            >
              <Package className="h-6 w-6 text-gray-600 mb-2" />
              <span className="text-sm font-medium text-gray-900">Add Product</span>
            </button>
            <button 
              onClick={() => router.push('/conversations')}
              className="flex flex-col items-center p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors cursor-pointer"
            >
              <MessageSquare className="h-6 w-6 text-gray-600 mb-2" />
              <span className="text-sm font-medium text-gray-900">View Messages</span>
            </button>
            <button 
              onClick={() => router.push('/analytics')}
              className="flex flex-col items-center p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors cursor-pointer"
            >
              <TrendingUp className="h-6 w-6 text-gray-600 mb-2" />
              <span className="text-sm font-medium text-gray-900">Analytics</span>
            </button>
          </div>
        </CardContent>
      </Card>
    </DashboardLayout>
  );
} 