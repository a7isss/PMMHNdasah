# 🚀 RAILWAY DEPLOYMENT GUIDE - Hndasah PM System v3.0 (Gamma)

**Production Deployment | Environment Variables | Railway Configuration**
**Status:** Production Deployed ✅ | November 5, 2025

---

## 🎯 **DEPLOYMENT OVERVIEW**

The Hndasah PM system is now **fully deployed and operational** on Railway with:

- ✅ **Backend:** FastAPI + PostgreSQL + Redis (Railway)
- ✅ **Frontend:** Next.js + Material-UI (Railway)
- ✅ **Superadmin Dashboard:** Complete admin interface
- ✅ **Environment Variables:** Secure credential management
- ✅ **Multi-tenant Architecture:** Production-ready isolation

### **Railway Services:**
```
├── Backend Service (FastAPI)
│   ├── Railway PostgreSQL Database
│   ├── Railway Redis Cache
│   └── Environment Variables
├── Frontend Service (Next.js)
│   ├── Static Site Hosting
│   └── Environment Variables
└── Domain Configuration
    ├── Custom Domain (optional)
    └── SSL Certificates (automatic)
```

---

## 🔧 **RAILWAY PROJECT SETUP**

### **1. Create Railway Project**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create new project
railway init hndasah-pm-gamma

# Link to existing project (if already created)
railway link
```

### **2. Backend Service Setup**
```bash
# Navigate to backend directory
cd GAMMA/hndasah-backend

# Create Railway service
railway add --name backend

# Deploy backend
railway up
```

### **3. Frontend Service Setup**
```bash
# Navigate to frontend directory
cd GAMMA/FRONTEND

# Create Railway service
railway add --name frontend

# Deploy frontend
railway up
```

---

## 🔐 **ENVIRONMENT VARIABLES CONFIGURATION**

### **Backend Environment Variables (Railway)**
```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:password@containers-us-west-1.railway.app:5432/railway

# Redis Configuration
REDIS_URL=redis://default:password@containers-us-west-1.railway.app:6379

# JWT Configuration
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Superadmin Configuration (REQUIRED)
SUPERADMIN_EMAIL=admin@hndasah-pm.com
SUPERADMIN_PASSWORD=your-superadmin-password-here

# CORS Configuration
FRONTEND_URL=https://hndasah-pm-gamma.up.railway.app
ALLOWED_ORIGINS=https://hndasah-pm-gamma.up.railway.app,http://localhost:3000

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# WhatsApp Configuration (Optional)
WHATSAPP_ACCESS_TOKEN=your-whatsapp-access-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_VERIFY_TOKEN=your-verify-token

# MCP Server Configuration (Optional)
MCP_SERVER_URL=https://your-mcp-server.com
MCP_API_KEY=your-mcp-api-key

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@hndasah-pm.com
```

### **Frontend Environment Variables (Railway)**
```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://hndasah-pm-gamma.up.railway.app

# Environment
NODE_ENV=production

# Build Configuration
NEXT_TELEMETRY_DISABLED=1
```

### **Setting Environment Variables in Railway**
```bash
# Via Railway CLI
railway variables set SUPERADMIN_EMAIL=admin@hndasah-pm.com
railway variables set SUPERADMIN_PASSWORD=your-secure-password
railway variables set DATABASE_URL=postgresql://...

# Via Railway Dashboard
# 1. Go to your project dashboard
# 2. Select the backend service
# 3. Go to Variables tab
# 4. Add each environment variable
```

---

## 🗄️ **DATABASE SETUP**

### **Railway PostgreSQL Configuration**
```sql
-- Railway automatically creates the database
-- No manual setup required

