# XMRT Ecosystem Security Configuration

import os
from typing import List, Dict, Any
from functools import wraps
from flask import request, abort, current_app
import hashlib
import hmac
import time

class SecurityConfig:
    """Centralized security configuration"""
    
    # Rate limiting configurations
    RATE_LIMITS = {
        'default': '100 per hour',
        'api_endpoints': '50 per hour',
        'sensitive_endpoints': '10 per hour',
        'innovation_cycle': '5 per hour'
    }
    
    # Protected endpoints requiring authentication
    PROTECTED_ENDPOINTS = [
        'api_run_cycle',
        'run_cycle_endpoint',
        'webhook_github',
        'webhook_render',
        'webhook_discord'
    ]
    
    # API key validation
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key against configured keys"""
        if not api_key:
            return False
        
        valid_keys = os.getenv('VALID_API_KEYS', '').split(',')
        return api_key.strip() in [key.strip() for key in valid_keys if key.strip()]
    
    @staticmethod
    def validate_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
        """Validate GitHub webhook signature"""
        if not signature or not secret:
            return False
        
        expected_signature = 'sha256=' + hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_app.config.get('TESTING'):
            return f(*args, **kwargs)
        
        api_key = request.headers.get('X-API-Key')
        if not SecurityConfig.validate_api_key(api_key):
            abort(401, description="Invalid or missing API key")
        
        return f(*args, **kwargs)
    return decorated_function

def validate_input(schema):
    """Decorator for input validation"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.is_json:
                try:
                    data = schema.load(request.get_json())
                    request.validated_data = data
                except Exception as e:
                    abort(400, description=f"Invalid input: {str(e)}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Input validation schemas
from marshmallow import Schema, fields, validate

class IssueCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    body = fields.Str(required=True, validate=validate.Length(min=1, max=65000))
    labels = fields.List(fields.Str(), missing=[])

class CycleRunSchema(Schema):
    force = fields.Bool(missing=False)
    dry_run = fields.Bool(missing=False)
