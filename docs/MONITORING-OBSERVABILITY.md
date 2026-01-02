# Monitoring & Observability Guide

## Overview

Comprehensive monitoring and observability stack for Bakhmach Business Hub, providing real-time insights into system health, performance, and user behavior.

## Architecture

### Components

1. **Prometheus** - Metrics collection and storage
2. **Grafana** - Visualization and dashboarding
3. **ELK Stack** - Logging (Elasticsearch, Logstash, Kibana)
4. **Jaeger** - Distributed tracing
5. **AlertManager** - Alert routing and management

## Setup

### Docker Compose

```yaml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
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
      - "16686:16686"
      - "14268:14268"
    environment:
      - COLLECTOR_ZIPKIN_HTTP_PORT=9411

volumes:
  prometheus_data:
  grafana_data:
  elasticsearch_data:
```

## Metrics

### Application Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Sync operations
sync_operations = Counter(
    'sync_operations_total',
    'Total sync operations',
    ['source', 'target', 'status']
)

sync_duration = Histogram(
    'sync_duration_seconds',
    'Sync operation duration',
    ['source', 'target'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0)
)

active_syncs = Gauge(
    'active_syncs',
    'Number of active sync operations',
    ['source']
)

# API metrics
http_requests = Counter(
    'http_requests_total',
    'HTTP requests',
    ['method', 'endpoint', 'status']
)

http_latency = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0)
)

# Database metrics
db_operations = Counter(
    'db_operations_total',
    'Database operations',
    ['operation', 'table', 'status']
)

db_connection_pool = Gauge(
    'db_connection_pool_size',
    'Database connection pool size'
)
```

### Custom Instrumentation

```python
from prometheus_client import start_http_server
from flask import Flask, request
from functools import wraps

app = Flask(__name__)

# Start metrics server
start_http_server(8001)

def track_metrics(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        with sync_duration.labels(source='github', target='ai-studio').time():
            return f(*args, **kwargs)
    return decorated_function

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    http_latency.labels(
        method=request.method,
        endpoint=request.path
    ).observe(duration)
    
    http_requests.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()
    
    return response
```

## Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alert_rules:
  - 'monitoring/alerts.yml'

scrape_configs:
  - job_name: 'bakhmach-app'
    static_configs:
      - targets: ['localhost:8001']
    scrape_interval: 5s
  
  - job_name: 'docker'
    static_configs:
      - targets: ['localhost:9323']

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

## Alerting Rules

```yaml
# monitoring/alerts.yml
groups:
  - name: bakhmach_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: |
          rate(sync_operations_total{status="error"}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}"
      
      - alert: SyncLatencyHigh
        expr: |
          histogram_quantile(0.95, sync_duration_seconds) > 5
        for: 10m
        annotations:
          summary: "Sync operation latency is high"
          description: "95th percentile latency: {{ $value }}s"
      
      - alert: DatabaseConnectionPoolExhausted
        expr: |
          db_connection_pool_size >= 95
        for: 5m
        annotations:
          summary: "Database connection pool nearly exhausted"
      
      - alert: APIUnavailable
        expr: |
          up{job="bakhmach-app"} == 0
        for: 2m
        annotations:
          summary: "API service is down"
```

## Logging

### Structured Logging

```python
import logging
import json
from pythonjsonlogger import jsonlogger

# Configure JSON logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Usage
logger.info(
    'sync_started',
    extra={
        'source': 'github',
        'target': 'ai-studio',
        'timestamp': datetime.now().isoformat(),
        'trace_id': request.headers.get('X-Trace-ID')
    }
)
```

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: Confirmation that system is working
- **WARNING**: Warning for potential issues
- **ERROR**: Error that needs attention
- **CRITICAL**: Critical failure requiring immediate action

### Logstash Configuration

```conf
input {
  tcp {
    port => 5000
    codec => json
  }
  file {
    path => "/var/log/bakhmach/*.log"
    start_position => "beginning"
    codec => json
  }
}

filter {
  if [type] == "app" {
    mutate {
      add_field => { "[@metadata][index_name]" => "bakhmach-app" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "%{[@metadata][index_name]}-%{+YYYY.MM.dd}"
  }
}
```

## Distributed Tracing

### Jaeger Integration

```python
from jaeger_client import Config
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure Jaeger
jager_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

# Usage
with tracer.start_as_current_span("sync_operation") as span:
    span.set_attribute("source", "github")
    span.set_attribute("target", "ai-studio")
    # Perform sync
```

## Dashboards

### Key Metrics to Monitor

1. **System Health**
   - Uptime
   - CPU usage
   - Memory consumption
   - Disk I/O

2. **Application Performance**
   - Request latency (p50, p95, p99)
   - Error rate
   - Throughput
   - Active connections

3. **Sync Operations**
   - Sync success rate
   - Sync duration
   - Conflicts detected
   - Conflicts resolved

4. **Database**
   - Connection pool utilization
   - Query latency
   - Slow query count
   - Replication lag

5. **Integration Health**
   - GitHub API availability
   - AI Studio API availability
   - Webhook delivery success rate
   - Retry count

### Sample Grafana Dashboard JSON

```json
{
  "dashboard": {
    "title": "Bakhmach Business Hub",
    "panels": [
      {
        "title": "Request Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Active Syncs",
        "targets": [
          {
            "expr": "active_syncs"
          }
        ],
        "type": "stat"
      }
    ]
  }
}
```

## Health Checks

### Endpoint Implementation

```python
@app.route('/health', methods=['GET'])
def health():
    checks = {
        'database': check_database(),
        'redis': check_redis(),
        'github_api': check_github_api(),
        'ai_studio_api': check_ai_studio_api()
    }
    
    status = 'healthy' if all(checks.values()) else 'degraded'
    
    return jsonify({
        'status': status,
        'timestamp': datetime.now().isoformat(),
        'checks': checks
    }), 200 if status == 'healthy' else 503

def check_database():
    try:
        db.session.execute('SELECT 1')
        return True
    except:
        return False

def check_redis():
    try:
        redis_client.ping()
        return True
    except:
        return False
```

## SLOs and SLIs

### Service Level Objectives

```
Sync Operation Availability:
- Target: 99.9% uptime
- SLI: (Successful syncs / Total sync attempts) * 100

API Response Time:
- Target: p95 latency < 200ms
- SLI: Percentage of requests completing within 200ms

Error Budget:
- Monthly: 43 minutes of downtime
- Used for: Deployments, updates, incident response
```

## Runbooks

### High Error Rate

1. Check error logs in Kibana
2. Identify error pattern
3. Check GitHub/AI Studio API status
4. Review recent deployments
5. Rollback if necessary

### High Latency

1. Check database query performance
2. Review Jaeger traces for bottlenecks
3. Check resource utilization (CPU, memory)
4. Scale horizontally if needed
5. Check for network issues

## Maintenance

- Clean up old logs weekly
- Archive metrics data monthly
- Review alert thresholds quarterly
- Update dashboards as needed
- Test alerting channels monthly

## Contact

For monitoring issues: @romanchaa997
