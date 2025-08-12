@echo off
echo 🚀 Starting unified deployment...

echo 📦 Installing Python dependencies...
pip install -r requirements.txt

echo 🏗️ Building frontend...
cd frontend
npm ci
npm run build
npm run export
cd ..

echo 🌐 Starting server...
uvicorn main:app --host 0.0.0.0 --port 8000 