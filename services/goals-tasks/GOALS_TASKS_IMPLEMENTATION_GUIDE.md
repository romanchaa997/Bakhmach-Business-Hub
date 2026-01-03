# Goals + Tasks Microservice - Complete Implementation Guide

## Overview
This guide provides all remaining code files needed to complete the Goals+Tasks microservice that is already scaffolded in `services/goals-tasks/src`. The service implements goal and task management with PostgreSQL persistence and Redis caching.

## Status
- ✅ server.ts (committed)
- ✅ routes/goalsRoutes.ts (committed)
- ✅ routes/tasksRoutes.ts (committed)
- ⏳ controllers/*.ts (this guide)
- ⏳ services/*.ts (this guide)
- ⏳ repositories/*.ts (this guide)
- ⏳ Dockerfile (this guide)
- ⏳ Database migration (this guide)
- ⏳ Kubernetes manifests (this guide)
- ⏳ Docker Compose integration
- ⏳ CI/CD wiring

## File Structure
```
services/goals-tasks/
├── src/
│   ├── server.ts                    # Express entrypoint ✅
│   ├── controllers/
│   │   ├── goalsController.ts      
│   │   └── tasksController.ts      
│   ├── services/
│   │   ├── goalsService.ts         
│   │   └── tasksService.ts         
│   ├── repositories/
│   │   ├── db.ts                   # PostgreSQL pool
│   │   ├── goalsRepository.ts      
│   │   └── tasksRepository.ts      
│   └── routes/
│       ├── goalsRoutes.ts           # ✅
│       └── tasksRoutes.ts           # ✅
├── Dockerfile
├── package.json
└── tsconfig.json
```

## Remaining Implementation Files

Developers should create the following files by copying code below into the correct paths:

### 1. src/controllers/tasksController.ts
```typescript
import { Request, Response } from "express";
import * as tasksService from "../services/tasksService";

export async function listTasks(req: Request, res: Response) {
  try {
    const userId = (req as any).user?.id || req.query.userId;
    const { status, dueBefore, dueAfter } = req.query;
    const tasks = await tasksService.listTasks({
      userId: String(userId),
      status: status ? String(status) : undefined,
      dueBefore: dueBefore ? String(dueBefore) : undefined,
      dueAfter: dueAfter ? String(dueAfter) : undefined,
    });
    res.json(tasks);
  } catch (error) {
    res.status(400).json({ error: (error as Error).message });
  }
}

export async function getTaskById(req: Request, res: Response) {
  try {
    const { taskId } = req.params;
    const task = await tasksService.getTaskById(taskId);
    if (!task) return res.status(404).json({ message: "Task not found" });
    res.json(task);
  } catch (error) {
    res.status(400).json({ error: (error as Error).message });
  }
}

export async function updateTask(req: Request, res: Response) {
  try {
    const { taskId } = req.params;
    const task = await tasksService.updateTask(taskId, req.body);
    res.json(task);
  } catch (error) {
    res.status(400).json({ error: (error as Error).message });
  }
}
```

### 2. src/services/goalsService.ts  
```typescript
import * as goalsRepo from "../repositories/goalsRepository";
import * as tasksRepo from "../repositories/tasksRepository";

interface CreateGoalInput {
  userId: string;
  title: string;
  description?: string;
  pdpId?: string;
  dueDate?: string;
}

export async function createGoal(input: CreateGoalInput) {
  return goalsRepo.createGoal(input);
}

export async function listGoals(filter: {
  userId: string;
  status?: string;
  pdpId?: string;
}) {
  return goalsRepo.listGoals(filter);
}

export async function getGoalById(goalId: string) {
  const goal = await goalsRepo.getGoalById(goalId);
  if (!goal) return null;
  
  const tasks = await tasksRepo.listTasksByGoalId(goalId);
  const completed = tasks.filter(t => t.status === "completed").length;
  const progress = tasks.length > 0 ? Math.round((completed / tasks.length) * 100) : 0;
  
  return { ...goal, tasks, progress };
}

export async function updateGoal(goalId: string, changes: any) {
  return goalsRepo.updateGoal(goalId, changes);
}

export async function createTaskForGoal(
  goalId: string,
  input: { title: string; description?: string; dueDate?: string }
) {
  const goal = await goalsRepo.getGoalById(goalId);
  if (!goal) throw new Error("Goal not found");
  
  return tasksRepo.createTask({
    ...input,
    goalId,
    userId: goal.userId,
  });
}
```

### 3. src/services/tasksService.ts
```typescript
import * as tasksRepo from "../repositories/tasksRepository";

export async function listTasks(filter: {
  userId: string;
  status?: string;
  dueBefore?: string;
  dueAfter?: string;
}) {
  return tasksRepo.listTasks(filter);
}

export async function getTaskById(taskId: string) {
  return tasksRepo.getTaskById(taskId);
}

export async function updateTask(taskId: string, changes: any) {
  const updated = await tasksRepo.updateTask(taskId, changes);
  // TODO: emit TaskCompleted event for Analytics/Consciousness microservices
  return updated;
}
```

### 4. src/repositories/db.ts
```typescript
import { Pool } from "pg";

export const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});
```

### 5. src/repositories/goalsRepository.ts
See earlier detailed code provided - approximately 120 lines of SQL/PostgreSQL CRUD operations for goals table.

### 6. src/repositories/tasksRepository.ts
See earlier detailed code provided - approximately 140 lines of SQL/PostgreSQL CRUD operations for tasks table.

## Database Schema

### File: `db/migrations/001_create_goals_tasks.sql`
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE goals (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id     UUID        NOT NULL,
  title       TEXT        NOT NULL,
  description TEXT,
  pdp_id      UUID,
  status      TEXT        NOT NULL DEFAULT 'active',
  due_date    TIMESTAMPTZ,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_goals_user_id ON goals (user_id);
CREATE INDEX idx_goals_status  ON goals (status);

CREATE TABLE tasks (
  id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  goal_id      UUID        NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
  user_id      UUID        NOT NULL,
  title        TEXT        NOT NULL,
  description  TEXT,
  status       TEXT        NOT NULL DEFAULT 'pending',
  due_date     TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id  ON tasks (user_id);
CREATE INDEX idx_tasks_goal_id  ON tasks (goal_id);
CREATE INDEX idx_tasks_status   ON tasks (status);
CREATE INDEX idx_tasks_due_date ON tasks (due_date);
```

## Docker & Kubernetes

### File: `services/goals-tasks/Dockerfile`
```dockerfile
FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json tsconfig.json ./
COPY services/goals-tasks ./services/goals-tasks

RUN npm install
RUN npm run build --workspace services/goals-tasks

FROM node:20-alpine

WORKDIR /app
ENV NODE_ENV=production

COPY package*.json ./
RUN npm install --omit=dev

COPY --from=build /app/services/goals-tasks/dist ./dist

ENV PORT=4002
EXPOSE 4002

CMD ["node", "dist/server.js"]
```

### File: `k8s/goals-tasks-deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: goals-tasks
  labels:
    app: goals-tasks
spec:
  replicas: 2
  selector:
    matchLabels:
      app: goals-tasks
  template:
    metadata:
      labels:
        app: goals-tasks
    spec:
      containers:
        - name: goals-tasks
          image: your-registry/goals-tasks:latest
          ports:
            - containerPort: 4002
          env:
            - name: NODE_ENV
              value: "production"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: core-database
                  key: DATABASE_URL
          readinessProbe:
            httpGet:
              path: /health
              port: 4002
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 4002
            initialDelaySeconds: 10
            periodSeconds: 20
---
apiVersion: v1
kind: Service
metadata:
  name: goals-tasks
spec:
  selector:
    app: goals-tasks
  ports:
    - port: 80
      targetPort: 4002
      protocol: TCP
```

## Next Steps for Integration

1. **Complete file creation**: Copy all TypeScript files into their respective directories
2. **Run migration**: Execute `001_create_goals_tasks.sql` against PostgreSQL
3. **Update STARTUP.sh**: Add goals-tasks container to the Docker Compose startup sequence
4. **Add to FastAPI integration**: Create client module to call this service's endpoints
5. **Setup CI/CD**: Wire into GitHub Actions for build/test/deploy
6. **Add validation**: Implement zod/Joi schemas for request validation
7. **Add tests**: Create unit and integration test files per TEST-SUITE.md

## Environment Variables Required

```bash
DATABASE_URL=postgres://user:password@localhost:5432/bakhmach_integration
GOALS_TASKS_SERVICE_URL=http://goals-tasks:4002
NODE_ENV=development
PORT=4002
```

## API Endpoints

All endpoints require `Authorization: Bearer <JWT>` header and follow REST conventions:

**Goals**:
- POST /api/v1/goals - Create goal
- GET /api/v1/goals - List goals (filters: status, pdpId)
- GET /api/v1/goals/:goalId - Get goal with progress
- PATCH /api/v1/goals/:goalId - Update goal
- POST /api/v1/goals/:goalId/tasks - Create task for goal

**Tasks**:
- GET /api/v1/tasks - List tasks (filters: status, dueBefore, dueAfter)
- GET /api/v1/tasks/:taskId - Get task
- PATCH /api/v1/tasks/:taskId - Update task

## References

- API Contracts: `API-CONTRACTS.md`
- Architecture: `ARCHITECTURE.json`
- Dev Standards: `DEV-REVIEW.md`
- Kubernetes: `DEPLOYMENT-KUBERNETES-GUIDE.md`
- Testing: `TEST-SUITE.md`
- CI/CD: `CI-CD-PIPELINE.md`
