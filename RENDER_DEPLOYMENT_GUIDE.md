# 🚀 Maya AI Content Optimization System - Render Deployment

## 📋 Render Deployment Guide

### Step 1: Create Render Web Service
1. Go to: https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: **stusseligmini/maya**

### Step 2: Configure Service
**Basic Settings:**
- **Name**: `maya-ai-content-creator`
- **Region**: `Oregon (US West)` or `Frankfurt (EU)`
- **Branch**: `main`
- **Runtime**: `Python 3`

**Build & Deploy Settings:**
- **Build Command**: `./build.sh`
- **Start Command**: `python main.py`

### Step 3: Environment Variables
Add these in Render dashboard:

```bash
NODE_ENV=production
PYTHON_ENV=production
AI_PROVIDER=openai
CONTENT_MODERATION=true
SECRET_KEY=maya-ai-render-secret-2025
```

### Step 4: Add Database (Optional)
- Click **"New +"** → **"PostgreSQL"**
- Name: `maya-ai-database`
- Render will auto-connect to your web service

## 📱 Access Your Maya AI App

After deployment:

### 🌐 Web Dashboard:
```
https://maya-ai-content-creator.onrender.com
```

### 📱 Mobile PWA App:
```
https://maya-ai-content-creator.onrender.com/app
```

### 🔗 API Documentation:
```
https://maya-ai-content-creator.onrender.com/docs
```

## 📲 Install Mobile App

### iPhone (iOS):
1. Open **Safari** (not Chrome!)
2. Go to: `https://your-app.onrender.com/app`
3. Tap **Share** button (□↑)
4. Select **"Add to Home Screen"**
5. Maya AI installs as native iOS app! 🍎

### Android:
1. Open **Chrome**
2. Go to: `https://your-app.onrender.com/app`
3. Chrome shows **"Add to Home screen"** banner
4. Tap **"Add"** or **"Install"**
5. Maya AI installs as Android app! 🤖

## ✨ Maya AI Features

Your deployed app includes:

- 🤖 **AI Content Generation** - Images, captions, optimization
- 📱 **Multi-Platform Publishing** - Instagram, TikTok, Twitter
- 📊 **Real-time Analytics** - Performance tracking
- 💬 **Telegram Integration** - Notifications and workflow
- 🔍 **Content Moderation** - AI safety scoring
- 📱 **Progressive Web App** - Installable mobile experience
- 🔐 **Authentication System** - Secure user management
- 🗄️ **Database Integration** - PostgreSQL storage

## 🔧 Render Advantages

- ✅ **Free Tier Available** - Great for testing
- ✅ **Auto-deploys from GitHub** - Push to deploy
- ✅ **Built-in SSL** - HTTPS automatically
- ✅ **Easy Scaling** - Upgrade plans as needed
- ✅ **PostgreSQL Included** - Database ready
- ✅ **No Heroku Limitations** - More flexible

## 🚀 Ready to Deploy!

1. **Push code to GitHub** (already done)
2. **Create Render account** and connect GitHub
3. **Follow the steps above** to create web service
4. **Deploy and access your Maya AI PWA!** 🎉

**Result**: Maya AI running as installable mobile PWA on Render! 📱
