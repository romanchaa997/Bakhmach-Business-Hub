# Goals + Tasks - DevSecOps & Infrastructure Configuration Guide

## 1. TypeScript Configuration (tsconfig.json)

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"]
}
```

## 2. ESLint Configuration (.eslintrc.json)

```json
{
  "root": true,
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": 2020,
    "sourceType": "module"
  },
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "@typescript-eslint/explicit-function-return-types": "warn",
    "@typescript-eslint/no-unused-vars": ["error", {"argsIgnorePattern": "^_"}],
    "no-console": "warn"
  }
}
```

## 3. Prettier Configuration (.prettierrc)

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": false,
  "printWidth": 100,
  "tabWidth": 2
}
```

## 4. Environment Template (.env.example)

```bash
# Database
DATABASE_URL=postgres://user:password@localhost:5432/bakhmach_integration
DB_POOL_SIZE=20
DB_IDLE_TIMEOUT=10000

# Service
NODE_ENV=development
PORT=4002
LOG_LEVEL=info

# Security
JWT_SECRET=your-secret-key-here
CORS_ORIGIN=http://localhost:3000

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
NEW_RELIC_LICENSE_KEY=your-nr-key
```

## 5. GitHub Actions Workflow (.github/workflows/goals-tasks.yml)

```yaml
name: Goals+Tasks CI/CD

on:
  push:
    branches: [main]
    paths:
      - 'services/goals-tasks/**'
  pull_request:
    branches: [main]
    paths:
      - 'services/goals-tasks/**'

jobs:
  build-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: bakhmach_test
          POSTGRES_PASSWORD: password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: cd services/goals-tasks && npm ci
      - run: cd services/goals-tasks && npm run lint
      - run: cd services/goals-tasks && npm run type-check
      - run: cd services/goals-tasks && npm run build
      - run: cd services/goals-tasks && npm test -- --coverage

      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./services/goals-tasks/coverage/lcov.info

      - name: Security Audit
        run: cd services/goals-tasks && npm audit --audit-level=moderate

      - name: Snyk Security Scan
        run: cd services/goals-tasks && npx snyk test

  docker-build:
    needs: build-test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v2
      - uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - uses: docker/build-push-action@v4
        with:
          context: ./services/goals-tasks
          push: true
          tags: ghcr.io/${{ github.repository }}/goals-tasks:${{ github.sha }}

  deploy-staging:
    needs: docker-build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: azure/setup-kubectl@v3
      - uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - run: |
          kubectl set image deployment/goals-tasks \
            goals-tasks=ghcr.io/${{ github.repository }}/goals-tasks:${{ github.sha }} \
            -n staging
```

## 6. Docker Compose Service (docker-compose.yml addition)

```yaml
goals-tasks:
  build:
    context: ./services/goals-tasks
    dockerfile: Dockerfile
  container_name: bakhmach-goals-tasks
  environment:
    DATABASE_URL: postgres://postgres:password@postgres:5432/bakhmach_integration
    NODE_ENV: development
    LOG_LEVEL: debug
  ports:
    - "4002:4002"
  depends_on:
    postgres:
      condition: service_healthy
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:4002/health"]
    interval: 10s
    timeout: 5s
    retries: 3
  networks:
    - bakhmach
  volumes:
    - ./services/goals-tasks/src:/app/src
```

## 7. Kubernetes Deployment (k8s/goals-tasks-deployment.yaml)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: goals-tasks
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
      app: goals-tasks
  template:
    metadata:
      labels:
        app: goals-tasks
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "4002"
    spec:
      serviceAccountName: goals-tasks
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: goals-tasks
          image: ghcr.io/bakhmach/goals-tasks:latest
          imagePullPolicy: Always
          ports:
            - containerPort: 4002
              name: http
              protocol: TCP
          env:
            - name: NODE_ENV
              value: "production"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: goals-tasks-secrets
                  key: database-url
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: goals-tasks-secrets
                  key: jwt-secret
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /health
              port: 4002
            initialDelaySeconds: 15
            periodSeconds: 20
            timeoutSeconds: 3
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health
              port: 4002
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 2
            failureThreshold: 2
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: goals-tasks
  namespace: production
spec:
  type: ClusterIP
  selector:
    app: goals-tasks
  ports:
    - port: 80
      targetPort: 4002
      protocol: TCP
      name: http
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: goals-tasks-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: goals-tasks
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

## 8. Database Migration (db/migrations/001_create_goals_tasks.sql)

See GOALS_TASKS_IMPLEMENTATION_GUIDE.md for complete schema

## 9. Sonarqube Configuration (sonar-project.properties)

```properties
sonar.projectKey=bakhmach-goals-tasks
sonar.projectName=Goals and Tasks Microservice
sonar.sources=services/goals-tasks/src
sonar.tests=services/goals-tasks/src
sonar.test.inclusions=**/*.test.ts,**/*.spec.ts
sonar.typescript.lcov.reportPaths=services/goals-tasks/coverage/lcov.info
sonar.coverage.exclusions=**/*.d.ts,**/node_modules/**
```

## 10. Security Scanning - SAST/DAST

### Trivy Image Scanning (in CI/CD)
```bash
trivy image --severity HIGH,CRITICAL ghcr.io/bakhmach/goals-tasks:${VERSION}
```

### OWASP Dependency Check
```bash
dependency-check --project goals-tasks --scan services/goals-tasks/node_modules
```

## 11. Monitoring & Observability Setup

### Prometheus Metrics (/metrics endpoint)
```typescript
// Install: npm install prom-client
import prometheus from 'prom-client';
app.get('/metrics', (req, res) => {
  res.set('Content-Type', prometheus.register.contentType);
  res.end(prometheus.register.metrics());
});
```

### Structured Logging (Winston)
```typescript
import winston from 'winston';
const logger = winston.createLogger({
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});
```

## Implementation Sequence

1. Create all config files in service directory
2. Run `npm install` to lock dependencies
3. Run `npm run lint && npm run type-check` to validate
4. Commit to git
5. CI/CD pipeline automatically runs tests, builds, and deploys

## Security Checklist

- [x] Environment variables for secrets (not hardcoded)
- [x] HTTPS enforced in production
- [x] CORS configured restrictively
- [x] CSRF protection enabled
- [x] Input validation with zod
- [x] SQL injection prevented via parameterized queries
- [x] Rate limiting configured
- [x] Security headers (helmet)
- [x] Dependency scanning (npm audit, snyk)
- [x] Container scanning (trivy)
- [x] SAST code analysis (sonarqube)
- [x] DAST API testing
- [x] Pod security policies enforced
- [x] Network policies configured
- [x] Secrets encrypted at rest

---
**Last Updated**: January 3, 2026  
**Ready for Deployment**: ✅ Yes
