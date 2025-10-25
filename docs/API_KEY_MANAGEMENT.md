# API Key Management Guide
## Astro Engine Authentication System

**Phase 1, Module 1.3:** API Key Configuration Management

---

## 🔑 API Key Registry

### Active API Keys

| Service | Service ID | Key Prefix | Status | Created | Last Rotated | Expires |
|---------|-----------|------------|--------|---------|--------------|---------|
| **Astro Corp Backend** | `corp_backend` | `astro_corp_backend_` | ✅ Active | 2025-10-25 | 2025-10-25 | 2026-01-23 (90 days) |
| **Astro Ratan (AI Agent)** | `astro_ratan` | `astro_astro_ratan_` | ✅ Active | 2025-10-25 | 2025-10-25 | 2026-01-23 |
| **Report Engine** | `report_engine` | `astro_report_engine_` | ✅ Active | 2025-10-25 | 2025-10-25 | 2026-01-23 |
| **Development/Testing** | `testing` | `astro_testing_` | ✅ Active | 2025-10-25 | 2025-10-25 | 2026-01-23 |

**IMPORTANT:** Actual API key values are NOT stored in this document. Keys are stored securely in:
1. DigitalOcean App Platform Secrets (production)
2. Team password manager (backup)
3. Secure key vault (if using one)

---

## 📋 API Key Format

### Structure
```
{prefix}_{service}_{random_32_chars}

Examples:
astro_corp_backend_Jj7WZL_wOWJMJFUxEamAbJKGA2L84FR4
astro_astro_ratan_KpBTYPkKY83US0_kIcr_-m70Ys7Q7rqc
```

### Components
- **Prefix:** `astro` (identifies Astro Engine keys)
- **Service:** Service identifier (e.g., `corp_backend`, `astro_ratan`)
- **Random:** 32 cryptographically secure random characters
- **Total Length:** ~50-65 characters

---

## 🔐 Security Best Practices

### DO:
- ✅ Store keys in environment variables or secrets manager
- ✅ Use HTTPS for all API calls
- ✅ Rotate keys every 90 days
- ✅ Use different keys for each service
- ✅ Include API key in X-API-Key header
- ✅ Monitor failed authentication attempts
- ✅ Revoke compromised keys immediately

### DON'T:
- ❌ Commit API keys to git
- ❌ Share keys in plain text email
- ❌ Reuse keys across services
- ❌ Send keys in URL query parameters (production)
- ❌ Log full API keys (always mask)
- ❌ Hard-code keys in source code

---

## 🚀 Usage Guide

### For API Consumers (Your Services)

#### **1. Astro Corp Backend**

```python
# Python Example
import requests

API_KEY = os.getenv('ASTRO_ENGINE_API_KEY')  # Load from environment
API_URL = 'https://your-app.ondigitalocean.app'

def calculate_natal_chart(user_data):
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }

    payload = {
        'user_name': user_data['name'],
        'birth_date': user_data['birth_date'],
        'birth_time': user_data['birth_time'],
        'latitude': user_data['latitude'],
        'longitude': user_data['longitude'],
        'timezone_offset': user_data['timezone_offset']
    }

    response = requests.post(
        f'{API_URL}/lahiri/natal',
        headers=headers,
        json=payload
    )

    if response.status_code == 401:
        # Invalid API key
        raise AuthenticationError("Invalid Astro Engine API key")

    if response.status_code == 429:
        # Rate limit exceeded
        raise RateLimitError("Astro Engine rate limit exceeded")

    return response.json()
```

#### **2. Astro Ratan (AI Agent)**

```javascript
// JavaScript/Node.js Example
const axios = require('axios');

const API_KEY = process.env.ASTRO_ENGINE_API_KEY;
const API_URL = 'https://your-app.ondigitalocean.app';

async function fetchNatalChart(userData) {
  try {
    const response = await axios.post(
      `${API_URL}/lahiri/natal`,
      {
        user_name: userData.name,
        birth_date: userData.birthDate,
        birth_time: userData.birthTime,
        latitude: userData.latitude,
        longitude: userData.longitude,
        timezone_offset: userData.timezoneOffset
      },
      {
        headers: {
          'X-API-Key': API_KEY,
          'Content-Type': 'application/json'
        }
      }
    );

    return response.data;
  } catch (error) {
    if (error.response?.status === 401) {
      throw new Error('Invalid Astro Engine API key');
    }
    throw error;
  }
}
```

#### **3. cURL Example (Testing)**

```bash
# Set your API key
export ASTRO_API_KEY="astro_testing_gcxfZNriE1W5AlvDvdyXJNVv6y1KBYNG"

# Make request
curl -X POST https://your-app.ondigitalocean.app/lahiri/natal \
  -H "X-API-Key: $ASTRO_API_KEY" \
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

## 🔄 Key Rotation Process

### When to Rotate:
- Every 90 days (scheduled)
- When team member with key access leaves
- When key is suspected to be compromised
- After security incident

### How to Rotate:

#### **Step 1: Generate New Keys**
```bash
cd "/Users/gouthamk/APPS/Astro Engine/Astro_Engine"
source venv/bin/activate

python3 -c "
from astro_engine.auth_manager import generate_api_key
services = ['corp_backend', 'astro_ratan', 'report_engine', 'testing']
for svc in services:
    print(f'{svc}: {generate_api_key(svc)}')
"
```

#### **Step 2: Update DigitalOcean Secrets**
```bash
# Via DigitalOcean Web UI:
1. Go to App Platform → Your App → Settings
2. Click "Environment Variables"
3. Edit VALID_API_KEYS
4. Add NEW keys alongside OLD keys (both valid temporarily)
5. Save (app will redeploy)

