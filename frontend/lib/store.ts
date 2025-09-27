import { create } from "zustand";
import { apiBase } from "./utils";
import { Product, ProductCreateRequest, ProductUpdateRequest } from "@/types/product";

// Legacy Product interface for backward compatibility
export interface LegacyProduct {
  id: string
  code: string
  name: string
  description: string
  price: number
  sizes: string[]
  image_url: string
  thumbnail_url?: string
  stock?: number
  category_id: number
  category_name: string
  tags?: string
  is_active: boolean
  createdAt: Date
  updatedAt?: Date
}

// Category interface
export interface Category {
  id: number
  name: string
  prefix: string
  created_at: string
}

// Conversation interface
export interface Conversation {
  id: string
  userId: string
  messages: any[]
  lastMessage: string
  lastMessageTime: Date
}

// SupportRequest interface
export interface SupportRequest {
  id: number
  customer_name: string
  customer_phone: string
  message: string
  status: 'pending' | 'in_progress' | 'resolved' | 'closed'
  telegram_user_id?: string
  admin_notes?: string
  created_at: string
  updated_at: string
}

// Product analytics interfaces
export interface ProductAnalytics {
  id: number;
  name: string;
  code: string;
  price: number;
  stock: number;
  category_id: number;
  category_name: string;
  total_sold: number;
  total_revenue: number;
  order_count: number;
  last_sale_date?: string;
  avg_price_sold: number;
}

export interface ProductAnalyticsSearchResponse {
  products: ProductAnalytics[];
  total_found: number;
  search_query: string;
  date_range: {
    start_date: string;
    end_date: string;
  };
}

export interface ProductAnalyticsDetails {
  product: {
    id: number;
    name: string;
    code: string;
    price: number;
    stock: number;
    category_id: number;
  };
  analytics: {
    total_sold: number;
    total_revenue: number;
    order_count: number;
    avg_sale_price: number;
    min_sale_price: number;
    max_sale_price: number;
  };
  daily_sales: Array<{
    date: string;
    sold: number;
    revenue: number;
  }>;
  recent_orders: Array<{
    order_id: number;
    order_number: string;
    customer_name: string;
    quantity: number;
    unit_price: number;
    total_price: number;
    created_at: string;
  }>;
  date_range: {
    start_date: string;
    end_date: string;
  };
}

// Order interface
export interface Order {
  id: number
  order_number: string
  customer_name: string
  customer_phone: string
  final_amount: number
  status: 'draft' | 'pending' | 'approved' | 'sold' | 'cancelled'
  payment_status: 'pending' | 'paid' | 'failed' | 'refunded'
  created_at: string
  items_count?: number
  items?: any[]
  customer_snapshot?: {
    first_name: string
    last_name: string
    phone: string
    address: string
    postal_code: string
    notes: string
  }
}

// Theme and Language types
export type Theme = 'light' | 'dark'
export type Language = 'fa' | 'en'

