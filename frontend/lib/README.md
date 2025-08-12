# Zustand Store Documentation

This document describes the comprehensive Zustand store for managing global state in the admin dashboard.

## Store Structure

The store manages the following state sections:

- **Products**: Product management with CRUD operations
- **Orders**: Order tracking and management
- **Conversations**: Chat conversations with users
- **Support Requests**: User support ticket management
- **User Session**: Admin authentication and profile management
- **UI State**: Sidebar and general UI state

## Features

- ✅ **Loading States**: Individual loading states for each section
- ✅ **Error Handling**: Comprehensive error management
- ✅ **API Integration**: Ready-to-use backend API calls
- ✅ **Persistence**: User session and UI state persistence
- ✅ **TypeScript**: Full type safety
- ✅ **DevTools**: Redux DevTools integration for debugging

## API Endpoints

The store expects the following API endpoints:

### Products
- `GET /api/products` - Fetch all products
- `POST /api/products` - Create new product
- `PUT /api/products/:id` - Update product
- `DELETE /api/products/:id` - Delete product

### Orders
- `GET /api/orders` - Fetch all orders
- `POST /api/orders` - Create new order
- `PUT /api/orders/:id` - Update order
- `DELETE /api/orders/:id` - Delete order

### Conversations
- `GET /api/messages` - Fetch all conversations
- `GET /api/messages/:userId` - Fetch chat history for specific user
- `POST /api/conversations` - Create new conversation
- `PUT /api/conversations/:id` - Update conversation
- `DELETE /api/messages/:userId` - Delete conversation

### Support Requests
- `GET /api/support-requests` - Fetch all support requests
- `POST /api/support-requests` - Create new support request
- `PUT /api/support-requests/:id` - Update support request
- `DELETE /api/support-requests/:id` - Delete support request
- `PUT /api/support-requests/:id/handle` - Mark request as handled

### Authentication
- `GET /api/auth/me` - Get current user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `PUT /api/auth/profile` - Update user profile

## Usage Examples

### Basic Usage

```typescript
import { useDashboardStore } from '@/lib/store'

// In your component
const { products, loading, error, fetchProducts } = useDashboardStore()

// Load data on mount
useEffect(() => {
  fetchProducts()
}, [fetchProducts])
```

### Products Management

```typescript
const { 
  products, 
  loading: { products: isLoading }, 
  errors: { products: error },
  fetchProducts, 
  addProduct, 
  updateProduct, 
  deleteProduct 
} = useDashboardStore()

// Add a new product
const handleAddProduct = async (productData) => {
  await addProduct({
    title: "New Product",
    description: "Product description",
    price: 100000,
    size: "M",
    image: "product-image.jpg"
  })
}

// Update a product
const handleUpdateProduct = async (id, updates) => {
  await updateProduct(id, {
    title: "Updated Title",
    price: 150000
  })
}

// Delete a product
const handleDeleteProduct = async (id) => {
  await deleteProduct(id)
}
```

### Orders Management

```typescript
const { 
  orders, 
  loading: { orders: isLoading }, 
  errors: { orders: error },
  fetchOrders, 
  addOrder, 
  updateOrder, 
  deleteOrder 
} = useDashboardStore()

// Fetch orders
useEffect(() => {
  fetchOrders()
}, [fetchOrders])

// Update order status
const handleUpdateOrderStatus = async (orderId, status) => {
  await updateOrder(orderId, { status })
}
```

### Conversations Management

```typescript
const { 
  conversations, 
  selectedConversation,
  loading: { conversations: isLoading }, 
  errors: { conversations: error },
  fetchConversations, 
  addConversation, 
  updateConversation, 
  deleteConversation,
  setSelectedConversation
} = useDashboardStore()

// Load conversations
useEffect(() => {
  fetchConversations()
}, [fetchConversations])

// Select a conversation
const handleSelectConversation = (conversation) => {
  setSelectedConversation(conversation)
}

// Delete a conversation
const handleDeleteConversation = async (id) => {
  await deleteConversation(id)
}
```

### Support Requests Management

```typescript
const { 
  supportRequests, 
  loading: { supportRequests: isLoading }, 
  errors: { supportRequests: error },
  fetchSupportRequests, 
  addSupportRequest, 
  updateSupportRequest, 
  deleteSupportRequest,
  markSupportRequestHandled
} = useDashboardStore()

// Load support requests
useEffect(() => {
  fetchSupportRequests()
}, [fetchSupportRequests])

// Mark request as handled
const handleMarkAsHandled = async (requestId) => {
  await markSupportRequestHandled(requestId)
}
```

### User Authentication

```typescript
const { 
  user, 
  loading: { user: isLoading }, 
  errors: { user: error },
  fetchUser, 
  loginUser, 
  logoutUser, 
  updateUser 
} = useDashboardStore()

// Login
const handleLogin = async (credentials) => {
  await loginUser({
    username: "admin",
    password: "password"
  })
}

// Logout
const handleLogout = async () => {
  await logoutUser()
}

// Update profile
const handleUpdateProfile = async (userData) => {
  await updateUser({
    email: "newemail@example.com",
    username: "newusername"
  })
}
```

### UI State Management

```typescript
const { 
  sidebarOpen, 
  setSidebarOpen, 
  clearErrors 
} = useDashboardStore()

// Toggle sidebar
const toggleSidebar = () => {
  setSidebarOpen(!sidebarOpen)
}

// Clear errors
const clearAllErrors = () => {
  clearErrors()
}

// Clear specific section errors
const clearProductErrors = () => {
  clearErrors('products')
}
```

## Error Handling

The store automatically handles errors for each section. You can access errors and loading states:

```typescript
const { 
  loading: { products: isLoading, orders: ordersLoading },
  errors: { products: productError, orders: orderError }
} = useDashboardStore()

// Check if any section is loading
const isAnyLoading = Object.values(loading).some(Boolean)

// Check if any section has errors
const hasAnyErrors = Object.values(errors).some(Boolean)
```

## Environment Configuration

Set your API base URL in your environment variables:

```env
NEXT_PUBLIC_API_URL=http://localhost:3001/api
```

If not set, it defaults to `http://localhost:3001/api`.

## Persistence

The store automatically persists:
- User session data
- Sidebar open/closed state

This data is stored in localStorage and restored on page reload.

## TypeScript Types

All types are exported from the store:

```typescript
import { 
  Product, 
  Order, 
  Conversation, 
  SupportRequest, 
  AdminUser,
  ApiResponse 
} from '@/lib/store'
```

## Development

For development, the store integrates with Redux DevTools. You can inspect state changes and time-travel through actions in the browser's developer tools. 