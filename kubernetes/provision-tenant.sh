#!/bin/bash

# VirtPLC Tenant Provisioning Script
# This script creates a new tenant namespace and deploys all necessary resources

set -e

# Configuration
TENANT_ID=$1
COMPANY_NAME=$2
COMPANY_DOMAIN=$3
TENANT_NAMESPACE="virtplc-${TENANT_ID}"

if [ -z "$TENANT_ID" ] || [ -z "$COMPANY_NAME" ] || [ -z "$COMPANY_DOMAIN" ]; then
    echo "Usage: $0 <tenant_id> <company_name> <company_domain>"
    echo "Example: $0 acme123 'ACME Corp' acme.virtplc.com"
    exit 1
fi

echo "🚀 Provisioning tenant: $TENANT_ID ($COMPANY_NAME)"

# Create tenant namespace
echo "📁 Creating namespace: $TENANT_NAMESPACE"
kubectl create namespace $TENANT_NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Label the namespace
kubectl label namespace $TENANT_NAMESPACE tenant=$TENANT_ID app=virtplc --overwrite

# Create tenant-specific configmap
echo "⚙️ Creating tenant configuration"
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: tenant-config-${TENANT_ID}
  namespace: $TENANT_NAMESPACE
data:
  TENANT_ID: "${TENANT_ID}"
  COMPANY_NAME: "${COMPANY_NAME}"
  COMPANY_DOMAIN: "${COMPANY_DOMAIN}"
  DB_HOST: "virtplc-postgres.virtplc-system.svc.cluster.local"
  DB_PORT: "5432"
EOF

# Create tenant-specific secrets
echo "🔐 Creating tenant secrets"
# Generate random passwords
JWT_SECRET=$(openssl rand -base64 32)
DB_PASSWORD=$(openssl rand -base64 16)

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: tenant-secrets-${TENANT_ID}
  namespace: $TENANT_NAMESPACE
type: Opaque
data:
  jwt-secret: $(echo -n $JWT_SECRET | base64)
  db-password: $(echo -n $DB_PASSWORD | base64)
EOF

# Deploy tenant services using templates
echo "🚀 Deploying tenant services"

# Replace template variables and apply
sed "s/{{TENANT_ID}}/${TENANT_ID}/g; s/{{TENANT_NAMESPACE}}/${TENANT_NAMESPACE}/g; s/{{TENANT_DOMAIN}}/${COMPANY_DOMAIN}/g" \
    kubernetes/tenant-deployment-template.yaml | kubectl apply -f -

sed "s/{{TENANT_ID}}/${TENANT_ID}/g; s/{{TENANT_NAMESPACE}}/${TENANT_NAMESPACE}/g; s/{{TENANT_DOMAIN}}/${COMPANY_DOMAIN}/g" \
    kubernetes/tenant-services-template.yaml | kubectl apply -f -

# Apply network policies
echo "🔒 Applying network policies"
sed "s/{{TENANT_ID}}/${TENANT_ID}/g; s/{{TENANT_NAMESPACE}}/${TENANT_NAMESPACE}/g" \
    kubernetes/network-policies.yaml | kubectl apply -f -

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready"
kubectl wait --for=condition=available --timeout=300s deployment/virtplc-backend -n $TENANT_NAMESPACE
kubectl wait --for=condition=available --timeout=300s deployment/virtplc-frontend -n $TENANT_NAMESPACE
kubectl wait --for=condition=available --timeout=300s deployment/virtplc-ai-service -n $TENANT_NAMESPACE

echo "✅ Tenant $TENANT_ID provisioned successfully!"
echo "🌐 Frontend: https://${COMPANY_DOMAIN}"
echo "🔗 API: https://api.${COMPANY_DOMAIN}"
echo ""
echo "📋 Tenant Details:"
echo "   ID: $TENANT_ID"
echo "   Namespace: $TENANT_NAMESPACE"
echo "   Domain: $COMPANY_DOMAIN"
echo "   JWT Secret: ${JWT_SECRET:0:16}..."
echo "   DB Password: ${DB_PASSWORD:0:16}..."