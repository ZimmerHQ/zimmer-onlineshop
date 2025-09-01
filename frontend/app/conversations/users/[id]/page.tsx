'use client'

import React from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import UserDetails from '@/components/conversations/UserDetails';

interface UserDetailsPageProps {
  params: {
    id: string;
  };
}

export default function UserDetailsPage({ params }: UserDetailsPageProps) {
  return (
    <DashboardLayout>
      <UserDetails userId={params.id} />
    </DashboardLayout>
  );
} 