// API functions for the application

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

// Conversations API
export const conversationsApi = {
  // Get users list with search and pagination
  async getUsers(params: { query?: string; page?: number; page_size?: number } = {}) {
    const searchParams = new URLSearchParams();
    if (params.query) searchParams.append('query', params.query);
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.page_size) searchParams.append('page_size', params.page_size.toString());
    
    const response = await fetch(`${API_BASE}/conversations/users?${searchParams.toString()}`);
    if (!response.ok) throw new Error('Failed to fetch users');
    return response.json();
  },

  // Get user details
  async getUserDetails(id: string) {
    const response = await fetch(`${API_BASE}/conversations/users/${id}`);
    if (!response.ok) throw new Error('Failed to fetch user details');
    return response.json();
  },

  // Update user
  async updateUser(id: string, payload: { phone?: string; address?: string }) {
    const response = await fetch(`${API_BASE}/conversations/users/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error('Failed to update user');
    return response.json();
  },
};

// Analytics API
export const analyticsApi = {
  // Get analytics summary with date range
  async getSummary(params: { start_date?: string; end_date?: string } = {}) {
    const searchParams = new URLSearchParams();
    if (params.start_date) searchParams.append('start_date', params.start_date);
    if (params.end_date) searchParams.append('end_date', params.end_date);
    
    const response = await fetch(`${API_BASE}/analytics/summary?${searchParams.toString()}`);
    if (!response.ok) throw new Error('Failed to fetch analytics');
    return response.json();
  },
};

// Generic API helper
export const api = {
  async get(endpoint: string, params: Record<string, string> = {}) {
    const searchParams = new URLSearchParams(params);
    const response = await fetch(`${API_BASE}${endpoint}?${searchParams.toString()}`);
    if (!response.ok) throw new Error(`API request failed: ${response.statusText}`);
    return response.json();
  },

  async post(endpoint: string, data: any) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error(`API request failed: ${response.statusText}`);
    return response.json();
  },

  async patch(endpoint: string, data: any) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error(`API request failed: ${response.statusText}`);
    return response.json();
  },

  async delete(endpoint: string) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error(`API request failed: ${response.statusText}`);
    return response.json();
  },
}; 