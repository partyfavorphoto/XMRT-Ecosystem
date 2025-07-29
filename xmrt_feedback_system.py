# XMRT Feedback System - Phase 3: Learning Loop
# Feeds conversation insights back to autonomous system

import requests
import json
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict, Counter

class XMRTFeedbackSystem:
    """Learns from conversations and influences autonomous priorities"""
    
    def __init__(self):
        self.knowledge_api = "https://xmrt-io.onrender.com"
        self.conversation_insights = []
        self.user_interests = defaultdict(int)
        self.priority_adjustments = {}
        self.learning_patterns = {
            "frequent_topics": Counter(),
            "user_pain_points": [],
            "requested_features": [],
            "knowledge_gaps": []
        }
    
    def record_conversation(self, user_query: str, eliza_response: str, 
                          knowledge_sources: List[Dict], user_satisfaction: float = None):
        """Record a conversation for learning analysis"""
        
        conversation_record = {
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "eliza_response": eliza_response,
            "knowledge_sources_used": len(knowledge_sources),
            "categories_accessed": [src.get('category') for src in knowledge_sources],
            "user_satisfaction": user_satisfaction,
            "query_type": self._classify_query_intent(user_query)
        }
        
        self.conversation_insights.append(conversation_record)
        self._analyze_conversation_patterns(conversation_record)
        
        # Keep only recent conversations (last 1000)
        if len(self.conversation_insights) > 1000:
            self.conversation_insights = self.conversation_insights[-1000:]
    
    def _classify_query_intent(self, query: str) -> str:
        """Classify what the user is really asking about"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["how", "tutorial", "guide", "learn"]):
            return "learning_request"
        elif any(word in query_lower for word in ["status", "progress", "update", "latest"]):
            return "status_inquiry"
        elif any(word in query_lower for word in ["problem", "issue", "error", "bug", "fix"]):
            return "problem_solving"
        elif any(word in query_lower for word in ["plan", "future", "roadmap", "next"]):
            return "planning_request"
        elif any(word in query_lower for word in ["why", "explain", "understand", "clarify"]):
            return "explanation_request"
        else:
            return "general_inquiry"
    
    def _analyze_conversation_patterns(self, conversation: Dict):
        """Analyze conversation to extract learning patterns"""
        
        query = conversation["user_query"].lower()
        query_type = conversation["query_type"]
        categories = conversation["categories_accessed"]
        
        # Track frequent topics
        words = [word for word in query.split() if len(word) > 3]
        for word in words:
            self.learning_patterns["frequent_topics"][word] += 1
        
        # Identify knowledge gaps (queries with few knowledge sources)
        if conversation["knowledge_sources_used"] < 2:
            self.learning_patterns["knowledge_gaps"].append({
                "query": conversation["user_query"],
                "timestamp": conversation["timestamp"],
                "categories_tried": categories
            })
        
        # Track user pain points (problem-solving queries)
        if query_type == "problem_solving":
            self.learning_patterns["user_pain_points"].append({
                "issue": conversation["user_query"],
                "timestamp": conversation["timestamp"]
            })
        
        # Track feature requests (planning queries)
        if query_type == "planning_request":
            self.learning_patterns["requested_features"].append({
                "request": conversation["user_query"],
                "timestamp": conversation["timestamp"]
            })
    
    def generate_priority_adjustments(self) -> Dict[str, Any]:
        """Generate priority adjustments for the autonomous system"""
        
        adjustments = {
            "timestamp": datetime.now().isoformat(),
            "conversation_count": len(self.conversation_insights),
            "priority_changes": {},
            "focus_areas": [],
            "new_tasks": []
        }
        
        # Analyze frequent topics to adjust priorities
        top_topics = self.learning_patterns["frequent_topics"].most_common(5)
        
        for topic, frequency in top_topics:
            if frequency > 5:  # Topic mentioned more than 5 times
                category = self._map_topic_to_category(topic)
                if category:
                    adjustments["priority_changes"][category] = {
                        "action": "increase_priority",
                        "reason": f"High user interest in {topic} ({frequency} mentions)",
                        "weight_adjustment": min(frequency * 0.1, 0.5)
                    }
        
        # Address knowledge gaps
        if len(self.learning_patterns["knowledge_gaps"]) > 3:
            gap_categories = Counter()
            for gap in self.learning_patterns["knowledge_gaps"][-10:]:  # Recent gaps
                for cat in gap["categories_tried"]:
                    if cat:
                        gap_categories[cat] += 1
            
            for category, gap_count in gap_categories.most_common(3):
                adjustments["focus_areas"].append({
                    "category": category,
                    "action": "expand_knowledge_base",
                    "reason": f"Knowledge gaps detected ({gap_count} instances)",
                    "priority": "high" if gap_count > 2 else "medium"
                })
        
        # Convert user pain points to tasks
        recent_pain_points = self.learning_patterns["user_pain_points"][-5:]
        for pain_point in recent_pain_points:
            adjustments["new_tasks"].append({
                "task": f"Investigate and address: {pain_point['issue']}",
                "category": "development",
                "priority": "high",
                "source": "user_feedback"
            })
        
        # Convert feature requests to tasks
        recent_requests = self.learning_patterns["requested_features"][-3:]
        for request in recent_requests:
            adjustments["new_tasks"].append({
                "task": f"Research feasibility: {request['request']}",
                "category": "development",
                "priority": "medium",
                "source": "user_request"
            })
        
        return adjustments
    
    def _map_topic_to_category(self, topic: str) -> str:
        """Map conversation topics to autonomous system categories"""
        
        topic_mappings = {
            "development": ["code", "programming", "api", "feature", "bug"],
            "analytics": ["data", "metrics", "performance", "stats", "analysis"],
            "marketing": ["users", "growth", "engagement", "community", "outreach"],
            "mining": ["mining", "pool", "hashrate", "rewards", "optimization"],
            "browser": ["interface", "frontend", "ui", "user", "experience"],
            "social_media": ["social", "twitter", "discord", "telegram", "community"]
        }
        
        for category, keywords in topic_mappings.items():
            if any(keyword in topic for keyword in keywords):
                return category
        
        return None
    
    def send_feedback_to_autonomous_system(self) -> bool:
        """Send priority adjustments to the autonomous system"""
        
        adjustments = self.generate_priority_adjustments()
        
        if not adjustments["priority_changes"] and not adjustments["new_tasks"]:
            return True  # Nothing to send
        
        try:
            # This would integrate with your xmrtnet system
            # For now, we'll create a feedback file that the autonomous system can read
            
            feedback_data = {
                "feedback_type": "conversation_learning",
                "generated_at": datetime.now().isoformat(),
                "adjustments": adjustments,
                "learning_summary": {
                    "total_conversations": len(self.conversation_insights),
                    "top_topics": dict(self.learning_patterns["frequent_topics"].most_common(10)),
                    "knowledge_gaps_count": len(self.learning_patterns["knowledge_gaps"]),
                    "pain_points_count": len(self.learning_patterns["user_pain_points"]),
                    "feature_requests_count": len(self.learning_patterns["requested_features"])
                }
            }
            
            print(f"📤 Generated feedback for autonomous system:")
            print(f"   🎯 Priority adjustments: {len(adjustments['priority_changes'])}")
            print(f"   📋 New focus areas: {len(adjustments['focus_areas'])}")
            print(f"   ⚡ New tasks: {len(adjustments['new_tasks'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send feedback: {e}")
            return False
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of what the system has learned from conversations"""
        
        return {
            "total_conversations": len(self.conversation_insights),
            "learning_patterns": {
                "frequent_topics": dict(self.learning_patterns["frequent_topics"].most_common(10)),
                "knowledge_gaps": len(self.learning_patterns["knowledge_gaps"]),
                "user_pain_points": len(self.learning_patterns["user_pain_points"]),
                "requested_features": len(self.learning_patterns["requested_features"])
            },
            "recent_adjustments": self.generate_priority_adjustments()
        }

