from flask import Blueprint, request, jsonify, session
from datetime import datetime
import uuid
import json
from src.models.conversation import db, Conversation, Message, InvestorProfile
from src.services.eliza_ai import ElizaAI

eliza_bp = Blueprint('eliza', __name__)
eliza_ai = ElizaAI()

@eliza_bp.route('/start-conversation', methods=['POST'])
def start_conversation():
    """Start a new conversation with Eliza"""
    try:
        data = request.get_json() or {}
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create new conversation record
        conversation = Conversation(
            session_id=session_id,
            investor_name=data.get('name'),
            investor_email=data.get('email'),
            investor_company=data.get('company')
        )
        
        db.session.add(conversation)
        db.session.commit()
        
        # Generate welcome message
        welcome_message = eliza_ai.generate_welcome_message(data.get('name'))
        
        # Save welcome message
        welcome_msg = Message(
            conversation_id=conversation.id,
            role='assistant',
            content=welcome_message,
            model_used='system'
        )
        
        db.session.add(welcome_msg)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'conversation_id': conversation.id,
            'welcome_message': welcome_message,
            'suggested_questions': eliza_ai.suggest_follow_up_questions([])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@eliza_bp.route('/send-message', methods=['POST'])
def send_message():
    """Send a message to Eliza and get a response"""
    try:
        data = request.get_json()
        
        session_id = data.get('session_id')
        user_message = data.get('message')
        
        if not session_id or not user_message:
            return jsonify({
                'success': False,
                'error': 'session_id and message are required'
            }), 400
        
        # Find the conversation
        conversation = Conversation.query.filter_by(session_id=session_id).first()
        if not conversation:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        # Save user message
        user_msg = Message(
            conversation_id=conversation.id,
            role='user',
            content=user_message
        )
        db.session.add(user_msg)
        
        # Get conversation history
        messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.timestamp).all()
        conversation_history = [msg.to_dict() for msg in messages]
        
        # Get investor context if available
        investor_context = None
        if conversation.investor_email:
            profile = InvestorProfile.query.filter_by(email=conversation.investor_email).first()
            if profile:
                investor_context = profile.to_dict()
        
        # Analyze investor intent
        intent_analysis = eliza_ai.analyze_investor_intent(user_message)
        
        # Generate Eliza's response
        response_data = eliza_ai.generate_response(
            user_message, 
            conversation_history, 
            investor_context
        )
        
        if response_data['success']:
            # Save Eliza's response
            eliza_msg = Message(
                conversation_id=conversation.id,
                role='assistant',
                content=response_data['content'],
                model_used=response_data.get('model_used'),
                tokens_used=response_data.get('tokens_used'),
                response_time_ms=response_data.get('response_time_ms')
            )
            db.session.add(eliza_msg)
            
            # Update conversation last activity
            conversation.last_activity = datetime.utcnow()
            
            db.session.commit()
            
            # Generate follow-up questions
            updated_history = conversation_history + [
                {'role': 'user', 'content': user_message},
                {'role': 'assistant', 'content': response_data['content']}
            ]
            suggested_questions = eliza_ai.suggest_follow_up_questions(updated_history)
            
            return jsonify({
                'success': True,
                'response': response_data['content'],
                'suggested_questions': suggested_questions,
                'intent_analysis': intent_analysis.get('analysis', {}),
                'metadata': {
                    'model_used': response_data.get('model_used'),
                    'tokens_used': response_data.get('tokens_used'),
                    'response_time_ms': response_data.get('response_time_ms')
                }
            })
        else:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': response_data.get('error', 'Failed to generate response')
            }), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@eliza_bp.route('/conversation-history/<session_id>', methods=['GET'])
def get_conversation_history(session_id):
    """Get the full conversation history"""
    try:
        conversation = Conversation.query.filter_by(session_id=session_id).first()
        if not conversation:
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.timestamp).all()
        
        return jsonify({
            'success': True,
            'conversation': conversation.to_dict(),
            'messages': [msg.to_dict() for msg in messages]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@eliza_bp.route('/update-investor-profile', methods=['POST'])
def update_investor_profile():
    """Update or create investor profile"""
    try:
        data = request.get_json()
        
        email = data.get('email')
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        # Find or create investor profile
        profile = InvestorProfile.query.filter_by(email=email).first()
        if not profile:
            profile = InvestorProfile(email=email)
            db.session.add(profile)
        
        # Update profile fields
        if 'name' in data:
            profile.name = data['name']
        if 'company' in data:
            profile.company = data['company']
        if 'investment_focus' in data:
            profile.investment_focus = json.dumps(data['investment_focus'])
        if 'risk_tolerance' in data:
            profile.risk_tolerance = data['risk_tolerance']
        if 'investment_range' in data:
            profile.investment_range = data['investment_range']
        if 'previous_dao_experience' in data:
            profile.previous_dao_experience = data['previous_dao_experience']
        
        profile.last_updated = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'profile': profile.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@eliza_bp.route('/investor-profile/<email>', methods=['GET'])
def get_investor_profile(email):
    """Get investor profile by email"""
    try:
        profile = InvestorProfile.query.filter_by(email=email).first()
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
        
        return jsonify({
            'success': True,
            'profile': profile.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@eliza_bp.route('/conversations', methods=['GET'])
def get_conversations():
    """Get list of all conversations (for admin/analytics)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        conversations = Conversation.query.order_by(Conversation.last_activity.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'conversations': [conv.to_dict() for conv in conversations.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': conversations.total,
                'pages': conversations.pages,
                'has_next': conversations.has_next,
                'has_prev': conversations.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@eliza_bp.route('/analytics', methods=['GET'])
def get_analytics():
    """Get conversation analytics"""
    try:
        # Basic analytics
        total_conversations = Conversation.query.count()
        total_messages = Message.query.count()
        active_conversations = Conversation.query.filter_by(status='active').count()
        
        # Recent activity (last 7 days)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_conversations = Conversation.query.filter(Conversation.created_at >= week_ago).count()
        recent_messages = Message.query.filter(Message.timestamp >= week_ago).count()
        
        # Top investor companies
        from sqlalchemy import func
        top_companies = db.session.query(
            Conversation.investor_company,
            func.count(Conversation.id).label('conversation_count')
        ).filter(
            Conversation.investor_company.isnot(None)
        ).group_by(
            Conversation.investor_company
        ).order_by(
            func.count(Conversation.id).desc()
        ).limit(10).all()
        
        return jsonify({
            'success': True,
            'analytics': {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'active_conversations': active_conversations,
                'recent_conversations_7d': recent_conversations,
                'recent_messages_7d': recent_messages,
                'top_companies': [
                    {'company': company, 'conversations': count} 
                    for company, count in top_companies
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@eliza_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        
        # Test OpenAI API (optional - might want to skip to avoid costs)
        # eliza_ai.client.models.list()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'database': 'connected',
                'openai_api': 'configured'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

