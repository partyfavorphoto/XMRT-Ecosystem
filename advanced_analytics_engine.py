#!/usr/bin/env python3
"""
XMRT-Ecosystem: Advanced Analytics Engine v2.0
Predictive analytics, pattern recognition, and performance optimization

Features:
- Real-time performance analytics with predictive modeling
- Machine learning-based pattern recognition
- Anomaly detection and alerting
- Predictive resource allocation and capacity planning
- Advanced visualization and reporting
- Time series analysis and forecasting
- Behavioral analytics and user journey mapping
- Custom metric tracking and KPI monitoring
"""

import asyncio
import logging
import json
import time
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict, deque
import statistics
from abc import ABC, abstractmethod

# ML and analytics imports
try:
    from sklearn.ensemble import IsolationForest, RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import DBSCAN
    from sklearn.decomposition import PCA
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics to track"""
    PERFORMANCE = "performance"
    USAGE = "usage"
    ERROR = "error"
    BUSINESS = "business"
    SYSTEM = "system"
    USER_BEHAVIOR = "user_behavior"
    AGENT_ACTIVITY = "agent_activity"

class AnomalyLevel(Enum):
    """Severity levels for anomalies"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PredictionType(Enum):
    """Types of predictions"""
    LOAD_FORECAST = "load_forecast"
    PERFORMANCE_TREND = "performance_trend"
    CAPACITY_PLANNING = "capacity_planning"
    USER_BEHAVIOR = "user_behavior"
    FAILURE_PREDICTION = "failure_prediction"

@dataclass
class MetricPoint:
    """Individual metric data point"""
    timestamp: datetime
    value: float
    metric_name: str
    metric_type: MetricType
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnomalyAlert:
    """Anomaly detection result"""
    id: str
    timestamp: datetime
    metric_name: str
    anomaly_level: AnomalyLevel
    description: str
    detected_value: float
    expected_range: Tuple[float, float]
    confidence: float
    suggested_actions: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PredictionResult:
    """Prediction analysis result"""
    id: str
    prediction_type: PredictionType
    timestamp: datetime
    predicted_values: List[float]
    prediction_timestamps: List[datetime]
    confidence_intervals: List[Tuple[float, float]]
    accuracy_metrics: Dict[str, float]
    model_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceProfile:
    """System or agent performance profile"""
    entity_id: str
    entity_type: str  # 'agent', 'system', 'user'
    metrics: Dict[str, float]
    trends: Dict[str, str]  # 'increasing', 'decreasing', 'stable'
    anomaly_score: float
    performance_grade: str  # 'A', 'B', 'C', 'D', 'F'
    recommendations: List[str]
    last_updated: datetime

