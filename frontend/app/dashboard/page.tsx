'use client';

import { useState, useEffect } from 'react';

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalOrders: 0,
    totalRevenue: 0,
    activeUsers: 0
  });

  useEffect(() => {
    // Fetch dashboard stats from backend
    const fetchStats = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/health');
        if (response.ok) {
          const data = await response.json();
          // You can update stats here when you have real data
        }
      } catch (error) {
        console.log('Backend not connected yet');
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>
        
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900">Total Products</h3>
            <p className="text-3xl font-bold text-blue-600">{stats.totalProducts}</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900">Total Orders</h3>
            <p className="text-3xl font-bold text-green-600">{stats.totalOrders}</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900">Total Revenue</h3>
            <p className="text-3xl font-bold text-purple-600">${stats.totalRevenue}</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900">Active Users</h3>
            <p className="text-3xl font-bold text-orange-600">{stats.activeUsers}</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
              Add Product
            </button>
            <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
              View Orders
            </button>
            <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors">
              Analytics
            </button>
          </div>
        </div>

        {/* Status */}
        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">System Status</h2>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-green-600 font-medium">Frontend Running on Port 3000</span>
          </div>
          <div className="flex items-center space-x-2 mt-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span className="text-blue-600 font-medium">Backend API on Port 8000</span>
          </div>
        </div>
      </div>
    </div>
  );
}
