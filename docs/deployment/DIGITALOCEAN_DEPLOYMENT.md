# 🚀 DigitalOcean Deployment Guide

## Quick Deployment Steps

### 1. 📋 Pre-deployment Checklist

**Required:**
- [ ] DigitalOcean account with payment method
- [ ] Domain name (optional but recommended)
- [ ] SSH key pair
- [ ] Team access requirements defined

**Recommended Droplet Specs:**
- **Minimum**: 2 GB RAM, 1 vCPU, 50 GB SSD ($12/month)
- **Recommended**: 4 GB RAM, 2 vCPUs, 80 GB SSD ($24/month)
- **Team Production**: 8 GB RAM, 4 vCPUs, 160 GB SSD ($48/month)

### 2. 🖥️ Create DigitalOcean Droplet

```bash
# Option 1: Using DigitalOcean CLI (doctl)
doctl compute droplet create astro-engine \
  --image ubuntu-22-04-x64 \
  --size s-2vcpu-4gb \
  --region nyc1 \
  --ssh-keys YOUR_SSH_KEY_ID

# Option 2: Using Web Interface
# 1. Go to DigitalOcean dashboard
# 2. Create → Droplets
# 3. Choose Ubuntu 22.04 LTS
# 4. Select appropriate size
# 5. Add your SSH key
# 6. Create droplet
```

### 3. 🔧 Server Setup

```bash
# SSH into your droplet
ssh root@YOUR_DROPLET_IP

# Clone your repository
git clone https://github.com/Astro-Engine/Astro_Engine_ORGNL.git
cd Astro_Engine

# Run deployment script
chmod +x deploy.sh
./deploy.sh

# Follow the prompts and wait for completion
```

### 4. 🌐 Domain Configuration (Optional)

If you have a domain:

```bash
# Update environment with your domain
export DOMAIN="yourdomain.com"
export EMAIL="admin@yourdomain.com"

# Re-run deployment with domain
./deploy.sh
```

**DNS Records to Add:**
```
Type: A
Name: @
Value: YOUR_DROPLET_IP

Type: A  
Name: api
Value: YOUR_DROPLET_IP
```

### 5. ✅ Verify Deployment

```bash
# Check service status
cd /opt/astro_engine
docker-compose ps

# Test health endpoint
curl http://YOUR_DROPLET_IP/health
# or with domain:
curl https://yourdomain.com/health

# Test API endpoint
curl -X POST http://YOUR_DROPLET_IP/lahiri/natal \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "Test User",
    "birth_date": "1990-01-15",
    "birth_time": "14:30:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timezone_offset": 5.5
  }'
```

## 🔧 Team Usage Setup

### 1. 👥 API Access for Team

**Base URLs:**
```
Production: https://yourdomain.com
Development: http://YOUR_DROPLET_IP:5000
Health Check: https://yourdomain.com/health
```

**Common Endpoints:**
```
POST /lahiri/natal          - Generate natal chart
POST /kp/calculate_kp       - KP calculations  
POST /lahiri/synastry       - Compatibility analysis
POST /lahiri/transit        - Current transits
```

### 2. 📚 Team Documentation

Share this with your team:

```bash
# API Documentation
curl https://yourdomain.com/

# Example API call
curl -X POST https://yourdomain.com/lahiri/natal \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "John Doe",
    "birth_date": "1985-06-15",
    "birth_time": "10:30:00",
    "latitude": 19.0760,
    "longitude": 72.8777,
    "timezone_offset": 5.5
  }'
```

### 3. 🔒 Security for Team Access

**Rate Limits:**
- 1000 requests per hour per IP
- Burst limit: 20 requests per second

**CORS Configuration:**
- Development: All origins allowed
- Production: Specific domains only

### 4. 📊 Monitoring & Alerts

**Health Monitoring:**
```bash
# Manual health check
curl https://yourdomain.com/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45Z",
  "version": "1.3.0",
  "services": {
    "swiss_ephemeris": "ok",
    "api_endpoints": "ok"
  }
}
```

**Log Monitoring:**
```bash
# SSH into server
ssh root@YOUR_DROPLET_IP

# View live logs
cd /opt/astro_engine
docker-compose logs -f astro-engine

# View nginx logs
docker-compose logs -f nginx
```

## 🚨 Troubleshooting

### Common Issues

**Issue: Service not starting**
```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs astro-engine

# Restart services
docker-compose restart
```

**Issue: SSL certificate problems**
```bash
# Renew certificate
certbot renew

# Test certificate
certbot certificates
```

**Issue: High memory usage**
```bash
# Check resource usage
docker stats

# Restart with memory limit
docker-compose down
docker-compose up -d
```

### Performance Optimization

**For Heavy Usage:**
```bash
# Increase worker processes
export WORKERS=8

# Increase memory limit
# Edit docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '4.0'
```

## 📞 Team Support

### Quick Commands for Team

**Check API Status:**
```bash
curl https://yourdomain.com/health
```

**Test Core Functionality:**
```bash
# Natal chart test
curl -X POST https://yourdomain.com/lahiri/natal \
  -H "Content-Type: application/json" \
  -d '{"user_name":"Test","birth_date":"1990-01-01","birth_time":"12:00:00","latitude":28.6139,"longitude":77.2090,"timezone_offset":5.5}'
```

**Development Integration:**
```javascript
// JavaScript/React example
const API_BASE = 'https://yourdomain.com';

const generateChart = async (birthData) => {
  const response = await fetch(`${API_BASE}/lahiri/natal`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(birthData),
  });
  return response.json();
};
```

```python
# Python example
import requests

API_BASE = 'https://yourdomain.com'

def generate_chart(birth_data):
    response = requests.post(f'{API_BASE}/lahiri/natal', json=birth_data)
    return response.json()
```

## 📈 Scaling for Team Growth

**When to Scale Up:**

1. **API Response Time > 2 seconds**
   - Upgrade to 8GB RAM droplet
   - Increase worker processes

2. **High CPU Usage (>80%)**
   - Upgrade to 4+ vCPU droplet
   - Consider load balancer

3. **Team Size > 10 developers**
   - Set up staging environment
   - Implement API authentication
   - Add comprehensive monitoring

**Auto-scaling Setup:**
```bash
# Set up load balancer (manual process)
# 1. Create multiple droplets
# 2. Configure DigitalOcean Load Balancer
# 3. Update DNS to point to load balancer
# 4. Configure health checks
```

Your Astro Engine is now ready for production team usage! 🎉
