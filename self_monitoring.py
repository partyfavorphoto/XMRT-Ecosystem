#!/usr/bin/env python3
"""
Self-Monitoring System
Comprehensive system health monitoring for XMRT-Ecosystem.
"""

import asyncio
import logging
import json
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SelfMonitoringSystem:
    """Comprehensive system health monitoring."""
    
    def __init__(self):
        self.metrics_history = []
        self.alerts = []
        self.health_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time': 1000,  # milliseconds
            'error_rate': 5.0  # percentage
        }
        self.monitoring_interval = 60  # seconds
        self.is_monitoring = False
        
    async def start_monitoring(self):
        """Start continuous monitoring."""
if __name__ == "__main__":
            logger.info("Starting self-monitoring system...")
        self.is_monitoring = True
        
        while self.is_monitoring:
            try:
                # Collect system metrics
                metrics = await self.collect_system_metrics()
                
                # Analyze health
                health_status = await self.analyze_health(metrics)
                
                # Check for alerts
                await self.check_alerts(metrics, health_status)
                
                # Store metrics
                self.metrics_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'metrics': metrics,
                    'health_status': health_status
                })
                
                # Keep only last 24 hours of data
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.metrics_history = [
                    m for m in self.metrics_history 
                    if datetime.fromisoformat(m['timestamp']) > cutoff_time
                ]
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                pass  # <-- AUTO-INSERTED
if __name__ == "__main__":
                    logger.error(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics."""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': await self._collect_system_metrics(),
            'application': await self._collect_application_metrics(),
            'network': await self._collect_network_metrics(),
            'database': await self._collect_database_metrics(),
            'blockchain': await self._collect_blockchain_metrics()
        }
        
        return metrics
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available': memory.available,
                'disk_usage': disk.percent,
                'disk_free': disk.free,
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0],
                'uptime': time.time() - psutil.boot_time()
            }
        except Exception as e:
            pass  # <-- AUTO-INSERTED
if __name__ == "__main__":
                logger.error(f"Error collecting system metrics: {e}")
            return {'error': str(e)}
    
    async def _collect_application_metrics(self) -> Dict[str, Any]:
        """Collect application-specific metrics."""
        try:
            # Simulate application metrics
            return {
                'active_connections': 25,
                'request_count': 1500,
                'error_count': 12,
                'response_time_avg': 250,
                'response_time_p95': 450,
                'cache_hit_rate': 85.5,
                'queue_size': 3,
                'worker_processes': 4
            }
        except Exception as e:
            pass  # <-- AUTO-INSERTED
if __name__ == "__main__":
                logger.error(f"Error collecting application metrics: {e}")
            return {'error': str(e)}
    
    async def _collect_network_metrics(self) -> Dict[str, Any]:
        """Collect network-related metrics."""
        try:
            net_io = psutil.net_io_counters()
            
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errors_in': net_io.errin,
                'errors_out': net_io.errout,
                'drops_in': net_io.dropin,
                'drops_out': net_io.dropout
            }
        except Exception as e:
            pass  # <-- AUTO-INSERTED
if __name__ == "__main__":
                logger.error(f"Error collecting network metrics: {e}")
            return {'error': str(e)}
    
    async def _collect_database_metrics(self) -> Dict[str, Any]:
        """Collect database performance metrics."""
        try:
            # Simulate database metrics
            return {
                'connection_count': 15,
                'active_queries': 3,
                'slow_queries': 1,
                'query_time_avg': 45,
                'cache_hit_ratio': 92.3,
                'deadlocks': 0,
                'table_locks': 2
            }
        except Exception as e:
            pass  # <-- AUTO-INSERTED
if __name__ == "__main__":
                logger.error(f"Error collecting database metrics: {e}")
            return {'error': str(e)}
    
    async def _collect_blockchain_metrics(self) -> Dict[str, Any]:
        """Collect blockchain-related metrics."""
        try:
            # Simulate blockchain metrics
            return {
                'block_height': 18500000,
                'gas_price': 25,
                'transaction_count': 150,
                'pending_transactions': 5,
                'network_hashrate': 250000000,
                'node_sync_status': 'synced',
                'peer_count': 25
            }
        except Exception as e:
            pass  # <-- AUTO-INSERTED
if __name__ == "__main__":
                logger.error(f"Error collecting blockchain metrics: {e}")
            return {'error': str(e)}
    
    async def analyze_health(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall system health."""
        health_status = {
            'overall_score': 100,
            'status': 'healthy',
            'components': {},
            'issues': [],
            'recommendations': []
        }
        
        # Analyze system health
        system_metrics = metrics.get('system', {})
        if not system_metrics.get('error'):
            cpu_usage = system_metrics.get('cpu_usage', 0)
            memory_usage = system_metrics.get('memory_usage', 0)
            disk_usage = system_metrics.get('disk_usage', 0)
            
            system_score = 100
            
            if cpu_usage > self.health_thresholds['cpu_usage']:
                system_score -= 20
                health_status['issues'].append(f"High CPU usage: {cpu_usage:.1f}%")
                health_status['recommendations'].append("Consider scaling up CPU resources")
            
            if memory_usage > self.health_thresholds['memory_usage']:
                system_score -= 20
                health_status['issues'].append(f"High memory usage: {memory_usage:.1f}%")
                health_status['recommendations'].append("Consider increasing memory allocation")
            
            if disk_usage > self.health_thresholds['disk_usage']:
                system_score -= 30
                health_status['issues'].append(f"High disk usage: {disk_usage:.1f}%")
                health_status['recommendations'].append("Clean up disk space or expand storage")
            
            health_status['components']['system'] = {
                'score': system_score,
                'status': 'healthy' if system_score >= 80 else 'warning' if system_score >= 60 else 'critical'
            }
        
        # Analyze application health
        app_metrics = metrics.get('application', {})
        if not app_metrics.get('error'):
            error_count = app_metrics.get('error_count', 0)
            request_count = app_metrics.get('request_count', 1)
            response_time = app_metrics.get('response_time_avg', 0)
            
            error_rate = (error_count / request_count) * 100 if request_count > 0 else 0
            app_score = 100
            
            if error_rate > self.health_thresholds['error_rate']:
                app_score -= 25
                health_status['issues'].append(f"High error rate: {error_rate:.1f}%")
                health_status['recommendations'].append("Investigate application errors")
            
            if response_time > self.health_thresholds['response_time']:
                app_score -= 15
                health_status['issues'].append(f"Slow response time: {response_time}ms")
                health_status['recommendations'].append("Optimize application performance")
            
            health_status['components']['application'] = {
                'score': app_score,
                'status': 'healthy' if app_score >= 80 else 'warning' if app_score >= 60 else 'critical'
            }
        
        # Analyze database health
        db_metrics = metrics.get('database', {})
        if not db_metrics.get('error'):
            slow_queries = db_metrics.get('slow_queries', 0)
            deadlocks = db_metrics.get('deadlocks', 0)
            cache_hit_ratio = db_metrics.get('cache_hit_ratio', 100)
            
            db_score = 100
            
            if slow_queries > 5:
                db_score -= 15
                health_status['issues'].append(f"High number of slow queries: {slow_queries}")
                health_status['recommendations'].append("Optimize database queries")
            
            if deadlocks > 0:
                db_score -= 20
                health_status['issues'].append(f"Database deadlocks detected: {deadlocks}")
                health_status['recommendations'].append("Review database transaction logic")
            
            if cache_hit_ratio < 85:
                db_score -= 10
                health_status['issues'].append(f"Low cache hit ratio: {cache_hit_ratio:.1f}%")
                health_status['recommendations'].append("Optimize database caching")
            
            health_status['components']['database'] = {
                'score': db_score,
                'status': 'healthy' if db_score >= 80 else 'warning' if db_score >= 60 else 'critical'
            }
        
        # Calculate overall score
        component_scores = [comp['score'] for comp in health_status['components'].values()]
        if component_scores:
            health_status['overall_score'] = sum(component_scores) / len(component_scores)
        
        # Determine overall status
        if health_status['overall_score'] >= 90:
            health_status['status'] = 'excellent'
        elif health_status['overall_score'] >= 80:
            health_status['status'] = 'healthy'
        elif health_status['overall_score'] >= 60:
            health_status['status'] = 'warning'
        else:
            health_status['status'] = 'critical'
        
        return health_status
    
    async def check_alerts(self, metrics: Dict[str, Any], health_status: Dict[str, Any]):
        """Check for alert conditions and generate alerts."""
        current_time = datetime.now()
        
        # Check for critical issues
        if health_status['status'] == 'critical':
            alert = {
                'id': f"alert_{int(current_time.timestamp())}",
                'timestamp': current_time.isoformat(),
                'severity': 'critical',
                'title': 'System Critical Health Alert',
                'description': f"System health score dropped to {health_status['overall_score']:.1f}",
                'issues': health_status['issues'],
                'recommendations': health_status['recommendations'],
                'acknowledged': False
            }
            
            self.alerts.append(alert)
            logger.critical(f"CRITICAL ALERT: {alert['title']}")
        
        # Check for warning conditions
        elif health_status['status'] == 'warning':
            alert = {
                'id': f"alert_{int(current_time.timestamp())}",
                'timestamp': current_time.isoformat(),
                'severity': 'warning',
                'title': 'System Warning Alert',
                'description': f"System health score is {health_status['overall_score']:.1f}",
                'issues': health_status['issues'],
                'recommendations': health_status['recommendations'],
                'acknowledged': False
            }
            
            self.alerts.append(alert)
if __name__ == "__main__":
                logger.warning(f"WARNING ALERT: {alert['title']}")
        
        # Clean up old alerts (keep last 100)
        self.alerts = self.alerts[-100:]
    
    async def get_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report."""
        if not self.metrics_history:
            return {'status': 'no_data', 'message': 'No monitoring data available'}
        
        latest_metrics = self.metrics_history[-1]
        
        # Calculate trends
        trends = await self._calculate_trends()
        
        # Get recent alerts
        recent_alerts = [
            alert for alert in self.alerts 
            if datetime.fromisoformat(alert['timestamp']) > datetime.now() - timedelta(hours=24)
        ]
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'current_health': latest_metrics['health_status'],
            'trends': trends,
            'recent_alerts': recent_alerts,
            'monitoring_status': {
                'is_active': self.is_monitoring,
                'data_points': len(self.metrics_history),
                'monitoring_interval': self.monitoring_interval,
                'uptime': self._calculate_monitoring_uptime()
            },
            'recommendations': await self._generate_health_recommendations()
        }
        
        return report
    
    async def _calculate_trends(self) -> Dict[str, Any]:
        """Calculate health trends over time."""
        if len(self.metrics_history) < 2:
            return {'status': 'insufficient_data'}
        
        # Get data from last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_data = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m['timestamp']) > one_hour_ago
        ]
        
        if len(recent_data) < 2:
            return {'status': 'insufficient_recent_data'}
        
        # Calculate trends
        health_scores = [m['health_status']['overall_score'] for m in recent_data]
        cpu_usage = [m['metrics']['system'].get('cpu_usage', 0) for m in recent_data if not m['metrics']['system'].get('error')]
        memory_usage = [m['metrics']['system'].get('memory_usage', 0) for m in recent_data if not m['metrics']['system'].get('error')]
        
        trends = {
            'health_score': {
                'current': health_scores[-1],
                'trend': 'improving' if health_scores[-1] > health_scores[0] else 'declining' if health_scores[-1] < health_scores[0] else 'stable',
                'change': health_scores[-1] - health_scores[0]
            }
        }
        
        if cpu_usage:
            trends['cpu_usage'] = {
                'current': cpu_usage[-1],
                'average': sum(cpu_usage) / len(cpu_usage),
                'trend': 'increasing' if cpu_usage[-1] > cpu_usage[0] else 'decreasing' if cpu_usage[-1] < cpu_usage[0] else 'stable'
            }
        
        if memory_usage:
            trends['memory_usage'] = {
                'current': memory_usage[-1],
                'average': sum(memory_usage) / len(memory_usage),
                'trend': 'increasing' if memory_usage[-1] > memory_usage[0] else 'decreasing' if memory_usage[-1] < memory_usage[0] else 'stable'
            }
        
        return trends
    
    def _calculate_monitoring_uptime(self) -> float:
        """Calculate monitoring system uptime percentage."""
        if not self.metrics_history:
            return 0.0
        
        # Simulate uptime calculation
        expected_data_points = len(self.metrics_history)
        actual_data_points = len([m for m in self.metrics_history if not m['metrics'].get('error')])
        
        return (actual_data_points / expected_data_points) * 100 if expected_data_points > 0 else 0.0
    
    async def _generate_health_recommendations(self) -> List[Dict[str, Any]]:
        """Generate health improvement recommendations."""
        recommendations = []
        
        if not self.metrics_history:
            return recommendations
        
        latest_health = self.metrics_history[-1]['health_status']
        
        # System recommendations
        if 'system' in latest_health['components']:
            system_score = latest_health['components']['system']['score']
            if system_score < 80:
                recommendations.append({
                    'category': 'system',
                    'priority': 'high' if system_score < 60 else 'medium',
                    'title': 'Optimize System Resources',
                    'description': 'System performance is below optimal levels',
                    'actions': [
                        'Monitor CPU and memory usage patterns',
                        'Consider resource scaling',
                        'Implement performance optimizations'
                    ]
                })
        
        # Application recommendations
        if 'application' in latest_health['components']:
            app_score = latest_health['components']['application']['score']
            if app_score < 80:
                recommendations.append({
                    'category': 'application',
                    'priority': 'high' if app_score < 60 else 'medium',
                    'title': 'Improve Application Performance',
                    'description': 'Application metrics indicate performance issues',
                    'actions': [
                        'Analyze error patterns',
                        'Optimize response times',
                        'Implement caching strategies'
                    ]
                })
        
        # Database recommendations
        if 'database' in latest_health['components']:
            db_score = latest_health['components']['database']['score']
            if db_score < 80:
                recommendations.append({
                    'category': 'database',
                    'priority': 'medium',
                    'title': 'Optimize Database Performance',
                    'description': 'Database performance can be improved',
                    'actions': [
                        'Optimize slow queries',
                        'Review indexing strategy',
                        'Implement query caching'
                    ]
                })
        
        return recommendations
    
    async def stop_monitoring(self):
        """Stop the monitoring system."""
if __name__ == "__main__":
            logger.info("Stopping self-monitoring system...")
        self.is_monitoring = False
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['acknowledged'] = True
                alert['acknowledged_at'] = datetime.now().isoformat()
if __name__ == "__main__":
                    logger.info(f"Alert {alert_id} acknowledged")
                return True
        
        return False

async def main():
    """Main function to run self-monitoring system."""
    monitor = SelfMonitoringSystem()
    
    # Start monitoring in background
    monitoring_task = asyncio.create_task(monitor.start_monitoring())
    
    # Wait a bit for some data to be collected
    await asyncio.sleep(5)
    
    # Generate health report
    report = await monitor.get_health_report()
if __name__ == "__main__":
        print(f"Health report: {json.dumps(report, indent=2)}")
    
    # Stop monitoring
    await monitor.stop_monitoring()
    monitoring_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
