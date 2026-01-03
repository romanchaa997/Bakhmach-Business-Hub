# Bakhmach Business Hub - Deployment & Initialization Guide

> Comprehensive step-by-step guide for deploying and initializing the Bakhmach Business Hub system  
> **Last Updated**: January 3, 2026  
> **Status**: Production Ready ✅

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [System Requirements](#system-requirements)
3. [Pre-Deployment Checklist](#pre-deployment-checklist)
4. [Installation Methods](#installation-methods)
5. [Configuration](#configuration)
6. [Initialization Steps](#initialization-steps)
7. [Verification & Testing](#verification--testing)
8. [Troubleshooting](#troubleshooting)
9. [Post-Deployment](#post-deployment)
10. [Support & Documentation](#support--documentation)

---

## 🚀 Quick Start

For fastest deployment, run the automated startup script:

```bash
#!/bin/bash
chmod +x startup.sh
./startup.sh
```

**Estimated Time**: 15 minutes  
**Automated Steps**: 10 major setup operations

---

## 💻 System Requirements

### Minimum Requirements
- **OS**: Linux/macOS/Windows (WSL2)
- **Python**: 3.10 or higher
- **PostgreSQL**: 13+
- **Redis**: 6.0+
- **Memory**: 4GB RAM minimum
- **Disk**: 10GB free space
- **CPU**: 2+ cores

### Recommended Specifications
- **OS**: Ubuntu 22.04 LTS or newer
- **Python**: 3.11+
- **PostgreSQL**: 15+
- **Redis**: 7.0+
- **Memory**: 8GB+ RAM
- **Disk**: 50GB SSD
- **CPU**: 4+ cores

### Required Software
- `git` - Version control
- `python3-pip` - Python package manager
- `virtualenv` - Python virtual environments
- `postgresql-client` - Database client tools
- `redis-tools` - Redis client tools

---

## ✅ Pre-Deployment Checklist

### Infrastructure Verification
- [ ] Server/VM provisioned and accessible
- [ ] SSH access configured
- [ ] Firewall rules configured (ports 22, 8000, 5432, 6379)
- [ ] DNS records updated
- [ ] SSL certificates prepared
- [ ] Backup strategy defined

### Software Installation
- [ ] Python 3.10+ installed and verified
- [ ] PostgreSQL service running
- [ ] Redis service running
- [ ] Git installed and configured
- [ ] pip/pip3 verified working

### Security Preparation
- [ ] GitHub tokens generated
- [ ] Google AI credentials prepared
- [ ] Database credentials secured
- [ ] API keys generated
- [ ] SSL certs ready
- [ ] Firewall configured

### Documentation Ready
- [ ] Architecture docs reviewed
- [ ] API reference available
- [ ] Deployment checklist printed
- [ ] Runbooks prepared
- [ ] Escalation contacts listed

---

## 📦 Installation Methods

### Method 1: Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/romanchaa997/Bakhmach-Business-Hub.git
cd Bakhmach-Business-Hub

# Run the startup script
chmod +x startup.sh
./startup.sh

# Follow on-screen prompts
```

**Pros**: 
- Fast and simple
- Automated validation
- Error handling

**Cons**:
- Less control over each step
- May require manual fixes

### Method 2: Manual Installation

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.template .env
# Edit .env with your settings

# 4. Initialize database
alembic upgrade head

# 5. Start services
python3 -m uvicorn services.integration.main:app --reload
```

**Pros**:
- Full control
- Easy to debug
- Customizable

**Cons**:
- Time-consuming
- Manual error handling

### Method 3: Docker Deployment

```bash
# Build image
docker build -t bakhmach-hub .

# Run container
docker run -p 8000:8000 -v $(pwd)/.env:/app/.env bakhmach-hub
```

**Pros**:
- Consistent environment
- Easy scaling
- CI/CD integration

**Cons**:
- Docker required
- More overhead

---

## ⚙️ Configuration

### Environment Variables

Create or update `.env` file:

```env
# GitHub Configuration
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_WEBHOOK_SECRET=your_secret_here
GITHUB_REPO=romanchaa997/Bakhmach-Business-Hub

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bakhmach_integration
DB_USER=postgres
DB_PASSWORD=secure_password_here

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Application
APP_ENV=development  # or production
APP_DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=generate_with_secrets.token_urlsafe(32)
```

### Database Configuration

```sql
-- Create main database
CREATE DATABASE bakhmach_integration;

-- Create user with privileges
CREATE USER bakhmach_user WITH PASSWORD 'secure_password';
ALTER ROLE bakhmach_user SET client_encoding TO 'utf8';
ALTER ROLE bakhmach_user SET default_transaction_isolation TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE bakhmach_integration TO bakhmach_user;
```

### Redis Configuration

```bash
# Test Redis connectivity
redis-cli ping
# Should return: PONG

# Check Redis info
redis-cli info server
```

---

## 🔧 Initialization Steps

### Step 1: Directory Setup

```bash
mkdir -p logs data tmp backups
chmod 755 logs data tmp backups
```

### Step 2: Database Migration

```bash
alembic upgrade head
# Verify migration
psql -U postgres -d bakhmach_integration -c "\dt"
```

### Step 3: Service Verification

```bash
# Check PostgreSQL
psql -h localhost -U postgres -c "SELECT 1"

# Check Redis
redis-cli ping

# Check Python environment
python3 --version
pip list
```

### Step 4: Application Startup

```bash
# Activate virtual environment
source venv/bin/activate

# Start FastAPI server
python3 -m uvicorn services.integration.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 Verification & Testing

### Health Check

```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "timestamp": "2026-01-03T12:00:00Z"}
```

### API Testing

```bash
# Visit API docs
curl http://localhost:8000/docs

# Test sample endpoint
curl -X GET http://localhost:8000/api/v1/status
```

### Database Verification

```bash
# Check database connection
psql -h localhost -U bakhmach_user -d bakhmach_integration -c "SELECT 1"

# List tables
psql -h localhost -U bakhmach_user -d bakhmach_integration -c "\dt"
```

### Cache Verification

```bash
# Check Redis connection
redis-cli ping

# Test cache operations
redis-cli SET test_key "test_value"
redis-cli GET test_key
```

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### Issue: Python not found
```bash
# Solution: Install Python 3.10+
sudo apt-get install python3.10

# Set as default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
```

#### Issue: PostgreSQL connection failed
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Start if needed
sudo service postgresql start

# Verify connectivity
psql -h localhost -U postgres
```

#### Issue: Redis connection refused
```bash
# Check Redis is running
redis-cli ping

# Start if needed
redis-server --daemonize yes

# Check on port 6379
lsof -i :6379
```

#### Issue: Permission denied when running startup.sh
```bash
# Make script executable
chmod +x startup.sh

# Try again
./startup.sh
```

#### Issue: Port 8000 already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process if needed
kill -9 <PID>

# Or use different port
python3 -m uvicorn services.integration.main:app --port 8001
```

---

## 📤 Post-Deployment

### Verification Checklist
- [ ] API is running and responsive
- [ ] Database connected and tables created
- [ ] Redis cache working
- [ ] GitHub webhooks configured
- [ ] Logs being written
- [ ] Monitoring setup complete
- [ ] Backups running
- [ ] Team trained on system

### Recommended Next Steps
1. **Set up monitoring**: Configure Prometheus + Grafana
2. **Enable logging**: Centralize logs to ELK stack
3. **Configure alerts**: Set up PagerDuty/Slack notifications
4. **Run load tests**: Verify performance under load
5. **Document processes**: Create runbooks for operations
6. **Plan backups**: Automated daily backups to cloud storage
7. **Security review**: Perform penetration testing
8. **Team training**: Conduct operations training

---

## 🆘 Support & Documentation

### Documentation Links
- [Architecture Guide](docs/ARCHITECTURE_INTEGRATION.md)
- [API Reference](docs/API-REFERENCE-COMPLETE.md)
- [Monitoring Setup](docs/MONITORING-OBSERVABILITY.md)
- [Security Hardening](docs/SECURITY-COMPLIANCE-STANDARDS.md)

### Getting Help
- **GitHub Issues**: https://github.com/romanchaa997/Bakhmach-Business-Hub/issues
- **Documentation**: https://github.com/romanchaa997/Bakhmach-Business-Hub/wiki
- **Discord**: [Community Server](https://discord.gg/bakhmach)
- **Email**: owner@romanchaa997.com

### Emergency Contacts
- **On-call Engineer**: romanchaa997
- **System Owner**: romanchaa997
- **Escalation**: Check RUNBOOK.md

---

## 📅 Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Pre-Deployment | 2-4 hours | ✅ Ready |
| Installation | 15-30 minutes | ✅ Ready |
| Configuration | 30-60 minutes | ✅ Ready |
| Testing & Verification | 1-2 hours | ✅ Ready |
| **Total Deployment Time** | **2-4 hours** | **READY** |

---

## 🎯 Success Criteria

Deployment is successful when:
- ✅ API responds to requests
- ✅ Database connected with all tables created
- ✅ Redis cache operational
- ✅ All tests passing
- ✅ Logs capturing activity
- ✅ Health checks green
- ✅ Team can access documentation
- ✅ Backup system running

---

**Version**: 1.0  
**Last Updated**: January 3, 2026  
**Maintained By**: @romanchaa997  
**Status**: ACTIVE ✅
