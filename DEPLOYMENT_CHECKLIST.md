# 🚀 Deployment Checklist

## ✅ Pre-Deployment Checklist

### Code Status
- [x] Main entry point (`main.py`) configured
- [x] Frontend Next.js app ready
- [x] Dependencies defined in `requirements.txt` and `package.json`
- [x] Database auto-creation on startup
- [x] CORS properly configured
- [x] Health check endpoint available
- [x] No linting errors

### Environment Variables Needed
Create `.env` file on your server with these variables:

```
ENV=production
NODE_ENV=production
DATABASE_URL=postgresql://shop_user:your_password@localhost:5432/shop_automation
BACKEND_URL=https://your-domain.com
FRONTEND_URL=https://your-domain.com
NEXT_PUBLIC_API_BASE=https://your-domain.com
OPENAI_API_KEY=your-openai-api-key
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_SECRET=your-webhook-secret
SECRET_KEY=your-super-secret-key
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
RATE_LIMIT_PER_MINUTE=100
MAX_FILE_SIZE=10485760
UPLOAD_DIR=/var/www/shop-automation/static/uploads
ADDITIONAL_CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

## 🚀 Deployment Steps

### Step 1: Upload Code
```bash
# Option A: Git
git add .
git commit -m "Production deployment"
git push origin main

# On server:
cd /var/www/shop-automation
sudo -u www-data git pull origin main
```

### Step 2: Install Dependencies
```bash
# Backend
cd /var/www/shop-automation
sudo -u www-data python3.11 -m venv venv
sudo -u www-data ./venv/bin/pip install -r requirements.txt

# Frontend
cd frontend
sudo -u www-data npm ci
sudo -u www-data npm run build
cd ..
```

### Step 3: Database Setup
```bash
# Create tables
sudo -u www-data ./venv/bin/python -c "
from database import engine
from models import Base
Base.metadata.create_all(bind=engine)
print('Database tables created')
"
```

### Step 4: Start Services
```bash
sudo systemctl start shop-backend
sudo systemctl start shop-frontend
sudo systemctl status shop-backend
sudo systemctl status shop-frontend
```

### Step 5: Test
```bash
curl http://localhost:8000/api/health
curl http://localhost:3000
curl https://your-domain.com/api/health
```

## 🔧 Troubleshooting

### Common Issues:
1. **Port conflicts**: Check with `sudo netstat -tulpn | grep :8000`
2. **Permission issues**: `sudo chown -R www-data:www-data /var/www/shop-automation`
3. **Database connection**: Check PostgreSQL status with `sudo systemctl status postgresql`

### Logs:
```bash
sudo journalctl -u shop-backend -f
sudo journalctl -u shop-frontend -f
sudo tail -f /var/log/nginx/error.log
```

## ✅ Your Code is Ready!
All systems are go for deployment!
