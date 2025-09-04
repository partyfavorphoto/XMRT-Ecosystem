"""
Learning Optimizer for XMRT-Ecosystem - Advanced AI Optimization

Provides advanced optimization algorithms, hyperparameter tuning, and
performance enhancement for the autonomous AI learning systems.
"""

import os
import json
import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
import threading
from collections import defaultdict, deque

@dataclass
class OptimizationResult:
    """Optimization result data structure"""
    timestamp: datetime
    algorithm: str
    parameters: Dict[str, Any]
    performance_before: float
    performance_after: float
    improvement: float
    confidence: float

@dataclass
class LearningMetrics:
    """Learning metrics tracking"""
    timestamp: datetime
    accuracy: float
    loss: float
    convergence_rate: float
    efficiency_score: float
    adaptation_rate: float

class LearningOptimizer:
    """Advanced Learning Optimization System"""

    def __init__(self, config: Dict[str, Any], autonomous_controller=None, analytics_engine=None, logger=None):
        self.config = config
        self.autonomous_controller = autonomous_controller
        self.analytics_engine = analytics_engine
        self.logger = logger or logging.getLogger(__name__)

        # Optimization state
        self.optimization_history = deque(maxlen=1000)
        self.learning_metrics = deque(maxlen=5000)
        self.current_parameters = {}
        self.best_parameters = {}
        self.optimization_thread = None
        self.is_optimizing = False

        # Optimization algorithms
        self.algorithms = {
            'adaptive_gradient': self._adaptive_gradient_optimization,
            'bayesian_optimization': self._bayesian_optimization,
            'evolutionary_algorithm': self._evolutionary_optimization,
            'reinforcement_learning': self._reinforcement_optimization,
            'neural_architecture_search': self._neural_architecture_optimization
        }

        # Performance tracking
        self.performance_baseline = 0.0
        self.optimization_targets = {
            'accuracy': 0.95,
            'efficiency': 0.90,
            'convergence': 0.85,
            'adaptation': 0.80
        }

        self.logger.info("🎯 Learning Optimizer initialized")

    def start_optimization(self):
        """Start continuous learning optimization"""
        if self.is_optimizing:
            return

        self.is_optimizing = True
        self.optimization_thread = threading.Thread(target=self._optimization_loop, daemon=True)
        self.optimization_thread.start()
        self.logger.info("🚀 Continuous learning optimization started")

    def stop_optimization(self):
        """Stop learning optimization"""
        self.is_optimizing = False
        if self.optimization_thread:
            self.optimization_thread.join(timeout=10.0)
        self.logger.info("⏹️ Learning optimization stopped")

    def _optimization_loop(self):
        """Main optimization loop"""
        while self.is_optimizing:
            try:
                # Collect current performance metrics
                current_metrics = self._collect_learning_metrics()

                # Analyze performance trends
                optimization_needed = self._analyze_optimization_needs(current_metrics)

                if optimization_needed:
                    # Select optimization algorithm
                    algorithm = self._select_optimization_algorithm()

                    # Perform optimization
                    result = self._perform_optimization(algorithm, current_metrics)

                    if result:
                        self.optimization_history.append(result)
                        self._apply_optimization_result(result)
                        self.logger.info(f"✨ Optimization completed: {result.improvement:.3f} improvement")

                # Update learning parameters
                self._update_learning_parameters()

                # Sleep before next optimization cycle
                time.sleep(300)  # Optimize every 5 minutes

            except Exception as e:
                self.logger.error(f"Error in optimization loop: {e}")
                time.sleep(60)

    def _collect_learning_metrics(self) -> LearningMetrics:
        """Collect current learning system metrics"""
        try:
            # Get metrics from autonomous controller
            if self.autonomous_controller:
                controller_metrics = self.autonomous_controller.get_performance_metrics()
            else:
                controller_metrics = {}

            # Get analytics data
            if self.analytics_engine:
                analytics_metrics = self.analytics_engine.get_performance_metrics()
            else:
                analytics_metrics = {}

            # Create learning metrics
            metrics = LearningMetrics(
                timestamp=datetime.now(),
                accuracy=controller_metrics.get('accuracy', 0.85),
                loss=controller_metrics.get('loss', 0.15),
                convergence_rate=self._calculate_convergence_rate(),
                efficiency_score=analytics_metrics.get('avg_response_time', 1.0),
                adaptation_rate=self._calculate_adaptation_rate()
            )

            self.learning_metrics.append(metrics)
            return metrics

        except Exception as e:
            self.logger.error(f"Error collecting learning metrics: {e}")
            return LearningMetrics(
                timestamp=datetime.now(),
                accuracy=0.5,
                loss=0.5,
                convergence_rate=0.5,
                efficiency_score=0.5,
                adaptation_rate=0.5
            )

    def _analyze_optimization_needs(self, metrics: LearningMetrics) -> bool:
        """Analyze if optimization is needed"""
        # Check if performance is below targets
        performance_issues = []

        if metrics.accuracy < self.optimization_targets['accuracy']:
            performance_issues.append('accuracy')

        if metrics.efficiency_score < self.optimization_targets['efficiency']:
            performance_issues.append('efficiency')

        if metrics.convergence_rate < self.optimization_targets['convergence']:
            performance_issues.append('convergence')

        if metrics.adaptation_rate < self.optimization_targets['adaptation']:
            performance_issues.append('adaptation')

        # Check performance trends
        if len(self.learning_metrics) >= 10:
            recent_metrics = list(self.learning_metrics)[-10:]
            accuracy_trend = self._calculate_trend([m.accuracy for m in recent_metrics])

            if accuracy_trend < -0.01:  # Declining accuracy
                performance_issues.append('declining_accuracy')

        return len(performance_issues) > 0

    def _select_optimization_algorithm(self) -> str:
        """Select the best optimization algorithm for current situation"""
        # Simple selection based on current performance
        if len(self.learning_metrics) < 10:
            return 'adaptive_gradient'  # Start with simple optimization

        recent_metrics = list(self.learning_metrics)[-10:]
        avg_accuracy = np.mean([m.accuracy for m in recent_metrics])

        if avg_accuracy < 0.7:
            return 'evolutionary_algorithm'  # Use evolutionary for poor performance
        elif avg_accuracy < 0.85:
            return 'bayesian_optimization'  # Use Bayesian for medium performance
        else:
            return 'reinforcement_learning'  # Use RL for fine-tuning

    def _perform_optimization(self, algorithm: str, current_metrics: LearningMetrics) -> Optional[OptimizationResult]:
        """Perform optimization using specified algorithm"""
        try:
            self.logger.info(f"🔬 Starting {algorithm} optimization")

            # Get current performance baseline
            baseline_performance = current_metrics.accuracy

            # Run optimization algorithm
            optimization_func = self.algorithms.get(algorithm)
            if not optimization_func:
                self.logger.error(f"Unknown optimization algorithm: {algorithm}")
                return None

            new_parameters = optimization_func(current_metrics)

            if not new_parameters:
                return None

            # Simulate performance improvement (in real implementation, this would test the parameters)
            performance_improvement = self._simulate_performance_improvement(new_parameters, current_metrics)
            new_performance = baseline_performance + performance_improvement

            # Create optimization result
            result = OptimizationResult(
                timestamp=datetime.now(),
                algorithm=algorithm,
                parameters=new_parameters,
                performance_before=baseline_performance,
                performance_after=new_performance,
                improvement=performance_improvement,
                confidence=self._calculate_optimization_confidence(algorithm)
            )

            return result

        except Exception as e:
            self.logger.error(f"Error performing optimization: {e}")
            return None

    def _adaptive_gradient_optimization(self, metrics: LearningMetrics) -> Dict[str, Any]:
        """Adaptive gradient descent optimization"""
        current_lr = self.current_parameters.get('learning_rate', 0.01)

        # Adjust learning rate based on loss trends
        if len(self.learning_metrics) >= 5:
            recent_losses = [m.loss for m in list(self.learning_metrics)[-5:]]
            loss_trend = self._calculate_trend(recent_losses)

            if loss_trend > 0:  # Loss increasing
                new_lr = current_lr * 0.9  # Decrease learning rate
            elif loss_trend < -0.01:  # Loss decreasing fast
                new_lr = current_lr * 1.1  # Increase learning rate
            else:
                new_lr = current_lr  # Keep current rate
        else:
            new_lr = current_lr

        return {
            'learning_rate': max(0.001, min(0.1, new_lr)),
            'momentum': 0.9,
            'weight_decay': 0.0001,
            'optimization_method': 'adaptive_gradient'
        }

    def _bayesian_optimization(self, metrics: LearningMetrics) -> Dict[str, Any]:
        """Bayesian optimization for hyperparameters"""
        # Simplified Bayesian optimization
        # In real implementation, this would use libraries like scikit-optimize

        # Sample from parameter space
        learning_rate = np.random.uniform(0.001, 0.1)
        batch_size = np.random.choice([16, 32, 64, 128])
        hidden_size = np.random.choice([128, 256, 512, 1024])
        dropout_rate = np.random.uniform(0.1, 0.5)

        return {
            'learning_rate': learning_rate,
            'batch_size': batch_size,
            'hidden_size': hidden_size,
            'dropout_rate': dropout_rate,
            'optimization_method': 'bayesian'
        }

    def _evolutionary_optimization(self, metrics: LearningMetrics) -> Dict[str, Any]:
        """Evolutionary algorithm optimization"""
        # Simple evolutionary approach
        population_size = 10
        mutation_rate = 0.1

        # Generate population of parameter sets
        population = []
        for _ in range(population_size):
            params = {
                'learning_rate': np.random.uniform(0.001, 0.1),
                'num_layers': np.random.randint(2, 8),
                'layer_size': np.random.choice([64, 128, 256, 512]),
                'activation': np.random.choice(['relu', 'tanh', 'sigmoid']),
                'optimizer': np.random.choice(['adam', 'sgd', 'rmsprop'])
            }
            population.append(params)

        # Select best parameters (simplified selection)
        best_params = population[0]  # In real implementation, would evaluate each
        best_params['optimization_method'] = 'evolutionary'

        return best_params

    def _reinforcement_optimization(self, metrics: LearningMetrics) -> Dict[str, Any]:
        """Reinforcement learning-based optimization"""
        # Simplified RL optimization
        current_lr = self.current_parameters.get('learning_rate', 0.01)

        # Use performance as reward signal
        reward = metrics.accuracy - 0.5  # Normalized reward

        # Simple policy gradient update
        if reward > 0:
            lr_adjustment = 1.05  # Increase slightly if performing well
        else:
            lr_adjustment = 0.95  # Decrease if performing poorly

        new_lr = current_lr * lr_adjustment

        return {
            'learning_rate': max(0.001, min(0.1, new_lr)),
            'exploration_rate': max(0.01, 0.1 - metrics.accuracy * 0.1),
            'reward_signal': reward,
            'optimization_method': 'reinforcement_learning'
        }

    def _neural_architecture_optimization(self, metrics: LearningMetrics) -> Dict[str, Any]:
        """Neural architecture search optimization"""
        # Simplified NAS approach
        architectures = [
            {'layers': [128, 64, 32], 'activations': ['relu', 'relu', 'sigmoid']},
            {'layers': [256, 128, 64], 'activations': ['relu', 'tanh', 'sigmoid']},
            {'layers': [512, 256, 128, 64], 'activations': ['relu', 'relu', 'relu', 'sigmoid']},
            {'layers': [64, 128, 64], 'activations': ['tanh', 'relu', 'sigmoid']}
        ]

        # Select architecture based on current performance
        if metrics.accuracy < 0.7:
            selected_arch = architectures[2]  # Larger network
        else:
            selected_arch = architectures[1]  # Medium network

        selected_arch['optimization_method'] = 'neural_architecture_search'
        return selected_arch

    def _simulate_performance_improvement(self, parameters: Dict[str, Any], metrics: LearningMetrics) -> float:
        """Simulate performance improvement from new parameters"""
        # This is a simplified simulation - in real implementation, 
        # you would actually test the parameters

        base_improvement = 0.0

        # Learning rate impact
        lr = parameters.get('learning_rate', 0.01)
        if 0.005 <= lr <= 0.05:  # Optimal range
            base_improvement += 0.02

        # Architecture impact
        if 'layers' in parameters:
            num_layers = len(parameters['layers'])
            if 2 <= num_layers <= 4:  # Good depth
                base_improvement += 0.015

        # Optimization method impact
        method = parameters.get('optimization_method', '')
        method_bonuses = {
            'bayesian': 0.025,
            'evolutionary': 0.02,
            'reinforcement_learning': 0.03,
            'neural_architecture_search': 0.035
        }
        base_improvement += method_bonuses.get(method, 0.01)

        # Add some randomness
        noise = np.random.uniform(-0.01, 0.01)

        return max(0.0, base_improvement + noise)

    def _calculate_optimization_confidence(self, algorithm: str) -> float:
        """Calculate confidence in optimization result"""
        confidence_scores = {
            'adaptive_gradient': 0.8,
            'bayesian_optimization': 0.85,
            'evolutionary_algorithm': 0.75,
            'reinforcement_learning': 0.9,
            'neural_architecture_search': 0.95
        }

        base_confidence = confidence_scores.get(algorithm, 0.7)

        # Adjust based on historical performance
        if len(self.optimization_history) > 5:
            recent_improvements = [r.improvement for r in list(self.optimization_history)[-5:]]
            avg_improvement = np.mean(recent_improvements)

            if avg_improvement > 0.02:
                base_confidence += 0.1
            elif avg_improvement < 0:
                base_confidence -= 0.1

        return max(0.1, min(1.0, base_confidence))

    def _apply_optimization_result(self, result: OptimizationResult):
        """Apply optimization result to the system"""
        try:
            # Update current parameters
            self.current_parameters.update(result.parameters)

            # If this is the best result so far, save it
            if result.improvement > 0 and (
                not self.best_parameters or 
                result.performance_after > self.best_parameters.get('best_performance', 0)
            ):
                self.best_parameters = result.parameters.copy()
                self.best_parameters['best_performance'] = result.performance_after
                self.best_parameters['timestamp'] = result.timestamp

            # Apply to autonomous controller if available
            if self.autonomous_controller and hasattr(self.autonomous_controller, 'update_parameters'):
                self.autonomous_controller.update_parameters(result.parameters)

            self.logger.info(f"📊 Applied optimization: {result.algorithm} -> {result.improvement:.3f} improvement")

        except Exception as e:
            self.logger.error(f"Error applying optimization result: {e}")

    def _update_learning_parameters(self):
        """Update learning parameters based on current state"""
        # Implement parameter updates based on learning progress
        pass

    def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization status"""
        recent_results = list(self.optimization_history)[-10:] if self.optimization_history else []

        return {
            'is_optimizing': self.is_optimizing,
            'total_optimizations': len(self.optimization_history),
            'recent_optimizations': len(recent_results),
            'best_performance': self.best_parameters.get('best_performance', 0.0),
            'current_parameters': self.current_parameters.copy(),
            'recent_improvements': [r.improvement for r in recent_results],
            'avg_recent_improvement': np.mean([r.improvement for r in recent_results]) if recent_results else 0.0,
            'optimization_targets': self.optimization_targets,
            'last_optimization': recent_results[-1].timestamp.isoformat() if recent_results else None
        }

    def get_learning_trends(self) -> Dict[str, Any]:
        """Get learning performance trends"""
        if len(self.learning_metrics) < 10:
            return {'status': 'insufficient_data'}

        recent_metrics = list(self.learning_metrics)[-50:]

        return {
            'accuracy_trend': self._calculate_trend([m.accuracy for m in recent_metrics]),
            'loss_trend': self._calculate_trend([m.loss for m in recent_metrics]),
            'convergence_trend': self._calculate_trend([m.convergence_rate for m in recent_metrics]),
            'efficiency_trend': self._calculate_trend([m.efficiency_score for m in recent_metrics]),
            'current_accuracy': recent_metrics[-1].accuracy,
            'accuracy_improvement': recent_metrics[-1].accuracy - recent_metrics[0].accuracy,
            'stability_score': self._calculate_stability_score(recent_metrics)
        }

    def health_check(self) -> Dict[str, Any]:
        """Perform optimizer health check"""
        return {
            'status': 'active' if self.is_optimizing else 'inactive',
            'optimization_active': self.is_optimizing,
            'metrics_collected': len(self.learning_metrics),
            'optimizations_performed': len(self.optimization_history),
            'current_performance': self.learning_metrics[-1].accuracy if self.learning_metrics else 0.0,
            'best_performance': self.best_parameters.get('best_performance', 0.0),
            'last_update': datetime.now().isoformat()
        }

    # Helper methods
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate linear trend from values"""
        if len(values) < 2:
            return 0.0

        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, 1)
        return coeffs[0]

    def _calculate_convergence_rate(self) -> float:
        """Calculate learning convergence rate"""
        if len(self.learning_metrics) < 5:
            return 0.5

        recent_accuracies = [m.accuracy for m in list(self.learning_metrics)[-10:]]
        variance = np.var(recent_accuracies)

        # Lower variance = higher convergence
        convergence = max(0.0, min(1.0, 1.0 - variance * 10))
        return convergence

    def _calculate_adaptation_rate(self) -> float:
        """Calculate system adaptation rate"""
        # Simplified calculation based on parameter changes
        if not self.optimization_history:
            return 0.5

        recent_optimizations = list(self.optimization_history)[-5:]
        avg_improvement = np.mean([opt.improvement for opt in recent_optimizations])

        # Higher improvements = better adaptation
        adaptation = max(0.0, min(1.0, 0.5 + avg_improvement * 10))
        return adaptation

    def _calculate_stability_score(self, metrics: List[LearningMetrics]) -> float:
        """Calculate learning stability score"""
        accuracies = [m.accuracy for m in metrics]
        variance = np.var(accuracies)

        # Lower variance = higher stability
        stability = max(0.0, min(1.0, 1.0 - variance * 5))
        return stability
