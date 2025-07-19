from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False, unique=True)
    investor_name = db.Column(db.String(100))
    investor_email = db.Column(db.String(200))
    investor_company = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, completed, archived
    
    # Relationships
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'investor_name': self.investor_name,
            'investor_email': self.investor_email,
            'investor_company': self.investor_company,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'status': self.status,
            'message_count': len(self.messages)
        }

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user, assistant, system
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    model_used = db.Column(db.String(50))  # gpt-4, custom-gpt, etc.
    tokens_used = db.Column(db.Integer)
    response_time_ms = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'model_used': self.model_used,
            'tokens_used': self.tokens_used,
            'response_time_ms': self.response_time_ms
        }

class InvestorProfile(db.Model):
    __tablename__ = 'investor_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    name = db.Column(db.String(100))
    company = db.Column(db.String(200))
    investment_focus = db.Column(db.Text)  # JSON string of investment interests
    risk_tolerance = db.Column(db.String(20))  # conservative, moderate, aggressive
    investment_range = db.Column(db.String(50))  # e.g., "$100K-$1M"
    previous_dao_experience = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    conversations = db.relationship('Conversation', backref='investor_profile', lazy=True,
                                  foreign_keys='Conversation.investor_email',
                                  primaryjoin='InvestorProfile.email == Conversation.investor_email')
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'company': self.company,
            'investment_focus': json.loads(self.investment_focus) if self.investment_focus else [],
            'risk_tolerance': self.risk_tolerance,
            'investment_range': self.investment_range,
            'previous_dao_experience': self.previous_dao_experience,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'total_conversations': len(self.conversations)
        }

class ElizaKnowledgeBase(db.Model):
    __tablename__ = 'eliza_knowledge_base'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # dao_info, tokenomics, roadmap, team, etc.
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.Text)  # JSON array of tags
    priority = db.Column(db.Integer, default=1)  # 1=high, 2=medium, 3=low
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'title': self.title,
            'content': self.content,
            'tags': json.loads(self.tags) if self.tags else [],
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'active': self.active
        }

