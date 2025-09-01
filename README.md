# 🏪 Zimmer Shop Admin System

A comprehensive e-commerce admin system built with FastAPI (backend) and Next.js (frontend), featuring product management, category management, chatbot integration, and more.

## ✨ **NEW FEATURES (Latest Update)**

### 🎯 **1. Enhanced Category Management**
- **Edit Categories**: Rename categories and change prefixes with safety guards
- **Prefix Validation**: 1-2 uppercase letters [A-Z]{1,2} with uniqueness checks
- **Historical Integrity**: Changing prefix does NOT retroactively rewrite existing product codes
- **Add Products from Categories**: Each category row has an "افزودن محصول" button
- **Category Preselection**: Products page automatically preselects category from URL parameters

### 🤖 **2. Chatbot Integration with Live Data**
- **Real-time Product Search**: Chatbot can search live products from backend
- **Smart Query Detection**: Automatically detects product-related questions
- **Product Display**: Shows product images, codes, prices, and stock in chat
- **Categories Integration**: Chatbot can provide category information
- **Persian Language Support**: Full RTL and Persian language support

### 🖼️ **3. Enhanced Product Images**
- **Dual Image Support**: `image_url` (main) + `thumbnail_url` (list view)
- **Thumbnail Priority**: List views prefer `thumbnail_url` over `image_url`
- **Fallback Handling**: Graceful fallback to placeholder when images missing
- **CSV Import Support**: Accepts `thumbnail_url` column in bulk imports
- **Visual Polish**: 56-80px square thumbnails with proper styling

### 🔍 **4. Improved Search & Navigation**
- **Debounced Search**: 300ms debounce for better performance
- **Category-First Workflow**: Add products directly from category pages
- **URL Integration**: Category preselection via URL parameters
- **Enhanced Filters**: Better search across name, code, and category

## 🚀 **Quick Start**

### Local Development

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 🚀 **Production Deployment**

For production deployment on Render, see [DEPLOYMENT.md](./DEPLOYMENT.md) for complete instructions.

**Quick Deploy:**
1. Push code to GitHub
2. Connect to Render Blueprint
3. Set environment variables
4. Deploy automatically

**Services:**
- Backend API (FastAPI + PostgreSQL)
- Frontend (Next.js)
- Database (PostgreSQL)

## 🧪 **Local E2E Testing (No Webhook Required)**

### Prerequisites
- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:3000`
- Python dependencies installed (`pip install -r requirements.txt`)

### Running Tests

#### 1. Start Backend
```bash
cd backend
make dev
# or manually: python main.py
```

#### 2. Start Frontend (in new terminal)
```bash
cd frontend
npm run dev
```

#### 3. Run Full E2E Test Suite
```bash
cd backend
make test:local
```

#### 4. Simulate Telegram Webhook Locally
```bash
cd backend
make tg:simulate
```

### Test Coverage
The E2E test suite covers:
- ✅ Health endpoint verification
- ✅ Category and product creation
- ✅ Chat flow (Q&A → order request → confirmation)
- ✅ Order approval and sale workflow
- ✅ Stock decrement verification
- ✅ Analytics data validation (`total_messages`, `msg_order_ratio`)

### What Gets Tested
1. **Health Checks**: `/api/health` and `/api/health/details`
2. **Data Setup**: Ensures test category and product exist
3. **Chat Flow**: Simulates user conversation and order creation
4. **Order Management**: Approves and sells the created order
5. **Stock Management**: Verifies product stock decreases by 1
6. **Analytics**: Checks today's analytics data for required fields

### Test Results
- **PASS/FAIL Table**: Clear indication of which tests passed/failed
- **Success Rate**: Percentage of successful tests
- **Detailed Logs**: Full request/response details for debugging
- **Exit Codes**: `0` for success, `1` for any failure

### Notes
- **Local Only**: These tests run against your local backend
- **No External Dependencies**: All testing is done locally
- **Real Data**: Tests create real orders and modify real stock
- **Telegram Simulation**: Webhook tests simulate bot messages locally
- **Production Ready**: Passing tests indicate your stack is ready for deployment

### For Real Telegram Bot
To enable real Telegram bot functionality:
1. **Public Webhook**: Use ngrok, Render, or similar for HTTPS URL
2. **Bot Token**: Configure in Settings → Integrations
3. **Webhook Setup**: Use the "Set Webhook" button in settings

## 🔧 **API Endpoints**

### Categories
- `GET /api/categories/exists` - Check if categories exist
- `GET /api/categories/summary` - Get categories with product counts
- `GET /api/categories/{id}` - Get specific category
- `POST /api/categories/` - Create new category
- `PATCH /api/categories/{id}` - **NEW**: Update category name and prefix
- `PUT /api/categories/{id}` - Update category name (legacy)
- `DELETE /api/categories/{id}` - Delete category

### Products
- `GET /api/products/` - List/search products with pagination
- `GET /api/products/chatbot` - **NEW**: Chatbot-optimized product search
- `POST /api/products/` - Create new product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

### Chat
- `POST /api/chat` - Send message to chatbot

## 📊 **Database Schema**

### Categories Table
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    prefix VARCHAR UNIQUE NOT NULL,  -- 1-2 uppercase letters
    created_at DATETIME NOT NULL
);
```

