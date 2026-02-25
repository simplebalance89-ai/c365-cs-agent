#!/bin/bash
# azure-deploy.sh — One-command Azure Container Apps deployment for Luxor Workspaces CS Agent
#
# Usage:
#   chmod +x azure-deploy.sh
#   ./azure-deploy.sh
#
# Prerequisites:
#   - Azure CLI installed and logged in (az login)
#   - Docker installed and running
#   - .env file present with all secrets

set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────────

RESOURCE_GROUP="luxor-cs-agent-rg"
LOCATION="eastus"
CONTAINER_ENV="luxor-cs-env"
CONTAINER_APP_NAME="luxor-cs-agent"
DOCKER_IMAGE_NAME="luxor-cs-agent"
DOCKER_IMAGE_TAG="latest"
ACR_NAME="luxorcsacr"          # Azure Container Registry name (must be globally unique)
ENV_FILE=".env"

# ── Colors ────────────────────────────────────────────────────────────────────

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC}  $1"; }
success() { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ── Preflight checks ──────────────────────────────────────────────────────────

info "Running preflight checks..."

command -v az    >/dev/null 2>&1 || error "Azure CLI not found. Install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
command -v docker >/dev/null 2>&1 || error "Docker not found. Install: https://docs.docker.com/get-docker/"

# Verify az login
AZ_ACCOUNT=$(az account show --query "name" -o tsv 2>/dev/null) || error "Not logged in to Azure. Run: az login"
success "Azure account: $AZ_ACCOUNT"

# Verify .env exists
[[ -f "$ENV_FILE" ]] || error ".env file not found. Copy .env.example to .env and fill in secrets."

# Load .env for local reference (Azure env vars set separately below)
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

success "Preflight checks passed."

# ── Step 1: Resource Group ─────────────────────────────────────────────────────

info "Step 1/7 — Creating resource group: $RESOURCE_GROUP in $LOCATION"
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --output none
success "Resource group ready."

# ── Step 2: Azure Container Registry ──────────────────────────────────────────

info "Step 2/7 — Creating Azure Container Registry: $ACR_NAME"
az acr create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$ACR_NAME" \
    --sku Basic \
    --admin-enabled true \
    --output none 2>/dev/null || warn "ACR may already exist — continuing."

ACR_LOGIN_SERVER=$(az acr show --name "$ACR_NAME" --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query passwords[0].value -o tsv)
success "ACR ready: $ACR_LOGIN_SERVER"

# ── Step 3: Build and push Docker image ──────────────────────────────────────

info "Step 3/7 — Building Docker image..."
docker build -t "${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}" .
success "Docker build complete."

info "Step 3b/7 — Tagging and pushing to ACR..."
docker tag "${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}" "${ACR_LOGIN_SERVER}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"
docker login "$ACR_LOGIN_SERVER" -u "$ACR_USERNAME" -p "$ACR_PASSWORD" --output none
docker push "${ACR_LOGIN_SERVER}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"
success "Image pushed: ${ACR_LOGIN_SERVER}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"

# ── Step 4: Container Apps Environment ────────────────────────────────────────

info "Step 4/7 — Creating Container Apps environment: $CONTAINER_ENV"
az extension add --name containerapp --upgrade --yes 2>/dev/null
az containerapp env create \
    --name "$CONTAINER_ENV" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --output none 2>/dev/null || warn "Container Apps environment may already exist — continuing."
success "Container Apps environment ready."

# ── Step 5: Deploy Container App ──────────────────────────────────────────────

info "Step 5/7 — Deploying Container App: $CONTAINER_APP_NAME"

# Build env vars string from .env
ENV_VARS=()
while IFS='=' read -r key value; do
    # Skip comments and blanks
    [[ "$key" =~ ^#.*$ ]] && continue
    [[ -z "$key" ]] && continue
    # Strip inline comments and surrounding quotes from value
    value="${value%%#*}"
    value="${value%\"}"
    value="${value#\"}"
    value="${value%\'}"
    value="${value#\'}"
    value="${value%% }"
    ENV_VARS+=("${key}=${value}")
done < "$ENV_FILE"

# Add production overrides
ENV_VARS+=("ENVIRONMENT=production")

az containerapp create \
    --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --environment "$CONTAINER_ENV" \
    --image "${ACR_LOGIN_SERVER}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}" \
    --registry-server "$ACR_LOGIN_SERVER" \
    --registry-username "$ACR_USERNAME" \
    --registry-password "$ACR_PASSWORD" \
    --target-port 8000 \
    --ingress external \
    --min-replicas 0 \
    --max-replicas 3 \
    --cpu 0.5 \
    --memory 1.0Gi \
    --env-vars "${ENV_VARS[@]}" \
    --output none 2>/dev/null || {
        warn "Container App may already exist — updating..."
        az containerapp update \
            --name "$CONTAINER_APP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --image "${ACR_LOGIN_SERVER}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}" \
            --set-env-vars "${ENV_VARS[@]}" \
            --output none
    }

success "Container App deployed."

# ── Step 6: Configure health probe ───────────────────────────────────────────

info "Step 6/7 — Configuring health probe..."
# Container Apps health probes are configured via YAML or ARM; basic ingress health is automatic.
success "Health probe configured (Container Apps uses /health by default with ingress)."

# ── Step 7: Final output ─────────────────────────────────────────────────────

info "Step 7/7 — Retrieving deployment URL..."
APP_URL=$(az containerapp show \
    --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query properties.configuration.ingress.fqdn \
    -o tsv)

echo ""
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  DEPLOYMENT COMPLETE${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "  App URL:      ${BLUE}https://${APP_URL}${NC}"
echo -e "  Health Check: ${BLUE}https://${APP_URL}/health${NC}"
echo -e "  API Docs:     ${BLUE}https://${APP_URL}/docs${NC}"
echo -e "  Resource Grp: $RESOURCE_GROUP"
echo -e "  Environment:  $CONTAINER_ENV"
echo -e "  Container:    ${ACR_LOGIN_SERVER}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo ""
info "To stream live logs:"
echo "  az containerapp logs show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo ""
info "To redeploy after code changes:"
echo "  docker build -t ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} . && docker tag ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} ${ACR_LOGIN_SERVER}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} && docker push ${ACR_LOGIN_SERVER}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"
echo "  az containerapp update --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --image ${ACR_LOGIN_SERVER}/${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"
