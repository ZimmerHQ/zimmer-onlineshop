# 🤖 Chatbot Integration with Live Catalog & Orders

This document describes the comprehensive chatbot integration that connects to the live product catalog and enables order creation through natural language conversations.

## 🎯 Overview

The chatbot can now:
- **Search products** by name, code, or category
- **Get detailed product information** including sizes, colors, stock, and pricing
- **Create draft orders** from chat conversations
- **Confirm orders** and move them to the admin approval workflow
- **Check product availability** in real-time

## 🏗️ Architecture

### Backend Components

#### 1. **ProductVariant Model** (`models.py`)
```python
class ProductVariant(Base):
    __tablename__ = "product_variants"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    size = Column(String, nullable=True)  # e.g., "S", "M", "L", "XL", "43", "44"
    color = Column(String, nullable=True)  # e.g., "قرمز", "آبی", "مشکی"
    sku = Column(String, nullable=True)  # Stock Keeping Unit
    stock = Column(Integer, default=0, nullable=False)
    price_delta = Column(Float, default=0.0, nullable=False)  # Price adjustment
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

#### 2. **Enhanced Product Schemas** (`schemas/product.py`)
- `ProductOut`: Includes variants and total_stock
- `ProductSearchResult`: Minimal info for suggestions
- `ProductDetails`: Full details for Q&A
- `VariantOut`: Variant information

#### 3. **Order Service** (`services/order_service.py`)
- `create_draft()`: Creates draft orders from chatbot
- `confirm_order()`: Moves draft to pending status
- `update_status()`: Handles status transitions and inventory updates

#### 4. **New API Endpoints**
- `GET /api/products/search` - Product search for suggestions
- `GET /api/products/code/{code}` - Product details by code
- `GET /api/products/id/{id}` - Product details by ID
- `POST /api/orders/draft` - Create draft order
- `POST /api/orders/confirm` - Confirm draft order
- `PATCH /api/orders/{id}/status` - Update order status

### Frontend Components

#### 1. **Chatbot Tools** (`frontend/lib/ai/tools.ts`)
- `searchProductsTool()` - Search products with minimal info
- `getProductDetailsTool()` - Get full product details
- `createOrderTool()` - Create draft orders
- `confirmOrderTool()` - Confirm draft orders
- `checkAvailabilityTool()` - Check stock availability

#### 2. **Enhanced Orders Page** (`frontend/app/orders/page.tsx`)
- New status workflow: Draft → Pending → Approved → Sold
- Status-specific actions (Approve, Mark as Sold, Cancel)
- Inventory management integration

## 🔄 Order Flow

### 1. **Chatbot Order Creation**
```
User → Chatbot → Draft Order (status: "draft") → User Confirms → Pending Order (status: "pending")
```

### 2. **Admin Approval Workflow**
```
Pending Order → Admin Approves → Approved Order (status: "approved") → Admin Marks as Sold → Sold Order (status: "sold") + Inventory Decremented
```

### 3. **Status Transitions**
- **draft** → pending, cancelled
- **pending** → approved, cancelled
- **approved** → sold, cancelled
- **sold** → cancelled
- **cancelled** → (no further changes)

## 🛠️ Implementation Details

### Database Migration
Run the migration script to add new tables and columns:
```bash
python migrate_schema.py
```

### Environment Setup
Ensure your `.env` file includes:
```env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///app.db
```

### Backend Startup
```bash
python main.py
```

### Frontend Development
```bash
cd frontend
npm run dev
```

## 🧪 Testing the Integration

### 1. **Product Search**
Ask the chatbot: "لیست محصولات موجود؟"
- Should use `searchProductsTool`
- Returns 3-5 product suggestions

### 2. **Product Details**
Ask: "کفش نایک کد A0004 سایز 43 داری؟"
- Should use `getProductDetailsTool`
- Returns size availability + price

### 3. **Order Creation**
Say: "۱ عدد سایز 43 مشکی می‌خوام"
- Should use `createOrderTool`
- Creates draft order
- Asks for confirmation

### 4. **Order Confirmation**
Say: "تایید"
- Should use `confirmOrderTool`
- Moves order to "pending" status

### 5. **Admin Actions**
1. Go to Orders page
2. See order with "pending" status
3. Click "تأیید ادمین" → status becomes "approved"
4. Click "فروخته شد" → status becomes "sold" + inventory decreases

## 📝 Chatbot Instructions

### System Prompt
```
You are a helpful e-commerce assistant. You can:

