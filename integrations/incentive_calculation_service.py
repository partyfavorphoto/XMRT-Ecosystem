"""
Incentive Calculation Service - XMRT Token Reward System
Calculates XMRT token rewards for successful utility building and learning activities.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import math

@dataclass
class RewardMetrics:
    """Metrics used for reward calculation"""
    base_reward: float
    quality_multiplier: float
    complexity_multiplier: float
    innovation_bonus: float
    consistency_bonus: float
    total_reward: float
    breakdown: Dict[str, float]

class IncentiveCalculationService:
    """
    Service for calculating XMRT token rewards based on learning activities

    Reward Factors:
    - Base reward for successful utility creation
    - Quality multiplier based on code quality metrics
    - Complexity multiplier for challenging repositories
    - Innovation bonus for novel approaches
    - Consistency bonus for regular learning activities
    - Community impact factor
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Reward configuration
        self.reward_config = {
            'base_reward': 50.0,  # Base XMRT tokens per successful utility
            'max_reward_per_cycle': 1000.0,  # Maximum tokens per learning cycle
            'quality_weight': 0.3,
            'complexity_weight': 0.25,
            'innovation_weight': 0.2,
            'consistency_weight': 0.15,
            'community_weight': 0.1,

            # Quality thresholds
            'min_quality_threshold': 0.5,
            'high_quality_threshold': 0.8,
            'excellent_quality_threshold': 0.9,

            # Complexity bonuses
            'high_complexity_bonus': 1.5,
            'moderate_complexity_bonus': 1.2,
            'low_complexity_penalty': 0.8,

            # Innovation bonuses
            'first_time_repo_bonus': 2.0,
            'new_pattern_bonus': 1.5,
            'novel_approach_bonus': 1.3,

            # Consistency bonuses
            'daily_streak_bonus': 0.1,  # Per consecutive day
            'weekly_consistency_bonus': 0.5,
            'monthly_achievement_bonus': 2.0
        }

        # Historical data for pattern recognition
        self.historical_patterns: Dict[str, List[Any]] = {
            'repo_types_built': [],
            'quality_trends': [],
            'innovation_patterns': [],
            'consistency_metrics': []
        }

        # Reputation tracking
        self.reputation_score = 0.0
        self.total_utilities_created = 0
        self.total_tokens_earned = 0.0
        self.learning_streak_days = 0

    async def calculate_cycle_rewards(self, build_results: List[Any], 
                                    current_cycle: Any) -> Dict[str, float]:
        """
        Calculate total rewards for a learning cycle

        Args:
            build_results: List of UtilityResult objects from utility building
            current_cycle: LearningCycle object with cycle information

        Returns:
            Dictionary with reward breakdown and totals
        """
        try:
            total_reward = 0.0
            detailed_breakdown = {}

            # Process each successful utility
            successful_builds = [r for r in build_results if r.success]

            if not successful_builds:
                return {
                    'total_tokens': 0.0,
                    'quality_score': 0.0,
                    'breakdown': {'no_successful_builds': 0.0}
                }

            for build in successful_builds:
                reward_metrics = await self._calculate_single_utility_reward(build)
                total_reward += reward_metrics.total_reward

                detailed_breakdown[build.utility_name] = {
                    'base_reward': reward_metrics.base_reward,
                    'quality_multiplier': reward_metrics.quality_multiplier,
                    'complexity_multiplier': reward_metrics.complexity_multiplier,
                    'innovation_bonus': reward_metrics.innovation_bonus,
                    'consistency_bonus': reward_metrics.consistency_bonus,
                    'total': reward_metrics.total_reward
                }

            # Apply cycle-level bonuses
            cycle_bonuses = await self._calculate_cycle_bonuses(
                build_results, current_cycle
            )
            total_reward += cycle_bonuses['total_bonus']
            detailed_breakdown['cycle_bonuses'] = cycle_bonuses

            # Apply maximum reward cap
            if total_reward > self.reward_config['max_reward_per_cycle']:
                cap_reduction = total_reward - self.reward_config['max_reward_per_cycle']
                total_reward = self.reward_config['max_reward_per_cycle']
                detailed_breakdown['cap_reduction'] = cap_reduction

            # Calculate overall quality score for the cycle
            avg_quality = sum(
                build.quality_metrics.get('overall_score', 0.0) 
                for build in successful_builds
            ) / len(successful_builds)

            # Update historical tracking
            await self._update_historical_data(build_results, total_reward)

            return {
                'total_tokens': round(total_reward, 2),
                'quality_score': round(avg_quality, 3),
                'breakdown': detailed_breakdown,
                'utilities_rewarded': len(successful_builds),
                'reputation_impact': await self._calculate_reputation_impact(total_reward)
            }

        except Exception as e:
            self.logger.error(f"Reward calculation failed: {e}")
            return {
                'total_tokens': 0.0,
                'quality_score': 0.0,
                'breakdown': {'error': str(e)}
            }

    async def _calculate_single_utility_reward(self, build_result: Any) -> RewardMetrics:
        """Calculate reward for a single utility"""
        try:
            # Base reward
            base_reward = self.reward_config['base_reward']

            # Quality multiplier
            quality_score = build_result.quality_metrics.get('overall_score', 0.5)
            quality_multiplier = await self._calculate_quality_multiplier(quality_score)

            # Complexity multiplier  
            complexity_multiplier = await self._calculate_complexity_multiplier(
                build_result.repository
            )

            # Innovation bonus
            innovation_bonus = await self._calculate_innovation_bonus(build_result)

            # Consistency bonus
            consistency_bonus = await self._calculate_consistency_bonus()

            # Calculate total reward
            core_reward = base_reward * quality_multiplier * complexity_multiplier
            bonus_reward = innovation_bonus + consistency_bonus
            total_reward = core_reward + bonus_reward

            # Ensure minimum quality threshold
            if quality_score < self.reward_config['min_quality_threshold']:
                total_reward *= 0.5  # 50% penalty for low quality

            return RewardMetrics(
                base_reward=base_reward,
                quality_multiplier=quality_multiplier,
                complexity_multiplier=complexity_multiplier,
                innovation_bonus=innovation_bonus,
                consistency_bonus=consistency_bonus,
                total_reward=max(total_reward, 0.0),
                breakdown={
                    'core_reward': core_reward,
                    'bonus_reward': bonus_reward,
                    'quality_penalty': 0.5 if quality_score < self.reward_config['min_quality_threshold'] else 1.0
                }
            )

        except Exception as e:
            self.logger.error(f"Single utility reward calculation failed: {e}")
            return RewardMetrics(
                base_reward=0.0,
                quality_multiplier=1.0,
                complexity_multiplier=1.0,
                innovation_bonus=0.0,
                consistency_bonus=0.0,
                total_reward=0.0,
                breakdown={'error': str(e)}
            )

    async def _calculate_quality_multiplier(self, quality_score: float) -> float:
        """Calculate quality-based reward multiplier"""
        if quality_score >= self.reward_config['excellent_quality_threshold']:
            return 2.0  # Excellent quality bonus
        elif quality_score >= self.reward_config['high_quality_threshold']:
            return 1.5  # High quality bonus
        elif quality_score >= self.reward_config['min_quality_threshold']:
            # Linear interpolation between 1.0 and 1.5
            return 1.0 + (quality_score - self.reward_config['min_quality_threshold']) / 0.3
        else:
            return 0.5  # Low quality penalty

    async def _calculate_complexity_multiplier(self, repository_name: str) -> float:
        """Calculate complexity-based reward multiplier"""
        # This would integrate with repository complexity analysis
        # For now, use heuristics based on repository name and type

        complexity_indicators = {
            'high': ['protocol', 'blockchain', 'consensus', 'cryptography', 'vm'],
            'moderate': ['api', 'service', 'integration', 'utility', 'tool'],
            'low': ['example', 'demo', 'test', 'simple', 'basic']
        }

        repo_lower = repository_name.lower()

        # Check for complexity indicators
        for indicator in complexity_indicators['high']:
            if indicator in repo_lower:
                return self.reward_config['high_complexity_bonus']

        for indicator in complexity_indicators['moderate']:
            if indicator in repo_lower:
                return self.reward_config['moderate_complexity_bonus']

        for indicator in complexity_indicators['low']:
            if indicator in repo_lower:
                return self.reward_config['low_complexity_penalty']

        return 1.0  # Default multiplier

    async def _calculate_innovation_bonus(self, build_result: Any) -> float:
        """Calculate innovation-based bonus reward"""
        bonus = 0.0

        # First time working with this repository type
        repo_name = build_result.repository
        if repo_name not in [r for r in self.historical_patterns['repo_types_built']]:
            bonus += self.reward_config['first_time_repo_bonus']
            self.historical_patterns['repo_types_built'].append(repo_name)

        # Novel approach detection (simplified)
        code_length = len(build_result.code_generated)
        avg_code_length = np.mean([
            len(pattern.get('code', '')) 
            for pattern in self.historical_patterns['innovation_patterns']
        ]) if self.historical_patterns['innovation_patterns'] else 1000

        if code_length > avg_code_length * 1.5:  # Significantly more comprehensive
            bonus += self.reward_config['novel_approach_bonus']

        # Test coverage innovation
        if build_result.tests_passed and 'test' in build_result.code_generated.lower():
            bonus += self.reward_config['new_pattern_bonus'] * 0.5

        return bonus

    async def _calculate_consistency_bonus(self) -> float:
        """Calculate consistency-based bonus reward"""
        bonus = 0.0

        # Daily streak bonus
        if self.learning_streak_days > 0:
            streak_bonus = min(
                self.learning_streak_days * self.reward_config['daily_streak_bonus'],
                5.0  # Cap streak bonus at 5 tokens
            )
            bonus += streak_bonus

        # Weekly consistency (simplified - would track actual patterns)
        if self.total_utilities_created % 7 == 0 and self.total_utilities_created > 0:
            bonus += self.reward_config['weekly_consistency_bonus']

        # Monthly achievement milestone
        if self.total_utilities_created % 30 == 0 and self.total_utilities_created > 0:
            bonus += self.reward_config['monthly_achievement_bonus']

        return bonus

    async def _calculate_cycle_bonuses(self, build_results: List[Any], 
                                     current_cycle: Any) -> Dict[str, float]:
        """Calculate cycle-level bonuses"""
        bonuses = {
            'diversity_bonus': 0.0,
            'efficiency_bonus': 0.0,
            'error_recovery_bonus': 0.0,
            'total_bonus': 0.0
        }

        try:
            # Diversity bonus - reward for working with different types of repositories
            repo_types = set()
            for build in build_results:
                if hasattr(build, 'repository'):
                    # Simple type classification
                    repo_name = build.repository.lower()
                    if any(x in repo_name for x in ['ai', 'agent', 'eliza']):
                        repo_types.add('ai')
                    elif any(x in repo_name for x in ['network', 'mesh', 'p2p']):
                        repo_types.add('network')
                    elif any(x in repo_name for x in ['gov', 'dao', 'vote']):
                        repo_types.add('governance')
                    else:
                        repo_types.add('general')

            if len(repo_types) > 2:  # Worked with 3+ different types
                bonuses['diversity_bonus'] = 20.0
            elif len(repo_types) > 1:  # Worked with 2+ different types
                bonuses['diversity_bonus'] = 10.0

            # Efficiency bonus - high success rate
            if build_results:
                success_rate = len([r for r in build_results if r.success]) / len(build_results)
                if success_rate >= 0.8:
                    bonuses['efficiency_bonus'] = 15.0
                elif success_rate >= 0.6:
                    bonuses['efficiency_bonus'] = 10.0

            # Error recovery bonus - learning from mistakes
            if hasattr(current_cycle, 'learning_insights') and current_cycle.learning_insights:
                insight_quality = len([
                    insight for insight in current_cycle.learning_insights
                    if len(insight) > 50  # Substantial insights
                ])
                bonuses['error_recovery_bonus'] = min(insight_quality * 5.0, 25.0)

            bonuses['total_bonus'] = sum(bonuses.values())
            return bonuses

        except Exception as e:
            self.logger.error(f"Cycle bonus calculation failed: {e}")
            return bonuses

    async def _calculate_reputation_impact(self, reward_amount: float) -> Dict[str, float]:
        """Calculate impact on reputation score"""
        # Simple reputation system
        reputation_gain = reward_amount * 0.01  # 1% of reward amount

        # Bonus for consistency
        if self.learning_streak_days > 7:
            reputation_gain *= 1.2

        # Bonus for high quality
        if reward_amount > self.reward_config['base_reward'] * 2:
            reputation_gain *= 1.5

        self.reputation_score += reputation_gain

        return {
            'reputation_gain': reputation_gain,
            'new_reputation_score': self.reputation_score,
            'reputation_level': self._get_reputation_level()
        }

    def _get_reputation_level(self) -> str:
        """Get current reputation level"""
        if self.reputation_score >= 1000:
            return 'Master Builder'
        elif self.reputation_score >= 500:
            return 'Expert Developer'
        elif self.reputation_score >= 200:
            return 'Advanced Learner'
        elif self.reputation_score >= 50:
            return 'Skilled Builder'
        elif self.reputation_score >= 10:
            return 'Active Contributor'
        else:
            return 'Newcomer'

    async def _update_historical_data(self, build_results: List[Any], reward_amount: float):
        """Update historical patterns for future calculations"""
        try:
            # Update quality trends
            quality_scores = [
                build.quality_metrics.get('overall_score', 0.0)
                for build in build_results if build.success
            ]
            if quality_scores:
                self.historical_patterns['quality_trends'].extend(quality_scores)
                # Keep only recent data (last 100 entries)
                self.historical_patterns['quality_trends'] =                     self.historical_patterns['quality_trends'][-100:]

            # Update innovation patterns
            innovation_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'reward_amount': reward_amount,
                'utilities_count': len([r for r in build_results if r.success]),
                'avg_quality': np.mean(quality_scores) if quality_scores else 0.0
            }
            self.historical_patterns['innovation_patterns'].append(innovation_data)
            self.historical_patterns['innovation_patterns'] =                 self.historical_patterns['innovation_patterns'][-50:]  # Keep last 50

            # Update consistency metrics
            consistency_data = {
                'date': datetime.utcnow().date().isoformat(),
                'utilities_built': len([r for r in build_results if r.success]),
                'total_reward': reward_amount
            }
            self.historical_patterns['consistency_metrics'].append(consistency_data)

            # Update totals
            self.total_utilities_created += len([r for r in build_results if r.success])
            self.total_tokens_earned += reward_amount

            # Update learning streak (simplified)
            if reward_amount > 0:
                self.learning_streak_days += 1
            else:
                self.learning_streak_days = 0  # Reset on unsuccessful day

        except Exception as e:
            self.logger.error(f"Failed to update historical data: {e}")

    async def get_reward_statistics(self) -> Dict[str, Any]:
        """Get comprehensive reward and performance statistics"""
        try:
            quality_trends = self.historical_patterns['quality_trends']
            innovation_patterns = self.historical_patterns['innovation_patterns']

            return {
                'total_tokens_earned': self.total_tokens_earned,
                'total_utilities_created': self.total_utilities_created,
                'reputation_score': self.reputation_score,
                'reputation_level': self._get_reputation_level(),
                'learning_streak_days': self.learning_streak_days,
                'average_quality': (
                    np.mean(quality_trends) if quality_trends else 0.0
                ),
                'quality_trend': (
                    'improving' if len(quality_trends) > 5 and
                    np.mean(quality_trends[-5:]) > np.mean(quality_trends[:-5])
                    else 'stable'
                ),
                'recent_innovation_score': (
                    np.mean([p['reward_amount'] for p in innovation_patterns[-5:]])
                    if len(innovation_patterns) >= 5 else 0.0
                ),
                'productivity_score': (
                    self.total_utilities_created / max(len(innovation_patterns), 1)
                )
            }

        except Exception as e:
            self.logger.error(f"Statistics calculation failed: {e}")
            return {
                'error': str(e),
                'total_tokens_earned': self.total_tokens_earned,
                'total_utilities_created': self.total_utilities_created
            }

    async def suggest_optimization_strategies(self) -> List[str]:
        """Suggest strategies to optimize reward earning"""
        suggestions = []

        try:
            stats = await self.get_reward_statistics()

            # Quality improvement suggestions
            if stats['average_quality'] < 0.7:
                suggestions.append(
                    "Focus on improving code quality - add more documentation, "
                    "error handling, and comprehensive testing"
                )

            # Consistency suggestions
            if self.learning_streak_days < 3:
                suggestions.append(
                    "Build learning consistency - daily utility creation "
                    "provides streak bonuses and improves skill development"
                )

            # Complexity suggestions
            if stats['recent_innovation_score'] < self.reward_config['base_reward']:
                suggestions.append(
                    "Challenge yourself with more complex repositories - "
                    "higher complexity provides better reward multipliers"
                )

            # Diversity suggestions
            repo_types_worked = len(set(self.historical_patterns['repo_types_built'][-10:]))
            if repo_types_worked < 3:
                suggestions.append(
                    "Diversify your learning - work with different types of "
                    "repositories (AI, networking, governance) for variety bonuses"
                )

            # Innovation suggestions
            if len(self.historical_patterns['innovation_patterns']) > 5:
                recent_patterns = self.historical_patterns['innovation_patterns'][-5:]
                code_variety = len(set(p.get('code_pattern', '') for p in recent_patterns))
                if code_variety < 3:
                    suggestions.append(
                        "Explore innovative approaches - novel patterns and "
                        "unique solutions earn significant innovation bonuses"
                    )

            return suggestions

        except Exception as e:
            self.logger.error(f"Failed to generate suggestions: {e}")
            return ["Focus on consistent learning and quality code production"]