# Via CLI:
doctl apps update <APP_ID> --spec .do/app.yaml
# (After updating VALID_API_KEYS in app.yaml)
```

#### **Step 3: Distribute New Keys**
```
Send new keys securely to each service team:
- Astro Corp Backend team → corp_backend key
- Astro Ratan team → astro_ratan key
- Report Engine team → report_engine key

Use secure channels:
✅ Encrypted email
✅ Password-protected document
✅ Slack DM (not public channels)
✅ Secrets management system
```

#### **Step 4: Grace Period**
```
Wait 7 days with BOTH old and new keys valid
- Allows teams time to update
- Monitor which services updated (check logs)
- Confirm all services using new keys
```

#### **Step 5: Revoke Old Keys**
```
After grace period:
1. Remove old keys from VALID_API_KEYS
2. Update in DigitalOcean
3. App redeploys
4. Old keys now invalid
5. Monitor for any services still using old keys (will get 401 errors)
```

---

## 🚨 Emergency Key Revocation

### If Key is Compromised:

#### **Immediate Actions (Within 1 Hour):**
1. **Remove compromised key from VALID_API_KEYS immediately**
2. **Update DigitalOcean App Platform** (triggers redeploy)
3. **Generate new key for affected service**
4. **Notify affected service team**
5. **Monitor for unauthorized usage attempts**

#### **DigitalOcean Web UI (Fastest):**
```
1. Login to DigitalOcean
2. Apps → Astro Engine → Settings
3. Environment Variables → VALID_API_KEYS → Edit
4. Remove compromised key
5. Save (auto-redeploys in ~3 minutes)
```

#### **CLI Method:**
```bash
# Edit .do/app.yaml to remove key
# Then update app
doctl apps update <APP_ID> --spec .do/app.yaml
```

---

## 📊 Monitoring & Alerts

### Failed Authentication Alerts

Set up alerts for:
- ✅ > 10 failed auth attempts in 5 minutes (potential attack)
- ✅ Failed auth from new IP address
- ✅ Unusual authentication patterns

### Queries:

**Check failed authentications (last hour):**
```
# View logs
doctl apps logs <APP_ID> --type RUN | grep "auth_failed"

# Check metrics
curl https://your-app.ondigitalocean.app/metrics | grep auth_failures_total
```

**Check which services are authenticated:**
```
# View successful auth by service
doctl apps logs <APP_ID> --type RUN | grep "auth_success" | grep -o "service.*"
```

---

## 🔧 Troubleshooting

### Issue: "Invalid API key" errors

**Symptoms:**
- Requests return 401 Unauthorized
- Error message: "Valid API key required"

**Causes & Solutions:**

1. **Missing X-API-Key header**
   ```python
   # ❌ Wrong
   requests.post(url, json=data)

   # ✅ Correct
   requests.post(url, json=data, headers={'X-API-Key': key})
   ```

2. **Wrong API key used**
   - Verify key matches one in VALID_API_KEYS
   - Check for typos
   - Verify no extra whitespace

3. **Key not yet active**
   - Wait 2-3 minutes after updating DigitalOcean
   - App needs to redeploy

4. **AUTH_REQUIRED=true but key not configured**
   - Check DigitalOcean environment variables
   - Verify VALID_API_KEYS is set

### Issue: Authentication disabled warnings

**Symptoms:**
- Logs show "authentication disabled"
- No authentication enforced

**Solution:**
```bash
# Check configuration
doctl apps get <APP_ID> | grep -E "(AUTH_REQUIRED|VALID_API_KEYS)"

# Should show:
# AUTH_REQUIRED: true
# VALID_API_KEYS: (set)
```

---

## 📝 For Service Teams

### **Astro Corp Backend Team**

**Your API Key:** (Provided separately via secure channel)

**Integration:**
1. Store key in environment variable: `ASTRO_ENGINE_API_KEY`
2. Include in every Astro Engine request: `X-API-Key: {your_key}`
3. Handle 401 errors (invalid key)
4. Handle 429 errors (rate limit)

**Rate Limit:** 5,000 requests/hour

### **Astro Ratan Team**

**Your API Key:** (Provided separately)

**Integration:** Same as above

**Rate Limit:** 2,000 requests/hour

### **Report Engine Team**

**Your API Key:** (Provided separately)

**Rate Limit:** 1,000 requests/hour

---

## 📅 Key Rotation Schedule

| Service | Current Key Created | Next Rotation Due | Rotation Contact |
|---------|---------------------|-------------------|------------------|
| Corp Backend | 2025-10-25 | 2026-01-23 | backend-team@example.com |
| Astro Ratan | 2025-10-25 | 2026-01-23 | ai-team@example.com |
| Report Engine | 2025-10-25 | 2026-01-23 | reports-team@example.com |
| Testing | 2025-10-25 | 2026-01-23 | dev-team@example.com |

**Rotation Reminder:** Set calendar reminder for 2026-01-16 (1 week before expiry)

---

## 🆘 Emergency Contacts

**If you need to revoke keys or have security concerns:**
- Primary: DevOps Team
- Secondary: Security Team
- Emergency: CTO

**Response Time SLA:**
- Critical (key compromised): < 1 hour
- High (key rotation): < 24 hours
- Normal (new service key): < 48 hours

---

**Document Version:** 1.0.0
**Last Updated:** October 25, 2025
**Next Review:** January 23, 2026 (before key rotation)
