#!/usr/bin/env python3
"""
Utility functions for XMRT Mobile Miner
"""

import os
import json
import time
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

def format_timestamp(timestamp: Optional[float] = None) -> str:
    if timestamp is None:
        timestamp = time.time()
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def calculate_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def safe_json_loads(json_string: str, default: Any = None) -> Any:
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"JSON parsing error: {e}")
        return default

def safe_json_dumps(data: Any, indent: int = 2) -> str:
    try:
        return json.dumps(data, indent=indent)
    except (TypeError, ValueError) as e:
        logger.error(f"JSON serialization error: {e}")
        return '{"error": "Serialization failed"}'

def retry_operation(func, max_attempts: int = 3, delay: float = 1.0):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_attempts - 1:
                time.sleep(delay * (2 ** attempt))
    logger.error(f"All {max_attempts} attempts failed")
    return None

def validate_github_token(token: Optional[str]) -> bool:
    if not token:
        return False
    if len(token) < 20:
        return False
    if not token.startswith(('ghp_', 'github_pat_')):
        logger.warning("Token does not match expected format")
    return True

def calculate_uptime(start_time: float) -> Dict[str, Any]:
    uptime_seconds = time.time() - start_time
    return {
        "uptime_seconds": round(uptime_seconds, 2),
        "uptime_minutes": round(uptime_seconds / 60, 2),
        "uptime_hours": round(uptime_seconds / 3600, 2),
        "uptime_days": round(uptime_seconds / 86400, 2),
        "formatted": format_uptime(uptime_seconds)
    }

def format_uptime(seconds: float) -> str:
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)

def sanitize_filename(filename: str) -> str:
    invalid_chars = '<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

def get_environment_info() -> Dict[str, Any]:
    return {
        "python_version": os.sys.version,
        "platform": os.sys.platform,
        "environment_variables": {
            "DEBUG": os.environ.get('DEBUG', 'False'),
            "ENVIRONMENT": os.environ.get('ENVIRONMENT', 'production'),
            "PORT": os.environ.get('PORT', '5000')
        },
        "current_directory": os.getcwd(),
        "timestamp": datetime.now().isoformat()
    }
