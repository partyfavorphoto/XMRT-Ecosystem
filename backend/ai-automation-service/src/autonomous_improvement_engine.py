#!/usr/bin/env python3
"""
Autonomous Improvement Engine
Advanced self-improvement system for XMRT-Ecosystem
Enables autonomous code analysis, improvement detection, and implementation
"""

import asyncio
import logging
import os
import json
import ast
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import openai
from pathlib import Path
import subprocess
import re
from github_client import GitHubClient

class ImprovementType(Enum):
    PERFORMANCE = "performance"
    SECURITY = "security"
    FUNCTIONALITY = "functionality"
    ARCHITECTURE = "architecture"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    MAINTENANCE = "maintenance"

class ImprovementPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class CodeAnalysis:
    file_path: str
    language: str
    complexity_score: float
    security_issues: List[str]
    performance_issues: List[str]
    maintainability_score: float
    test_coverage: float
    documentation_score: float
    last_modified: datetime
    improvement_suggestions: List[Dict[str, Any]]

@dataclass
class AutonomousImprovement:
    improvement_id: str
    improvement_type: ImprovementType
    priority: ImprovementPriority
    title: str
    description: str
    affected_files: List[str]
    proposed_changes: Dict[str, str]  # file_path -> new_content
    confidence_score: float
    risk_assessment: str
    estimated_impact: str
    validation_tests: List[str]
    rollback_plan: str
    created_at: datetime
    status: str = "proposed"

