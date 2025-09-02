import React from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import UserDetails from '@/components/conversations/UserDetails';

interface UserDetailsPageProps {
  params: {
    id: string;
  };
}

// Required for static export compatibility
export async function generateStaticParams() {
  // Return empty array since we don't know user IDs at build time
  // This makes the page buildable but not pre-rendered
  return [];
}

export default function UserDetailsPage({ params }: UserDetailsPageProps) {
  return (
    <DashboardLayout>
      <UserDetails userId={params.id} />
    </DashboardLayout>
  );
} 