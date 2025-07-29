# XMRT Knowledge Router - Phase 2 Integration
# Connects conversational Eliza to autonomous cycle insights

import requests
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

class XMRTKnowledgeRouter:
    """Routes queries to autonomous knowledge and enhances responses"""
    
    def __init__(self):
        self.knowledge_api = "https://xmrt-io.onrender.com"
        self.agent_specializations = {
            "technical": ["development", "browser"],
            "business": ["analytics", "marketing"], 
            "operations": ["mining", "social_media"],
            "general": ["analytics", "development", "marketing"]
        }
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def enhance_conversation(self, user_query: str, context: str = "") -> Dict[str, Any]:
        """Main method to enhance conversations with autonomous insights"""
        
        try:
            # Classify the query
            query_type = self._classify_query(user_query)
            
            # Get relevant insights
            insights = await self._fetch_relevant_insights(user_query, query_type)
            
            # Generate enhanced response
            enhanced_response = self._generate_enhanced_response(user_query, insights, context)
            
            return {
                "enhanced_response": enhanced_response,
                "knowledge_sources": insights,
                "agent_type": query_type,
                "confidence": self._calculate_confidence(insights),
                "autonomous_cycles_used": len(insights),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "enhanced_response": f"I'm processing your query, but my autonomous systems are currently updating. Let me help you directly: {user_query}",
                "error": str(e),
                "fallback_mode": True
            }
    
    def _classify_query(self, query: str) -> str:
        """Classify query to determine which agent specialization to use"""
        query_lower = query.lower()
        
        technical_keywords = ["code", "api", "development", "bug", "feature", "technical", "programming", "deploy"]
        business_keywords = ["analytics", "marketing", "growth", "users", "metrics", "revenue", "dao", "governance"]
        operations_keywords = ["mining", "social", "community", "operations", "performance", "optimization"]
        
        if any(keyword in query_lower for keyword in technical_keywords):
            return "technical"
        elif any(keyword in query_lower for keyword in business_keywords):
            return "business"
        elif any(keyword in query_lower for keyword in operations_keywords):
            return "operations"
        else:
            return "general"
    
    async def _fetch_relevant_insights(self, query: str, agent_type: str) -> List[Dict]:
        """Fetch relevant insights from the Knowledge Bridge"""
        
        # Check cache first
        cache_key = f"{query}_{agent_type}"
        if cache_key in self.cache:
            cache_data = self.cache[cache_key]
            if (datetime.now() - cache_data['timestamp']).seconds < self.cache_ttl:
                return cache_data['insights']
        
        insights = []
        
        # Get categories for this agent type
        categories = self.agent_specializations.get(agent_type, ["analytics", "development"])
        
        try:
            # Search for specific query terms first
            search_terms = self._extract_search_terms(query)
            
            for term in search_terms:
                search_response = requests.get(
                    f"{self.knowledge_api}/api/knowledge/search/{term}?limit=3",
                    timeout=15
                )
                
                if search_response.status_code == 200:
                    search_results = search_response.json()
                    insights.extend(search_results)
            
            # Get latest insights from relevant categories
            for category in categories:
                try:
                    category_response = requests.get(
                        f"{self.knowledge_api}/api/knowledge/latest/{category}?limit=2",
                        timeout=15
                    )
                    
                    if category_response.status_code == 200:
                        category_insights = category_response.json()
                        insights.extend(category_insights)
                        
                except requests.exceptions.RequestException:
                    continue  # Skip failed category requests
            
            # Cache the results
            self.cache[cache_key] = {
                'insights': insights[:8],  # Limit to top 8
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"Error fetching insights: {e}")
        
        return insights[:8]  # Return top 8 most relevant
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract meaningful search terms from query"""
        # Remove common words and extract key terms
        stop_words = {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'to', 'are', 'as', 'how', 'what', 'can', 'you'}
        words = [word.lower().strip('.,!?') for word in query.split()]
        meaningful_words = [word for word in words if len(word) > 3 and word not in stop_words]
        
        return meaningful_words[:3]  # Return top 3 search terms
    
    def _generate_enhanced_response(self, query: str, insights: List[Dict], context: str) -> str:
        """Generate enhanced response using autonomous insights"""
        
        if not insights:
            return f"I'm ready to help with your query about: {query}. Let me know what specific aspect you'd like to explore!"
        
        # Extract different types of information
        recent_progress = []
        metrics = []
        actions = []
        summaries = []
        
        for insight in insights:
            content = insight.get('content', '')
            cycle_num = insight.get('cycle', 0)
            
            if 'Progress:' in content:
                recent_progress.append(f"Cycle #{cycle_num}: {content}")
            elif 'Metric:' in content:
                metrics.append(f"Cycle #{cycle_num}: {content}")
            elif 'Action:' in content:
                actions.append(f"Cycle #{cycle_num}: {content}")
            elif 'Summary:' in content:
                summaries.append(f"Cycle #{cycle_num}: {content}")
        
        # Build contextual response
        response_parts = []
        
        # Add autonomous context
        response_parts.append(f"Based on my autonomous analysis across {len(insights)} recent cycles:")
        
        if recent_progress:
            response_parts.append(f"\n📈 Recent Progress: {recent_progress[0].split(': ', 1)[1][:150]}...")
        
        if metrics:
            response_parts.append(f"\n📊 Current Metrics: {metrics[0].split(': ', 1)[1][:150]}...")
        
        if actions:
            response_parts.append(f"\n🎯 Recommended Actions: {actions[0].split(': ', 1)[1][:150]}...")
        
        if summaries and not (recent_progress or metrics or actions):
            response_parts.append(f"\n💡 Key Insights: {summaries[0].split(': ', 1)[1][:150]}...")
        
        # Add direct response to user query
        response_parts.append(f"\n\nRegarding your specific question about '{query}', I can provide more detailed guidance based on these autonomous insights. What aspect would you like me to elaborate on?")
        
        return "".join(response_parts)
    
    def _calculate_confidence(self, insights: List[Dict]) -> float:
        """Calculate confidence score based on insight relevance"""
        if not insights:
            return 0.2  # Base confidence even without insights
        
        # Confidence based on number and recency of insights
        base_confidence = min(len(insights) * 0.1, 0.8)
        
        # Boost for recent cycles (700+)
        recent_cycles = [i for i in insights if i.get('cycle', 0) > 700]
        recency_boost = len(recent_cycles) * 0.05
        
        return min(base_confidence + recency_boost, 0.95)
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get current knowledge base statistics"""
        try:
            response = requests.get(f"{self.knowledge_api}/api/knowledge/stats", timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return {"error": "Knowledge stats unavailable"}

# Initialize the router
knowledge_router = XMRTKnowledgeRouter()

# Example usage function
async def enhance_eliza_response(user_message: str, conversation_context: str = "") -> str:
    """Main function to enhance Eliza responses with autonomous knowledge"""
    
    enhancement = await knowledge_router.enhance_conversation(user_message, conversation_context)
    
    if enhancement.get('fallback_mode'):
        return f"I understand you're asking about: {user_message}. How can I help you with this?"
    
    return enhancement.get('enhanced_response', user_message)

# Test function
def test_knowledge_integration():
    """Test the knowledge integration"""
    print("🧪 Testing XMRT Knowledge Integration...")
    
    # Test knowledge stats
    stats = knowledge_router.get_knowledge_stats()
    if 'total_cycles' in stats:
        print(f"✅ Connected to {stats['total_cycles']} autonomous cycles")
        print(f"✅ Categories: {list(stats.get('categories', {}).keys())}")
    else:
        print("⚠️ Knowledge API connection issue")
    
    return stats.get('total_cycles', 0) > 0

if __name__ == "__main__":
    # Test the integration
    success = test_knowledge_integration()
    if success:
        print("🎉 XMRT Knowledge Router ready for integration!")
    else:
        print("⚠️ Check knowledge API connection")
