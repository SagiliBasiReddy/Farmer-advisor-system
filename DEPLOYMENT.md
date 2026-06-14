# 🚀 Deployment Guide - Agro Advisor

## Prerequisites
- GitHub account (for Vercel connection)
- Railway or Render account
- API Keys:
  - `OPENROUTER_API_KEY` - Get from [OpenRouter](https://openrouter.ai)
  - `SARVAM_API_KEY` - Get from [Sarvam AI](https://sarvam.ai)

---

## 🔧 Step 1: Deploy Backend (Railway or Render)

### Option A: Deploy on Railway (Recommended)

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create a new project → **Deploy from GitHub repo**
4. Select your `Farmer-advisor-system` repository
5. Railway will auto-detect the `Procfile`
6. Add Environment Variables:
   - Click on project → Variables
   - Add:
     - `OPENROUTER_API_KEY` = your API key
     - `SARVAM_API_KEY` = your API key
     - `FLASK_ENV` = `production`
7. Deploy will start automatically
8. Copy your backend URL (e.g., `https://farmer-advisor-xyz.railway.app`)

### Option B: Deploy on Render

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Create → New Web Service
4. Connect your GitHub repository
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment Variables**:
     - `OPENROUTER_API_KEY`
     - `SARVAM_API_KEY`
     - `FLASK_ENV` = `production`
6. Deploy
7. Copy your backend URL (e.g., `https://farmer-advisor.onrender.com`)

---

## 🌐 Step 2: Deploy Frontend (Vercel)

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click **Add New Project** → Import Git Repository
4. Select your `Farmer-advisor-system` repository
5. Configure:
   - **Root Directory**: `agri-advisor`
   - **Framework**: React
   - **Environment Variables**:
     - `VITE_API_BASE_URL` = `https://your-backend-url.railway.app` (or Render URL)
6. Click **Deploy**
7. Your frontend will be live at `https://your-project.vercel.app`

---

## ✅ Testing Your Live Application

1. Open your Vercel frontend URL in browser
2. Try submitting a query
3. Check browser console (F12) for any errors
4. Verify both frontend and backend are communicating

---

## 📝 Environment Variables Summary

### Backend (.env)
```
OPENROUTER_API_KEY=your_key_here
SARVAM_API_KEY=your_key_here
FLASK_ENV=production
```

### Frontend (.env.production in vercel)
```
VITE_API_BASE_URL=https://your-backend-url.railway.app
```

---

## 🔗 CORS Configuration

Backend already has CORS enabled for all origins (`"*"`). For production, update in `app.py`:

```python
CORS(app, origins=["https://your-frontend-url.vercel.app"])
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Frontend can't reach backend | Check `VITE_API_BASE_URL` is correct in Vercel env vars |
| 503 Backend error | Check API keys are set correctly in Railway/Render |
| CORS errors | Ensure backend URL is added to CORS origins |
| Build fails | Check requirements.txt is in root directory |

---

## 📊 Cost Estimate (Free Tier)

- **Vercel**: Free tier includes frontend deployment
- **Railway**: $5/month free credits (usually sufficient)
- **Render**: Free tier available (with limitations)

---

## 📞 Support

For issues:
1. Check Railway/Render logs for backend errors
2. Check Vercel deployment logs for frontend errors
3. Use browser DevTools console for frontend debugging
4. Verify API keys are valid and have quota

Happy farming! 🌾
