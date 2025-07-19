import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.config import Config
from src.models.user import db
from src.routes.user import user_bp
from src.routes.boardroom import boardroom_bp
from src.routes.x_integration import x_integration_bp
from src.routes.typefully_integration import typefully_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Load configuration
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['DEBUG'] = Config.DEBUG

# Enable CORS for all routes
CORS(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(boardroom_bp, url_prefix='/api/boardroom')
app.register_blueprint(x_integration_bp, url_prefix='/api/x')
app.register_blueprint(typefully_bp, url_prefix='/api/typefully')

# Database configuration
try:
    db_config = Config.get_database_config()
    app.config.update(db_config)
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("Database initialized successfully")
except Exception as e:
    print(f"Database initialization failed: {e}")
    print("Running without database - some features may not work")

@app.route('/health')
def health_check():
    """Health check endpoint"""
    config_validation = Config.validate_required_config()
    config_summary = Config.get_config_summary()
    
    return jsonify({
        'status': 'healthy',
        'config_validation': config_validation,
        'config_summary': config_summary
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
