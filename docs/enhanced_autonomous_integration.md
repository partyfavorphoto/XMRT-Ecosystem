# Enhanced Autonomous Communication Integration


# Add to main.py imports
from enhanced_coordination_api import enhanced_coordination_bp, orchestrator, start_autonomous_scheduler
import threading

# Add to main.py after app initialization
app.register_blueprint(enhanced_coordination_bp)

# Start autonomous communication scheduler in background thread
def start_background_scheduler():
    """Start autonomous scheduler in background thread"""
    try:
        start_autonomous_scheduler()
    except Exception as e:
        logger.error(f"Autonomous scheduler error: {e}")

# Start scheduler thread
scheduler_thread = threading.Thread(target=start_background_scheduler, daemon=True)
scheduler_thread.start()

logger.info("🤖 Enhanced autonomous communication system integrated")

# Enhanced chat endpoint with autonomous communication
@app.route('/api/chat/enhanced_autonomous', methods=['POST'])
def enhanced_autonomous_chat():
    """Enhanced chat with autonomous inter-agent communication"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        # Log user message
        logger.info(f"Enhanced autonomous chat: {user_message}")
        
        # Trigger autonomous communication based on user message
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        autonomous_responses = loop.run_until_complete(
            orchestrator.initiate_autonomous_communication(user_message)
        )
        loop.close()
        
        # Format response
        response_data = {
            'user_message': user_message,
            'autonomous_responses': autonomous_responses,
            'agents_participated': len(autonomous_responses),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Enhanced autonomous chat error: {e}")
        return jsonify({'error': str(e)}), 500
