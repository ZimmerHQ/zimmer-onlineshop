# 🚀 Deployment Guide for Render

This guide will help you deploy your unified backend and frontend application to Render.

## 📋 Prerequisites

1. **GitHub Account**: You need a GitHub account to host your code
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **OpenAI API Key**: For the chatbot functionality

## 🛠️ Step 1: Prepare Your Repository

### 1.1 Create a new GitHub repository

1. Go to [GitHub](https://github.com) and click "New repository"
2. Name it something like `insta-backend-unified`
3. Make it **Public** (Render free tier requirement)
4. Don't initialize with README (we'll push our existing code)

### 1.2 Push your code to GitHub

```bash
# Navigate to your backend directory (the one containing frontend folder)
cd "C:\Users\Pro Shop\Desktop\ZIMMER\automation\insta\backend"

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Unified backend and frontend"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/insta-backend-unified.git

# Push to GitHub
git push -u origin main
```

## 🌐 Step 2: Deploy to Render

### 2.1 Connect to Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" and select "Web Service"
3. Connect your GitHub account if not already connected
4. Select your repository: `insta-backend-unified`

### 2.2 Configure the Web Service

**Basic Settings:**
- **Name**: `insta-backend-unified` (or any name you prefer)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: Leave empty (root of repository)

**Build & Deploy Settings:**
- **Build Command**: `pip install -r requirements.txt && cd frontend && npm install && npm run build`
- **Start Command**: `python start_server.py`

### 2.3 Environment Variables

Add these environment variables in Render dashboard:

| Key | Value | Description |
|-----|-------|-------------|
| `ENVIRONMENT` | `production` | Tells the app it's in production mode |
| `OPENAI_API_KEY` | `your_openai_api_key_here` | Your OpenAI API key |
| `DATABASE_URL` | `sqlite:///app.db` | Database URL (SQLite for free tier) |

### 2.4 Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Wait for the build to complete (usually 5-10 minutes)

## 🔧 Step 3: Post-Deployment Setup

### 3.1 Test Your Application

1. Once deployed, Render will give you a URL like: `https://your-app-name.onrender.com`
2. Visit the URL to test your application
3. Test the chat functionality
4. Test product management
5. Test file uploads

### 3.2 Custom Domain (Optional)

1. In Render dashboard, go to your web service
2. Click "Settings" → "Custom Domains"
3. Add your custom domain
4. Update DNS records as instructed

## 🐛 Troubleshooting

### Common Issues:

1. **Build Fails**: Check the build logs in Render dashboard
2. **Frontend Not Loading**: Ensure `npm run build` completed successfully
3. **Database Issues**: SQLite files are ephemeral on Render free tier
4. **API Key Issues**: Verify your OpenAI API key is set correctly

### Debug Commands:

```bash
# Check if frontend built correctly
ls frontend/.next

# Check if backend starts
python start_server.py

# Test API endpoints
curl https://your-app.onrender.com/api/health
```

## 📝 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | Yes | `development` | Set to `production` for Render |
| `OPENAI_API_KEY` | Yes | - | Your OpenAI API key |
| `DATABASE_URL` | No | `sqlite:///app.db` | Database connection string |
| `PORT` | No | `8000` | Port for the server |

## 🔄 Updating Your Application

To update your application:

1. Make changes to your code
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update description"
   git push
   ```
3. Render will automatically redeploy

## 💰 Cost Considerations

- **Free Tier**: 750 hours/month, 512MB RAM, shared CPU
- **Paid Plans**: Start at $7/month for dedicated resources
- **Database**: Consider PostgreSQL for production (paid)

## 🎉 Success!

Your application is now deployed and accessible worldwide! 

**Next Steps:**
1. Test all functionality
2. Set up monitoring
3. Consider upgrading to paid plan for production use
4. Set up custom domain
5. Configure SSL certificates (automatic on Render) 