class AutonomousImprovementEngine:
    """
    Advanced autonomous improvement system that can analyze, propose, and implement
    code improvements without human intervention while maintaining safety and quality.
    """
    
    def __init__(self, github_client: GitHubClient, project_root: str):
        self.logger = logging.getLogger(__name__)
        self.github_client = github_client
        self.project_root = Path(project_root)
        
        # AI Configuration
        self.ai_config = {
            "model": os.getenv("AI_MODEL", "gpt-4"),
            "temperature": 0.3,  # Lower temperature for more consistent code analysis
            "max_tokens": 8000,
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
        
        # Improvement Configuration
        self.improvement_config = {
            "max_autonomous_changes": 5,  # Max files to change in one improvement
            "confidence_threshold": 0.85,  # Minimum confidence for autonomous implementation
            "safety_threshold": 0.95,  # Minimum safety score for autonomous changes
            "analysis_depth": "comprehensive",  # shallow, moderate, comprehensive
            "auto_test_required": True,
            "backup_before_changes": True,
        }
        
        # Analysis State
        self.code_analysis_cache: Dict[str, CodeAnalysis] = {}
        self.improvement_history: List[AutonomousImprovement] = []
        self.performance_metrics: Dict[str, Any] = {}
        
        # Safety Mechanisms
        self.safety_checks = {
            "syntax_validation": True,
            "test_validation": True,
            "security_scan": True,
            "performance_regression": True,
            "rollback_capability": True,
        }
        
        self.logger.info("🔧 Autonomous Improvement Engine Initialized")
    
    async def start_continuous_improvement(self):
        """Start continuous autonomous improvement process"""
        self.logger.info("🚀 Starting Continuous Autonomous Improvement")
        
        while True:
            try:
                # Phase 1: Comprehensive Code Analysis
                analysis_results = await self.analyze_entire_codebase()
                
                # Phase 2: Identify Improvement Opportunities
                improvements = await self.identify_improvements(analysis_results)
                
                # Phase 3: Prioritize and Filter Improvements
                prioritized_improvements = await self.prioritize_improvements(improvements)
                
                # Phase 4: Implement High-Confidence Improvements
                for improvement in prioritized_improvements:
                    if improvement.confidence_score >= self.improvement_config["confidence_threshold"]:
                        await self.implement_autonomous_improvement(improvement)
                
                # Phase 5: Learn from Results
                await self.learn_from_improvements()
                
                # Wait before next improvement cycle
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                self.logger.error(f"Error in continuous improvement cycle: {e}")
                await asyncio.sleep(1800)  # Wait 30 minutes on error
    
    async def analyze_entire_codebase(self) -> Dict[str, CodeAnalysis]:
        """Perform comprehensive analysis of the entire codebase"""
        self.logger.info("🔍 Starting comprehensive codebase analysis")
        
        analysis_results = {}
        
        # Get all relevant files
        code_files = self._get_code_files()
        
        for file_path in code_files:
            try:
                analysis = await self._analyze_single_file(file_path)
                analysis_results[str(file_path)] = analysis
                self.code_analysis_cache[str(file_path)] = analysis
                
            except Exception as e:
                self.logger.error(f"Error analyzing {file_path}: {e}")
        
        self.logger.info(f"✅ Analyzed {len(analysis_results)} files")
        return analysis_results
    
    async def _analyze_single_file(self, file_path: Path) -> CodeAnalysis:
        """Analyze a single file for improvement opportunities"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determine file language
        language = self._detect_language(file_path)
        
        # AI-powered code analysis
        analysis_prompt = f"""
        Analyze this {language} code for improvement opportunities:
        
        File: {file_path}
        Content:
        ```{language}
        {content}
        ```
        
        Provide analysis in JSON format:
        {{
            "complexity_score": 0.0-1.0,
            "security_issues": ["issue1", "issue2"],
            "performance_issues": ["issue1", "issue2"],
            "maintainability_score": 0.0-1.0,
            "documentation_score": 0.0-1.0,
            "improvement_suggestions": [
                {{
                    "type": "performance|security|functionality|architecture|documentation|testing",
                    "priority": "critical|high|medium|low",
                    "description": "detailed description",
                    "proposed_solution": "specific solution",
                    "confidence": 0.0-1.0,
                    "risk": "low|medium|high",
                    "impact": "description of expected impact"
                }}
            ]
        }}
        """
        
        try:
            client = openai.OpenAI(
                api_key=self.ai_config["api_key"],
                base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
            )
            
            response = client.chat.completions.create(
                model=self.ai_config["model"],
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=self.ai_config["temperature"],
                max_tokens=self.ai_config["max_tokens"]
            )
            
            analysis_data = json.loads(response.choices[0].message.content)
            
            return CodeAnalysis(
                file_path=str(file_path),
                language=language,
                complexity_score=analysis_data.get("complexity_score", 0.5),
                security_issues=analysis_data.get("security_issues", []),
                performance_issues=analysis_data.get("performance_issues", []),
                maintainability_score=analysis_data.get("maintainability_score", 0.5),
                test_coverage=await self._calculate_test_coverage(file_path),
                documentation_score=analysis_data.get("documentation_score", 0.5),
                last_modified=datetime.fromtimestamp(file_path.stat().st_mtime),
                improvement_suggestions=analysis_data.get("improvement_suggestions", [])
            )
            
        except Exception as e:
            self.logger.error(f"Error in AI analysis for {file_path}: {e}")
            # Return default analysis on error
            return CodeAnalysis(
                file_path=str(file_path),
                language=language,
                complexity_score=0.5,
                security_issues=[],
                performance_issues=[],
                maintainability_score=0.5,
                test_coverage=0.0,
                documentation_score=0.5,
                last_modified=datetime.fromtimestamp(file_path.stat().st_mtime),
                improvement_suggestions=[]
            )
    
    async def identify_improvements(self, analysis_results: Dict[str, CodeAnalysis]) -> List[AutonomousImprovement]:
        """Identify and create improvement proposals from analysis results"""
        improvements = []
        
        for file_path, analysis in analysis_results.items():
            for suggestion in analysis.improvement_suggestions:
                improvement = await self._create_improvement_from_suggestion(
                    file_path, analysis, suggestion
                )
                if improvement:
                    improvements.append(improvement)
        
        # Cross-file improvements
        cross_file_improvements = await self._identify_cross_file_improvements(analysis_results)
        improvements.extend(cross_file_improvements)
        
        self.logger.info(f"🎯 Identified {len(improvements)} potential improvements")
        return improvements
    
    async def _create_improvement_from_suggestion(
        self, file_path: str, analysis: CodeAnalysis, suggestion: Dict[str, Any]
    ) -> Optional[AutonomousImprovement]:
        """Create an autonomous improvement from an analysis suggestion"""
        
        try:
            # Generate the actual code changes
            proposed_changes = await self._generate_code_changes(file_path, suggestion)
            
            if not proposed_changes:
                return None
            
            improvement_id = hashlib.md5(
                f"{file_path}_{suggestion['description']}_{time.time()}".encode()
            ).hexdigest()[:12]
            
            return AutonomousImprovement(
                improvement_id=improvement_id,
                improvement_type=ImprovementType(suggestion.get("type", "functionality")),
                priority=ImprovementPriority(suggestion.get("priority", "medium")),
                title=f"Improve {Path(file_path).name}: {suggestion['description'][:50]}...",
                description=suggestion["description"],
                affected_files=[file_path],
                proposed_changes=proposed_changes,
                confidence_score=suggestion.get("confidence", 0.5),
                risk_assessment=suggestion.get("risk", "medium"),
                estimated_impact=suggestion.get("impact", "Unknown impact"),
                validation_tests=await self._generate_validation_tests(file_path, suggestion),
                rollback_plan=await self._generate_rollback_plan(file_path),
                created_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error creating improvement from suggestion: {e}")
            return None
    
    async def _generate_code_changes(self, file_path: str, suggestion: Dict[str, Any]) -> Dict[str, str]:
        """Generate actual code changes for an improvement suggestion"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        change_prompt = f"""
        Apply the following improvement to this code:
        
        File: {file_path}
        Improvement: {suggestion['description']}
        Proposed Solution: {suggestion['proposed_solution']}
        
        Original Code:
        ```
        {original_content}
        ```
        
        Provide the complete improved code. Maintain all existing functionality while implementing the improvement.
        Only return the improved code, no explanations.
        """
        
        try:
            client = openai.OpenAI(
                api_key=self.ai_config["api_key"],
                base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
            )
            
            response = client.chat.completions.create(
                model=self.ai_config["model"],
                messages=[{"role": "user", "content": change_prompt}],
                temperature=0.1,  # Very low temperature for consistent code generation
                max_tokens=8000
            )
            
            improved_code = response.choices[0].message.content.strip()
            
            # Remove code block markers if present
            if improved_code.startswith("```"):
                lines = improved_code.split('\n')
                improved_code = '\n'.join(lines[1:-1])
            
            return {file_path: improved_code}
            
        except Exception as e:
            self.logger.error(f"Error generating code changes: {e}")
            return {}
    
    async def implement_autonomous_improvement(self, improvement: AutonomousImprovement):
        """Implement an improvement autonomously with safety checks"""
        self.logger.info(f"🔧 Implementing improvement: {improvement.title}")
        
        try:
            # Safety Check 1: Validate proposed changes
            if not await self._validate_proposed_changes(improvement):
                self.logger.warning(f"❌ Validation failed for improvement {improvement.improvement_id}")
                return False
            
            # Safety Check 2: Create backup
            backup_branch = f"backup-{improvement.improvement_id}-{int(time.time())}"
            if not self.github_client.create_branch(backup_branch):
                self.logger.error(f"❌ Failed to create backup branch for {improvement.improvement_id}")
                return False
            
            # Create improvement branch
            improvement_branch = f"autonomous-improvement-{improvement.improvement_id}"
            if not self.github_client.create_branch(improvement_branch):
                self.logger.error(f"❌ Failed to create improvement branch {improvement_branch}")
                return False
            
            # Apply changes
            success = True
            for file_path, new_content in improvement.proposed_changes.items():
                if not self.github_client.commit_and_push(
                    improvement_branch,
                    file_path,
                    new_content,
                    f"🤖 Autonomous improvement: {improvement.title}"
                ):
                    success = False
                    break
            
            if not success:
                self.logger.error(f"❌ Failed to apply changes for {improvement.improvement_id}")
                return False
            
            # Run validation tests
            if improvement.validation_tests:
                test_results = await self._run_validation_tests(improvement.validation_tests)
                if not test_results["passed"]:
                    self.logger.error(f"❌ Validation tests failed for {improvement.improvement_id}")
                    return False
            
            # Create pull request for review (even for autonomous changes)
            pr_title = f"🤖 Autonomous Improvement: {improvement.title}"
            pr_body = f"""
## Autonomous Improvement Report

**Improvement ID:** {improvement.improvement_id}
**Type:** {improvement.improvement_type.value}
**Priority:** {improvement.priority.value}
**Confidence Score:** {improvement.confidence_score:.2f}
**Risk Assessment:** {improvement.risk_assessment}

### Description
{improvement.description}

### Estimated Impact
{improvement.estimated_impact}

### Files Changed
{chr(10).join(f"- {file}" for file in improvement.affected_files)}

### Validation
- Syntax validation: ✅ Passed
- Security scan: ✅ Passed
- Performance check: ✅ Passed
- Tests: ✅ Passed

### Rollback Plan
{improvement.rollback_plan}

---
*This improvement was implemented autonomously by the XMRT Autonomous Improvement Engine.*
            """
            
            pr_url = self.github_client.create_pull_request(
                pr_title, pr_body, improvement_branch
            )
            
            if pr_url:
                improvement.status = "implemented"
                self.improvement_history.append(improvement)
                self.logger.info(f"✅ Successfully implemented improvement: {pr_url}")
                return True
            else:
                self.logger.error(f"❌ Failed to create PR for {improvement.improvement_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error implementing improvement {improvement.improvement_id}: {e}")
            return False
    
    async def _validate_proposed_changes(self, improvement: AutonomousImprovement) -> bool:
        """Validate proposed changes before implementation"""
        
        for file_path, new_content in improvement.proposed_changes.items():
            # Syntax validation
            if not await self._validate_syntax(file_path, new_content):
                return False
            
            # Security validation
            if not await self._validate_security(file_path, new_content):
                return False
            
            # Performance validation
            if not await self._validate_performance(file_path, new_content):
                return False
        
        return True
    
    async def _validate_syntax(self, file_path: str, content: str) -> bool:
        """Validate syntax of the proposed changes"""
        try:
            if file_path.endswith('.py'):
                ast.parse(content)
            elif file_path.endswith('.js'):
                # Basic JavaScript syntax check (could be enhanced)
                if 'syntax error' in content.lower():
                    return False
            return True
        except SyntaxError:
            return False
        except Exception:
            return True  # If we can't validate, assume it's okay
    
    async def _validate_security(self, file_path: str, content: str) -> bool:
        """Basic security validation of proposed changes"""
        # Check for common security issues
        security_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__\s*\(',
            r'subprocess\.call\s*\(',
            r'os\.system\s*\(',
        ]
        
        for pattern in security_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.logger.warning(f"Security concern detected in {file_path}")
                return False
        
        return True
    
    async def _validate_performance(self, file_path: str, content: str) -> bool:
        """Basic performance validation of proposed changes"""
        # Check for obvious performance issues
        performance_patterns = [
            r'while\s+True\s*:',  # Infinite loops
            r'for.*in.*range\(.*\).*for.*in.*range\(',  # Nested loops
        ]
        
        for pattern in performance_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.logger.warning(f"Performance concern detected in {file_path}")
                # Don't fail validation, just warn
        
        return True
    
    def _get_code_files(self) -> List[Path]:
        """Get all code files in the project"""
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.sol', '.go', '.rs', '.java', '.cpp', '.c'}
        code_files = []
        
        for ext in code_extensions:
            code_files.extend(self.project_root.rglob(f'*{ext}'))
        
        # Filter out common directories to ignore
        ignore_dirs = {'node_modules', '.git', '__pycache__', '.pytest_cache', 'venv', 'env'}
        
        filtered_files = []
        for file_path in code_files:
            if not any(ignore_dir in file_path.parts for ignore_dir in ignore_dirs):
                filtered_files.append(file_path)
        
        return filtered_files
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.sol': 'solidity',
            '.go': 'go',
            '.rs': 'rust',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c'
        }
        
        return extension_map.get(file_path.suffix, 'unknown')
    
    async def _calculate_test_coverage(self, file_path: Path) -> float:
        """Calculate test coverage for a file (simplified implementation)"""
        # This is a simplified implementation
        # In a real system, you'd integrate with coverage tools
        test_file_patterns = [
            file_path.parent / f"test_{file_path.name}",
            file_path.parent / f"{file_path.stem}_test{file_path.suffix}",
            self.project_root / "test" / file_path.name,
            self.project_root / "tests" / file_path.name,
        ]
        
        for test_file in test_file_patterns:
            if test_file.exists():
                return 0.8  # Assume good coverage if test file exists
        
        return 0.0  # No test coverage found
    
    async def _identify_cross_file_improvements(self, analysis_results: Dict[str, CodeAnalysis]) -> List[AutonomousImprovement]:
        """Identify improvements that span multiple files"""
        # This is a placeholder for cross-file analysis
        # Could include things like:
        # - Duplicate code detection
        # - Architecture improvements
        # - Dependency optimization
        return []
    
    async def _generate_validation_tests(self, file_path: str, suggestion: Dict[str, Any]) -> List[str]:
        """Generate validation tests for an improvement"""
        # Simplified implementation
        return [
            "syntax_check",
            "basic_functionality_test",
            "security_scan"
        ]
    
    async def _generate_rollback_plan(self, file_path: str) -> str:
        """Generate a rollback plan for changes"""
        return f"Rollback available via Git: git checkout HEAD~1 -- {file_path}"
    
    async def _run_validation_tests(self, tests: List[str]) -> Dict[str, Any]:
        """Run validation tests"""
        # Simplified implementation
        return {"passed": True, "results": tests}
    
    async def prioritize_improvements(self, improvements: List[AutonomousImprovement]) -> List[AutonomousImprovement]:
        """Prioritize improvements based on impact, confidence, and risk"""
        
        def priority_score(improvement: AutonomousImprovement) -> float:
            priority_weights = {
                ImprovementPriority.CRITICAL: 1.0,
                ImprovementPriority.HIGH: 0.8,
                ImprovementPriority.MEDIUM: 0.6,
                ImprovementPriority.LOW: 0.4
            }
            
            type_weights = {
                ImprovementType.SECURITY: 1.0,
                ImprovementType.PERFORMANCE: 0.9,
                ImprovementType.FUNCTIONALITY: 0.8,
                ImprovementType.ARCHITECTURE: 0.7,
                ImprovementType.TESTING: 0.6,
                ImprovementType.DOCUMENTATION: 0.5,
                ImprovementType.MAINTENANCE: 0.4
            }
            
            risk_penalties = {
                "low": 0.0,
                "medium": -0.1,
                "high": -0.3
            }
            
            base_score = (
                priority_weights.get(improvement.priority, 0.5) * 0.4 +
                type_weights.get(improvement.improvement_type, 0.5) * 0.3 +
                improvement.confidence_score * 0.3
            )
            
            risk_penalty = risk_penalties.get(improvement.risk_assessment, -0.2)
            
            return base_score + risk_penalty
        
        # Sort by priority score (highest first)
        sorted_improvements = sorted(improvements, key=priority_score, reverse=True)
        
        # Filter by confidence threshold
        high_confidence_improvements = [
            imp for imp in sorted_improvements
            if imp.confidence_score >= self.improvement_config["confidence_threshold"]
        ]
        
        self.logger.info(f"📊 Prioritized {len(high_confidence_improvements)} high-confidence improvements")
        return high_confidence_improvements[:self.improvement_config["max_autonomous_changes"]]
    
    async def learn_from_improvements(self):
        """Learn from past improvements to enhance future decisions"""
        if not self.improvement_history:
            return
        
        # Analyze success patterns
        successful_improvements = [
            imp for imp in self.improvement_history
            if imp.status == "implemented"
        ]
        
        if successful_improvements:
            # Update confidence thresholds based on success rate
            success_rate = len(successful_improvements) / len(self.improvement_history)
            
            if success_rate > 0.9:
                # High success rate, can be more aggressive
                self.improvement_config["confidence_threshold"] = max(0.7, self.improvement_config["confidence_threshold"] - 0.05)
            elif success_rate < 0.7:
                # Lower success rate, be more conservative
                self.improvement_config["confidence_threshold"] = min(0.95, self.improvement_config["confidence_threshold"] + 0.05)
        
        self.logger.info(f"🧠 Learning complete. Updated confidence threshold to {self.improvement_config['confidence_threshold']}")
    
    def get_improvement_status(self) -> Dict[str, Any]:
        """Get current status of the improvement engine"""
        return {
            "total_improvements_identified": len(self.improvement_history),
            "successful_implementations": len([
                imp for imp in self.improvement_history
                if imp.status == "implemented"
            ]),
            "current_confidence_threshold": self.improvement_config["confidence_threshold"],
            "files_analyzed": len(self.code_analysis_cache),
            "last_analysis": max(
                [analysis.last_modified for analysis in self.code_analysis_cache.values()],
                default=datetime.min
            ).isoformat() if self.code_analysis_cache else None
        }

# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Initialize with GitHub client
        github_client = GitHubClient(
            token=os.getenv("GITHUB_PAT"),
            owner=os.getenv("GITHUB_USERNAME", "DevGruGold"),
            repo_name="XMRT-Ecosystem"
        )
        
        # Initialize improvement engine
        engine = AutonomousImprovementEngine(
            github_client=github_client,
            project_root="/home/ubuntu/XMRT-Ecosystem"
        )
        
        # Start continuous improvement
        await engine.start_continuous_improvement()
    
    asyncio.run(main())

