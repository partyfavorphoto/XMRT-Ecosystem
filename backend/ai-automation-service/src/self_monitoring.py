#!/usr/bin/env python3
"""
Self-Monitoring System for Autonomous ElizaOS
Monitors system health, performance, and autonomous decision quality
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import aiofiles
import psutil
from web3 import Web3

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class MetricType(Enum):
    SYSTEM = "system"
    BLOCKCHAIN = "blockchain"
    AI_DECISION = "ai_decision"
    PERFORMANCE = "performance"
    SECURITY = "security"

@dataclass
class HealthMetric:
    metric_type: MetricType
    name: str
    value: float
    status: HealthStatus
    threshold_warning: float
    threshold_critical: float
    timestamp: datetime
    details: Dict[str, Any]

@dataclass
class SystemAlert:
    alert_id: str
    severity: str
    message: str
    timestamp: datetime
    resolved: bool
    resolution_time: Optional[datetime] = None

class SelfMonitoringSystem:
    """
    Comprehensive self-monitoring system for autonomous operations
    """
    
    def __init__(self, db_path: str = "monitoring.db"):
        self.db_path = db_path
        self.metrics_history: List[HealthMetric] = []
        self.active_alerts: List[SystemAlert] = []
        self.monitoring_enabled = True
        
        # Thresholds for various metrics
        self.thresholds = {
            "cpu_usage": {"warning": 70.0, "critical": 90.0},
            "memory_usage": {"warning": 80.0, "critical": 95.0},
            "disk_usage": {"warning": 85.0, "critical": 95.0},
            "response_time": {"warning": 5.0, "critical": 10.0},
            "error_rate": {"warning": 5.0, "critical": 10.0},
            "decision_confidence": {"warning": 0.6, "critical": 0.4},
            "blockchain_sync": {"warning": 10.0, "critical": 50.0}  # blocks behind
        }
        
        self._init_database()
        logger.info("Self-monitoring system initialized")

    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    status TEXT NOT NULL,
                    threshold_warning REAL,
                    threshold_critical REAL,
                    timestamp TEXT NOT NULL,
                    details TEXT
                )
            """)
            
            # Create alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolution_time TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    async def start_monitoring(self):
        """Start the monitoring loop"""
        logger.info("Starting self-monitoring system...")
        
        monitoring_tasks = [
            asyncio.create_task(self._monitor_system_resources()),
            asyncio.create_task(self._monitor_blockchain_health()),
            asyncio.create_task(self._monitor_ai_decisions()),
            asyncio.create_task(self._monitor_performance()),
            asyncio.create_task(self._process_alerts()),
            asyncio.create_task(self._cleanup_old_metrics())
        ]
        
        try:
            await asyncio.gather(*monitoring_tasks)
        except Exception as e:
            logger.error(f"Monitoring system error: {e}")

    async def _monitor_system_resources(self):
        """Monitor system resource usage"""
        while self.monitoring_enabled:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                await self._record_metric(
                    MetricType.SYSTEM,
                    "cpu_usage",
                    cpu_percent,
                    self.thresholds["cpu_usage"],
                    {"cores": psutil.cpu_count()}
                )
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                await self._record_metric(
                    MetricType.SYSTEM,
                    "memory_usage",
                    memory_percent,
                    self.thresholds["memory_usage"],
                    {
                        "total_gb": round(memory.total / (1024**3), 2),
                        "available_gb": round(memory.available / (1024**3), 2)
                    }
                )
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                await self._record_metric(
                    MetricType.SYSTEM,
                    "disk_usage",
                    disk_percent,
                    self.thresholds["disk_usage"],
                    {
                        "total_gb": round(disk.total / (1024**3), 2),
                        "free_gb": round(disk.free / (1024**3), 2)
                    }
                )
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring system resources: {e}")
                await asyncio.sleep(60)

    async def _monitor_blockchain_health(self):
        """Monitor blockchain connectivity and sync status"""
        while self.monitoring_enabled:
            try:
                # Check Ethereum connection
                eth_rpc = os.getenv('ETHEREUM_RPC_URL')
                if eth_rpc:
                    w3 = Web3(Web3.HTTPProvider(eth_rpc))
                    
                    if w3.is_connected():
                        # Check sync status
                        latest_block = w3.eth.block_number
                        sync_info = w3.eth.syncing
                        
                        if sync_info:
                            blocks_behind = sync_info['highestBlock'] - sync_info['currentBlock']
                        else:
                            blocks_behind = 0
                        
                        await self._record_metric(
                            MetricType.BLOCKCHAIN,
                            "blockchain_sync",
                            blocks_behind,
                            self.thresholds["blockchain_sync"],
                            {
                                "latest_block": latest_block,
                                "is_syncing": bool(sync_info),
                                "network": "ethereum"
                            }
                        )
                    else:
                        await self._create_alert(
                            "blockchain_disconnected",
                            "critical",
                            "Ethereum blockchain connection lost"
                        )
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error monitoring blockchain health: {e}")
                await asyncio.sleep(120)

    async def _monitor_ai_decisions(self):
        """Monitor AI decision quality and patterns"""
        while self.monitoring_enabled:
            try:
                # Read recent AI decisions from log files
                decision_metrics = await self._analyze_recent_decisions()
                
                if decision_metrics:
                    avg_confidence = decision_metrics.get('avg_confidence', 0.8)
                    decision_count = decision_metrics.get('decision_count', 0)
                    error_rate = decision_metrics.get('error_rate', 0.0)
                    
                    await self._record_metric(
                        MetricType.AI_DECISION,
                        "decision_confidence",
                        avg_confidence,
                        self.thresholds["decision_confidence"],
                        {
                            "decision_count": decision_count,
                            "error_rate": error_rate,
                            "period_hours": 1
                        }
                    )
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error monitoring AI decisions: {e}")
                await asyncio.sleep(600)

    async def _monitor_performance(self):
        """Monitor system performance metrics"""
        while self.monitoring_enabled:
            try:
                # Monitor response times (placeholder - would integrate with actual services)
                response_time = await self._measure_api_response_time()
                
                await self._record_metric(
                    MetricType.PERFORMANCE,
                    "response_time",
                    response_time,
                    self.thresholds["response_time"],
                    {"endpoint": "health_check"}
                )
                
                await asyncio.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                logger.error(f"Error monitoring performance: {e}")
                await asyncio.sleep(240)

    async def _record_metric(self, metric_type: MetricType, name: str, value: float, 
                           thresholds: Dict[str, float], details: Dict[str, Any]):
        """Record a metric and determine its health status"""
        
        # Determine status based on thresholds
        if value >= thresholds["critical"]:
            status = HealthStatus.CRITICAL
        elif value >= thresholds["warning"]:
            status = HealthStatus.WARNING
        else:
            status = HealthStatus.HEALTHY
        
        metric = HealthMetric(
            metric_type=metric_type,
            name=name,
            value=value,
            status=status,
            threshold_warning=thresholds["warning"],
            threshold_critical=thresholds["critical"],
            timestamp=datetime.now(),
            details=details
        )
        
        # Store in memory (limited history)
        self.metrics_history.append(metric)
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-500:]  # Keep last 500
        
        # Store in database
        await self._store_metric_db(metric)
        
        # Create alert if critical
        if status == HealthStatus.CRITICAL:
            await self._create_alert(
                f"{name}_critical",
                "critical",
                f"{name} is critical: {value} (threshold: {thresholds['critical']})"
            )
        elif status == HealthStatus.WARNING:
            await self._create_alert(
                f"{name}_warning",
                "warning",
                f"{name} is in warning state: {value} (threshold: {thresholds['warning']})"
            )

    async def _store_metric_db(self, metric: HealthMetric):
        """Store metric in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO metrics (metric_type, name, value, status, threshold_warning, 
                                   threshold_critical, timestamp, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.metric_type.value,
                metric.name,
                metric.value,
                metric.status.value,
                metric.threshold_warning,
                metric.threshold_critical,
                metric.timestamp.isoformat(),
                json.dumps(metric.details)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store metric in database: {e}")

    async def _create_alert(self, alert_id: str, severity: str, message: str):
        """Create a new alert"""
        
        # Check if alert already exists and is unresolved
        existing_alert = next((a for a in self.active_alerts if a.alert_id == alert_id and not a.resolved), None)
        if existing_alert:
            return  # Don't create duplicate alerts
        
        alert = SystemAlert(
            alert_id=alert_id,
            severity=severity,
            message=message,
            timestamp=datetime.now(),
            resolved=False
        )
        
        self.active_alerts.append(alert)
        
        # Store in database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO alerts (alert_id, severity, message, timestamp, resolved)
                VALUES (?, ?, ?, ?, ?)
            """, (
                alert.alert_id,
                alert.severity,
                alert.message,
                alert.timestamp.isoformat(),
                alert.resolved
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store alert in database: {e}")
        
        logger.warning(f"Alert created: {severity.upper()} - {message}")

    async def _process_alerts(self):
        """Process and potentially resolve alerts"""
        while self.monitoring_enabled:
            try:
                for alert in self.active_alerts:
                    if not alert.resolved:
                        # Check if alert condition has been resolved
                        if await self._check_alert_resolution(alert):
                            await self._resolve_alert(alert)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error processing alerts: {e}")
                await asyncio.sleep(120)

    async def _check_alert_resolution(self, alert: SystemAlert) -> bool:
        """Check if an alert condition has been resolved"""
        
        # Get recent metrics for the alert type
        recent_metrics = [m for m in self.metrics_history 
                         if m.name in alert.alert_id and 
                         m.timestamp > datetime.now() - timedelta(minutes=5)]
        
        if recent_metrics:
            latest_metric = max(recent_metrics, key=lambda x: x.timestamp)
            return latest_metric.status == HealthStatus.HEALTHY
        
        return False

    async def _resolve_alert(self, alert: SystemAlert):
        """Resolve an alert"""
        alert.resolved = True
        alert.resolution_time = datetime.now()
        
        # Update in database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE alerts SET resolved = ?, resolution_time = ?
                WHERE alert_id = ?
            """, (True, alert.resolution_time.isoformat(), alert.alert_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update alert resolution in database: {e}")
        
        logger.info(f"Alert resolved: {alert.alert_id}")

    async def _analyze_recent_decisions(self) -> Dict[str, Any]:
        """Analyze recent AI decisions from logs"""
        try:
            # This would analyze actual decision logs
            # For now, return mock data
            return {
                "avg_confidence": 0.85,
                "decision_count": 12,
                "error_rate": 2.0
            }
        except Exception as e:
            logger.error(f"Error analyzing recent decisions: {e}")
            return {}

    async def _measure_api_response_time(self) -> float:
        """Measure API response time"""
        try:
            start_time = time.time()
            # This would make actual API calls to measure response time
            # For now, simulate
            await asyncio.sleep(0.1)
            return time.time() - start_time
        except Exception as e:
            logger.error(f"Error measuring API response time: {e}")
            return 10.0  # Return high value to trigger alert

    async def _cleanup_old_metrics(self):
        """Clean up old metrics from database"""
        while self.monitoring_enabled:
            try:
                cutoff_date = datetime.now() - timedelta(days=30)
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM metrics WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                cursor.execute("""
                    DELETE FROM alerts WHERE resolved = 1 AND resolution_time < ?
                """, (cutoff_date.isoformat(),))
                
                conn.commit()
                conn.close()
                
                await asyncio.sleep(86400)  # Run daily
                
            except Exception as e:
                logger.error(f"Error cleaning up old metrics: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour

    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status"""
        
        if not self.metrics_history:
            return {"status": "unknown", "message": "No metrics available"}
        
        # Get latest metrics for each type
        latest_metrics = {}
        for metric in reversed(self.metrics_history):
            if metric.name not in latest_metrics:
                latest_metrics[metric.name] = metric
        
        # Determine overall health
        critical_count = sum(1 for m in latest_metrics.values() if m.status == HealthStatus.CRITICAL)
        warning_count = sum(1 for m in latest_metrics.values() if m.status == HealthStatus.WARNING)
        
        if critical_count > 0:
            overall_status = "critical"
        elif warning_count > 0:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "critical_alerts": critical_count,
            "warning_alerts": warning_count,
            "total_metrics": len(latest_metrics),
            "active_alerts": len([a for a in self.active_alerts if not a.resolved]),
            "last_check": datetime.now().isoformat(),
            "metrics": {name: {
                "value": metric.value,
                "status": metric.status.value,
                "timestamp": metric.timestamp.isoformat()
            } for name, metric in latest_metrics.items()}
        }

    def get_metrics_history(self, metric_name: str = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics history"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_metrics = [
            m for m in self.metrics_history 
            if m.timestamp > cutoff_time and (metric_name is None or m.name == metric_name)
        ]
        
        return [asdict(metric) for metric in filtered_metrics]

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts"""
        return [asdict(alert) for alert in self.active_alerts if not alert.resolved]

    async def stop_monitoring(self):
        """Stop the monitoring system"""
        self.monitoring_enabled = False
        logger.info("Self-monitoring system stopped")

# Global monitoring instance
monitoring_system = SelfMonitoringSystem()

# Convenience functions
async def start_monitoring():
    """Start the monitoring system"""
    await monitoring_system.start_monitoring()

def get_system_health():
    """Get current system health"""
    return monitoring_system.get_system_health()

def get_metrics_history(metric_name: str = None, hours: int = 24):
    """Get metrics history"""
    return monitoring_system.get_metrics_history(metric_name, hours)

def get_active_alerts():
    """Get active alerts"""
    return monitoring_system.get_active_alerts()

