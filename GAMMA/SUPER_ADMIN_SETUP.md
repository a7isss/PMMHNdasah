# 🔐 Super Admin Setup Guide

## Overview

The WhatsApp PM System v3.0 (Gamma) uses environment variable-based super admin authentication for maximum security. This guide provides step-by-step instructions for setting up and accessing the super admin dashboard.

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ installed
- PostgreSQL database (local or Railway)
- Git repository access

## Quick Setup (3 minutes)

### 1. Environment Configuration

```bash
# Copy the environment template
cp .env.example .env

# Edit .env file with your super admin credentials
# Required variables:
SUPERADMIN_EMAIL=admin@yourdomain.com
SUPERADMIN_PASSWORD=YourSecurePassword123!
```

### 2. Start the Application

```bash
# Terminal 1: Start Backend
cd hndasah-backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend
cd ../FRONTEND
npm install
npm run dev
```

### 3. Access Super Admin

1. **Open Browser**: Navigate to `http://localhost:3000/admin/login`
2. **Login Credentials**:
   - **Email**: `admin@yourdomain.com` (from SUPERADMIN_EMAIL)
   - **Password**: `YourSecurePassword123!` (from SUPERADMIN_PASSWORD)
3. **Access Dashboard**: After login, you'll be redirected to `/admin`
4. **Debug Tools**: Click "Debug Dashboard" for system diagnostics

## Environment Variables Reference

### Required for Super Admin
```bash
SUPERADMIN_EMAIL=admin@yourdomain.com
SUPERADMIN_PASSWORD=YourSecurePassword123!
```

### Optional but Recommended
```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost/whatsapp_pm
DEBUG=true
SECRET_KEY=your-super-secret-key-change-this-in-production
```

## API Endpoints

### Super Admin Login
- **Endpoint**: `POST /api/v1/auth/superadmin/login`
- **Content-Type**: `application/x-www-form-urlencoded`
- **Parameters**:
  - `username`: Super admin email
  - `password`: Super admin password

### Debug Endpoints (Super Admin Only)
- `GET /api/v1/admin/debug/system-info` - System information
- `GET /api/v1/admin/debug/database-status` - Database diagnostics
- `GET /api/v1/admin/debug/logs` - System logs
- `GET /api/v1/admin/debug/metrics` - Performance metrics

## Security Notes

- **Environment Variables**: Super admin credentials are stored in environment variables, not in the database
- **Automatic Creation**: The super admin user is automatically created in the database on first login
- **JWT Tokens**: Super admin sessions use standard JWT authentication
- **Access Control**: All debug endpoints require `super_admin` role

## Troubleshooting

### Login Issues
1. **Check Environment Variables**: Ensure `SUPERADMIN_EMAIL` and `SUPERADMIN_PASSWORD` are set
2. **Database Connection**: Verify database is running and accessible
3. **Clear Browser Cache**: Try clearing browser cache and cookies

### Application Won't Start
1. **Dependencies**: Run `pip install -r requirements.txt` in backend directory
2. **Database**: Ensure PostgreSQL is running or DATABASE_URL is correctly set
3. **Ports**: Make sure ports 8000 (backend) and 3000 (frontend) are available

### Debug Dashboard Not Working
1. **Super Admin Login**: Ensure you're logged in as super admin
2. **API Endpoints**: Check that backend is running on port 8000
3. **CORS**: Frontend should be running on port 3000 for proper CORS

## Production Deployment

For Railway deployment, set these environment variables in your Railway project:

```bash
SUPERADMIN_EMAIL=admin@yourdomain.com
SUPERADMIN_PASSWORD=YourProductionSecurePassword!
ENVIRONMENT=production
DEBUG=false
```

## Support

If you encounter issues:
1. Check the debug dashboard for system diagnostics
2. Review application logs in Railway dashboard
3. Verify environment variables are correctly set
4. Ensure database connectivity

---

**🎉 Ready to access your super admin dashboard!**

Navigate to `http://localhost:3000/admin/login` and use your configured super admin credentials.
