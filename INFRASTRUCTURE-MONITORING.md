# Infrastructure Monitoring & Observability

## Overview
Comprehensive monitoring, observability, and alerting system for Bakhmach Business Hub infrastructure, covering metrics, logs, traces, and health checks.

## Core Components

### 1. Metrics Collection

#### Prometheus Configuration
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'bakhmach-services'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'backend'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
  
  - job_name: 'database'
    static_configs:
      - targets: ['localhost:9187']
```

#### Key Metrics

**Application Metrics:**
- Request rate (requests/sec)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Cache hit/miss ratio
- Database query latency
- Message queue depth
- Active connections

**Infrastructure Metrics:**
- CPU usage (%)
- Memory usage (MB, %)
- Disk I/O (read/write ops)
- Network throughput (bytes/sec)
- Container/Pod resource usage
- Database connection pool utilization

**Business Metrics:**
- Active users
- Revenue/transactions
- Feature adoption
- User engagement score
- Churn rate
- Conversion funnel

### 2. Logging Stack

#### ELK (Elasticsearch, Logstash, Kibana) Setup

```yaml
# logstash.conf
input {
  tcp {
    port => 5000
    codec => json
  }
}

filter {
  if [type] == "bakhmach" {
    grok {
      match => { "message" => "%{COMMONLOGFORMAT}" }
    }
    date {
      match => [ "timestamp", "dd/MMM/YYYY:HH:mm:ss Z" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "bakhmach-%{+YYYY.MM.dd}"
  }
}
```

#### Log Levels & Categories
- **DEBUG**: Development/diagnostic info
- **INFO**: General operational info
- **WARN**: Potential issues
- **ERROR**: Error conditions
- **CRITICAL**: Critical failures

#### Structured Logging
```json
{
  "timestamp": "2026-01-02T19:30:00Z",
  "service": "backend",
  "level": "ERROR",
  "correlation_id": "req-12345",
  "user_id": "user-789",
  "action": "payment_processing",
  "error": "Insufficient funds",
  "error_code": "PAYMENT_001",
  "duration_ms": 245
}
```

### 3. Distributed Tracing

#### Jaeger Configuration
```yaml
jaeger:
  enabled: true
  service_name: bakhmach-hub
  sampler:
    type: probabilistic
    param: 0.1  # 10% sampling
  reporter:
    log_spans: false
    endpoint: http://jaeger:14268/api/traces
```

#### Trace Instrumentation
- Service-to-service calls
- Database queries
- Cache operations
- External API calls
- Message queue operations

### 4. Health Checks

#### Readiness Probe
```typescript
// Health check endpoint
GET /health/ready

Response (200 OK):
{
  "status": "ready",
  "services": {
    "database": "connected",
    "cache": "connected",
    "queue": "connected"
  }
}
```

#### Liveness Probe
```typescript
GET /health/live

Response (200 OK):
{
  "status": "alive",
  "uptime_seconds": 864000,
  "memory_usage_mb": 512
}
```

### 5. Alerting Rules

#### Critical Alerts
```yaml
groups:
  - name: bakhmach_critical
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
      
      - alert: DatabaseDown
        expr: pg_up == 0
        for: 2m
        annotations:
          summary: "Database is down"
      
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
        for: 10m
        annotations:
          summary: "Memory usage above 90%"
```

#### Warning Alerts
- Response time > 1000ms (p95)
- Cache hit ratio < 70%
- Database connections > 80% pool
- Disk usage > 80%
- Message queue lag > 5 minutes

### 6. Dashboard Configuration

#### Grafana Dashboards

**System Overview:**
- CPU, memory, disk usage
- Network throughput
- Top processes by resource usage

**Application Performance:**
- Request latency distribution
- Error rate trends
- Throughput/RPS
- Apdex score

**Business Metrics:**
- Revenue/transactions
- User engagement
- Conversion funnel
- Feature usage

**Infrastructure:**
- Kubernetes pod status
- Database replication lag
- Cache efficiency
- Queue depth trends

## Monitoring Strategy

### SLO/SLI Definitions

```
SLO: 99.9% availability (9 hours 26 minutes downtime/month)
SLI: Uptime measured by successful health checks

SLO: 99th percentile latency < 500ms
SLI: Measured from request ingestion to response

SLO: 99% of requests succeed
SLI: HTTP 2xx responses / total requests
```

### Error Budget
- Monthly error budget: 0.1% (43 minutes)
- Tracked per service and feature
- Enables deployment gates

### Monitoring Runbook Example

**Issue: High Error Rate**
1. Check alert dashboard for error types
2. Review recent deployments
3. Check database connection pool
4. Review application logs for stacktraces
5. Escalate if > 5% error rate

## Implementation

### Docker Compose Setup
```yaml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
  
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
  
  kibana:
    image: docker.elastic.co/kibana/kibana:8.0.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
  
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "6831:6831/udp"
      - "16686:16686"

volumes:
  prometheus_data:
  grafana_data:
  elasticsearch_data:
```

### Maintenance Tasks

**Daily:**
- Review alert dashboard
- Check critical metric trends
- Monitor deployment status

**Weekly:**
- Analyze SLO compliance
- Review error patterns
- Update runbooks if needed

**Monthly:**
- Capacity planning review
- Alert threshold tuning
- Dashboard optimization

## Monitoring Costs

- Prometheus: Self-hosted (minimal)
- Grafana: $10-50/month or self-hosted
- ELK Stack: $50-200/month or self-hosted
- Jaeger: Self-hosted (minimal)
- Total: Typically $100-300/month for managed SaaS

## Best Practices

1. **Instrument at application entry/exit points**
2. **Use consistent metric naming conventions**
3. **Implement sampling for high-volume traces**
4. **Regularly review and tune alert thresholds**
5. **Keep runbooks updated**
6. **Monitor your monitoring system**
7. **Use correlation IDs for request tracking**
8. **Implement graceful degradation**

## Integration Points

- Application instrumentation (OpenTelemetry)
- Database query monitoring (pg_stat_statements)
- Container orchestration (Kubernetes metrics)
- Custom business metrics
- Third-party service monitoring (payment providers, etc.)
