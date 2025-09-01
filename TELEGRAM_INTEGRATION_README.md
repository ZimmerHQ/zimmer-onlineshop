# 🤖 Telegram Bot Integration

This document describes the comprehensive Telegram bot integration system for the e-commerce admin panel.

## 🎯 **Features Overview**

### **1. Bot Management**
- **Bot Configuration**: Set bot token, webhook URL, and security secret
- **Connection Testing**: Verify bot connectivity with Telegram API
- **Webhook Management**: Secure webhook endpoint with secret validation

### **2. User Tracking**
- **User Management**: Track Telegram users with visit counts and activity
- **Returning User Detection**: Welcome back users who return after 24+ hours
- **Contact Information**: Store phone numbers and notes for users

### **3. FAQ System**
- **Dynamic FAQs**: Admin-manageable question-answer pairs
- **Tag System**: Categorize FAQs with comma-separated tags
- **Smart Search**: Fuzzy matching on questions, answers, and tags

### **4. CRM & Analytics**
- **Message Logging**: Track all inbound/outbound messages
- **User Interactions**: Monitor user engagement and behavior
- **Statistics**: Comprehensive analytics on bot usage

### **5. Automated Reports**
- **Sales Reports**: Weekly and monthly automated generation
- **CSV Export**: Download reports in CSV format
- **Scheduled Jobs**: Automatic report generation using APScheduler

## 🚀 **Quick Start**

### **1. Install Dependencies**

```bash
# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
```

### **2. Run Migration**

```bash
python migrate_telegram.py
```

### **3. Start Services**

```bash
# Backend
python main.py

# Frontend (in another terminal)
cd frontend
npm run dev
```

### **4. Configure Bot**

1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Go to `/telegram` in the admin panel
4. Enter bot token and webhook URL
5. Click "تست اتصال" to verify connection

## 📱 **Bot Commands**

### **User Commands**
- `/start` - Welcome message and help
- `/faq` - Show frequently asked questions
- `/contact [phone]` - Attach phone number
- `/orders` - View user's orders
- `/help` - Show available commands

### **Product Queries**
- `قیمت A0001` - Get product price by code
- `موجودی شلوار نایک` - Check product stock
- `لیست محصولات` - Show available products

## 🗄️ **Database Schema**

