#!/usr/bin/env python3
"""
Orchestrator Main Service for Bakhmach-Business-Hub

Adaptive load balancing, service health monitoring, auto-scaling trigger,
and business metrics collection from IoT sensors and API endpoints.

Author: romanchaa997
Version: 1.0.0
"""

import os
import sys
import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

import psycopg2
from psycopg2 import pool
import aiohttp
from prometheus_client import Counter, Gauge, Histogram, generate_latest

# === CONFIGURATION ===
LOGGING_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://bakhmach_user:password@localhost:5432/bakhmach_db')
PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', 9091))
MONITOR_INTERVAL = int(os.getenv('MONITOR_INTERVAL', 10))  # Seconds

# === LOGGING ===
logging.basicConfig(
    level=LOGGING_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === PROMETHEUS METRICS ===
class MetricsCollector:
    """Centralized Prometheus metrics for business operations"""

    # Business Metrics
    orders_total = Counter(
        'bakhmach_orders_total',
        'Total orders processed',
        ['business_id', 'status']
    )
    orders_value = Counter(
        'bakhmach_orders_value_uah',
        'Total order value in UAH',
        ['business_id']
    )
    active_businesses = Gauge(
        'bakhmach_active_businesses',
        'Number of active businesses'
    )
    users_total = Gauge(
        'bakhmach_users_total',
        'Total registered users'
    )
    
    # Energy Metrics
    energy_consumption_watts = Gauge(
        'bakhmach_energy_consumption_watts',
        'Current power consumption',
        ['device_id', 'business_id']
    )
    energy_daily_cost_uah = Gauge(
        'bakhmach_energy_daily_cost_uah',
        'Daily energy cost',
        ['business_id']
    )
    
    # Service Health
    service_health_status = Gauge(
        'bakhmach_service_health',
        'Service health status (1=healthy, 0=unhealthy)',
        ['service_name']
    )
    api_latency_seconds = Histogram(
        'bakhmach_api_latency_seconds',
        'API endpoint latency',
        ['endpoint', 'method']
    )
    database_connections = Gauge(
        'bakhmach_database_connections',
        'Active database connections'
    )
    
    # IoT Metrics
    iot_devices_online = Gauge(
        'bakhmach_iot_devices_online',
        'Number of online IoT devices'
    )
    iot_messages_received = Counter(
        'bakhmach_iot_messages_received_total',
        'Total IoT messages received',
        ['device_type']
    )


class ServiceHealth(Enum):
    """Service health states"""
    HEALTHY = 1
    DEGRADED = 2
    UNHEALTHY = 3


@dataclass
class BusinessMetrics:
    """Daily business metrics snapshot"""
    business_id: str
    date: str
    total_orders: int = 0
    total_revenue: float = 0.0
    avg_order_value: float = 0.0
    energy_cost_uah: float = 0.0
    profit_margin_percent: float = 0.0
    customer_count: int = 0
    last_updated: str = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.utcnow().isoformat()


class OrchestratorService:
    """Main orchestrator service"""

    def __init__(self):
        self.db_pool: Optional[pool.SimpleConnectionPool] = None
        self.metrics = MetricsCollector()
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False

    async def init(self):
        """Initialize service"""
        logger.info("Initializing Orchestrator Service...")
        try:
            # Initialize database connection pool
            self.db_pool = pool.SimpleConnectionPool(
                1, 5, DATABASE_URL,
                connect_timeout=10
            )
            self.session = aiohttp.ClientSession()
            self.running = True
            logger.info("Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise

    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down Orchestrator...")
        self.running = False
        if self.session:
            await self.session.close()
        if self.db_pool:
            self.db_pool.closeall()
        logger.info("Orchestrator shut down")

    async def collect_business_metrics(self) -> List[BusinessMetrics]:
        """Collect metrics from all businesses"""
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            
            # Query for daily metrics
            query = """
            SELECT 
                bm.business_id,
                bm.metric_date::text,
                bm.total_orders,
                bm.total_revenue,
                bm.avg_order_value,
                bm.energy_cost_uah,
                bm.profit_margin_percent,
                bm.customer_count
            FROM business_metrics bm
            WHERE bm.metric_date = CURRENT_DATE
            ORDER BY bm.total_revenue DESC
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            metrics_list = []
            for row in rows:
                metric = BusinessMetrics(
                    business_id=str(row[0]),
                    date=row[1],
                    total_orders=row[2],
                    total_revenue=float(row[3]) if row[3] else 0.0,
                    avg_order_value=float(row[4]) if row[4] else 0.0,
                    energy_cost_uah=float(row[5]) if row[5] else 0.0,
                    profit_margin_percent=float(row[6]) if row[6] else 0.0,
                    customer_count=row[7]
                )
                metrics_list.append(metric)
                
                # Update Prometheus metrics
                self.metrics.orders_total.labels(
                    business_id=metric.business_id,
                    status='completed'
                ).inc(metric.total_orders)
                self.metrics.orders_value.labels(
                    business_id=metric.business_id
                ).inc(metric.total_revenue)
            
            cursor.close()
            self.db_pool.putconn(conn)
            logger.info(f"Collected metrics from {len(metrics_list)} businesses")
            return metrics_list
            
        except Exception as e:
            logger.error(f"Error collecting business metrics: {e}")
            return []

    async def collect_energy_metrics(self):
        """Collect energy consumption data from IoT devices"""
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            
            # Get latest energy readings
            query = """
            SELECT 
                device_id,
                business_id,
                power_watts,
                current_amps,
                voltage,
                recorded_at
            FROM energy_consumption
            WHERE recorded_at > NOW() - INTERVAL '1 hour'
            ORDER BY device_id, recorded_at DESC
            LIMIT 100
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                device_id = row[0]
                business_id = str(row[1])
                power_watts = float(row[2]) if row[2] else 0.0
                
                # Update Prometheus metric
                self.metrics.energy_consumption_watts.labels(
                    device_id=device_id,
                    business_id=business_id
                ).set(power_watts)
            
            cursor.close()
            self.db_pool.putconn(conn)
            logger.info(f"Collected energy metrics from {len(rows)} readings")
            
        except Exception as e:
            logger.error(f"Error collecting energy metrics: {e}")

    async def check_service_health(self) -> Dict[str, ServiceHealth]:
        """Monitor health of critical services"""
        health_status = {}
        
        # Database health
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.close()
            self.db_pool.putconn(conn)
            health_status['database'] = ServiceHealth.HEALTHY
            self.metrics.service_health_status.labels(
                service_name='database'
            ).set(ServiceHealth.HEALTHY.value)
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            health_status['database'] = ServiceHealth.UNHEALTHY
            self.metrics.service_health_status.labels(
                service_name='database'
            ).set(ServiceHealth.UNHEALTHY.value)
        
        return health_status

    async def adaptive_load_balancing(self):
        """Adaptive load balancing based on metrics"""
        try:
            metrics = await self.collect_business_metrics()
            
            # Calculate load distribution
            total_revenue = sum(m.total_revenue for m in metrics)
            
            for metric in metrics:
                if total_revenue > 0:
                    load_percent = (metric.total_revenue / total_revenue) * 100
                    logger.debug(f"Business {metric.business_id}: {load_percent:.2f}% of traffic")
            
            logger.info("Load balancing calculation complete")
        except Exception as e:
            logger.error(f"Error in load balancing: {e}")

    async def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Starting monitoring loop...")
        
        while self.running:
            try:
                # Collect metrics
                await self.collect_business_metrics()
                await self.collect_energy_metrics()
                await self.check_service_health()
                await self.adaptive_load_balancing()
                
                # Wait before next iteration
                await asyncio.sleep(MONITOR_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(MONITOR_INTERVAL)

    def get_metrics(self):
        """Return Prometheus metrics"""
        return generate_latest()


async def main():
    """Main entry point"""
    service = OrchestratorService()
    
    try:
        await service.init()
        
        # Start monitoring loop (non-blocking)
        monitor_task = asyncio.create_task(service.monitor_loop())
        
        # Keep service running
        await monitor_task
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        await service.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
