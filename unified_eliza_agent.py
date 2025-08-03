#!/usr/bin/env python3
"""
Redesigned Unified Eliza Agent
Completely new frontend design with modern chat interface and reliable input system.
"""

import asyncio
import logging
import json
import numpy as np
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import openai
import aiohttp
from github import Github

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DecisionLevel(Enum):
    """Decision levels for autonomous operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DecisionCriteria:
    """Decision criteria for MCDA analysis."""
    name: str
    weight: float
    description: str
    measurement_type: str  # 'benefit' or 'cost'

class ConfidenceManager:
    """Dynamic confidence adjustment based on historical performance."""
    
    def __init__(self):
        self.confidence_thresholds = {
            DecisionLevel.LOW: 0.6,
            DecisionLevel.MEDIUM: 0.75,
            DecisionLevel.HIGH: 0.85,
            DecisionLevel.CRITICAL: 0.95
        }
        self.performance_history = []
        self.adjustment_factor = 0.01
        
    def get_threshold(self, decision_level: DecisionLevel) -> float:
        """Get current threshold for decision level."""
        return self.confidence_thresholds[decision_level]

class DecisionEvaluator:
    """Multi-criteria decision analysis for governance decisions."""
    
    def __init__(self):
        self.mcda_criteria = [
            DecisionCriteria("financial_impact", 0.3, "Financial impact on DAO treasury", "benefit"),
            DecisionCriteria("community_benefit", 0.25, "Benefit to community members", "benefit"),
            DecisionCriteria("technical_feasibility", 0.2, "Technical implementation feasibility", "benefit"),
            DecisionCriteria("risk_level", 0.15, "Associated risks and potential downsides", "cost"),
            DecisionCriteria("alignment_with_mission", 0.1, "Alignment with DAO mission and values", "benefit")
        ]
        
    async def evaluate_proposal(self, proposal: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate proposal using MCDA."""
        scores = {}
        
        for criteria in self.mcda_criteria:
            if criteria.name == "financial_impact":
                score = await self._assess_financial_impact(proposal)
            elif criteria.name == "community_benefit":
                score = await self._assess_community_benefit(proposal)
            elif criteria.name == "technical_feasibility":
                score = await self._assess_technical_feasibility(proposal)
            elif criteria.name == "risk_level":
                score = await self._assess_risk_level(proposal)
            elif criteria.name == "alignment_with_mission":
                score = await self._assess_mission_alignment(proposal)
            else:
                score = 0.5  # Default neutral score
            
            scores[criteria.name] = score
        
        # Calculate weighted score
        weighted_score = sum(
            scores[criteria.name] * criteria.weight 
            for criteria in self.mcda_criteria
        )
        scores['weighted_total'] = weighted_score
        
        return scores
    
    async def _assess_financial_impact(self, proposal: Dict[str, Any]) -> float:
        """Assess financial impact of proposal."""
        amount = proposal.get('amount', 0)
        treasury_balance = proposal.get('treasury_balance', 1000000)
        
        if amount == 0:
            return 0.5
        
        impact_ratio = amount / treasury_balance
        
        if impact_ratio < 0.01:
            return 0.9
        elif impact_ratio < 0.05:
            return 0.7
        elif impact_ratio < 0.1:
            return 0.5
        else:
            return 0.2
    
    async def _assess_community_benefit(self, proposal: Dict[str, Any]) -> float:
        """Assess community benefit of proposal."""
        category = proposal.get('category', 'general')
        
        benefit_scores = {
            'development': 0.9,
            'community': 0.8,
            'governance': 0.7,
            'treasury': 0.6,
            'marketing': 0.5,
            'general': 0.4
        }
        
        return benefit_scores.get(category, 0.5)
    
    async def _assess_technical_feasibility(self, proposal: Dict[str, Any]) -> float:
        """Assess technical feasibility of proposal."""
        complexity = proposal.get('complexity', 'medium')
        
        complexity_scores = {
            'low': 0.9,
            'medium': 0.7,
            'high': 0.4,
            'very_high': 0.2
        }
        
        return complexity_scores.get(complexity, 0.5)
    
    async def _assess_risk_level(self, proposal: Dict[str, Any]) -> float:
        """Assess risk level of proposal."""
        risk_factors = proposal.get('risk_factors', [])
        
        if not risk_factors:
            return 0.8  # Low risk
        
        risk_score = max(0.1, 1.0 - (len(risk_factors) * 0.2))
        return risk_score
    
    async def _assess_mission_alignment(self, proposal: Dict[str, Any]) -> float:
        """Assess alignment with DAO mission."""
        category = proposal.get('category', 'general')
        
        alignment_scores = {
            'governance': 0.9,
            'development': 0.8,
            'community': 0.8,
            'treasury': 0.7,
            'marketing': 0.6,
            'general': 0.5
        }
        
        return alignment_scores.get(category, 0.5)