interface DashboardState {
  selectedTab: string;
  setSelectedTab: (tab: string) => void;
  // UI state
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  // Products state
  products: Product[];
  loading: boolean;
  errors: string | null;
  fetchProducts: (query?: string, categoryId?: number) => Promise<void>;
  addProduct: (product: ProductCreateRequest) => Promise<void>;
  updateProduct: (id: number, product: ProductUpdateRequest) => Promise<{ success: boolean; data?: Product; error?: string }>;
  deleteProduct: (id: number) => Promise<void>;
  setProducts: (products: Product[]) => void;
  // Categories state
  categories: Category[];
  categoriesLoading: boolean;
  categoriesError: string | null;
  fetchCategories: () => Promise<void>;
  addCategory: (name: string) => Promise<void>;
  deleteCategory: (id: number) => Promise<void>;
  setCategories: (categories: Category[]) => void;
  // Conversations state
  conversations: Conversation[];
  selectedConversation: Conversation | null;
  fetchConversations: () => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  setConversations: (conversations: Conversation[]) => void;
  setSelectedConversation: (conversation: Conversation | null) => void;
  // Support requests state
  supportRequests: SupportRequest[];
  fetchSupportRequests: () => Promise<void>;
  markSupportRequestHandled: (id: string) => Promise<void>;
  // Analytics state
  analytics: any;
  fetchAnalytics: () => Promise<void>;
  // Product analytics state
  productAnalytics: ProductAnalyticsSearchResponse | null;
  productAnalyticsDetails: ProductAnalyticsDetails | null;
  productAnalyticsLoading: boolean;
  productAnalyticsError: string | null;
  searchProductAnalytics: (query: string, startDate?: string, endDate?: string, limit?: number) => Promise<void>;
  getProductAnalyticsDetails: (productId: number, startDate?: string, endDate?: string) => Promise<void>;
  setSupportRequests: (requests: SupportRequest[]) => void;
  // Orders state
  orders: Order[];
  fetchOrders: () => Promise<void>;
  addOrder: (order: Omit<Order, 'id'>) => Promise<void>;
  updateOrder: (id: string, order: Partial<Omit<Order, 'id'>>) => Promise<void>;
  deleteOrder: (id: string) => Promise<void>;
  setOrders: (orders: Order[]) => void;
  // Theme and language state
  theme: Theme;
  language: Language;
  setTheme: (theme: Theme) => void;
  setLanguage: (language: Language) => void;
  toggleTheme: () => void;
  toggleLanguage: () => void;
  // User state
  user: any;
  setUser: (user: any) => void;
  loginUser: (credentials: any) => Promise<void>;
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  selectedTab: "chat",
  setSelectedTab: (tab) => set({ selectedTab: tab }),
  
  // UI state
  sidebarOpen: true,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  
  // Products state
  products: [],
  loading: false,
  errors: null,
  
  // Categories state
  categories: [],
  categoriesLoading: false,
  categoriesError: null,
  
