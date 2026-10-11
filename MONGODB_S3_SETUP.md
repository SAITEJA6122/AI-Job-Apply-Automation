# MongoDB Atlas + AWS S3 Setup Guide

This guide explains how to set up MongoDB Atlas and AWS S3 for persistent data storage on free tier.

## Overview

- **MongoDB Atlas**: Free tier database (512 MB, always on)
- **AWS S3**: Free tier storage (5 GB, 20,000 requests/month)
- **Total Cost**: $0/month
- **Suitable for**: 3 users, persistent data, full workflow

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

## Part 2: AWS S3 Setup

### Step 1: Create AWS Account

1. Go to https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Follow the signup process
4. You'll need:
   - Email address
   - Phone number (for verification)
   - Credit card (required, but won't be charged for free tier)

**Note:** AWS requires a credit card for verification, but you won't be charged for free tier usage.

### Step 2: Create S3 Bucket

1. After login, go to https://console.aws.amazon.com/s3/
2. Click "Create bucket"
3. Configure:
   - **Bucket name**: `naukri-automation-unique-name` (must be globally unique)
   - **Region**: Choose closest to your MongoDB Atlas region
   - **Block Public Access settings**: Uncheck all (for now)
4. Click "Create bucket"

### Step 3: Configure Bucket Permissions

1. Click on your bucket name
2. Go to "Permissions" tab
3. In "Block Public Access" section, click "Edit"
4. Uncheck "Block all public access"
5. Click "Save"

**Important:** For production, use presigned URLs instead of public access.

### Step 4: Create IAM User for Programmatic Access

1. Go to https://console.aws.amazon.com/iam/
2. Click "Users" in left sidebar
3. Click "Add users"
4. Configure:
   - **User name**: `naukri-automation`
   - **Select AWS credential type**: Access key - Programmatic access
5. Click "Next: Permissions"
6. Click "Attach existing policies directly"
7. Search for "S3" and select:
   - `AmazonS3FullAccess` (for simplicity)
   - Or create custom policy with limited permissions
8. Click "Next: Tags" (skip)
9. Click "Next: Review"
10. Click "Create user"

### Step 5: Save AWS Credentials

1. After creating user, you'll see:
   - **Access key ID** (save this!)
   - **Secret access key** (save this - shown only once!)
2. Download the CSV file with credentials
3. Store credentials securely

**Important:** You cannot retrieve the secret access key later. Save it now!

### Step 6: Test S3 Access (Optional)

1. Install AWS CLI or boto3:
   ```bash
   pip install boto3
   ```

2. Create test file:
   ```python
   import boto3
   
   s3 = boto3.client(
       's3',
       aws_access_key_id='YOUR_ACCESS_KEY',
       aws_secret_access_key='YOUR_SECRET_KEY',
       region_name='us-east-1'
   )
   
   # Test upload
   try:
       s3.put_object(
           Bucket='your-bucket-name',
           Key='test.txt',
           Body='Hello from S3!'
       )
       print("Successfully uploaded to S3!")
   except Exception as e:
       print(f"Upload failed: {e}")
   ```

3. Run: `python test_s3.py`

---

## Part 3: Configure Environment Variables

### Local Development (.env)

Create or update `.env` in project root:

```env
# MongoDB Atlas
MONGODB_URI=mongodb+srv://naukri-admin:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/naukri_automation?retryWrites=true&w=majority
MONGODB_DATABASE=naukri_automation

# AWS S3
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# LLM API Keys
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
| `AWS_ACCESS_KEY_ID` | Your AWS access key | S3 authentication |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key | S3 authentication |
| `AWS_REGION` | `us-east-1` | AWS region |
| `S3_BUCKET_NAME` | Your bucket name | S3 bucket |
| `GROQ_API_KEY` | Your Groq API key | LLM API |

4. Click "Save Changes"
5. Deploy service again

---

## Part 4: Verify Setup

### Test MongoDB Connection

1. Update `.env` with your credentials
2. Run backend locally:
   ```bash
   python backend/app.py
   ```
3. Check logs for: "Connected to MongoDB: naukri_automation"

### Test S3 Connection

1. Check logs for: "Connected to S3 bucket: your-bucket-name"
2. Upload a resume in the frontend
3. Check if file appears in S3 bucket

### Test Full Workflow

1. Upload resume
2. Approve data
3. Connect to Naukri
4. Start automation
5. Check MongoDB for data persistence
6. Check S3 for file storage

---

## Part 5: Troubleshooting

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

### AWS S3 Issues

**Error: "AccessDenied"**
- Verify IAM user has S3 permissions
- Check bucket permissions
- Ensure region matches

**Error: "NoCredentialsError"**
- Verify AWS credentials are correct
- Check environment variables
- Ensure no typos in keys

**Error: "Bucket not found"**
- Verify bucket name is correct
- Check region matches
- Ensure bucket exists

### General Issues

**Backend won't start**
- Check all environment variables are set
- Verify MongoDB and S3 credentials
- Check backend logs for specific errors

**Data not persisting**
- Verify MongoDB connection is working
- Check S3 uploads are succeeding
- Review backend logs for errors

---

## Part 6: Security Best Practices

### MongoDB Atlas

1. **Use strong passwords** for database users
2. **Limit IP whitelist** to specific IPs in production
3. **Enable data encryption** (MongoDB Atlas provides by default)
4. **Enable audit logging** for production
5. **Regular backups** (MongoDB Atlas provides automated backups)

### AWS S3

1. **Use IAM roles** instead of access keys when possible
2. **Rotate access keys** regularly
3. **Enable bucket versioning** to prevent accidental deletions
4. **Use presigned URLs** instead of public access
5. **Enable server-side encryption**
6. **Set up bucket policies** for restricted access

### General

1. **Never commit credentials** to GitHub
2. **Use environment variables** for all secrets
3. **Rotate credentials** periodically
4. **Monitor usage** to stay within free tier limits
5. **Set up alerts** for unusual activity

---

## Part 7: Cost Monitoring

### MongoDB Atlas Free Tier

- **Storage**: 512 MB
- **Operations**: Unlimited
- **Uptime**: 99.9%
- **Duration**: Forever (no time limit)

**Monitor at:** https://cloud.mongodb.com/v2/#/metrics

### AWS S3 Free Tier

- **Storage**: 5 GB
- **Requests**: 20,000 per month
- **Data transfer**: 100 GB per month
- **Duration**: First 12 months

**Monitor at:** https://console.aws.amazon.com/billing/

### Estimated Usage for 3 Users

| Resource | Estimated Usage | Free Tier Limit | % Used |
|----------|------------------|-----------------|--------|
| MongoDB Storage | ~6 MB | 512 MB | 1.2% |
| S3 Storage | ~156 MB | 5 GB | 3% |
| S3 Requests | ~5,000/month | 20,000/month | 25% |

**You'll be well within free tier limits!**

---

## Part 8: Next Steps

After completing this setup:

1. ✅ Update `.env` with your credentials
2. ✅ Test backend locally with MongoDB + S3
3. ✅ Deploy to Render with environment variables
4. ✅ Test full workflow on deployed backend
5. ✅ Monitor usage in MongoDB Atlas and AWS consoles

**Your application is now ready for production on free tier!** 🎉

---

## Need Help?

- MongoDB Atlas Support: https://www.mongodb.com/docs/atlas/
- AWS S3 Documentation: https://docs.aws.amazon.com/s3/
- Render Documentation: https://render.com/docs
