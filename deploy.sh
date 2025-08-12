#!/bin/bash

# 🚀 Deployment Script for Render
# This script helps you deploy your application to Render

echo "🎯 Starting deployment process..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not initialized. Please run:"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
    exit 1
fi

# Check if remote is set
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❌ Git remote 'origin' not set. Please run:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/insta-backend-unified.git"
    exit 1
fi

# Build frontend
echo "🔨 Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Commit changes
echo "📝 Committing changes..."
git add .
git commit -m "Deploy: $(date)"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push origin main

echo "✅ Deployment script completed!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://dashboard.render.com"
echo "2. Create a new Web Service"
echo "3. Connect your GitHub repository"
echo "4. Set environment variables:"
echo "   - ENVIRONMENT=production"
echo "   - OPENAI_API_KEY=your_key_here"
echo "5. Deploy!"
echo ""
echo "📖 See DEPLOYMENT.md for detailed instructions" 