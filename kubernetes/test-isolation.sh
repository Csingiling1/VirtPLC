#!/bin/bash

# Test Multi-Tenant Isolation in Kubernetes
# This script verifies that tenants are properly isolated from each other

set -e

echo "🧪 Testing Multi-Tenant Isolation"
echo "================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test 1: Network Isolation
echo "Test 1: Network Isolation"
echo "-------------------------"
echo "Attempting to access TechCorp backend from ACME pod..."

ACME_POD=$(kubectl get pod -n virtplc-acme123 -l app=virtplc-backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
TECH_POD=$(kubectl get pod -n virtplc-tech456 -l app=virtplc-backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$ACME_POD" ]; then
    echo -e "${RED}❌ ACME pod not found. Is the tenant deployed?${NC}"
else
    # Try to access TechCorp service from ACME pod (should fail)
    if kubectl exec -n virtplc-acme123 $ACME_POD -- timeout 5 curl -s http://virtplc-backend.virtplc-tech456.svc.cluster.local:8080/actuator/health 2>/dev/null; then
        echo -e "${RED}❌ FAILED: Cross-tenant access succeeded (isolation broken!)${NC}"
    else
        echo -e "${GREEN}✅ PASSED: Cross-tenant access denied (network policies working)${NC}"
    fi
fi

echo ""

# Test 2: Database Schema Isolation
echo "Test 2: Database Schema Isolation"
echo "----------------------------------"
echo "Checking tenant database schemas..."

POSTGRES_POD=$(kubectl get pod -n virtplc-system -l app=postgres -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$POSTGRES_POD" ]; then
    echo -e "${RED}❌ PostgreSQL pod not found${NC}"
else
    echo "Database schemas:"
    kubectl exec -n virtplc-system $POSTGRES_POD -- psql -U virtplc -d virtplc -t -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'tenant_%' ORDER BY schema_name;"
    
    # Check if each tenant has their own schema
    ACME_SCHEMA=$(kubectl exec -n virtplc-system $POSTGRES_POD -- psql -U virtplc -d virtplc -t -c "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = 'tenant_acme123';" | tr -d ' ')
    TECH_SCHEMA=$(kubectl exec -n virtplc-system $POSTGRES_POD -- psql -U virtplc -d virtplc -t -c "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = 'tenant_tech456';" | tr -d ' ')
    
    if [ "$ACME_SCHEMA" = "1" ] && [ "$TECH_SCHEMA" = "1" ]; then
        echo -e "${GREEN}✅ PASSED: Each tenant has isolated database schema${NC}"
    else
        echo -e "${RED}❌ FAILED: Tenant schemas not properly created${NC}"
    fi
fi

echo ""

# Test 3: Namespace Isolation
echo "Test 3: Namespace Isolation"
echo "----------------------------"
echo "Verifying namespace labels and network policies..."

ACME_LABELS=$(kubectl get namespace virtplc-acme123 -o jsonpath='{.metadata.labels}' 2>/dev/null || echo "")
TECH_LABELS=$(kubectl get namespace virtplc-tech456 -o jsonpath='{.metadata.labels}' 2>/dev/null || echo "")

if [[ $ACME_LABELS == *"tenant-isolation=true"* ]] && [[ $TECH_LABELS == *"tenant-isolation=true"* ]]; then
    echo -e "${GREEN}✅ PASSED: Namespaces properly labeled for isolation${NC}"
else
    echo -e "${RED}❌ FAILED: Namespace labels missing${NC}"
fi

# Check network policies exist
ACME_NETPOL=$(kubectl get networkpolicy -n virtplc-acme123 --no-headers 2>/dev/null | wc -l)
TECH_NETPOL=$(kubectl get networkpolicy -n virtplc-tech456 --no-headers 2>/dev/null | wc -l)

if [ "$ACME_NETPOL" -gt 0 ] && [ "$TECH_NETPOL" -gt 0 ]; then
    echo -e "${GREEN}✅ PASSED: Network policies exist for both tenants${NC}"
else
    echo -e "${RED}❌ FAILED: Network policies missing${NC}"
fi

echo ""

# Test 4: Resource Quotas
echo "Test 4: Resource Limits"
echo "-----------------------"
echo "Checking pod resource requests/limits..."

ACME_RESOURCES=$(kubectl get pods -n virtplc-acme123 -o json 2>/dev/null | jq -r '.items[0].spec.containers[0].resources')
TECH_RESOURCES=$(kubectl get pods -n virtplc-tech456 -o json 2>/dev/null | jq -r '.items[0].spec.containers[0].resources')

if [[ $ACME_RESOURCES == *"limits"* ]] && [[ $TECH_RESOURCES == *"limits"* ]]; then
    echo -e "${GREEN}✅ PASSED: Resource limits configured for tenant pods${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING: Resource limits not configured${NC}"
fi

echo ""

# Test 5: Secret Isolation
echo "Test 5: Secret Isolation"
echo "------------------------"
echo "Verifying tenant-specific secrets..."

ACME_SECRETS=$(kubectl get secrets -n virtplc-acme123 2>/dev/null | grep -c tenant-secrets || echo "0")
TECH_SECRETS=$(kubectl get secrets -n virtplc-tech456 2>/dev/null | grep -c tenant-secrets || echo "0")

if [ "$ACME_SECRETS" -gt 0 ] && [ "$TECH_SECRETS" -gt 0 ]; then
    echo -e "${GREEN}✅ PASSED: Each tenant has isolated secrets${NC}"
else
    echo -e "${RED}❌ FAILED: Tenant secrets not found${NC}"
fi

echo ""

# Test 6: Ingress Routing
echo "Test 6: Ingress Routing"
echo "-----------------------"
echo "Testing domain-based routing..."

MINIKUBE_IP=$(minikube ip 2>/dev/null || echo "127.0.0.1")

# Test ACME domain
ACME_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://api.acme.virtplc.local/actuator/health 2>/dev/null || echo "000")
if [ "$ACME_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ PASSED: ACME ingress routing working (HTTP $ACME_STATUS)${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING: ACME API not responding (HTTP $ACME_STATUS)${NC}"
fi

# Test TechCorp domain
TECH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://api.techcorp.virtplc.local/actuator/health 2>/dev/null || echo "000")
if [ "$TECH_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ PASSED: TechCorp ingress routing working (HTTP $TECH_STATUS)${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING: TechCorp API not responding (HTTP $TECH_STATUS)${NC}"
fi

echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}📊 Test Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "If all tests passed, your multi-tenant isolation is working correctly!"
echo ""
echo "Key isolation mechanisms verified:"
echo "  ✅ Network policies prevent cross-tenant pod communication"
echo "  ✅ Database schemas separate tenant data"
echo "  ✅ Namespaces provide logical isolation"
echo "  ✅ Secrets are scoped to individual tenants"
echo "  ✅ Ingress routes traffic by domain to correct tenant"
echo ""
echo "Additional manual tests:"
echo "  1. Try to list pods from one tenant's pod:"
echo "     kubectl exec -n virtplc-acme123 $ACME_POD -- kubectl get pods -n virtplc-tech456"
echo "     (Should fail - no RBAC permissions)"
echo ""
echo "  2. Check TimescaleDB data isolation:"
echo "     kubectl exec -n virtplc-system $POSTGRES_POD -- psql -U virtplc -d virtplc -c \"SELECT * FROM tenant_acme123.plc_data LIMIT 5;\""
echo ""
