# Docker Compose Deployment Checklist

**Status**: Pre-deployment verification complete  
**Date**: July 13, 2024  
**Next Action**: Run `docker-compose up --build` when Docker daemon is available

---

## Pre-Deployment Verification (✅ Complete)

### Configuration Files
- ✅ `docker-compose.yml` - Valid YAML syntax, services defined correctly
- ✅ `Dockerfile` - Python 3.11-slim base, non-root user, gunicorn configured
- ✅ `.dockerignore` - Excludes __pycache__, .git, *.pyc, build artifacts
- ✅ `.env.example` - All required environment variables documented

### Application Code
- ✅ All Python modules compile without syntax errors
- ✅ Flask app factory initializes successfully
- ✅ All 4 blueprints register correctly (auth, bugs, dashboard, users)
- ✅ 22 routes configured and respond to test client
- ✅ SQLAlchemy models defined with proper relationships

### Dependencies
- ✅ `requirements.txt` - All production dependencies listed
- ✅ Core packages: Flask, SQLAlchemy, Flask-Login, Flask-WTF
- ✅ Database: psycopg2 (PostgreSQL adapter)
- ✅ Security: werkzeug (password hashing)
- ✅ Utilities: email-validator, python-dotenv, Jinja2

### Frontend Assets
- ✅ HTML templates: 11 files, Jinja2 syntax validated
- ✅ CSS: 658 lines, responsive design verified
- ✅ JavaScript: 8 lines, DOM initialization present

---

## Docker Compose Deployment Test Steps

Run these commands from `apps/bug-tracker/` directory when Docker daemon is available:

### Step 1: Build Images
```bash
docker-compose build
```
**Expected**: 
- Flask image builds successfully
- PostgreSQL 16 image pulls from registry
- No build errors or warnings

### Step 2: Start Services
```bash
docker-compose up
```
**Expected**:
- PostgreSQL service starts and reports healthy
- Flask web service starts on port 5000
- No connection timeouts or startup errors

### Step 3: Verify Database Initialization
```bash
docker exec bugtracker-db psql -U buguser -d bugtracker -c "\dt"
```
**Expected**: 
- Tables created: users, bugs, comments, attachments
- Schema initialized successfully
- Default users seeded (admin, dev, tester)

### Step 4: Test Web Service
```bash
curl http://localhost:5000/auth/login
```
**Expected**:
- HTTP 200 response
- HTML login page returned

### Step 5: Test Database Connectivity
```bash
curl http://localhost:5000/dashboard/stats
```
**Expected**:
- HTTP 401 (unauthorized) or 302 (redirect to login) - normal
- Not 500 (internal error) or connection refused

### Step 6: Login Test
```bash
curl -c cookies.txt -d "email=admin@example.com&password=password123" \
  http://localhost:5000/auth/login -L
```
**Expected**:
- Successful login
- Session cookie set
- Redirect to dashboard

### Step 7: Create Bug (Authenticated)
```bash
curl -b cookies.txt -X POST \
  -d "title=Test Bug&description=Testing&priority=high&status=open" \
  http://localhost:5000/bugs/create
```
**Expected**:
- HTTP 302 redirect after creation
- Bug appears in /bugs/ list

---

## Verification Matrix

| Component | Check | Expected | Pre-Deploy Status |
|-----------|-------|----------|------------------|
| **Python** | Syntax | No errors | ✅ Pass |
| | Imports | All modules load | ✅ Pass |
| | Flask app | Initializes | ✅ Pass |
| **Database** | Models | Defined correctly | ✅ Pass |
| | Relationships | Configured | ✅ Pass |
| | Initialization | auto-seeded | ✅ Ready |
| **Frontend** | Templates | Jinja2 valid | ✅ Pass |
| | CSS | Syntax valid | ✅ Pass |
| | JS | Functions defined | ✅ Pass |
| **Docker** | Compose | YAML valid | ✅ Pass |
| | Dockerfile | Image buildable | ✅ Ready |
| | .env | Example provided | ✅ Ready |
| **Security** | Passwords | werkzeug PBKDF2 | ✅ Configured |
| | File Upload | Validation present | ✅ Configured |
| | CSRF | Flask-WTF enabled | ✅ Configured |

---

## Default Test Credentials

After `docker-compose up`, test with these credentials:

