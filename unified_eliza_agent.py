#!/usr/bin/env python3
"""
Enhanced Unified Eliza Agent
Consolidated AI agent for XMRT-Ecosystem with advanced decision-making, orchestration, and coordination capabilities.
Now includes proper frontend serving.
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
import redis
import sqlite3
from contextlib import asynccontextmanager

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

@dataclass
class ConfidenceMetrics:
    """Confidence metrics for decision making."""
    historical_accuracy: float
    data_quality: float
    consensus_level: float
    risk_assessment: float

@dataclass
class SystemStatus:
    """System status data structure."""
    component: str
    status: str
    last_update: datetime
    metrics: Dict[str, Any]

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
        
    def adjust_threshold(self, decision_level: DecisionLevel, success_rate: float):
        """Adjust confidence threshold based on success rate."""
        current_threshold = self.confidence_thresholds[decision_level]
        
        if success_rate > 0.9:
            # Lower threshold if performing well
            new_threshold = max(0.5, current_threshold - self.adjustment_factor)
        elif success_rate < 0.7:
            # Raise threshold if performing poorly
            new_threshold = min(0.95, current_threshold + self.adjustment_factor)
        else:
            new_threshold = current_threshold
            
        self.confidence_thresholds[decision_level] = new_threshold
        logger.info(f"Adjusted {decision_level.value} threshold to {new_threshold:.3f}")
        
    def get_threshold(self, decision_level: DecisionLevel) -> float:
        """Get current threshold for decision level."""
        return self.confidence_thresholds[decision_level]

class DecisionEvaluator:
    """Multi-criteria decision analysis for governance decisions."""
    
    def __init__(self):
        self.criteria_weights = {
            'financial_impact': 0.30,
            'security_risk': 0.25,
            'community_sentiment': 0.25,
            'regulatory_compliance': 0.20
        }
        self.mcda_criteria = self._initialize_mcda_criteria()
        
    def _initialize_mcda_criteria(self) -> List[DecisionCriteria]:
        """Initialize Multi-Criteria Decision Analysis criteria."""
        return [
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
        # Simplified assessment based on proposal category
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
            logger.warning("GitHub token not provided, GitHub integration disabled")
    
    async def initialize(self):
        """Initialize the unified agent."""
        logger.info("Initializing Unified Eliza Agent...")
        
        # Initialize core components
        self.components['decision_making'] = {'status': 'active', 'last_update': datetime.now()}
        self.components['learning'] = {'status': 'active', 'last_update': datetime.now()}
        self.components['explanation'] = {'status': 'active', 'last_update': datetime.now()}
        self.components['github_integration'] = {'status': 'active' if self.github else 'disabled', 'last_update': datetime.now()}
        
        logger.info("Unified Eliza Agent initialized successfully")
    
    async def process_governance_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Process a governance proposal with full analysis."""
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
            'agent_version': '1.0.0',
            'status': 'operational',
            'components': self.components,
            'confidence_thresholds': {level.value: threshold for level, threshold in self.confidence_manager.confidence_thresholds.items()}
        }
    
    async def chat_response(self, user_message: str, context: str = "") -> str:
        """Generate chat response for user interaction."""
        try:
            # Simple response generation for now
            # In a full implementation, this would use the knowledge router and advanced NLP
            
            if "governance" in user_message.lower():
                return "I can help you with XMRT DAO governance processes. I analyze proposals using Multi-Criteria Decision Analysis and provide transparent explanations for all decisions."
            elif "status" in user_message.lower():
                status = await self.get_system_status()
                return f"System Status: {status['status']}. All components operational."
            elif "capabilities" in user_message.lower():
                return "I am Eliza, the XMRT DAO autonomous orchestrator. My capabilities include: governance proposal analysis, autonomous decision-making with MCDA, explainable AI, continuous learning, and system coordination."
            elif "hello" in user_message.lower() or "hi" in user_message.lower():
                return "Hello! I'm Eliza, your XMRT DAO AI assistant. I can help with governance, treasury management, and system operations. What would you like to know?"
            else:
                return "I'm here to help with XMRT DAO operations. You can ask me about governance proposals, system status, treasury management, or my capabilities. How can I assist you today?"
                
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return "I apologize, but I encountered an error processing your request. Please try again."

# FastAPI application for deployment
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Unified Eliza Agent", version="1.0.0")

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

