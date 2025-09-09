#!/usr/bin/env python3
"""
XMRT-Ecosystem Integration Patch
Applies all API and WebSocket fixes to the main application
"""

import os
import re
from pathlib import Path

def apply_integration_patch():
    """Apply all fixes to the main application files"""
    
    # 1. Patch main.py to include fixed API routes
    main_py_path = Path("main.py")
    
    if main_py_path.exists():
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Add import for fixed API routes
        if "from fixed_api_routes import apply_api_fixes" not in content:
            # Find the imports section and add our import
            import_section = re.search(r'(from flask_socketio import.*?\n)', content)
            if import_section:
                new_import = import_section.group(1) + "from fixed_api_routes import apply_api_fixes\n"
                content = content.replace(import_section.group(1), new_import)
        
        # Add API fixes initialization after socketio initialization
        if "api_fixer = apply_api_fixes(app, socketio)" not in content:
            socketio_init = re.search(r'(socketio = SocketIO\(app.*?\))', content)
            if socketio_init:
                new_init = socketio_init.group(1) + "\n\n# Apply API fixes\napi_fixer = apply_api_fixes(app, socketio)\n"
                content = content.replace(socketio_init.group(1), new_init)
        
        # Write back the patched content
        with open(main_py_path, 'w') as f:
            f.write(content)
        
        print("✅ main.py patched successfully")
    
    # 2. Update index.html to include enhanced frontend integration
    index_html_path = Path("index.html")
    
    if index_html_path.exists():
        with open(index_html_path, 'r') as f:
            content = f.read()
        
        # Add enhanced frontend script before closing body tag
        if "enhanced_frontend_integration.js" not in content:
            script_tag = '<script src="/enhanced_frontend_integration.js"></script>'
            
            # Find closing body tag and add script before it
            if '</body>' in content:
                content = content.replace('</body>', f'    {script_tag}\n</body>')
            else:
                # Add to end of file if no body tag found
                content += f'\n{script_tag}\n'
        
        # Ensure Socket.IO is loaded
        if 'socket.io.js' not in content:
            socketio_script = '<script src="/socket.io/socket.io.js"></script>'
            if '</body>' in content:
                content = content.replace('</body>', f'    {socketio_script}\n</body>')
        
        # Write back the updated content
        with open(index_html_path, 'w') as f:
            f.write(content)
        
        print("✅ index.html updated successfully")
    
    # 3. Create static file serving route for enhanced frontend
    static_route_code = '''
# Enhanced static file serving for frontend integration
@app.route('/enhanced_frontend_integration.js')
def serve_enhanced_frontend():
    """Serve enhanced frontend integration script"""
    try:
        with open('enhanced_frontend_integration.js', 'r') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'application/javascript'}
    except FileNotFoundError:
        return "console.error('Enhanced frontend integration not found');", 404, {'Content-Type': 'application/javascript'}
'''
    
    # Add static route to main.py if not present
    if main_py_path.exists():
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        if "serve_enhanced_frontend" not in content:
            # Find a good place to insert the route (after other routes)
            route_insertion_point = content.rfind("@app.route")
            if route_insertion_point != -1:
                # Find the end of the last route function
                next_function = content.find("\n\n", route_insertion_point)
                if next_function != -1:
                    content = content[:next_function] + "\n" + static_route_code + content[next_function:]
                else:
                    content += "\n" + static_route_code
            else:
                content += "\n" + static_route_code
            
            with open(main_py_path, 'w') as f:
                f.write(content)
            
            print("✅ Static route added successfully")
    
    print("\n🎯 Integration patch applied successfully!")
    print("📋 Changes made:")
    print("   - Fixed API routes integrated")
    print("   - Enhanced WebSocket handlers added")
    print("   - Frontend JavaScript integration updated")
    print("   - Static file serving configured")
    
    return True

if __name__ == "__main__":
    apply_integration_patch()

