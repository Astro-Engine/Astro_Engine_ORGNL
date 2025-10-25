# DigitalOcean App Platform Deployment Guide
## Complete CLI Deployment for Astro Engine

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Detailed Deployment Steps](#detailed-deployment-steps)
5. [Post-Deployment](#post-deployment)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)
8. [Cost Breakdown](#cost-breakdown)

---

## 🎯 Overview

This guide will help you deploy Astro Engine to DigitalOcean App Platform using the CLI (`doctl`).

**What you get:**
- ✅ Auto-scaling (1-5 instances)
- ✅ Managed Redis cache (1GB)
- ✅ Automatic HTTPS/SSL
- ✅ Built-in load balancing
- ✅ GitHub auto-deploy
- ✅ Zero-downtime deployments
- ✅ Built-in monitoring

**Estimated monthly cost:** $39-156/month depending on traffic

---

## 🔧 Prerequisites

### 1. DigitalOcean Account

Create an account at: https://www.digitalocean.com/

### 2. Install `doctl` (DigitalOcean CLI)

**macOS:**
```bash
brew install doctl
```

**Linux (Ubuntu/Debian):**
```bash
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.98.1/doctl-1.98.1-linux-amd64.tar.gz
tar xf doctl-1.98.1-linux-amd64.tar.gz
sudo mv doctl /usr/local/bin
```

**Linux (via snap):**
```bash
sudo snap install doctl
```

**Windows:**
Download from: https://github.com/digitalocean/doctl/releases

**Verify installation:**
```bash
doctl version
```

### 3. Authenticate `doctl`

```bash
# Initialize authentication
doctl auth init

# You'll be prompted for your API token
# Get it from: https://cloud.digitalocean.com/account/api/tokens

# Verify authentication
doctl account get
```

### 4. Prepare Your Repository

```bash
# Ensure all changes are committed
cd "/Users/gouthamk/APPS/Astro Engine/Astro_Engine"
git status

# If you have uncommitted changes:
git add -A
git commit -m "Prepare for DigitalOcean deployment"
git push origin main
```

---

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)

```bash
# Validate configuration
./deploy-digitalocean.sh --validate

# Create new app
./deploy-digitalocean.sh --create

# Follow the prompts and save the App ID!
```

### Option 2: Manual CLI Deployment

```bash
# 1. Validate spec file
doctl apps spec validate .do/app.yaml

# 2. Create the app
doctl apps create --spec .do/app.yaml

# 3. Get the App ID from output and save it
# App ID will look like: a1b2c3d4-5678-90ab-cdef-1234567890ab
```

---

## 📝 Detailed Deployment Steps

### Step 1: Validate Configuration

```bash
# Check if YAML is valid
./deploy-digitalocean.sh --validate
```

**Expected output:**
```
========================================
Checking Prerequisites
========================================
✅ doctl CLI found
✅ doctl authenticated
✅ Spec file found: .do/app.yaml
✅ Prerequisites check complete

========================================
Validating App Specification
========================================
✅ YAML syntax valid
✅ DigitalOcean spec validation passed
✅ Validation complete
```

### Step 2: Generate SECRET_KEY

```bash
# Generate a random secret key
./deploy-digitalocean.sh --secret
```

**Save the generated key!** You'll need it in Step 4.

Example output:
```
ℹ️  Generating random SECRET_KEY...
✅ SECRET_KEY generated (save this!)
SECRET_KEY=a1b2c3d4e5f6...your-64-char-hex-key...
```

### Step 3: Create the App

```bash
# Create the app
./deploy-digitalocean.sh --create
```

**What happens:**
1. Validates configuration
2. Creates app on DigitalOcean
3. Connects to your GitHub repository
4. Creates managed Redis database
5. Starts initial deployment

**Save the App ID!** It will be shown in the output and saved to `.do/app_id.txt`

Example:
```
✅ App created successfully!
✅ App ID: a1b2c3d4-5678-90ab-cdef-1234567890ab
```

### Step 4: Update SECRET_KEY in App Platform

**Via Web UI (Easiest):**
1. Go to https://cloud.digitalocean.com/apps
2. Click on your app (astro-engine)
3. Go to "Settings" → "App-Level Environment Variables"
4. Find `SECRET_KEY`
5. Click "Edit"
6. Paste your generated SECRET_KEY
7. Click "Save"
8. App will automatically redeploy

**Via CLI:**
```bash
# Set your App ID
APP_ID="your-app-id-here"

# Update SECRET_KEY
doctl apps update $APP_ID --spec .do/app.yaml

# Note: You'll need to edit .do/app.yaml first to add the real SECRET_KEY
```

### Step 5: Monitor Deployment

```bash
# Get app details
doctl apps get <APP_ID>

# Watch build logs (live)
doctl apps logs <APP_ID> --type BUILD --follow

# Watch runtime logs (live)
doctl apps logs <APP_ID> --type RUN --follow

# Check deployment status
doctl apps list
```

**Deployment stages:**
1. 🔵 **Building** (5-10 minutes)
   - Cloning repository
   - Building Docker image
   - Installing dependencies
2. 🟡 **Deploying** (2-3 minutes)
   - Starting containers
   - Health checks
   - Load balancer setup
3. 🟢 **Active** (Ready!)
   - App is live and serving traffic

### Step 6: Get Your App URL

```bash
# Get app details
doctl apps get <APP_ID>

# Look for "Live URL" in the output
# Example: https://astro-engine-xxxxx.ondigitalocean.app
```

### Step 7: Test Your Deployment

```bash
# Set your app URL
APP_URL="https://astro-engine-xxxxx.ondigitalocean.app"

# Test health endpoint
curl $APP_URL/health

# Expected response:
# {"status":"healthy","version":"1.3.0",...}

# Test metrics endpoint
curl $APP_URL/metrics

# Test a calculation endpoint
curl -X POST $APP_URL/lahiri/natal \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "Test User",
    "birth_date": "1990-05-15",
    "birth_time": "14:30:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timezone_offset": 5.5
  }'
```

---

## 🎉 Post-Deployment

### Configure Custom Domain (Optional)

**Via Web UI:**
1. Go to https://cloud.digitalocean.com/apps
2. Click on your app
3. Go to "Settings" → "Domains"
4. Click "Add Domain"
5. Enter your domain (e.g., api.yourdomain.com)
6. Follow DNS configuration instructions

**Via CLI:**
```bash
# Add custom domain
doctl apps create-domain <APP_ID> \
  --domain api.yourdomain.com \
  --zone yourdomain.com
```

### Enable Auto-Deploy from GitHub

Already configured in `.do/app.yaml`!

Every time you push to `main` branch, the app automatically redeploys.

To disable:
1. Edit `.do/app.yaml`
2. Change `deploy_on_push: true` to `deploy_on_push: false`
3. Update app: `./deploy-digitalocean.sh --update`

### Set Up Monitoring Alerts

**Via Web UI:**
1. Go to your app in DigitalOcean
2. Click "Insights" tab
3. Set up alerts for:
   - CPU usage > 80%
   - Memory usage > 80%
   - Request errors > 5%
   - Deployment failures

---

## 📊 Monitoring & Maintenance

### View Logs

```bash
# Real-time logs
doctl apps logs <APP_ID> --type RUN --follow

# Build logs
doctl apps logs <APP_ID> --type BUILD

# Last 100 lines
doctl apps logs <APP_ID> --type RUN --tail 100
```

### Check App Status

```bash
# App overview
doctl apps get <APP_ID>

# List all apps
doctl apps list

# App spec
doctl apps spec get <APP_ID>
```

### Monitor Performance

```bash
# Get your app URL
APP_URL=$(doctl apps get <APP_ID> --format LiveURL --no-header)

# Check metrics
curl $APP_URL/metrics

# Check cache stats
curl $APP_URL/cache/stats

# Check health
curl $APP_URL/health
```

### Update App Configuration

```bash
# Edit .do/app.yaml as needed
vim .do/app.yaml

# Validate changes
doctl apps spec validate .do/app.yaml

# Apply updates
./deploy-digitalocean.sh --update
```

### Scale Up/Down

**Edit `.do/app.yaml`:**
```yaml
autoscaling:
  min_instance_count: 2  # Increase minimum
  max_instance_count: 10  # Increase maximum
```

**Apply:**
```bash
./deploy-digitalocean.sh --update
```

### Update Environment Variables

**Via CLI:**
```bash
# Edit .do/app.yaml to update env vars
# Then update the app
./deploy-digitalocean.sh --update
```

**Via Web UI:**
1. Go to app settings
2. Click "Environment Variables"
3. Edit values
4. Save (auto-redeploys)

---

## 🔧 Troubleshooting

### Deployment Fails

```bash
# Check build logs
doctl apps logs <APP_ID> --type BUILD

# Common issues:
# 1. pyswisseph build fails → Already fixed with g++ in Dockerfile
# 2. Redis connection fails → Check REDIS_URL is set
# 3. Health check fails → Check /health endpoint works
```

### App Not Responding

```bash
# Check app status
doctl apps get <APP_ID>

# Check runtime logs
doctl apps logs <APP_ID> --type RUN --tail 200

# Restart app
doctl apps create-deployment <APP_ID>
```

### Redis Connection Errors

```bash
# Check Redis database
doctl databases list

# Get Redis connection string
doctl databases connection <REDIS_DB_ID>

# Verify REDIS_URL is set in app
doctl apps get <APP_ID> | grep REDIS_URL
```

### High Memory Usage

```bash
# Check current usage
doctl apps get <APP_ID>

# Increase instance size in .do/app.yaml:
instance_size_slug: professional-s  # 4GB RAM instead of 2GB

# Update app
./deploy-digitalocean.sh --update
```

### Slow Performance

1. **Check cache status:**
```bash
curl $APP_URL/cache/stats
```

2. **Verify Redis is connected:**
- Should show `redis_available: true`

3. **Scale up if needed:**
- Increase `max_instance_count` in `.do/app.yaml`

---

## 💰 Cost Breakdown

### Current Configuration

**App Service (Professional XS):**
- 2GB RAM, 1 vCPU
- $24/month per instance
- Auto-scaling: 1-5 instances
- **Cost: $24-120/month** (based on traffic)

**Managed Redis (1GB):**
- $15/month
- Automatic backups
- High availability

**Total Estimated Cost:**
- **Minimum:** $39/month (1 instance + Redis)
- **Average:** $63-87/month (2-3 instances + Redis)
- **Peak:** $135/month (5 instances + Redis)

### Cost Optimization Tips

1. **Scale down minimum instances** (if low traffic):
```yaml
autoscaling:
  min_instance_count: 1  # Reduce to 1
```

2. **Use smaller Redis** (if needed):
```yaml
databases:
  - size: db-s-1vcpu-512mb  # $10/month instead of $15
```

3. **Monitor and adjust**:
- Check usage weekly
- Scale based on actual traffic
- Use alerts to prevent over-scaling

---

## 📚 Additional Resources

- **DigitalOcean App Platform Docs:** https://docs.digitalocean.com/products/app-platform/
- **doctl Reference:** https://docs.digitalocean.com/reference/doctl/
- **App Platform Pricing:** https://www.digitalocean.com/pricing/app-platform
- **Redis Pricing:** https://www.digitalocean.com/pricing/managed-databases

---

## ✅ Deployment Checklist

- [ ] doctl installed and authenticated
- [ ] Repository pushed to GitHub
- [ ] Configuration validated (`./deploy-digitalocean.sh --validate`)
- [ ] SECRET_KEY generated and saved
- [ ] App created (`./deploy-digitalocean.sh --create`)
- [ ] App ID saved
- [ ] SECRET_KEY updated in App Platform
- [ ] Deployment successful (check logs)
- [ ] Health endpoint tested
- [ ] API endpoints tested
- [ ] Custom domain configured (optional)
- [ ] Monitoring alerts set up
- [ ] Team notified of new URL

---

## 🆘 Support

If you encounter issues:

1. **Check logs:** `doctl apps logs <APP_ID> --type RUN --follow`
2. **Check DigitalOcean status:** https://status.digitalocean.com/
3. **Community:** https://www.digitalocean.com/community
4. **Support:** Open a ticket in DigitalOcean console

---

**Deployment prepared by:** Claude Code
**Last updated:** October 25, 2025
**Version:** 1.0.0