# Frontend HTML content
FRONTEND_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eliza AI - XMRT DAO</title>
    <style>
        :root {
            --primary-green: #00ff88;
            --dark-bg: #1a1a1a;
            --card-bg: #2d2d2d;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
        }

        * {
            box-sizing: border-box;
        }

        body {
            background-color: var(--dark-bg);
            color: var(--text-primary);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .chat-container {
            width: 100%;
            max-width: 600px;
            height: 80vh;
            background-color: var(--card-bg);
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            margin: 20px;
        }

        .chat-header {
            padding: 20px;
            border-bottom: 1px solid #444;
            text-align: center;
        }

        .chat-title {
            font-size: 24px;
            font-weight: bold;
            color: var(--primary-green);
            margin-bottom: 8px;
        }

        .chat-subtitle {
            font-size: 14px;
            color: var(--text-secondary);
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .message {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.4;
            word-wrap: break-word;
        }

        .message.bot {
            background-color: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
            align-self: flex-start;
            border-bottom-left-radius: 4px;
        }

        .message.user {
            background-color: var(--primary-green);
            color: #000;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }

        .chat-input-container {
            padding: 20px;
            border-top: 1px solid #444;
            display: flex;
            gap: 12px;
            align-items: center;
        }

        .chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #444;
            border-radius: 24px;
            background-color: var(--dark-bg);
            color: var(--text-primary);
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s ease;
        }

        .chat-input:focus {
            border-color: var(--primary-green);
        }

        .chat-input::placeholder {
            color: var(--text-secondary);
        }

        .send-button {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background-color: var(--primary-green);
            color: #000;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: bold;
            transition: all 0.2s ease;
        }

        .send-button:hover {
            background-color: #00e67a;
            transform: scale(1.05);
        }

        .send-button:disabled {
            background-color: #666;
            cursor: not-allowed;
            transform: none;
        }

        .typing-indicator {
            display: none;
            align-self: flex-start;
            padding: 12px 16px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            border-bottom-left-radius: 4px;
            max-width: 80px;
        }

        .typing-dots {
            display: flex;
            gap: 4px;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--text-secondary);
            animation: typing 1.4s infinite ease-in-out;
        }

        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }

        @keyframes typing {
            0%, 80%, 100% {
                transform: scale(0.8);
                opacity: 0.5;
            }
            40% {
                transform: scale(1);
                opacity: 1;
            }
        }

        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--primary-green);
            margin-right: 8px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .error-message {
            background-color: #ff4444;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            margin-top: 8px;
            display: none;
        }

        @media (max-width: 768px) {
            .chat-container {
                height: 100vh;
                margin: 0;
                border-radius: 0;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="chat-title">Eliza AI</div>
            <div class="chat-subtitle">
                <span class="status-indicator"></span>
                XMRT DAO Autonomous Orchestrator
            </div>
        </div>

        <div class="chat-messages" id="chatMessages">
            <div class="message bot">
                Hello. I am Eliza. All systems are operational. How can I assist you?
            </div>
        </div>

        <div class="typing-indicator" id="typingIndicator">
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>

        <div class="chat-input-container">
            <input 
                type="text" 
                class="chat-input" 
                id="chatInput" 
                placeholder="Ask Eliza about governance, treasury, or development..."
                maxlength="500"
            >
            <button class="send-button" id="sendButton" type="button">
                ➤
            </button>
        </div>
        
        <div class="error-message" id="errorMessage"></div>
    </div>

    <script>
        // Global variables
        let isProcessing = false;
        const chatMessages = document.getElementById('chatMessages');
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');
        const typingIndicator = document.getElementById('typingIndicator');
        const errorMessage = document.getElementById('errorMessage');

        // Initialize the chat
        function initializeChat() {
            console.log('Initializing Eliza chat interface...');
            
            // Add event listeners
            sendButton.addEventListener('click', sendMessage);
            chatInput.addEventListener('keypress', handleKeyPress);
            
            // Focus on input
            chatInput.focus();
            
            console.log('Chat interface initialized successfully');
        }

        // Handle key press events
        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }

        // Send message function
        async function sendMessage() {
            if (isProcessing) return;
            
            const messageText = chatInput.value.trim();
            if (messageText === '') return;
            
            console.log('Sending message:', messageText);
            
            // Disable input and show processing state
            isProcessing = true;
            sendButton.disabled = true;
            chatInput.disabled = true;
            hideError();
            
            // Add user message to chat
            addMessage(messageText, 'user');
            
            // Clear input
            chatInput.value = '';
            
            // Show typing indicator
            showTypingIndicator();
            
            try {
                // Send message to API
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        message: messageText,
                        context: ""
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('API response:', data);
                
                // Hide typing indicator
                hideTypingIndicator();
                
                // Add bot response to chat
                if (data.response) {
                    addMessage(data.response, 'bot');
                } else {
                    addMessage('I apologize, but I encountered an issue processing your request. Please try again.', 'bot');
                }
                
            } catch (error) {
                console.error('Error sending message:', error);
                hideTypingIndicator();
                showError('Failed to send message. Please check your connection and try again.');
                
                // Add error message to chat
                addMessage('I apologize, but I\\'m having trouble connecting right now. Please try again in a moment.', 'bot');
            } finally {
                // Re-enable input
                isProcessing = false;
                sendButton.disabled = false;
                chatInput.disabled = false;
                chatInput.focus();
            }
        }

        // Add message to chat
        function addMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            messageDiv.textContent = text;
            
            chatMessages.appendChild(messageDiv);
            
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        // Show typing indicator
        function showTypingIndicator() {
            typingIndicator.style.display = 'block';
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        // Hide typing indicator
        function hideTypingIndicator() {
            typingIndicator.style.display = 'none';
        }

        // Show error message
        function showError(message) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
            setTimeout(hideError, 5000); // Auto-hide after 5 seconds
        }

        // Hide error message
        function hideError() {
            errorMessage.style.display = 'none';
        }

        // Test API connection
        async function testApiConnection() {
            try {
                const response = await fetch('/health');
                if (response.ok) {
                    console.log('API connection successful');
                    return true;
                } else {
                    console.warn('API health check failed');
                    return false;
                }
            } catch (error) {
                console.error('API connection test failed:', error);
                return false;
            }
        }

        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {
            initializeChat();
            testApiConnection();
        });

        // Handle page visibility changes
        document.addEventListener('visibilitychange', function() {
            if (!document.hidden && !isProcessing) {
                chatInput.focus();
            }
        });
    </script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the frontend HTML."""
    return HTMLResponse(content=FRONTEND_HTML)

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
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

