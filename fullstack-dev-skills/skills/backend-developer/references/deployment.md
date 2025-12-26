# Deployment Guide

Deployment patterns for Node.js and Python backends.

## Table of Contents
1. Environment Configuration
2. Docker Deployment
3. Railway
4. Vercel (Serverless)
5. Fly.io
6. Production Checklist

## Environment Configuration

### Required Variables

```bash
# .env.example
NODE_ENV=production
PORT=3000

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# Optional
LOG_LEVEL=info
CORS_ORIGIN=https://yourapp.com
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW=60000
```

### Environment Validation

```typescript
// src/config/env.ts
import { z } from 'zod';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.string().transform(Number).default('3000'),
  SUPABASE_URL: z.string().url(),
  SUPABASE_ANON_KEY: z.string().min(1),
  SUPABASE_SERVICE_ROLE_KEY: z.string().min(1),
  CORS_ORIGIN: z.string().optional(),
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
});

export const config = envSchema.parse(process.env);
```

## Docker Deployment

### Dockerfile (Node.js)

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Security: run as non-root
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/package.json ./

USER nodejs

ENV NODE_ENV=production
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "dist/server.js"]
```

### Dockerfile (Python/FastAPI)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Security: run as non-root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Railway

### railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "npm start",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Deploy Commands

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to existing project
railway link

# Deploy
railway up

# Set environment variables
railway variables set SUPABASE_URL=https://...
railway variables set SUPABASE_ANON_KEY=...

# View logs
railway logs
```

## Vercel (Serverless)

### vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "src/server.ts",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "src/server.ts"
    }
  ]
}
```

### Serverless Considerations

```typescript
// Adapt for serverless
import { VercelRequest, VercelResponse } from '@vercel/node';
import { app } from './app';

// Export handler for Vercel
export default function handler(req: VercelRequest, res: VercelResponse) {
  return app(req, res);
}
```

Note: Serverless has cold starts. Consider:
- Keep functions small
- Use edge functions for latency-sensitive routes
- Preload Supabase client outside handler

## Fly.io

### fly.toml

```toml
app = "my-api"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  NODE_ENV = "production"
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1

[[http_service.checks]]
  grace_period = "5s"
  interval = "30s"
  method = "GET"
  timeout = "5s"
  path = "/health"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

### Deploy Commands

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch app
fly launch

# Set secrets
fly secrets set SUPABASE_URL=https://...
fly secrets set SUPABASE_SERVICE_ROLE_KEY=...

# Deploy
fly deploy

# Scale
fly scale count 2

# View logs
fly logs
```

## Production Checklist

### Security

- [ ] Environment variables in secrets manager (not in code)
- [ ] HTTPS enforced
- [ ] Helmet.js configured (Node.js)
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (Supabase handles this)
- [ ] RLS enabled on all user data tables
- [ ] Service role key never exposed to client

### Performance

- [ ] Response compression enabled
- [ ] Database connection pooling (Supabase handles this)
- [ ] Proper indexes on frequently queried columns
- [ ] Caching strategy (Redis/in-memory where appropriate)
- [ ] CDN for static assets

### Reliability

- [ ] Health check endpoint (`GET /health`)
- [ ] Graceful shutdown handling
- [ ] Structured logging (JSON format)
- [ ] Error tracking (Sentry, etc.)
- [ ] Database backups enabled
- [ ] Monitoring and alerting

### Health Check Endpoint

```typescript
// src/routes/health.ts
import { Router } from 'express';
import { supabase } from '../services/supabase';

const router = Router();

router.get('/health', async (req, res) => {
  try {
    // Check database connection
    const { error } = await supabase.from('_health_check').select().limit(1);
    
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      database: error ? 'unhealthy' : 'healthy',
    });
  } catch (err) {
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
    });
  }
});

export default router;
```

### Graceful Shutdown

```typescript
// src/server.ts
import { app } from './app';

const server = app.listen(config.port, () => {
  console.log(`Server running on port ${config.port}`);
});

// Graceful shutdown
const shutdown = async (signal: string) => {
  console.log(`${signal} received, shutting down gracefully`);
  
  server.close(() => {
    console.log('HTTP server closed');
    process.exit(0);
  });

  // Force close after 10s
  setTimeout(() => {
    console.error('Forced shutdown');
    process.exit(1);
  }, 10000);
};

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
```

### Logging

```typescript
// src/utils/logger.ts
import pino from 'pino';

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV === 'development' 
    ? { target: 'pino-pretty' }
    : undefined,
  base: {
    env: process.env.NODE_ENV,
  },
});

// Request logging middleware
import pinoHttp from 'pino-http';

export const requestLogger = pinoHttp({
  logger,
  autoLogging: {
    ignore: (req) => req.url === '/health',
  },
});
```
