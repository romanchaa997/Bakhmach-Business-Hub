# CI/CD Pipeline & Deployment Automation

## Overview
Automated continuous integration, continuous deployment, and infrastructure-as-code pipeline for Bakhmach Business Hub using GitHub Actions, Docker, and Kubernetes.

## Pipeline Architecture

### GitHub Actions Workflow

```yaml
# .github/workflows/main.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # Stage 1: Build
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18.x'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build application
        run: npm run build
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build
          path: dist/
  
  # Stage 2: Test
  test:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18.x'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run unit tests
        run: npm run test:unit
      
      - name: Run integration tests
        run: npm run test:integration
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
  
  # Stage 3: Security Scanning
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Snyk security scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      
      - name: SAST with SonarQube
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
  
  # Stage 4: Build Docker Image
  docker:
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKER_USERNAME }}/bakhmach-hub:latest
            ${{ secrets.DOCKER_USERNAME }}/bakhmach-hub:${{ github.sha }}
          cache-from: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/bakhmach-hub:buildcache
          cache-to: type=registry,ref=${{ secrets.DOCKER_USERNAME }}/bakhmach-hub:buildcache,mode=max
  
  # Stage 5: Deploy
  deploy:
    runs-on: ubuntu-latest
    needs: docker
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure kubectl
        run: |
          mkdir -p $HOME/.kube
          echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > $HOME/.kube/config
          chmod 600 $HOME/.kube/config
      
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/bakhmach-backend \
            bakhmach-backend=${{ secrets.DOCKER_USERNAME }}/bakhmach-hub:${{ github.sha }} \
            -n production
          kubectl rollout status deployment/bakhmach-backend -n production
      
      - name: Run smoke tests
        run: npm run test:smoke
      
      - name: Notify deployment
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ Deployed to production'
            })
```

## Docker Build Optimization

### Multi-stage Dockerfile
```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Test stage
FROM builder AS tester
RUN npm ci
COPY . .
RUN npm run test:ci

# Runtime stage
FROM node:18-alpine AS runtime
WORKDIR /app
RUN apk add --no-cache dumb-init
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package*.json ./

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s \
  CMD node healthcheck.js

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/index.js"]
```

## Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bakhmach-backend
  namespace: production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: bakhmach-backend
  template:
    metadata:
      labels:
        app: bakhmach-backend
    spec:
      containers:
      - name: bakhmach-backend
        image: romanchaa997/bakhmach-hub:latest
        ports:
        - containerPort: 8080
        env:
        - name: NODE_ENV
          value: production
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
```

## Database Migrations

```typescript
// migrations/1704197400000_initial_schema.ts
export async function up(db) {
  await db.createTable('users', {
    id: { type: 'uuid', primaryKey: true },
    email: { type: 'varchar', unique: true },
    created_at: { type: 'timestamp', default: 'now()' }
  });
}

export async function down(db) {
  await db.dropTable('users');
}
```

## Environment Management

```yaml
# Environment-specific configs
environments:
  development:
    database: postgresql://localhost/bakhmach_dev
    redis: redis://localhost:6379/0
    log_level: debug
  
  staging:
    database: postgresql://staging-db/bakhmach
    redis: redis://staging-cache:6379/0
    log_level: info
  
  production:
    database: postgresql://prod-db/bakhmach
    redis: redis://prod-cache:6379/0
    log_level: warn
```

## Testing Strategy

### Test Coverage Requirements
- **Unit Tests**: 80%+ coverage
- **Integration Tests**: All API endpoints
- **E2E Tests**: Critical user flows
- **Performance Tests**: > 99th percentile latency < 500ms

```bash
# Test commands
npm run test:unit      # Jest unit tests
npm run test:int       # Integration tests
npm run test:e2e       # Cypress E2E tests
npm run test:perf      # k6 performance tests
npm run test:ci        # All tests with coverage
```

## Deployment Checklist

- [ ] All tests passing (unit, integration, E2E)
- [ ] Code coverage > 80%
- [ ] Security scan passed
- [ ] Performance tests passed
- [ ] Database migrations ready
- [ ] Environment variables configured
- [ ] Secrets properly encrypted
- [ ] Docker image built and pushed
- [ ] Kubernetes manifests validated
- [ ] Monitoring/alerting configured
- [ ] Rollback plan documented
- [ ] Team notified of deployment

## Rollback Procedure

```bash
# Immediate rollback
kubectl rollout undo deployment/bakhmach-backend -n production

# Check rollout history
kubectl rollout history deployment/bakhmach-backend -n production

# Rollback to specific revision
kubectl rollout undo deployment/bakhmach-backend --to-revision=5 -n production
```

## Pipeline Metrics

- **Build Time**: < 5 minutes
- **Test Execution**: < 10 minutes
- **Deployment Time**: < 3 minutes
- **Rollback Time**: < 1 minute
- **Success Rate**: > 95%

## Best Practices

1. **Immutable container images**: Version by commit hash
2. **Secret management**: Never commit secrets to git
3. **Automated rollback**: On failed health checks
4. **Progressive deployment**: Canary → Staging → Production
5. **Infrastructure as Code**: All infrastructure versioned
6. **Monitoring**: Real-time deployment insights
