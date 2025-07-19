from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models.agent import db, AIAgent, BoardroomSession, BoardroomMessage, AgendaItem, Vote
from src.services.typefully_service import TypefullyService
import json

typefully_bp = Blueprint('typefully', __name__)
typefully_service = TypefullyService()

@typefully_bp.route('/post-tweet', methods=['POST'])
def post_tweet():
    """Post a tweet using Typefully API"""
    data = request.get_json()
    
    content = data.get('content')
    schedule_time = data.get('schedule_time')  # Optional
    
    if not content:
        return jsonify({
            'success': False,
            'error': 'content is required'
        }), 400
    
    result = typefully_service.post_tweet(content, schedule_time)
    
    return jsonify(result)

@typefully_bp.route('/post-thread', methods=['POST'])
def post_thread():
    """Post a Twitter thread using Typefully API"""
    data = request.get_json()
    
    tweets = data.get('tweets')
    schedule_time = data.get('schedule_time')  # Optional
    
    if not tweets or not isinstance(tweets, list):
        return jsonify({
            'success': False,
            'error': 'tweets array is required'
        }), 400
    
    result = typefully_service.post_thread(tweets, schedule_time)
    
    return jsonify(result)

@typefully_bp.route('/announce-session', methods=['POST'])
def announce_session():
    """Announce a boardroom session on Twitter"""
    data = request.get_json()
    
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({
            'success': False,
            'error': 'session_id is required'
        }), 400
    
    session = BoardroomSession.query.get_or_404(session_id)
    
    result = typefully_service.post_boardroom_announcement(
        session.title,
        session.description or "AI agents gathering for transparent governance",
        session.x_space_url
    )
    
    if result['success']:
        # Create a message record
        message = BoardroomMessage(
            session_id=session_id,
            agent_id=1,  # Use main Eliza agent ID
            message_type='announcement',
            content=f"Session announcement posted: {session.title}",
            x_posted=True
        )
        db.session.add(message)
        db.session.commit()
    
    return jsonify(result)

@typefully_bp.route('/post-vote-results', methods=['POST'])
def post_vote_results():
    """Post vote results for an agenda item"""
    data = request.get_json()
    
    agenda_item_id = data.get('agenda_item_id')
    
    if not agenda_item_id:
        return jsonify({
            'success': False,
            'error': 'agenda_item_id is required'
        }), 400
    
    agenda_item = AgendaItem.query.get_or_404(agenda_item_id)
    
    # Get vote counts
    votes = Vote.query.filter_by(agenda_item_id=agenda_item_id).all()
    
    vote_counts = {
        'yes': sum(1 for vote in votes if vote.vote_value == 'yes'),
        'no': sum(1 for vote in votes if vote.vote_value == 'no'),
        'abstain': sum(1 for vote in votes if vote.vote_value == 'abstain')
    }
    
    result = typefully_service.post_vote_results(agenda_item.title, vote_counts)
    
    if result['success']:
        # Create a message record
        session = BoardroomSession.query.get(agenda_item.session_id)
        message = BoardroomMessage(
            session_id=agenda_item.session_id,
            agent_id=1,  # Use main Eliza agent ID
            message_type='announcement',
            content=f"Vote results posted for: {agenda_item.title}",
            x_posted=True
        )
        db.session.add(message)
        db.session.commit()
    
    return jsonify(result)

@typefully_bp.route('/post-agent-message', methods=['POST'])
def post_agent_message():
    """Post a message from an AI agent"""
    data = request.get_json()
    
    message_id = data.get('message_id')
    
    if not message_id:
        return jsonify({
            'success': False,
            'error': 'message_id is required'
        }), 400
    
    message = BoardroomMessage.query.get_or_404(message_id)
    agent = AIAgent.query.get_or_404(message.agent_id)
    session = BoardroomSession.query.get_or_404(message.session_id)
    
    result = typefully_service.post_agent_message(
        agent.name,
        message.content,
        session.title
    )
    
    if result['success']:
        # Mark message as posted
        message.x_posted = True
        db.session.commit()
    
    return jsonify(result)

