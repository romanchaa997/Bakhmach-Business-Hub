# CI/CD Policy & Governance

## Policy Matrix: Change Types & Required Checks

| Change Type | Auto‑Merge | Required Checks | Manual Review | Notes |
|------------|-----------|-----------------|---------------|-------|
| **docs** | ✅ possible | lint, links | optional | no prod deploy, low risk |
| **refactor** | ❌ no | unit tests, perf baseline | required | backend/ml/services must pass SLO |
| **feature** | ❌ no | unit + integration tests, perf, SLO gates | required | approval needed + consciousness check |
| **security** | ❌ no | security scan, unit tests, threat review | required | security label + approval |
| **infra** | ❌ no | integration tests, deployment dry-run | required | DevOps approval required |
| **ml-model** | ❌ no | model tests, drift check, metric validation | required | ML + prod team approval |

## Change Type Detection

Commit messages should include prefixes for routing:
```
docs: update README with new API endpoints
refactor: optimize database query in services/
feat: add payment reminder service for debt-companion
security: add CSRF protection to auth endpoints
infra: upgrade Node.js runtime to 20.x
ml: retrain user-risk-model with new data
```

## Automation Levels

### Level 1: Auto-Merge Candidates
- Documentation updates (docs/)
- Non-functional changes (comments, formatting)
- Version bumps for dependencies (with security clearance)

### Level 2: Require Consciousness Check
- Feature branches with SLO pass
- Infrastructure changes with dry-run success
- ML model updates with drift validation

Requires: `consciousness_guard.py` approval

### Level 3: Require Explicit Approval
- Security changes
- Critical path modifications (auth, payment, data-handling)
- Breaking API changes

Requires: team review + consciousness clearance

## SLO Gates

All code changes must pass domain-specific SLO checks:

**Backend (TypeScript/Node):**
- Unit test coverage ≥ 80%
- Integration tests pass
- Performance regression < 5% on perf baseline
- No security issues (trivy/snyk)

**ML (Python):**
- Data quality checks pass
- Model tests pass
- Feature store consistency check
- No data drift beyond threshold

**Services:**
- Integration tests pass
- Load test p95 latency < SLO threshold
- Error rate < 0.5%

## Consciousness Guard Integration

Before merging, `consciousness_guard.py` evaluates:

```
Integration Score (from code/ml/services): ≥ medium
Well-being Score (from workflow/PDP): ≥ medium
Stability Score (recent incidents): ≥ high
```

If any score is LOW → requires manual approval

## Policy Enforcement via GitHub Actions

Main workflow: `.github/workflows/policy-gate.yml`

1. Detect change type from commit message/PR labels
2. Run required checks based on matrix
3. Evaluate domain SLOs
4. Call `consciousness_guard.py`
5. Auto-merge or request review per policy

## Rollback Policy

Automatic rollback triggers:
- Error rate spike > 5% sustained for 5 min
- SLO violation (p95 latency > 2x threshold)
- Consciousness stability score drops below threshold

Rollback action: revert to previous stable commit + create incident issue