# Test the service
async def test_incentive_calculation():
    """Test the incentive calculation service"""

    # Mock build result for testing
    class MockBuildResult:
        def __init__(self, success=True, repository="test-repo", 
                     quality_metrics=None, tests_passed=True):
            self.success = success
            self.repository = repository
            self.quality_metrics = quality_metrics or {'overall_score': 0.75}
            self.tests_passed = tests_passed
            self.utility_name = f"{repository}_utility"
            self.code_generated = "# Test code\nclass TestUtility:\n    pass"

    # Mock learning cycle
    class MockLearningCycle:
        def __init__(self):
            self.cycle_id = "test_cycle_1"
            self.learning_insights = ["Learned about error handling", "Improved documentation"]

    # Test the service
    calc_service = IncentiveCalculationService()

    # Create test data
    build_results = [
        MockBuildResult(True, "xmrt-ai-agent", {'overall_score': 0.85}),
        MockBuildResult(True, "xmrt-network-mesh", {'overall_score': 0.70}),
        MockBuildResult(False, "failed-repo", {'overall_score': 0.30}),
        MockBuildResult(True, "xmrt-governance-dao", {'overall_score': 0.92})
    ]

    current_cycle = MockLearningCycle()

    # Calculate rewards
    rewards = await calc_service.calculate_cycle_rewards(build_results, current_cycle)

    print("Reward Calculation Test Results:")
    print(f"Total Tokens: {rewards['total_tokens']}")
    print(f"Quality Score: {rewards['quality_score']}")
    print(f"Utilities Rewarded: {rewards['utilities_rewarded']}")
    print("\nDetailed Breakdown:")
    for utility, details in rewards['breakdown'].items():
        if isinstance(details, dict) and 'total' in details:
            print(f"  {utility}: {details['total']:.2f} tokens")

    # Get statistics
    stats = await calc_service.get_reward_statistics()
    print(f"\nReputation Level: {stats['reputation_level']}")
    print(f"Learning Streak: {stats['learning_streak_days']} days")

    # Get suggestions
    suggestions = await calc_service.suggest_optimization_strategies()
    print("\nOptimization Suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")

if __name__ == "__main__":
    asyncio.run(test_incentive_calculation())