@typefully_bp.route('/post-session-summary', methods=['POST'])
def post_session_summary():
    """Post a summary of a completed session"""
    data = request.get_json()
    
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({
            'success': False,
            'error': 'session_id is required'
        }), 400
    
    session = BoardroomSession.query.get_or_404(session_id)
    
    if session.status != 'completed':
        return jsonify({
            'success': False,
            'error': 'Session must be completed to post summary'
        }), 400
    
    # Calculate session metrics
    duration_minutes = 0
    if session.actual_start and session.actual_end:
        duration = session.actual_end - session.actual_start
        duration_minutes = int(duration.total_seconds() / 60)
    
    agenda_items_count = AgendaItem.query.filter_by(session_id=session_id).count()
    votes_cast = Vote.query.join(AgendaItem).filter(AgendaItem.session_id == session_id).count()
    
    result = typefully_service.post_session_summary(
        session.title,
        duration_minutes,
        agenda_items_count,
        votes_cast
    )
    
    if result['success']:
        # Create a message record
        message = BoardroomMessage(
            session_id=session_id,
            agent_id=1,  # Use main Eliza agent ID
            message_type='announcement',
            content=f"Session summary posted: {session.title}",
            x_posted=True
        )
        db.session.add(message)
        db.session.commit()
    
    return jsonify(result)

@typefully_bp.route('/schedule-reminder', methods=['POST'])
def schedule_reminder():
    """Schedule a reminder for an upcoming session"""
    data = request.get_json()
    
    session_id = data.get('session_id')
    reminder_minutes_before = data.get('reminder_minutes_before', 30)
    
    if not session_id:
        return jsonify({
            'success': False,
            'error': 'session_id is required'
        }), 400
    
    session = BoardroomSession.query.get_or_404(session_id)
    
    if not session.scheduled_start:
        return jsonify({
            'success': False,
            'error': 'Session must have a scheduled start time'
        }), 400
    
    # Calculate reminder time
    reminder_time = session.scheduled_start - timedelta(minutes=reminder_minutes_before)
    
    # Format times for display
    start_time_str = session.scheduled_start.strftime("%Y-%m-%d %H:%M UTC")
    schedule_time_str = reminder_time.isoformat()
    
    result = typefully_service.schedule_session_reminder(
        session.title,
        start_time_str,
        schedule_time_str
    )
    
    return jsonify(result)

@typefully_bp.route('/drafts', methods=['GET'])
def get_drafts():
    """Get list of Typefully drafts"""
    result = typefully_service.get_drafts()
    return jsonify(result)

@typefully_bp.route('/drafts/<draft_id>', methods=['DELETE'])
def delete_draft(draft_id):
    """Delete a Typefully draft"""
    result = typefully_service.delete_draft(draft_id)
    return jsonify(result)

@typefully_bp.route('/auto-post-session-updates', methods=['POST'])
def auto_post_session_updates():
    """Automatically post updates for active sessions"""
    data = request.get_json()
    
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({
            'success': False,
            'error': 'session_id is required'
        }), 400
    
    session = BoardroomSession.query.get_or_404(session_id)
    
    if session.status != 'active':
        return jsonify({
            'success': False,
            'error': 'Session must be active'
        }), 400
    
    results = []
    
    # Post session announcement if not already posted
    announcement_posted = BoardroomMessage.query.filter_by(
        session_id=session_id,
        message_type='announcement',
        x_posted=True
    ).first()
    
    if not announcement_posted:
        announcement_result = typefully_service.post_boardroom_announcement(
            session.title,
            session.description or "AI agents gathering for transparent governance",
            session.x_space_url
        )
        results.append({
            'type': 'announcement',
            'result': announcement_result
        })
        
        if announcement_result['success']:
            message = BoardroomMessage(
                session_id=session_id,
                agent_id=1,  # Use main Eliza agent ID
                message_type='announcement',
                content=f"Auto-posted session announcement: {session.title}",
                x_posted=True
            )
            db.session.add(message)
    
    # Post any unposted agent messages
    unposted_messages = BoardroomMessage.query.filter_by(
        session_id=session_id,
        x_posted=False
    ).limit(3).all()  # Limit to avoid spam
    
    for message in unposted_messages:
        agent = AIAgent.query.get(message.agent_id)
        if agent:
            post_result = typefully_service.post_agent_message(
                agent.name,
                message.content,
                session.title
            )
            results.append({
                'type': 'agent_message',
                'message_id': message.id,
                'result': post_result
            })
            
            if post_result['success']:
                message.x_posted = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'updates_posted': len(results),
        'results': results
    })

@typefully_bp.route('/test-connection', methods=['GET'])
def test_connection():
    """Test the Typefully API connection"""
    try:
        result = typefully_service.get_drafts()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Typefully API connection successful',
                'drafts_count': len(result.get('drafts', []))
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Typefully API connection failed',
                'error': result.get('error')
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Typefully API connection failed',
            'error': str(e)
        })

