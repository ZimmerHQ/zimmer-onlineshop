import { create } from "zustand";
import { apiBase } from "./utils";

// Product interface
export interface Product {
  id: string
  name: string
  description: string
  price: number
  sizes: string[]
  image_url: string
  thumbnail_url?: string
  stock?: number
  createdAt: Date
  updatedAt?: Date
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
  id: string
  userId: string
  phone?: string
  message: string
  status: 'pending' | 'handled'
  createdAt: Date
  updatedAt?: Date
}

// Order interface
export interface Order {
  id: number
  order_number: string
  customer_name: string
  customer_phone: string
  final_amount: number
  status: 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled'
  payment_status: 'pending' | 'paid' | 'failed' | 'refunded'
  created_at: string
  items_count: number
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
  fetchProducts: () => Promise<void>;
  addProduct: (product: Omit<Product, 'id' | 'createdAt'>) => Promise<void>;
  updateProduct: (id: string, product: Partial<Omit<Product, 'id' | 'createdAt'>>) => Promise<{ success: boolean; data?: Product; error?: string }>;
  deleteProduct: (id: string) => Promise<void>;
  setProducts: (products: Product[]) => void;
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
  
  fetchProducts: async () => {
    set({ loading: true, errors: null });
    try {
      const response = await fetch(`${apiBase}/api/products/`, {
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        const data = await response.json();
        // Ensure data is an array
        const productsArray = Array.isArray(data) ? data : [];
        set({ products: productsArray, loading: false });
      } else {
        set({ products: [], errors: 'Failed to fetch products', loading: false });
      }
    } catch (error) {
      console.error('CORS or network error in fetchProducts:', error);
      // Fallback to dummy data for demo purposes when API fails
      const dummyProducts: Product[] = [
        {
          id: '1',
          name: 'کفش ورزشی نایک',
          description: 'کفش ورزشی با کیفیت بالا برای دویدن',
          price: 250000,
          sizes: ['38', '39', '40', '41', '42'],
          image_url: 'https://placehold.co/400x400/cccccc/666666?text=تصویر+موجود+نیست',
          stock: 15,
          createdAt: new Date(),
          updatedAt: new Date()
        },
        {
          id: '2',
          name: 'کفش رسمی مردانه',
          description: 'کفش رسمی مناسب برای مراسم و محل کار',
          price: 180000,
          sizes: ['39', '40', '41', '42', '43'],
          image_url: 'https://placehold.co/400x400/cccccc/666666?text=تصویر+موجود+نیست',
          stock: 8,
          createdAt: new Date(),
          updatedAt: new Date()
        },
        {
          id: '3',
          name: 'کفش کتانی',
          description: 'کفش کتانی راحت برای پیاده‌روی روزانه',
          price: 120000,
          sizes: ['36', '37', '38', '39', '40'],
          image_url: 'https://placehold.co/400x400/cccccc/666666?text=تصویر+موجود+نیست',
          stock: 22,
          createdAt: new Date(),
          updatedAt: new Date()
        }
      ];
      set({ products: dummyProducts, loading: false, errors: 'Using demo data due to API connection issue' });
    }
  },
  
  addProduct: async (productData) => {
    set({ loading: true, errors: null });
    try {
      const response = await fetch(`${apiBase}/api/products/`, {
        method: 'POST',
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(productData)
      });
      if (response.ok) {
        const newProduct = await response.json();
        set(state => ({ 
          products: [...state.products, newProduct], 
          loading: false 
        }));
      } else {
        set({ errors: 'Failed to add product', loading: false });
      }
    } catch (error) {
      set({ errors: 'Network error', loading: false });
    }
  },
  
  updateProduct: async (id, productData) => {
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
        set(state => ({
          products: state.products.map(p => p.id === id ? updatedProduct : p),
          loading: false
        }));
        return { success: true, data: updatedProduct };
      } else {
        set({ errors: 'Failed to update product', loading: false });
        return { success: false, error: 'Failed to update product' };
      }
    } catch (error) {
      set({ errors: 'Network error', loading: false });
      return { success: false, error: 'Network error' };
    }
  },
  
  deleteProduct: async (id) => {
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
  
  fetchSupportRequests: async () => {
    try {
      const response = await fetch(`${apiBase}/api/support`, {
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        const data = await response.json();
        set({ supportRequests: data });
      } else {
        // Fallback to dummy data for demo
        const dummyRequests: SupportRequest[] = [
          {
            id: '1',
            userId: 'user1',
            phone: '09123456789',
            message: 'مشکل در سفارش',
            status: 'pending',
            createdAt: new Date(),
            updatedAt: new Date()
          }
        ];
        set({ supportRequests: dummyRequests });
      }
    } catch (error) {
      // Fallback to dummy data for demo
      const dummyRequests: SupportRequest[] = [
        {
          id: '1',
          userId: 'user1',
          phone: '09123456789',
          message: 'مشکل در سفارش',
          status: 'pending',
          createdAt: new Date(),
          updatedAt: new Date()
        }
      ];
      set({ supportRequests: dummyRequests });
    }
  },
  
  markSupportRequestHandled: async (id) => {
    try {
      const response = await fetch(`${apiBase}/api/support/${id}/handle`, {
        method: 'PUT',
        mode: 'cors'
      });
      if (response.ok) {
        set(state => ({
          supportRequests: state.supportRequests.map(r => 
            r.id === id ? { ...r, status: 'handled' } : r
          )
        }));
      }
    } catch (error) {
      console.error('Error marking support request as handled:', error);
    }
  },
  
  setSupportRequests: (requests) => set({ supportRequests: requests }),
  
  // Orders state
  orders: [],
  
  fetchOrders: async () => {
    try {
      const response = await fetch(`${apiBase}/api/orders/`, {
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        const data = await response.json();
        // Ensure data is an array
        const ordersArray = Array.isArray(data) ? data : [];
        set({ orders: ordersArray });
      } else {
        // Fallback to dummy data for demo
        const dummyOrders: Order[] = [
          {
            id: 1,
            order_number: 'ORD001',
            customer_name: 'محمد حسینی',
            customer_phone: '09123456789',
            final_amount: 150000,
            status: 'pending',
            payment_status: 'pending',
            created_at: '2023-10-27T10:00:00Z',
            items_count: 2
          }
        ];
        set({ orders: dummyOrders });
      }
    } catch (error) {
      console.error('CORS or network error in fetchOrders:', error);
      // Fallback to dummy data for demo
      const dummyOrders: Order[] = [
        {
          id: 1,
          order_number: 'ORD001',
          customer_name: 'محمد حسینی',
          customer_phone: '09123456789',
          final_amount: 150000,
          status: 'pending',
          payment_status: 'pending',
          created_at: '2023-10-27T10:00:00Z',
          items_count: 2
        }
      ];
      set({ orders: dummyOrders });
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