-- Verify connection after deployment
SELECT version();
SELECT current_database();
SELECT current_user;
```

### **Database Migrations**
```bash
# Railway runs migrations automatically on deploy
# If manual migration needed:
railway run python -m alembic upgrade head
```

### **Redis Setup**
```bash
# Railway provides Redis automatically
# Verify connection:
railway run python -c "
import redis
import os
r = redis.from_url(os.getenv('REDIS_URL'))
r.set('test', 'hello')
print(r.get('test'))
"
```

---

## 🔐 **SUPERADMIN SETUP**

### **Environment Variables (Required)**
```bash
# Set these in Railway backend service variables
SUPERADMIN_EMAIL=admin@hndasah-pm.com
SUPERADMIN_PASSWORD=SecurePassword123!
```

### **First-Time Superadmin Access**
```bash
# After deployment, the superadmin user is created automatically
# Access the admin login at:
https://your-railway-app.up.railway.app/admin/login

# Login credentials:
# Email: admin@hndasah-pm.com (from SUPERADMIN_EMAIL)
# Password: SecurePassword123! (from SUPERADMIN_PASSWORD)
```

### **Superadmin Dashboard Features**
- ✅ **Tenant Management:** Create, view, update tenants
- ✅ **User Management:** Manage users across all tenants
- ✅ **System Statistics:** View comprehensive metrics
- ✅ **Role Management:** Change user roles and permissions
- ✅ **Account Control:** Activate/deactivate user accounts

---

## 🌐 **DOMAIN & SSL CONFIGURATION**

### **Custom Domain Setup**
```bash
# Add custom domain in Railway dashboard
# 1. Go to Settings > Domains
# 2. Add your domain (e.g., pm.hndasah.com)
# 3. Update DNS records as instructed
# 4. SSL certificate is automatic

# Update environment variables
FRONTEND_URL=https://pm.hndasah.com
ALLOWED_ORIGINS=https://pm.hndasah.com
```

### **Railway-Generated URLs**
```
Backend: https://hndasah-pm-gamma.up.railway.app
Frontend: https://hndasah-pm-gamma-frontend.up.railway.app
Database: Internal Railway networking
Redis: Internal Railway networking
```

---

## 🔍 **DEPLOYMENT VERIFICATION**

### **Health Checks**
```bash
# Backend health check
curl https://your-app.up.railway.app/health

# Frontend health check
curl https://your-frontend.up.railway.app

# Database connection test
railway run python -c "
import asyncpg
import os
async def test():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    result = await conn.fetchval('SELECT 1')
    print('Database connected:', result)
import asyncio
asyncio.run(test())
"
```

### **Superadmin Login Test**
```bash
# Test superadmin login
curl -X POST https://your-app.up.railway.app/api/v1/auth/superadmin/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@hndasah-pm.com&password=your-password"
```

### **API Endpoints Test**
```bash
# Test admin stats (requires superadmin token)
curl -H "Authorization: Bearer <token>" \
  https://your-app.up.railway.app/api/v1/admin/stats
```

---

## 📊 **MONITORING & LOGS**

### **Railway Monitoring**
```bash
# View logs
railway logs

# View specific service logs
railway logs --service backend

# Monitor deployments
railway status
```

### **Application Logs**
```bash
# Backend logs include:
# - API requests/responses
# - Database queries
# - Authentication events
# - Superadmin actions
# - Error tracking

# Frontend logs include:
# - Build status
# - Runtime errors
# - API calls
```

---

## 🔧 **TROUBLESHOOTING**

### **Common Issues**

#### **Database Connection Failed**
```bash
# Check DATABASE_URL format
railway variables get DATABASE_URL

# Test connection manually
railway run python -c "
import os
print('DATABASE_URL:', os.getenv('DATABASE_URL'))
"
```

#### **Superadmin Login Failed**
```bash
# Verify environment variables
railway variables get SUPERADMIN_EMAIL
railway variables get SUPERADMIN_PASSWORD

# Check if user was created
railway run python -c "
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine

async def check():
    engine = create_async_engine(os.getenv('DATABASE_URL'))
    async with engine.begin() as conn:
        result = await conn.execute('SELECT email FROM users WHERE email = $1', (os.getenv('SUPERADMIN_EMAIL'),))
        user = result.fetchone()
        print('Superadmin user exists:', user is not None)