### **TelegramConfig**
```sql
CREATE TABLE telegram_configs (
    id INTEGER PRIMARY KEY,
    bot_token TEXT NOT NULL UNIQUE,
    webhook_url TEXT NOT NULL,
    webhook_secret TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### **TelegramUser**
```sql
CREATE TABLE telegram_users (
    id INTEGER PRIMARY KEY,
    telegram_user_id BIGINT UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    language_code TEXT(8),
    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    visits_count INTEGER DEFAULT 1,
    phone TEXT,
    note TEXT,
    is_blocked BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### **TelegramMessage**
```sql
CREATE TABLE telegram_messages (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    direction TEXT NOT NULL, -- 'in' or 'out'
    text TEXT NOT NULL,
    payload_json TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES telegram_users(id)
);
```

### **FAQ**
```sql
CREATE TABLE faqs (
    id INTEGER PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    tags TEXT, -- comma-separated
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### **SalesReport**
```sql
CREATE TABLE sales_reports (
    id INTEGER PRIMARY KEY,
    period TEXT NOT NULL, -- 'weekly' or 'monthly'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    totals_json TEXT NOT NULL, -- JSON data
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(period, start_date, end_date)
);
```

## 🔧 **API Endpoints**

### **Telegram Webhook**
```
POST /api/telegram/webhook?secret=<webhook_secret>
```

### **Bot Configuration**
```
GET    /api/telegram/config          # Get current config
POST   /api/telegram/config          # Create/update config
POST   /api/telegram/test-connection # Test bot connection
```

### **User Management**
```
GET /api/telegram/users              # List users (paginated)
GET /api/telegram/users/{id}         # Get user details
GET /api/telegram/messages           # List messages
GET /api/telegram/stats              # Get bot statistics
```

### **FAQ Management**
```
GET    /api/telegram/faq             # List FAQs
POST   /api/telegram/faq             # Create FAQ
PATCH  /api/telegram/faq/{id}        # Update FAQ
DELETE /api/telegram/faq/{id}        # Delete FAQ
GET    /api/telegram/faq/stats       # Get FAQ statistics
```

### **Reports**
```
POST /api/telegram/reports/generate  # Generate report
GET  /api/telegram/reports/latest    # Get latest report
GET  /api/telegram/reports           # List reports
GET  /api/telegram/reports/{id}      # Get report details
GET  /api/telegram/reports/{id}/csv  # Download CSV
```

## 🔐 **Security Features**

### **Webhook Security**
- **Secret Validation**: All webhook requests must include the secret
- **Rate Limiting**: Built-in protection against spam
- **Input Validation**: Comprehensive validation of all inputs

### **Bot Token Security**
- **Environment Variables**: Store sensitive data in `.env`
- **Database Encryption**: Optional encryption for stored tokens
- **Access Control**: Admin-only configuration access

## 📊 **Scheduled Jobs**

### **Weekly Reports**
- **Schedule**: Every Monday at 00:10
- **Content**: Orders, revenue, top products, categories
- **Storage**: Automatic database storage

### **Monthly Reports**
- **Schedule**: 1st day of month at 00:15
- **Content**: Comprehensive monthly analytics
- **Cleanup**: Automatic cleanup of old reports

## 🎨 **Frontend Features**

### **Admin Dashboard**
- **Settings Tab**: Bot configuration and testing
- **Users Tab**: User management and analytics
- **Messages Tab**: Message history and CRM
- **FAQ Tab**: FAQ management with inline editing
- **Reports Tab**: Report generation and download

### **RTL Support**
- **Persian Interface**: Full RTL layout support
- **Localized Content**: Persian text throughout
- **Cultural Adaptation**: Iranian phone number validation

## 🧪 **Testing**

### **Bot Testing**
1. **Connection Test**: Verify bot token validity
2. **Webhook Test**: Send test messages via webhook
3. **Command Testing**: Test all bot commands
4. **Product Queries**: Test product search functionality

### **API Testing**
```bash
# Test webhook
curl -X POST "http://localhost:8000/api/telegram/webhook?secret=your_secret" \
  -H "Content-Type: application/json" \
  -d '{"update_id": 1, "message": {"from": {"id": 123}, "text": "/start"}}'

# Test config
curl -X GET "http://localhost:8000/api/telegram/config"

# Test FAQ
curl -X GET "http://localhost:8000/api/telegram/faq"
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Bot Not Responding**
- Check bot token validity
- Verify webhook URL is accessible
- Check webhook secret matches
- Review server logs for errors

#### **Database Errors**
- Run migration script: `python migrate_telegram.py`
- Check database connection
- Verify table structure

#### **Frontend Issues**
- Install dependencies: `npm install`
- Check browser console for errors
- Verify API endpoints are accessible

### **Logs**
- **Backend**: Check Python console output
- **Frontend**: Browser developer tools
- **Database**: SQLite database file

## 📈 **Performance Optimization**

### **Database Indexes**
- User lookup by telegram_user_id
- Message queries by user_id and created_at
- Report queries by period and dates

### **Caching**
- FAQ responses cached in memory
- User data cached for active sessions
- Report data cached for quick access

### **Rate Limiting**
- Webhook rate limiting per IP
- User message rate limiting
- API endpoint rate limiting

## 🔄 **Updates & Maintenance**

### **Regular Tasks**
- **Daily**: Monitor bot activity and errors
- **Weekly**: Review user engagement metrics
- **Monthly**: Generate and review reports
- **Quarterly**: Clean up old data and logs

### **Backup**
- **Database**: Regular SQLite backup
- **Config**: Export bot configuration
- **Logs**: Archive old log files

## 📚 **Additional Resources**

### **Telegram Bot API**
- [Official Documentation](https://core.telegram.org/bots/api)
- [Bot Development Guide](https://core.telegram.org/bots)
- [Webhook Setup](https://core.telegram.org/bots/webhooks)

### **Development Tools**
- [@BotFather](https://t.me/botfather) - Bot creation and management
- [Telegram Webhook Tester](https://webhook.site/) - Test webhook endpoints
- [Bot API Tester](https://t.me/BotFather) - Test bot commands

### **Community**
- [Telegram Bot Development](https://t.me/BotDevelopment)
- [FastAPI Community](https://discord.gg/9U9V5j8)
- [React/Next.js Community](https://discord.gg/nextjs)

## 🎉 **Success Metrics**

### **Bot Performance**
- **Response Time**: < 2 seconds average
- **Uptime**: > 99.9% availability
- **User Satisfaction**: > 90% positive feedback

### **Business Impact**
- **Customer Engagement**: Increased interaction rates
- **Order Conversion**: Higher conversion from chat
- **Support Efficiency**: Reduced manual support requests

---

**Need Help?** Check the logs, run the migration script, or review this documentation. The system is designed to be robust and self-healing. 