# ASTRO ENGINE - DEPLOYMENT INSTRUCTIONS
## Ready to Deploy to DigitalOcean App Platform

**Status:** ✅ **ALL PREREQUISITES COMPLETE**
**Date:** October 28, 2025

---

## ⚠️ **GITHUB AUTHENTICATION REQUIRED**

The deployment requires connecting your GitHub account to DigitalOcean.

### **Steps to Deploy:**

#### **Option 1: Deploy via DigitalOcean Console (Recommended)**

**Step 1: Connect GitHub**
```
1. Go to: https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Choose "GitHub" as source
4. Click "Authorize DigitalOcean" (if not already connected)
5. Authorize access to your repositories
```

**Step 2: Select Repository**
```
1. Select repository: Astro-Engine/Astro_Engine_ORGNL
2. Select branch: main
3. Auto-deploy: ✅ Enable (deploys on git push)
```

**Step 3: Import Spec**
```
1. Click "Edit App Spec"
2. Click "Import from file"
3. Upload: .do/app.yaml
4. Or copy/paste the contents
```

**Step 4: Review & Create**
```
1. Review configuration
2. Click "Create Resources"
3. Wait 10-15 minutes for deployment
```

---

#### **Option 2: CLI Deployment (After GitHub Connected)**

**Step 1: Connect GitHub via Console**
```
Visit: https://cloud.digitalocean.com/apps
Click "Manage" → "Settings" → "Source Control"
Connect GitHub account
```

**Step 2: Deploy via CLI**
```bash
cd "/Users/gouthamk/APPS/Astro Engine/Astro_Engine"
doctl apps create --spec .do/app.yaml
```

---

## 📋 **POST-DEPLOYMENT CONFIGURATION**

### **Immediately After Deployment (Required):**

**1. Set API Keys (CRITICAL)**
```
Console: Apps → astro-engine → Settings → Environment Variables
Update: VALID_API_KEYS
Value: (The 4 API keys generated - see docs/API_KEY_MANAGEMENT.md)
Format: key1,key2,key3,key4
```

**2. Set SECRET_KEY (CRITICAL)**
```
Generate:
  openssl rand -hex 32

Set in Console:
  Environment Variables → SECRET_KEY
  Value: [paste generated key]
```

**3. Verify Deployment**
```bash
# Get app URL
APP_URL=$(doctl apps list --format DefaultIngress --no-header)

# Test health
curl $APP_URL/health

# Should return:
# {"status":"healthy","components":{...}}
```

---

## 🔧 **DEPLOYMENT CONFIGURATION**

### **Current Setup:**

```yaml
Name: astro-engine
Region: Bangalore, India (blr)
Instance: basic-xxs (512MB, $5/month)
Redis: 1GB ($15/month)
Total: $20/month

GitHub:
  Repository: Astro-Engine/Astro_Engine_ORGNL
  Branch: main
  Auto-deploy: Enabled

Health Check:
  Path: /health
  Interval: 10 seconds
  Timeout: 5 seconds
```

---

## ✅ **VERIFICATION CHECKLIST**

**Before Deployment:**
- ✅ doctl authenticated
- ✅ App spec validated
- ✅ GitHub repository exists
- ⏳ GitHub connected to DigitalOcean (do via console)

**After Deployment:**
- ⏳ App status: ACTIVE
- ⏳ Health check: Passing
- ⏳ API keys configured
- ⏳ SECRET_KEY set
- ⏳ Redis connected

---

## 🚀 **READY TO DEPLOY**

**Use Console Method (Recommended):**
https://cloud.digitalocean.com/apps

**All configuration files are ready!**

---

**Prepared by:** Claude Code
**Date:** October 28, 2025
**Status:** ✅ READY (GitHub auth needed)
