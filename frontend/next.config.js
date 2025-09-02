/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable static export for single-service deployment
  output: 'export',
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000',
  },

  // Note: headers() is not compatible with static export
  // Headers will be handled by the backend server instead
}

module.exports = nextConfig 