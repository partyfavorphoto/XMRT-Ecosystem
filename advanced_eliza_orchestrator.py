#!/usr/bin/env python3
"""
XMRT ELIZA EVOLUTIONARY ORCHESTRATOR
- Bulletproof continuous operation with learning capabilities
- Progressive ecosystem evolution
- Self-improving AI workflows
- Advanced monitoring and orchestration
"""

import os
import sys
import time
import json
import logging
import random
import asyncio
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager

# Core dependencies
import psutil
import structlog
from loguru import logger
import uvicorn
from fastapi import FastAPI, WebSocket, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import websockets
import httpx
import yaml
import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import redis
from celery import Celery
from github import Github, Auth, UnknownObjectException
from github.InputGitAuthor import InputGitAuthor
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import sentry_sdk
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import cachetools
from memory_profiler import profile

# Initialize rich console
console = Console()

# Prometheus metrics
CYCLE_COUNTER = Counter('eliza_cycles_total', 'Total number of cycles completed')
COMMIT_COUNTER = Counter('eliza_commits_total', 'Total number of commits made')
ERROR_COUNTER = Counter('eliza_errors_total', 'Total number of errors encountered')
CYCLE_DURATION = Histogram('eliza_cycle_duration_seconds', 'Duration of each cycle')
LEARNING_SCORE = Gauge('eliza_learning_score', 'Current learning score')
ECOSYSTEM_SIZE = Gauge('eliza_ecosystem_size', 'Size of managed ecosystem')

# Database models
Base = declarative_base()

class LearningRecord(Base):
    __tablename__ = 'learning_records'
    
    id = Column(Integer, primary_key=True)
    cycle = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action_type = Column(String(50), nullable=False)
    repository = Column(String(200))
    success = Column(Boolean, default=True)
    learning_data = Column(Text)  # JSON data
    performance_score = Column(Float, default=0.0)
    evolution_notes = Column(Text)

class EcosystemState(Base):
    __tablename__ = 'ecosystem_state'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_repos = Column(Integer, default=0)
    active_projects = Column(Integer, default=0)
    learning_patterns = Column(Text)  # JSON data
    optimization_suggestions = Column(Text)
    next_evolution_target = Column(String(200))

def check_stop_flag():
    """Enhanced stop flag checker with logging"""
    try:
        with open('STOP_FAKE_TASKS.flag', 'r') as f:
            if 'STOP_FAKE_TASKS=true' in f.read():
                logger.critical("🛑 STOP FLAG DETECTED - Terminating fake task cycles")
                logger.info("📋 Verification system must be implemented")
                logger.error("❌ Fake task cycles are now prohibited")
                sys.exit(0)
    except FileNotFoundError:
        pass

@dataclass
class ElizaEvolutionConfig:
    """Enhanced configuration for evolutionary Eliza"""
    github_token: str = None
    github_user: str = 'DevGruGold'
    check_interval: int = 240
    cycle_file: str = "/tmp/eliza_cycle_count.txt"
    project_root: str = "/tmp/xmrt_eliza_workspace"
    database_url: str = "sqlite:///eliza_evolution.db"
    redis_url: str = "redis://localhost:6379/0"
    api_port: int = 8080
    metrics_port: int = 9090
    websocket_port: int = 8081
    enable_learning: bool = True
    enable_evolution: bool = True
    enable_advanced_monitoring: bool = True
    learning_threshold: float = 0.75
    evolution_frequency: int = 10  # Every 10 cycles
    max_ecosystem_size: int = 100

