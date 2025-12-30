# Real-Time Monitoring System

## Overview

Continuous metrics collection and visualization system for Bakhmach-Business-Hub. Monitors all domains (code, ML, services, workflow) and provides live alerts.

## Components

### `realtime_dashboard.py`

Main server that:
- Collects metrics from all domain JSON files every 30 seconds
- Evaluates alerts based on thresholds
- Maintains 60-minute rolling history
- Outputs console dashboard with key metrics
- Generates JSON reports for external consumption

**Usage:**
```bash
python monitoring/realtime_dashboard.py
```

**Output (every 30s):**
```
======================================================================
REALTIME DASHBOARD - 2025-12-30T04:00:00.123456
======================================================================
Integration: 70/100 | Well-being: 65/100 | Stability: 75/100
Mode: SAFE | Alerts: 2
SLO Status: PASS
======================================================================
```

## Metrics Collected

### Domain Metrics

**Backend (`code/perf/baseline.json`)**
- Test coverage %
- Performance regression %
- Test status (passed/failed)
- Last run timestamp

**ML (`ml/monitoring/metrics.json`)**
- Data drift score (0-1)
- Model accuracy
- Feature store readiness
- Last training timestamp

**Services (`services/readiness.json`)**
- P95 latency (ms)
- Error rate (%)
- SLO passing status
- Uptime %

### Consciousness Scores

Read from `.consciousness_report.json`:
- **Integration Score** (0-100): Cross-domain alignment
- **Well-being Score** (0-100): Personal capacity state
- **Stability Score** (0-100): System reliability
- **Mode**: FAST/SAFE/HALT

### SLO Status

Read from `.orchestrator_report.json`:
- Overall PASS/FAIL decision
- Per-domain status
- SLO gate violations

## Alerts & Thresholds

| Metric | Threshold | Severity | Action |
|--------|-----------|----------|--------|
| Consciousness Mode | HALT | CRITICAL | Trigger incident, block deployments |
| Integration Score | < 50 | WARNING | Require manual review |
| Code Coverage | < 75% | WARNING | Block merge |
| Service Error Rate | > 1.0% | CRITICAL | Auto-rollback |
| P95 Latency | > 300ms | WARNING | Trigger investigation |
| Data Drift | > 0.5 | WARNING | Schedule retraining |

## Real-Time Monitoring Loop

```
Every 30 seconds:
1. Collect metrics from JSON files
2. Read consciousness & orchestrator reports
3. Evaluate alerts (check thresholds)
4. Update metrics history (keep last 60 entries)
5. Print dashboard summary
6. Export to JSON for dashboards
```

## Dashboard JSON Format

```json
{
  "current": {
    "timestamp": "2025-12-30T04:00:00.123456",
    "domains": {
      "code": { "coverage": 82, "perf_regression": 1.5, ... },
      "ml": { "data_drift": 0.15, "model_accuracy": 0.92, ... },
      "services": { "p95_latency_ms": 145, "error_rate": 0.2, ... }
    },
    "consciousness_scores": {
      "integration": 70,
      "wellbeing": 65,
      "stability": 75,
      "mode": "SAFE"
    },
    "alerts": [
      {
        "severity": "WARNING",
        "message": "Integration score low: 45/100",
        "timestamp": "2025-12-30T04:00:00.123456"
      }
    ]
  },
  "history": [...],  // Last 30 metric snapshots
  "status": "running",
  "last_update": "2025-12-30T04:00:00.123456"
}
```

## Integration Points

### With Consciousness Guard

Dashboard monitors consciousness scores and triggers alerts when:
- Mode switches to HALT (auto-block deployments)
- Well-being drops below 50 (reduce automation)
- Integration score falls below 60 (manual review required)

### With CI/CD Pipeline

GitHub Actions can:
- Call `/monitoring/realtime_dashboard.py` before deployments
- Check alert count > 0 → block merge
- Store historical metrics in artifacts

### With Local Development

Run dashboard in background:
```bash
python monitoring/realtime_dashboard.py > monitoring.log 2>&1 &
```

## Extending Monitoring

Add new metrics by:
1. Create JSON metric file (e.g., `my_domain/metrics.json`)
2. Update `realtime_dashboard.py` → `collect_metrics()` method
3. Add alert rules in `_evaluate_alerts()` method
4. Push data to external dashboards (Grafana, Datadog, etc.)

## Future Enhancements

- [ ] HTTP server for live dashboard UI (Flask/FastAPI)
- [ ] WebSocket support for browser-based live updates
- [ ] Grafana integration
- [ ] Slack/email alerting
- [ ] Prometheus metrics export
- [ ] Time-series database for long-term retention
