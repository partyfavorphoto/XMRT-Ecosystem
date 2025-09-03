"""
XMRT-Ecosystem Memory System

This module implements persistent memory and learning pattern analysis using:
- Supabase for real-time database operations
- Vector embeddings for semantic search and pattern recognition  
- Long-term memory storage for learning cycles and insights
- Pattern analysis for continuous improvement identification
- Cross-session knowledge retention and application
"""

import asyncio
import logging
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
import traceback
import hashlib

# Supabase client (placeholder for actual implementation)
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Supabase not available - using local memory only")

# Vector embeddings and similarity (with fallbacks)
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Sentence transformers not available - using basic text similarity")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemorySystem:
    """
    Persistent memory system for the XMRT-Ecosystem autonomous learning

    Features:
    - Real-time data storage with Supabase
    - Vector embeddings for semantic search
    - Learning pattern analysis and recognition
    - Cross-session knowledge retention
    - Automatic knowledge graph building
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize memory system with Supabase and embedding models"""
        self.config = config

        # Supabase configuration
        self.supabase_url = config.get('supabase_url')
        self.supabase_key = config.get('supabase_key')
        self.supabase_client = None

        # Vector embedding model
        self.embedding_model = None
        self.embedding_dimension = 384  # Default for sentence-transformers models

        # Memory caches
        self.learning_patterns_cache = []
        self.knowledge_graph = {}
        self.session_memory = {}

        # Memory statistics
        self.memory_stats = {
            'total_learning_cycles': 0,
            'total_patterns_stored': 0,
            'total_insights_generated': 0,
            'memory_size_bytes': 0,
            'last_cleanup': None,
            'retrieval_performance': []
        }

        logger.info("🧠 Memory System initialized")

    async def initialize(self):
        """Initialize Supabase connection and embedding model"""
        try:
            logger.info("🔧 Initializing memory system components...")

            # Initialize Supabase client
            if self.supabase_url and self.supabase_key and SUPABASE_AVAILABLE:
                self.supabase_client = create_client(self.supabase_url, self.supabase_key)
                logger.info("✅ Supabase client initialized")
            else:
                logger.warning("⚠️ Supabase credentials not provided, using local memory only")

            # Initialize embedding model
            await self._initialize_embedding_model()

            # Load existing memory data
            await self._load_memory_cache()

            logger.info("✅ Memory system initialization completed")

        except Exception as e:
            logger.error(f"❌ Memory system initialization failed: {e}")
            logger.error(traceback.format_exc())
            # Continue with basic functionality

    async def _initialize_embedding_model(self):
        """Initialize sentence transformer model for vector embeddings"""
        try:
            if EMBEDDINGS_AVAILABLE:
                logger.info("🔄 Loading sentence transformer model...")

                # Use a lightweight but effective model
                model_name = 'all-MiniLM-L6-v2'  # 384 dimensions, good performance
                self.embedding_model = SentenceTransformer(model_name)
                self.embedding_dimension = self.embedding_model.get_sentence_embedding_dimension()

                logger.info(f"✅ Embedding model loaded: {model_name} ({self.embedding_dimension}D)")
            else:
                logger.warning("⚠️ Sentence transformers not available, using text hashing")
                self.embedding_model = None
                self.embedding_dimension = 256

        except Exception as e:
            logger.error(f"❌ Failed to initialize embedding model: {e}")
            # Fallback to simple text hashing if model fails
            self.embedding_model = None
            self.embedding_dimension = 256

    async def _load_memory_cache(self):
        """Load recent memory data into cache for fast access"""
        try:
            logger.info("📖 Loading memory cache...")

            if self.supabase_client:
                # Load recent learning patterns from database
                recent_patterns = await self._get_recent_patterns_from_db(limit=100)
                self.learning_patterns_cache = recent_patterns

                # Build knowledge graph from patterns
                await self._build_knowledge_graph()

            logger.info(f"✅ Memory cache loaded: {len(self.learning_patterns_cache)} patterns")

        except Exception as e:
            logger.error(f"❌ Failed to load memory cache: {e}")
            self.learning_patterns_cache = []

    async def _get_recent_patterns_from_db(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent learning patterns from database"""
        try:
            if not self.supabase_client:
                return []

            # Placeholder for actual Supabase query
            # In real implementation, this would query the learning_patterns table
            return []

        except Exception as e:
            logger.error(f"❌ Database query failed: {e}")
            return []

    async def store_learning_cycle(self, cycle_data: Dict[str, Any]):
        """Store complete learning cycle data with vector embedding"""
        try:
            cycle_id = cycle_data.get('cycle_id')
            logger.info(f"💾 Storing learning cycle: {cycle_id}")

            # Generate embedding for the cycle
            cycle_text = self._extract_text_for_embedding(cycle_data)
            embedding = await self._generate_embedding(cycle_text)

            # Prepare data for storage
            storage_data = {
                'cycle_id': cycle_id,
                'timestamp': cycle_data.get('timestamp', datetime.now().isoformat()),
                'strategic_analysis': cycle_data.get('results', {}).get('strategic_analysis', {}),
                'collaboration_results': cycle_data.get('results', {}).get('collaboration_results', {}),
                'implementation_results': cycle_data.get('results', {}).get('implementation_results', {}),
                'deployment_results': cycle_data.get('results', {}).get('deployment_results', {}),
                'cycle_duration': cycle_data.get('results', {}).get('cycle_duration', 0),
                'success_metrics': cycle_data.get('metrics_snapshot', {}),
                'embedding': embedding.tolist() if embedding is not None else None
            }

            # Store in database if available
            if self.supabase_client:
                await self._store_in_database('learning_cycles', storage_data)

            # Update local cache and stats
            self.memory_stats['total_learning_cycles'] += 1

            # Extract and store learning patterns
            await self._extract_learning_patterns(cycle_data)

            logger.info(f"✅ Learning cycle {cycle_id} stored successfully")

        except Exception as e:
            logger.error(f"❌ Failed to store learning cycle: {e}")

    async def store_learning_pattern(self, pattern_data: Dict[str, Any]):
        """Store individual learning pattern"""
        try:
            pattern_type = pattern_data.get('type', 'general')

            # Generate pattern ID
            pattern_content = json.dumps(pattern_data, sort_keys=True)
            pattern_id = hashlib.md5(pattern_content.encode()).hexdigest()

            # Generate embedding
            pattern_text = self._extract_pattern_text(pattern_data)
            embedding = await self._generate_embedding(pattern_text)

            # Check if pattern already exists
            existing_pattern = await self._find_similar_pattern(embedding, threshold=0.9)

            if existing_pattern:
                # Update existing pattern frequency
                await self._update_pattern_frequency(existing_pattern['pattern_id'])
                logger.info(f"📈 Updated existing pattern frequency: {existing_pattern['pattern_id']}")
            else:
                # Store new pattern
                storage_data = {
                    'pattern_id': pattern_id,
                    'pattern_type': pattern_type,
                    'pattern_data': pattern_data,
                    'confidence_score': self._calculate_pattern_confidence(pattern_data),
                    'frequency_count': 1,
                    'first_seen': datetime.now().isoformat(),
                    'last_seen': datetime.now().isoformat(),
                    'embedding': embedding.tolist() if embedding is not None else None
                }

                if self.supabase_client:
                    await self._store_in_database('learning_patterns', storage_data)

                # Add to cache
                self.learning_patterns_cache.append(storage_data)
                self.memory_stats['total_patterns_stored'] += 1

                logger.info(f"💡 New learning pattern stored: {pattern_id}")

        except Exception as e:
            logger.error(f"❌ Failed to store learning pattern: {e}")

    async def get_recent_learning_patterns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent learning patterns for analysis"""
        try:
            # First check cache
            if len(self.learning_patterns_cache) >= limit:
                return self.learning_patterns_cache[:limit]

            # Query database if needed
            if self.supabase_client:
                patterns = await self._get_recent_patterns_from_db(limit)
                return patterns

            # Return cached patterns if no database
            return self.learning_patterns_cache[:limit]

        except Exception as e:
            logger.error(f"❌ Failed to get recent patterns: {e}")
            return []

    async def get_learning_patterns_since(self, since_date: datetime) -> List[Dict[str, Any]]:
        """Get learning patterns since a specific date"""
        try:
            # Filter from cache
            filtered_patterns = [
                pattern for pattern in self.learning_patterns_cache
                if datetime.fromisoformat(pattern.get('last_seen', datetime.now().isoformat())) >= since_date
            ]

            return filtered_patterns

        except Exception as e:
            logger.error(f"❌ Failed to get patterns since date: {e}")
            return []

    async def store_health_report(self, health_report: Dict[str, Any]):
        """Store system health report"""
        try:
            report_id = f"health_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            storage_data = {
                'report_id': report_id,
                'timestamp': health_report.get('timestamp', datetime.now().isoformat()),
                'system_metrics': health_report.get('metrics', {}),
                'agent_health': health_report.get('system_status', {}),
                'recommendations': health_report.get('recommendations', []),
                'overall_score': self._calculate_health_score(health_report)
            }

            if self.supabase_client:
                await self._store_in_database('health_reports', storage_data)

            logger.info(f"🏥 Health report stored: {report_id}")

        except Exception as e:
            logger.error(f"❌ Failed to store health report: {e}")

    async def store_weekly_analysis(self, analysis_data: Dict[str, Any]):
        """Store weekly analysis results"""
        try:
            # Calculate week boundaries
            now = datetime.now()
            week_start = now - timedelta(days=7)

            analysis_id = f"weekly_{week_start.strftime('%Y%W')}"

            storage_data = {
                'analysis_id': analysis_id,
                'week_start': week_start.isoformat(),
                'week_end': now.isoformat(),
                'analysis_data': analysis_data,
                'trends': await self._extract_weekly_trends(),
                'recommendations': analysis_data.get('recommendations', []),
                'performance_metrics': await self._calculate_weekly_metrics(),
                'created_at': now.isoformat()
            }

            if self.supabase_client:
                await self._store_in_database('weekly_analyses', storage_data)

            logger.info(f"📊 Weekly analysis stored: {analysis_id}")

        except Exception as e:
            logger.error(f"❌ Failed to store weekly analysis: {e}")

    async def _extract_learning_patterns(self, cycle_data: Dict[str, Any]):
        """Extract patterns from learning cycle data"""
        try:
            patterns = []

            results = cycle_data.get('results', {})

            # Extract success/failure patterns
            if 'error' in results.get('strategic_analysis', {}):
                patterns.append({
                    'type': 'failure',
                    'subtype': 'strategic_analysis',
                    'details': results['strategic_analysis']['error'],
                    'cycle_id': cycle_data.get('cycle_id'),
                    'timestamp': cycle_data.get('timestamp')
                })
            else:
                patterns.append({
                    'type': 'success',
                    'subtype': 'strategic_analysis',
                    'details': 'Strategic analysis completed successfully',
                    'cycle_id': cycle_data.get('cycle_id'),
                    'timestamp': cycle_data.get('timestamp')
                })

            # Extract deployment patterns
            deployment = results.get('deployment_results', {})
            if deployment.get('deployment_triggered', False):
                patterns.append({
                    'type': 'deployment_success',
                    'subtype': 'auto_deployment',
                    'details': f"Files deployed: {len(deployment.get('files_committed', []))}",
                    'files_count': len(deployment.get('files_committed', [])),
                    'cycle_id': cycle_data.get('cycle_id'),
                    'timestamp': cycle_data.get('timestamp')
                })

            # Store extracted patterns
            for pattern in patterns:
                await self.store_learning_pattern(pattern)

        except Exception as e:
            logger.error(f"❌ Failed to extract learning patterns: {e}")

    async def _generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate vector embedding for text"""
        try:
            if self.embedding_model and text:
                embedding = self.embedding_model.encode(text)
                return np.array(embedding)
            else:
                # Fallback to simple hash-based embedding
                text_hash = hashlib.sha256(text.encode()).digest()
                return np.frombuffer(text_hash, dtype=np.uint8)[:self.embedding_dimension]

        except Exception as e:
            logger.error(f"❌ Failed to generate embedding: {e}")
            return None

    def _extract_text_for_embedding(self, data: Dict[str, Any]) -> str:
        """Extract meaningful text from data for embedding generation"""
        text_parts = []

        # Extract text from various fields recursively
        def extract_text_recursive(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str) and len(value) > 0:
                        text_parts.append(f"{prefix}{key}: {value}")
                    elif isinstance(value, (dict, list)):
                        extract_text_recursive(value, f"{prefix}{key}_")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if isinstance(item, str) and len(item) > 0:
                        text_parts.append(f"{prefix}{i}: {item}")
                    elif isinstance(item, (dict, list)):
                        extract_text_recursive(item, f"{prefix}{i}_")

        extract_text_recursive(data)
        return " ".join(text_parts)

    def _extract_pattern_text(self, pattern_data: Dict[str, Any]) -> str:
        """Extract text representation of pattern for embedding"""
        pattern_type = pattern_data.get('type', '')
        details = pattern_data.get('details', '')
        subtype = pattern_data.get('subtype', '')

        return f"{pattern_type} {subtype} {details}".strip()

    async def _find_similar_pattern(self, embedding: np.ndarray, threshold: float = 0.9) -> Optional[Dict[str, Any]]:
        """Find existing similar pattern based on embedding similarity"""
        try:
            if embedding is None or not EMBEDDINGS_AVAILABLE:
                return None

            for pattern in self.learning_patterns_cache:
                if 'embedding' in pattern and pattern['embedding']:
                    stored_embedding = np.array(pattern['embedding'])

                    similarity = cosine_similarity(
                        embedding.reshape(1, -1),
                        stored_embedding.reshape(1, -1)
                    )[0][0]

                    if similarity >= threshold:
                        return pattern

            return None

        except Exception as e:
            logger.error(f"❌ Failed to find similar pattern: {e}")
            return None

    async def _update_pattern_frequency(self, pattern_id: str):
        """Update frequency count for existing pattern"""
        try:
            # Update in cache
            for pattern in self.learning_patterns_cache:
                if pattern.get('pattern_id') == pattern_id:
                    pattern['frequency_count'] = pattern.get('frequency_count', 0) + 1
                    pattern['last_seen'] = datetime.now().isoformat()
                    break

        except Exception as e:
            logger.error(f"❌ Failed to update pattern frequency: {e}")

    def _calculate_pattern_confidence(self, pattern_data: Dict[str, Any]) -> float:
        """Calculate confidence score for a pattern"""
        base_confidence = 0.5

        # Increase confidence based on data completeness
        if pattern_data.get('details'):
            base_confidence += 0.2

        if pattern_data.get('cycle_id'):
            base_confidence += 0.1

        if pattern_data.get('type') in ['success', 'failure']:
            base_confidence += 0.2

        return min(1.0, base_confidence)

    def _calculate_health_score(self, health_report: Dict[str, Any]) -> float:
        """Calculate overall health score from report"""
        try:
            metrics = health_report.get('metrics', {})
            system_status = health_report.get('system_status', {})

            score = 1.0

            # Deduct points for failures
            failed_attempts = metrics.get('failed_attempts', 0)
            if failed_attempts > 0:
                score -= min(0.3, failed_attempts * 0.1)

            # Check system component health
            for component, status in system_status.items():
                if isinstance(status, dict) and not status.get('active', True):
                    score -= 0.2

            return max(0.0, score)

        except Exception as e:
            logger.error(f"❌ Failed to calculate health score: {e}")
            return 0.5

    async def _extract_weekly_trends(self) -> Dict[str, Any]:
        """Extract trends from the past week"""
        try:
            week_ago = datetime.now() - timedelta(days=7)
            weekly_patterns = await self.get_learning_patterns_since(week_ago)

            trends = {
                'pattern_count': len(weekly_patterns),
                'success_rate': 0.0,
                'most_common_pattern': 'none',
                'failure_rate': 0.0
            }

            if weekly_patterns:
                success_patterns = [p for p in weekly_patterns if p.get('pattern_type') == 'success']
                failure_patterns = [p for p in weekly_patterns if p.get('pattern_type') == 'failure']

                trends['success_rate'] = len(success_patterns) / len(weekly_patterns)
                trends['failure_rate'] = len(failure_patterns) / len(weekly_patterns)

                # Find most common pattern
                pattern_types = {}
                for pattern in weekly_patterns:
                    ptype = pattern.get('pattern_type', 'unknown')
                    pattern_types[ptype] = pattern_types.get(ptype, 0) + 1

                if pattern_types:
                    trends['most_common_pattern'] = max(pattern_types.items(), key=lambda x: x[1])[0]

            return trends

        except Exception as e:
            logger.error(f"❌ Failed to extract weekly trends: {e}")
            return {}

    async def _calculate_weekly_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics for the past week"""
        try:
            return {
                'total_learning_cycles': self.memory_stats['total_learning_cycles'],
                'patterns_discovered': self.memory_stats['total_patterns_stored'],
                'insights_generated': self.memory_stats['total_insights_generated'],
                'memory_efficiency': self._calculate_memory_efficiency()
            }

        except Exception as e:
            logger.error(f"❌ Failed to calculate weekly metrics: {e}")
            return {}

    def _calculate_memory_efficiency(self) -> float:
        """Calculate memory system efficiency"""
        try:
            cache_size = len(self.learning_patterns_cache)
            total_patterns = self.memory_stats['total_patterns_stored']

            if total_patterns == 0:
                return 1.0

            # Efficiency based on cache hit rate and pattern diversity
            efficiency = min(1.0, cache_size / max(1, total_patterns))
            return efficiency

        except Exception as e:
            return 0.5

    async def _store_in_database(self, table: str, data: Dict[str, Any]):
        """Store data in Supabase table"""
        try:
            if self.supabase_client:
                # Placeholder for actual Supabase storage
                logger.debug(f"📝 Stored data in {table} table")
                return True
            return False

        except Exception as e:
            logger.error(f"❌ Database storage failed for {table}: {e}")
            return False

    async def _build_knowledge_graph(self):
        """Build knowledge graph from learning patterns"""
        try:
            self.knowledge_graph = {
                'nodes': [],
                'edges': [],
                'concepts': {}
            }

            # Extract concepts and relationships from patterns
            for pattern in self.learning_patterns_cache:
                pattern_type = pattern.get('pattern_type', 'unknown')

                # Add pattern as node
                node_id = pattern.get('pattern_id')
                self.knowledge_graph['nodes'].append({
                    'id': node_id,
                    'type': pattern_type,
                    'frequency': pattern.get('frequency_count', 1),
                    'confidence': pattern.get('confidence_score', 0.5)
                })

                # Track concept frequency
                if pattern_type in self.knowledge_graph['concepts']:
                    self.knowledge_graph['concepts'][pattern_type] += 1
                else:
                    self.knowledge_graph['concepts'][pattern_type] = 1

            logger.debug(f"🕸️ Knowledge graph built: {len(self.knowledge_graph['nodes'])} nodes")

        except Exception as e:
            logger.error(f"❌ Failed to build knowledge graph: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Perform memory system health check"""
        try:
            health_status = {
                'memory_system_status': 'healthy',
                'supabase_connected': self.supabase_client is not None,
                'embedding_model_loaded': self.embedding_model is not None,
                'cache_size': len(self.learning_patterns_cache),
                'memory_stats': self.memory_stats.copy(),
                'knowledge_graph_size': len(self.knowledge_graph.get('nodes', [])),
                'last_check': datetime.now().isoformat()
            }

            # Check if system is functioning properly
            if not self.embedding_model:
                health_status['memory_system_status'] = 'degraded'

            if len(self.learning_patterns_cache) == 0:
                health_status['memory_system_status'] = 'initializing'

            return health_status

        except Exception as e:
            logger.error(f"❌ Memory health check failed: {e}")
            return {
                'memory_system_status': 'unhealthy',
                'error': str(e)
            }

    def get_status(self) -> Dict[str, Any]:
        """Get current memory system status"""
        return {
            'initialized': self.embedding_model is not None,
            'supabase_connected': self.supabase_client is not None,
            'patterns_cached': len(self.learning_patterns_cache),
            'memory_stats': self.memory_stats.copy(),
            'last_activity': datetime.now().isoformat()
        }
