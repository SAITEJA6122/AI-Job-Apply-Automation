# MongoDB Atlas Setup Guide (Simplified)

This guide explains how to set up MongoDB Atlas for persistent data storage on free tier.

## Overview

- **MongoDB Atlas**: Free tier database (512 MB, always on)
- **GridFS**: Built-in file storage for resumes and screenshots
- **Total Cost**: $0/month
- **Suitable for**: 3 users, ~212 MB storage (resumes + screenshots)
- **No AWS S3 needed!**

---

## Part 1: MongoDB Atlas Setup

### Step 1: Create MongoDB Atlas Account

1. Go to https://www.mongodb.com/cloud/atlas
2. Click "Try Free"
3. Sign up with email or Google account
4. Verify your email address

### Step 2: Create a Free Cluster

1. After login, click "Build a Database"
2. Select "M0" (Free Tier) - 512 MB storage
3. Choose a cloud provider and region (closest to you)
   - Recommended: AWS, Region closest to your location
4. Enter cluster name (e.g., `naukri-automation`)
5. Click "Create"

**Wait time:** Cluster creation takes 2-5 minutes

### Step 3: Create Database User

1. Click "Database Access" in left sidebar
2. Click "Add New Database User"
3. Configure:
   - **Username**: `naukri-admin` (or your choice)
   - **Password**: Generate a strong password (save this!)
   - **Database User Privileges**: Read and write to any database
4. Click "Create User"

**Important:** Save the username and password securely!

### Step 4: Whitelist IP Addresses

1. Click "Network Access" in left sidebar
2. Click "Add IP Address"
3. Select "Allow Access from Anywhere" (0.0.0.0/0)
   - This allows Render to connect from any IP
4. Click "Confirm"

**Note:** For production, use specific Render IPs instead of 0.0.0.0/0

### Step 5: Get Connection String

1. Click "Database" in left sidebar
2. Click "Connect" button
3. Select "Connect your application"
4. Select driver: Python
5. Copy the connection string

**Example connection string:**
```
mongodb+srv://naukri-admin:PASSWORD@cluster0.xxxxx.mongodb.net/naukri_automation?retryWrites=true&w=majority
```

**Replace `PASSWORD` with your actual password.**

### Step 6: Test Connection (Optional)

1. In your project root, create a test file:
   ```python
   from pymongo import MongoClient
   
   uri = "mongodb+srv://naukri-admin:PASSWORD@cluster0.xxxxx.mongodb.net/naukri_automation?retryWrites=true&w=majority"
   client = MongoClient(uri)
   
   # Test connection
   try:
       client.admin.command('ping')
       print("Successfully connected to MongoDB!")
   except Exception as e:
       print(f"Connection failed: {e}")
   ```

2. Run: `python test_mongodb.py`

---

## Part 2: Configure Environment Variables

### Local Development (.env)

Create or update `.env` in project root:

```env
# MongoDB Atlas (Required)
MONGODB_URI=mongodb+srv://naukri-admin:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/naukri_automation?retryWrites=true&w=majority
MONGODB_DATABASE=naukri_automation

# LLM API Key (Required - at least one)
GROQ_API_KEY=your-groq-api-key-here
```

### Render Deployment

After deploying to Render:

1. Go to your service in Render dashboard
2. Click "Environment" tab
3. Add the following environment variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `MONGODB_URI` | Your MongoDB connection string | Database connection |
| `MONGODB_DATABASE` | `naukri_automation` | Database name |
| `GROQ_API_KEY` | Your Groq API key | LLM API |

4. Click "Save Changes"
5. Deploy service again

---

## Part 3: Storage Details

### What Gets Stored in MongoDB

| Data Type | Storage Method | Size (3 users) |
|-----------|---------------|----------------|
| User profiles | MongoDB documents | ~1 MB |
| Sessions | MongoDB documents | ~1 MB |
| Application state | MongoDB documents | ~2 MB |
| Statistics | MongoDB documents | ~1 MB |
| Resumes | MongoDB GridFS | ~6 MB |
| Screenshots | MongoDB GridFS | ~200 MB |
| **Total** | **MongoDB only** | **~211 MB** |

### MongoDB Free Tier Limits

- **Storage**: 512 MB
- **Operations**: Unlimited
- **Uptime**: 99.9%
- **Duration**: Forever (no time limit)

