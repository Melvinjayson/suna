# Atlas AI Render Deployment Troubleshooting

## 🚨 Common Deployment Issues & Solutions

### Issue 1: "failed to read dockerfile: open Dockerfile: no such file or directory"

**Problem:** Render can't find the Dockerfile in the expected location.

**Solutions:**

#### Option A: Use the Fixed Docker Configuration ✅ **RECOMMENDED**
```yaml
# Use the updated render.yaml (already fixed)
# Backend uses: Dockerfile.backend
# Frontend uses: Node.js runtime (more reliable)
```

#### Option B: Use Simplified Configuration
```bash
# Rename render-simple.yaml to render.yaml
mv render-simple.yaml render.yaml
git add render.yaml
git commit -m "Use simplified Render configuration"
git push origin main
```

#### Option C: Manual Service Creation
1. **Create Backend Service:**
   - Type: Web Service
   - Runtime: Docker
   - Dockerfile Path: `Dockerfile.backend`
   - Docker Context: `.` (root)

2. **Create Frontend Service:**
   - Type: Web Service
   - Runtime: Node
   - Build Command: `cd frontend && npm ci && npm run build`
   - Start Command: `cd frontend && npm start`

### Issue 2: Build Failures

**Backend Build Issues:**
```bash
# Check Python dependencies
cd backend
pip install -r requirements.txt

# Verify all Atlas AI dependencies are present:
# - aiohttp>=3.9.0
# - email-validator>=2.0.0
# - tavily-python>=0.5.4
```

**Frontend Build Issues:**
```bash
# Check Node.js dependencies
cd frontend
npm ci
npm run build

# Verify Next.js configuration
npm run lint
```

### Issue 3: Environment Variable Issues

**Missing Required Variables:**
```bash
# Backend minimum required:
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Frontend minimum required:
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_key
NEXT_PUBLIC_BACKEND_URL=https://atlas-ai-backend.onrender.com/api
```

**Setting Variables in Render:**
1. Go to Service → Environment
2. Add each variable individually
3. Mark sensitive keys as "Secret"
4. Click "Save Changes"

### Issue 4: Service Communication Issues

**CORS Errors:**
```bash
# Backend automatically includes Render URLs in CORS
# If issues persist, manually add your frontend URL:
FRONTEND_URL=https://your-frontend-url.onrender.com
```

**Health Check Failures:**
```bash
# Test health endpoints:
curl https://atlas-ai-backend.onrender.com/health
curl https://atlas-ai-frontend.onrender.com/api/health
```

### Issue 5: Atlas AI Features Not Working

**Voice Features:**
- ✅ Requires HTTPS (automatic with Render)
- ✅ Test in Chrome, Edge, or Safari
- ✅ Allow microphone permissions

**Assistant Features:**
```bash
# Test weather API:
curl "https://atlas-ai-backend.onrender.com/api/assistant/weather/current?location=London"

# Test assistant query:
curl -X POST "https://atlas-ai-backend.onrender.com/api/assistant/query" \
  -H "Content-Type: application/json" \
  -d '{"text": "what is the weather like?"}'
```

## 🔧 Quick Fixes

### Fix 1: Redeploy with Latest Changes
```bash
# Latest commit includes all fixes
git pull origin main
# Trigger manual deploy in Render dashboard
```

### Fix 2: Use Alternative Configuration
```bash
# Switch to simplified configuration
cp render-simple.yaml render.yaml
git add render.yaml
git commit -m "Switch to simplified Render config"
git push origin main
```

### Fix 3: Manual Service Setup
If Blueprint fails, create services manually:

1. **Backend Service:**
   - Repository: Melvinjayson/suna
   - Runtime: Docker
   - Dockerfile: Dockerfile.backend
   - Environment: Copy from backend/.env.render

2. **Frontend Service:**
   - Repository: Melvinjayson/suna
   - Runtime: Node
   - Build: `cd frontend && npm ci && npm run build`
   - Start: `cd frontend && npm start`
   - Environment: Copy from frontend/.env.render

## 📞 Getting Help

### Check Service Logs
1. Go to Render Dashboard
2. Select your service
3. Click "Logs" tab
4. Look for error messages

### Common Log Messages
```bash
# Good signs:
"Application startup complete"
"Uvicorn running on http://0.0.0.0:8000"
"ready - started server on 0.0.0.0:3000"

# Issues to investigate:
"ModuleNotFoundError"
"ENOENT: no such file or directory"
"Error: Cannot find module"
```

### Test Locally First
```bash
# Test backend locally:
cd backend
pip install -r requirements.txt
python api.py

# Test frontend locally:
cd frontend
npm install
npm run build
npm start
```

## ✅ Success Checklist

- [ ] Services deploy without errors
- [ ] Health checks pass
- [ ] Environment variables set
- [ ] Frontend loads at your URL
- [ ] Backend API responds
- [ ] Voice features work (HTTPS)
- [ ] Assistant features respond
- [ ] No CORS errors in browser console

## 🎯 Alternative Deployment Options

If Render continues to have issues:

1. **Vercel** (Frontend) + **Railway** (Backend)
2. **Netlify** (Frontend) + **Heroku** (Backend)
3. **AWS App Runner** (Both services)
4. **Google Cloud Run** (Both services)

---

**Need more help?** Check the detailed logs in Render dashboard and compare with the working local setup.