asyncio.run(check())
"
```

#### **CORS Issues**
```bash
# Check FRONTEND_URL and ALLOWED_ORIGINS
railway variables get FRONTEND_URL
railway variables get ALLOWED_ORIGINS
```

#### **Build Failures**
```bash
# Check build logs
railway logs --service backend --lines 100

# Common issues:
# - Missing environment variables
# - Database connection during build
# - Python dependencies
```

---

## 🚀 **DEPLOYMENT CHECKLIST**

### **Pre-Deployment**
- [ ] Railway account created and logged in
- [ ] Project initialized (`railway init`)
- [ ] Environment variables prepared
- [ ] Database schema reviewed
- [ ] Superadmin credentials decided

### **Backend Deployment**
- [ ] Backend service created (`railway add --name backend`)
- [ ] Environment variables set in Railway dashboard
- [ ] Database URL configured
- [ ] Redis URL configured
- [ ] Superadmin credentials set
- [ ] CORS origins configured
- [ ] Deployment successful (`railway up`)

### **Frontend Deployment**
- [ ] Frontend service created (`railway add --name frontend`)
- [ ] API URL environment variable set
- [ ] Build successful
- [ ] Frontend accessible

### **Post-Deployment Verification**
- [ ] Backend health check passes
- [ ] Frontend loads correctly
- [ ] Superadmin login works
- [ ] Admin dashboard accessible
- [ ] Database connections verified
- [ ] API endpoints responding
- [ ] Logs show no critical errors

### **Production Configuration**
- [ ] Custom domain configured (optional)
- [ ] SSL certificates verified
- [ ] Monitoring alerts set up
- [ ] Backup procedures confirmed
- [ ] Team access configured

---

## 🔒 **SECURITY BEST PRACTICES**

### **Environment Variables**
- ✅ **Never commit secrets** to version control
- ✅ **Use Railway's built-in variable management**
- ✅ **Rotate credentials regularly**
- ✅ **Use strong, unique passwords**

### **Access Control**
- ✅ **Superadmin credentials** known only to authorized personnel
- ✅ **Railway project access** restricted to team members
- ✅ **Database access** limited to application only
- ✅ **API endpoints** properly authenticated

### **Data Protection**
- ✅ **Database encryption** enabled (Railway default)
- ✅ **HTTPS enforced** (Railway automatic)
- ✅ **Input validation** implemented
- ✅ **SQL injection protection** via SQLAlchemy

---

## 📞 **SUPPORT & MAINTENANCE**

### **Regular Maintenance**
```bash
# Update dependencies monthly
railway run pip install -r requirements.txt --upgrade

# Monitor logs weekly
railway logs --since 7d

# Check system health
curl https://your-app.up.railway.app/health
```

### **Backup Strategy**
- ✅ **Railway automatic backups** for PostgreSQL
- ✅ **Database exports** available via Railway dashboard
- ✅ **Code repository** backed up separately
- ✅ **Environment variables** documented securely

### **Scaling Considerations**
```bash
# Monitor usage
railway metrics

# Scale resources if needed
# Railway dashboard > Service > Settings > Resources

# Consider upgrading plans for:
# - High traffic (>1000 concurrent users)
# - Large databases (>100GB)
# - High API throughput
```

---

## 🎉 **SUCCESS METRICS**

After successful deployment, verify:

- ✅ **Application accessible** via Railway URL
- ✅ **Superadmin login** functional
- ✅ **Admin dashboard** fully operational
- ✅ **Database connections** stable
- ✅ **API responses** <100ms
- ✅ **No critical errors** in logs
- ✅ **SSL certificate** active
- ✅ **Mobile responsive** design working

**Deployment Status:** ✅ **PRODUCTION LIVE**

---

*Complete Railway deployment guide for Hndasah PM system with superadmin dashboard and environment variable configuration.*
