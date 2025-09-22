#!/usr/bin/env python3
"""
Enhanced Autonomous Learning System for XMRT-Ecosystem
Advanced ML algorithms, neural networks, and predictive modeling
"""

import numpy as np
import json
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque, defaultdict
import threading
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class LearningExperience:
    """Individual learning experience record"""
    timestamp: datetime
    context: Dict[str, Any]
    action_taken: str
    outcome: Dict[str, Any]
    reward: float
    confidence: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModelWeights:
    """Neural network model weights container"""
    layer_weights: List[np.ndarray]
    layer_biases: List[np.ndarray]
    last_updated: datetime = field(default_factory=datetime.now)
    performance_score: float = 0.0
    generation: int = 0

class OptimizationAlgorithm(ABC):
    """Abstract base class for optimization algorithms"""

    @abstractmethod
    def update(self, current_state: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Update algorithm state based on feedback"""
        pass

    @abstractmethod
    def get_next_parameters(self) -> Dict[str, Any]:
        """Get next set of parameters to try"""
        pass

class AdaptiveGradientDescent(OptimizationAlgorithm):
    """Advanced gradient descent with adaptive learning rates"""

    def __init__(self, learning_rate: float = 0.01, momentum: float = 0.9, 
                 adaptive_factor: float = 1.1, decay_factor: float = 0.95):
        self.learning_rate = learning_rate
        self.base_learning_rate = learning_rate
        self.momentum = momentum
        self.adaptive_factor = adaptive_factor
        self.decay_factor = decay_factor
        self.velocity = {}
        self.gradients_history = deque(maxlen=100)
        self.performance_history = deque(maxlen=50)

    def update(self, current_state: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Update gradient descent parameters"""
        performance = feedback.get('performance', 0.0)
        gradients = feedback.get('gradients', {})

        # Adapt learning rate based on performance trend
        self.performance_history.append(performance)
        if len(self.performance_history) >= 2:
            if self.performance_history[-1] > self.performance_history[-2]:
                # Performance improving - increase learning rate slightly
                self.learning_rate = min(self.learning_rate * self.adaptive_factor, 
                                       self.base_learning_rate * 2.0)
            else:
                # Performance declining - decrease learning rate
                self.learning_rate *= self.decay_factor

        # Update velocity for momentum
        for param_name, gradient in gradients.items():
            if param_name not in self.velocity:
                self.velocity[param_name] = 0
            self.velocity[param_name] = (self.momentum * self.velocity[param_name] + 
                                       self.learning_rate * gradient)

        self.gradients_history.append(gradients)

        return {
            'learning_rate': self.learning_rate,
            'velocity': dict(self.velocity),
            'momentum': self.momentum
        }

    def get_next_parameters(self) -> Dict[str, Any]:
        """Get next parameter update"""
        return {
            'learning_rate': self.learning_rate,
            'update_rule': 'momentum_gradient_descent',
            'velocity': dict(self.velocity)
        }

class BayesianOptimizer(OptimizationAlgorithm):
    """Bayesian optimization for hyperparameter tuning"""

    def __init__(self, parameter_space: Dict[str, Tuple[float, float]], 
                 acquisition_function: str = 'ucb'):
        self.parameter_space = parameter_space
        self.acquisition_function = acquisition_function
        self.observations = []
        self.parameter_history = []
        self.best_params = None
        self.best_score = float('-inf')

    def update(self, current_state: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Update Bayesian model with new observation"""
        parameters = current_state.get('parameters', {})
        performance = feedback.get('performance', 0.0)

        # Store observation
        self.observations.append(performance)
        self.parameter_history.append(parameters.copy())

        # Update best parameters
        if performance > self.best_score:
            self.best_score = performance
            self.best_params = parameters.copy()

        return {
            'best_score': self.best_score,
            'best_params': self.best_params,
            'observations_count': len(self.observations)
        }

    def get_next_parameters(self) -> Dict[str, Any]:
        """Suggest next parameters using acquisition function"""
        if len(self.observations) < 3:
            # Random exploration for initial points
            return self._random_sample()

        # Use acquisition function (simplified UCB)
        return self._ucb_acquisition()

    def _random_sample(self) -> Dict[str, Any]:
        """Random parameter sampling"""
        params = {}
        for param_name, (min_val, max_val) in self.parameter_space.items():
            params[param_name] = np.random.uniform(min_val, max_val)
        return params

    def _ucb_acquisition(self) -> Dict[str, Any]:
        """Upper Confidence Bound acquisition function"""
        # Simplified UCB implementation
        best_params = self.best_params.copy() if self.best_params else self._random_sample()

        # Add exploration noise
        for param_name in best_params:
            min_val, max_val = self.parameter_space[param_name]
            noise_scale = (max_val - min_val) * 0.1  # 10% noise
            best_params[param_name] += np.random.normal(0, noise_scale)
            # Clip to bounds
            best_params[param_name] = np.clip(best_params[param_name], min_val, max_val)

        return best_params

class EvolutionaryOptimizer(OptimizationAlgorithm):
    """Evolutionary algorithm for parameter optimization"""

    def __init__(self, population_size: int = 20, mutation_rate: float = 0.1,
                 crossover_rate: float = 0.7, elitism_rate: float = 0.2):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_rate = elitism_rate
        self.population = []
        self.fitness_scores = []
        self.generation = 0
        self.best_individual = None
        self.best_fitness = float('-inf')

    def update(self, current_state: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Update evolutionary algorithm state"""
        individual = current_state.get('parameters', {})
        fitness = feedback.get('performance', 0.0)

        # Add individual to population
        self.population.append(individual)
        self.fitness_scores.append(fitness)

        # Update best individual
        if fitness > self.best_fitness:
            self.best_fitness = fitness
            self.best_individual = individual.copy()

        # Evolve population when full
        if len(self.population) >= self.population_size:
            self._evolve_population()

        return {
            'generation': self.generation,
            'best_fitness': self.best_fitness,
            'population_size': len(self.population),
            'best_individual': self.best_individual
        }

    def _evolve_population(self):
        """Evolve the population to next generation"""
        # Selection, crossover, and mutation
        new_population = []
        new_fitness = []

        # Elitism - keep best individuals
        elite_count = int(self.population_size * self.elitism_rate)
        elite_indices = np.argsort(self.fitness_scores)[-elite_count:]

        for idx in elite_indices:
            new_population.append(self.population[idx].copy())
            new_fitness.append(self.fitness_scores[idx])

        # Generate rest through selection and crossover
        while len(new_population) < self.population_size:
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()

            if np.random.random() < self.crossover_rate:
                child = self._crossover(parent1, parent2)
            else:
                child = parent1.copy()

            child = self._mutate(child)
            new_population.append(child)
            new_fitness.append(0.0)  # Will be evaluated later

        self.population = new_population
        self.fitness_scores = new_fitness
        self.generation += 1

    def _tournament_selection(self) -> Dict[str, Any]:
        """Tournament selection for parent selection"""
        tournament_size = 3
        tournament_indices = np.random.choice(len(self.population), tournament_size, replace=False)
        best_idx = max(tournament_indices, key=lambda i: self.fitness_scores[i])
        return self.population[best_idx].copy()

    def _crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Dict[str, Any]:
        """Crossover operation between two parents"""
        child = {}
        for key in parent1:
            if np.random.random() < 0.5:
                child[key] = parent1[key]
            else:
                child[key] = parent2[key]
        return child

    def _mutate(self, individual: Dict[str, Any]) -> Dict[str, Any]:
        """Mutation operation"""
        for key, value in individual.items():
            if np.random.random() < self.mutation_rate:
                if isinstance(value, (int, float)):
                    # Gaussian mutation
                    noise = np.random.normal(0, abs(value) * 0.1)
                    individual[key] = value + noise
        return individual

    def get_next_parameters(self) -> Dict[str, Any]:
        """Get next parameters to evaluate"""
        if len(self.population) < self.population_size:
            # Return random individual for initial population
            return self._generate_random_individual()
        else:
            # Return individual from current population
            idx = len([f for f in self.fitness_scores if f > 0])
            if idx < len(self.population):
                return self.population[idx]
            else:
                return self._generate_random_individual()

    def _generate_random_individual(self) -> Dict[str, Any]:
        """Generate random individual"""
        # Placeholder - would be based on parameter space
        return {
            'learning_rate': np.random.uniform(0.001, 0.1),
            'batch_size': np.random.randint(16, 128),
            'hidden_units': np.random.randint(64, 512)
        }

class ReinforcementLearningAgent:
    """Q-learning based reinforcement learning agent"""

    def __init__(self, state_space_size: int = 1000, action_space_size: int = 10,
                 learning_rate: float = 0.1, discount_factor: float = 0.95,
                 epsilon: float = 0.1, epsilon_decay: float = 0.995):
        self.state_space_size = state_space_size
        self.action_space_size = action_space_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.q_table = np.zeros((state_space_size, action_space_size))
        self.experience_buffer = deque(maxlen=10000)
        self.total_episodes = 0

    def get_state_hash(self, state: Dict[str, Any]) -> int:
        """Convert state dictionary to hash for Q-table indexing"""
        # Simple hash function - in practice would use more sophisticated encoding
        state_str = str(sorted(state.items()))
        return hash(state_str) % self.state_space_size

    def select_action(self, state: Dict[str, Any]) -> int:
        """Select action using epsilon-greedy policy"""
        state_hash = self.get_state_hash(state)

        if np.random.random() < self.epsilon:
            # Exploration
            return np.random.randint(0, self.action_space_size)
        else:
            # Exploitation
            return np.argmax(self.q_table[state_hash])

    def update_q_value(self, state: Dict[str, Any], action: int, reward: float,
                      next_state: Dict[str, Any], done: bool):
        """Update Q-value using Q-learning update rule"""
        state_hash = self.get_state_hash(state)
        next_state_hash = self.get_state_hash(next_state)

        if done:
            target = reward
        else:
            target = reward + self.discount_factor * np.max(self.q_table[next_state_hash])

        current_q = self.q_table[state_hash, action]
        self.q_table[state_hash, action] += self.learning_rate * (target - current_q)

        # Store experience
        experience = {
            'state': state,
            'action': action,
            'reward': reward,
            'next_state': next_state,
            'done': done,
            'timestamp': datetime.now()
        }
        self.experience_buffer.append(experience)

        # Decay epsilon
        self.epsilon = max(0.01, self.epsilon * self.epsilon_decay)

    def get_policy_strength(self) -> float:
        """Calculate policy strength (confidence in learned policy)"""
        # Calculate variance in Q-values as measure of policy certainty
        q_variance = np.var(self.q_table)
        max_q = np.max(self.q_table)

        if max_q == 0:
            return 0.0

        # Normalize variance by maximum Q-value
        policy_strength = min(1.0, q_variance / max_q)
        return policy_strength

class NeuralArchitectureSearch:
    """Neural Architecture Search for optimal network design"""

    def __init__(self, max_layers: int = 5, max_units: int = 512):
        self.max_layers = max_layers
        self.max_units = max_units
        self.architecture_history = []
        self.performance_history = []
        self.best_architecture = None
        self.best_performance = float('-inf')

    def generate_architecture(self) -> Dict[str, Any]:
        """Generate a neural network architecture"""
        num_layers = np.random.randint(1, self.max_layers + 1)
        architecture = {
            'layers': [],
            'activation_functions': [],
            'dropout_rates': []
        }

        for i in range(num_layers):
            # Layer size
            if i == 0:  # Input layer
                layer_size = np.random.randint(64, self.max_units)
            else:
                # Gradually decrease size
                prev_size = architecture['layers'][-1]
                layer_size = max(32, np.random.randint(prev_size // 2, prev_size))

            architecture['layers'].append(layer_size)

            # Activation function
            activations = ['relu', 'tanh', 'sigmoid', 'leaky_relu']
            architecture['activation_functions'].append(np.random.choice(activations))

            # Dropout rate
            dropout_rate = np.random.uniform(0.0, 0.5)
            architecture['dropout_rates'].append(dropout_rate)

        return architecture

    def evaluate_architecture(self, architecture: Dict[str, Any], 
                            performance_score: float):
        """Evaluate and record architecture performance"""
        self.architecture_history.append(architecture)
        self.performance_history.append(performance_score)

        if performance_score > self.best_performance:
            self.best_performance = performance_score
            self.best_architecture = architecture.copy()

    def get_optimized_architecture(self) -> Dict[str, Any]:
        """Get architecture optimized based on historical performance"""
        if not self.best_architecture:
            return self.generate_architecture()

        # Create variation of best architecture
        optimized = self.best_architecture.copy()

        # Small random modifications
        if np.random.random() < 0.3:  # 30% chance to modify
            layer_idx = np.random.randint(0, len(optimized['layers']))

            # Modify layer size
            current_size = optimized['layers'][layer_idx]
            variation = np.random.randint(-32, 33)
            new_size = max(32, min(self.max_units, current_size + variation))
            optimized['layers'][layer_idx] = new_size

            # Modify dropout rate
            current_dropout = optimized['dropout_rates'][layer_idx]
            variation = np.random.uniform(-0.1, 0.1)
            new_dropout = max(0.0, min(0.5, current_dropout + variation))
            optimized['dropout_rates'][layer_idx] = new_dropout

        return optimized

class EnhancedAutonomousLearningCore:
    """Enhanced autonomous learning system with advanced algorithms"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # Initialize optimization algorithms
        self.gradient_optimizer = AdaptiveGradientDescent(
            learning_rate=self.config.get('learning_rate', 0.01)
        )

        parameter_space = {
            'learning_rate': (0.001, 0.1),
            'batch_size': (16, 128),
            'hidden_units': (64, 512)
        }
        self.bayesian_optimizer = BayesianOptimizer(parameter_space)
        self.evolutionary_optimizer = EvolutionaryOptimizer()

        # Initialize RL agent
        self.rl_agent = ReinforcementLearningAgent()

        # Initialize neural architecture search
        self.nas = NeuralArchitectureSearch()

        # Learning history and metrics
        self.learning_experiences = deque(maxlen=10000)
        self.performance_metrics = defaultdict(list)
        self.model_weights_history = deque(maxlen=100)

        # Current learning state
        self.current_optimizer = 'gradient'  # 'gradient', 'bayesian', 'evolutionary'
        self.learning_iteration = 0
        self.last_performance = 0.0

        # Adaptive learning parameters
        self.adaptation_threshold = 0.05  # Performance change threshold for adaptation
        self.optimizer_switch_cooldown = 10  # Iterations to wait before switching optimizers
        self.last_optimizer_switch = 0

        logger.info("Enhanced Autonomous Learning Core initialized")

    def learn_from_experience(self, experience: LearningExperience) -> Dict[str, Any]:
        """Process and learn from a new experience"""
        try:
            self.learning_experiences.append(experience)

            # Update current performance metrics
            self._update_performance_metrics(experience)

            # Determine if adaptation is needed
            adaptation_result = self._evaluate_adaptation_need()

            # Apply learning updates
            learning_result = self._apply_learning_updates(experience)

            # Update RL agent
            self._update_rl_agent(experience)

            # Neural architecture optimization
            architecture_result = self._optimize_architecture(experience)

            result = {
                'learning_iteration': self.learning_iteration,
                'performance_improvement': learning_result.get('performance_improvement', 0.0),
                'adaptation_applied': adaptation_result.get('adapted', False),
                'current_optimizer': self.current_optimizer,
                'rl_policy_strength': self.rl_agent.get_policy_strength(),
                'architecture_optimized': architecture_result.get('optimized', False),
                'confidence': experience.confidence,
                'timestamp': experience.timestamp.isoformat()
            }

            self.learning_iteration += 1
            logger.info(f"Learning iteration {self.learning_iteration} completed")

            return result

        except Exception as e:
            logger.error(f"Learning from experience failed: {e}")
            return {'error': str(e), 'success': False}

    def _update_performance_metrics(self, experience: LearningExperience):
        """Update performance tracking metrics"""
        performance = experience.outcome.get('performance', 0.0)
        self.performance_metrics['overall'].append({
            'value': performance,
            'timestamp': experience.timestamp,
            'context': experience.context.get('type', 'unknown')
        })

        # Context-specific metrics
        context_type = experience.context.get('type', 'general')
        self.performance_metrics[context_type].append(performance)

        # Keep only recent metrics
        for metric_type in self.performance_metrics:
            if len(self.performance_metrics[metric_type]) > 1000:
                self.performance_metrics[metric_type] = self.performance_metrics[metric_type][-1000:]

    def _evaluate_adaptation_need(self) -> Dict[str, Any]:
        """Evaluate if learning adaptation is needed"""
        if len(self.performance_metrics['overall']) < 10:
            return {'adapted': False, 'reason': 'insufficient_data'}

        recent_performances = [m['value'] for m in self.performance_metrics['overall'][-10:]]
        avg_recent = np.mean(recent_performances)

        # Compare with historical average
        if len(self.performance_metrics['overall']) >= 50:
            historical_performances = [m['value'] for m in self.performance_metrics['overall'][-50:-10]]
            avg_historical = np.mean(historical_performances)

            performance_change = avg_recent - avg_historical

            # Check if significant performance change
            if abs(performance_change) > self.adaptation_threshold:
                if (self.learning_iteration - self.last_optimizer_switch) > self.optimizer_switch_cooldown:
                    return self._adapt_learning_strategy(performance_change)

        return {'adapted': False, 'reason': 'no_adaptation_needed'}

    def _adapt_learning_strategy(self, performance_change: float) -> Dict[str, Any]:
        """Adapt learning strategy based on performance trends"""
        old_optimizer = self.current_optimizer

        if performance_change < -self.adaptation_threshold:
            # Performance declining - switch to more exploratory optimizer
            if self.current_optimizer == 'gradient':
                self.current_optimizer = 'bayesian'
            elif self.current_optimizer == 'bayesian':
                self.current_optimizer = 'evolutionary'
            else:
                self.current_optimizer = 'gradient'
        elif performance_change > self.adaptation_threshold:
            # Performance improving - continue with current or switch to exploitation
            if self.current_optimizer == 'evolutionary':
                self.current_optimizer = 'gradient'

        self.last_optimizer_switch = self.learning_iteration

        logger.info(f"Adapted learning strategy: {old_optimizer} -> {self.current_optimizer}")

        return {
            'adapted': True,
            'old_optimizer': old_optimizer,
            'new_optimizer': self.current_optimizer,
            'performance_change': performance_change
        }

    def _apply_learning_updates(self, experience: LearningExperience) -> Dict[str, Any]:
        """Apply learning updates using current optimizer"""
        current_state = {
            'parameters': experience.context.get('parameters', {}),
            'performance': experience.outcome.get('performance', 0.0)
        }

        feedback = {
            'performance': experience.outcome.get('performance', 0.0),
            'reward': experience.reward,
            'gradients': experience.outcome.get('gradients', {}),
            'confidence': experience.confidence
        }

        try:
            if self.current_optimizer == 'gradient':
                update_result = self.gradient_optimizer.update(current_state, feedback)
            elif self.current_optimizer == 'bayesian':
                update_result = self.bayesian_optimizer.update(current_state, feedback)
            elif self.current_optimizer == 'evolutionary':
                update_result = self.evolutionary_optimizer.update(current_state, feedback)
            else:
                update_result = {'error': 'unknown_optimizer'}

            # Calculate performance improvement
            current_performance = feedback['performance']
            performance_improvement = current_performance - self.last_performance
            self.last_performance = current_performance

            update_result['performance_improvement'] = performance_improvement

            return update_result

        except Exception as e:
            logger.error(f"Learning update failed: {e}")
            return {'error': str(e)}

    def _update_rl_agent(self, experience: LearningExperience):
        """Update reinforcement learning agent"""
        try:
            # Convert experience to RL format
            state = experience.context
            action = hash(experience.action_taken) % self.rl_agent.action_space_size
            reward = experience.reward
            next_state = experience.outcome.get('next_state', {})
            done = experience.outcome.get('episode_done', False)

            self.rl_agent.update_q_value(state, action, reward, next_state, done)

        except Exception as e:
            logger.error(f"RL agent update failed: {e}")

    def _optimize_architecture(self, experience: LearningExperience) -> Dict[str, Any]:
        """Optimize neural architecture based on performance"""
        try:
            performance = experience.outcome.get('performance', 0.0)
            current_architecture = experience.context.get('architecture')

            if current_architecture:
                self.nas.evaluate_architecture(current_architecture, performance)
                return {'optimized': True, 'performance': performance}
            else:
                # Generate new architecture suggestion
                suggested_architecture = self.nas.get_optimized_architecture()
                return {
                    'optimized': True,
                    'suggested_architecture': suggested_architecture,
                    'performance': performance
                }

        except Exception as e:
            logger.error(f"Architecture optimization failed: {e}")
            return {'optimized': False, 'error': str(e)}

    def get_next_parameters(self) -> Dict[str, Any]:
        """Get next parameters to try based on current optimizer"""
        try:
            if self.current_optimizer == 'gradient':
                return self.gradient_optimizer.get_next_parameters()
            elif self.current_optimizer == 'bayesian':
                return self.bayesian_optimizer.get_next_parameters()
            elif self.current_optimizer == 'evolutionary':
                return self.evolutionary_optimizer.get_next_parameters()
            else:
                return {}
        except Exception as e:
            logger.error(f"Parameter generation failed: {e}")
            return {}

    def get_learning_analytics(self) -> Dict[str, Any]:
        """Get comprehensive learning analytics"""
        try:
            recent_experiences = list(self.learning_experiences)[-100:]  # Last 100 experiences

            # Performance trends
            performance_values = [exp.outcome.get('performance', 0.0) for exp in recent_experiences]
            confidence_values = [exp.confidence for exp in recent_experiences]

            # Optimizer effectiveness
            optimizer_performance = defaultdict(list)
            for exp in recent_experiences:
                if hasattr(exp, 'optimizer_used'):
                    optimizer_performance[exp.optimizer_used].append(exp.outcome.get('performance', 0.0))

            analytics = {
                'total_experiences': len(self.learning_experiences),
                'learning_iteration': self.learning_iteration,
                'current_optimizer': self.current_optimizer,
                'performance_trend': {
                    'mean': np.mean(performance_values) if performance_values else 0.0,
                    'std': np.std(performance_values) if performance_values else 0.0,
                    'min': np.min(performance_values) if performance_values else 0.0,
                    'max': np.max(performance_values) if performance_values else 0.0,
                    'recent_trend': np.polyfit(range(len(performance_values)), performance_values, 1)[0] if len(performance_values) > 1 else 0.0
                },
                'confidence_trend': {
                    'mean': np.mean(confidence_values) if confidence_values else 0.0,
                    'std': np.std(confidence_values) if confidence_values else 0.0
                },
                'rl_agent_stats': {
                    'policy_strength': self.rl_agent.get_policy_strength(),
                    'epsilon': self.rl_agent.epsilon,
                    'total_experiences': len(self.rl_agent.experience_buffer)
                },
                'optimizer_effectiveness': {
                    optimizer: {
                        'mean_performance': np.mean(performances),
                        'usage_count': len(performances)
                    } for optimizer, performances in optimizer_performance.items()
                },
                'architecture_optimization': {
                    'architectures_evaluated': len(self.nas.architecture_history),
                    'best_performance': self.nas.best_performance,
                    'best_architecture': self.nas.best_architecture
                }
            }

            return analytics

        except Exception as e:
            logger.error(f"Analytics generation failed: {e}")
            return {'error': str(e)}

    def save_learning_state(self, filepath: str) -> bool:
        """Save current learning state to file"""
        try:
            state = {
                'learning_iteration': self.learning_iteration,
                'current_optimizer': self.current_optimizer,
                'last_performance': self.last_performance,
                'experiences': [
                    {
                        'timestamp': exp.timestamp.isoformat(),
                        'context': exp.context,
                        'action_taken': exp.action_taken,
                        'outcome': exp.outcome,
                        'reward': exp.reward,
                        'confidence': exp.confidence
                    }
                    for exp in list(self.learning_experiences)[-1000:]  # Save last 1000 experiences
                ],
                'q_table': self.rl_agent.q_table.tolist(),
                'nas_history': {
                    'architectures': self.nas.architecture_history,
                    'performances': self.nas.performance_history,
                    'best_architecture': self.nas.best_architecture,
                    'best_performance': self.nas.best_performance
                }
            }

            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)

            logger.info(f"Learning state saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save learning state: {e}")
            return False

    def load_learning_state(self, filepath: str) -> bool:
        """Load learning state from file"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)

            self.learning_iteration = state.get('learning_iteration', 0)
            self.current_optimizer = state.get('current_optimizer', 'gradient')
            self.last_performance = state.get('last_performance', 0.0)

            # Restore experiences
            experiences_data = state.get('experiences', [])
            for exp_data in experiences_data:
                experience = LearningExperience(
                    timestamp=datetime.fromisoformat(exp_data['timestamp']),
                    context=exp_data['context'],
                    action_taken=exp_data['action_taken'],
                    outcome=exp_data['outcome'],
                    reward=exp_data['reward'],
                    confidence=exp_data['confidence']
                )
                self.learning_experiences.append(experience)

            # Restore RL agent state
            if 'q_table' in state:
                self.rl_agent.q_table = np.array(state['q_table'])

            # Restore NAS state
            nas_data = state.get('nas_history', {})
            self.nas.architecture_history = nas_data.get('architectures', [])
            self.nas.performance_history = nas_data.get('performances', [])
            self.nas.best_architecture = nas_data.get('best_architecture')
            self.nas.best_performance = nas_data.get('best_performance', float('-inf'))

            logger.info(f"Learning state loaded from {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to load learning state: {e}")
            return False

# Export function for integration
def get_enhanced_learning_core(config: Optional[Dict[str, Any]] = None) -> EnhancedAutonomousLearningCore:
    """Get instance of enhanced autonomous learning core"""
    return EnhancedAutonomousLearningCore(config)

# Integration function for existing system
def enhance_existing_autonomous_controller(existing_controller, learning_config: Optional[Dict[str, Any]] = None):
    """Enhance existing autonomous controller with advanced learning capabilities"""
    enhanced_learning_core = get_enhanced_learning_core(learning_config)

    # Add enhanced methods to existing controller
    if hasattr(existing_controller, 'learn_from_experiences'):
        existing_controller.enhanced_learning_core = enhanced_learning_core
        existing_controller.advanced_learn_from_experience = enhanced_learning_core.learn_from_experience
        existing_controller.get_optimized_parameters = enhanced_learning_core.get_next_parameters
        existing_controller.get_learning_analytics = enhanced_learning_core.get_learning_analytics
        existing_controller.save_learning_state = enhanced_learning_core.save_learning_state
        existing_controller.load_learning_state = enhanced_learning_core.load_learning_state

    logger.info("Enhanced autonomous learning capabilities added")
    return existing_controller
