# Deployment Guide

This guide explains how to deploy the Naukri Job Automation application to Render (backend) and Netlify (frontend).

## Architecture

- **Backend (Flask + Socket.IO)**: Deployed on Render
- **Frontend (React + Vite)**: Deployed on Netlify
- **Database**: SQLite (stored on Render's persistent disk)
- **Communication**: REST API + WebSocket (Socket.IO)

## Prerequisites

1. **Render Account**: Sign up at https://render.com
2. **Netlify Account**: Sign up at https://netlify.com
3. **GitHub Account**: Push your code to GitHub
4. **API Keys**: Configure LLM API keys (Groq, Gemini, or OpenRouter)

## Step 1: Configure Environment Variables

### Backend (.env)

Create or update `.env` in the project root:

```env
# LLM API Keys (at least one required)
GROQ_API_KEY=your-groq-api-key-here
# GEMINI_API_KEY=your-gemini-api-key-here
# OPENROUTER_API_KEY=your-openrouter-api-key-here

# Optional: Email notifications
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
# NOTIFICATION_FROM_EMAIL=your-email@gmail.com
# NOTIFICATION_TO_EMAIL=your-email@gmail.com
```

### Frontend (.env.production)

The `.env.production` file is already configured:

```env
VITE_API_BASE_URL=https://naukri-automation-backend.onrender.com/api
```

**Important**: After deploying the backend, update this URL with your actual Render backend URL.

## Step 2: Deploy Backend to Render

### Option A: Using render.yaml (Recommended)

1. Push your code to GitHub
2. Go to https://dashboard.render.com
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Render will automatically detect `render.yaml`
6. Click "Create Web Service"

### Option B: Manual Configuration

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: naukri-automation-backend
   - **Region**: Oregon (or closest to you)
   - **Branch**: main
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt && playwright install chromium`
   - **Start Command**: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT backend.app:app`
5. Add Environment Variables:
   - `PORT`: `5000`
   - `ENABLE_HTTPS`: `false`
   - `FLASK_DEBUG`: `false`
6. Click "Create Web Service"

### Important: Free Tier Limitations

⚠️ **Render Free Tier does NOT support persistent storage**

On the free tier:
- Data is lost when the service spins down (every 15 minutes of inactivity)
- Session data, profile, and resumes will be deleted automatically
- Browser automation won't work continuously (server sleeps)
- For persistent data, upgrade to Render Starter Plan ($7/month)

To keep data persistent, consider:
1. **Using a database service** (Render PostgreSQL - free tier available)
2. **Using external storage** (AWS S3, Google Cloud Storage)
3. **Upgrading to Render Starter Plan** ($7/month)

### Verify Backend Deployment

1. Copy your backend URL from Render (e.g., `https://naukri-automation-backend.onrender.com`)
2. Test: `https://naukri-automation-backend.onrender.com/api/session/status`
3. Should return: `{"success": true, "connected": false, "expires_at": null}`

## Step 3: Deploy Frontend to Netlify

### Option A: Using Netlify CLI (Recommended)

1. Install Netlify CLI:
   ```bash
   npm install -g netlify-cli
   ```

2. Login to Netlify:
   ```bash
   netlify login
   ```

3. Build and deploy:
   ```bash
   cd frontend
   npm run build
   netlify deploy --prod
   ```

4. Follow the prompts to create a new site

### Option B: Using Netlify Dashboard

1. Go to https://app.netlify.com
2. Click "Add new site" → "Import an existing project"
3. Connect your GitHub repository
4. Configure:
   - **Build command**: `npm run build`
   - **Publish directory**: `dist`
5. Click "Deploy site"

### Update Frontend Environment Variable

After backend deployment, update `frontend/.env.production`:

```env
VITE_API_BASE_URL=https://YOUR-BACKEND-URL.onrender.com/api
```

Then redeploy the frontend.

## Step 4: Configure CORS and WebSocket

The backend is already configured with:
- CORS enabled for all origins
- Socket.IO with polling fallback (WebSocket may not work on Render free tier)

If you encounter WebSocket issues, the app will automatically fall back to HTTP polling.

## Step 5: Test the Deployment

1. Open your Netlify frontend URL
2. Upload a resume
3. Connect to Naukri
4. Start automation
5. Verify real-time updates work

## Important Notes

### Render Free Tier Limitations

- **No WebSocket support**: The app uses HTTP polling as fallback
- **Sleeps after 15 minutes of inactivity**: Browser automation will not work on the free tier
- **512 MB RAM**: May be insufficient for Playwright browser automation
- **No persistent storage**: Data is lost when the service spins down (every 15 minutes of inactivity)
- **Limited to 750 hours/month**: May hit limit if service stays awake

### Recommended Production Setup

For production use, consider:
1. **Render Starter Plan** ($7/month): Keeps server awake, supports WebSocket
2. **Or use a VPS** (DigitalOcean, AWS Lightsail): Full control, cheaper for long-running processes

### Browser Automation in Production

Browser automation (Playwright) requires:
- Running server (no sleep)
- Sufficient RAM
- Chromium browser installed

The current setup is suitable for:
- Testing and development
- Short automation runs
- Manual triggering

For continuous automation, consider:
- Using a cron job or scheduler
- Running on a VPS with 24/7 uptime
- Implementing a queue system

## Troubleshooting

### Backend deployment fails

- Check Render logs for errors
- Ensure `requirements.txt` is up to date
- Verify Playwright installation: `playwright install chromium`

### Frontend can't connect to backend

- Verify backend URL in `.env.production`
- Check CORS configuration in `backend/app.py`
- Ensure backend is running

### WebSocket connection fails

- Check if you're on Render free tier (no WebSocket support)
- The app should fall back to HTTP polling automatically
- Verify Socket.IO configuration in `backend/app.py`

### Automation doesn't start

- Check if server is awake (Render free tier sleeps)
- Verify Playwright is installed: `playwright install chromium`
- Check backend logs for errors

### Data not persisting

- This is expected on Render free tier - data is lost when service spins down
- Consider upgrading to Render Starter Plan ($7/month) for persistent storage
- Or use external database/storage services

## Monitoring

### Render

- View logs in Render dashboard
- Set up alerts for service health
- Monitor resource usage

### Netlify

- View deploy logs in Netlify dashboard
- Monitor site performance
- Set up form submissions (if needed)

## Cost Estimate

### Render (Free Tier)
- $0/month
- 512 MB RAM
- 0.1 CPU
- Sleeps after 15 minutes inactivity
- **No persistent storage** (data lost on spin-down)
- **No disks** (paid feature only)

### Render (Starter Plan - Recommended for production)
- $7/month
- 512 MB RAM
- 0.5 CPU
- No sleep
- WebSocket support

### Netlify (Free Tier)
- $0/month
- 100 GB bandwidth
- 300 GB build minutes
- Free SSL

## Security Notes

1. **Never commit `.env` file** to GitHub
2. **Use environment variables** for all secrets
3. **Enable HTTPS** (both Render and Netlify provide free SSL)
4. **Add rate limiting** (already configured in backend)
5. **Validate all inputs** (already implemented)
6. **Regular security updates**: Keep dependencies updated

## Support

For issues:
- Check Render documentation: https://render.com/docs
- Check Netlify documentation: https://docs.netlify.com
- Review backend logs in Render dashboard
- Review frontend build logs in Netlify dashboard