class TimeSeriesAnalyzer:
    """Advanced time series analysis and forecasting"""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.data_buffers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))

    def add_data_point(self, metric_name: str, value: float, timestamp: datetime):
        """Add a data point to the time series"""
        self.data_buffers[metric_name].append((timestamp, value))

    def detect_trends(self, metric_name: str, lookback_periods: int = 20) -> Dict[str, Any]:
        """Detect trends in time series data"""
        if metric_name not in self.data_buffers or len(self.data_buffers[metric_name]) < lookback_periods:
            return {'trend': 'insufficient_data', 'confidence': 0.0}

        data = list(self.data_buffers[metric_name])[-lookback_periods:]
        values = [point[1] for point in data]

        # Calculate trend using linear regression
        x = np.arange(len(values))
        y = np.array(values)

        # Simple linear regression
        n = len(x)
        sum_x = np.sum(x)
        sum_y = np.sum(y)
        sum_xy = np.sum(x * y)
        sum_x2 = np.sum(x * x)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)

        # Determine trend direction and strength
        if abs(slope) < 0.001:
            trend = 'stable'
        elif slope > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'

        # Calculate confidence based on R-squared
        y_mean = np.mean(y)
        y_pred = slope * x + (sum_y - slope * sum_x) / n

        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - y_mean) ** 2)

        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        confidence = max(0, min(1, r_squared))

        return {
            'trend': trend,
            'slope': slope,
            'confidence': confidence,
            'r_squared': r_squared,
            'data_points': len(values)
        }

    def forecast(self, metric_name: str, periods_ahead: int = 10) -> Dict[str, Any]:
        """Simple forecasting using exponential smoothing"""
        if metric_name not in self.data_buffers or len(self.data_buffers[metric_name]) < 10:
            return {'error': 'insufficient_data'}

        data = list(self.data_buffers[metric_name])
        values = [point[1] for point in data]
        timestamps = [point[0] for point in data]

        # Exponential smoothing parameters
        alpha = 0.3  # smoothing factor

        # Initialize
        s = [values[0]]

        # Calculate smoothed values
        for i in range(1, len(values)):
            s.append(alpha * values[i] + (1 - alpha) * s[i-1])

        # Forecast
        last_smoothed = s[-1]
        forecasts = []

        # Simple trend component
        if len(s) >= 2:
            trend = s[-1] - s[-2]
        else:
            trend = 0

        last_timestamp = timestamps[-1]
        forecast_timestamps = []

        for i in range(periods_ahead):
            forecast_value = last_smoothed + trend * (i + 1)
            forecasts.append(forecast_value)

            # Estimate next timestamp (assuming regular intervals)
            if len(timestamps) >= 2:
                interval = (timestamps[-1] - timestamps[-2]).total_seconds()
                next_timestamp = last_timestamp + timedelta(seconds=interval * (i + 1))
            else:
                next_timestamp = last_timestamp + timedelta(minutes=5 * (i + 1))

            forecast_timestamps.append(next_timestamp)

        return {
            'forecasts': forecasts,
            'timestamps': forecast_timestamps,
            'confidence': 0.7,  # Simple confidence estimate
            'method': 'exponential_smoothing'
        }

