# Deployment Guide for Google Cloud Run

This guide explains how to deploy the Felend backend to Google Cloud Run.

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **gcloud CLI** installed and configured
3. **Docker** installed locally (for testing)
4. **Required APIs enabled**:
   - Cloud Run API
   - Cloud Build API
   - Container Registry API
   - Secret Manager API (recommended for secrets)

## Environment Variables

The following environment variables need to be set in Cloud Run:

### Required Variables

```bash
DATABASE_URL=postgresql://user:password@host:5432/database
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
REDIRECT_URI=https://your-domain.com/api/v1/auth/google/callback
FRONTEND_URL=https://your-frontend-domain.com
```

### Optional Variables

```bash
DEBUG=false
PROJECT_NAME=Felend
VERSION=0.1.0
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Email Configuration (for verification emails)

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@felend.com
```

## Deployment Methods

### Method 1: Using Cloud Build (Recommended)

This method uses the `cloudbuild.yaml` file for automated deployment.

#### 1. Setup Google Cloud Project

```bash
# Set your project ID
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

#### 2. Store Secrets in Secret Manager

```bash
# Create secrets
echo -n "your-secret-key" | gcloud secrets create SECRET_KEY --data-file=-
echo -n "postgresql://..." | gcloud secrets create DATABASE_URL --data-file=-
echo -n "your-google-client-id" | gcloud secrets create GOOGLE_CLIENT_ID --data-file=-
echo -n "your-google-client-secret" | gcloud secrets create GOOGLE_CLIENT_SECRET --data-file=-

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding SECRET_KEY \
    --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding DATABASE_URL \
    --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

#### 3. Deploy using Cloud Build

```bash
# Submit build from backend directory
cd backend
gcloud builds submit --config=cloudbuild.yaml
```

#### 4. Configure Cloud Run Service

After deployment, update environment variables to use secrets:

```bash
gcloud run services update felend-backend \
  --region us-central1 \
  --update-secrets=SECRET_KEY=SECRET_KEY:latest \
  --update-secrets=DATABASE_URL=DATABASE_URL:latest \
  --update-secrets=GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID:latest \
  --update-secrets=GOOGLE_CLIENT_SECRET=GOOGLE_CLIENT_SECRET:latest
```

### Method 2: Manual Deployment

#### 1. Build Docker Image Locally

```bash
# Navigate to backend directory
cd backend

# Build the image
docker build -t gcr.io/$PROJECT_ID/felend-backend:latest .
```

#### 2. Test Locally (Optional)

```bash
# Run container locally
docker run -p 8080:8080 \
  -e DATABASE_URL="postgresql://..." \
  -e SECRET_KEY="your-secret-key" \
  -e GOOGLE_CLIENT_ID="your-client-id" \
  -e GOOGLE_CLIENT_SECRET="your-client-secret" \
  gcr.io/$PROJECT_ID/felend-backend:latest

# Test the API
curl http://localhost:8080/health
```

#### 3. Push to Container Registry

```bash
# Configure Docker to use gcloud credentials
gcloud auth configure-docker

# Push the image
docker push gcr.io/$PROJECT_ID/felend-backend:latest
```

#### 4. Deploy to Cloud Run

```bash
gcloud run deploy felend-backend \
  --image gcr.io/$PROJECT_ID/felend-backend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "DATABASE_URL=postgresql://...,SECRET_KEY=your-secret-key" \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --min-instances 0 \
  --timeout 300
```

## Database Setup

### Cloud SQL (Recommended for Production)

1. **Create Cloud SQL PostgreSQL instance**:

```bash
gcloud sql instances create felend-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1
```

2. **Create database and user**:

```bash
gcloud sql databases create felend --instance=felend-db
gcloud sql users create felend-user --instance=felend-db --password=secure-password
```

3. **Connect Cloud Run to Cloud SQL**:

```bash
gcloud run services update felend-backend \
  --add-cloudsql-instances $PROJECT_ID:us-central1:felend-db \
  --region us-central1
```

