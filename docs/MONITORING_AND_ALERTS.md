# Monitoring and Alerts Configuration Guide
## Phase 10: Monitoring Alerts & Dashboards

**Status:** ✅ **COMPLETE** - Ready for post-deployment configuration
**Date:** October 25, 2025

---

## 📋 **MONITORING ENDPOINTS (Already Implemented)**

### **Health & Status:**
- `GET /health` - Application health check
- `GET /metrics` - Prometheus metrics (text format)
- `GET /metrics/json` - Metrics in JSON format

### **Authentication Monitoring:**
- `GET /auth/stats` - Authentication statistics
- `GET /auth/keys/info` - API key registry
- `GET /auth/health` - Auth system health

### **Infrastructure Monitoring:**
- `GET /cache/stats` - Cache performance stats
- `GET /circuit/status` - Circuit breaker status

---

## 🚨 **CRITICAL ALERTS (Module 10.1 & 10.2)**

### **Alert Configuration (Post-Deployment)**

After deploying to DigitalOcean, configure these critical alerts:

#### **1. CPU Usage Alert**
```yaml
Alert: CPU > 80%
Duration: 5 minutes
Action: Scale up instances
Severity: HIGH
Notification: Email + Slack
```

**Setup via DigitalOcean CLI:**
```bash
doctl monitoring alert create \\
  --resource-type apps \\
  --resource-id <APP_ID> \\
  --type cpu_utilization \\
  --compare greater_than \\
  --value 80 \\
  --window 5m \\
  --enabled \\
  --emails "team@example.com"
```

#### **2. Memory Usage Alert**
```yaml
Alert: Memory > 80%
Duration: 5 minutes
Action: Investigate memory leak / scale up
Severity: HIGH
Notification: Email + Slack
```

#### **3. Error Rate Alert**
```yaml
Alert: Error rate > 5%
Duration: 5 minutes
Action: Check logs, investigate
Severity: CRITICAL
Notification: Email + Slack + PagerDuty
```

#### **4. Authentication Failures**
```yaml
Alert: Failed auth > 10 in 1 minute
Duration: 1 minute
Action: Potential attack, investigate
Severity: CRITICAL
Notification: Security team
```

**Monitor via:**
```bash
curl https://your-app.ondigitalocean.app/auth/stats
```

#### **5. Service Down**
```yaml
Alert: Health check failed 3x
Duration: 30 seconds
Action: Auto-restart, investigate
Severity: CRITICAL
Notification: On-call engineer
```

#### **6. Circuit Breaker Open**
```yaml
Alert: Circuit breaker state = OPEN
Duration: Immediate
Action: Service dependency failing
Severity: HIGH
Notification: Engineering team
```

**Monitor via:**
```bash
curl https://your-app.ondigitalocean.app/circuit/status
```

---

## 📊 **PROMETHEUS METRICS (Module 10.2)**

### **Already Collected:**

**Request Metrics:**
```
astro_engine_requests_total
astro_engine_request_duration_seconds
astro_engine_active_requests
```

**Cache Metrics:**
```
astro_engine_cache_operations_total
astro_engine_cache_hit_rate
```

**Error Metrics:**
```
astro_engine_errors_total
```

**System Metrics:**
```
astro_engine_memory_usage_bytes
astro_engine_cpu_usage_percentage
```

### **Prometheus Alert Rules (Optional):**

Create `prometheus/alerts.yml`:

```yaml
groups:
  - name: astro_engine_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(astro_engine_errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: HighMemoryUsage
        expr: astro_engine_memory_usage_percentage > 80
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "Memory usage above 80%"

      - alert: CacheHitRateLow
        expr: astro_engine_cache_hit_rate < 50
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Cache hit rate below 50%"
```

---

## 🔧 **MODULE 10.3: GRAFANA (OPTIONAL - SKIP FOR NOW)**

**Status:** Not needed initially

DigitalOcean provides built-in monitoring dashboard with:
- CPU usage graphs
- Memory usage graphs
- Request count
- Error rates
- Response times

**If Grafana needed later:**
- Can integrate with Prometheus endpoint
- Import pre-built dashboards
- Customize as needed

---

## 📈 **MODULE 10.4: UPTIME MONITORING**

### **External Uptime Monitoring (Recommended):**

**Services to use:**
1. **UptimeRobot** (Free tier available)
2. **Pingdom**
3. **StatusCake**
4. **Better Uptime**

**Setup:**
```
Monitor URL: https://your-app.ondigitalocean.app/health
Check Interval: 1 minute
Alert on: 3 consecutive failures
Notifications: Email, Slack, SMS
Expected Response: 200 OK
Expected Content: "healthy"
```

**Benefits:**
- External monitoring (independent of your infrastructure)
- Geographic checks (test from multiple locations)
- Status page for customers
- SMS/email alerts

---

## 📚 **MODULE 10.5: ON-CALL & INCIDENT RESPONSE**

### **Incident Response Playbook:**

#### **Scenario 1: High Error Rate (>5%)**