1. **Search Products**: When users ask about available products, use searchProductsTool
2. **Get Product Details**: For specific product questions, use getProductDetailsTool
3. **Create Orders**: When users want to buy, use createOrderTool and ask for confirmation
4. **Confirm Orders**: After user confirms, use confirmOrderTool

IMPORTANT: Do NOT decrement inventory yourself. Inventory only changes when admin approves and marks as "sold".

Persian Examples:
- "قیمت A0001 چقدره؟" → Use getProductDetailsTool
- "سایز مدیوم کفش نایک داری؟" → Use getProductDetailsTool
- "۲ عدد شلوار کد A0002 سایز ۳۲ می‌خوام" → Use createOrderTool
- "سفارش رو تایید کن" → Use confirmOrderTool
```

### Tool Usage Examples

#### Product Search
```typescript
const result = await searchProductsTool({
  q: "کفش نایک",
  limit: 5
});
```

#### Product Details
```typescript
const result = await getProductDetailsTool({
  code: "A0001"
});
```

#### Order Creation
```typescript
const result = await createOrderTool({
  customer_name: "احمد احمدی",
  contact: "09123456789",
  items: [{
    product_id: 1,
    variant_id: 2,
    quantity: 1
  }]
});
```

## 🔧 Configuration

### OpenAI Configuration
The chatbot uses OpenAI's GPT models for natural language understanding and response generation.

### Database Configuration
- SQLite for development
- PostgreSQL for production (update DATABASE_URL)

### API Configuration
- Backend runs on port 8000
- Frontend runs on port 3000
- CORS configured for local development

## 🚀 Deployment

### Production Considerations
1. **Database**: Use PostgreSQL for production
2. **Security**: Implement proper authentication for admin endpoints
3. **Rate Limiting**: Add rate limiting for chatbot API calls
4. **Monitoring**: Add logging and monitoring for order operations
5. **Backup**: Implement database backup strategy

### Environment Variables
```env
# Production
DATABASE_URL=postgresql://user:pass@host:port/db
OPENAI_API_KEY=your_production_key
ENVIRONMENT=production
```

## 📊 Monitoring & Analytics

### Key Metrics
- Orders created via chatbot
- Conversion rate (draft → sold)
- Average order value
- Popular products in chat

### Logging
- All order status changes are logged
- Inventory updates are tracked
- Chatbot tool usage is monitored

## 🔮 Future Enhancements

### Planned Features
1. **Payment Integration**: Direct payment processing in chat
2. **Inventory Alerts**: Low stock notifications
3. **Customer Support**: Escalation to human agents
4. **Multi-language**: Support for additional languages
5. **Voice Chat**: Voice-to-text integration

### Technical Improvements
1. **Caching**: Redis for product data caching
2. **Async Processing**: Background order processing
3. **Webhooks**: Real-time inventory updates
4. **Analytics**: Advanced reporting and insights

## 🆘 Troubleshooting

### Common Issues

#### 1. **Database Migration Errors**
```bash
# Check if tables exist
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
```

#### 2. **Import Errors**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt
```

#### 3. **CORS Issues**
- Check backend CORS configuration
- Verify frontend URL in backend CORS settings

#### 4. **OpenAI API Errors**
- Verify API key in .env file
- Check API quota and billing

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Next.js Documentation](https://nextjs.org/docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note**: This integration provides a powerful foundation for e-commerce chatbot functionality. The system is designed to be extensible and can be enhanced with additional features as needed. 