4. **Update DATABASE_URL**:

```bash
DATABASE_URL=postgresql://felend-user:password@/felend?host=/cloudsql/$PROJECT_ID:us-central1:felend-db
```

### Run Alembic Migrations

You can run migrations using Cloud Run Jobs or Cloud Build:

```bash
# Create a one-off job to run migrations
gcloud run jobs create felend-migrate \
  --image gcr.io/$PROJECT_ID/felend-backend:latest \
  --region us-central1 \
  --set-env-vars "DATABASE_URL=..." \
  --command alembic \
  --args "upgrade,head"

# Execute the job
gcloud run jobs execute felend-migrate --region us-central1
```

## CORS Configuration

Update the CORS origins in `app/main.py` to include your frontend domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-domain.com",
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Monitoring and Logging

### View Logs

```bash
# Stream logs
gcloud run services logs tail felend-backend --region us-central1

# View logs in console
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=felend-backend" --limit 50
```

### Set up Monitoring

```bash
# Create uptime check
gcloud monitoring uptime create felend-backend-uptime \
  --resource-type=uptime-url \
  --hostname=your-service-url.run.app \
  --path=/health
```

## CI/CD with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches:
      - main
    paths:
      - 'backend/**'

env:
  PROJECT_ID: your-project-id
  SERVICE_NAME: felend-backend
  REGION: us-central1

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1

      - name: Build and Deploy
        run: |
          gcloud builds submit --config=backend/cloudbuild.yaml
```

## Scaling Configuration

### Auto-scaling Settings

```bash
gcloud run services update felend-backend \
  --region us-central1 \
  --min-instances 1 \
  --max-instances 10 \
  --cpu-throttling \
  --concurrency 80
```

### Resource Allocation

- **Development**: 512Mi memory, 1 CPU
- **Production**: 1Gi memory, 2 CPU

```bash
gcloud run services update felend-backend \
  --region us-central1 \
  --memory 1Gi \
  --cpu 2
```

## Custom Domain Setup

1. **Map custom domain**:

```bash
gcloud run domain-mappings create \
  --service felend-backend \
  --domain api.yourdomain.com \
  --region us-central1
```

2. **Update DNS records** as shown in the console output

## Cost Optimization

- Use **min-instances=0** for development
- Use **min-instances=1** for production (to avoid cold starts)
- Enable **CPU throttling** when idle
- Use **Cloud SQL for PostgreSQL** with appropriate tier
- Monitor usage and adjust resources accordingly

## Troubleshooting

### Check Service Status

```bash
gcloud run services describe felend-backend --region us-central1
```

### Test Health Endpoint

```bash
curl https://your-service-url.run.app/health
```

### View Error Logs

```bash
gcloud logging read "resource.type=cloud_run_revision AND severity=ERROR" --limit 10
```

### Common Issues

1. **Cold starts**: Set min-instances to 1
2. **Database connection**: Check Cloud SQL connection and credentials
3. **Memory issues**: Increase memory allocation
4. **Timeout**: Increase timeout setting

## Security Best Practices

1. ✅ Use Secret Manager for sensitive data
2. ✅ Run as non-root user (already configured in Dockerfile)
3. ✅ Use least privilege IAM roles
4. ✅ Enable VPC connector for Cloud SQL
5. ✅ Use HTTPS only (Cloud Run default)
6. ✅ Implement rate limiting
7. ✅ Regular security updates

## Useful Commands

```bash
# Delete service
gcloud run services delete felend-backend --region us-central1

# Update environment variable
gcloud run services update felend-backend \
  --region us-central1 \
  --set-env-vars "NEW_VAR=value"

# View service URL
gcloud run services describe felend-backend \
  --region us-central1 \
  --format 'value(status.url)'

# Scale to zero
gcloud run services update felend-backend \
  --region us-central1 \
  --no-traffic
```

## Support

For issues or questions:
- Check Cloud Run logs
- Review Cloud Build logs
- Verify environment variables
- Test database connectivity
