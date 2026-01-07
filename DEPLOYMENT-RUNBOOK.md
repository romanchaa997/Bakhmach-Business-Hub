# DEPLOYMENT RUNBOOK & OPERATIONAL GUIDE

## Quick Start Production Deployment

### Prerequisites Checklist
- [ ] Kubernetes clusters provisioned (dev, staging, prod)
- [ ] Container registry configured (GitHub Container Registry)
- [ ] DNS records configured for all 6 contexts
- [ ] SSL certificates issued (Let's Encrypt)
- [ ] Database backups tested
- [ ] All secrets stored in Sealed Secrets
- [ ] Team access to kubectl configured
- [ ] Monitoring stack deployed
- [ ] Disaster recovery plan reviewed
- [ ] Security audit completed

### Phase 1: Infrastructure Setup (Week 1)

#### Step 1.1: Provision Kubernetes Cluster
```bash
# Using Azure Kubernetes Service (AKS)
az aks create \\
  --resource-group bakhmach-prod \\
  --name bakhmach-prod-cluster \\
  --node-count 15 \\
  --vm-set-type VirtualMachineScaleSets \\
  --load-balancer-sku standard \\
  --enable-managed-identity \\
  --network-plugin azure

# Get credentials
az aks get-credentials --resource-group bakhmach-prod --name bakhmach-prod-cluster
```

#### Step 1.2: Install Service Mesh (Istio)
```bash
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm install istio-base istio/base --namespace istio-system --create-namespace
helm install istiod istio/istiod --namespace istio-system
helm install istio-ingress istio/gateway --namespace istio-ingress --create-namespace
```

#### Step 1.3: Install Monitoring Stack
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \\
  --namespace monitoring --create-namespace \\
  --values monitoring-values.yaml
```

### Phase 2: Deploy Core Services (Week 2-3)

#### Step 2.1: Create Namespace
```bash
kubectl create namespace bakhmach-prod
kubectl label namespace bakhmach-prod istio-injection=enabled
```

#### Step 2.2: Deploy Auth Service
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/deployment-manifests.yaml

# Verify rollout
kubectl rollout status deployment/auth-service -n bakhmach-prod

# Check pod health
kubectl get pods -n bakhmach-prod -l app=auth-service
kubectl logs -f deployment/auth-service -n bakhmach-prod
```

#### Step 2.3: Deploy Business Context Services
```bash
# Deploy all 6 context services
for service in bakhmach-core slon-finance audityzer-audit debt-agent-ai trade-connector infusion-processor; do
  kubectl rollout status deployment/$service -n bakhmach-prod
done
```

#### Step 2.4: Configure Service Mesh Routes
```bash
# Apply VirtualService and Gateway resources
kubectl apply -f k8s/istio-config.yaml

# Verify traffic routing
kubectl get virtualservices -n bakhmach-prod
kubectl get gateways -n bakhmach-prod
```

### Phase 3: Data Migration & Validation (Week 4)

#### Step 3.1: Backup Current Data
```bash
# PostgreSQL backup
kubectl exec -it <postgres-pod> -n bakhmach-prod -- \\
  pg_dump -U postgres bakhmach_db > backup-$(date +%Y%m%d).sql

# MongoDB backup
kubectl exec -it <mongo-pod> -n bakhmach-prod -- \\
  mongodump --out /backup/$(date +%Y%m%d)
```

#### Step 3.2: Validate Data Consistency
```bash
# Run integrity checks
kubectl exec -it deployment/audityzer-audit -n bakhmach-prod -- \\
  python /app/scripts/data-validation.py
```

#### Step 3.3: Test Failover
```bash
# Simulate pod failure
kubectl delete pod -l app=auth-service -n bakhmach-prod

# Verify recovery
kubectl get pods -n bakhmach-prod -l app=auth-service
kubectl logs -f deployment/auth-service -n bakhmach-prod | head -20
```

### Phase 4: Production Cutover (Week 5)

#### Step 4.1: DNS Cutover
```bash
# Update DNS to point to new ingress IP
NEW_IP=$(kubectl get service istio-ingress -n istio-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Update DNS records (use your DNS provider)
# bakhmach.prod -> $NEW_IP
# slon.prod -> $NEW_IP
# etc...
```

#### Step 4.2: Enable Auto-Scaling
```bash
# Apply HPA configs
kubectl apply -f k8s/hpa-config.yaml

# Verify HPA status
kubectl get hpa -n bakhmach-prod
```

#### Step 4.3: Run Smoke Tests
```bash
#!/bin/bash
echo "Testing API endpoints..."
curl -f https://bakhmach.prod/health
curl -f https://slon.prod/health
curl -f https://audityzer.prod/health
curl -f https://debt-agent.prod/health
curl -f https://trade.prod/health
curl -f https://infusion.prod/health

echo "All smoke tests passed!"
```

### Phase 5: Production Validation (Week 6+)

#### Step 5.1: Monitor Key Metrics
```bash
# Check error rates
kubectl port-forward svc/prometheus 9090:9090 -n monitoring &
# Visit: http://localhost:9090

# Query:
# rate(http_requests_total{status=~"5.."}[5m])
```

#### Step 5.2: Verify Business KPIs
```yaml
Checklist:
  - [ ] Bakhmach-Hub: Smart city connectivity > 99.8%
  - [ ] Slon Credit: Loan processing latency p95 < 5s
  - [ ] Audityzer-EU: Compliance score > 98%
  - [ ] DebtDefenseAgent: ML accuracy > 95%
  - [ ] Black Sea Corridor: Transaction success rate > 99.9%
  - [ ] Cannabis Infusion: Quality control pass rate > 98%
```

## Incident Response Procedures

### Service Degradation Alert
```bash
# 1. Identify affected service
kubectl top pods -n bakhmach-prod
kubectl top nodes

# 2. Check pod logs
kubectl logs deployment/<service-name> -n bakhmach-prod --tail=100

# 3. Scale up if CPU-bound
kubectl scale deployment <service-name> --replicas=5 -n bakhmach-prod

# 4. Restart if memory-bound
kubectl rollout restart deployment/<service-name> -n bakhmach-prod
```

### Database Connection Exhaustion
```bash
# 1. Check connection pool status
kubectl exec -it <postgres-pod> -- \\
  psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# 2. Kill long-running queries
kubectl exec -it <postgres-pod> -- \\
  psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE duration > '5 minutes';"

# 3. Increase pool size
kubectl set env deployment/<app> CONNECTION_POOL_SIZE=50 -n bakhmach-prod
```

### Failover Procedure
```bash
# 1. Detect primary failure
kubectl get pod <primary-pod> -n bakhmach-prod

# 2. Promote replica (PostgreSQL)
kubectl exec -it <replica-pod> -- \\
  pg_ctl promote -D /var/lib/postgresql/data

# 3. Restart affected services
kubectl rollout restart deployment/auth-service -n bakhmach-prod
kubectl rollout restart deployment/bakhmach-core -n bakhmach-prod

# 4. Verify new primary
kubectl exec -it <new-primary> -- \\
  psql -U postgres -c "SELECT pg_is_in_recovery();"
```

## Rollback Procedure

### Application Rollback
```bash
# 1. Check deployment history
kubectl rollout history deployment/auth-service -n bakhmach-prod

# 2. Rollback to previous version
kubectl rollout undo deployment/auth-service -n bakhmach-prod

# 3. Verify rollback
kubectl rollout status deployment/auth-service -n bakhmach-prod
```

### Database Rollback
```bash
# 1. Restore from backup
kubectl cp backup-20240120.sql <postgres-pod>:/tmp/ -n bakhmach-prod

kubectl exec -it <postgres-pod> -n bakhmach-prod -- \\
  psql -U postgres bakhmach_db < /tmp/backup-20240120.sql

# 2. Verify data integrity
kubectl exec -it <postgres-pod> -- \\
  psql -U postgres -c "SELECT COUNT(*) FROM users;"
```

## Maintenance Windows

### Drain Node for Maintenance
```bash
# 1. Cordon node (prevent new pods)
kubectl cordon <node-name>

# 2. Drain existing pods
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# 3. Perform maintenance
SSH to node, perform updates

# 4. Uncordon node
kubectl uncordon <node-name>
```

### Cluster Upgrade
```bash
# 1. Plan upgrade
kubectl version --short

# 2. Upgrade control plane
az aks upgrade --resource-group bakhmach-prod --name bakhmach-prod-cluster --kubernetes-version 1.28

# 3. Upgrade node pools
az aks nodepool upgrade --resource-group bakhmach-prod --cluster-name bakhmach-prod-cluster --name nodepool1 --kubernetes-version 1.28

# 4. Verify upgrade
kubectl get nodes
kubectl get pods --all-namespaces
```

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-20  
**Owner**: DevOps Team  
**Emergency Contact**: +1-XXX-XXX-XXXX  
**Status**: READY FOR PRODUCTION
