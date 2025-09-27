# Zimmer Integration Deployment Guide

## Environment Configuration

Set these environment variables for production:

```bash
# Required
ZIMMER_SERVICE_TOKEN=your-secret-token-here
OPENAI_API_KEY=your-openai-key
TELEGRAM_TOKEN=your-telegram-token

# Optional (with defaults)
CHAT_BUDGET_SECONDS=7
CHAT_API_TIMEOUT=9
LLM_TIMEOUT=6
AGENT_MAX_ITERS=3
CHAT_MODEL=gpt-3.5-turbo
```

## Reverse Proxy Configuration

### Nginx Configuration
```nginx
upstream backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Health check - public access
    location /health {
        proxy_pass http://backend;
        proxy_read_timeout 5s;
        proxy_connect_timeout 2s;
    }

    # Chat API - extended timeout
    location /api/chat {
        proxy_pass http://backend;
        proxy_read_timeout 12s;
        proxy_connect_timeout 5s;
    }

    # Other API endpoints
    location /api/ {
        proxy_pass http://backend;
        proxy_read_timeout 30s;
        proxy_connect_timeout 5s;
    }
}
```

### Kubernetes Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: zimmer-ingress
spec:
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /health
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
```

## Health Checks

### Liveness Probe
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
```

### Readiness Probe
```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
```

## Database Migration

The `ZimmerTenant` table will be created automatically on first startup. No manual migration required.

## Monitoring

### Log Format
All Zimmer endpoints log in this format:
```
Zimmer [endpoint] - user_automation_id: [id], status: [code], latency: [ms]ms, endpoint: [path]
```

### Metrics to Monitor
- Response times for all endpoints
- Error rates (4xx, 5xx)
- Token consumption rates
- Chat API timeout frequency

## Security

- Never log `X-Zimmer-Service-Token` header
- Use HTTPS in production
- Rotate `ZIMMER_SERVICE_TOKEN` regularly
- Monitor for unusual token consumption patterns

## Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check `ZIMMER_SERVICE_TOKEN` environment variable
2. **Chat API Timeout**: Verify `CHAT_BUDGET_SECONDS` and `CHAT_API_TIMEOUT` settings
3. **Database Errors**: Ensure database is accessible and migrations completed

### Health Check Response
```json
{
  "status": "ok",
  "version": "abc1234",
  "uptime": 3600
}
```

## Deployment Checklist

- [ ] Environment variables set
- [ ] Reverse proxy configured with correct timeouts
- [ ] Health checks configured
- [ ] Database accessible
- [ ] Logs monitoring configured
- [ ] Security headers configured
- [ ] SSL/TLS certificates installed

