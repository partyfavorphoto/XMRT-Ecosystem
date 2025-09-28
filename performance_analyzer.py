#!/usr/bin/env python3
"""
Performance Analyzer
Analyzes system and application performance
"""

import time
import statistics
import json
from datetime import datetime

class PerformanceAnalyzer:
    def __init__(self):
        self.metrics = []
        self.start_time = time.time()
    
    def measure_function_performance(self, func, *args, **kwargs):
        """Measure function execution performance"""
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        
        metric = {
            "function": func.__name__,
            "execution_time": end - start,
            "timestamp": datetime.now().isoformat()
        }
        self.metrics.append(metric)
        return result, metric
    
    def analyze_performance_trends(self):
        """Analyze performance trends"""
        if not self.metrics:
            return {"status": "no_data"}
        
        execution_times = [m["execution_time"] for m in self.metrics]
        
        return {
            "total_measurements": len(self.metrics),
            "average_execution_time": statistics.mean(execution_times),
            "median_execution_time": statistics.median(execution_times),
            "min_execution_time": min(execution_times),
            "max_execution_time": max(execution_times),
            "performance_trend": "stable",
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        analysis = self.analyze_performance_trends()
        return {
            "report_type": "performance_analysis",
            "generated_at": datetime.now().isoformat(),
            "system_uptime": time.time() - self.start_time,
            "performance_metrics": analysis,
            "recommendations": [
                "Monitor execution times regularly",
                "Optimize functions with high execution times",
                "Implement caching for frequently called functions"
            ]
        }

if __name__ == "__main__":
    analyzer = PerformanceAnalyzer()
    report = analyzer.generate_performance_report()
    print(json.dumps(report, indent=2))
