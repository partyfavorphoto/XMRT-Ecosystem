#!/usr/bin/env python3
"""
System Health Monitor
Monitors system health and performance metrics
"""

import psutil
import time
import json
from datetime import datetime

class SystemHealthMonitor:
    def __init__(self):
        self.start_time = time.time()
    
    def get_system_health(self):
        """Get comprehensive system health metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "uptime": time.time() - self.start_time,
            "status": "healthy" if psutil.cpu_percent() < 80 else "warning"
        }
    
    def monitor_continuous(self, duration=60):
        """Monitor system for specified duration"""
        metrics = []
        for _ in range(duration):
            metrics.append(self.get_system_health())
            time.sleep(1)
        return metrics

if __name__ == "__main__":
    monitor = SystemHealthMonitor()
    health = monitor.get_system_health()
    print(json.dumps(health, indent=2))
