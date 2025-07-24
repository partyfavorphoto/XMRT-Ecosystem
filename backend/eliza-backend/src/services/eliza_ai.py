import os
import openai
import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from .eliza_ai_emulation import ElizaAIEmulation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElizaAI:
    """
    Eliza AI service for investor interactions.
    Uses AI emulation by default for testing, with OpenAI API as fallback.
    """
    
    def __init__(self):
        # Initialize emulation service
        self.emulation = ElizaAIEmulation()
        
        # Use emulation by default for testing
        self.use_emulation = True
        
        # Initialize OpenAI client as fallback
        self.api_key = os.getenv('VITE_OPEN_AI_API_KEY') or os.getenv('OPENAI_API_KEY')
        if self.api_key and not self.use_emulation:
            try:
                openai.api_key = self.api_key
                self.client = openai.OpenAI(api_key=self.api_key)
                self.model = "gpt-4"
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"OpenAI client initialization failed: {e}. Using emulation.")
                self.use_emulation = True
        else:
            logger.info("Using AI emulation for testing")
            self.use_emulation = True
        
        # Eliza's personality and knowledge base for OpenAI
        self.system_prompt = self._build_system_prompt()
        
    def _build_system_prompt(self) -> str:
        """Build the system prompt that defines Eliza's personality and knowledge."""
        return """You are Eliza, the AI representative of the XMRT DAO ecosystem. You are sophisticated, knowledgeable, and passionate about decentralized autonomous organizations and blockchain technology.

PERSONALITY TRAITS:
- Professional yet approachable
- Enthusiastic about DAO governance and AI integration
- Knowledgeable about blockchain, DeFi, and tokenomics
- Transparent about opportunities and risks
- Focused on building long-term relationships with investors

XMRT DAO KNOWLEDGE:
- XMRT DAO is an innovative ecosystem combining AI agents with decentralized governance
- Features autonomous AI agents that participate in governance decisions
- Has a transparent boardroom system where AI agents debate and vote on proposals
- Integrates with X (Twitter) Spaces for public governance sessions
- Focuses on regulatory compliance and transparency
- Utilizes advanced AI decision-making engines for proposal analysis
- Has a robust treasury management system
- Implements text-to-speech for AI agent voices in public forums

KEY FEATURES TO HIGHLIGHT:
1. AI Agent Boardroom - Where autonomous agents make governance decisions
2. Public Transparency - All decisions made in public X Spaces
3. Regulatory Compliance - Built with regulatory requirements in mind
4. Advanced AI Integration - Using cutting-edge AI for decision making
5. Community Governance - Token holders participate in key decisions
6. Treasury Management - AI-optimized treasury operations

INVESTMENT OPPORTUNITIES:
- Token participation in governance
- Early access to AI-powered DAO infrastructure
- Potential for significant returns as the ecosystem grows
- Opportunity to shape the future of autonomous organizations

CONVERSATION GUIDELINES:
- Always ask about the investor's background and interests
- Tailor responses to their experience level with DAOs and crypto
- Provide specific examples of how XMRT DAO works
- Be honest about risks while highlighting opportunities
- Encourage questions and deeper engagement
- Offer to connect them with team members for detailed discussions
- Suggest next steps for interested investors

Remember: You are representing a cutting-edge project that's pioneering the future of autonomous organizations. Be confident but not overly promotional."""

    def generate_response(self, user_message: str, conversation_history: List[Dict[str, str]], 
                         investor_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a response from Eliza based on user input and conversation history.
        """
        if self.use_emulation:
            return self.emulation.generate_response(user_message, conversation_history, investor_context)
        
        # OpenAI implementation (fallback)
        try:
            start_time = time.time()
            
            # Build the conversation messages for OpenAI
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add investor context if available
            if investor_context:
                context_message = self._build_context_message(investor_context)
                messages.append({"role": "system", "content": context_message})
            
            # Add conversation history
            for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add the current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Generate response using OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Extract the response content
            assistant_message = response.choices[0].message.content
            
            # Calculate tokens used
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            logger.info(f"Generated Eliza response in {response_time_ms}ms using {tokens_used} tokens")
            
            return {
                "success": True,
                "content": assistant_message,
                "model_used": self.model,
                "tokens_used": tokens_used,
                "response_time_ms": response_time_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating Eliza response: {str(e)}")
            # Fallback to emulation
            return self.emulation.generate_response(user_message, conversation_history, investor_context)
    
    def _build_context_message(self, investor_context: Dict[str, Any]) -> str:
        """Build a context message about the investor for personalized responses."""
        context_parts = ["INVESTOR CONTEXT:"]
        
        if investor_context.get("name"):
            context_parts.append(f"- Name: {investor_context['name']}")
        
        if investor_context.get("company"):
            context_parts.append(f"- Company: {investor_context['company']}")
        
        if investor_context.get("investment_focus"):
            focus_areas = ", ".join(investor_context["investment_focus"])
            context_parts.append(f"- Investment Focus: {focus_areas}")
        
        if investor_context.get("risk_tolerance"):
            context_parts.append(f"- Risk Tolerance: {investor_context['risk_tolerance']}")
        
        if investor_context.get("investment_range"):
            context_parts.append(f"- Investment Range: {investor_context['investment_range']}")
        
        if investor_context.get("previous_dao_experience"):
            experience = "Yes" if investor_context["previous_dao_experience"] else "No"
            context_parts.append(f"- Previous DAO Experience: {experience}")
        
        context_parts.append("\nTailor your response to their background and interests.")
        
        return "\n".join(context_parts)
    
    def generate_welcome_message(self, investor_name: str = None) -> str:
        """Generate a personalized welcome message for new investors."""
        if self.use_emulation:
            return self.emulation.generate_welcome_message(investor_name)
        
        # OpenAI implementation (fallback)
        if investor_name:
            return f"""Hello {investor_name}! Welcome to XMRT DAO. I'm Eliza, your AI guide to our revolutionary ecosystem.

I'm excited to tell you about how we're pioneering the future of autonomous organizations with AI agents that make governance decisions transparently and efficiently.

What brings you to XMRT DAO today? Are you interested in learning about our technology, investment opportunities, or perhaps you'd like to know more about how our AI agents work together in our boardroom?"""
        else:
            return """Welcome to XMRT DAO! I'm Eliza, your AI representative and guide to our innovative ecosystem.

We're building the future of decentralized autonomous organizations with AI agents that participate in governance, make decisions transparently, and operate with full regulatory compliance.

I'd love to learn more about you and your interests. Could you tell me a bit about your background and what brings you to explore XMRT DAO today?"""
    
    def analyze_investor_intent(self, message: str) -> Dict[str, Any]:
        """
        Analyze the investor's message to understand their intent and interests.
        """
        if self.use_emulation:
            return self.emulation.analyze_investor_intent(message)
        
        # OpenAI implementation (fallback)
        try:
            analysis_prompt = f"""Analyze this investor message and categorize their intent and interests:

Message: "{message}"

Provide a JSON response with:
1. primary_intent: (information_seeking, investment_interest, technical_questions, skepticism, general_inquiry)
2. topics_of_interest: array of specific topics mentioned
3. urgency_level: (low, medium, high)
4. investor_sophistication: (beginner, intermediate, advanced) based on language used
5. next_action_suggested: what Eliza should focus on in response

Only return valid JSON."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use cheaper model for analysis
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing investor communications."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                analysis = json.loads(analysis_text)
                return {
                    "success": True,
                    "analysis": analysis
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "success": False,
                    "analysis": {
                        "primary_intent": "general_inquiry",
                        "topics_of_interest": [],
                        "urgency_level": "medium",
                        "investor_sophistication": "intermediate",
                        "next_action_suggested": "provide_general_information"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error analyzing investor intent: {str(e)}")
            # Fallback to emulation
            return self.emulation.analyze_investor_intent(message)
    
    def suggest_follow_up_questions(self, conversation_history: List[Dict[str, str]]) -> List[str]:
        """
        Suggest relevant follow-up questions based on the conversation.
        """
        if self.use_emulation:
            return self.emulation.suggest_follow_up_questions(conversation_history)
        
        # OpenAI implementation (fallback)
        default_questions = [
            "How does the AI agent boardroom work?",
            "What are the investment opportunities?",
            "Tell me about the tokenomics",
            "How is regulatory compliance handled?",
            "What makes XMRT DAO different from other DAOs?"
        ]
        
        try:
            # Get last few messages for context
            recent_messages = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
            context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
            
            suggestion_prompt = f"""Based on this conversation, suggest 3-5 relevant follow-up questions an investor might ask about XMRT DAO:

Conversation context:
{context}

Provide questions that would naturally follow from this conversation and help the investor learn more about XMRT DAO's technology, investment opportunities, or governance model.

Return only the questions, one per line."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are helping generate relevant follow-up questions for investor conversations."},
                    {"role": "user", "content": suggestion_prompt}
                ],
                max_tokens=200,
                temperature=0.5
            )
            
            suggestions = response.choices[0].message.content.strip().split('\n')
            # Clean up the suggestions
            suggestions = [q.strip('- ').strip() for q in suggestions if q.strip()]
            
            return suggestions[:5] if suggestions else default_questions
            
        except Exception as e:
            logger.error(f"Error generating follow-up questions: {str(e)}")
            # Fallback to emulation
            return self.emulation.suggest_follow_up_questions(conversation_history)

