# Online Shop API Upgrade - v2.0.0

This document describes the comprehensive upgrade to the FastAPI + SQLAlchemy online shop backend, adding categories, product codes, and bulk import functionality.

## 🚀 New Features

### 1. Categories with Auto-Assigned Prefixes
- **Unique 1-letter prefixes**: A, B, C, ..., Z, AA, AB, etc.
- **Automatic assignment**: No manual prefix management needed
- **Global scope**: Categories are shared across all users

### 2. Product Codes per Category
- **Format**: `{prefix}{number:04d}` (e.g., A0001, A0002, B0001)
- **Auto-generation**: Codes are automatically assigned when creating products
- **Unique per category**: Each category starts from 0001
- **Immutable**: Product codes cannot be changed after creation

### 3. Advanced Product Search
- **Multi-field search**: Search by product name, code, or category name
- **Category filtering**: Filter products by category ID
- **Pagination**: Built-in limit/offset pagination
- **Case-insensitive**: Search works with partial matches

### 4. Bulk Import System
- **CSV/XLSX support**: Import products from spreadsheet files
- **Preview mode**: Validate data before importing
- **Auto-category creation**: New categories are created automatically
- **Robust validation**: Comprehensive error checking and reporting
- **Template download**: Get a CSV template with proper headers

### 5. GPT-Friendly Outputs
- **Flat structure**: All data in simple, readable fields
- **Category names included**: No need for additional lookups
- **Consistent format**: All timestamps in ISO format
- **Persian support**: Full support for Persian text

## 📁 Project Structure

```
backend/
├── models/
│   ├── __init__.py
│   ├── category.py          # Category SQLAlchemy model
│   └── product.py           # Updated Product model
├── schemas/
│   ├── __init__.py
│   ├── category.py          # Category Pydantic schemas
│   ├── product.py           # Product Pydantic schemas
│   └── imports.py           # Import schemas
├── services/
│   ├── __init__.py
│   ├── category_service.py  # Category business logic
│   ├── product_service.py   # Product business logic
│   └── import_service.py    # Import business logic
├── routers/
│   ├── __init__.py
│   ├── categories.py        # Category endpoints
│   ├── products.py          # Product endpoints
│   └── imports.py           # Import endpoints
├── utils/
│   ├── __init__.py
│   ├── clock.py             # UTC datetime utilities
│   ├── category_prefix.py   # Prefix assignment logic
│   └── product_code.py      # Code generation logic
├── main_new.py              # Updated main application
├── migrate_schema.py        # Database migration script
├── test_new_api.py          # API test script
└── requirements.txt         # Updated dependencies
```

## 🗄️ Database Schema

### Categories Table
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    prefix VARCHAR(1) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL
);
```

### Products Table (Updated)
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    stock INTEGER DEFAULT 0,
    code VARCHAR NOT NULL UNIQUE,
    category_id INTEGER NOT NULL,
    image_url VARCHAR,
    tags VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Database Migration
```bash
python migrate_schema.py
```

### 3. Start the Server
```bash
python main_new.py
```

### 4. Test the API
```bash
python test_new_api.py
```

## 📚 API Endpoints

### Categories

#### Create Category
```http
POST /api/categories/
Content-Type: application/json

{
    "name": "Jeans"
}
```

**Response:**
```json
{
    "id": 1,
    "name": "Jeans",
    "prefix": "A",
    "created_at": "2024-01-15T10:30:00Z"
}
```

#### List Categories
```http
GET /api/categories/
```

**Response:**
```json
[
    {
        "id": 1,
        "name": "Jeans",
        "prefix": "A",
        "created_at": "2024-01-15T10:30:00Z"
    },
    {
        "id": 2,
        "name": "Shirts",
        "prefix": "B",
        "created_at": "2024-01-15T10:35:00Z"
    }
]
```

### Products

#### Create Product
```http
POST /api/products/
Content-Type: application/json

{
    "name": "شلوار جین آبی",
    "description": "کلاسیک روزمره",
    "price": 450000.0,
    "stock": 10,
    "category_id": 1,
    "image_url": "https://example.com/jeans1.jpg",
    "tags": "jeans,blue,classic",
    "is_active": true
}
```

**Response:**
```json
{
    "id": 12,
    "code": "A0001",
    "name": "شلوار جین آبی",
    "description": "کلاسیک روزمره",
    "price": 450000.0,
    "stock": 10,
    "category_id": 1,
    "category_name": "Jeans",
    "image_url": "https://example.com/jeans1.jpg",
    "tags": "jeans,blue,classic",
    "is_active": true,
    "created_at": "2024-01-15T10:40:00Z",
    "updated_at": "2024-01-15T10:40:00Z"
}
```

#### Search Products
```http
GET /api/products/?q=جین&category_id=1&limit=10&offset=0
```

#### Get Product by ID
```http
GET /api/products/12
```

#### Update Product
```http
PATCH /api/products/12
Content-Type: application/json