| Email | Password | Role | Expected Access |
|-------|----------|------|-----------------|
| admin@example.com | password123 | Admin | Full access to all features |
| dev@example.com | password123 | Developer | Create/edit bugs, view dashboard |
| tester@example.com | password123 | Tester | Create bugs, view-only on management |

---

## Docker Services Configuration

### PostgreSQL Service (bugtracker-db)
```yaml
Image: postgres:16
Port: 5432 (localhost:5432)
Database: bugtracker
User: buguser
Password: bugpass
Health Check: pg_isready -U buguser -d bugtracker
```

### Flask Web Service (bugtracker-web)
```yaml
Build: apps/bug-tracker/Dockerfile
Port: 5000 (localhost:5000)
Command: flask run --host 0.0.0.0
Environment: 
  - FLASK_APP=wsgi.py
  - DATABASE_URL=postgresql://buguser:bugpass@db:5432/bugtracker
  - FLASK_ENV=development
Health Check: Based on web service responsiveness
```

---

## Troubleshooting Guide

### PostgreSQL Connection Failed
**Problem**: `psycopg2.OperationalError: connection refused`

**Solution**:
1. Ensure database service is healthy: `docker-compose ps`
2. Wait 10-15 seconds for database to fully initialize
3. Check database service logs: `docker-compose logs db`
4. Verify `DATABASE_URL` matches service credentials

### Flask Application Won't Start
**Problem**: Container crashes or won't start

**Solution**:
1. Check logs: `docker-compose logs web`
2. Verify all Python files present: `docker exec bugtracker-web ls -la /app/app/`
3. Check if port 5000 is already in use: `lsof -i :5000`
4. Rebuild image: `docker-compose build --no-cache`

### Database Not Initialized
**Problem**: Tables don't exist or seed users missing

**Solution**:
1. Check database logs: `docker-compose logs db`
2. Verify environment variables in docker-compose.yml
3. Manually seed: `docker exec bugtracker-web flask shell`
   ```python
   >>> from app import db, create_app
   >>> app = create_app()
   >>> with app.app_context():
   ...     db.create_all()
   ```

### Port Conflicts
**Problem**: `bind: address already in use`

**Solution**:
1. Change ports in docker-compose.yml:
   ```yaml
   ports:
     - "5001:5000"  # web
     - "5433:5432"  # db
   ```
2. Update DATABASE_URL accordingly

---

## Performance Expectations

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| docker-compose build | 2-5 minutes | First build, pulls base images |
| docker-compose up | 10-15 seconds | Services startup |
| Database initialization | 5-10 seconds | Schema creation + seed |
| Login | <1 second | Password hash verification |
| Bug creation | <1 second | Database insert |
| Dashboard stats | <500ms | Query + Chart.js rendering |
| Page load | <2 seconds | HTML render + CSS + JS |

---

## Security Notes for Local Development

⚠️ **These settings are for local development only:**
- `FLASK_ENV=development` - Debug enabled
- `SECRET_KEY` hardcoded - Use strong random key in production
- Database password in docker-compose.yml - Use secrets management in production
- Default users seeded automatically - Remove in production

---

## Post-Deployment Validation

After `docker-compose up` succeeds:

1. **Access Web UI**: http://localhost:5000
2. **Login**: Use admin@example.com / password123
3. **Create Bug**: Test bug creation with file upload
4. **View Dashboard**: Verify Chart.js renders
5. **Test Roles**: Try each user role (admin, dev, tester)
6. **File Upload**: Upload a screenshot and verify storage
7. **Search/Filter**: Filter bugs by status and priority
8. **Responsive**: Test mobile viewport (375px)

---

## Cleanup Commands

### Stop Services
```bash
docker-compose down
```

### Remove All Data (Reset Everything)
```bash
docker-compose down -v
```

### Rebuild Without Cache
```bash
docker-compose build --no-cache
```

### View Logs
```bash
docker-compose logs -f web
docker-compose logs -f db
```

---

## Next Phase: Production Deployment

When ready to deploy to Kubernetes:

1. Update docker-compose.yml to reference external PostgreSQL (not embedded service)
2. Create Kubernetes manifests (Deployment, Service, ConfigMap, Secret)
3. Implement proper secrets management (Kubernetes Secrets, Vault)
4. Configure persistent volumes for database and uploads
5. Set up ingress for external access
6. Configure health checks and resource limits
7. Implement CI/CD pipeline for automated deployment

---

**Status**: ✅ Pre-deployment verification complete. Ready for Docker Compose testing.

