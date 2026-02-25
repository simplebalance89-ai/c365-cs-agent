# C365 CS Agent — Azure Container Apps Deployment Guide

## Architecture Overview

```
.env (local secrets)
     |
azure-deploy.sh  ──>  Docker build
                           |
                     Azure Container Registry (ACR)  ──>  Container Apps
                                                               |
                                                         c365-cs-agent.<region>.azurecontainerapps.io
```

**Stack:**
- Azure Container Apps (consumption plan, scales to zero when idle)
- Azure Container Registry (Basic, ~$5/month)
- FastAPI + Uvicorn (2 workers)
- Secrets via Container Apps environment variables (never baked into image)

---

## Prerequisites

### Tools Required

| Tool | Install |
|------|---------|
| Azure CLI | https://docs.microsoft.com/en-us/cli/azure/install-azure-cli |
| Docker Desktop | https://docs.docker.com/get-docker/ |
| Azure subscription | https://portal.azure.com |

### Verify installs
```bash
az --version
docker --version
az login
```

---

## Step 1 — Create your .env file

Copy `.env.example` to `.env` and fill in all values:

```bash
cp .env.example .env
```

Required variables (match `config.py`):

```env
# AI Provider (choose one)
ANTHROPIC_API_KEY=sk-ant-...
# OR use Azure OpenAI:
# AZURE_OPENAI_KEY=your-azure-openai-key
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

CLAUDE_MODEL_CLASSIFY=claude-sonnet-4-6
CLAUDE_MODEL_RESPOND=claude-sonnet-4-6
CLAUDE_MAX_TOKENS=1024

# Zendesk
ZENDESK_SUBDOMAIN=conveyance365
ZENDESK_EMAIL=your-agent@conveyance365.com
ZENDESK_API_TOKEN=your_zendesk_token

# Microsoft Graph (Outlook)
MS_TENANT_ID=your-tenant-id
MS_CLIENT_ID=your-client-id
MS_CLIENT_SECRET=your-client-secret
MS_MAILBOX=support@conveyance365.com

# App
ENVIRONMENT=production
DEBUG=false
DEMO_MODE=true
```

**Never commit .env to git. It is in .gitignore.**

---

## Step 2 — Test locally with Docker

```bash
# Build
docker build -t c365-cs-agent:latest .

# Run with env vars
docker run --env-file .env -p 8000:8000 c365-cs-agent:latest

# Test
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

If the app starts and /health returns a 200, you're ready to deploy.

---

## Step 3 — Create Azure Container Registry

```bash
# Set variables
RESOURCE_GROUP="c365-cs-agent-rg"
LOCATION="eastus"
ACR_NAME="c365csacr"

# Create resource group (or use existing)
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create ACR
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true
```

---

## Step 4 — Build and push Docker image to ACR

```bash
# Login to ACR
az acr login --name $ACR_NAME

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)

# Build and tag
docker build -t c365-cs-agent:latest .
docker tag c365-cs-agent:latest $ACR_LOGIN_SERVER/c365-cs-agent:latest

# Push to ACR
docker push $ACR_LOGIN_SERVER/c365-cs-agent:latest
```

---

## Step 5 — Deploy to Azure Container Apps

```bash
# Install Container Apps extension if needed
az extension add --name containerapp --upgrade

# Create Container Apps environment
az containerapp env create \
  --name c365-cs-env \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# Deploy the container app
az containerapp create \
  --name c365-cs-agent \
  --resource-group $RESOURCE_GROUP \
  --environment c365-cs-env \
  --image $ACR_LOGIN_SERVER/c365-cs-agent:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8000 \
  --ingress external \
  --min-replicas 0 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --env-vars \
    ANTHROPIC_API_KEY="sk-ant-..." \
    ZENDESK_SUBDOMAIN="conveyance365" \
    ZENDESK_EMAIL="support@conveyance365.com" \
    ZENDESK_API_TOKEN="..." \
    MS_TENANT_ID="..." \
    MS_CLIENT_ID="..." \
    MS_CLIENT_SECRET="..." \
    MS_MAILBOX="support@conveyance365.com" \
    ENVIRONMENT="production" \
    DEMO_MODE="true"
