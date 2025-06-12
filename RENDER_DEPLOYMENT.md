# Atlas AI - Render.com Deployment Guide

## 🎯 Overview

This guide provides step-by-step instructions for deploying Atlas AI to Render.com with all voice-enabled personal assistant features.

## ✅ Pre-Deployment Checklist

### Required Services & API Keys
- [ ] **Supabase Account** - Database and authentication
- [ ] **OpenAI API Key** - Core LLM functionality
- [ ] **Anthropic API Key** - Claude models
- [ ] **OpenWeather API Key** - Weather assistant features
- [ ] **Tavily API Key** - Search assistant features
- [ ] **Render.com Account** - Hosting platform

### Optional Services
- [ ] **SERP API Key** - Enhanced search capabilities
- [ ] **Firecrawl API Key** - Web scraping features
- [ ] **Daytona API Key** - Code execution sandbox
- [ ] **Mailtrap API Token** - Email notifications

## 🚀 Deployment Steps

### Step 1: Prepare Repository

1. **Ensure all files are committed:**
```bash
git add .
git commit -m "Prepare Atlas AI for Render deployment"
git push origin main
```

2. **Verify deployment files exist:**
- ✅ `render.yaml` - Render Blueprint configuration
- ✅ `backend/Dockerfile` - Backend container configuration
- ✅ `frontend/Dockerfile` - Frontend container configuration
- ✅ `backend/.env.render` - Backend environment template
- ✅ `frontend/.env.render` - Frontend environment template

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up or log in
3. Connect your GitHub account
4. Authorize Render to access your Atlas AI repository

### Step 3: Deploy Using Blueprint

1. **In Render Dashboard:**
   - Click **"New"** → **"Blueprint"**
   - Select your **Atlas AI repository**
   - Render will detect `render.yaml` automatically

2. **Review Services:**
   - `atlas-ai-backend` - FastAPI backend service
   - `atlas-ai-frontend` - Next.js frontend service
   - `atlas-ai-redis` - Redis database (optional)

3. **Click "Apply"** to create services

### Step 4: Configure Environment Variables

#### Backend Service (`atlas-ai-backend`)

**Required Variables:**
```bash
# Core Configuration
ENV_MODE=production
PYTHONPATH=/app

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# LLM APIs
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key
MODEL_TO_USE=anthropic/claude-3-7-sonnet-latest

# Atlas AI Assistant APIs
OPENWEATHER_API_KEY=your_openweather_api_key
TAVILY_API_KEY=your_tavily_api_key

# Redis (if using Render Redis)
REDIS_HOST=atlas-ai-redis
REDIS_PORT=6379
REDIS_SSL=true

# Performance
WORKERS=4
THREADS=2
WORKER_CONNECTIONS=1000
```

**Optional Variables:**
```bash
# Enhanced Search
SERP_API_KEY=your_serp_api_key

# Web Scraping
FIRECRAWL_API_KEY=your_firecrawl_api_key
FIRECRAWL_URL=https://api.firecrawl.dev

# Code Execution
DAYTONA_API_KEY=your_daytona_api_key
DAYTONA_SERVER_URL=https://app.daytona.io/api
DAYTONA_TARGET=us

# Email Notifications
MAILTRAP_API_TOKEN=your_mailtrap_api_token
MAILTRAP_SENDER_EMAIL=noreply@your-domain.com
MAILTRAP_SENDER_NAME=Atlas AI Team

# Monitoring
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

#### Frontend Service (`atlas-ai-frontend`)

**Required Variables:**
```bash
# Environment
NODE_ENV=production
NEXT_PUBLIC_ENV_MODE=production
NEXT_PUBLIC_VERCEL_ENV=production

# Backend Connection
NEXT_PUBLIC_BACKEND_URL=https://atlas-ai-backend.onrender.com/api
NEXT_PUBLIC_API_URL=https://atlas-ai-backend.onrender.com/api

# Frontend URL
NEXT_PUBLIC_URL=https://atlas-ai-frontend.onrender.com

# Database
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Optional Variables:**
```bash
# Google OAuth
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id

# OpenAI for frontend features
OPENAI_API_KEY=your_openai_api_key
```

### Step 5: Set Environment Variables in Render

1. **For Backend Service:**
   - Go to `atlas-ai-backend` service
   - Click **"Environment"** tab
   - Add each variable from the backend list above
   - Mark sensitive keys as **"Secret"**

2. **For Frontend Service:**
   - Go to `atlas-ai-frontend` service
   - Click **"Environment"** tab
   - Add each variable from the frontend list above

