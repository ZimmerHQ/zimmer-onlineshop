'use client'

import React from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import UsersList from '@/components/conversations/UsersList';

export default function UsersPage() {
  return (
    <DashboardLayout>
      <UsersList />
    </DashboardLayout>
  );
} 