# Initialize the feedback system
feedback_system = XMRTFeedbackSystem()

# Example integration with the knowledge router
def enhanced_conversation_with_feedback(user_query: str, eliza_response: str, 
                                      knowledge_sources: List[Dict]) -> Dict[str, Any]:
    """Enhanced conversation that includes feedback learning"""
    
    # Record the conversation for learning
    feedback_system.record_conversation(user_query, eliza_response, knowledge_sources)
    
    # Check if we should send feedback to autonomous system
    if len(feedback_system.conversation_insights) % 10 == 0:  # Every 10 conversations
        feedback_sent = feedback_system.send_feedback_to_autonomous_system()
        
        return {
            "conversation_recorded": True,
            "feedback_sent": feedback_sent,
            "learning_summary": feedback_system.get_learning_summary()
        }
    
    return {"conversation_recorded": True}

# Test the feedback system
def test_feedback_system():
    """Test the feedback system with sample conversations"""
    
    print("🧪 TESTING FEEDBACK SYSTEM")
    print("=" * 40)
    
    # Simulate some conversations
    sample_conversations = [
        ("How is the development progressing?", "Based on my analysis...", [{"category": "development"}]),
        ("What are the latest analytics?", "Current metrics show...", [{"category": "analytics"}]),
        ("I'm having trouble with the API", "Let me help you with that...", [{"category": "development"}]),
        ("Can we add a new feature for mining?", "That's an interesting request...", [{"category": "mining"}]),
        ("The interface is confusing", "I understand your concern...", [{"category": "browser"}])
    ]
    
    for query, response, sources in sample_conversations:
        feedback_system.record_conversation(query, response, sources)
    
    # Generate learning summary
    summary = feedback_system.get_learning_summary()
    
    print(f"✅ Recorded {summary['total_conversations']} conversations")
    print(f"✅ Top topics: {list(summary['learning_patterns']['frequent_topics'].keys())[:3]}")
    print(f"✅ Knowledge gaps: {summary['learning_patterns']['knowledge_gaps']}")
    print(f"✅ Pain points: {summary['learning_patterns']['user_pain_points']}")
    
    # Test feedback generation
    adjustments = feedback_system.generate_priority_adjustments()
    print(f"✅ Generated {len(adjustments['new_tasks'])} new tasks for autonomous system")
    
    return True

if __name__ == "__main__":
    test_feedback_system()