### Products Table
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    stock INTEGER DEFAULT 0,
    low_stock_threshold INTEGER DEFAULT 5,
    code VARCHAR UNIQUE NOT NULL,
    category_id INTEGER NOT NULL,
    image_url VARCHAR,           -- Main product image
    thumbnail_url VARCHAR,       -- NEW: Thumbnail for list views
    sizes VARCHAR,               -- Comma-separated sizes
    tags VARCHAR,                -- Comma-separated tags
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

## 🎨 **Frontend Features**

### Category Management
- **Edit Modal**: Update both name and prefix with validation
- **Safety Warnings**: Clear warnings about prefix changes
- **Product Count Display**: Shows how many products in each category
- **Add Product Button**: Direct product creation from category rows

### Product Management
- **Thumbnail Display**: Shows product images in list/grid views
- **Category Preselection**: Automatically selects category from URL or filter
- **Enhanced Forms**: Separate fields for main image and thumbnail URLs
- **Image Upload**: File upload with preview and validation

### Chatbot Interface
- **Smart Detection**: Automatically detects product queries
- **Live Data**: Fetches real-time product information
- **Visual Results**: Displays product images and details in chat
- **Persian Support**: Full RTL and Persian language interface

## 🔄 **Migration Guide**

### Adding thumbnail_url Column
If you need to add the `thumbnail_url` column to existing databases:

```sql
ALTER TABLE products ADD COLUMN thumbnail_url VARCHAR;
```

### Updating Existing Products
```sql
-- Set thumbnail_url to image_url for existing products
UPDATE products SET thumbnail_url = image_url WHERE thumbnail_url IS NULL;
```

## 📝 **CSV Import Format**

### Required Columns
- `name` - Product name
- `price` - Product price
- `stock` - Available stock

### Optional Columns
- `description` - Product description
- `image_url` - Main product image URL
- `thumbnail_url` - **NEW**: Thumbnail image URL
- `tags` - Comma-separated tags
- `is_active` - Active status (true/false)
- `low_stock_threshold` - Low stock warning threshold

### Column Aliases
The system automatically recognizes these variations:
- `qty`, `quantity` → `stock`
- `amount`, `cost` → `price`
- `title`, `product_name`, `product` → `name`
- `desc` → `description`
- `img`, `image` → `image_url`
- `thumbnail`, `thumb`, `thumb_img` → `thumbnail_url`
- `active`, `enabled` → `is_active`

## 🤖 **Chatbot Integration**

### Product Search Tool
The chatbot automatically calls `searchProductsTool` when users ask about products:

```typescript
// Example usage in chatbot
const products = await searchProductsTool({ 
  q: "کفش ورزشی", 
  limit: 5 
});
```

### System Prompt Rules
- **Always search first**: When users ask about available products, call `searchProductsTool`
- **Never guess**: Always fetch live data before answering availability questions
- **Provide codes**: Include product codes in responses for easy reference

### Example Queries
- "چه محصولاتی موجوده؟" → Searches all products
- "قیمت کفش چقدره؟" → Searches for shoes
- "محصولات دسته‌بندی پوشاک" → Searches by category
- "کد محصول A0001" → Searches by product code

## 🎯 **Usage Examples**

### Editing Categories
1. Go to `/dashboard/categories`
2. Click the edit button (✏️) on any category
3. Update name and/or prefix
4. Save changes (prefix changes only affect new products)

### Adding Products from Categories
1. Go to `/dashboard/categories`
2. Click the "افزودن محصول" button (📦) on any category
3. Product modal opens with category preselected
4. Fill in product details and save

### Category Preselection in Products
1. Navigate to `/products?category=1`
2. Product modal automatically selects category ID 1
3. Or use category filter dropdown to select category

### Chatbot Product Queries
1. Go to `/chat` or `/dashboard/chat`
2. Ask questions like:
   - "چه محصولاتی دارید؟"
   - "قیمت کفش چقدره؟"
   - "محصولات دسته‌بندی پوشاک"
3. Chatbot searches live data and shows results with images

## 🚨 **Important Notes**

### Category Prefix Changes
- **Historical Integrity**: Changing a category prefix does NOT affect existing product codes
- **New Products Only**: Only new products created after the change will use the new prefix
- **Validation**: Prefixes must be 1-2 uppercase letters and unique across all categories

### Image Handling
- **Thumbnail Priority**: List views prefer `thumbnail_url` over `image_url`
- **Fallback**: Shows placeholder icon when no images available
- **Performance**: Thumbnails are optimized for list display (56-80px)

### Chatbot Performance
- **Search Limits**: Product searches are capped at 20 results for performance
- **Real-time Data**: Always fetches latest product information
- **Error Handling**: Graceful fallback when search fails

## 🔧 **Troubleshooting**

### Common Issues

#### Category Edit Fails
- Check if name/prefix already exists
- Ensure prefix format is 1-2 uppercase letters
- Verify category ID exists

#### Products Not Showing Thumbnails
- Check if `thumbnail_url` column exists in database
- Verify image URLs are accessible
- Check browser console for image loading errors

#### Chatbot Not Finding Products
- Verify backend is running on correct port
- Check if `/api/products/chatbot` endpoint is accessible
- Ensure products exist in database

#### Import Fails with Thumbnail
- Verify CSV has `thumbnail_url` column (optional)
- Check column name variations (thumbnail, thumb, thumb_img)
- Ensure URLs are valid

## 📚 **API Documentation**

For detailed API documentation, visit:
- Backend: `http://localhost:8000/docs` (Swagger UI)
- Frontend: Check component props and TypeScript interfaces

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🎉 Happy Shopping! 🛍️**

For support or questions, please open an issue in the repository.