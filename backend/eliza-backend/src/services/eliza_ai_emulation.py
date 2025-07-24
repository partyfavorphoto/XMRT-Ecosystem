import time
import random
import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class ElizaAIEmulation:
    """
    AI emulation service that mimics OpenAI API responses for testing purposes.
    Provides realistic responses about XMRT DAO without external API calls.
    """
    
    def __init__(self):
        self.knowledge_base = {
            "welcome": [
                "Hello {name}! Welcome to XMRT DAO. I'm Eliza, your AI guide to our revolutionary ecosystem where AI agents make governance decisions transparently and efficiently.",
                "Greetings {name}! I'm Eliza, representing XMRT DAO's innovative approach to autonomous organizations. How can I help you explore our AI-powered governance today?",
                "Welcome, {name}! I'm excited to share how XMRT DAO is pioneering the future of decentralized governance with AI agents. What brings you here today?"
            ],
            "general_info": [
                "XMRT DAO is a cutting-edge decentralized autonomous organization that combines AI agents with transparent governance. Our AI agents participate in decision-making through our boardroom system, conducting debates and votes in public X Spaces for full transparency.",
                "We're revolutionizing DAO governance by having autonomous AI agents make decisions transparently. Every governance session is held publicly on X Spaces, ensuring regulatory compliance and community oversight.",
                "XMRT DAO features an innovative AI agent boardroom where autonomous agents debate proposals, analyze data, and make governance decisions. This creates unprecedented transparency and efficiency in decentralized organizations."
            ],
            "investment": [
                "Investment in XMRT DAO offers early access to the future of autonomous organizations. Our token holders participate in governance alongside AI agents, creating a unique hybrid decision-making model with significant growth potential.",
                "We offer multiple investment opportunities: governance tokens for voting rights, early access to our AI infrastructure, and participation in our treasury management system. The combination of AI efficiency and human oversight creates compelling value propositions.",
                "Investing in XMRT DAO means joining a pioneering ecosystem where AI agents optimize treasury operations, conduct transparent governance, and create value through autonomous decision-making. Our regulatory-compliant approach ensures sustainable growth."
            ],
            "governance": [
                "Our governance model is unique: AI agents conduct debates in our boardroom, analyze proposals using advanced decision engines, and vote transparently. All sessions are broadcast on X Spaces for public oversight and regulatory compliance.",
                "XMRT DAO governance combines the efficiency of AI with human oversight. Our AI agents have individual Twitter handles, participate in public debates, and make decisions based on comprehensive data analysis while maintaining full transparency.",
                "The AI agent boardroom operates like a traditional board but with autonomous agents. They analyze proposals, debate merits, and vote on decisions. Every session is public, recorded, and compliant with regulatory requirements."
            ],
            "technology": [
                "Our technology stack includes autonomous AI agents with individual personalities, a sophisticated boardroom system for debates, integration with X Spaces for public transparency, and advanced decision engines for proposal analysis.",
                "We've developed text-to-speech capabilities for our AI agents, allowing them to participate in live X Spaces discussions. Our backend includes comprehensive conversation management, investor profiling, and real-time analytics.",
                "The technical architecture features AI agent management, automated social media integration through Typefully API, treasury optimization algorithms, and a complete investor interaction system with chat interfaces."
            ],
            "roadmap": [
                "Our roadmap includes expanding the AI agent boardroom, launching additional governance features, integrating with more social platforms, and developing advanced AI decision-making capabilities for complex proposals.",
                "Upcoming developments include enhanced AI agent personalities, automated proposal generation, cross-chain governance capabilities, and partnerships with other DAOs to create a network of autonomous organizations.",
                "We're building toward a future where AI agents can autonomously manage entire ecosystems while maintaining human oversight and regulatory compliance. This includes advanced treasury management and strategic decision-making."
            ],
            "risks": [
                "Like all innovative projects, XMRT DAO carries risks including regulatory changes, technology challenges, and market volatility. However, our focus on compliance and transparency helps mitigate these concerns.",
                "Key risks include the evolving regulatory landscape for DAOs, potential technical issues with AI decision-making, and market adoption challenges. We address these through careful development and regulatory engagement.",
                "Investment risks include token volatility, regulatory uncertainty, and the experimental nature of AI governance. Our transparent approach and public decision-making help investors make informed choices."
            ],
            "default": [
                "That's an interesting question about XMRT DAO. Could you provide more specific details about what aspect you'd like to explore?",
                "I'd be happy to help you understand more about XMRT DAO. What particular area interests you most - our AI agents, governance model, or investment opportunities?",
                "Let me help you learn more about XMRT DAO's innovative approach to autonomous organizations. What specific information would be most valuable to you?"
            ]
        }

        self.suggested_questions_pool = [
            "How does the AI agent boardroom actually work?",
            "What are the specific investment opportunities available?",
            "Tell me about the tokenomics and governance structure",
            "How do you ensure regulatory compliance?",
            "What makes XMRT DAO different from other DAOs?",
            "Can I see a live governance session?",
            "How do AI agents make decisions?",
            "What's the expected ROI for investors?",
            "How can I participate in governance?",
            "What are the main risks I should consider?",
            "Who are your key team members?",
            "What partnerships do you have?",
            "How is the treasury managed?",
            "What's your competitive advantage?",
            "Can you explain the technology stack?"
        ]

        self.intent_keywords = {
            "investment_interest": ["invest", "buy", "token", "fund", "money", "roi", "return", "profit", "purchase"],
            "governance_inquiry": ["govern", "vote", "decision", "proposal", "boardroom", "agent", "democracy"],
            "technical_questions": ["technical", "technology", "blockchain", "smart contract", "api", "code", "development"],
            "partnership_interest": ["partner", "collaborate", "business", "deal", "alliance", "cooperation"],
            "risk_assessment": ["risk", "safe", "secure", "danger", "concern", "worry", "problem"],
            "general_inquiry": ["what", "how", "why", "tell me", "explain", "describe", "information"]
        }

    def _simulate_api_delay(self):
        """Simulate realistic API response time."""
        time.sleep(random.uniform(0.2, 0.8))

    def _analyze_message_intent(self, message: str) -> str:
        """Analyze message to determine intent category."""
        message_lower = message.lower()
        intent_scores = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        return "general_inquiry"

    def _select_response_category(self, message: str) -> str:
        """Select appropriate response category based on message content."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["welcome", "hello", "hi", "greet"]):
            return "welcome"
        elif any(word in message_lower for word in ["invest", "buy", "token", "fund", "money"]):
            return "investment"
        elif any(word in message_lower for word in ["govern", "vote", "decision", "boardroom", "agent"]):
            return "governance"
        elif any(word in message_lower for word in ["technical", "technology", "how it works", "architecture"]):
            return "technology"
        elif any(word in message_lower for word in ["roadmap", "future", "plan", "upcoming", "development"]):
            return "roadmap"
        elif any(word in message_lower for word in ["risk", "danger", "concern", "safe", "secure"]):
            return "risks"
        elif any(word in message_lower for word in ["what is", "about", "explain", "describe"]):
            return "general_info"
        else:
            return "default"

    def _personalize_response(self, response: str, investor_context: Optional[Dict] = None) -> str:
        """Personalize response based on investor context."""
        if investor_context:
            name = investor_context.get("name", "")
            company = investor_context.get("company", "")
            
            if name and "{name}" in response:
                response = response.replace("{name}", name)
            elif name:
                response = f"{name}, {response}"
            
            if company:
                response += f" Given your background at {company}, this could be particularly relevant to your investment strategy."
        
        return response

    def generate_welcome_message(self, name: str = None) -> str:
        """Generate a personalized welcome message."""
        self._simulate_api_delay()
        
        welcome_templates = self.knowledge_base["welcome"]
        selected_template = random.choice(welcome_templates)
        
        if name:
            return selected_template.format(name=name)
        else:
            return selected_template.format(name="investor")

    def generate_response(self, user_message: str, conversation_history: List[Dict], 
                         investor_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate Eliza's response using emulation."""
        start_time = time.time()
        self._simulate_api_delay()
        
        # Select response category
        category = self._select_response_category(user_message)
        
        # Get response from knowledge base
        responses = self.knowledge_base.get(category, self.knowledge_base["default"])
        base_response = random.choice(responses)
        
        # Personalize response
        final_response = self._personalize_response(base_response, investor_context)
        
        # Add contextual information based on conversation history
        if len(conversation_history) > 2:
            final_response += " Is there a specific aspect you'd like me to elaborate on?"
        
        end_time = time.time()
        response_time_ms = int((end_time - start_time) * 1000)
        
        return {
            "success": True,
            "content": final_response,
            "model_used": "ElizaEmulation-v1.0",
            "tokens_used": len(final_response.split()) * 1.3,  # Simulate token count
            "response_time_ms": response_time_ms,
            "timestamp": datetime.utcnow().isoformat()
        }

    def analyze_investor_intent(self, message: str) -> Dict[str, Any]:
        """Analyze investor intent using emulation."""
        intent = self._analyze_message_intent(message)
        confidence = random.uniform(0.7, 0.95)  # Simulate confidence score
        
        # Generate reasoning based on intent
        reasoning_map = {
            "investment_interest": "Message contains investment-related keywords and financial terms",
            "governance_inquiry": "Message asks about decision-making and governance processes",
            "technical_questions": "Message focuses on technical implementation and architecture",
            "partnership_interest": "Message indicates interest in business collaboration",
            "risk_assessment": "Message expresses concerns about risks and security",
            "general_inquiry": "Message seeks general information about XMRT DAO"
        }
        
        reasoning = reasoning_map.get(intent, "General information request")
        
        # Determine sophistication level
        sophistication_indicators = {
            "beginner": ["what is", "explain", "simple", "basic", "new to"],
            "intermediate": ["how does", "process", "mechanism", "structure"],
            "advanced": ["architecture", "tokenomics", "governance model", "technical", "implementation"]
        }
        
        message_lower = message.lower()
        sophistication = "intermediate"  # default
        
        for level, indicators in sophistication_indicators.items():
            if any(indicator in message_lower for indicator in indicators):
                sophistication = level
                break

        return {
            "success": True,
            "analysis": {
                "primary_intent": intent,
                "topics_of_interest": self._extract_topics(message),
                "urgency_level": "medium",
                "investor_sophistication": sophistication,
                "next_action_suggested": self._suggest_next_action(intent),
                "confidence": confidence,
                "reasoning": reasoning
            }
        }

    def _extract_topics(self, message: str) -> List[str]:
        """Extract topics of interest from message."""
        topics = []
        topic_keywords = {
            "AI agents": ["ai", "agent", "artificial intelligence"],
            "governance": ["govern", "vote", "decision", "boardroom"],
            "investment": ["invest", "token", "fund", "money", "roi"],
            "technology": ["technical", "blockchain", "smart contract"],
            "compliance": ["regulatory", "compliance", "legal"],
            "treasury": ["treasury", "fund management", "financial"]
        }
        
        message_lower = message.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)
        
        return topics

    def _suggest_next_action(self, intent: str) -> str:
        """Suggest next action based on intent."""
        action_map = {
            "investment_interest": "provide_investment_details",
            "governance_inquiry": "explain_governance_model",
            "technical_questions": "share_technical_documentation",
            "partnership_interest": "connect_with_business_development",
            "risk_assessment": "address_concerns_transparently",
            "general_inquiry": "provide_comprehensive_overview"
        }
        
        return action_map.get(intent, "provide_general_information")

    def suggest_follow_up_questions(self, conversation_history: List[Dict]) -> List[str]:
        """Suggest relevant follow-up questions."""
        # Analyze recent conversation to suggest relevant questions
        if not conversation_history:
            return random.sample(self.suggested_questions_pool, 4)
        
        # Get last few messages to understand context
        recent_topics = []
        for msg in conversation_history[-3:]:
            content = msg.get("content", "").lower()
            if "invest" in content:
                recent_topics.append("investment")
            elif "govern" in content:
                recent_topics.append("governance")
            elif "technical" in content or "technology" in content:
                recent_topics.append("technology")
        
        # Filter questions based on recent topics
        relevant_questions = []
        if "investment" in recent_topics:
            relevant_questions.extend([
                "What's the expected ROI for investors?",
                "How can I participate in the token sale?",
                "What are the main investment risks?"
            ])
        
        if "governance" in recent_topics:
            relevant_questions.extend([
                "Can I watch a live AI agent debate?",
                "How do I submit a governance proposal?",
                "What voting rights do token holders have?"
            ])
        
        if "technology" in recent_topics:
            relevant_questions.extend([
                "What's the technical architecture?",
                "How do AI agents make decisions?",
                "Is the code open source?"
            ])
        
        # Fill remaining slots with general questions
        if len(relevant_questions) < 4:
            remaining = [q for q in self.suggested_questions_pool if q not in relevant_questions]
            relevant_questions.extend(random.sample(remaining, 4 - len(relevant_questions)))
        
        return relevant_questions[:4]