class UnifiedElizaAgent:
    """Unified Eliza Agent with advanced capabilities."""
    
    def __init__(self):
        self.confidence_manager = ConfidenceManager()
        self.decision_evaluator = DecisionEvaluator()
        
        # System components
        self.components = {}
        self.status_history = []
        self.is_running = True
        
        # Initialize OpenAI
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Initialize GitHub integration
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            self.github = Github(github_token)
        else:
            self.github = None
if __name__ == "__main__":
                logger.warning("GitHub token not provided, GitHub integration disabled")
    
    async def initialize(self):
        """Initialize the unified agent."""
if __name__ == "__main__":
            logger.info("Initializing Unified Eliza Agent...")
        
        # Initialize core components
        self.components['decision_making'] = {'status': 'active', 'last_update': datetime.now()}
        self.components['learning'] = {'status': 'active', 'last_update': datetime.now()}
        self.components['explanation'] = {'status': 'active', 'last_update': datetime.now()}
        self.components['github_integration'] = {'status': 'active' if self.github else 'disabled', 'last_update': datetime.now()}
        
if __name__ == "__main__":
            logger.info("Unified Eliza Agent initialized successfully")
    
    async def process_governance_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Process a governance proposal with full analysis."""
if __name__ == "__main__":
            logger.info(f"Processing governance proposal: {proposal.get('id', 'unknown')}")
        
        try:
            # Perform MCDA analysis
            mcda_scores = await self.decision_evaluator.evaluate_proposal(proposal)
            
            # Calculate confidence
            confidence = await self._calculate_confidence(proposal, mcda_scores)
            
            # Make decision
            decision = await self._make_decision(proposal, mcda_scores, confidence)
            
            # Record for learning
            decision_id = f"decision_{int(datetime.now().timestamp())}"
            
            result = {
                'decision_id': decision_id,
                'timestamp': datetime.now().isoformat(),
                'proposal_id': proposal.get('id'),
                'mcda_scores': mcda_scores,
                'confidence': confidence,
                'decision': decision,
                'autonomous_action': confidence >= self.confidence_manager.get_threshold(DecisionLevel.MEDIUM)
            }
            
            return result
            
        except Exception as e:
if __name__ == "__main__":
                logger.error(f"Error processing governance proposal: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'proposal_id': proposal.get('id')
            }
    
    async def _calculate_confidence(self, proposal: Dict[str, Any], mcda_scores: Dict[str, float]) -> float:
        """Calculate decision confidence."""
        # Base confidence from MCDA weighted score
        base_confidence = mcda_scores.get('weighted_total', 0.5)
        
        # Adjust based on data quality
        data_quality = self._assess_data_quality(proposal)
        
        # Calculate final confidence
        confidence = (base_confidence * 0.8 + data_quality * 0.2)
        
        return min(1.0, max(0.0, confidence))
    
    def _assess_data_quality(self, proposal: Dict[str, Any]) -> float:
        """Assess quality of proposal data."""
        required_fields = ['id', 'description', 'amount', 'category']
        present_fields = sum(1 for field in required_fields if proposal.get(field))
        
        data_quality = present_fields / len(required_fields)
        
        # Bonus for additional detail
        if len(proposal.get('description', '')) > 100:
            data_quality += 0.1
        
        return min(1.0, data_quality)
    
    async def _make_decision(self, proposal: Dict[str, Any], mcda_scores: Dict[str, float], confidence: float) -> Dict[str, Any]:
        """Make decision based on analysis."""
        weighted_score = mcda_scores.get('weighted_total', 0)
        
        decision = {
            'action': 'approve' if weighted_score > 0.6 else 'reject',
            'confidence': confidence,
            'autonomous': confidence >= self.confidence_manager.get_threshold(DecisionLevel.MEDIUM),
            'score': weighted_score,
            'recommendation': '',
            'next_steps': []
        }
        
        # Generate recommendation
        if decision['autonomous']:
            if decision['action'] == 'approve':
                decision['recommendation'] = 'Proposal meets criteria for autonomous approval'
                decision['next_steps'] = ['Execute proposal', 'Monitor outcomes', 'Update learning']
            else:
                decision['recommendation'] = 'Proposal does not meet criteria for approval'
                decision['next_steps'] = ['Reject proposal', 'Provide feedback', 'Suggest improvements']
        else:
            decision['recommendation'] = 'Human review recommended due to lower confidence'
            decision['next_steps'] = ['Queue for human review', 'Provide analysis summary', 'Await manual decision']
        
        return decision
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'timestamp': datetime.now().isoformat(),
            'agent_version': '2.0.0',
            'status': 'operational',
            'components': self.components,
            'confidence_thresholds': {level.value: threshold for level, threshold in self.confidence_manager.confidence_thresholds.items()}
        }
    
    async def chat_response(self, user_message: str, context: str = "") -> str:
        """Generate chat response for user interaction."""
        try:
            user_message_lower = user_message.lower()
            
            if "governance" in user_message_lower:
                return "I can help you with XMRT DAO governance processes. I analyze proposals using Multi-Criteria Decision Analysis and provide transparent explanations for all decisions. Would you like me to analyze a specific proposal?"
            elif "status" in user_message_lower:
                status = await self.get_system_status()
                return f"System Status: {status['status']}. All components operational. Agent version: {status['agent_version']}. How can I assist you further?"
            elif "capabilities" in user_message_lower or "what can you do" in user_message_lower:
                return "I am Eliza, the XMRT DAO autonomous orchestrator. My capabilities include: governance proposal analysis using MCDA, autonomous decision-making with explainable AI, continuous learning, system coordination, treasury management assistance, and real-time status monitoring. What specific area would you like to explore?"
            elif any(greeting in user_message_lower for greeting in ["hello", "hi", "hey", "greetings"]):
                return "Hello! I'm Eliza, your XMRT DAO AI assistant. I'm here to help with governance, treasury management, and system operations. What would you like to know or discuss today?"
            elif "treasury" in user_message_lower:
                return "I can assist with treasury management including fund allocation analysis, risk assessment, and financial impact evaluation. What treasury-related question do you have?"
            elif "help" in user_message_lower:
                return "I'm here to help! You can ask me about: governance proposals and analysis, system status and monitoring, treasury management, my capabilities and features, or any XMRT DAO operations. What specific topic interests you?"
            elif "test" in user_message_lower:
                return "Test successful! I'm fully operational and ready to assist. All systems are functioning normally. Is there anything specific you'd like me to help you with?"
            else:
                return f"I understand you're asking about: '{user_message}'. I'm here to help with XMRT DAO operations including governance, treasury management, and system coordination. Could you provide more specific details about what you'd like to know or accomplish?"
                
        except Exception as e:
if __name__ == "__main__":
                logger.error(f"Error generating chat response: {e}")
            return "I apologize, but I encountered an error processing your request. Please try again, and if the issue persists, please check the system status."

# FastAPI application for deployment
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Redesigned Unified Eliza Agent", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
eliza_agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup."""
    global eliza_agent
    eliza_agent = UnifiedElizaAgent()
    await eliza_agent.initialize()

