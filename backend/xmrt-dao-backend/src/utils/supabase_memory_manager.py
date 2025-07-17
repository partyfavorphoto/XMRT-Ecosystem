"""Supabase-integrated Memory Manager for Eliza."""

import os
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from supabase import create_client, Client
from openai import OpenAI

# Supabase configuration
SUPABASE_URL = "https://vlaikrbfunhhnihavxky.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZsYWlrcmJmdW5oaG5paGF2eGt5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjcxMjkyNSwiZXhwIjoyMDY4Mjg4OTI1fQ.7HmpHEle8dz7WQTlLdOi577MBkRhhVk3FuGu7vXFe70"


class SupabaseMemoryManager:
    """
    Supabase-integrated memory management system for Eliza's long-term memory.
    Handles storage, retrieval, and management of memories with vector embeddings.
    """
    
    def __init__(self, app=None):
        self.app = app
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        self.openai_client = None
        self.embedding_model = 'text-embedding-ada-002'
        self.similarity_threshold = 0.7
        self.max_memories_per_user = 10000
        self.memory_retention_days = 365
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the memory manager with Flask app"""
        self.app = app
        
        # Initialize OpenAI client if API key is available
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
        
        # Configuration from environment or defaults
        self.embedding_model = os.environ.get('EMBEDDING_MODEL', 'text-embedding-ada-002')
        self.similarity_threshold = float(os.environ.get('SIMILARITY_THRESHOLD', '0.7'))
        self.max_memories_per_user = int(os.environ.get('MAX_MEMORIES_PER_USER', '10000'))
        self.memory_retention_days = int(os.environ.get('MEMORY_RETENTION_DAYS', '365'))
    
    def store_memory(self, user_id: str, content: str, memory_type: str = 'general',
                    session_id: str = None, metadata: Dict[str, Any] = None, 
                    tags: List[str] = None, relevance_score: float = 1.0) -> Optional[Dict]:
        """
        Store a new memory with optional vector embedding.
        """
        try:
            # Generate embedding if OpenAI client is available
            embedding = None
            if self.openai_client:
                try:
                    embedding_response = self._generate_embedding(content)
                    if embedding_response:
                        embedding = embedding_response
                except Exception as e:
                    print(f"Warning: Failed to generate embedding: {e}")
            
            # Prepare memory data
            memory_data = {
                'user_id': user_id,
                'content': content,
                'memory_type': memory_type,
                'session_id': session_id,
                'metadata': json.dumps(metadata) if metadata else None,
                'embedding': embedding,
                'relevance_score': relevance_score,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'tags': ','.join(tags) if tags else None,
                'is_active': True
            }
            
            # Insert into Supabase
            result = self.supabase.table('eliza_memory').insert(memory_data).execute()
            
            if result.data:
                # Check if user has too many memories and prune if necessary
                self._check_and_prune_memories(user_id)
                return result.data[0]
            
            return None
            
        except Exception as e:
            print(f"Error storing memory: {e}")
            return None
    
    def retrieve_memories(self, user_id: str, query: str = None, memory_types: List[str] = None,
                         limit: int = 10, session_id: str = None, 
                         tags: List[str] = None) -> List[Dict]:
        """
        Retrieve memories based on various filters.
        """
        try:
            # Build query
            query_builder = self.supabase.table('eliza_memory').select('*').eq('user_id', user_id).eq('is_active', True)
            
            # Apply filters
            if memory_types:
                query_builder = query_builder.in_('memory_type', memory_types)
            
            if session_id:
                query_builder = query_builder.eq('session_id', session_id)
            
            if query:
                query_builder = query_builder.ilike('content', f'%{query}%')
            
            if tags:
                for tag in tags:
                    query_builder = query_builder.ilike('tags', f'%{tag}%')
            
            # Order by relevance and recency
            query_builder = query_builder.order('relevance_score', desc=True).order('created_at', desc=True).limit(limit)
            
            result = query_builder.execute()
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error retrieving memories: {e}")
            return []
    
    def search_memories_semantic(self, user_id: str, query_text: str, 
                               limit: int = 10, memory_types: List[str] = None) -> List[Tuple[Dict, float]]:
        """
        Search memories using semantic similarity with vector embeddings.
        """
        if not self.openai_client:
            # Fallback to text search if embeddings not available
            memories = self.retrieve_memories(user_id, query_text, memory_types, limit)
            return [(memory, 1.0) for memory in memories]
        
        try:
            # Generate embedding for query
            query_embedding = self._generate_embedding(query_text)
            if not query_embedding:
                return []
            
            # Use Supabase vector similarity search
            query_builder = self.supabase.table('eliza_memory').select('*').eq('user_id', user_id).eq('is_active', True)
            
            if memory_types:
                query_builder = query_builder.in_('memory_type', memory_types)
            
            # For now, get all memories and calculate similarity in Python
            # In production, you'd use Supabase's vector similarity functions
            result = query_builder.execute()
            memories = result.data if result.data else []
            
            # Calculate similarities
            similarities = []
            query_vector = np.array(query_embedding)
            
            for memory in memories:
                if memory.get('embedding'):
                    try:
                        memory_vector = np.array(memory['embedding'])
                        similarity = self._cosine_similarity(query_vector, memory_vector)
                        
                        if similarity >= self.similarity_threshold:
                            similarities.append((memory, similarity))
                    except Exception as e:
                        print(f"Error calculating similarity for memory {memory.get('id')}: {e}")
                        continue
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    def store_conversation(self, user_id: str, session_id: str, role: str, content: str,
                          message_type: str = None, autonomous_actions: List[Dict] = None,
                          context_data: Dict[str, Any] = None, memory_references: List[int] = None,
                          sentiment_score: float = None, importance_score: float = 0.5) -> Optional[Dict]:
        """
        Store a conversation entry in the history.
        """
        try:
            conversation_data = {
                'user_id': user_id,
                'session_id': session_id,
                'role': role,
                'content': content,
                'message_type': message_type,
                'autonomous_actions': json.dumps(autonomous_actions) if autonomous_actions else None,
                'context_data': json.dumps(context_data) if context_data else None,
                'memory_references': ','.join(map(str, memory_references)) if memory_references else None,
                'sentiment_score': sentiment_score,
                'importance_score': importance_score,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('conversation_history').insert(conversation_data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error storing conversation: {e}")
            return None
    
    def get_conversation_history(self, user_id: str, session_id: str = None, 
                               limit: int = 50) -> List[Dict]:
        """
        Get conversation history for a user.
        """
        try:
            query_builder = self.supabase.table('conversation_history').select('*').eq('user_id', user_id)
            
            if session_id:
                query_builder = query_builder.eq('session_id', session_id)
            
            query_builder = query_builder.order('timestamp', desc=True).limit(limit)
            
            result = query_builder.execute()
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    def create_memory_association(self, source_id: int, target_id: int, 
                                association_type: str, strength: float = 1.0) -> Optional[Dict]:
        """
        Create an association between two memories.
        """
        try:
            # Check if association already exists
            existing = self.supabase.table('memory_associations').select('*').eq('source_memory_id', source_id).eq('target_memory_id', target_id).eq('association_type', association_type).execute()
            
            if existing.data:
                # Update existing association strength
                updated = self.supabase.table('memory_associations').update({'strength': max(existing.data[0]['strength'], strength)}).eq('id', existing.data[0]['id']).execute()
                return updated.data[0] if updated.data else None
            
            # Create new association
            association_data = {
                'source_memory_id': source_id,
                'target_memory_id': target_id,
                'association_type': association_type,
                'strength': strength,
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('memory_associations').insert(association_data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error creating memory association: {e}")
            return None
    
    def get_memory_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get memory usage analytics for a user.
        """
        try:
            # Total memories
            total_result = self.supabase.table('eliza_memory').select('id', count='exact').eq('user_id', user_id).eq('is_active', True).execute()
            total_memories = total_result.count if total_result.count else 0
            
            # Recent activity (last 30 days)
            recent_cutoff = (datetime.utcnow() - timedelta(days=30)).isoformat()
            recent_result = self.supabase.table('eliza_memory').select('id', count='exact').eq('user_id', user_id).eq('is_active', True).gte('created_at', recent_cutoff).execute()
            recent_memories = recent_result.count if recent_result.count else 0
            
            # Conversation history count
            conv_result = self.supabase.table('conversation_history').select('id', count='exact').eq('user_id', user_id).execute()
            conversation_count = conv_result.count if conv_result.count else 0
            
            return {
                'total_memories': total_memories,
                'recent_memories_30d': recent_memories,
                'conversation_entries': conversation_count,
                'max_memories_limit': self.max_memories_per_user,
                'retention_days': self.memory_retention_days
            }
            
        except Exception as e:
            print(f"Error getting memory analytics: {e}")
            return {}
    
    def prune_old_memories(self, user_id: str, days_threshold: int = None) -> int:
        """
        Remove old or low-relevance memories for a user.
        """
        if days_threshold is None:
            days_threshold = self.memory_retention_days
        
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days_threshold)).isoformat()
            
            # Soft delete by setting is_active to False
            result = self.supabase.table('eliza_memory').update({'is_active': False}).eq('user_id', user_id).lt('created_at', cutoff_date).lt('relevance_score', 0.3).execute()
            
            return len(result.data) if result.data else 0
            
        except Exception as e:
            print(f"Error pruning memories: {e}")
            return 0
    
    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate vector embedding for text using OpenAI API"""
        if not self.openai_client:
            return None
        
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception:
            return 0.0
    
    def _check_and_prune_memories(self, user_id: str):
        """Check if user has too many memories and prune if necessary"""
        try:
            memory_count_result = self.supabase.table('eliza_memory').select('id', count='exact').eq('user_id', user_id).eq('is_active', True).execute()
            memory_count = memory_count_result.count if memory_count_result.count else 0
            
            if memory_count > self.max_memories_per_user:
                # Get oldest, lowest relevance memories to prune
                excess_count = memory_count - self.max_memories_per_user
                
                memories_to_prune = self.supabase.table('eliza_memory').select('id').eq('user_id', user_id).eq('is_active', True).order('relevance_score').order('created_at').limit(excess_count).execute()
                
                if memories_to_prune.data:
                    memory_ids = [mem['id'] for mem in memories_to_prune.data]
                    self.supabase.table('eliza_memory').update({'is_active': False}).in_('id', memory_ids).execute()
                
        except Exception as e:
            print(f"Error in auto-pruning: {e}")


# Global memory manager instance
supabase_memory_manager = SupabaseMemoryManager()

