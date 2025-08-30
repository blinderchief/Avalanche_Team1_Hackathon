# Environment Setup Guide

This guide helps you set up the environment variables for the SpectraQ AI Agent project.

## 🔧 Quick Setup

### 1. Copy Environment Files

```bash
# Root level
cp .env.example .env

# Frontend
cp frontend/.env.example frontend/.env

# Backend
cp backend/.env.example backend/.env
```

### 2. Get Required API Keys

#### Essential Services

1. **Gemini AI API Key** (Primary AI service)
   - Visit: https://aistudio.google.com/app/apikey
   - Create an account and generate an API key
   - Add to: `GEMINI_API_KEY`

2. **Wallet Connect Project ID** (Web3 connectivity)
   - Visit: https://cloud.walletconnect.com/
   - Create a project
   - Add to: `VITE_WALLET_CONNECT_PROJECT_ID`

#### Optional Services (Enhanced functionality)

3. **Comput3.ai API Key** (Alternative AI service)
   - Visit: https://comput3.ai/
   - Sign up and get API key
   - Add to: `COMPUT3_API_KEY`

4. **CoinGecko Pro API Key** (Enhanced market data)
   - Visit: https://www.coingecko.com/api/pricing
   - Upgrade to Pro plan
   - Add to: `COINGECKO_API_KEY`

5. **CryptoPanic API Key** (News data)
   - Visit: https://cryptopanic.com/developers/api/
   - Sign up for free account
   - Add to: `CRYPTOPANIC_API_KEY`

6. **Firecrawl API Key** (Web scraping)
   - Visit: https://firecrawl.dev/
   - Sign up for account
   - Add to: `FIRECRAWL_API_KEY`

### 3. Database Setup

#### Development (SQLite - Default)
No additional setup required. SQLite database will be created automatically.

#### Production (PostgreSQL - Recommended)
```bash
# Install PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS with Homebrew
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/

# Create database
sudo -u postgres psql
CREATE DATABASE spectraq_agent;
CREATE USER spectraq_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE spectraq_agent TO spectraq_user;
\q

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://spectraq_user:your_password@localhost:5432/spectraq_agent
```

### 4. Redis Setup (Optional)

#### Development
```bash
# Install Redis
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS with Homebrew
brew install redis

# Windows
# Download from https://github.com/microsoftarchive/redis/releases

# Start Redis
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:alpine
```

#### Production
Consider using Redis Cloud or AWS ElastiCache for production deployments.

## 📝 Environment Files Overview

### Root `.env`
Contains project-wide configuration and shared environment variables.

### Frontend `.env` (`frontend/.env`)
Contains frontend-specific configuration:
- API endpoints
- Web3 configuration
- Feature flags
- Client-side API keys (public)

### Backend `.env` (`backend/.env`)
Contains backend-specific configuration:
- Database credentials
- AI service API keys
- Server configuration
- Security secrets

## 🔐 Security Best Practices

### 1. Keep Secrets Secret
- **Never commit `.env` files** to version control
- Use different secrets for development and production
- Rotate API keys regularly

### 2. Environment-Specific Configuration
```bash
# Development
DEBUG=true
LOG_LEVEL=debug
DATABASE_URL=sqlite:///./dev.db

# Production
DEBUG=false
LOG_LEVEL=warning
DATABASE_URL=postgresql://...
```

### 3. Use Strong Secrets
```bash
# Generate secure keys
openssl rand -hex 32  # For SECRET_KEY
uuidgen               # For unique identifiers
```

## 🧪 Testing Configuration

### Test Environment Variables
```bash
# Create test environment
cp .env.example .env.test

# Update for testing
ENVIRONMENT=test
DATABASE_URL=sqlite:///./test.db
REDIS_URL=redis://localhost:6379/15  # Different Redis DB
```

## 🚀 Production Deployment

### Environment Variables Checklist

#### Security
- [ ] `SECRET_KEY` - Strong, unique secret (min 32 characters)
- [ ] `JWT_SECRET` - Different from SECRET_KEY
- [ ] `ALLOWED_ORIGINS` - Specific domains only
- [ ] `DEBUG=false`
- [ ] `ENVIRONMENT=production`

#### Database
- [ ] `DATABASE_URL` - Production PostgreSQL instance
- [ ] `DATABASE_POOL_SIZE` - Appropriate for your load
- [ ] `REDIS_URL` - Production Redis instance

#### AI Services
- [ ] `GEMINI_API_KEY` - Production API key with appropriate quota
- [ ] Rate limiting configured appropriately

#### Monitoring
- [ ] `SENTRY_DSN` - Error tracking
- [ ] `ENABLE_METRICS=true`
- [ ] Log levels appropriate for production

### Deployment Platforms

#### Docker
```dockerfile
# Use multi-stage build
FROM node:18-alpine AS frontend-builder
# ... build frontend

FROM python:3.12-slim AS backend
# ... setup backend

# Environment files not included in image
# Mount secrets at runtime
```

#### Cloud Platforms
- **Heroku**: Use config vars
- **AWS**: Use Systems Manager Parameter Store or Secrets Manager
- **Google Cloud**: Use Secret Manager
- **Azure**: Use Key Vault

## 🔍 Troubleshooting

### Common Issues

#### 1. API Key Not Working
```bash
# Test API key
curl -H "Authorization: Bearer $GEMINI_API_KEY" https://generativelanguage.googleapis.com/v1/models

# Check environment loading
python -c "import os; print(os.getenv('GEMINI_API_KEY', 'NOT_FOUND'))"
```

#### 2. Database Connection Issues
```bash
# Test database connection
python -c "
from sqlalchemy import create_engine
engine = create_engine('your_database_url_here')
connection = engine.connect()
print('Database connected successfully')
connection.close()
"
```

#### 3. Redis Connection Issues
```bash
# Test Redis connection
redis-cli ping
# Should return PONG

# Test from Python
python -c "
import redis
r = redis.from_url('redis://localhost:6379/0')
r.ping()
print('Redis connected successfully')
"
```

#### 4. Environment Variables Not Loading
```bash
# Check if .env file exists
ls -la .env

# Check file permissions
chmod 600 .env

# Verify environment loading in application
# Add debug print in your application startup
```

## 📚 Additional Resources

- [Environment Variables Best Practices](https://12factor.net/config)
- [FastAPI Settings Documentation](https://fastapi.tiangolo.com/advanced/settings/)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

## 🆘 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all required environment variables are set
3. Ensure all services (database, Redis) are running
4. Check application logs for specific error messages
5. Create an issue in the repository with details

---

**Remember**: Always keep your `.env` files secure and never commit them to version control! 🔒
