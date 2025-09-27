import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Dynamic API base URL for production/development
export const apiBase = process.env.NODE_ENV === 'production' 
  ? (typeof window !== 'undefined' ? window.location.origin : '') 
  : "http://localhost:8000"

// CORS-friendly fetch options
export const fetchOptions = {
  mode: 'cors' as const,
  headers: {
    'Content-Type': 'application/json',
  },
}

export function formatDate(date: Date | string | null | undefined): string {
  // Handle null, undefined, or empty values
  if (!date) {
    return 'No date'
  }
  
  // Handle both Date objects and date strings
  const dateObj = typeof date === 'string' ? new Date(date) : date
  
  // Check if the date is valid
  if (!dateObj || isNaN(dateObj.getTime())) {
    return 'Invalid date'
  }
  
  return new Intl.DateTimeFormat('fa-IR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(dateObj)
}

export function formatPrice(price: number): string {
  return new Intl.NumberFormat('fa-IR', {
    style: 'currency',
    currency: 'IRR',
  }).format(price)
}
