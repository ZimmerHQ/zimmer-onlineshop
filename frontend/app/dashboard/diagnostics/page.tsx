'use client'

import React from 'react';
import DashboardLayout from '@/components/DashboardLayout';

export default function DiagnosticsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">تشخیص و عیب‌یابی</h1>
          <p className="text-gray-600 mt-1">ابزارهای تشخیص و عیب‌یابی سیستم</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <p className="text-gray-500">این صفحه در حال توسعه است.</p>
        </div>
      </div>
    </DashboardLayout>
  );
} 