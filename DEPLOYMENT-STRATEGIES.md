# Deployment Strategies & Rollback Procedures

## Overview
Advanced deployment strategies for Bakhmach Business Hub including blue-green deployments, canary releases, and automated rollback procedures.

## Blue-Green Deployment

### Architecture
```
Production Traffic (100%)
         ↓
    Load Balancer
      ↙       ↘
   Blue      Green
 (Current)  (New)
```

### Process
1. Deploy new version to Green environment
2. Run smoke tests and validation
3. Switch load balancer to Green (instantaneous)
4. Monitor metrics for 5-10 minutes
5. If issues: Switch back to Blue
6. Keep Blue as rollback target for 24 hours

### Benefits
- Zero-downtime deployments
- Instant rollback capability
- Easy health verification
- Minimal risk

```bash
# Switch traffic to green
kubectl patch service bakhmach-backend \
  -p '{"spec":{"selector":{"version":"green"}}}'

# Monitor for issues
sleep 600

# If needed, rollback to blue
kubectl patch service bakhmach-backend \
  -p '{"spec":{"selector":{"version":"blue"}}}'
```

## Canary Deployment

### Release Process
```
Phase 1: 5% Traffic  (5 min)
Phase 2: 25% Traffic (10 min)
Phase 3: 50% Traffic (15 min)
Phase 4: 100% Traffic
```

### Automated Canary with Flagger

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: bakhmach-canary
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: bakhmach-backend
  service:
    port: 8080
  analysis:
    interval: 1m
    threshold: 5
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
    - name: request-duration
      thresholdRange:
        max: 500
  stages:
  - weight: 5
    duration: 5m
  - weight: 25
    duration: 10m
  - weight: 50
    duration: 15m
```

### Monitoring During Canary
- Error rate < 0.1%
- p95 latency < 500ms
- No critical alerts

## Rolling Deployment

### Kubernetes Rolling Update

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bakhmach-backend
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1          # 1 extra pod
      maxUnavailable: 0    # No unavailable pods
  selector:
    matchLabels:
      app: bakhmach-backend
  template:
    # ... pod spec
```

### Timeline
- Pod 1 → New version (Pod 5 spins up)
- Pod 2 → New version (Pod 4 spins up)
- Pod 3 → New version (Pod 6 spins up)
- All traffic moved gradually

## Rollback Strategies

### Automatic Rollback

```yaml
# If health check fails, auto-rollback
lifecycle:
  readinessProbe:
    httpGet:
      path: /health
      port: 8080
    failureThreshold: 3  # Trigger rollback after 3 failures
```

### Manual Rollback

```bash
# Check rollout history
kubectl rollout history deployment/bakhmach-backend

# Rollback to previous version
kubectl rollout undo deployment/bakhmach-backend

# Rollback to specific revision
kubectl rollout undo deployment/bakhmach-backend --to-revision=5

# Check rollout status
kubectl rollout status deployment/bakhmach-backend
```

## Deployment Checklist

### Pre-Deployment
- [ ] Code reviewed and approved
- [ ] All tests passing
- [ ] Database migrations tested
- [ ] Performance benchmarks acceptable
- [ ] Security scan passed
- [ ] Monitoring configured
- [ ] Rollback plan documented
- [ ] Team notified

### During Deployment
- [ ] Monitor error rates
- [ ] Track latency metrics
- [ ] Watch database connections
- [ ] Monitor CPU/memory usage
- [ ] Check log for anomalies

### Post-Deployment
- [ ] Confirm metrics stable
- [ ] Run smoke tests
- [ ] Verify feature functionality
- [ ] Update deployment record
- [ ] Document any issues

## Deployment Windows

| Environment | Weekday | Weekend | Maintenance |
|-------------|---------|---------|-------------|
| Development | Anytime | Anytime | N/A |
| Staging | Anytime | Limited | Tuesday 2-4 AM |
| Production | Off-peak | Avoided | Sunday 2-4 AM |

## Incident Response

### Deployment Failed
1. **Immediate**: Rollback to previous version
2. **Analysis**: Identify root cause
3. **Fix**: Apply hotfix
4. **Retest**: Verify in staging
5. **Redeploy**: With additional monitoring

### Critical Issue in Production
1. **Rollback**: Instant rollback
2. **Alert**: Notify team immediately
3. **Investigation**: Post-mortem process
4. **Prevention**: Add safeguards

## Best Practices

1. **Test in staging first**: Always mirror production
2. **Deploy during business hours**: For faster response
3. **Have rollback ready**: Before hitting deploy
4. **Monitor actively**: First 30 minutes critical
5. **Communicate**: Keep team informed
6. **Document**: Record all deployments
7. **Automate**: Reduce manual errors
