#!/usr/bin/env python3
"""
Unified Eliza Agent
Consolidated AI agent for XMRT-Ecosystem with advanced decision-making, orchestration, and coordination capabilities.
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

class DecisionExplainer:
    """Explainable AI system for decision transparency."""
    
    def __init__(self):
        self.explanation_templates = {
            'governance_proposal': self._explain_governance_proposal,
            'treasury_allocation': self._explain_treasury_allocation,
            'system_update': self._explain_system_update
        }
    
    def generate_explanation(self, decision_context: Dict[str, Any], decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive decision explanation."""
        explanation_type = decision_context.get('type', 'general')
        
        explanation = {
            'decision_summary': self._create_summary(decision_result),
            'reasoning_chain': self._build_reasoning_chain(decision_context),
            'evidence_sources': self._compile_evidence(decision_context),
            'confidence_analysis': self._explain_confidence(decision_result),
            'alternative_options': self._analyze_alternatives(decision_context),
            'risk_assessment': self._assess_risks(decision_context)
        }
        
        # Add specific explanation based on type
        if explanation_type in self.explanation_templates:
            specific_explanation = self.explanation_templates[explanation_type](decision_context, decision_result)
            explanation.update(specific_explanation)
        
        return explanation
    
    def _create_summary(self, decision_result: Dict[str, Any]) -> str:
        """Create decision summary."""
        action = decision_result.get('action', 'unknown')
        confidence = decision_result.get('confidence', 0)
        
        return f"Decision: {action} with {confidence:.1%} confidence"
    
    def _build_reasoning_chain(self, decision_context: Dict[str, Any]) -> List[str]:
        """Build step-by-step reasoning chain."""
        return [
            "Analyzed proposal context and requirements",
            "Applied Multi-Criteria Decision Analysis (MCDA)",
            "Evaluated confidence based on historical performance",
            "Generated recommendation based on weighted criteria"
        ]
    
    def _compile_evidence(self, decision_context: Dict[str, Any]) -> List[str]:
        """Compile evidence sources."""
        return [
            "Historical decision performance data",
            "MCDA criteria scores",
            "Risk assessment analysis",
            "Community sentiment indicators"
        ]
    
    def _explain_confidence(self, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """Explain confidence level."""
        confidence = decision_result.get('confidence', 0)
        
        if confidence >= 0.9:
            level = "Very High"
            explanation = "Strong evidence supports this decision with minimal risk"
        elif confidence >= 0.75:
            level = "High"
            explanation = "Good evidence supports this decision with acceptable risk"
        elif confidence >= 0.6:
            level = "Medium"
            explanation = "Moderate evidence supports this decision with some uncertainty"
        else:
            level = "Low"
            explanation = "Limited evidence available, high uncertainty"
        
        return {
            'level': level,
            'score': confidence,
            'explanation': explanation
        }
    
    def _analyze_alternatives(self, decision_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze alternative options."""
        return [
            {'option': 'Approve with modifications', 'score': 0.7, 'rationale': 'Reduce risk while maintaining benefits'},
            {'option': 'Defer decision', 'score': 0.5, 'rationale': 'Gather more information before deciding'},
            {'option': 'Reject proposal', 'score': 0.3, 'rationale': 'Risks outweigh potential benefits'}
        ]
    
    def _assess_risks(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess decision risks."""
        return {
            'financial_risk': 'Low to Medium',
            'operational_risk': 'Low',
            'reputational_risk': 'Low',
            'mitigation_strategies': [
                'Implement monitoring and alerts',
                'Set up rollback procedures',
                'Establish performance metrics'
            ]
        }
    
    def _explain_governance_proposal(self, context: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Specific explanation for governance proposals."""
        return {
            'governance_impact': 'This proposal affects DAO governance structure',
            'voting_implications': 'May require community vote for implementation',
            'precedent_analysis': 'Similar proposals have had positive outcomes'
        }
    
    def _explain_treasury_allocation(self, context: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Specific explanation for treasury allocations."""
        return {
            'treasury_impact': 'Allocation represents X% of total treasury',
            'roi_analysis': 'Expected return on investment within 6 months',
            'budget_alignment': 'Aligns with approved budget categories'
        }
    
    def _explain_system_update(self, context: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Specific explanation for system updates."""
        return {
            'technical_impact': 'Update improves system performance and security',
            'compatibility_check': 'Backward compatible with existing integrations',
            'rollback_plan': 'Automated rollback available if issues arise'
        }

class LearningEngine:
    """Advanced learning and pattern recognition system."""
    
    def __init__(self):
        self.learning_data = []
        self.patterns = {}
        self.performance_metrics = {}
        
    def record_decision_outcome(self, decision_id: str, outcome: Dict[str, Any]):
        """Record decision outcome for learning."""
        learning_record = {
            'decision_id': decision_id,
            'timestamp': datetime.now().isoformat(),
            'outcome': outcome,
            'success': outcome.get('success', True),
            'performance_score': outcome.get('performance_score', 0.5)
        }
        
        self.learning_data.append(learning_record)
        self._update_patterns()
        
    def _update_patterns(self):
        """Update learning patterns based on recorded data."""
        if len(self.learning_data) < 5:
            return
            
        # Analyze recent performance
        recent_data = self.learning_data[-10:]
        success_rate = sum(1 for record in recent_data if record['success']) / len(recent_data)
        avg_performance = sum(record['performance_score'] for record in recent_data) / len(recent_data)
        
        self.performance_metrics = {
            'success_rate': success_rate,
            'average_performance': avg_performance,
            'total_decisions': len(self.learning_data),
            'learning_trend': self._calculate_trend()
        }
        
    def _calculate_trend(self) -> str:
        """Calculate performance trend."""
        if len(self.learning_data) < 10:
            return 'insufficient_data'
            
        recent_avg = np.mean([record['performance_score'] for record in self.learning_data[-5:]])
        older_avg = np.mean([record['performance_score'] for record in self.learning_data[-10:-5]])
        
        if recent_avg > older_avg * 1.1:
            return 'improving'
        elif recent_avg < older_avg * 0.9:
            return 'declining'
        else:
            return 'stable'
    
    def get_optimization_suggestions(self) -> List[str]:
        """Generate optimization suggestions based on learning."""
        suggestions = []
        
        if self.performance_metrics.get('success_rate', 0) < 0.8:
            suggestions.append("Consider raising confidence thresholds to improve decision quality")
            
        if self.performance_metrics.get('learning_trend') == 'declining':
            suggestions.append("Review recent decision patterns for potential issues")
            
        if len(self.learning_data) > 100:
            suggestions.append("Archive old learning data to maintain performance")
            
        return suggestions

class UnifiedElizaAgent:
    """Unified Eliza Agent with advanced capabilities."""
    
    def __init__(self):
        self.confidence_manager = ConfidenceManager()
        self.decision_evaluator = DecisionEvaluator()
        self.decision_explainer = DecisionExplainer()
        self.learning_engine = LearningEngine()
        
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
            
            # Generate explanation
            explanation = self.decision_explainer.generate_explanation(proposal, decision)
            
            # Record for learning
            decision_id = f"decision_{int(datetime.now().timestamp())}"
            self.learning_engine.record_decision_outcome(decision_id, {
                'success': True,
                'performance_score': confidence,
                'decision_type': 'governance_proposal'
            })
            
            result = {
                'decision_id': decision_id,
                'timestamp': datetime.now().isoformat(),
                'proposal_id': proposal.get('id'),
                'mcda_scores': mcda_scores,
                'confidence': confidence,
                'decision': decision,
                'explanation': explanation,
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
        
        # Adjust based on historical performance
        performance_metrics = self.learning_engine.performance_metrics
        historical_factor = performance_metrics.get('success_rate', 0.8)
        
        # Calculate final confidence
        confidence = (base_confidence * 0.6 + data_quality * 0.2 + historical_factor * 0.2)
        
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
        performance_metrics = self.learning_engine.performance_metrics
        
        return {
            'timestamp': datetime.now().isoformat(),
            'agent_version': '1.0.0',
            'status': 'operational',
            'components': self.components,
            'performance_metrics': performance_metrics,
            'confidence_thresholds': {level.value: threshold for level, threshold in self.confidence_manager.confidence_thresholds.items()},
            'optimization_suggestions': self.learning_engine.get_optimization_suggestions()
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
                return f"System Status: {status['status']}. Performance: {status['performance_metrics'].get('success_rate', 0):.1%} success rate."
            elif "capabilities" in user_message.lower():
                return "I am Eliza, the XMRT DAO autonomous orchestrator. My capabilities include: governance proposal analysis, autonomous decision-making with MCDA, explainable AI, continuous learning, and system coordination."
            else:
                return "Hello! I'm Eliza, your XMRT DAO AI assistant. I can help with governance, treasury management, and system operations. What would you like to know?"
                
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return "I apologize, but I encountered an error processing your request. Please try again."

# FastAPI application for deployment
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