**Detection:**
```bash
# Check error metrics
curl https://your-app.ondigitalocean.app/metrics | grep errors_total

# Check logs
doctl apps logs <APP_ID> --type RUN | grep ERROR
```

**Response:**
1. Check error types (auth, validation, calculation)
2. Review recent deployments (rollback if needed)
3. Check dependencies (Redis, ephemeris)
4. Scale up if resource exhaustion

#### **Scenario 2: Service Down**

**Detection:**
```bash
# Health check fails
curl https://your-app.ondigitalocean.app/health
# Returns 503 or timeout
```

**Response:**
1. Check DigitalOcean app status
2. Review deployment logs
3. Check circuit breakers (`/circuit/status`)
4. Manual restart if needed:
```bash
doctl apps create-deployment <APP_ID>
```

#### **Scenario 3: High Memory Usage**

**Detection:**
```bash
# Memory > 80%
doctl apps get <APP_ID>
```

**Response:**
1. Check for memory leaks
2. Review recent code changes
3. Scale up instance size
4. Restart workers (auto-restarts after 1000 requests)

#### **Scenario 4: Authentication Attack**

**Detection:**
```bash
# >10 failed auths in 1 minute
curl https://your-app.ondigitalocean.app/auth/stats
```

**Response:**
1. Review failed auth IPs
2. Block suspicious IPs if needed
3. Verify API keys not compromised
4. Increase rate limiting if needed

#### **Scenario 5: Circuit Breaker Open**

**Detection:**
```bash
curl https://your-app.ondigitalocean.app/circuit/status
# Returns state: "open"
```

**Response:**
1. Check which circuit (ephemeris or redis)
2. Verify ephemeris files exist
3. Check Redis connectivity
4. Wait for auto-recovery (30-60s)
5. Manual investigation if doesn't recover

---

## 📞 **ESCALATION PROCEDURE**

### **Severity Levels:**

**P1 - CRITICAL (Service Down):**
- Response time: <15 minutes
- Escalate to: On-call engineer immediately
- Notification: Phone call + SMS + Email

**P2 - HIGH (Performance Degraded):**
- Response time: <1 hour
- Escalate to: Engineering team
- Notification: Email + Slack

**P3 - MEDIUM (Warnings, Non-Critical):**
- Response time: <4 hours
- Escalate to: Engineering team (next business day)
- Notification: Email

**P4 - LOW (Informational):**
- Response time: Next sprint
- Track in: Issue tracker

---

## 🔍 **MONITORING CHECKLIST**

### **Post-Deployment (Within 24 hours):**
- [ ] Configure DigitalOcean CPU alert (>80%)
- [ ] Configure DigitalOcean memory alert (>80%)
- [ ] Set up external uptime monitoring (UptimeRobot, etc.)
- [ ] Test alert notifications work
- [ ] Create status page (statuspage.io or similar)

### **Week 1:**
- [ ] Monitor error rates daily
- [ ] Check authentication stats
- [ ] Verify cache hit rates (when Redis enabled)
- [ ] Review logs for anomalies
- [ ] Adjust alert thresholds if needed

### **Ongoing:**
- [ ] Weekly metrics review
- [ ] Monthly incident review
- [ ] Quarterly alert tuning
- [ ] Update runbooks based on incidents

---

## 📊 **KEY METRICS TO MONITOR**

### **Application Health:**
```
✅ Uptime %
✅ Request count
✅ Error rate
✅ Response time (p50, p95, p99)
✅ Active instances
```

### **Authentication:**
```
✅ Total authentications
✅ Success rate
✅ Failed attempts per hour
✅ Rate limit exceeded count
```

### **Performance:**
```
✅ Cache hit rate (target: >70%)
✅ Cache response time
✅ Calculation time
✅ Ephemeris access time
```

### **Infrastructure:**
```
✅ CPU utilization
✅ Memory utilization
✅ Redis connection status
✅ Circuit breaker states
```

---

## ✅ **PHASE 10 DELIVERABLES**

### **Documentation:**
- ✅ docs/MONITORING_AND_ALERTS.md (this document)
- ✅ Alert configuration guide
- ✅ Incident response playbooks
- ✅ Escalation procedures
- ✅ Monitoring checklist

### **Endpoints (Already Implemented):**
- ✅ /health
- ✅ /metrics
- ✅ /auth/stats
- ✅ /cache/stats
- ✅ /circuit/status

### **Ready for Configuration:**
- ✅ DigitalOcean alerts (post-deployment)
- ✅ External uptime monitoring
- ✅ Prometheus integration (if needed)

---

## 🎯 **PHASE 10 COMPLETION**

**Modules 10.1-10.5:** ✅ **COMPLETE**

All monitoring infrastructure is in place:
- Metrics endpoints
- Health checks
- Documentation
- Alert guidelines
- Incident playbooks

**Actual alert configuration** happens post-deployment (requires live app).

**Status:** ✅ **READY FOR DEPLOYMENT AND MONITORING**

---

**Prepared by:** Claude Code
**Date:** October 25, 2025
**Phase 10:** ✅ **COMPLETE**
