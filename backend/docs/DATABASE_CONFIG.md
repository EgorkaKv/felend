# Database Connection Configuration

This guide explains how to configure database connections for different environments.

## Overview

The application supports two connection methods:
- **Public IP** - for local development (TCP/IP connection)
- **Unix Socket** - for GCP Cloud SQL (socket connection)

## Configuration Parameters

### Connection Type Selection
```bash
# Choose connection method
DB_CONNECTION_TYPE=public          # or "unix_socket"
```

## Method 1: Public IP Connection (Local Development)

Use this method for local development with PostgreSQL running on your machine or accessible via network.

### Configuration (.env)
```bash
DB_CONNECTION_TYPE=public
DB_HOST=localhost
DB_PORT=5432
DB_NAME=felend
DB_USER=user
DB_PASSWORD=password
```

### Generated Connection String
```
postgresql://user:password@localhost:5432/felend
```

### Use Cases
- ✅ Local development
- ✅ PostgreSQL in Docker
- ✅ Remote PostgreSQL server
- ✅ Development database on network

## Method 2: Unix Socket Connection (GCP Cloud SQL)

Use this method when deploying to Google Cloud Run with Cloud SQL.

### Configuration (.env)
```bash
DB_CONNECTION_TYPE=unix_socket
DB_INSTANCE_CONNECTION_NAME=my-project:us-central1:felend-db
DB_NAME=felend
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_SOCKET_DIR=/cloudsql
```

### Generated Connection String
```
postgresql+psycopg2://postgres:your-secure-password@/felend?host=/cloudsql/my-project:us-central1:felend-db
```

### Important Notes
- `DB_INSTANCE_CONNECTION_NAME` format: `project-id:region:instance-name`
- `DB_SOCKET_DIR` is `/cloudsql` by default (Cloud Run standard)
- Requires `psycopg2` or `psycopg2-binary` package
- Cloud Run must have Cloud SQL connection configured

### Use Cases
- ✅ Google Cloud Run deployment
- ✅ Google Cloud SQL connection
- ✅ Production environment on GCP
- ✅ Staging environment on GCP

## Method 3: Legacy DATABASE_URL (Backward Compatibility)

For backward compatibility, you can still use the old `DATABASE_URL` variable.

### Configuration (.env)
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/felend
```

**Note:** If `DATABASE_URL` is set, it takes priority over all other database settings.

## Environment-Specific Examples

### Local Development
```bash
# .env.local
DB_CONNECTION_TYPE=public
DB_HOST=localhost
DB_PORT=5432
DB_NAME=felend
DB_USER=felend_dev
DB_PASSWORD=dev_password
```

### GCP Cloud Run Production
```bash
# .env.production (set via Secret Manager or environment variables)
DB_CONNECTION_TYPE=unix_socket
DB_INSTANCE_CONNECTION_NAME=felend-prod:us-central1:felend-db
DB_NAME=felend_production
DB_USER=felend_app
DB_PASSWORD=<secure-password-from-secret-manager>
```

### GCP Cloud Run Staging
```bash
# .env.staging
DB_CONNECTION_TYPE=unix_socket
DB_INSTANCE_CONNECTION_NAME=felend-staging:us-central1:felend-db-staging
DB_NAME=felend_staging
DB_USER=felend_app
DB_PASSWORD=<secure-password-from-secret-manager>
```

## Connection Pool Settings

The application uses these connection pool settings:

```python
pool_pre_ping=True      # Verify connections before using them
pool_recycle=3600       # Recycle connections after 1 hour
```

These settings ensure:
- Dead connections are detected and replaced
- Connections don't exceed Cloud SQL connection limits
- Better stability in serverless environments

## Troubleshooting

### Error: "DB_INSTANCE_CONNECTION_NAME is required"
**Solution:** When using `DB_CONNECTION_TYPE=unix_socket`, you must set `DB_INSTANCE_CONNECTION_NAME`.

### Error: "No module named 'psycopg2'"
**Solution:** For unix_socket connections, install psycopg2:
```bash
pip install psycopg2-binary
```

### Error: "FATAL: password authentication failed"
**Solution:** 
1. Verify `DB_USER` and `DB_PASSWORD` are correct
2. Check Cloud SQL user exists and has proper permissions
3. Verify database name is correct

### Error: "could not connect to server: No such file or directory"
**Solution:**
1. Verify `DB_INSTANCE_CONNECTION_NAME` format is correct
2. Ensure Cloud Run service has Cloud SQL connection configured
3. Check Cloud SQL instance is running

## Security Best Practices

### For Production
1. ✅ Use Secret Manager for `DB_PASSWORD`
2. ✅ Use unix_socket connection on GCP
3. ✅ Use strong passwords
4. ✅ Limit database user permissions
5. ✅ Never commit `.env` files to git

### For Development
1. ✅ Use separate database for development
2. ✅ Use `.env.local` (add to `.gitignore`)
3. ✅ Don't use production credentials locally

## Testing Configuration

To verify your database configuration works:

```bash
# Check connection
python -c "from app.core.database import engine; print(engine.url)"

# Test connection
python -c "from app.core.database import engine; engine.connect(); print('✅ Connected!')"
```

## Migration Guide

### From old DATABASE_URL to new system

**Before:**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/felend
```

**After (Local):**
```bash
DB_CONNECTION_TYPE=public
DB_HOST=localhost
DB_PORT=5432
DB_NAME=felend
DB_USER=user
DB_PASSWORD=password
```

**After (GCP):**
```bash
DB_CONNECTION_TYPE=unix_socket
DB_INSTANCE_CONNECTION_NAME=my-project:us-central1:felend-db
DB_NAME=felend
DB_USER=user
DB_PASSWORD=password
```

**Note:** Old `DATABASE_URL` still works for backward compatibility!
