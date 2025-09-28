#!/usr/bin/env python3
"""
API Documentation Generator
Automatically generates API documentation
"""

import inspect
import json
from datetime import datetime

class APIDocumentationGenerator:
    def __init__(self):
        self.docs = {
            "generated_at": datetime.now().isoformat(),
            "endpoints": [],
            "version": "1.0.0"
        }
    
    def analyze_flask_app(self, app):
        """Analyze Flask app and generate documentation"""
        for rule in app.url_map.iter_rules():
            endpoint_doc = {
                "endpoint": rule.rule,
                "methods": list(rule.methods),
                "function": rule.endpoint,
                "description": f"API endpoint: {rule.rule}"
            }
            self.docs["endpoints"].append(endpoint_doc)
        return self.docs
    
    def generate_markdown(self):
        """Generate markdown documentation"""
        md = f"# API Documentation\n\nGenerated: {self.docs['generated_at']}\n\n"
        for endpoint in self.docs["endpoints"]:
            md += f"## {endpoint['endpoint']}\n"
            md += f"**Methods**: {', '.join(endpoint['methods'])}\n"
            md += f"**Description**: {endpoint['description']}\n\n"
        return md
    
    def save_documentation(self, filename="api_docs.md"):
        """Save documentation to file"""
        with open(filename, 'w') as f:
            f.write(self.generate_markdown())
        return filename

if __name__ == "__main__":
    generator = APIDocumentationGenerator()
    print("API Documentation Generator ready")
