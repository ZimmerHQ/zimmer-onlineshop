# 🚀 Zimmer Integration Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ Code Status
- [x] Zimmer integration fully implemented
- [x] All hardcoded data removed and made configurable
- [x] Database models created
- [x] API endpoints implemented
- [x] Persian dashboard ready
- [x] Service token authentication working
- [x] Usage forwarding configured

### 📁 New Files Added
- `app/` - Complete Zimmer integration module
- `migrations/add_zimmer_tables.sql` - Database migration
- `backend.env.example` - Updated with Zimmer settings

## 🚀 Deployment Options

### Option 1: Git-based Deployment (Recommended)

#### Step 1: Commit and Push Changes
```bash
# Add all new files
git add .

# Commit with descriptive message
git commit -m "feat: Add complete Zimmer integration with configurable settings

- Add service token authentication with bcrypt
- Add multi-tenant user management
- Add token consumption and usage tracking
- Add Persian dashboard with RTL support
- Add platform integration with usage forwarding
- Remove all hardcoded data, make everything configurable
- Add comprehensive health checks
- Add database migration for Zimmer tables"

# Push to remote repository
git push origin main
```

#### Step 2: Deploy to Server
```bash
# SSH to your server
ssh user@your-server.com

# Navigate to project directory
cd /path/to/your/project

# Pull latest changes
git pull origin main

# Install/update dependencies
pip install -r requirements.txt

# Run database migration
python -c "
from database import engine, Base
from app.models.zimmer import AutomationUser, UserSession, UsageLedger
Base.metadata.create_all(bind=engine)
print('Zimmer tables created successfully')
"

# Restart services
sudo systemctl restart your-backend-service
```

### Option 2: Direct File Upload

#### Step 1: Create Deployment Package
```bash
# Create deployment archive (excluding unnecessary files)
tar -czf zimmer-update.tar.gz \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='node_modules' \
  --exclude='.env' \
  --exclude='*.pyc' \
  --exclude='app.db' \
  .
```

#### Step 2: Upload to Server
```bash
# Upload to server
scp zimmer-update.tar.gz user@your-server.com:/tmp/

# SSH to server and extract
ssh user@your-server.com
cd /path/to/your/project
tar -xzf /tmp/zimmer-update.tar.gz
```

## 🔧 Environment Configuration

### Required Environment Variables

Add these to your server's `.env` file:

```bash
# Zimmer Integration Settings
SERVICE_TOKEN=your-secure-service-token-here
SERVICE_TOKEN_HASH=optional-bcrypt-hash-if-pre-computed
PLATFORM_API_URL=https://api.zimmerai.com
SEED_TOKENS=1000
APP_VERSION=1.0.0

# Zimmer Configuration Settings
DEFAULT_AUTOMATION_ID=18
HTTP_TIMEOUT=30.0
WEBHOOK_PATH_TEMPLATE=/webhook/{user_id}

# Database field length limits
USER_ID_MAX_LENGTH=255
AUTOMATION_ID_MAX_LENGTH=255
EMAIL_MAX_LENGTH=255
NAME_MAX_LENGTH=255
SESSION_ID_MAX_LENGTH=255
REASON_MAX_LENGTH=255

# Existing settings (keep these)
ENV=production
NODE_ENV=production
DATABASE_URL=your-database-url
OPENAI_API_KEY=your-openai-key
TELEGRAM_BOT_TOKEN=your-telegram-token
```

## 🗄️ Database Migration

### Automatic Migration (Recommended)
The Zimmer tables will be created automatically when the application starts, as they're imported in `main.py`.

### Manual Migration (If Needed)
```bash
# Run the SQL migration directly
sqlite3 app.db < migrations/add_zimmer_tables.sql

# Or for PostgreSQL
psql -d your_database -f migrations/add_zimmer_tables.sql
```

## 🧪 Testing the Deployment

### 1. Health Check
```bash
curl http://your-server.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "last_updated": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "uptime": 3600,
  "database_status": "ok"
}
```

### 2. Test Zimmer Endpoints

#### Test Dashboard
```bash
curl "http://your-server.com/dashboard?user_id=test123&automation_id=18"
```

#### Test Provision Endpoint (with service token)
```bash
curl -X POST "http://your-server.com/api/provision" \
  -H "X-Zimmer-Service-Token: your-service-token" \
  -H "Content-Type: application/json" \
  -d '{
    "user_automation_id": "test123",
    "user_id": "test123",
    "bot_token": "test-bot-token",
    "demo_tokens": 100
  }'
```

#### Test Usage Consumption
```bash
curl -X POST "http://your-server.com/api/usage/consume" \
  -H "X-Zimmer-Service-Token: your-service-token" \
  -H "Content-Type: application/json" \
  -d '{
    "user_automation_id": "test123",
    "tokens_consumed": 10,
    "action": "chat"
  }'
```

## 🔒 Security Considerations

### 1. Service Token Security
- Generate a strong, random service token
- Consider using `SERVICE_TOKEN_HASH` for additional security
- Rotate tokens regularly
- Never log the service token

### 2. Database Security
- Ensure database is properly secured
- Use connection pooling
- Regular backups

### 3. Network Security
- Use HTTPS in production
- Configure proper CORS settings
- Monitor for unusual activity

## 📊 Monitoring

### Key Metrics to Monitor
- Token consumption rates
- API response times
- Error rates (4xx, 5xx)
- Database performance
- Memory usage

### Log Monitoring
```bash
# Monitor application logs
tail -f /var/log/your-app/app.log

# Monitor system logs
journalctl -u your-backend-service -f
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path

2. **Database Errors**
   - Verify database connection
   - Check if tables were created

3. **Authentication Errors**
   - Verify SERVICE_TOKEN is set correctly
   - Check token format

4. **CORS Errors**
   - Update CORS_ORIGINS in config
   - Check frontend URL settings

### Debug Commands
```bash
# Check if Zimmer modules can be imported
python -c "from app.core.settings import *; print('Zimmer config loaded')"

# Test database connection
python -c "from database import engine; print('Database connected')"

# Check service token
python -c "from app.core.service_token import verify_service_token; print('Service token module loaded')"
```

## ✅ Post-Deployment Checklist

- [ ] All environment variables set
- [ ] Database tables created
- [ ] Health check endpoint working
- [ ] Dashboard accessible
- [ ] Service token authentication working
- [ ] Usage tracking functional
- [ ] Platform integration configured (if needed)
- [ ] Monitoring set up
- [ ] Logs being collected
- [ ] Backup strategy in place

## 🎉 Success!

Your Zimmer integration is now deployed and ready to use! The system provides:

- ✅ Multi-tenant user management
- ✅ Token consumption tracking
- ✅ Persian dashboard interface
- ✅ Platform integration capabilities
- ✅ Comprehensive health monitoring
- ✅ Configurable settings for all environments

For support or questions, refer to the individual module documentation in the `app/` directory.
