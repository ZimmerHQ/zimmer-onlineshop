/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output for production deployment
  output: 'standalone',
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000',
  },

  // Production optimizations
  experimental: {
    outputFileTracingRoot: undefined,
  },
}

module.exports = nextConfig 