{
    "price": 480000.0,
    "stock": 8
}
```

### Imports

#### Preview Import
```http
POST /api/imports/products/preview
Content-Type: multipart/form-data

file: products.csv
mapping: {"Product Name": "name", "Price": "price"}
```

#### Commit Import
```http
POST /api/imports/products/commit
Content-Type: multipart/form-data

file: products.csv
```

#### Download Template
```http
GET /api/imports/products/template.csv
```

## 📊 Import Format

### CSV Template
```csv
name,price,stock,category_name,description,image_url,tags,is_active
شلوار جین آبی,450000,10,Jeans,کلاسیک روزمره,https://example.com/jeans1.jpg,jeans,blue,classic,true
پیراهن سفید,350000,15,Shirts,پیراهن رسمی,https://example.com/shirt1.jpg,shirt,white,formal,true
```

### Required Fields
- `name`: Product name (required)
- `price`: Product price (required, > 0)
- `stock`: Stock quantity (required, >= 0)
- `category_name`: Category name (required, will be created if doesn't exist)

### Optional Fields
- `description`: Product description
- `image_url`: Product image URL
- `tags`: Comma-separated tags
- `is_active`: Active status (true/false, default: true)

## 🔧 Configuration

### Environment Variables
```bash
DATABASE_URL=sqlite:///./app.db
OPENAI_API_KEY=your_openai_key
TELEGRAM_TOKEN=your_telegram_token
```

### Dependencies
- `fastapi>=0.116.0`
- `sqlalchemy>=2.0.41`
- `openpyxl>=3.1.0` (for XLSX import support)
- `python-multipart>=0.0.20` (for file uploads)

## 🧪 Testing

### Run Tests
```bash
python test_new_api.py
```

### Manual Testing with curl

#### Create Category
```bash
curl -X POST "http://localhost:8000/api/categories/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Jeans"}'
```

#### Create Product
```bash
curl -X POST "http://localhost:8000/api/products/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "شلوار جین آبی",
    "description": "کلاسیک روزمره",
    "price": 450000.0,
    "stock": 10,
    "category_id": 1,
    "tags": "jeans,blue,classic"
  }'
```

#### Search Products
```bash
curl "http://localhost:8000/api/products/?q=جین&limit=10"
```

#### Download Template
```bash
curl "http://localhost:8000/api/imports/products/template.csv" -o template.csv
```

## 🔄 Migration from v1.0

### Automatic Migration
The `migrate_schema.py` script handles:
1. Creating the categories table
2. Adding new columns to products table
3. Creating an "Uncategorized" category
4. Backfilling product codes for existing products

### Manual Steps
1. Backup your existing database
2. Run the migration script
3. Update your application to use the new main.py
4. Test the new functionality

## 🐛 Troubleshooting

### Common Issues

1. **Import fails with "Category not found"**
   - Ensure category_name is provided in the CSV
   - Categories will be created automatically if they don't exist

2. **Product code conflicts**
   - The system automatically handles race conditions
   - If conflicts persist, check for duplicate category prefixes

3. **XLSX import fails**
   - Install openpyxl: `pip install openpyxl`
   - Ensure the file is a valid Excel format

4. **Database migration errors**
   - Backup your database before migration
   - Check for existing foreign key constraints
   - Run migration in a test environment first

## 📈 Performance Notes

- **Indexes**: Product codes and category IDs are indexed for fast lookups
- **Pagination**: Use limit/offset for large result sets
- **Search**: Case-insensitive search with LIKE queries
- **Import**: Large files are processed in memory with validation

## 🔮 Future Enhancements

- **Bulk operations**: Update/delete multiple products
- **Category hierarchy**: Parent-child category relationships
- **Advanced search**: Full-text search with Elasticsearch
- **Image processing**: Automatic thumbnail generation
- **Audit trail**: Track product changes over time
- **API versioning**: Support for multiple API versions

## 📄 License

This upgrade maintains compatibility with the existing system while adding powerful new features for product management and bulk operations. 