  fetchProducts: async (query?: string, categoryId?: number) => {
    set({ loading: true, errors: null });
    try {
      const params = new URLSearchParams();
      if (query) params.append('q', query);
      if (categoryId) params.append('category_id', categoryId.toString());
      
      const url = `${apiBase}/api/products/${params.toString() ? '?' + params.toString() : ''}`;
      const response = await fetch(url, {
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        const data = await response.json();
        // Ensure data is an array and transform to match frontend interface
        const productsArray = Array.isArray(data) ? data.map((product: any) => ({
          ...product,
          id: Number(product.id), // Convert id to number
          createdAt: product.created_at || product.createdAt, // Keep as string
          updatedAt: product.updated_at || product.updatedAt, // Keep as string
        })) : [];
        set({ products: productsArray, loading: false });
      } else {
        set({ products: [], errors: 'Failed to fetch products', loading: false });
      }
    } catch (error) {
      console.error('CORS or network error in fetchProducts:', error);
      // Fallback to dummy data for demo purposes when API fails
      const dummyProducts: Product[] = [
        {
          id: 1,
          code: 'A0001',
          name: 'کفش ورزشی نایک',
          description: 'کفش ورزشی با کیفیت بالا برای دویدن',
          price: 250000,
          stock: 15,
          category_id: 1,
          image_url: 'https://placehold.co/400x400/cccccc/666666?text=تصویر+موجود+نیست',
          tags: 'ورزشی,نایک',
          labels: ['کفش', 'ورزشی'],
          attributes: { size: ['38', '39', '40', '41', '42'] },
          is_active: true,
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T00:00:00Z'
        },
        {
          id: 2,
          code: 'A0002',
          name: 'کفش رسمی مردانه',
          description: 'کفش رسمی مناسب برای مراسم و محل کار',
          price: 180000,
          stock: 8,
          category_id: 1,
          image_url: 'https://placehold.co/400x400/cccccc/666666?text=تصویر+موجود+نیست',
          tags: 'رسمی,مردانه',
          labels: ['کفش', 'رسمی'],
          attributes: { size: ['39', '40', '41', '42', '43'] },
          is_active: true,
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T00:00:00Z'
        },
        {
          id: 3,
          code: 'A0003',
          name: 'کفش کتانی',
          description: 'کفش کتانی راحت برای پیاده‌روی روزانه',
          price: 120000,
          stock: 22,
          category_id: 1,
          image_url: 'https://placehold.co/400x400/cccccc/666666?text=تصویر+موجود+نیست',
          tags: 'کتانی,پیاده‌روی',
          labels: ['کفش', 'کتانی'],
          attributes: { size: ['36', '37', '38', '39', '40'] },
          is_active: true,
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T00:00:00Z'
        }
      ];
      set({ products: dummyProducts, loading: false, errors: 'Using demo data due to API connection issue' });
    }
  },
  
  addProduct: async (productData: ProductCreateRequest) => {
    set({ loading: true, errors: null });
    try {
      // The payload is already properly typed and cleaned
      const cleanPayload = productData;

      // Validate required fields
      if (!cleanPayload.name || !cleanPayload.price || !cleanPayload.stock || !cleanPayload.category_id) {
        throw new Error('فیلدهای نام، قیمت، موجودی و دسته‌بندی الزامی هستند');
      }

      const response = await fetch(`${apiBase}/api/products`, {
        method: 'POST',
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cleanPayload)
      });

      if (response.ok) {
        const newProduct = await response.json();
        // Transform the new product to match frontend interface
        const transformedProduct = {
          ...newProduct,
          id: Number(newProduct.id),
          createdAt: newProduct.created_at || newProduct.createdAt,
          updatedAt: newProduct.updated_at || newProduct.updatedAt,
        };
        set(state => ({ 
          products: [...state.products, transformedProduct], 
          loading: false 
        }));
      } else {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        console.error('Backend error response:', errorData);
        console.error('Error response type:', typeof errorData);
        console.error('Error response details:', JSON.stringify(errorData, null, 2));
        throw new Error(errorData.detail || 'خطا در افزودن محصول');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'خطای شبکه';
      set({ errors: errorMessage, loading: false });
      throw error; // Re-throw to allow component to handle
    }
  },
  
  updateProduct: async (id: number, productData: ProductUpdateRequest) => {
    set({ loading: true, errors: null });
    try {
      const response = await fetch(`${apiBase}/api/products/${id}`, {
        method: 'PUT',
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(productData)
      });
      if (response.ok) {
        const updatedProduct = await response.json();
        // Transform the updated product to match frontend interface
        const transformedProduct = {
          ...updatedProduct,
          id: Number(updatedProduct.id),
          createdAt: updatedProduct.created_at || updatedProduct.createdAt,
          updatedAt: updatedProduct.updated_at || updatedProduct.updatedAt,
        };
        set(state => ({
          products: state.products.map(p => p.id === id ? transformedProduct : p),
          loading: false
        }));
        return { success: true, data: transformedProduct };
      } else {
        set({ errors: 'Failed to update product', loading: false });
        return { success: false, error: 'Failed to update product' };
      }
    } catch (error) {
      set({ errors: 'Network error', loading: false });
      return { success: false, error: 'Network error' };
    }
  },
  
  deleteProduct: async (id: number) => {
    set({ loading: true, errors: null });
    try {
      const response = await fetch(`${apiBase}/api/products/${id}`, {
        method: 'DELETE',
        mode: 'cors'
      });
      if (response.ok) {
        set(state => ({
          products: state.products.filter(p => p.id !== id),
          loading: false
        }));
      } else {
        set({ errors: 'Failed to delete product', loading: false });
      }
    } catch (error) {
      set({ errors: 'Network error', loading: false });
    }
  },
  
  setProducts: (products) => set({ products }),
  
  // Categories functions
  fetchCategories: async () => {
    set({ categoriesLoading: true, categoriesError: null });
    try {
      const response = await fetch(`${apiBase}/api/categories/`, {
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        const data = await response.json();
        // Ensure data is an array
        const categoriesArray = Array.isArray(data) ? data : [];
        set({ categories: categoriesArray, categoriesLoading: false });
      } else {
        console.error('Categories API error:', response.status, response.statusText);
        set({ categories: [], categoriesError: 'Failed to fetch categories', categoriesLoading: false });
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
      // Fallback to dummy categories for demo purposes
      const dummyCategories: Category[] = [
        {
          id: 1,
          name: 'کفش',
          prefix: 'A',
          created_at: new Date().toISOString()
        },
        {
          id: 2,
          name: 'لباس',
          prefix: 'B',
          created_at: new Date().toISOString()
        }
      ];
      set({ categories: dummyCategories, categoriesLoading: false, categoriesError: 'Using demo data due to API connection issue' });
    }
  },
  
  addCategory: async (name: string) => {
    set({ categoriesLoading: true, categoriesError: null });
    try {
      const response = await fetch(`${apiBase}/api/categories/`, {
        method: 'POST',
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });
      if (response.ok) {
        const newCategory = await response.json();
        set(state => ({
          categories: [...state.categories, newCategory],
          categoriesLoading: false
        }));
      } else {
        set({ categoriesError: 'Failed to add category', categoriesLoading: false });
      }
    } catch (error) {
      set({ categoriesError: 'Network error', categoriesLoading: false });
    }
  },
  
  deleteCategory: async (id: number) => {
    set({ categoriesLoading: true, categoriesError: null });
    try {
      const response = await fetch(`${apiBase}/api/categories/${id}`, {
        method: 'DELETE',
        mode: 'cors'
      });
      if (response.ok) {
        set(state => ({
          categories: state.categories.filter(cat => cat.id !== id),
          categoriesLoading: false
        }));
      } else {
        set({ categoriesError: 'Failed to delete category', categoriesLoading: false });
      }
    } catch (error) {
      set({ categoriesError: 'Network error', categoriesLoading: false });
    }
  },
  
  setCategories: (categories) => set({ categories }),
  
  // Conversations state
  conversations: [],
  selectedConversation: null,
  
  fetchConversations: async () => {
    try {
      const response = await fetch(`${apiBase}/api/conversations/`, {
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        const data = await response.json();
        // Ensure data is an array
        const conversationsArray = Array.isArray(data) ? data : [];
        set({ conversations: conversationsArray });
      } else {
        // Fallback to dummy data for demo
        const dummyConversations: Conversation[] = [
          {
            id: '1',
            userId: 'user1',
            messages: [],
            lastMessage: 'سلام، سوالی دارم',
            lastMessageTime: new Date()
          },
          {
            id: '2',
            userId: 'user2',
            messages: [],
            lastMessage: 'قیمت محصولات چقدر است؟',
            lastMessageTime: new Date(Date.now() - 1000 * 60 * 60)
          }
        ];
        set({ conversations: dummyConversations });
      }
    } catch (error) {
      console.error('CORS or network error in fetchConversations:', error);
      // Fallback to dummy data for demo
      const dummyConversations: Conversation[] = [
        {
          id: '1',
          userId: 'user1',
          messages: [],
          lastMessage: 'سلام، سوالی دارم',
          lastMessageTime: new Date()
        },
        {
          id: '2',
          userId: 'user2',
          messages: [],
          lastMessage: 'قیمت محصولات چقدر است؟',
          lastMessageTime: new Date(Date.now() - 1000 * 60 * 60)
        }
      ];
      set({ conversations: dummyConversations });
    }
  },
  
  deleteConversation: async (id) => {
    try {
      const response = await fetch(`${apiBase}/api/conversations/${id}`, {
        method: 'DELETE',
        mode: 'cors'
      });
      if (response.ok) {
        set(state => ({
          conversations: state.conversations.filter(c => c.id !== id)
        }));
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  },
  
  setConversations: (conversations) => set({ conversations }),
  setSelectedConversation: (conversation) => set({ selectedConversation: conversation }),
  
  // Support requests state
  supportRequests: [],
  
  // Analytics state
  analytics: null,
  
  // Product analytics state
  productAnalytics: null,
  productAnalyticsDetails: null,
  productAnalyticsLoading: false,
  productAnalyticsError: null,
  
  fetchSupportRequests: async () => {
    try {
      const response = await fetch(`${apiBase}/api/support/requests`, {
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        const data = await response.json();
        set({ supportRequests: data });
      } else {
        console.error('Failed to fetch support requests:', response.status);
        set({ supportRequests: [] });
      }
    } catch (error) {
      console.error('Error fetching support requests:', error);
      set({ supportRequests: [] });
    }
  },
  
  markSupportRequestHandled: async (id) => {
    try {
      const response = await fetch(`${apiBase}/api/support/requests/${id}`, {
        method: 'PATCH',
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'resolved' })
      });
      if (response.ok) {
        set(state => ({
          supportRequests: state.supportRequests.map(r => 
            r.id === id ? { ...r, status: 'resolved' } : r
          )
        }));
      }
    } catch (error) {
      console.error('Error marking support request as handled:', error);
    }
  },
  
  setSupportRequests: (requests) => set({ supportRequests: requests }),
  
  // Analytics functions
  fetchAnalytics: async () => {
    try {
      const response = await fetch(`${apiBase}/api/analytics/summary`, {
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        const data = await response.json();
        set({ analytics: data });
      } else {
        console.error('Failed to fetch analytics:', response.status);
        set({ analytics: null });
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
      set({ analytics: null });
    }
  },

  // Product analytics functions
  searchProductAnalytics: async (query: string, startDate?: string, endDate?: string, limit: number = 20) => {
    set({ productAnalyticsLoading: true, productAnalyticsError: null });
    try {
      const params = new URLSearchParams({
        q: query,
        limit: limit.toString()
      });
      
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      const response = await fetch(`${apiBase}/api/analytics/products/search?${params}`, {
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        set({ productAnalytics: data, productAnalyticsLoading: false });
      } else {
        console.error('Failed to search product analytics:', response.status);
        set({ productAnalytics: null, productAnalyticsError: 'خطا در جستجوی محصولات', productAnalyticsLoading: false });
      }
    } catch (error) {
      console.error('Error searching product analytics:', error);
      set({ productAnalytics: null, productAnalyticsError: 'خطا در اتصال به سرور', productAnalyticsLoading: false });
    }
  },

  getProductAnalyticsDetails: async (productId: number, startDate?: string, endDate?: string) => {
    set({ productAnalyticsLoading: true, productAnalyticsError: null });
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      const response = await fetch(`${apiBase}/api/analytics/products/${productId}/details?${params}`, {
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        set({ productAnalyticsDetails: data, productAnalyticsLoading: false });
      } else {
        console.error('Failed to get product analytics details:', response.status);
        set({ productAnalyticsDetails: null, productAnalyticsError: 'خطا در دریافت جزئیات محصول', productAnalyticsLoading: false });
      }
    } catch (error) {
      console.error('Error getting product analytics details:', error);
      set({ productAnalyticsDetails: null, productAnalyticsError: 'خطا در اتصال به سرور', productAnalyticsLoading: false });
    }
  },
  
  // Orders state
  orders: [],
  
    fetchOrders: async () => {
    console.log('🔍 fetchOrders: Starting to fetch orders from', `${apiBase}/api/orders/`);
    set({ loading: true, errors: null });
    try {
      const response = await fetch(`${apiBase}/api/orders/`, {
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' }
      });
      console.log('🔍 fetchOrders: Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('🔍 fetchOrders: Raw data received:', data);
        
        // Ensure data is an array and map to frontend format
        const ordersArray = Array.isArray(data) ? data : [];
        const mappedOrders = ordersArray.map(order => ({
          ...order,
          items_count: order.items ? order.items.length : 0
        }));
        console.log('🔍 fetchOrders: Mapped orders:', mappedOrders);
        set({ orders: mappedOrders, loading: false });
        console.log('✅ fetchOrders: Orders updated in store');
      } else {
        console.error('❌ fetchOrders: Failed to fetch orders:', response.status, response.statusText);
        const errorText = await response.text();
        console.error('❌ fetchOrders: Error response:', errorText);
        set({ orders: [], loading: false, errors: `Failed to fetch orders: ${response.statusText}` });
      }
    } catch (error) {
      console.error('❌ fetchOrders: CORS or network error:', error);
      set({ orders: [], loading: false, errors: 'Network error while fetching orders' });
    }
  },
  
  addOrder: async (orderData) => {
    set({ loading: true, errors: null });
    try {
      const response = await fetch(`${apiBase}/api/orders/`, {
        method: 'POST',
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData)
      });
      if (response.ok) {
        const newOrder = await response.json();
        set(state => ({ 
          orders: [...state.orders, newOrder], 
          loading: false 
        }));
      } else {
        set({ errors: 'Failed to add order', loading: false });
      }
    } catch (error) {
      set({ errors: 'Network error', loading: false });
    }
  },
  
  updateOrder: async (id, orderData) => {
    set({ loading: true, errors: null });
    try {
      // If updating status, use the new status endpoint
      if (orderData.status) {
        const response = await fetch(`${apiBase}/api/orders/${id}/status`, {
          method: 'PATCH',
          mode: 'cors',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: orderData.status })
        });
        
        if (response.ok) {
          const updatedOrder = await response.json();
          set(state => ({
            orders: state.orders.map(o => o.id === Number(id) ? updatedOrder : o),
            loading: false
          }));
          
          // Show success message for inventory update
          if (orderData.status === 'sold') {
            alert('سفارش به عنوان فروخته شده علامت‌گذاری شد و موجودی به‌روز شد');
          }
        } else {
          const errorData = await response.json().catch(() => ({ detail: response.statusText }));
          console.error('Order status update failed:', errorData);
          
          // Handle specific error cases
          if (response.status === 409) {
            // Insufficient stock
            alert(`خطا در به‌روزرسانی موجودی: ${errorData.detail}`);
          } else {
            alert(`خطا در به‌روزرسانی سفارش: ${errorData.detail || 'خطای نامشخص'}`);
          }
          
          set({ errors: errorData.detail || 'Failed to update order status', loading: false });
        }
      } else {
        // For other updates, use the general update endpoint
        const response = await fetch(`${apiBase}/api/orders/${id}`, {
          method: 'PATCH',
          mode: 'cors',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(orderData)
        });
        
        if (response.ok) {
          const updatedOrder = await response.json();
          set(state => ({
            orders: state.orders.map(o => o.id === Number(id) ? updatedOrder : o),
            loading: false
          }));
        } else {
          const errorData = await response.text();
          console.error('Order update failed:', errorData);
          set({ errors: 'Failed to update order', loading: false });
        }
      }
    } catch (error) {
      console.error('Order update error:', error);
      set({ errors: 'Network error', loading: false });
    }
  },
  
  deleteOrder: async (id) => {
    set({ loading: true, errors: null });
    try {
      const response = await fetch(`${apiBase}/api/orders/${id}`, {
        method: 'DELETE',
        mode: 'cors'
      });
      if (response.ok) {
        set(state => ({
          orders: state.orders.filter(o => o.id !== Number(id)),
          loading: false
        }));
      } else {
        set({ errors: 'Failed to delete order', loading: false });
      }
    } catch (error) {
      set({ errors: 'Network error', loading: false });
    }
  },
  
  setOrders: (orders) => set({ orders }),
  
  // Theme and language state
  theme: 'light' as Theme,
  language: 'fa' as Language,
  
  setTheme: (theme) => set({ theme }),
  setLanguage: (language) => set({ language }),
  toggleTheme: () => set(state => ({ theme: state.theme === 'light' ? 'dark' : 'light' })),
  toggleLanguage: () => set(state => ({ language: state.language === 'fa' ? 'en' : 'fa' })),
  
  // User state
  user: null,
  setUser: (user) => set({ user }),
  
  loginUser: async (credentials) => {
    try {
      const response = await fetch(`${apiBase}/api/auth/login`, {
        method: 'POST',
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      });
      if (response.ok) {
        const userData = await response.json();
        set({ user: userData });
      }
    } catch (error) {
      console.error('Login error:', error);
    }
  },
}));

// Example chat store
interface ChatState {
  messages: string[];
  addMessage: (msg: string) => void;
}

export const useStore = create<ChatState>((set) => ({
  messages: [],
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
}));
