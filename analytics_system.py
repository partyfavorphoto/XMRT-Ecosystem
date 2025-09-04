"""
Analytics System for XMRT-Ecosystem - Advanced Monitoring & Intelligence

Provides comprehensive analytics, monitoring, and intelligence capabilities
for the autonomous AI ecosystem with real-time insights and optimization.
"""

import os
import json
import time
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    response_time: float
    memory_usage: float
    cpu_usage: float
    active_connections: int
    throughput: float
    error_rate: float
    learning_accuracy: float

@dataclass
class UserBehavior:
    """User behavior tracking data structure"""
    user_id: str
    session_id: str
    timestamp: datetime
    action: str
    context: Dict[str, Any]
    engagement_score: float

class AnalyticsEngine:
    """Advanced Analytics and Monitoring Engine"""

    def __init__(self, config: Dict[str, Any], memory_system=None, socketio=None, logger=None):
        self.config = config
        self.memory_system = memory_system
        self.socketio = socketio
        self.logger = logger or logging.getLogger(__name__)

        # Analytics data storage
        self.performance_metrics = deque(maxlen=10000)
        self.user_behaviors = deque(maxlen=50000)
        self.system_events = deque(maxlen=20000)
        self.prediction_cache = {}

        # Real-time tracking
        self.active_sessions = {}
        self.client_monitors = {}
        self.alert_thresholds = {
            'response_time': 2.0,
            'memory_usage': 0.8,
            'cpu_usage': 0.9,
            'error_rate': 0.05
        }

        # Analytics state
        self.is_monitoring = False
        self.analytics_thread = None

        self.logger.info("🔥 Analytics Engine initialized")

    def start_monitoring(self):
        """Start real-time analytics monitoring"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.analytics_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.analytics_thread.start()
        self.logger.info("📊 Real-time analytics monitoring started")

    def stop_monitoring(self):
        """Stop analytics monitoring"""
        self.is_monitoring = False
        if self.analytics_thread:
            self.analytics_thread.join(timeout=5.0)
        self.logger.info("📊 Analytics monitoring stopped")

    def _monitoring_loop(self):
        """Main analytics monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                self._collect_performance_metrics()

                # Analyze trends
                self._analyze_performance_trends()

                # Check for anomalies
                self._detect_anomalies()

                # Update predictions
                self._update_predictions()

                # Emit real-time updates
                if self.socketio:
                    self._emit_real_time_updates()

                time.sleep(30)  # Update every 30 seconds

            except Exception as e:
                self.logger.error(f"Error in analytics monitoring loop: {e}")
                time.sleep(60)

    def _collect_performance_metrics(self):
        """Collect current performance metrics"""
        try:
            import psutil

            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            # Create performance metric
            metric = PerformanceMetrics(
                timestamp=datetime.now(),
                response_time=self._calculate_avg_response_time(),
                memory_usage=memory.percent / 100.0,
                cpu_usage=cpu_percent / 100.0,
                active_connections=len(self.active_sessions),
                throughput=self._calculate_throughput(),
                error_rate=self._calculate_error_rate(),
                learning_accuracy=self._get_learning_accuracy()
            )

            self.performance_metrics.append(metric)

        except Exception as e:
            self.logger.error(f"Error collecting performance metrics: {e}")

    def track_user_behavior(self, user_id: str, session_id: str, action: str, context: Dict[str, Any]):
        """Track user behavior for analytics"""
        try:
            behavior = UserBehavior(
                user_id=user_id,
                session_id=session_id,
                timestamp=datetime.now(),
                action=action,
                context=context,
                engagement_score=self._calculate_engagement_score(action, context)
            )

            self.user_behaviors.append(behavior)

            # Update session tracking
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {
                    'start_time': datetime.now(),
                    'actions': [],
                    'user_id': user_id
                }

            self.active_sessions[session_id]['actions'].append(behavior)

        except Exception as e:
            self.logger.error(f"Error tracking user behavior: {e}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics summary"""
        if not self.performance_metrics:
            return {}

        recent_metrics = list(self.performance_metrics)[-100:]  # Last 100 entries

        return {
            'current_response_time': recent_metrics[-1].response_time if recent_metrics else 0,
            'avg_response_time': np.mean([m.response_time for m in recent_metrics]),
            'current_memory_usage': recent_metrics[-1].memory_usage if recent_metrics else 0,
            'avg_memory_usage': np.mean([m.memory_usage for m in recent_metrics]),
            'current_cpu_usage': recent_metrics[-1].cpu_usage if recent_metrics else 0,
            'avg_cpu_usage': np.mean([m.cpu_usage for m in recent_metrics]),
            'active_connections': len(self.active_sessions),
            'throughput': self._calculate_throughput(),
            'error_rate': self._calculate_error_rate(),
            'uptime_hours': self._calculate_uptime(),
            'total_requests': len(self.user_behaviors),
            'unique_users': len(set(b.user_id for b in self.user_behaviors))
        }

    def get_user_analytics(self) -> Dict[str, Any]:
        """Get user behavior analytics"""
        if not self.user_behaviors:
            return {}

        recent_behaviors = [b for b in self.user_behaviors if b.timestamp > datetime.now() - timedelta(hours=24)]

        # Action frequency
        action_counts = defaultdict(int)
        for behavior in recent_behaviors:
            action_counts[behavior.action] += 1

        # User engagement
        user_engagement = defaultdict(list)
        for behavior in recent_behaviors:
            user_engagement[behavior.user_id].append(behavior.engagement_score)

        avg_engagement = {
            user_id: np.mean(scores) 
            for user_id, scores in user_engagement.items()
        }

        return {
            'total_actions_24h': len(recent_behaviors),
            'unique_users_24h': len(set(b.user_id for b in recent_behaviors)),
            'top_actions': dict(sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'avg_engagement_score': np.mean([b.engagement_score for b in recent_behaviors]),
            'top_engaged_users': dict(sorted(avg_engagement.items(), key=lambda x: x[1], reverse=True)[:5])
        }

    def predict_system_load(self, hours_ahead: int = 1) -> Dict[str, Any]:
        """Predict system load for specified hours ahead"""
        if len(self.performance_metrics) < 10:
            return {'prediction': 'insufficient_data'}

        try:
            # Simple time series prediction using recent trends
            recent_metrics = list(self.performance_metrics)[-100:]

            # Extract time series data
            timestamps = [m.timestamp for m in recent_metrics]
            cpu_usage = [m.cpu_usage for m in recent_metrics]
            memory_usage = [m.memory_usage for m in recent_metrics]
            throughput = [m.throughput for m in recent_metrics]

            # Calculate trends (simple linear regression)
            cpu_trend = self._calculate_trend(cpu_usage)
            memory_trend = self._calculate_trend(memory_usage)
            throughput_trend = self._calculate_trend(throughput)

            # Predict future values
            prediction = {
                'prediction_time': datetime.now() + timedelta(hours=hours_ahead),
                'predicted_cpu_usage': max(0, min(1.0, cpu_usage[-1] + cpu_trend * hours_ahead)),
                'predicted_memory_usage': max(0, min(1.0, memory_usage[-1] + memory_trend * hours_ahead)),
                'predicted_throughput': max(0, throughput[-1] + throughput_trend * hours_ahead),
                'confidence': self._calculate_prediction_confidence(),
                'recommendations': self._generate_load_recommendations(cpu_trend, memory_trend)
            }

            return prediction

        except Exception as e:
            self.logger.error(f"Error predicting system load: {e}")
            return {'prediction': 'error', 'error': str(e)}

    def detect_performance_anomalies(self) -> List[Dict[str, Any]]:
        """Detect performance anomalies"""
        anomalies = []

        if len(self.performance_metrics) < 20:
            return anomalies

        recent_metrics = list(self.performance_metrics)[-50:]

        # Check for response time anomalies
        response_times = [m.response_time for m in recent_metrics]
        if self._is_anomaly(response_times, self.alert_thresholds['response_time']):
            anomalies.append({
                'type': 'response_time',
                'severity': 'high',
                'message': f"Response time anomaly detected: {response_times[-1]:.2f}s",
                'timestamp': datetime.now(),
                'recommendation': "Check for system bottlenecks or increase resources"
            })

        # Check for memory usage anomalies
        memory_usage = [m.memory_usage for m in recent_metrics]
        if memory_usage[-1] > self.alert_thresholds['memory_usage']:
            anomalies.append({
                'type': 'memory_usage',
                'severity': 'medium',
                'message': f"High memory usage: {memory_usage[-1]*100:.1f}%",
                'timestamp': datetime.now(),
                'recommendation': "Consider memory optimization or scaling"
            })

        # Check for error rate anomalies
        error_rate = self._calculate_error_rate()
        if error_rate > self.alert_thresholds['error_rate']:
            anomalies.append({
                'type': 'error_rate',
                'severity': 'high', 
                'message': f"High error rate: {error_rate*100:.1f}%",
                'timestamp': datetime.now(),
                'recommendation': "Investigate and fix underlying issues"
            })

        return anomalies

    def start_client_monitoring(self, client_id: str):
        """Start monitoring for a specific client"""
        self.client_monitors[client_id] = {
            'start_time': datetime.now(),
            'actions': 0,
            'last_activity': datetime.now()
        }

    def stop_client_monitoring(self, client_id: str):
        """Stop monitoring for a specific client"""
        if client_id in self.client_monitors:
            del self.client_monitors[client_id]

    def health_check(self) -> Dict[str, Any]:
        """Perform analytics system health check"""
        return {
            'status': 'healthy' if self.is_monitoring else 'inactive',
            'monitoring_active': self.is_monitoring,
            'metrics_collected': len(self.performance_metrics),
            'behaviors_tracked': len(self.user_behaviors),
            'active_sessions': len(self.active_sessions),
            'client_monitors': len(self.client_monitors),
            'last_update': datetime.now().isoformat()
        }

    # Helper methods
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time from recent data"""
        if len(self.performance_metrics) < 5:
            return 0.0
        recent = list(self.performance_metrics)[-10:]
        return np.mean([m.response_time for m in recent])

    def _calculate_throughput(self) -> float:
        """Calculate current throughput (requests per second)"""
        if len(self.user_behaviors) < 2:
            return 0.0

        # Calculate requests in last minute
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        recent_requests = sum(1 for b in self.user_behaviors if b.timestamp > one_minute_ago)
        return recent_requests / 60.0

    def _calculate_error_rate(self) -> float:
        """Calculate current error rate"""
        # This would be implemented based on error tracking
        return 0.01  # Placeholder

    def _get_learning_accuracy(self) -> float:
        """Get current learning system accuracy"""
        # This would interface with the learning system
        return 0.85  # Placeholder

    def _calculate_engagement_score(self, action: str, context: Dict[str, Any]) -> float:
        """Calculate engagement score for user action"""
        base_scores = {
            'view': 1.0,
            'click': 2.0,
            'search': 3.0,
            'interact': 4.0,
            'create': 5.0,
            'share': 4.0,
            'feedback': 3.0
        }

        base_score = base_scores.get(action, 1.0)

        # Adjust based on context
        time_spent = context.get('time_spent', 0)
        if time_spent > 30:  # More than 30 seconds
            base_score *= 1.5

        return min(10.0, base_score)

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate simple linear trend"""
        if len(values) < 2:
            return 0.0

        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, 1)
        return coeffs[0]  # Return slope

    def _calculate_prediction_confidence(self) -> float:
        """Calculate confidence level for predictions"""
        if len(self.performance_metrics) < 50:
            return 0.5
        return min(0.95, 0.5 + (len(self.performance_metrics) / 1000))

    def _generate_load_recommendations(self, cpu_trend: float, memory_trend: float) -> List[str]:
        """Generate recommendations based on trends"""
        recommendations = []

        if cpu_trend > 0.1:
            recommendations.append("CPU usage trending up - consider scaling")
        if memory_trend > 0.1:
            recommendations.append("Memory usage trending up - optimize or scale")
        if cpu_trend < -0.05 and memory_trend < -0.05:
            recommendations.append("Resource usage stable - system performing well")

        return recommendations

    def _is_anomaly(self, values: List[float], threshold: float) -> bool:
        """Simple anomaly detection"""
        if len(values) < 5:
            return False

        recent_avg = np.mean(values[-5:])
        overall_avg = np.mean(values)

        return recent_avg > threshold or recent_avg > overall_avg * 2

    def _analyze_performance_trends(self):
        """Analyze performance trends and patterns"""
        # Implementation for trend analysis
        pass

    def _detect_anomalies(self):
        """Advanced anomaly detection"""
        anomalies = self.detect_performance_anomalies()
        if anomalies and self.socketio:
            self.socketio.emit('anomaly_detected', anomalies)

    def _update_predictions(self):
        """Update system predictions"""
        # Update prediction cache
        self.prediction_cache['load_prediction'] = self.predict_system_load()

    def _emit_real_time_updates(self):
        """Emit real-time analytics updates"""
        if not self.socketio:
            return

        update_data = {
            'timestamp': datetime.now().isoformat(),
            'performance_metrics': self.get_performance_metrics(),
            'user_analytics': self.get_user_analytics(),
            'active_sessions': len(self.active_sessions),
            'system_health': self.health_check()
        }

        self.socketio.emit('analytics_update', update_data, room='monitoring')

    def _calculate_uptime(self) -> float:
        """Calculate system uptime in hours"""
        if not hasattr(self, 'start_time'):
            self.start_time = datetime.now()
        return (datetime.now() - self.start_time).total_seconds() / 3600
