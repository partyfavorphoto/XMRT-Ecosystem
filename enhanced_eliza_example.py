# XMRT-Ecosystem Integration Example
# How to integrate the Knowledge Router with your existing Eliza

from xmrt_knowledge_router import knowledge_router, enhance_eliza_response
import asyncio

class EnhancedEliza:
    """Enhanced Eliza with autonomous knowledge integration"""
    
    def __init__(self):
        self.knowledge_router = knowledge_router
        self.conversation_history = []
    
    async def process_message(self, user_message: str) -> str:
        """Process user message with autonomous knowledge enhancement"""
        
        # Build conversation context
        context = " ".join(self.conversation_history[-3:])  # Last 3 exchanges
        
        # Get enhanced response
        enhanced_response = await enhance_eliza_response(user_message, context)
        
        # Store in conversation history
        self.conversation_history.append(f"User: {user_message}")
        self.conversation_history.append(f"Eliza: {enhanced_response}")
        
        # Keep history manageable
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        return enhanced_response
    
    def get_system_status(self) -> dict:
        """Get status of the enhanced system"""
        stats = self.knowledge_router.get_knowledge_stats()
        return {
            "autonomous_cycles": stats.get('total_cycles', 0),
            "knowledge_categories": len(stats.get('categories', {})),
            "router_status": "operational" if stats.get('total_cycles', 0) > 0 else "limited",
            "conversation_history": len(self.conversation_history)
        }

# Example usage
async def demo_enhanced_eliza():
    """Demo the enhanced Eliza system"""
    
    eliza = EnhancedEliza()
    
    # Test queries
    test_queries = [
        "How is the development going?",
        "What are the latest analytics insights?",
        "Tell me about recent marketing progress",
        "What's the status of mining operations?"
    ]
    
    print("🤖 ENHANCED ELIZA DEMO")
    print("=" * 40)
    
    for query in test_queries:
        print(f"\n👤 User: {query}")
        response = await eliza.process_message(query)
        print(f"🤖 Enhanced Eliza: {response[:200]}...")
    
    # Show system status
    status = eliza.get_system_status()
    print(f"\n📊 System Status:")
    print(f"   Autonomous Cycles: {status['autonomous_cycles']}")
    print(f"   Knowledge Categories: {status['knowledge_categories']}")
    print(f"   Router Status: {status['router_status']}")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_enhanced_eliza())
