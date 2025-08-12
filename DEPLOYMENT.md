# 🚀 Deployment Guide

## 🌟 Deployment Options

### 1. 🚂 Railway Deployment

Railway is the recommended deployment platform for its simplicity and performance.

#### Prerequisites
- Railway account
- GitHub repository connected to Railway

#### Setup Steps

1. **Create Railway Project**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   
   # Create new project
   railway init
   ```

2. **Add Services**
   - Add PostgreSQL service: `railway add --service postgresql`
   - Add Redis service: `railway add --service redis`

3. **Configure Environment Variables**
   ```bash
   # Set required environment variables
   railway variables set APP_ENV=production
   railway variables set SECRET_KEY=$(openssl rand -base64 32)
   railway variables set ACCESS_TOKEN_EXPIRE_MINUTES=30
   railway variables set REFRESH_TOKEN_EXPIRE_DAYS=30
   ```

4. **Deploy**
   ```bash
   railway up
   ```

5. **Custom Domain (Optional)**
   ```bash
   railway domain add api.yourdomain.com
   ```

### 2. 🎨 Render Deployment

#### Prerequisites
- Render account
- GitHub repository

#### Setup Steps

1. **Connect Repository**
   - Go to Render Dashboard
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Select `render.yaml` file

2. **Environment Variables**
   Set these in Render Dashboard:
   - `SECRET_KEY` (generate secure key)
   - `APP_ENV=production`
   - Database variables are auto-configured

3. **Deploy**
   - Render will automatically deploy on push to main branch
   - Access your API at: `https://your-service.onrender.com`

### 3. 🐳 Docker Deployment

#### Local Development
```bash
# Copy environment variables
cp .env.example .env
# Edit .env with your values

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Scale API instances
docker-compose up -d --scale api=3
```

#### Production Docker
```bash
# Build production image
docker build -t ecommerce-api:latest .

# Run with external database
docker run -d \
  --name ecommerce-api \
  -p 8000:8000 \
  -e APP_ENV=production \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db \
  -e REDIS_URL=redis://host:6379/0 \
  -e SECRET_KEY=your-secret-key \
  ecommerce-api:latest
```

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `APP_ENV` | Environment (development/production/testing) | `production` |
| `SECRET_KEY` | JWT secret key (must be secure in production) | `your-super-secret-key` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://...` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `DEBUG` | `false` | Debug mode |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT token expiration |
| `RATE_LIMIT_REQUESTS` | `100` | Rate limit per window |
| `RATE_LIMIT_WINDOW` | `60` | Rate limit window (seconds) |

## 🏥 Health Checks

The API provides comprehensive health check endpoints:

- `GET /health` - Basic health check
- `GET /health/ready` - Readiness check (includes dependencies)
- `GET /health/live` - Liveness check
- `GET /health/detailed` - Detailed health with metrics

## 📊 Monitoring

### Built-in Monitoring

- **Structured Logging**: All logs are in JSON format
- **Request Tracking**: Each request has a unique ID
- **Performance Metrics**: Response time tracking
- **Error Tracking**: Detailed error logging with context

### External Monitoring (Optional)

1. **Sentry for Error Tracking**
   ```bash
   pip install sentry-sdk[fastapi]
   export SENTRY_DSN=your-sentry-dsn
   ```

2. **New Relic for APM**
   ```bash
   pip install newrelic
   export NEW_RELIC_LICENSE_KEY=your-license-key
   ```

## 🔒 Security Checklist

- [ ] ✅ Strong `SECRET_KEY` (32+ random characters)
- [ ] ✅ HTTPS enabled in production
- [ ] ✅ Environment variables properly secured
- [ ] ✅ Database access restricted
- [ ] ✅ CORS origins configured for production
- [ ] ✅ Rate limiting enabled
- [ ] ✅ Security headers configured
- [ ] ✅ Regular dependency updates

## 🚦 CI/CD Pipeline

The GitHub Actions workflow automatically:

1. **Tests**: Run unit tests and quality checks
2. **Security**: Scan for vulnerabilities
3. **Build**: Create Docker image
4. **Deploy**: Deploy to staging/production
5. **Verify**: Run health checks and smoke tests

### Branch Strategy

- `main` → Production deployment
- `develop` → Staging deployment
- Feature branches → PR checks only

## 📈 Performance Optimization

### Production Optimizations

1. **Multiple Workers**
   ```bash
   # Railway/Render automatically scale
   uvicorn main:app --workers 4
   ```

2. **Connection Pooling**
   - PostgreSQL: 20 connections pool
   - Redis: Connection reuse

3. **Caching Strategy**
   - Product catalog cached for 10 minutes
   - User sessions cached for 30 minutes
   - API responses cached where appropriate

### Scaling Considerations

- **Horizontal Scaling**: Multiple API instances
- **Database**: Read replicas for heavy read workloads
- **Caching**: Redis cluster for high availability
- **CDN**: For static assets

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check environment variables
   echo $DATABASE_URL
   
   # Test connection
   python -c "import asyncpg; print('OK')"
   ```

2. **Redis Connection Failed**
   ```bash
   # Check Redis URL
   echo $REDIS_URL
   
   # Test connection
   redis-cli -u $REDIS_URL ping
   ```

3. **High Memory Usage**
   ```bash
   # Check worker processes
   ps aux | grep uvicorn
   
   # Monitor with health endpoint
   curl /health/detailed
   ```

### Logs

```bash
# Railway logs
railway logs

# Render logs
# Available in Render Dashboard

# Docker logs
docker-compose logs api
```

## 📞 Support

- **Health Checks**: Monitor `/health/detailed`
- **Documentation**: Visit `/docs` (development only)
- **Logs**: Check structured JSON logs
- **Issues**: Create GitHub issue with logs and error details

## 🔄 Database Migrations

For schema changes:

1. Update models in `app/models.py`
2. Use Alembic for migrations (future enhancement):
   ```bash
   # Generate migration
   alembic revision --autogenerate -m "description"
   
   # Apply migration
   alembic upgrade head
   ```

Currently, the app uses automatic table creation on startup.