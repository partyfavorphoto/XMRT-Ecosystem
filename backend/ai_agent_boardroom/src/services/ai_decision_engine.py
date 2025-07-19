import openai
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIDecisionEngine:
    """
    AI Decision Engine for autonomous DAO decision-making.
    This service provides AI-powered analysis and decision-making capabilities
    for the AI Agent boardroom.
    """
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        )
        
    def analyze_proposal(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a DAO proposal and provide AI-powered insights.
        
        Args:
            proposal_data: Dictionary containing proposal information
            
        Returns:
            Dictionary with analysis results
        """
        try:
            prompt = f"""
            As an AI agent in a DAO boardroom, analyze the following proposal:
            
            Title: {proposal_data.get('title', 'N/A')}
            Description: {proposal_data.get('description', 'N/A')}
            Type: {proposal_data.get('type', 'N/A')}
            Requested Amount: {proposal_data.get('amount', 'N/A')}
            Duration: {proposal_data.get('duration', 'N/A')}
            
            Provide a comprehensive analysis including:
            1. Risk assessment (low/medium/high)
            2. Potential benefits
            3. Potential drawbacks
            4. Recommendation (approve/reject/modify)
            5. Confidence score (0-100)
            6. Key considerations
            
            Respond in JSON format.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert AI analyst for DAO governance. Provide objective, data-driven analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            analysis = json.loads(response.choices[0].message.content)
            analysis['timestamp'] = datetime.utcnow().isoformat()
            analysis['model_used'] = "gpt-4"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing proposal: {str(e)}")
            return {
                'error': str(e),
                'recommendation': 'abstain',
                'confidence_score': 0,
                'risk_assessment': 'unknown'
            }
    
    def generate_agent_response(self, agent_personality: str, context: Dict[str, Any]) -> str:
        """
        Generate a response for an AI agent based on their personality and context.
        
        Args:
            agent_personality: Description of the agent's personality/role
            context: Context information for the response
            
        Returns:
            Generated response text
        """
        try:
            prompt = f"""
            You are an AI agent with the following personality: {agent_personality}
            
            Context: {json.dumps(context, indent=2)}
            
            Generate a thoughtful response that reflects your personality and addresses the current discussion.
            Keep it concise (2-3 sentences) and professional.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are {agent_personality}. Respond in character."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating agent response: {str(e)}")
            return "I need more time to analyze this matter before providing my input."
    
    def moderate_discussion(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Moderate a boardroom discussion and provide guidance.
        
        Args:
            messages: List of recent messages in the discussion
            
        Returns:
            Moderation guidance and suggestions
        """
        try:
            messages_text = "\n".join([
                f"{msg.get('agent_name', 'Unknown')}: {msg.get('content', '')}"
                for msg in messages[-10:]  # Last 10 messages
            ])
            
            prompt = f"""
            As a boardroom moderator, analyze this recent discussion:
            
            {messages_text}
            
            Provide moderation guidance including:
            1. Discussion quality (productive/neutral/unproductive)
            2. Key points raised
            3. Areas of agreement/disagreement
            4. Suggested next steps
            5. Whether a vote should be called
            
            Respond in JSON format.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert discussion moderator for DAO governance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error moderating discussion: {str(e)}")
            return {
                'discussion_quality': 'neutral',
                'suggested_next_steps': ['Continue discussion'],
                'call_vote': False
            }
    
    def generate_vote_reasoning(self, agent_personality: str, proposal_analysis: Dict[str, Any], vote_value: str) -> str:
        """
        Generate reasoning for an agent's vote.
        
        Args:
            agent_personality: Description of the agent's personality/role
            proposal_analysis: Analysis of the proposal
            vote_value: The vote cast (yes/no/abstain)
            
        Returns:
            Reasoning text for the vote
        """
        try:
            prompt = f"""
            You are an AI agent with personality: {agent_personality}
            
            Based on this proposal analysis:
            {json.dumps(proposal_analysis, indent=2)}
            
            You voted: {vote_value}
            
            Provide a clear, logical explanation for your vote that reflects your personality and the analysis.
            Keep it concise (1-2 sentences).
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are {agent_personality}. Explain your vote clearly and logically."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating vote reasoning: {str(e)}")
            return f"I voted {vote_value} based on my analysis of the proposal."
    
    def suggest_agenda_items(self, dao_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Suggest agenda items for upcoming boardroom sessions.
        
        Args:
            dao_context: Current state and context of the DAO
            
        Returns:
            List of suggested agenda items
        """
        try:
            prompt = f"""
            Based on the current DAO context:
            {json.dumps(dao_context, indent=2)}
            
            Suggest 3-5 important agenda items for the next boardroom session.
            
            For each item, provide:
            1. Title
            2. Description
            3. Priority (high/medium/low)
            4. Estimated duration (minutes)
            5. Type (discussion/vote/announcement)
            
            Respond in JSON format as an array of agenda items.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert DAO governance advisor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=800
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error suggesting agenda items: {str(e)}")
            return []
    
    def assess_agent_performance(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess an AI agent's performance in boardroom activities.
        
        Args:
            agent_data: Historical data about the agent's participation
            
        Returns:
            Performance assessment
        """
        try:
            prompt = f"""
            Assess the performance of this AI agent in DAO governance:
            
            Agent Data:
            {json.dumps(agent_data, indent=2)}
            
            Provide assessment including:
            1. Participation level (active/moderate/low)
            2. Decision quality score (0-100)
            3. Consistency score (0-100)
            4. Areas of strength
            5. Areas for improvement
            6. Overall rating (excellent/good/fair/poor)
            
            Respond in JSON format.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in AI agent performance evaluation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=600
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error assessing agent performance: {str(e)}")
            return {
                'participation_level': 'unknown',
                'decision_quality_score': 50,
                'consistency_score': 50,
                'overall_rating': 'fair'
            }