```

**Estimated time:** 3-5 minutes on first deploy.

---

## Step 6 — Verify the deployment

```bash
# Get the app URL
APP_URL=$(az containerapp show \
  --name c365-cs-agent \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)

# Health check
curl https://$APP_URL/health

# API docs (FastAPI Swagger UI)
open https://$APP_URL/docs

# Live logs
az containerapp logs show \
  --name c365-cs-agent \
  --resource-group $RESOURCE_GROUP \
  --follow
```

Expected /health response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "services": { ... }
}
```

---

## Step 7 — Update Environment Variables

To update secrets after initial deploy:

### Via Azure Portal
1. Go to portal.azure.com
2. Navigate to: Container Apps > c365-cs-agent > Settings > Environment variables
3. Add/edit key/value, click Save
4. App restarts automatically

### Via CLI
```bash
az containerapp update \
  --name c365-cs-agent \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars ANTHROPIC_API_KEY="sk-ant-new-key" DEMO_MODE="false"
```

---

## Step 8 — Redeploy after code changes

```bash
# Rebuild, push, and restart
docker build -t c365-cs-agent:latest . && \
docker tag c365-cs-agent:latest $ACR_LOGIN_SERVER/c365-cs-agent:latest && \
docker push $ACR_LOGIN_SERVER/c365-cs-agent:latest

# Force new revision
az containerapp update \
  --name c365-cs-agent \
  --resource-group $RESOURCE_GROUP \
  --image $ACR_LOGIN_SERVER/c365-cs-agent:latest

# Or re-run the full deploy script
./azure-deploy.sh
```

---

## Step 9 — Custom Domain (Optional)

### Add a custom domain

1. In Azure Portal: Container Apps > c365-cs-agent > Custom domains
2. Click "Add custom domain"
3. Enter your domain (e.g. `cs-agent.conveyance365.com`)
4. Follow the DNS verification steps (add TXT + CNAME records at your registrar)
5. Azure auto-provisions a managed certificate

Or via CLI:
```bash
az containerapp hostname add \
  --name c365-cs-agent \
  --resource-group $RESOURCE_GROUP \
  --hostname cs-agent.conveyance365.com

# Bind managed certificate
az containerapp hostname bind \
  --name c365-cs-agent \
  --resource-group $RESOURCE_GROUP \
  --hostname cs-agent.conveyance365.com \
  --environment c365-cs-env \
  --validation-method CNAME
```

---

## Step 10 — Monitoring

### Application logs

```bash
# Stream live logs
az containerapp logs show \
  --name c365-cs-agent \
  --resource-group $RESOURCE_GROUP \
  --follow

# View system logs
az containerapp logs show \
  --name c365-cs-agent \
  --resource-group $RESOURCE_GROUP \
  --type system
```

### Metrics in Azure Portal

Navigate to: Container Apps > c365-cs-agent > Monitoring > Metrics

Useful metrics to watch:
- Http 5xx errors
- Response time (P95)
- Requests/second
- CPU usage
- Memory working set
- Replica count

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Container fails to start | Check logs: `az containerapp logs show --name c365-cs-agent --resource-group c365-cs-agent-rg` |
| 503 Service Unavailable | Container may be scaling from zero (cold start). Wait 10-15s and retry. |
| 500 on /health | Missing environment variable. Check Container Apps > Environment variables in portal. |
| Docker push fails | Re-run `az acr login --name c365csacr` |
| App not updating after push | Run `az containerapp update` with `--image` flag to force new revision |
| ACR name already taken | Edit `ACR_NAME` (must be globally unique, alphanumeric only) |

---

## Cost Estimate

| Resource | SKU | Est. Monthly Cost |
|----------|-----|-------------------|
| Container Apps | Consumption (scales to 0) | ~$0-10 (usage-based) |
| Container Registry | Basic | ~$5 |
| Bandwidth (outbound) | First 5GB free | ~$0 |
| **Total** | | **~$5-15/month** |

Container Apps consumption plan charges only when running. If DEMO_MODE=true and no traffic, cost approaches $0.

To tear down completely:
```bash
az group delete --name c365-cs-agent-rg --yes
```
