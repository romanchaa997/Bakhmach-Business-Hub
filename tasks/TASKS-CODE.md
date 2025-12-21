# Code Tasks Backlog

## Meta
- domain: code
- focus_period: 2025-12
- strategic_goal: "Performance-first foundation with automated profiling and optimization"

---

## Task T-CODE-001
title: Set up profiling framework
priority: P0
domain: code
milestone: "Code: Profiling framework"
readiness_delta: 10
time_estimate_h: 6
status: planned
deps: []

## Task T-CODE-002
title: CI/CD pipeline foundation
priority: P0
domain: code
milestone: "Code: CI/CD"
readiness_delta: 8
time_estimate_h: 8
status: planned
deps: []

## Task T-CODE-003
title: Memory management guidelines & linting
priority: P1
domain: code
milestone: "Code: Optimization"
readiness_delta: 5
time_estimate_h: 4
status: planned
deps: ["T-CODE-001"]

## Task T-CODE-004
title: Parallelization baseline
priority: P1
domain: code
milestone: "Code: Performance"
readiness_delta: 7
time_estimate_h: 6
status: planned
deps: ["T-CODE-001"]

## Task T-CODE-005
title: Code review checklist for performance
priority: P1
domain: code
milestone: "Code: Workflow"
readiness_delta: 3
time_estimate_h: 3
status: planned
deps: []

## Task T-CODE-006
title: Infrastructure-as-Code (Terraform/Pulumi)
priority: P2
domain: code
milestone: "Code: Infrastructure"
readiness_delta: 6
time_estimate_h: 10
status: planned
deps: ["T-CODE-002"]

## Task T-CODE-007
title: Algorithmic efficiency audit
priority: P2
domain: code
milestone: "Code: Audit"
readiness_delta: 4
time_estimate_h: 8
status: planned
deps: ["T-CODE-001"]

## Task T-CODE-008
title: Static analysis (SonarCloud/CodeQL)
priority: P2
domain: code
milestone: "Code: Quality"
readiness_delta: 4
time_estimate_h: 4
status: planned
deps: ["T-CODE-002"]

## Task T-CODE-009
title: Low-level optimization (Cython/Rust bindings)
priority: P3
domain: code
milestone: "Code: Advanced Performance"
readiness_delta: 5
time_estimate_h: 12
status: planned
deps: ["T-CODE-007"]
