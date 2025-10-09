"""
Centralized error handling for XMRT-Ecosystem
"""

import logging
from datetime import datetime
from flask import Flask, jsonify, request

logger = logging.getLogger(__name__)

class XMRTError(Exception):
    """Base exception class for XMRT-Ecosystem"""
    
    def __init__(self, message, code="XMRT_ERROR", status_code=500, details=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()

class GitHubError(XMRTError):
    """GitHub integration errors"""
    
    def __init__(self, message, details=None):
        super().__init__(
            message=message,
            code="GITHUB_ERROR",
            status_code=502,
            details=details
        )

class AIError(XMRTError):
    """AI processing errors"""
    
    def __init__(self, message, details=None):
        super().__init__(
            message=message,
            code="AI_ERROR",
            status_code=502,
            details=details
        )

def register_error_handlers(app):
    """Register error handlers with Flask app"""
    
    @app.errorhandler(XMRTError)
    def handle_xmrt_error(error):
        """Handle custom XMRT errors"""
        logger.error(f"XMRT Error [{error.code}]: {error.message}")
        
        response = {
            "error": {
                "code": error.code,
                "message": error.message,
                "timestamp": error.timestamp,
                "details": error.details
            }
        }
        
        return jsonify(response), error.status_code
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors"""
        logger.warning(f"404 Not Found: {request.path}")
        
        response = {
            "error": {
                "code": "NOT_FOUND",
                "message": f"Endpoint not found: {request.path}",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return jsonify(response), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 errors"""
        logger.error(f"Internal Server Error: {str(error)}")
        
        response = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal server error occurred",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return jsonify(response), 500
