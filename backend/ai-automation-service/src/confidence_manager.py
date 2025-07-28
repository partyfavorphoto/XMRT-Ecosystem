#!/usr/bin/env python3
"""
Dynamic Confidence Manager for Autonomous Eliza
Implements adaptive confidence thresholds based on historical performance
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import statistics
import redis
import numpy as np

from autonomous_eliza import DecisionLevel, AgentCapability

@dataclass
class DecisionOutcome:
    """Record of a decision outcome for learning"""
    decision_id: str
    decision_level: DecisionLevel
    capability: AgentCapability
    confidence_score: float
    success: bool
    timestamp: datetime
    context: Dict[str, Any]
    feedback_score: Optional[float] = None

class ConfidenceManager:
    """
    Manages dynamic confidence adjustment based on historical performance
    Tracks success rates and adapts thresholds for optimal autonomous operation
    """
    
    def __init__(self, memory_api_client=None, redis_host='localhost', redis_port=6379):
        self.logger = logging.getLogger(__name__)
        self.memory_api_client = memory_api_client
        
        # Redis connection for fast access to recent outcomes
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=1, decode_responses=True)
            self.redis_client.ping()
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}. Using in-memory storage.")
            self.redis_client = None
        
        # Initial confidence thresholds
        self.confidence_thresholds = {
            DecisionLevel.AUTONOMOUS: 0.85,
            DecisionLevel.ADVISORY: 0.60,
            DecisionLevel.EMERGENCY: 0.95
        }
        
        # Capability-specific thresholds
        self.capability_thresholds = {
            AgentCapability.GOVERNANCE: {
                DecisionLevel.AUTONOMOUS: 0.90,
                DecisionLevel.ADVISORY: 0.70,
                DecisionLevel.EMERGENCY: 0.98
            },
            AgentCapability.TREASURY: {
                DecisionLevel.AUTONOMOUS: 0.88,
                DecisionLevel.ADVISORY: 0.65,
                DecisionLevel.EMERGENCY: 0.96
            },
            AgentCapability.SECURITY: {
                DecisionLevel.AUTONOMOUS: 0.92,
                DecisionLevel.ADVISORY: 0.75,
                DecisionLevel.EMERGENCY: 0.99
            },
            AgentCapability.COMMUNITY: {
                DecisionLevel.AUTONOMOUS: 0.80,
                DecisionLevel.ADVISORY: 0.55,
                DecisionLevel.EMERGENCY: 0.90
            },
            AgentCapability.ANALYTICS: {
                DecisionLevel.AUTONOMOUS: 0.75,
                DecisionLevel.ADVISORY: 0.50,
                DecisionLevel.EMERGENCY: 0.85
            },
            AgentCapability.CROSS_CHAIN: {
                DecisionLevel.AUTONOMOUS: 0.87,
                DecisionLevel.ADVISORY: 0.68,
                DecisionLevel.EMERGENCY: 0.97
            },
            AgentCapability.DEPLOYMENT: {
                DecisionLevel.AUTONOMOUS: 0.93,
                DecisionLevel.ADVISORY: 0.78,
                DecisionLevel.EMERGENCY: 0.99
            }
        }
        
        # Learning parameters
        self.learning_config = {
            "window_size": 100,
            "min_samples": 10,
            "adjustment_rate": 0.01,
            "max_adjustment": 0.1,
            "success_target": 0.85,
            "confidence_decay": 0.95,
            "adaptation_speed": {
                DecisionLevel.AUTONOMOUS: 0.02,
                DecisionLevel.ADVISORY: 0.015,
                DecisionLevel.EMERGENCY: 0.005
            }
        }
        
        self.performance_history = {}
        self.last_adjustment = {}
        
        self.logger.info("🧠 ConfidenceManager initialized with adaptive thresholds")
    
    def get_threshold(self, decision_level: DecisionLevel, capability: AgentCapability = None) -> float:
        """Get the current confidence threshold for a decision level and capability"""
        if capability and capability in self.capability_thresholds:
            return self.capability_thresholds[capability].get(decision_level, 
                                                            self.confidence_thresholds[decision_level])
        return self.confidence_thresholds.get(decision_level, 0.75)
    
    def record_decision_outcome(self, decision_id: str, decision_level: DecisionLevel, 
                              capability: AgentCapability, confidence_score: float, 
                              success: bool, context: Dict[str, Any] = None,
                              feedback_score: float = None):
        """Record the outcome of a decision for learning"""
        outcome = DecisionOutcome(
            decision_id=decision_id,
            decision_level=decision_level,
            capability=capability,
            confidence_score=confidence_score,
            success=success,
            timestamp=datetime.now(),
            context=context or {},
            feedback_score=feedback_score
        )
        
        # Store in Redis for fast access
        if self.redis_client:
            key = f"outcome:{capability.value}:{decision_level.value}:{decision_id}"
            self.redis_client.setex(
                key, 
                timedelta(days=30).total_seconds(),
                json.dumps({
                    "decision_id": outcome.decision_id,
                    "decision_level": outcome.decision_level.value,
                    "capability": outcome.capability.value,
                    "confidence_score": outcome.confidence_score,
                    "success": outcome.success,
                    "timestamp": outcome.timestamp.isoformat(),
                    "context": outcome.context,
                    "feedback_score": outcome.feedback_score
                })
            )
        
        # Store in memory API for long-term persistence
        if self.memory_api_client:
            try:
                self.memory_api_client.store(
                    memory_type="decision_outcome",
                    content=f"Decision {decision_id} for {capability.value} at {decision_level.value} level: {'Success' if success else 'Failure'}",
                    timestamp=outcome.timestamp.isoformat(),
                    metadata={
                        "decision_id": decision_id,
                        "decision_level": decision_level.value,
                        "capability": capability.value,
                        "confidence_score": confidence_score,
                        "success": success,
                        "feedback_score": feedback_score,
                        "context": context
                    }
                )
            except Exception as e:
                self.logger.error(f"Failed to store outcome in memory API: {e}")
        
        self._update_performance_tracking(outcome)
        self._consider_threshold_adjustment(capability, decision_level)
        
        self.logger.info(f"📊 Recorded outcome: {capability.value}/{decision_level.value} - {'✅' if success else '❌'}")
    
    def update_threshold(self, decision_level: DecisionLevel, success_rate: float, capability: AgentCapability = None):
        """Update threshold based on success rate"""
        if success_rate > 0.95 and self.get_threshold(decision_level, capability) > 0.5:
            new_threshold = max(0.5, self.get_threshold(decision_level, capability) - 0.01)
        elif success_rate < 0.70 and self.get_threshold(decision_level, capability) < 0.99:
            new_threshold = min(0.99, self.get_threshold(decision_level, capability) + 0.02)
        else:
            return
        
        if capability:
            if capability not in self.capability_thresholds:
                self.capability_thresholds[capability] = {}
            self.capability_thresholds[capability][decision_level] = new_threshold
        else:
            self.confidence_thresholds[decision_level] = new_threshold
        
        self.logger.info(f"Updated {capability.value if capability else 'general'} {decision_level.value} threshold to: {new_threshold:.2f}")
    
    def _update_performance_tracking(self, outcome: DecisionOutcome):
        """Update internal performance tracking"""
        key = f"{outcome.capability.value}:{outcome.decision_level.value}"
        
        if key not in self.performance_history:
            self.performance_history[key] = []
        
        self.performance_history[key].append(outcome)
        
        # Keep only recent outcomes within window
        window_size = self.learning_config["window_size"]
        if len(self.performance_history[key]) > window_size:
            self.performance_history[key] = self.performance_history[key][-window_size:]
    
    def _consider_threshold_adjustment(self, capability: AgentCapability, decision_level: DecisionLevel):
        """Consider adjusting thresholds based on recent performance"""
        key = f"{capability.value}:{decision_level.value}"
        
        # Check if enough time has passed since last adjustment
        if key in self.last_adjustment:
            time_since_last = datetime.now() - self.last_adjustment[key]
            if time_since_last < timedelta(hours=1):
                return
        
        # Get recent outcomes
        recent_outcomes = self._get_recent_outcomes(capability, decision_level)
        
        if len(recent_outcomes) < self.learning_config["min_samples"]:
            return
        
        # Calculate success rate
        success_rate = sum(1 for outcome in recent_outcomes if outcome.success) / len(recent_outcomes)
        
        # Update threshold based on success rate
        self.update_threshold(decision_level, success_rate, capability)
        self.last_adjustment[key] = datetime.now()
    
    def _get_recent_outcomes(self, capability: AgentCapability, decision_level: DecisionLevel) -> List[DecisionOutcome]:
        """Get recent outcomes for a capability and decision level"""
        key = f"{capability.value}:{decision_level.value}"
        return self.performance_history.get(key, [])
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for analysis"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "current_thresholds": {},
            "performance_metrics": {}
        }
        
        # Current thresholds
        for cap, thresholds in self.capability_thresholds.items():
            summary["current_thresholds"][cap.value] = {
                level.value: threshold for level, threshold in thresholds.items()
            }
        
        # Performance metrics
        for key, outcomes in self.performance_history.items():
            if outcomes:
                success_rate = sum(1 for o in outcomes if o.success) / len(outcomes)
                avg_confidence = statistics.mean(o.confidence_score for o in outcomes)
                
                summary["performance_metrics"][key] = {
                    "success_rate": success_rate,
                    "average_confidence": avg_confidence,
                    "sample_count": len(outcomes)
                }
        
        return summary