### Step 6: Deploy Services

1. **Automatic Deployment:**
   - Services will deploy automatically after environment setup
   - Monitor deployment logs for any errors

2. **Manual Deployment (if needed):**
   - Go to service dashboard
   - Click **"Manual Deploy"**
   - Select **"Deploy latest commit"**

### Step 7: Verify Deployment

1. **Check Service URLs:**
   - Backend: `https://atlas-ai-backend.onrender.com`
   - Frontend: `https://atlas-ai-frontend.onrender.com`

2. **Test Health Endpoints:**
   ```bash
   curl https://atlas-ai-backend.onrender.com/health
   curl https://atlas-ai-backend.onrender.com/api/health
   ```

3. **Test Frontend:**
   - Visit your frontend URL
   - Test voice features (requires HTTPS ✅)
   - Try assistant commands:
     - "Hey Atlas, what's the weather?"
     - "Remind me to call mom at 3pm"
     - "Search for the latest AI news"

## 🔧 Post-Deployment Configuration

### Update CORS Origins

If you encounter CORS errors, update the backend CORS configuration:

1. **In your backend service environment, add:**
```bash
# Add your actual frontend URL
FRONTEND_URL=https://your-actual-frontend-url.onrender.com
```

2. **The backend automatically includes Render URLs in CORS origins**

### Custom Domain (Optional)

1. **In Render Dashboard:**
   - Go to your frontend service
   - Click **"Settings"** → **"Custom Domains"**
   - Add your domain (e.g., `atlas-ai.yourdomain.com`)
   - Update DNS records as instructed

2. **Update Environment Variables:**
   - Update `NEXT_PUBLIC_URL` to your custom domain
   - Update backend CORS origins if needed

## 🐛 Troubleshooting

### Common Issues

**Build Failures:**
- Check service logs in Render dashboard
- Verify all dependencies in requirements.txt/package.json
- Ensure Dockerfile syntax is correct

**Environment Variable Issues:**
- Verify all required variables are set
- Check for typos in variable names
- Ensure sensitive variables are marked as "Secret"

**CORS Errors:**
- Verify frontend URL in backend CORS configuration
- Check NEXT_PUBLIC_BACKEND_URL is correct
- Ensure both services are using HTTPS

**Voice Features Not Working:**
- Voice features require HTTPS (✅ automatic with Render)
- Test in Chrome, Edge, or Safari
- Check browser permissions for microphone

**Database Connection Issues:**
- Verify Supabase URL and keys
- Check Supabase project is active
- Ensure 'basejump' schema is exposed in Supabase

### Performance Optimization

**For Production Traffic:**
1. **Upgrade Service Plans:**
   - Backend: Standard or Pro plan
   - Frontend: Standard plan
   - Redis: Standard plan

2. **Optimize Workers:**
   ```bash
   # For Standard plan (1 CPU)
   WORKERS=3
   THREADS=2
   
   # For Pro plan (2 CPU)
   WORKERS=5
   THREADS=2
   ```

### Monitoring

**Service Health:**
- Monitor service metrics in Render dashboard
- Set up alerts for service downtime
- Check logs regularly for errors

**Application Monitoring:**
- Use Langfuse for LLM call monitoring
- Monitor Supabase usage and performance
- Track API usage for external services

## 💰 Cost Estimation

### Free Tier Limitations
- **Services sleep after 15 minutes** of inactivity
- **750 hours/month** total across all services
- **Limited CPU and memory**

### Recommended Production Setup
- **Backend:** Standard plan ($7/month)
- **Frontend:** Starter plan ($0/month) or Standard ($7/month)
- **Redis:** Starter plan ($0/month) or Standard ($7/month)
- **Total:** ~$14-21/month

## 🎯 Success Criteria

✅ **Backend service running** at `https://atlas-ai-backend.onrender.com`
✅ **Frontend service running** at `https://atlas-ai-frontend.onrender.com`
✅ **Health checks passing** for both services
✅ **Voice features working** (speech recognition and synthesis)
✅ **Assistant features working** (weather, reminders, search)
✅ **Database connected** (Supabase)
✅ **No CORS errors** between frontend and backend

## 📚 Additional Resources

- [Render Documentation](https://docs.render.com)
- [Atlas AI Setup Guide](./ATLAS_AI_SETUP.md)
- [Supabase Documentation](https://supabase.com/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)

---

**🎉 Congratulations!** Your Atlas AI voice-enabled personal assistant is now deployed and ready to use on Render.com!