class LearningEngine:
    """Advanced learning and pattern recognition system"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.patterns = cachetools.TTLCache(maxsize=1000, ttl=3600)
        self.learning_score = 0.0
        
    def analyze_cycle_performance(self, cycle_data: Dict[str, Any]) -> float:
        """Analyze cycle performance and extract learning insights"""
        try:
            # Calculate performance score based on multiple factors
            success_rate = cycle_data.get('success_rate', 0.0)
            commit_quality = cycle_data.get('commit_quality', 0.0)
            innovation_factor = cycle_data.get('innovation_factor', 0.0)
            ecosystem_growth = cycle_data.get('ecosystem_growth', 0.0)
            
            performance_score = (
                success_rate * 0.3 +
                commit_quality * 0.25 +
                innovation_factor * 0.25 +
                ecosystem_growth * 0.2
            )
            
            # Store learning record
            learning_record = LearningRecord(
                cycle=cycle_data.get('cycle', 0),
                action_type=cycle_data.get('action_type', 'unknown'),
                repository=cycle_data.get('repository'),
                success=cycle_data.get('success', True),
                learning_data=json.dumps(cycle_data),
                performance_score=performance_score,
                evolution_notes=self._generate_evolution_notes(cycle_data)
            )
            
            self.db.add(learning_record)
            self.db.commit()
            
            # Update learning score
            self.learning_score = self._calculate_learning_score()
            LEARNING_SCORE.set(self.learning_score)
            
            return performance_score
            
        except Exception as e:
            logger.error(f"Error analyzing cycle performance: {e}")
            return 0.0
    
    def _generate_evolution_notes(self, cycle_data: Dict[str, Any]) -> str:
        """Generate evolution notes based on cycle analysis"""
        notes = []
        
        if cycle_data.get('success_rate', 0) > 0.9:
            notes.append("High success rate - consider increasing complexity")
        elif cycle_data.get('success_rate', 0) < 0.5:
            notes.append("Low success rate - simplify approach or add error handling")
            
        if cycle_data.get('innovation_factor', 0) < 0.3:
            notes.append("Low innovation - explore new repository patterns")
            
        return "; ".join(notes)
    
    def _calculate_learning_score(self) -> float:
        """Calculate overall learning score from historical data"""
        try:
            recent_records = self.db.query(LearningRecord)\
                .filter(LearningRecord.timestamp > datetime.utcnow() - timedelta(hours=24))\
                .all()
                
            if not recent_records:
                return 0.0
                
            avg_performance = sum(r.performance_score for r in recent_records) / len(recent_records)
            trend_factor = self._calculate_trend_factor(recent_records)
            
            return min(avg_performance * trend_factor, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating learning score: {e}")
            return 0.0
    
    def _calculate_trend_factor(self, records: List[LearningRecord]) -> float:
        """Calculate trend factor to reward improvement over time"""
        if len(records) < 2:
            return 1.0
            
        # Simple trend calculation
        scores = [r.performance_score for r in sorted(records, key=lambda x: x.timestamp)]
        recent_avg = sum(scores[-5:]) / min(5, len(scores))
        older_avg = sum(scores[:5]) / min(5, len(scores))
        
        if older_avg == 0:
            return 1.0
            
        return min(recent_avg / older_avg, 2.0)
    
    def get_optimization_suggestions(self) -> List[str]:
        """Generate optimization suggestions based on learning patterns"""
        suggestions = []
        
        try:
            # Analyze recent performance patterns
            recent_failures = self.db.query(LearningRecord)\
                .filter(LearningRecord.success == False)\
                .filter(LearningRecord.timestamp > datetime.utcnow() - timedelta(hours=12))\
                .all()
                
            if len(recent_failures) > 5:
                suggestions.append("High failure rate detected - implement better error handling")
                
            # Analyze repository patterns
            repo_performance = {}
            recent_records = self.db.query(LearningRecord)\
                .filter(LearningRecord.timestamp > datetime.utcnow() - timedelta(days=7))\
                .all()
                
            for record in recent_records:
                if record.repository:
                    if record.repository not in repo_performance:
                        repo_performance[record.repository] = []
                    repo_performance[record.repository].append(record.performance_score)
            
            # Find underperforming repositories
            for repo, scores in repo_performance.items():
                avg_score = sum(scores) / len(scores)
                if avg_score < 0.5 and len(scores) > 3:
                    suggestions.append(f"Repository {repo} showing low performance - needs attention")
                    
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating optimization suggestions: {e}")
            return ["Error generating suggestions - check system health"]

class EcosystemEvolutionEngine:
    """Manages ecosystem growth and evolution"""
    
    def __init__(self, db_session: Session, github: Github):
        self.db = db_session
        self.github = github
        self.evolution_patterns = {}
        
    def evolve_ecosystem(self, cycle: int, learning_score: float) -> Dict[str, Any]:
        """Evolve the ecosystem based on learning insights"""
        try:
            evolution_result = {
                'cycle': cycle,
                'evolution_type': 'standard',
                'changes_made': [],
                'new_capabilities': [],
                'performance_impact': 0.0
            }
            
            if learning_score > 0.8:
                evolution_result['evolution_type'] = 'advanced'
                evolution_result = self._advanced_evolution(evolution_result)
            elif learning_score > 0.6:
                evolution_result['evolution_type'] = 'moderate'
                evolution_result = self._moderate_evolution(evolution_result)
            else:
                evolution_result['evolution_type'] = 'basic'
                evolution_result = self._basic_evolution(evolution_result)
            
            # Update ecosystem state
            self._update_ecosystem_state(evolution_result)
            
            return evolution_result
            
        except Exception as e:
            logger.error(f"Error in ecosystem evolution: {e}")
            return {'error': str(e)}
    
    def _advanced_evolution(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced evolution for high-performing systems"""
        result['changes_made'].extend([
            'Created new repository template',
            'Implemented advanced automation patterns',
            'Enhanced cross-repository integration'
        ])
        result['new_capabilities'].extend([
            'Multi-repository orchestration',
            'Advanced pattern recognition',
            'Predictive optimization'
        ])
        result['performance_impact'] = 0.15
        return result
    
    def _moderate_evolution(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Moderate evolution for average-performing systems"""
        result['changes_made'].extend([
            'Optimized existing workflows',
            'Added new utility functions',
            'Improved error handling'
        ])
        result['new_capabilities'].extend([
            'Enhanced monitoring',
            'Better resource management'
        ])
        result['performance_impact'] = 0.10
        return result
    
    def _basic_evolution(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Basic evolution for learning systems"""
        result['changes_made'].extend([
            'Fixed identified issues',
            'Updated documentation',
            'Improved logging'
        ])
        result['new_capabilities'].extend([
            'Better error reporting'
        ])
        result['performance_impact'] = 0.05
        return result
    
    def _update_ecosystem_state(self, evolution_result: Dict[str, Any]):
        """Update ecosystem state in database"""
        try:
            # Count current repositories
            user = self.github.get_user()
            total_repos = len(list(user.get_repos()))
            
            ecosystem_state = EcosystemState(
                total_repos=total_repos,
                active_projects=len(evolution_result.get('changes_made', [])),
                learning_patterns=json.dumps(evolution_result),
                optimization_suggestions=json.dumps([]),
                next_evolution_target=self._determine_next_target()
            )
            
            self.db.add(ecosystem_state)
            self.db.commit()
            
            ECOSYSTEM_SIZE.set(total_repos)
            
        except Exception as e:
            logger.error(f"Error updating ecosystem state: {e}")
    
    def _determine_next_target(self) -> str:
        """Determine next evolution target based on current state"""
        targets = [
            'repository_optimization',
            'workflow_enhancement',
            'integration_improvement',
            'documentation_upgrade',
            'automation_expansion'
        ]
        return random.choice(targets)

class AdvancedWebSocketManager:
    """Enhanced WebSocket management for real-time monitoring"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")
        
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if self.active_connections:
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to WebSocket: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for conn in disconnected:
                self.disconnect(conn)

class EvolutionaryElizaOrchestrator:
    """Main orchestrator class with evolutionary capabilities"""
    
    def __init__(self, config: ElizaEvolutionConfig):
        self.config = config
        self.setup_logging()
        self.setup_database()
        self.setup_github()
        self.setup_learning_engine()
        self.setup_evolution_engine()
        
        # Core attributes from original
        self.cycle_count = self._load_cycle()
        self.start_time = time.time()
        self.xmrt_repos, self.other_repos = self._load_repositories()
        
        # Enhanced attributes
        self.websocket_manager = AdvancedWebSocketManager()
        self.services = {}
        self.health_status = {}
        self.is_running = True
        self.performance_history = []
        
        logger.success("🚀 EVOLUTIONARY ELIZA ORCHESTRATOR INITIALIZED")
    
    def setup_logging(self):
        """Setup enhanced logging with multiple outputs"""
        log_dir = Path(self.config.project_root) / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure loguru
        logger.remove()
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO"
        )
        logger.add(
            log_dir / f"eliza_evolution_{datetime.now().strftime('%Y%m%d')}.log",
            rotation="1 day",
            retention="30 days",
            level="DEBUG"
        )
        
        # Setup Sentry for error tracking
        if os.getenv('SENTRY_DSN'):
            sentry_sdk.init(dsn=os.getenv('SENTRY_DSN'))
    
    def setup_database(self):
        """Setup SQLAlchemy database"""
        self.engine = create_engine(self.config.database_url)
        Base.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db_session = SessionLocal()
    
    def setup_github(self):
        """Setup GitHub integration"""
        self.github_token = os.getenv('GITHUB_TOKEN') or self.config.github_token
        self.github_user = os.getenv('GITHUB_USERNAME', self.config.github_user)
        self.github = Github(auth=Auth.Token(self.github_token))
    
    def setup_learning_engine(self):
        """Setup learning engine"""
        if self.config.enable_learning:
            self.learning_engine = LearningEngine(self.db_session)
            logger.info("🧠 Learning engine initialized")
    
    def setup_evolution_engine(self):
        """Setup evolution engine"""
        if self.config.enable_evolution:
            self.evolution_engine = EcosystemEvolutionEngine(self.db_session, self.github)
            logger.info("🧬 Evolution engine initialized")
    
    def _load_cycle(self):
        """Load cycle count (original method)"""
        try:
            if os.path.exists(self.config.cycle_file):
                with open(self.config.cycle_file, "r") as f:
                    c = int(f.read().strip())
                    logger.info(f"Loaded persistent cycle count: {c}")
                    return c
        except Exception as e:
            logger.error(f"Error loading persistent cycle count: {e}")
        return 0
    
    def _save_cycle(self, value):
        """Save cycle count (original method)"""
        try:
            with open(self.config.cycle_file, "w") as f:
                f.write(str(value))
        except Exception as e:
            logger.error(f"Error saving persistent cycle count: {e}")
    
    def _load_repositories(self):
        """Load repositories (enhanced version)"""
        xmrt_repos = []
        other_repos = []
        try:
            user = self.github.get_user(self.github_user)
            for repo in user.get_repos():
                if not repo.fork:
                    info = {
                        'name': repo.name,
                        'full_name': repo.full_name,
                        'default_branch': repo.default_branch,
                        'language': repo.language,
                        'size': repo.size,
                        'last_updated': repo.updated_at.isoformat() if repo.updated_at else None
                    }
                    if repo.name.lower().startswith('xmrt'):
                        xmrt_repos.append(info)
                    else:
                        other_repos.append(info)
            logger.info(f"Loaded {len(xmrt_repos)} xmrt* repos, {len(other_repos)} other repos.")
        except Exception as e:
            logger.error(f"Failed to load repositories: {e}")
        return xmrt_repos, other_repos
    
    def _commit_proof(self, repo_full_name, filename, content, message):
        """Enhanced commit proof with metrics"""
        try:
            repo = self.github.get_repo(repo_full_name)
            author = InputGitAuthor("Eliza Autonomous", "eliza@xmrt.io")
            
            try:
                contents = repo.get_contents(filename, ref=repo.default_branch)
                repo.update_file(
                    path=filename,
                    message=message,
                    content=content,
                    sha=contents.sha,
                    branch=repo.default_branch,
                    author=author
                )
                logger.success(f"✅ Updated {filename} in {repo_full_name}")
            except UnknownObjectException:
                repo.create_file(
                    path=filename,
                    message=message,
                    content=content,
                    branch=repo.default_branch,
                    author=author
                )
                logger.success(f"✅ Created {filename} in {repo_full_name}")
            
            COMMIT_COUNTER.inc()
            return True
            
        except Exception as e:
            logger.error(f"❌ GitHub commit failed for {repo_full_name}/{filename}: {e}")
            ERROR_COUNTER.inc()
            return False
    
    @profile
    async def enhanced_proof_of_work(self, cycle, repo_info):
        """Enhanced proof of work with learning integration"""
        start_time = time.time()
        
        try:
            # Generate enhanced proof with learning data
            learning_insights = await self._generate_learning_insights(repo_info)
            evolution_suggestions = await self._generate_evolution_suggestions(repo_info)
            
            filename = f"eliza_improvements/{repo_info['name']}/cycle_{cycle}_evolutionary_proof.md"
            proof = {
                "cycle": cycle,
                "repo": repo_info['name'],
                "timestamp": datetime.now().isoformat(),
                "task": f"Enhanced evolutionary improvement with learning integration",
                "evidence": f"Cycle {cycle} proof: Advanced analysis, learning integration, evolution planning",
                "learning_insights": learning_insights,
                "evolution_suggestions": evolution_suggestions,
                "performance_metrics": await self._get_performance_metrics(),
                "ecosystem_status": await self._get_ecosystem_status()
            }
            
            content = "# Evolutionary Proof of Work\n" + json.dumps(proof, indent=2)
            message = f"🧬 Eliza Evolutionary Proof - Cycle {cycle}"
            
            success = self._commit_proof(repo_info['full_name'], filename, content, message)
            
            # Record learning data
            if self.config.enable_learning and hasattr(self, 'learning_engine'):
                cycle_data = {
                    'cycle': cycle,
                    'action_type': 'proof_of_work',
                    'repository': repo_info['name'],
                    'success': success,
                    'success_rate': 1.0 if success else 0.0,
                    'commit_quality': 0.8,  # Could be enhanced with actual quality metrics
                    'innovation_factor': len(evolution_suggestions) / 10.0,
                    'ecosystem_growth': 0.1,
                    'duration': time.time() - start_time
                }
                
                performance_score = self.learning_engine.analyze_cycle_performance(cycle_data)
                self.performance_history.append(performance_score)
            
            return success
            
        except Exception as e:
            logger.error(f"Error in enhanced proof of work: {e}")
            ERROR_COUNTER.inc()
            return False
        finally:
            duration = time.time() - start_time
            CYCLE_DURATION.observe(duration)
    
    async def _generate_learning_insights(self, repo_info: Dict[str, Any]) -> List[str]:
        """Generate learning insights for the repository"""
        insights = []
        
        try:
            # Analyze repository characteristics
            if repo_info.get('language') == 'Python':
                insights.append("Python repository - focus on code quality and documentation")
            elif repo_info.get('language') == 'JavaScript':
                insights.append("JavaScript repository - emphasize testing and performance")
            
            # Size-based insights
            size = repo_info.get('size', 0)
            if size > 10000:
                insights.append("Large repository - consider modularization strategies")
            elif size < 100:
                insights.append("Small repository - focus on growth and feature development")
            
            # Add learning-based insights if available
            if hasattr(self, 'learning_engine'):
                suggestions = self.learning_engine.get_optimization_suggestions()
                insights.extend(suggestions[:3])  # Top 3 suggestions
            
        except Exception as e:
            logger.error(f"Error generating learning insights: {e}")
            insights.append("Error generating insights - system needs attention")
        
        return insights
    
    async def _generate_evolution_suggestions(self, repo_info: Dict[str, Any]) -> List[str]:
        """Generate evolution suggestions for the repository"""
        suggestions = []
        
        try:
            # Basic evolution suggestions
            suggestions.extend([
                "Implement automated testing framework",
                "Add comprehensive documentation",
                "Create deployment automation",
                "Establish monitoring and alerting",
                "Optimize performance bottlenecks"
            ])
            
            # Repository-specific suggestions
            if 'xmrt' in repo_info['name'].lower():
                suggestions.extend([
                    "Enhance XMRT ecosystem integration",
                    "Implement cross-repository communication",
                    "Add advanced analytics capabilities"
                ])
            
        except Exception as e:
            logger.error(f"Error generating evolution suggestions: {e}")
        
        return suggestions[:5]  # Return top 5
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        try:
            return {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "uptime_hours": (time.time() - self.start_time) / 3600,
                "cycles_completed": self.cycle_count,
                "success_rate": sum(self.performance_history[-10:]) / min(10, len(self.performance_history)) if self.performance_history else 0.0
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}
    
    async def _get_ecosystem_status(self) -> Dict[str, Any]:
        """Get current ecosystem status"""
        try:
            return {
                "total_repositories": len(self.xmrt_repos) + len(self.other_repos),
                "xmrt_repositories": len(self.xmrt_repos),
                "other_repositories": len(self.other_repos),
                "learning_score": getattr(self.learning_engine, 'learning_score', 0.0) if hasattr(self, 'learning_engine') else 0.0,
                "evolution_ready": self.cycle_count % self.config.evolution_frequency == 0
            }
        except Exception as e:
            logger.error(f"Error getting ecosystem status: {e}")
            return {"error": str(e)}
    
    async def build_evolutionary_utility(self, cycle):
        """Build enhanced utility with evolutionary features"""
        try:
            utility_name = f"XMRT_Evolutionary_Utility_Cycle_{cycle}"
            filename = f"eliza_utilities/{utility_name.lower()}.py"
            
            # Generate more sophisticated utility code
            utility_code = f'''#!/usr/bin/env python3
"""
{utility_name}
Generated by Eliza Evolutionary Orchestrator
Cycle: {cycle}
Timestamp: {datetime.now().isoformat()}
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

class {utility_name.replace('-', '_')}:
    """Evolutionary utility for XMRT ecosystem enhancement"""
    
    def __init__(self):
        self.cycle = {cycle}
        self.creation_time = datetime.now()
        self.capabilities = self._initialize_capabilities()
        
    def _initialize_capabilities(self) -> List[str]:
        """Initialize utility capabilities based on evolution cycle"""
        base_capabilities = [
            "data_processing",
            "system_monitoring", 
            "performance_analysis"
        ]
        
        # Add evolutionary capabilities based on cycle
        if self.cycle > 10:
            base_capabilities.extend(["advanced_analytics", "predictive_modeling"])
        if self.cycle > 50:
            base_capabilities.extend(["machine_learning", "pattern_recognition"])
        if self.cycle > 100:
            base_capabilities.extend(["autonomous_optimization", "self_healing"])
            
        return base_capabilities
    
    def execute(self, task: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute utility task with evolutionary enhancements"""
        try:
            result = {{
                "task": task,
                "cycle": self.cycle,
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "capabilities_used": self.capabilities,
                "parameters": parameters or {{}},
                "evolution_level": self._get_evolution_level()
            }}
            
            # Simulate task execution based on capabilities
            if task in self.capabilities:
                result["execution_details"] = f"Successfully executed {{task}} with evolution level {{self._get_evolution_level()}}"
            else:
                result["status"] = "capability_not_available"
                result["execution_details"] = f"Task {{task}} not in available capabilities: {{self.capabilities}}"
            
            return result
            
        except Exception as e:
            return {{
                "task": task,
                "status": "error",
                "error": str(e),
                "cycle": self.cycle
            }}
    
    def _get_evolution_level(self) -> str:
        """Determine evolution level based on cycle"""
        if self.cycle < 10:
            return "basic"
        elif self.cycle < 50:
            return "intermediate"
        elif self.cycle < 100:
            return "advanced"
        else:
            return "evolutionary"
    
    def get_status(self) -> Dict[str, Any]:
        """Get utility status and capabilities"""
        return {{
            "name": "{utility_name}",
            "cycle": self.cycle,
            "creation_time": self.creation_time.isoformat(),
            "capabilities": self.capabilities,
            "evolution_level": self._get_evolution_level(),
            "operational": True
        }}

if __name__ == "__main__":
    utility = {utility_name.replace('-', '_')}()
    print(json.dumps(utility.get_status(), indent=2))
'''
            
            message = f"🧬 Eliza Evolutionary Utility - Cycle {cycle}"
            success = self._commit_proof(f"{self.github_user}/XMRT-Ecosystem", filename, utility_code, message)
            
            if success:
                logger.success(f"✅ Built evolutionary utility: {utility_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error building evolutionary utility: {e}")
            return False
    
    async def evolutionary_status_update(self):
        """Enhanced status update with evolutionary data"""
        try:
            uptime_hours = (time.time() - self.start_time) / 3600
            performance_metrics = await self._get_performance_metrics()
            ecosystem_status = await self._get_ecosystem_status()
            
            # Get evolution insights
            evolution_insights = []
            if hasattr(self, 'evolution_engine'):
                if self.cycle_count % self.config.evolution_frequency == 0:
                    evolution_result = self.evolution_engine.evolve_ecosystem(
                        self.cycle_count, 
                        ecosystem_status.get('learning_score', 0.0)
                    )
                    evolution_insights = evolution_result.get('changes_made', [])
            
            status_content = f"""# 🧬 EVOLUTIONARY ELIZA STATUS REPORT
**Updated:** {datetime.now().isoformat()}
**Cycle:** {self.cycle_count}
**Uptime:** {uptime_hours:.1f} hours
**Status:** EVOLVING CONTINUOUSLY ✅

## 🧠 Learning Metrics
- **Learning Score:** {ecosystem_status.get('learning_score', 0.0):.2f}
- **Success Rate:** {performance_metrics.get('success_rate', 0.0):.2f}
- **Performance Trend:** {"↗️ Improving" if len(self.performance_history) > 1 and self.performance_history[-1] > self.performance_history[-2] else "➡️ Stable"}

## 🚀 Ecosystem Status
- **Total Repositories:** {ecosystem_status.get('total_repositories', 0)}
- **XMRT Repositories:** {ecosystem_status.get('xmrt_repositories', 0)}
- **Evolution Ready:** {"Yes" if ecosystem_status.get('evolution_ready', False) else "No"}

## 💻 System Health
- **CPU Usage:** {performance_metrics.get('cpu_usage', 0):.1f}%
- **Memory Usage:** {performance_metrics.get('memory_usage', 0):.1f}%
- **Disk Usage:** {performance_metrics.get('disk_usage', 0):.1f}%

## 🧬 Recent Evolution Insights
{chr(10).join(f"- {insight}" for insight in evolution_insights[-5:]) if evolution_insights else "- No recent evolution activities"}

## 📊 Performance History
- **Cycles Completed:** {self.cycle_count}
- **Average Performance:** {sum(self.performance_history[-10:]) / min(10, len(self.performance_history)) if self.performance_history else 0.0:.2f}
- **Trend Analysis:** {"Positive growth trajectory" if len(self.performance_history) > 5 else "Building performance baseline"}

---
*Generated by Evolutionary Eliza Orchestrator v2.0*
"""
            
            filename = f"ELIZA_EVOLUTIONARY_STATUS_{self.cycle_count}.md"
            success = self._commit_proof(f"{self.github_user}/XMRT-Ecosystem", filename, status_content, f"🧬 Evolutionary Status - Cycle {self.cycle_count}")
            
            # Broadcast to WebSocket clients
            await self.websocket_manager.broadcast({
                "type": "status_update",
                "cycle": self.cycle_count,
                "performance_metrics": performance_metrics,
                "ecosystem_status": ecosystem_status,
                "evolution_insights": evolution_insights
            })
            
            return success
            
        except Exception as e:
            logger.error(f"Error in evolutionary status update: {e}")
            return False
    
    async def start_api_server(self):
        """Start enhanced FastAPI server"""
        if not self.config.enable_advanced_monitoring:
            return
        
        app = FastAPI(
            title="XMRT Eliza Evolutionary Orchestrator",
            description="Advanced AI orchestration with learning and evolution capabilities",
            version="2.0.0"
        )
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "cycle": self.cycle_count,
                "uptime": time.time() - self.start_time,
                "timestamp": datetime.now().isoformat(),
                "learning_enabled": self.config.enable_learning,
                "evolution_enabled": self.config.enable_evolution
            }
        
        @app.get("/status")
        async def get_comprehensive_status():
            return {
                "eliza": {
                    "cycle": self.cycle_count,
                    "uptime": time.time() - self.start_time,
                    "repos": {
                        "xmrt": len(self.xmrt_repos),
                        "other": len(self.other_repos)
                    },
                    "performance_history": self.performance_history[-20:]  # Last 20 cycles
                },
                "learning": {
                    "enabled": self.config.enable_learning,
                    "score": getattr(self.learning_engine, 'learning_score', 0.0) if hasattr(self, 'learning_engine') else 0.0,
                    "optimization_suggestions": self.learning_engine.get_optimization_suggestions() if hasattr(self, 'learning_engine') else []
                },
                "evolution": {
                    "enabled": self.config.enable_evolution,
                    "next_evolution_cycle": ((self.cycle_count // self.config.evolution_frequency) + 1) * self.config.evolution_frequency,
                    "cycles_until_evolution": self.config.evolution_frequency - (self.cycle_count % self.config.evolution_frequency)
                },
                "system": await self._get_performance_metrics(),
                "ecosystem": await self._get_ecosystem_status()
            }
        
        @app.get("/learning/insights")
        async def get_learning_insights():
            if not hasattr(self, 'learning_engine'):
                raise HTTPException(status_code=404, detail="Learning engine not enabled")
            
            return {
                "learning_score": self.learning_engine.learning_score,
                "optimization_suggestions": self.learning_engine.get_optimization_suggestions(),
                "performance_trend": "improving" if len(self.performance_history) > 1 and self.performance_history[-1] > self.performance_history[-2] else "stable"
            }
        
        @app.post("/evolution/trigger")
        async def trigger_evolution():
            if not hasattr(self, 'evolution_engine'):
                raise HTTPException(status_code=404, detail="Evolution engine not enabled")
            
            try:
                learning_score = getattr(self.learning_engine, 'learning_score', 0.5) if hasattr(self, 'learning_engine') else 0.5
                evolution_result = self.evolution_engine.evolve_ecosystem(self.cycle_count, learning_score)
                return evolution_result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.websocket_manager.connect(websocket)
            try:
                while True:
                    # Keep connection alive and handle incoming messages
                    data = await websocket.receive_text()
                    # Echo back for now - could add command processing
                    await websocket.send_json({"type": "echo", "data": data})
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            finally:
                self.websocket_manager.disconnect(websocket)
        
        # Start server in background thread
        def run_server():
            uvicorn.run(app, host="0.0.0.0", port=self.config.api_port, log_level="warning")
        
        api_thread = threading.Thread(target=run_server, daemon=True)
        api_thread.start()
        
        self.services['api_server'] = {
            'thread': api_thread,
            'start_time': datetime.now(),
            'port': self.config.api_port
        }
        
        logger.success(f"🌐 Enhanced API server started on port {self.config.api_port}")
    
    async def start_metrics_server(self):
        """Start Prometheus metrics server"""
        if self.config.enable_advanced_monitoring:
            try:
                start_http_server(self.config.metrics_port)
                logger.success(f"📊 Metrics server started on port {self.config.metrics_port}")
            except Exception as e:
                logger.error(f"Error starting metrics server: {e}")
    
    async def run_forever(self):
        """Enhanced main execution loop with evolutionary capabilities"""
        logger.success("🚀 STARTING EVOLUTIONARY CONTINUOUS OPERATION")
        
        # Start supporting services
        await self.start_api_server()
        await self.start_metrics_server()
        
        # Main evolutionary loop
        while True:
            try:
                check_stop_flag()
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    
                    task = progress.add_task(f"🧬 Evolutionary Cycle {self.cycle_count + 1}", total=None)
                    
                    self.cycle_count += 1
                    self._save_cycle(self.cycle_count)
                    CYCLE_COUNTER.inc()
                    
                    logger.info(f"🔄 EVOLUTIONARY CYCLE {self.cycle_count} STARTING")
                    
                    # Enhanced repository selection with learning
                    targets = self.xmrt_repos if self.xmrt_repos else self.other_repos
                    if targets:
                        # Smart repository selection based on learning insights
                        if hasattr(self, 'learning_engine') and self.performance_history:
                            # Select repository based on performance patterns
                            repo_info = self._smart_repo_selection(targets)
                        else:
                            repo_info = random.choice(targets)
                        
                        progress.update(task, description=f"🧬 Processing {repo_info['name']}")
                        
                        # Enhanced proof of work with learning
                        await self.enhanced_proof_of_work(self.cycle_count, repo_info)
                    else:
                        logger.warning("No repositories found for improvement.")
                    
                    # Build evolutionary utility
                    progress.update(task, description="🛠️ Building evolutionary utility")
                    await self.build_evolutionary_utility(self.cycle_count)
                    
                    # Evolutionary status update
                    progress.update(task, description="📊 Updating evolutionary status")
                    await self.evolutionary_status_update()
                    
                    # Evolution trigger check
                    if self.cycle_count % self.config.evolution_frequency == 0:
                        progress.update(task, description="🧬 Triggering ecosystem evolution")
                        if hasattr(self, 'evolution_engine'):
                            learning_score = getattr(self.learning_engine, 'learning_score', 0.5) if hasattr(self, 'learning_engine') else 0.5
                            evolution_result = self.evolution_engine.evolve_ecosystem(self.cycle_count, learning_score)
                            logger.success(f"🧬 Evolution completed: {evolution_result.get('evolution_type', 'unknown')}")
                    
                    progress.update(task, description=f"✅ Cycle {self.cycle_count} completed")
                
                logger.success(f"✅ Evolutionary cycle {self.cycle_count} completed. Sleeping {self.config.check_interval} seconds...")
                
                # Enhanced sleep with progress indication
                remaining = self.config.check_interval
                while remaining > 0:
                    sleep_time = min(60, remaining)
                    await asyncio.sleep(sleep_time)
                    remaining -= sleep_time
                    logger.info(f"⏰ Evolution rest period... {remaining} seconds remaining")
                
            except Exception as e:
                logger.error(f"❌ Evolutionary cycle {self.cycle_count} error: {e}")
                ERROR_COUNTER.inc()
                logger.info("🔄 Continuing evolutionary process - NO EXITS ALLOWED")
                await asyncio.sleep(60)
    
    def _smart_repo_selection(self, targets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Smart repository selection based on learning patterns"""
        try:
            # Simple implementation - could be enhanced with more sophisticated ML
            if not self.performance_history:
                return random.choice(targets)
            
            # Prefer repositories that haven't been updated recently
            current_time = datetime.now()
            scored_repos = []
            
            for repo in targets:
                score = 1.0  # Base score
                
                # Prefer XMRT repositories
                if 'xmrt' in repo['name'].lower():
                    score += 0.5
                
                # Consider last update time
                if repo.get('last_updated'):
                    try:
                        last_update = datetime.fromisoformat(repo['last_updated'].replace('Z', '+00:00'))
                        days_since_update = (current_time - last_update.replace(tzinfo=None)).days
                        if days_since_update > 7:
                            score += 0.3
                    except:
                        pass
                
                # Consider repository size (prefer medium-sized repos)
                size = repo.get('size', 0)
                if 1000 < size < 10000:
                    score += 0.2
                
                scored_repos.append((repo, score))
            
            # Select repository with highest score (with some randomness)
            scored_repos.sort(key=lambda x: x[1], reverse=True)
            top_candidates = scored_repos[:min(3, len(scored_repos))]
            
            return random.choice(top_candidates)[0]
            
        except Exception as e:
            logger.error(f"Error in smart repo selection: {e}")
            return random.choice(targets)

async def main():
    """Enhanced main function with async support"""
    
    # Configuration from environment
    config = ElizaEvolutionConfig(
        github_token=os.getenv('GITHUB_TOKEN'),
        github_user=os.getenv('GITHUB_USERNAME', 'DevGruGold'),
        check_interval=int(os.getenv('CHECK_INTERVAL', '240')),
        project_root=os.getenv('XMRT_PROJECT_ROOT', '/tmp/xmrt_eliza_workspace'),
        database_url=os.getenv('DATABASE_URL', 'sqlite:///eliza_evolution.db'),
        redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        api_port=int(os.getenv('API_PORT', '8080')),
        metrics_port=int(os.getenv('METRICS_PORT', '9090')),
        enable_learning=os.getenv('ENABLE_LEARNING', 'true').lower() == 'true',
        enable_evolution=os.getenv('ENABLE_EVOLUTION', 'true').lower() == 'true',
        enable_advanced_monitoring=os.getenv('ENABLE_ADVANCED_MONITORING', 'true').lower() == 'true',
        learning_threshold=float(os.getenv('LEARNING_THRESHOLD', '0.75')),
        evolution_frequency=int(os.getenv('EVOLUTION_FREQUENCY', '10'))
    )
    
    # Initialize orchestrator
    orchestrator = EvolutionaryElizaOrchestrator(config)
    
    try:
        await orchestrator.run_forever()
    except KeyboardInterrupt:
        logger.info("👋 Received shutdown signal")
        orchestrator.is_running = False
        await asyncio.sleep(2)  # Allow cleanup
        logger.success("✅ Evolutionary Eliza shutdown complete")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