class AnomalyDetector:
    """Advanced anomaly detection using multiple algorithms"""

    def __init__(self):
        self.baseline_stats: Dict[str, Dict[str, float]] = {}
        self.isolation_forests: Dict[str, Any] = {}
        self.update_interval = 3600  # 1 hour
        self.last_model_update = {}

    def update_baseline(self, metric_name: str, data_points: List[float]):
        """Update baseline statistics for a metric"""
        if len(data_points) < 5:
            return

        self.baseline_stats[metric_name] = {
            'mean': statistics.mean(data_points),
            'median': statistics.median(data_points),
            'std': statistics.stdev(data_points) if len(data_points) > 1 else 0,
            'min': min(data_points),
            'max': max(data_points),
            'q25': np.percentile(data_points, 25),
            'q75': np.percentile(data_points, 75),
            'iqr': np.percentile(data_points, 75) - np.percentile(data_points, 25)
        }

        # Update Isolation Forest model if available
        if SKLEARN_AVAILABLE and len(data_points) >= 10:
            try:
                # Reshape for sklearn
                X = np.array(data_points).reshape(-1, 1)

                # Create and fit Isolation Forest
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                iso_forest.fit(X)

                self.isolation_forests[metric_name] = iso_forest
                self.last_model_update[metric_name] = datetime.utcnow()

            except Exception as e:
                logger.warning(f"Failed to update Isolation Forest for {metric_name}: {e}")

    def detect_anomaly(self, metric_name: str, value: float, timestamp: datetime) -> Optional[AnomalyAlert]:
        """Detect if a value is anomalous"""

        if metric_name not in self.baseline_stats:
            return None

        stats = self.baseline_stats[metric_name]
        anomaly_level = None
        description = ""
        confidence = 0.0
        expected_range = (stats['min'], stats['max'])

        # Statistical outlier detection (Z-score method)
        if stats['std'] > 0:
            z_score = abs(value - stats['mean']) / stats['std']

            if z_score > 3:
                anomaly_level = AnomalyLevel.CRITICAL
                confidence = min(0.95, z_score / 10)
                description = f"Extreme outlier detected (Z-score: {z_score:.2f})"
            elif z_score > 2.5:
                anomaly_level = AnomalyLevel.HIGH
                confidence = min(0.85, z_score / 8)
                description = f"High anomaly detected (Z-score: {z_score:.2f})"
            elif z_score > 2:
                anomaly_level = AnomalyLevel.MEDIUM
                confidence = min(0.75, z_score / 6)
                description = f"Moderate anomaly detected (Z-score: {z_score:.2f})"

        # IQR-based detection
        iqr_lower = stats['q25'] - 1.5 * stats['iqr']
        iqr_upper = stats['q75'] + 1.5 * stats['iqr']

        if value < iqr_lower or value > iqr_upper:
            if anomaly_level is None:
                anomaly_level = AnomalyLevel.MEDIUM
                confidence = 0.7
                description = f"IQR outlier detected (value: {value:.2f}, expected: {iqr_lower:.2f}-{iqr_upper:.2f})"

            expected_range = (iqr_lower, iqr_upper)

        # Isolation Forest detection
        if SKLEARN_AVAILABLE and metric_name in self.isolation_forests:
            try:
                iso_forest = self.isolation_forests[metric_name]
                anomaly_score = iso_forest.decision_function([[value]])[0]
                is_anomaly = iso_forest.predict([[value]])[0] == -1

                if is_anomaly:
                    if anomaly_level is None:
                        anomaly_level = AnomalyLevel.MEDIUM
                        confidence = max(confidence, 0.8)
                        description = f"ML anomaly detected (score: {anomaly_score:.3f})"
                    else:
                        confidence = max(confidence, 0.9)
                        description += f" + ML confirmed (score: {anomaly_score:.3f})"

            except Exception as e:
                logger.warning(f"Isolation Forest detection failed for {metric_name}: {e}")

        # Create alert if anomaly detected
        if anomaly_level:
            suggested_actions = self._generate_suggested_actions(metric_name, value, anomaly_level)

            return AnomalyAlert(
                id=str(uuid.uuid4()),
                timestamp=timestamp,
                metric_name=metric_name,
                anomaly_level=anomaly_level,
                description=description,
                detected_value=value,
                expected_range=expected_range,
                confidence=confidence,
                suggested_actions=suggested_actions,
                context={'baseline_stats': stats}
            )

        return None

    def _generate_suggested_actions(self, metric_name: str, value: float, level: AnomalyLevel) -> List[str]:
        """Generate suggested actions based on anomaly type and severity"""
        actions = []

        metric_lower = metric_name.lower()

        if level in [AnomalyLevel.CRITICAL, AnomalyLevel.HIGH]:
            actions.append("Investigate immediately")
            actions.append("Check system logs for errors")

        if 'cpu' in metric_lower or 'memory' in metric_lower:
            actions.append("Monitor resource usage")
            actions.append("Check for resource-intensive processes")
            if level == AnomalyLevel.CRITICAL:
                actions.append("Consider scaling resources")

        elif 'response_time' in metric_lower or 'latency' in metric_lower:
            actions.append("Check network connectivity")
            actions.append("Analyze slow queries or operations")
            if level >= AnomalyLevel.HIGH:
                actions.append("Consider load balancing")

        elif 'error' in metric_lower or 'failure' in metric_lower:
            actions.append("Review error logs")
            actions.append("Check system health")
            if level == AnomalyLevel.CRITICAL:
                actions.append("Implement emergency response procedures")

        if not actions:
            actions.extend([
                "Monitor trend continuation",
                "Investigate root cause",
                "Review recent system changes"
            ])

        return actions

