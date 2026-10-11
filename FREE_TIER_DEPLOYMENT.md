# Free Tier Deployment Guide (Render + Netlify)

This guide explains how to deploy the Naukri Job Automation application on **Render free tier** and **Netlify free tier**.

## ⚠️ Important Free Tier Limitations

### Render Free Tier
- **No persistent storage**: Data is lost when service spins down (every 15 min of inactivity)
- **No WebSocket support**: Uses HTTP polling fallback (already configured)
- **Sleeps after 15 minutes**: Server goes to sleep, browser automation stops
- **512 MB RAM**: May be insufficient for Playwright
- **750 hours/month limit**: If service stays awake continuously

### What This Means for Your Application

❌ **Won't work on free tier:**
- Continuous browser automation (server sleeps)
- Persistent session data (lost on spin-down)
- Long-running automation jobs
- Resume storage between sessions

✅ **Will work on free tier:**
- Testing the UI/frontend
- API endpoints testing
- Manual automation runs (if you keep server awake)
- Short automation sessions (under 15 minutes)

## Step 1: Deploy Backend to Render (Free Tier)

### 1. Push Code to GitHub

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2. Deploy to Render

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml`
5. Click "Create Web Service"

### 3. Verify Deployment

1. Wait for build to complete (may take 5-10 minutes)
2. Copy your backend URL from Render (e.g., `https://naukri-automation-backend.onrender.com`)
3. Test: `https://naukri-automation-backend.onrender.com/api/session/status`
4. Should return: `{"success": true, "connected": false, "expires_at": null}`

## Step 2: Deploy Frontend to Netlify (Free Tier)

### 1. Update API URL

Edit `frontend/.env.production`:
```env
VITE_API_BASE_URL=https://YOUR-BACKEND-URL.onrender.com/api
```

Replace `YOUR-BACKEND-URL` with your actual Render URL.

### 2. Deploy to Netlify

#### Option A: Using Netlify CLI

```bash
cd frontend
npm install -g netlify-cli
netlify login
npm run build
netlify deploy --prod
```

#### Option B: Using Netlify Dashboard

1. Go to https://app.netlify.com
2. Click "Add new site" → "Import an existing project"
3. Connect your GitHub repository
4. Configure:
   - Build command: `npm run build`
   - Publish directory: `dist`
5. Click "Deploy site"

## Step 3: Test the Deployment

1. Open your Netlify frontend URL
2. Try uploading a resume
3. Connect to Naukri
4. **Start automation** (must be done within 15 minutes of last activity)

## Keeping Server Awake (Free Tier Workaround)

To prevent the server from sleeping during automation:

### Option 1: Use Uptime Monitoring

Services like:
- https://uptimerobot.com (free)
- https://betteruptime.com (free)

Set up monitoring to ping your backend every 5-10 minutes.

### Option 2: Manual Wake-Up

Before running automation:
1. Visit your backend URL: `https://your-backend.onrender.com/api/session/status`
2. Wait 30 seconds for server to wake up
3. Start automation immediately

### Option 3: Upgrade to Paid Plan

Render Starter Plan ($7/month):
- No sleep
- Persistent storage
- WebSocket support
- Better performance

## Free Tier Alternatives

If you need persistent data and continuous automation:

### Option 1: Railway (Free Tier)

- Has persistent storage on free tier
- $5 free credit/month
- Supports PostgreSQL
- https://railway.app

### Option 2: Fly.io (Free Tier)

- Free for apps that sleep
- $5 free credit/month
- Persistent storage available
- https://fly.io

### Option 3: VPS (Cheapest for Production)

- DigitalOcean: $4/month
- AWS Lightsail: $3.50/month
- Linode: $5/month
- Full control, 24/7 uptime, persistent storage

## Database on Free Tier

Since Render free tier doesn't have persistent storage:

### Option 1: Use Render PostgreSQL (Free Tier)

Render offers PostgreSQL on free tier:
- 1 GB storage
- 90 days auto-hibernate
- Better than SQLite for production

To switch:
1. Create PostgreSQL database on Render
2. Update `backend/app.py` to use PostgreSQL instead of SQLite
3. Install `psycopg2-binary` in requirements.txt

### Option 2: Use External Database

- Supabase (PostgreSQL, free tier)
- Neon (PostgreSQL, free tier)
- PlanetScale (MySQL, free tier)

## Troubleshooting

### Server won't wake up

- Wait 2-3 minutes after hitting the URL
- Check Render logs for errors
- Verify service is not suspended

### Data disappeared

- This is expected on free tier
- Data is lost when service spins down
- Consider upgrading or using external database

### Automation stops mid-way

- Server went to sleep (15 min timeout)
- Wake up server and restart automation
- Consider uptime monitoring service

### Browser automation fails

- Free tier may not have enough RAM for Playwright
- Try reducing concurrent operations
- Consider upgrading to paid plan

## Recommendation

**For Testing/Development:**
- ✅ Use Render free tier + Netlify free tier
- ✅ Good for testing UI and API
- ❌ Not suitable for production automation

**For Production:**
- Upgrade to Render Starter Plan ($7/month) OR
- Use a VPS ($4-5/month) for full control
- Use PostgreSQL (Render free tier or external)
- Set up uptime monitoring

## Summary

Free tier deployment is **possible but limited**:

| Feature | Free Tier | Paid Tier |
|---------|-----------|-----------|
| Backend hosting | ✅ Render free | ✅ Render $7/mo |
| Frontend hosting | ✅ Netlify free | ✅ Netlify free |
| Persistent storage | ❌ No | ✅ Yes |
| Continuous automation | ❌ Sleeps | ✅ Yes |
| WebSocket | ❌ No | ✅ Yes |
| Database | ❌ SQLite lost | ✅ Persistent |

**For production use, budget $7-12/month for reliable deployment.**
