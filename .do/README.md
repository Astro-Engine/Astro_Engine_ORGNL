# DigitalOcean App Platform Configuration

This directory contains the configuration files for deploying Astro Engine to DigitalOcean App Platform.

## Files

### `app.yaml`
The main App Platform specification file. This defines:
- Service configuration (Python Flask app)
- Auto-scaling settings (1-5 instances)
- Environment variables
- Health checks
- Managed Redis database
- Build and deployment settings

## Deployment

### Quick Start

```bash
# From project root
./deploy-digitalocean.sh --create
```

### Manual Deployment

```bash
# Validate configuration
doctl apps spec validate .do/app.yaml

# Create app
doctl apps create --spec .do/app.yaml

# Update existing app
doctl apps update <APP_ID> --spec .do/app.yaml
```

## Configuration Updates

When you need to update the configuration:

1. Edit `app.yaml`
2. Validate: `doctl apps spec validate .do/app.yaml`
3. Apply: `doctl apps update <APP_ID> --spec .do/app.yaml`

## Important Notes

### SECRET_KEY
The `SECRET_KEY` in `app.yaml` is a placeholder. You MUST update it:

1. Generate a secure key:
```bash
openssl rand -hex 32
```

2. Update in DigitalOcean:
   - Go to App Settings → Environment Variables
   - Edit SECRET_KEY
   - Paste your generated key
   - Save (auto-redeploys)

### REDIS_URL
This is automatically injected by DigitalOcean when the Redis database is created. No manual configuration needed.

### Auto-Deploy
The app is configured to automatically deploy when you push to the `main` branch. To disable:

```yaml
github:
  deploy_on_push: false  # Change to false
```

## Scaling

### Vertical Scaling (More RAM/CPU per instance)

Edit `app.yaml`:
```yaml
instance_size_slug: professional-s  # 4GB RAM, 2 vCPU
# Options: professional-xs, professional-s, professional-m, professional-l
```

### Horizontal Scaling (More instances)

Edit `app.yaml`:
```yaml
autoscaling:
  min_instance_count: 2  # Minimum instances
  max_instance_count: 10  # Maximum instances
  metrics:
    cpu:
      percent: 60  # Scale up at 60% CPU
```

## Monitoring

```bash
# View logs
doctl apps logs <APP_ID> --type RUN --follow

# Check status
doctl apps get <APP_ID>

# View metrics
doctl apps list-metrics <APP_ID>
```

## Cost Optimization

Current configuration:
- **App:** $24/month per instance (1-5 instances)
- **Redis:** $15/month
- **Total:** $39-135/month depending on traffic

To reduce costs:
1. Reduce `max_instance_count`
2. Use smaller Redis: `db-s-1vcpu-512mb` ($10/month)
3. Monitor usage and adjust

## Resources

- [App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [doctl Reference](https://docs.digitalocean.com/reference/doctl/)
- [Pricing](https://www.digitalocean.com/pricing/app-platform)
