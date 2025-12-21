# ML Tasks Backlog

## Meta
- domain: ml
- focus_period: 2025-12
- strategic_goal: "End-to-end ML pipeline from raw data to basic prod inference"

---

## Task T-ML-001
title: Define core data sources and contracts
priority: P0
domain: ml
milestone: "ML: Data contracts & ingestion layer"
readiness_delta: 5
time_estimate_h: 4
status: planned
deps: []

## Task T-ML-002
title: Choose and scaffold feature store approach
priority: P0
domain: ml
milestone: "ML: Feature store setup"
readiness_delta: 7
time_estimate_h: 6
status: planned
deps: ["T-ML-001"]

## Task T-ML-003
title: Baseline training pipeline (batch)
priority: P1
domain: ml
milestone: "ML: Training & evaluation pipeline"
readiness_delta: 8
time_estimate_h: 8
status: planned
deps: ["T-ML-002"]

## Task T-ML-004
title: Simple inference service (CPU-only)
priority: P1
domain: ml
milestone: "ML: Inference API v0"
readiness_delta: 6
time_estimate_h: 6
status: planned
deps: ["T-ML-003"]

## Task T-ML-005
title: ML observability skeleton
priority: P2
domain: ml
milestone: "ML: Monitoring & drift alerts"
readiness_delta: 6
time_estimate_h: 6
status: planned
deps: ["T-ML-004"]

## Task T-ML-006
title: Experiment tracking standard
priority: P2
domain: ml
milestone: "ML: Reproducible experimentation"
readiness_delta: 3
time_estimate_h: 3
status: planned
deps: ["T-ML-003"]

## Task T-ML-007
title: Data quality checks v0
priority: P1
domain: ml
milestone: "ML: Data validation"
readiness_delta: 5
time_estimate_h: 4
status: planned
deps: ["T-ML-001"]

## Task T-ML-008
title: Model registry integration
priority: P1
domain: ml
milestone: "ML: Model registry"
readiness_delta: 5
time_estimate_h: 5
status: planned
deps: ["T-ML-003"]

## Task T-ML-009
title: Data drift detection v0
priority: P2
domain: ml
milestone: "ML: Drift monitoring"
readiness_delta: 4
time_estimate_h: 6
status: planned
deps: ["T-ML-005"]

## Task T-ML-010
title: AutoML exploration
priority: P3
domain: ml
milestone: "ML: R&D"
readiness_delta: 3
time_estimate_h: 10
status: planned
deps: ["T-ML-003"]