class AdvancedAnalyticsEngine:
    """
    Advanced Analytics Engine for comprehensive system monitoring and optimization

    Features:
    - Real-time metric collection and analysis
    - Predictive analytics and forecasting
    - Anomaly detection with machine learning
    - Performance profiling and optimization recommendations
    - Custom dashboard and reporting
    - Behavioral analytics and pattern recognition
    """

    def __init__(self, retention_days: int = 30):
        self.retention_days = retention_days
        self.metrics_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.time_series_analyzer = TimeSeriesAnalyzer()
        self.anomaly_detector = AnomalyDetector()

        # Analytics state
        self.running = False
        self.analysis_interval = 60.0  # seconds
        self.cleanup_interval = 3600.0  # 1 hour

        # Performance profiles
        self.performance_profiles: Dict[str, PerformanceProfile] = {}

        # Alert callbacks
        self.alert_callbacks: List[Callable] = []

        # Custom metrics and KPIs
        self.custom_metrics: Dict[str, Callable] = {}
        self.kpi_definitions: Dict[str, Dict[str, Any]] = {}

        # Prediction models
        self.prediction_models: Dict[str, Any] = {}

        logger.info("🔬 Advanced Analytics Engine initialized")

    async def start(self):
        """Start the analytics engine"""
        self.running = True

        # Start background processes
        analysis_task = asyncio.create_task(self._analysis_loop())
        cleanup_task = asyncio.create_task(self._cleanup_loop())
        model_update_task = asyncio.create_task(self._model_update_loop())

        logger.info("🚀 Advanced Analytics Engine started")

        return [analysis_task, cleanup_task, model_update_task]

    async def stop(self):
        """Stop the analytics engine"""
        self.running = False
        logger.info("⏹️ Advanced Analytics Engine stopping...")

    def record_metric(self, name: str, value: float, metric_type: MetricType = MetricType.SYSTEM,
                     tags: Dict[str, str] = None, metadata: Dict[str, Any] = None):
        """Record a metric value"""
        timestamp = datetime.utcnow()

        metric_point = MetricPoint(
            timestamp=timestamp,
            value=value,
            metric_name=name,
            metric_type=metric_type,
            tags=tags or {},
            metadata=metadata or {}
        )

        # Store in buffer
        self.metrics_buffer[name].append(metric_point)

        # Update time series analyzer
        self.time_series_analyzer.add_data_point(name, value, timestamp)

        # Check for anomalies
        asyncio.create_task(self._check_anomaly_async(name, value, timestamp))

    async def _check_anomaly_async(self, metric_name: str, value: float, timestamp: datetime):
        """Asynchronously check for anomalies"""
        try:
            anomaly = self.anomaly_detector.detect_anomaly(metric_name, value, timestamp)

            if anomaly:
                logger.warning(f"🚨 Anomaly detected in {metric_name}: {anomaly.description}")

                # Notify callbacks
                for callback in self.alert_callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(anomaly)
                        else:
                            callback(anomaly)
                    except Exception as e:
                        logger.error(f"Alert callback error: {e}")

        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")

    def add_alert_callback(self, callback: Callable):
        """Add a callback for anomaly alerts"""
        self.alert_callbacks.append(callback)

    def register_custom_metric(self, name: str, calculator: Callable[[], float]):
        """Register a custom metric calculator"""
        self.custom_metrics[name] = calculator
        logger.info(f"📊 Custom metric '{name}' registered")

    def define_kpi(self, name: str, metric_names: List[str], calculation_method: str,
                   target_value: float = None, acceptable_range: Tuple[float, float] = None):
        """Define a KPI based on existing metrics"""
        self.kpi_definitions[name] = {
            'metric_names': metric_names,
            'calculation_method': calculation_method,
            'target_value': target_value,
            'acceptable_range': acceptable_range
        }
        logger.info(f"🎯 KPI '{name}' defined")

    def get_metric_summary(self, metric_name: str, time_window: timedelta = None) -> Dict[str, Any]:
        """Get comprehensive summary for a metric"""
        if metric_name not in self.metrics_buffer:
            return {'error': 'Metric not found'}

        data_points = list(self.metrics_buffer[metric_name])

        # Apply time window filter
        if time_window:
            cutoff_time = datetime.utcnow() - time_window
            data_points = [dp for dp in data_points if dp.timestamp >= cutoff_time]

        if not data_points:
            return {'error': 'No data points in time window'}

        values = [dp.value for dp in data_points]

        # Basic statistics
        summary = {
            'metric_name': metric_name,
            'data_points': len(values),
            'time_range': {
                'start': min(dp.timestamp for dp in data_points).isoformat(),
                'end': max(dp.timestamp for dp in data_points).isoformat()
            },
            'statistics': {
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'std': statistics.stdev(values) if len(values) > 1 else 0,
                'min': min(values),
                'max': max(values),
                'range': max(values) - min(values)
            }
        }

        # Add trend analysis
        trends = self.time_series_analyzer.detect_trends(metric_name)
        summary['trends'] = trends

        # Add forecast
        forecast = self.time_series_analyzer.forecast(metric_name, 10)
        if 'error' not in forecast:
            summary['forecast'] = forecast

        return summary

    def get_performance_profile(self, entity_id: str, entity_type: str) -> Optional[PerformanceProfile]:
        """Get performance profile for an entity"""
        profile_key = f"{entity_type}:{entity_id}"
        return self.performance_profiles.get(profile_key)

    def calculate_kpis(self) -> Dict[str, Any]:
        """Calculate all defined KPIs"""
        kpi_results = {}

        for kpi_name, definition in self.kpi_definitions.items():
            try:
                metric_values = {}

                # Gather metric values
                for metric_name in definition['metric_names']:
                    if metric_name in self.metrics_buffer and self.metrics_buffer[metric_name]:
                        recent_values = [dp.value for dp in list(self.metrics_buffer[metric_name])[-10:]]
                        metric_values[metric_name] = statistics.mean(recent_values)

                # Calculate KPI based on method
                method = definition['calculation_method']
                kpi_value = None

                if method == 'mean' and metric_values:
                    kpi_value = statistics.mean(metric_values.values())
                elif method == 'sum' and metric_values:
                    kpi_value = sum(metric_values.values())
                elif method == 'ratio' and len(metric_values) >= 2:
                    values_list = list(metric_values.values())
                    kpi_value = values_list[0] / values_list[1] if values_list[1] != 0 else 0

                if kpi_value is not None:
                    # Evaluate against targets
                    status = 'unknown'
                    if definition.get('target_value'):
                        target = definition['target_value']
                        deviation = abs(kpi_value - target) / target
                        if deviation < 0.05:
                            status = 'excellent'
                        elif deviation < 0.1:
                            status = 'good'
                        elif deviation < 0.2:
                            status = 'acceptable'
                        else:
                            status = 'poor'

                    elif definition.get('acceptable_range'):
                        low, high = definition['acceptable_range']
                        if low <= kpi_value <= high:
                            status = 'good'
                        else:
                            status = 'poor'

                    kpi_results[kpi_name] = {
                        'value': kpi_value,
                        'status': status,
                        'target': definition.get('target_value'),
                        'range': definition.get('acceptable_range'),
                        'component_metrics': metric_values
                    }

            except Exception as e:
                logger.error(f"KPI calculation error for {kpi_name}: {e}")
                kpi_results[kpi_name] = {'error': str(e)}

        return kpi_results

    async def generate_insights(self, entity_id: str = None, time_window: timedelta = None) -> Dict[str, Any]:
        """Generate analytical insights"""
        insights = {
            'timestamp': datetime.utcnow().isoformat(),
            'time_window': str(time_window) if time_window else 'all_time',
            'entity_id': entity_id,
            'summary': {},
            'anomalies': [],
            'trends': {},
            'recommendations': [],
            'predictions': {}
        }

        # Analyze all metrics or filtered by entity
        metrics_to_analyze = []

        if entity_id:
            # Filter metrics related to specific entity
            metrics_to_analyze = [name for name in self.metrics_buffer.keys() 
                                if entity_id in name or entity_id in str(self.metrics_buffer[name])]
        else:
            metrics_to_analyze = list(self.metrics_buffer.keys())

        # Generate insights for each metric
        for metric_name in metrics_to_analyze[:20]:  # Limit to prevent overload
            try:
                summary = self.get_metric_summary(metric_name, time_window)
                if 'error' not in summary:
                    insights['summary'][metric_name] = summary['statistics']

                    if 'trends' in summary:
                        insights['trends'][metric_name] = summary['trends']

                    # Check for recent anomalies (simplified)
                    recent_data = list(self.metrics_buffer[metric_name])[-20:]
                    for dp in recent_data:
                        if time_window:
                            cutoff = datetime.utcnow() - time_window
                            if dp.timestamp < cutoff:
                                continue

                        # This is a simplified anomaly check
                        if abs(dp.value - summary['statistics']['mean']) > 2 * summary['statistics']['std']:
                            insights['anomalies'].append({
                                'metric': metric_name,
                                'value': dp.value,
                                'timestamp': dp.timestamp.isoformat(),
                                'deviation': abs(dp.value - summary['statistics']['mean'])
                            })

            except Exception as e:
                logger.error(f"Insight generation error for {metric_name}: {e}")

        # Generate recommendations
        insights['recommendations'] = self._generate_recommendations(insights)

        return insights

    def _generate_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on insights"""
        recommendations = []

        # Analyze trends
        increasing_trends = [name for name, trend in insights['trends'].items() 
                           if trend.get('trend') == 'increasing' and trend.get('confidence', 0) > 0.7]

        decreasing_trends = [name for name, trend in insights['trends'].items()
                           if trend.get('trend') == 'decreasing' and trend.get('confidence', 0) > 0.7]

        if increasing_trends:
            recommendations.append(f"Monitor increasing trends in: {', '.join(increasing_trends[:3])}")

        if decreasing_trends:
            recommendations.append(f"Investigate decreasing trends in: {', '.join(decreasing_trends[:3])}")

        # Analyze anomalies
        if len(insights['anomalies']) > 5:
            recommendations.append("High anomaly count detected - investigate system stability")

        # Performance recommendations
        cpu_metrics = [name for name in insights['summary'].keys() if 'cpu' in name.lower()]
        memory_metrics = [name for name in insights['summary'].keys() if 'memory' in name.lower()]

        for metric in cpu_metrics:
            if insights['summary'][metric]['mean'] > 80:
                recommendations.append("High CPU usage detected - consider scaling or optimization")

        for metric in memory_metrics:
            if insights['summary'][metric]['mean'] > 80:
                recommendations.append("High memory usage detected - investigate memory leaks")

        if not recommendations:
            recommendations.append("System performance appears stable - continue monitoring")

        return recommendations

    async def _analysis_loop(self):
        """Background analysis loop"""
        while self.running:
            try:
                await self._update_performance_profiles()
                await self._calculate_custom_metrics()
                await self._update_anomaly_baselines()

                await asyncio.sleep(self.analysis_interval)

            except Exception as e:
                logger.error(f"Analysis loop error: {e}")
                await asyncio.sleep(5.0)

    async def _cleanup_loop(self):
        """Background cleanup loop"""
        while self.running:
            try:
                await self._cleanup_old_data()

                await asyncio.sleep(self.cleanup_interval)

            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(60.0)

    async def _model_update_loop(self):
        """Background model update loop"""
        while self.running:
            try:
                await self._update_prediction_models()

                await asyncio.sleep(1800)  # 30 minutes

            except Exception as e:
                logger.error(f"Model update loop error: {e}")
                await asyncio.sleep(300.0)

    async def _update_performance_profiles(self):
        """Update performance profiles for entities"""
        # This would be implemented based on specific entities in the system
        # For now, create a system-wide profile

        system_metrics = {}

        # Gather recent metrics
        for metric_name, buffer in self.metrics_buffer.items():
            if buffer:
                recent_values = [dp.value for dp in list(buffer)[-10:]]
                system_metrics[metric_name] = statistics.mean(recent_values)

        if system_metrics:
            # Calculate overall performance grade
            anomaly_count = len([m for m in system_metrics if abs(system_metrics[m]) > 100])
            performance_grade = 'A'

            if anomaly_count > 5:
                performance_grade = 'F'
            elif anomaly_count > 3:
                performance_grade = 'D'
            elif anomaly_count > 1:
                performance_grade = 'C'
            elif anomaly_count > 0:
                performance_grade = 'B'

            self.performance_profiles['system:overall'] = PerformanceProfile(
                entity_id='overall',
                entity_type='system',
                metrics=system_metrics,
                trends={name: self.time_series_analyzer.detect_trends(name)['trend'] 
                       for name in list(system_metrics.keys())[:5]},
                anomaly_score=anomaly_count / len(system_metrics) if system_metrics else 0,
                performance_grade=performance_grade,
                recommendations=self._generate_recommendations({'summary': system_metrics, 'trends': {}, 'anomalies': []}),
                last_updated=datetime.utcnow()
            )

    async def _calculate_custom_metrics(self):
        """Calculate custom metrics"""
        for metric_name, calculator in self.custom_metrics.items():
            try:
                value = calculator()
                self.record_metric(metric_name, value, MetricType.BUSINESS)

            except Exception as e:
                logger.error(f"Custom metric calculation error for {metric_name}: {e}")

    async def _update_anomaly_baselines(self):
        """Update anomaly detection baselines"""
        for metric_name, buffer in self.metrics_buffer.items():
            if len(buffer) >= 10:
                values = [dp.value for dp in buffer]
                self.anomaly_detector.update_baseline(metric_name, values)

    async def _cleanup_old_data(self):
        """Clean up old data beyond retention period"""
        cutoff_time = datetime.utcnow() - timedelta(days=self.retention_days)

        for metric_name in list(self.metrics_buffer.keys()):
            buffer = self.metrics_buffer[metric_name]

            # Remove old data points
            while buffer and buffer[0].timestamp < cutoff_time:
                buffer.popleft()

            # Remove empty buffers
            if not buffer:
                del self.metrics_buffer[metric_name]

    async def _update_prediction_models(self):
        """Update prediction models with recent data"""
        if not SKLEARN_AVAILABLE:
            return

        for metric_name, buffer in self.metrics_buffer.items():
            if len(buffer) >= 50:  # Need sufficient data for ML models
                try:
                    # Prepare data
                    data_points = list(buffer)[-100:]  # Last 100 points
                    X = np.array([[i] for i in range(len(data_points))])
                    y = np.array([dp.value for dp in data_points])

                    # Train simple regression model
                    model = RandomForestRegressor(n_estimators=10, random_state=42)
                    model.fit(X, y)

                    self.prediction_models[metric_name] = {
                        'model': model,
                        'last_updated': datetime.utcnow(),
                        'data_points': len(data_points)
                    }

                except Exception as e:
                    logger.warning(f"Model update failed for {metric_name}: {e}")

# Example usage and integration functions
def create_sample_kpis(analytics: AdvancedAnalyticsEngine):
    """Create sample KPI definitions"""
    analytics.define_kpi(
        'system_health',
        ['cpu_usage', 'memory_usage'],
        'mean',
        target_value=50.0,
        acceptable_range=(0, 80)
    )

    analytics.define_kpi(
        'performance_efficiency',
        ['response_time', 'throughput'],
        'ratio',
        target_value=0.1
    )

async def example_alert_handler(anomaly: AnomalyAlert):
    """Example anomaly alert handler"""
    logger.warning(f"ALERT: {anomaly.description}")

    # Here you could send notifications, create tickets, etc.
    if anomaly.anomaly_level == AnomalyLevel.CRITICAL:
        logger.critical(f"CRITICAL ALERT: {anomaly.metric_name} = {anomaly.detected_value}")

async def main():
    """Example usage of Advanced Analytics Engine"""

    # Initialize analytics engine
    analytics = AdvancedAnalyticsEngine(retention_days=7)

    # Add alert handler
    analytics.add_alert_callback(example_alert_handler)

    # Define custom metrics
    def system_efficiency():
        return 95.0 + np.random.normal(0, 2)

    analytics.register_custom_metric('system_efficiency', system_efficiency)

    # Create sample KPIs
    create_sample_kpis(analytics)

    # Start analytics
    await analytics.start()

    # Simulate some metrics
    for i in range(100):
        analytics.record_metric('cpu_usage', 50 + np.random.normal(0, 10), MetricType.SYSTEM)
        analytics.record_metric('memory_usage', 60 + np.random.normal(0, 5), MetricType.SYSTEM)
        analytics.record_metric('response_time', 100 + np.random.normal(0, 20), MetricType.PERFORMANCE)

        await asyncio.sleep(0.1)

    # Generate insights
    insights = await analytics.generate_insights()
    print(json.dumps(insights, indent=2, default=str))

    # Calculate KPIs
    kpis = analytics.calculate_kpis()
    print("KPIs:", json.dumps(kpis, indent=2))

    await analytics.stop()

if __name__ == "__main__":
    asyncio.run(main())
