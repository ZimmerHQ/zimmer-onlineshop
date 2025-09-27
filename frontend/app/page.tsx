"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { StatsCard } from "@/components/ui/stats-card";
import { SectionCard } from "@/components/ui/section-card";
import { StatusChip } from "@/components/ui/status-chip";
import DashboardLayout from "@/components/DashboardLayout";
import { useDashboardStore } from "@/lib/store";
import { formatDate } from "@/lib/utils";
import { 
  MessageSquare, 
  ShoppingCart, 
  Package, 
  Users, 
  TrendingUp,
  Bot
} from "lucide-react";


export default function DashboardPage() {
  const router = useRouter();
  const { 
    orders, 
    products, 
    analytics, 
    loading: storeLoading,
    fetchOrders, 
    fetchProducts, 
    fetchAnalytics 
  } = useDashboardStore();
  
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setIsLoading(true);
        // Fetch real data from the store
        await Promise.all([
          fetchOrders(),
          fetchProducts(),
          fetchAnalytics()
        ]);
      } catch (error) {
        console.error("Error loading dashboard data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboardData();
  }, [fetchOrders, fetchProducts, fetchAnalytics]);

  // Calculate stats from real data
  const stats = {
    totalMessages: analytics?.total_messages || 0,
    totalOrders: orders?.length || 0,
    totalProducts: products?.length || 0,
    totalUsers: analytics?.total_customers || 0,
    recentMessages: [] as Array<{
      id: string;
      user: string;
      message: string;
      timestamp: string;
      status: 'read' | 'unread';
    }>, // We'll implement this later
    recentOrders: orders?.slice(0, 5).map(order => ({
      id: order.order_number,
      customer: order.customer_name,
      amount: order.final_amount,
      status: order.status,
      timestamp: order.created_at
    })) || []
  };


  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          {/* Header skeleton */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <div className="h-6 bg-gray-200 rounded mb-2 w-32 animate-pulse" />
              <div className="h-4 bg-gray-200 rounded w-64 animate-pulse" />
            </div>
          </div>
          
          {/* KPI skeleton */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="rounded-xl border border-black/5 bg-white shadow-sm p-4 md:p-5 animate-pulse">
                <div className="h-4 bg-gray-200 rounded mb-3 w-16" />
                <div className="flex items-center justify-between mb-3">
                  <div className="h-8 w-8 bg-gray-200 rounded-lg" />
                  <div className="h-4 bg-gray-200 rounded w-12" />
                </div>
                <div className="h-8 bg-gray-200 rounded w-20" />
              </div>
            ))}
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      {/* (A) Header row */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg md:text-xl font-semibold">داشبورد</h2>
          <p className="text-sm text-muted-foreground">
            تعاملات مشتریان، سفارش‌ها و عملکرد ربات را به صورت زنده نظارت کنید.
          </p>
        </div>
        <div>
          {/* Keep empty or show today/date if it already exists */}
        </div>
      </div>

      {/* (B) KPI row (4 cards) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatsCard
          icon={<ShoppingCart className="h-5 w-5 text-primary-500" />}
          label="کل سفارش‌ها"
          value={stats.totalOrders}
          deltaLabel="+8%"
          delta={8}
        />
        
        <StatsCard
          icon={<MessageSquare className="h-5 w-5 text-primary-500" />}
          label="کل پیام‌ها"
          value={stats.totalMessages}
          deltaLabel="+12%"
          delta={12}
        />
        
        <StatsCard
          icon={<Package className="h-5 w-5 text-primary-500" />}
          label="کل محصولات"
          value={stats.totalProducts}
          deltaLabel="+5%"
          delta={5}
        />
        
        <StatsCard
          icon={<Users className="h-5 w-5 text-primary-500" />}
          label="کل مشتریان"
          value={stats.totalUsers}
          deltaLabel="+15%"
          delta={15}
        />
      </div>

      {/* (C) Two-column content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        {/* Recent Orders */}
        <SectionCard title="سفارش‌های اخیر">
          <div className="space-y-3 md:max-h-[380px] md:overflow-auto">
            {stats.recentOrders.length > 0 ? (
              stats.recentOrders.map((order) => (
                <div key={order.id} className="flex items-center justify-between py-3 border-b border-black/5 last:border-b-0">
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium">
                        <span dir="ltr" className="font-mono tabular-nums">{order.id}</span> - {order.customer}
                      </p>
                      <p className="text-xs text-muted-foreground">{formatDate(new Date(order.timestamp))}</p>
                    </div>
                    <div className="flex items-center space-x-2 space-x-reverse mt-1">
                      <span className="text-sm text-muted-foreground">
                        <span dir="ltr" className="font-mono tabular-nums">{order.amount.toLocaleString('fa-IR')}</span> <span>تومان</span>
                      </span>
                      <StatusChip status={order.status as any} />
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <ShoppingCart className="h-12 w-12 mx-auto mb-4 text-muted-foreground/30" />
                <p>هیچ سفارشی یافت نشد</p>
              </div>
            )}
          </div>
        </SectionCard>

        {/* Recent Messages */}
        <SectionCard title="پیام‌های اخیر">
          <div className="space-y-3 md:max-h-[380px] md:overflow-auto">
            {stats.recentMessages.length > 0 ? (
              stats.recentMessages.map((message) => (
                <div key={message.id} className="flex items-start space-x-3 space-x-reverse py-3 border-b border-black/5 last:border-b-0">
                  <div className="flex-shrink-0">
                    {message.status === 'unread' ? (
                      <div className="w-2 h-2 bg-primary-500 rounded-full" />
                    ) : (
                      <div className="w-2 h-2 bg-muted-foreground/50 rounded-full" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium">{message.user}</p>
                      <p className="text-xs text-muted-foreground">{message.timestamp}</p>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{message.message}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <MessageSquare className="h-12 w-12 mx-auto mb-4 text-muted-foreground/30" />
                <p>هیچ پیامی یافت نشد</p>
              </div>
            )}
          </div>
        </SectionCard>
      </div>

      {/* (D) Quick actions (bottom) */}
      <SectionCard title="دسترسی سریع">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button 
            onClick={() => router.push('/products')}
            className="flex flex-col items-center p-4 rounded-xl border border-black/5 hover:bg-gray-50 transition-transform hover:-translate-y-0.5 cursor-pointer"
          >
            <Package className="h-6 w-6 text-primary-500 mb-2" />
            <span className="text-sm font-medium">افزودن محصول</span>
          </button>
          <button 
            onClick={() => router.push('/analytics/crm')}
            className="flex flex-col items-center p-4 rounded-xl border border-black/5 hover:bg-gray-50 transition-transform hover:-translate-y-0.5 cursor-pointer"
          >
            <Users className="h-6 w-6 text-primary-500 mb-2" />
            <span className="text-sm font-medium">مدیریت مشتریان</span>
          </button>
          <button 
            onClick={() => router.push('/analytics')}
            className="flex flex-col items-center p-4 rounded-xl border border-black/5 hover:bg-gray-50 transition-transform hover:-translate-y-0.5 cursor-pointer"
          >
            <TrendingUp className="h-6 w-6 text-primary-500 mb-2" />
            <span className="text-sm font-medium">تحلیل‌ها</span>
          </button>
          <button 
            onClick={() => router.push('/webhook')}
            className="flex flex-col items-center p-4 rounded-xl border border-black/5 hover:bg-gray-50 transition-transform hover:-translate-y-0.5 cursor-pointer"
          >
            <Bot className="h-6 w-6 text-primary-500 mb-2" />
            <span className="text-sm font-medium">راه‌اندازی ربات</span>
          </button>
        </div>
      </SectionCard>
    </DashboardLayout>
  );
} 