### Your Usage

- **Estimated**: 211 MB
- **Limit**: 512 MB
- **Usage**: 41%
- **Remaining**: 301 MB

**You'll be well within free tier limits!**

---

## Part 4: Automatic Cleanup

### 12-Hour Expiration

All data automatically expires after 12 hours:
- ✅ Sessions expire after 12 hours
- ✅ Resumes expire after 12 hours
- ✅ Screenshots expire after 12 hours
- ✅ Automatic cleanup of expired data

### Scheduled Daily Cleanup (9 AM UTC)

The backend automatically runs cleanup every day at **9 AM UTC**:
- ✅ Deletes all expired sessions
- ✅ Deletes all expired resumes
- ✅ Deletes all expired screenshots
- ✅ Deletes associated GridFS files
- ✅ Runs automatically - no manual intervention needed

### Manual Cleanup

You can also manually trigger cleanup:
- Disconnect Naukri account (deletes all user data immediately)
- Use `/api/session/cleanup` endpoint to trigger cleanup manually
- Backend automatically runs cleanup tasks periodically

---

## Part 5: Verify Setup

### Test MongoDB Connection

1. Update `.env` with your credentials
2. Run backend locally:
   ```bash
   python backend/app.py
   ```
3. Check logs for: "Connected to MongoDB: naukri_automation"

### Test Full Workflow

1. Upload resume
2. Approve data
3. Connect to Naukri
4. Start automation
5. Check MongoDB for data persistence
6. Verify screenshots are stored

---

## Part 6: Troubleshooting

### MongoDB Atlas Issues

**Error: "Authentication failed"**
- Check username and password in connection string
- Ensure password doesn't contain special characters that need URL encoding
- Verify user has correct permissions

**Error: "Connection timeout"**
- Check IP whitelist (0.0.0.0/0)
- Verify firewall allows MongoDB ports
- Try different region

**Error: "Invalid connection string"**
- Ensure connection string format is correct
- Remove `< >` placeholders
- Check for typos in cluster name

### Storage Issues

**Error: "GridFS upload failed"**
- Verify MongoDB connection is working
- Check if file is not too large (MongoDB limit: 16 MB per file)
- Review backend logs for specific errors

**Data not persisting**
- Verify MongoDB connection is working
- Check that environment variables are set correctly
- Review backend logs for errors

---

## Part 7: Security Best Practices

### MongoDB Atlas

1. **Use strong passwords** for database users
2. **Limit IP whitelist** to specific IPs in production
3. **Enable data encryption** (MongoDB Atlas provides by default)
4. **Enable audit logging** for production
5. **Regular backups** (MongoDB Atlas provides automated backups)

### General

1. **Never commit credentials** to GitHub
2. **Use environment variables** for all secrets
3. **Rotate credentials** periodically
4. **Monitor usage** to stay within free tier limits
5. **Set up alerts** for unusual activity

---

## Part 8: Cost Monitoring

### MongoDB Atlas Free Tier

- **Storage**: 512 MB
- **Operations**: Unlimited
- **Uptime**: 99.9%
- **Duration**: Forever (no time limit)

**Monitor at:** https://cloud.mongodb.com/v2/#/metrics

### Estimated Usage for 3 Users

| Resource | Estimated Usage | Free Tier Limit | % Used |
|----------|------------------|-----------------|--------|
| MongoDB Storage | ~211 MB | 512 MB | 41% |

**You'll be well within free tier limits!**

---

## Part 9: Next Steps

After completing this setup:

1. ✅ Update `.env` with your MongoDB connection string
2. ✅ Test backend locally with MongoDB
3. ✅ Deploy to Render with environment variables
4. ✅ Test full workflow on deployed backend
5. ✅ Monitor usage in MongoDB Atlas console

**Your application is now ready for production on free tier!** 🎉

---

## Part 10: No AWS S3 Needed!

**You don't need AWS S3!** MongoDB GridFS handles everything:
- ✅ Resume storage
- ✅ Screenshot storage
- ✅ Automatic cleanup
- ✅ All in one database
- ✅ Simpler setup
- ✅ Fewer credentials

**One database, everything you need!**

---

## Need Help?

- MongoDB Atlas Support: https://www.mongodb.com/docs/atlas/
- Render Documentation: https://render.com/docs
