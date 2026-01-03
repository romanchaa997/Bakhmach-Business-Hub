# Payment Saga Implementation Guide

## Overview
Comprehensive guide for implementing distributed payment transactions using Saga pattern with Kafka topics, SQS queues, retry strategies, and idempotency mechanisms.

## Architecture Components

### 1. Kafka Topics

```yaml
Topics:
  payment.initiated:
    partitions: 3
    replication_factor: 2
    retention_ms: 604800000  # 7 days
    
  payment.authorized:
    partitions: 3
    replication_factor: 2
    
  payment.captured:
    partitions: 3
    replication_factor: 2
    
  payment.failed:
    partitions: 2
    replication_factor: 2
    
  payment.reversed:
    partitions: 2
    replication_factor: 2
```

### 2. SQS Queues

```yaml
Queues:
  payment-processing:
    MessageRetentionPeriod: 1209600  # 14 days
    VisibilityTimeout: 300  # 5 minutes
    RedrivePolicy:
      maxReceiveCount: 3
      deadLetterTargetArn: payment-dlq
      
  payment-dlq:
    MessageRetentionPeriod: 1209600
    
  payment-settlement:
    MessageRetentionPeriod: 604800
    VisibilityTimeout: 600
```

## Retry Strategy

### Exponential Backoff Configuration
```yaml
Retry Levels:
  Level 1:
    delay: 1 second
    max_attempts: 2
    
  Level 2:
    delay: 5 seconds
    max_attempts: 2
    
  Level 3:
    delay: 30 seconds
    max_attempts: 2
    
  Level 4:
    delay: 300 seconds (5 minutes)
    max_attempts: 3
    
  Level 5 (DLQ):
    manual_review_required: true
```

## Idempotency Implementation

### Request ID Strategy
```python
import hashlib
import json
from typing import Dict, Any

class IdempotencyManager:
    def __init__(self, cache_ttl: int = 3600):
        self.cache_ttl = cache_ttl
        self.idempotency_cache = {}  # In production: Redis/DynamoDB
        
    def generate_request_id(self, payload: Dict[str, Any]) -> str:
        """Generate deterministic request ID"""
        canonical = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()
        
    def is_duplicate(self, request_id: str) -> bool:
        """Check if request has been processed"""
        return request_id in self.idempotency_cache
        
    def record_result(self, request_id: str, result: Dict[str, Any]):
        """Store idempotent result"""
        self.idempotency_cache[request_id] = {
            'result': result,
            'timestamp': time.time()
        }
```

## Event Saga Flow

### Payment Lifecycle States

1. **INITIATED** -> Request received, validated
2. **AUTHORIZED** -> Card authorized, amount reserved  
3. **CAPTURED** -> Charge captured from card
4. **SETTLED** -> Funds transferred to merchant
5. **FAILED** -> Transaction rejected
6. **REVERSED** -> Refund issued

## A/B Testing Framework

### Retry Interval Variations

```python
from enum import Enum
import random

class RetryStrategy(Enum):
    CONTROL = "exponential_1s_5s_30s_300s"  # Baseline
    TEST_A = "exponential_500ms_2s_10s_60s"  # Aggressive
    TEST_B = "exponential_2s_10s_60s_600s"   # Conservative
    
class ABTestingManager:
    def __init__(self):
        self.test_allocation = {
            RetryStrategy.CONTROL: 0.5,
            RetryStrategy.TEST_A: 0.25,
            RetryStrategy.TEST_B: 0.25
        }
        
    def assign_strategy(self, user_id: str) -> RetryStrategy:
        """Assign user to test variant"""
        random.seed(hash(user_id) % 2**32)
        return random.choices(
            list(self.test_allocation.keys()),
            weights=self.test_allocation.values()
        )[0]
        
    def get_retry_delays(self, strategy: RetryStrategy) -> list[float]:
        """Get retry delays for strategy"""
        delays_map = {
            RetryStrategy.CONTROL: [1, 5, 30, 300],
            RetryStrategy.TEST_A: [0.5, 2, 10, 60],
            RetryStrategy.TEST_B: [2, 10, 60, 600]
        }
        return delays_map[strategy]
```

## Risk Score Model

### Prediction Model

```python
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier

class PaymentRiskScorer:
    def __init__(self):
        self.model = GradientBoostingClassifier(n_estimators=100)
        self.features = [
            'amount',
            'card_age_days',
            'merchant_category',
            'previous_success_rate',
            'time_since_last_transaction',
            'geo_velocity_score',
            'device_risk_score'
        ]
        
    def calculate_risk_score(self, transaction: dict) -> float:
        """Calculate risk score 0-1"""
        X = np.array([[transaction[f] for f in self.features]])
        return self.model.predict_proba(X)[0][1]
        
    def stratify_payments(self, transactions: list[dict]):
        """Stratify payments by risk for A/B test"""
        risks = [(t, self.calculate_risk_score(t)) for t in transactions]
        
        strata = {
            'low_risk': [],
            'medium_risk': [],
            'high_risk': []
        }
        
        for transaction, risk_score in risks:
            if risk_score < 0.3:
                strata['low_risk'].append(transaction)
            elif risk_score < 0.7:
                strata['medium_risk'].append(transaction)
            else:
                strata['high_risk'].append(transaction)
                
        return strata
```

## Production Deployment

### Configuration
```yaml
Environment: production
Kafka:
  brokers:
    - kafka-1:9092
    - kafka-2:9092  
    - kafka-3:9092
  consumer_group: payment-processor-v1
  
SQS:
  region: us-east-1
  queue_url: https://sqs.us-east-1.amazonaws.com/123456/payment-processing
  
Database:
  host: postgres-primary.internal
  pool_size: 20
  max_overflow: 10
  
Monitoring:
  metrics_port: 9090
  logs_level: INFO
  alert_threshold_error_rate: 0.05
```

## Monitoring & Alerting

### Key Metrics
- Payment success rate (target: >99.5%)
- Average retry count (target: <1.2)
- Settlement lag (target: <2 hours)
- DLQ message count (alert if >100)

## References
See COMPREHENSIVE-ARCHITECTURE-TEMPLATE.md for integration details.