class ChatRequest(BaseModel):
    message: str
    context: str = ""

class ProposalRequest(BaseModel):
    id: str
    description: str
    amount: float = 0
    category: str = "general"
    complexity: str = "medium"
    risk_factors: List[str] = []
    treasury_balance: float = 1000000

# Completely redesigned frontend HTML with new input system
REDESIGNED_FRONTEND_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eliza AI v2.0 - XMRT DAO</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #00ff88;
            --primary-dark: #00cc6a;
            --bg-primary: #0a0a0a;
            --bg-secondary: #1a1a1a;
            --bg-tertiary: #2a2a2a;
            --text-primary: #ffffff;
            --text-secondary: #b0b0b0;
            --text-muted: #808080;
            --border: #333333;
            --shadow: rgba(0, 255, 136, 0.1);
            --error: #ff4444;
            --success: #00ff88;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .app-container {
            width: 100%;
            max-width: 800px;
            height: 90vh;
            background: var(--bg-secondary);
            border-radius: 20px;
            border: 1px solid var(--border);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), 0 0 0 1px var(--shadow);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .header {
            background: linear-gradient(90deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
            padding: 24px 32px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .avatar {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: 700;
            color: var(--bg-primary);
            box-shadow: 0 4px 12px var(--shadow);
        }

        .header-info h1 {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 4px;
        }

        .header-info p {
            font-size: 14px;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: var(--primary);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
        }

        .chat-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 32px;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }

        .message {
            display: flex;
            gap: 16px;
            max-width: 85%;
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            align-self: flex-end;
            flex-direction: row-reverse;
        }

        .message-avatar {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: 600;
            flex-shrink: 0;
        }

        .message.bot .message-avatar {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: var(--bg-primary);
        }

        .message.user .message-avatar {
            background: var(--bg-tertiary);
            color: var(--text-primary);
            border: 1px solid var(--border);
        }

        .message-content {
            background: var(--bg-tertiary);
            padding: 16px 20px;
            border-radius: 16px;
            font-size: 15px;
            line-height: 1.5;
            border: 1px solid var(--border);
        }

        .message.user .message-content {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: var(--bg-primary);
            border: none;
        }

        .message.bot .message-content {
            border-bottom-left-radius: 6px;
        }

        .message.user .message-content {
            border-bottom-right-radius: 6px;
        }

        .typing-indicator {
            display: none;
            align-items: center;
            gap: 16px;
            padding: 0 32px;
            margin-bottom: 16px;
        }

        .typing-indicator.show {
            display: flex;
        }

        .typing-dots {
            display: flex;
            gap: 4px;
            padding: 16px 20px;
            background: var(--bg-tertiary);
            border-radius: 16px;
            border-bottom-left-radius: 6px;
            border: 1px solid var(--border);
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            background: var(--text-muted);
            border-radius: 50%;
            animation: typing 1.4s infinite ease-in-out;
        }

        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }
        .typing-dot:nth-child(3) { animation-delay: 0s; }

        @keyframes typing {
            0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
            40% { transform: scale(1.2); opacity: 1; }
        }

        .input-area {
            padding: 24px 32px;
            border-top: 1px solid var(--border);
            background: var(--bg-secondary);
        }

        .input-container {
            display: flex;
            gap: 12px;
            align-items: flex-end;
            background: var(--bg-tertiary);
            border: 2px solid var(--border);
            border-radius: 16px;
            padding: 4px;
            transition: border-color 0.2s ease;
        }

        .input-container:focus-within {
            border-color: var(--primary);
            box-shadow: 0 0 0 4px var(--shadow);
        }

        .message-input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: var(--text-primary);
            font-size: 15px;
            font-family: inherit;
            padding: 16px 20px;
            resize: none;
            min-height: 24px;
            max-height: 120px;
            line-height: 1.5;
        }

        .message-input::placeholder {
            color: var(--text-muted);
        }

        .send-btn {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            border: none;
            border-radius: 12px;
            color: var(--bg-primary);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: 600;
            transition: all 0.2s ease;
            flex-shrink: 0;
        }

        .send-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px var(--shadow);
        }

        .send-btn:active {
            transform: translateY(0);
        }

        .send-btn:disabled {
            background: var(--border);
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .error-toast {
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--error);
            color: white;
            padding: 16px 24px;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 8px 24px rgba(255, 68, 68, 0.3);
            transform: translateX(400px);
            transition: transform 0.3s ease;
            z-index: 1000;
        }

        .error-toast.show {
            transform: translateX(0);
        }

        .welcome-message {
            text-align: center;
            padding: 40px 20px;
            color: var(--text-secondary);
        }

        .welcome-message h2 {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 12px;
            color: var(--text-primary);
        }

        .welcome-message p {
            font-size: 15px;
            line-height: 1.6;
        }

        @media (max-width: 768px) {
            .app-container {
                height: 100vh;
                border-radius: 0;
                border: none;
            }
            
            .header {
                padding: 20px 24px;
            }
            
            .messages-container {
                padding: 24px 20px;
            }
            
            .input-area {
                padding: 20px 24px;
            }
        }

        /* Custom scrollbar */
        .messages-container::-webkit-scrollbar {
            width: 6px;
        }

        .messages-container::-webkit-scrollbar-track {
            background: var(--bg-secondary);
        }

        .messages-container::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 3px;
        }

        .messages-container::-webkit-scrollbar-thumb:hover {
            background: var(--text-muted);
        }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="header">
            <div class="avatar">E</div>
            <div class="header-info">
                <h1>Eliza AI v2.0</h1>
                <p>
                    <span class="status-dot"></span>
                    XMRT DAO Autonomous Orchestrator
                </p>
            </div>
        </div>

        <div class="chat-area">
            <div class="messages-container" id="messagesContainer">
                <div class="welcome-message">
                    <h2>Welcome to Eliza AI v2.0</h2>
                    <p>I'm your XMRT DAO autonomous orchestrator. I can help with governance analysis, treasury management, system monitoring, and more. How can I assist you today?</p>
                </div>
            </div>

            <div class="typing-indicator" id="typingIndicator">
                <div class="message-avatar" style="background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); color: var(--bg-primary);">E</div>
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>

            <div class="input-area">
                <div class="input-container">
                    <textarea 
                        class="message-input" 
                        id="messageInput" 
                        placeholder="Type your message here..."
                        rows="1"
                    ></textarea>
                    <button class="send-btn" id="sendButton" type="button">
                        ↗
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div class="error-toast" id="errorToast"></div>

    <script>
        class ElizaChat {
            constructor() {
                this.messagesContainer = document.getElementById('messagesContainer');
                this.messageInput = document.getElementById('messageInput');
                this.sendButton = document.getElementById('sendButton');
                this.typingIndicator = document.getElementById('typingIndicator');
                this.errorToast = document.getElementById('errorToast');
                this.isProcessing = false;
                
                this.init();
            }

            init() {
                console.log('Initializing Eliza Chat v2.0...');
                
                // Event listeners
                this.sendButton.addEventListener('click', () => this.sendMessage());
                this.messageInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
                this.messageInput.addEventListener('input', () => this.autoResize());
                
                // Focus input
                this.messageInput.focus();
                
                // Test API connection
                this.testConnection();
                
                console.log('Eliza Chat v2.0 initialized successfully');
            }

            handleKeyDown(event) {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    this.sendMessage();
                } else if (event.key === 'Enter' && event.shiftKey) {
                    // Allow line break
                    return;
                }
            }

            autoResize() {
                const textarea = this.messageInput;
                textarea.style.height = 'auto';
                textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
            }

            async sendMessage() {
                if (this.isProcessing) return;
                
                const message = this.messageInput.value.trim();
                if (!message) return;
                
                console.log('Sending message:', message);
                
                // Set processing state
                this.isProcessing = true;
                this.sendButton.disabled = true;
                this.messageInput.disabled = true;
                
                // Add user message
                this.addMessage(message, 'user');
                
                // Clear input
                this.messageInput.value = '';
                this.autoResize();
                
                // Show typing indicator
                this.showTyping();
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            context: ''
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    console.log('API response:', data);
                    
                    // Hide typing indicator
                    this.hideTyping();
                    
                    // Add bot response
                    const botMessage = data.response || 'I apologize, but I encountered an issue processing your request.';
                    this.addMessage(botMessage, 'bot');
                    
                } catch (error) {
                    console.error('Error sending message:', error);
                    this.hideTyping();
                    this.showError(`Failed to send message: ${error.message}`);
                    
                    // Add error message to chat
                    this.addMessage('I apologize, but I\\'m having trouble connecting right now. Please try again in a moment.', 'bot');
                } finally {
                    // Reset state
                    this.isProcessing = false;
                    this.sendButton.disabled = false;
                    this.messageInput.disabled = false;
                    this.messageInput.focus();
                }
            }

            addMessage(text, sender) {
                // Remove welcome message if it exists
                const welcomeMessage = this.messagesContainer.querySelector('.welcome-message');
                if (welcomeMessage) {
                    welcomeMessage.remove();
                }
                
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}`;
                
                const avatar = document.createElement('div');
                avatar.className = 'message-avatar';
                avatar.textContent = sender === 'bot' ? 'E' : 'U';
                
                const content = document.createElement('div');
                content.className = 'message-content';
                content.textContent = text;
                
                messageDiv.appendChild(avatar);
                messageDiv.appendChild(content);
                
                this.messagesContainer.appendChild(messageDiv);
                this.scrollToBottom();
            }

            showTyping() {
                this.typingIndicator.classList.add('show');
                this.scrollToBottom();
            }

            hideTyping() {
                this.typingIndicator.classList.remove('show');
            }

            showError(message) {
                this.errorToast.textContent = message;
                this.errorToast.classList.add('show');
                
                setTimeout(() => {
                    this.errorToast.classList.remove('show');
                }, 5000);
            }

            scrollToBottom() {
                setTimeout(() => {
                    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
                }, 100);
            }

            async testConnection() {
                try {
                    const response = await fetch('/health');
                    if (response.ok) {
                        console.log('API connection successful');
                    } else {
                        console.warn('API health check failed');
                    }
                } catch (error) {
                    console.error('API connection test failed:', error);
                }
            }
        }

        // Initialize when DOM is loaded
        document.addEventListener('DOMContentLoaded', () => {
            new ElizaChat();
        });
    </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the redesigned frontend HTML."""
    return HTMLResponse(content=REDESIGNED_FRONTEND_HTML)

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint for user interaction."""
    if not eliza_agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    response = await eliza_agent.chat_response(request.message, request.context)
    return {"response": response}

@app.post("/api/governance/analyze")
async def analyze_proposal(request: ProposalRequest):
    """Analyze governance proposal."""
    if not eliza_agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    proposal_data = request.dict()
    result = await eliza_agent.process_governance_proposal(proposal_data)
    return result

@app.get("/api/status")
async def get_status():
    """Get system status."""
    if not eliza_agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    status = await eliza_agent.get_system_status()
    return status

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



@app.head(\"/\")
def root_head():
    return {}
