#!/usr/bin/env python3
"""
GitHub Integration for Autonomous Self-Improvement
Enables Eliza to autonomously analyze, improve, and commit code changes
"""

import asyncio
import logging
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import openai
from pathlib import Path
import subprocess
import re
from github import Github
from github.GithubException import GithubException
import git

logger = logging.getLogger(__name__)

class ChangeType(Enum):
    BUG_FIX = "bug_fix"
    FEATURE_ENHANCEMENT = "feature_enhancement"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    SECURITY_IMPROVEMENT = "security_improvement"
    CODE_REFACTORING = "code_refactoring"
    DOCUMENTATION_UPDATE = "documentation_update"
    TEST_IMPROVEMENT = "test_improvement"

@dataclass
class CodeChange:
    file_path: str
    change_type: ChangeType
    description: str
    old_content: str
    new_content: str
    confidence_score: float
    impact_assessment: Dict[str, Any]
    test_results: Optional[Dict[str, Any]] = None

@dataclass
class ImprovementPlan:
    improvement_id: str
    title: str
    description: str
    changes: List[CodeChange]
    priority: str
    estimated_impact: float
    risk_level: str
    created_at: datetime

class GitHubSelfImprovementEngine:
    """
    Autonomous GitHub integration for self-improvement
    """
    
    def __init__(self, repo_owner: str, repo_name: str, pat_token: str):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_client = Github(pat_token)
        self.repo = self.github_client.get_user(repo_owner).get_repo(repo_name)
        self.local_repo_path = f"/tmp/{repo_name}"
        
        # OpenAI client for code analysis
        self.openai_client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        )
        
        # Configuration
        self.config = {
            "max_changes_per_pr": 5,
            "min_confidence_threshold": 0.8,
            "auto_merge_threshold": 0.95,
            "branch_prefix": "eliza-autonomous-",
            "review_required_threshold": 0.85
        }
        
        self.improvement_history: List[ImprovementPlan] = []
        
        logger.info(f"GitHub Self-Improvement Engine initialized for {repo_owner}/{repo_name}")

    async def analyze_repository_for_improvements(self) -> List[ImprovementPlan]:
        """
        Analyze the entire repository for potential improvements
        """
        logger.info("Starting repository analysis for improvements...")
        
        try:
            # Clone or update local repository
            await self._ensure_local_repo()
            
            # Analyze different aspects
            improvements = []
            
            # Code quality improvements
            code_improvements = await self._analyze_code_quality()
            improvements.extend(code_improvements)
            
            # Security improvements
            security_improvements = await self._analyze_security_issues()
            improvements.extend(security_improvements)
            
            # Performance improvements
            performance_improvements = await self._analyze_performance_issues()
            improvements.extend(performance_improvements)
            
            # Documentation improvements
            doc_improvements = await self._analyze_documentation_gaps()
            improvements.extend(doc_improvements)
            
            # Test coverage improvements
            test_improvements = await self._analyze_test_coverage()
            improvements.extend(test_improvements)
            
            # Sort by priority and impact
            improvements.sort(key=lambda x: (x.priority, x.estimated_impact), reverse=True)
            
            self.improvement_history.extend(improvements)
            
            logger.info(f"Found {len(improvements)} potential improvements")
            return improvements
            
        except Exception as e:
            logger.error(f"Error analyzing repository: {e}")
            return []

    async def implement_improvements_autonomously(self, improvements: List[ImprovementPlan]) -> Dict[str, Any]:
        """
        Autonomously implement improvements based on confidence and risk levels
        """
        logger.info(f"Starting autonomous implementation of {len(improvements)} improvements...")
        
        results = {
            "implemented": [],
            "pending_review": [],
            "failed": [],
            "skipped": []
        }
        
        for improvement in improvements:
            try:
                # Check if improvement meets autonomous implementation criteria
                if await self._should_implement_autonomously(improvement):
                    result = await self._implement_improvement_autonomous(improvement)
                    if result["success"]:
                        results["implemented"].append({
                            "improvement_id": improvement.improvement_id,
                            "title": improvement.title,
                            "pr_url": result.get("pr_url"),
                            "commit_hash": result.get("commit_hash")
                        })
                    else:
                        results["failed"].append({
                            "improvement_id": improvement.improvement_id,
                            "title": improvement.title,
                            "error": result.get("error")
                        })
                
                elif improvement.risk_level in ["low", "medium"]:
                    # Create PR for review
                    result = await self._create_improvement_pr(improvement)
                    if result["success"]:
                        results["pending_review"].append({
                            "improvement_id": improvement.improvement_id,
                            "title": improvement.title,
                            "pr_url": result.get("pr_url")
                        })
                    else:
                        results["failed"].append({
                            "improvement_id": improvement.improvement_id,
                            "title": improvement.title,
                            "error": result.get("error")
                        })
                
                else:
                    results["skipped"].append({
                        "improvement_id": improvement.improvement_id,
                        "title": improvement.title,
                        "reason": "High risk - requires manual review"
                    })
                    
            except Exception as e:
                logger.error(f"Error implementing improvement {improvement.improvement_id}: {e}")
                results["failed"].append({
                    "improvement_id": improvement.improvement_id,
                    "title": improvement.title,
                    "error": str(e)
                })
        
        logger.info(f"Implementation complete: {len(results['implemented'])} implemented, "
                   f"{len(results['pending_review'])} pending review, "
                   f"{len(results['failed'])} failed, {len(results['skipped'])} skipped")
        
        return results

    async def _ensure_local_repo(self):
        """Ensure local repository is up to date"""
        try:
            if os.path.exists(self.local_repo_path):
                # Update existing repo
                repo = git.Repo(self.local_repo_path)
                repo.remotes.origin.pull()
            else:
                # Clone repository
                git.Repo.clone_from(
                    f"https://github.com/{self.repo_owner}/{self.repo_name}.git",
                    self.local_repo_path
                )
            
            logger.info("Local repository updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating local repository: {e}")
            raise

    async def _analyze_code_quality(self) -> List[ImprovementPlan]:
        """Analyze code quality and suggest improvements"""
        improvements = []
        
        try:
            # Find Python files
            python_files = list(Path(self.local_repo_path).rglob("*.py"))
            
            for file_path in python_files[:10]:  # Limit to first 10 files for demo
                if file_path.stat().st_size > 100000:  # Skip very large files
                    continue
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Analyze with AI
                analysis = await self._ai_analyze_code_quality(str(file_path), content)
                
                if analysis and analysis.get("improvements"):
                    for improvement_data in analysis["improvements"]:
                        improvement = ImprovementPlan(
                            improvement_id=f"code_quality_{int(time.time())}_{hash(str(file_path)) % 10000}",
                            title=improvement_data["title"],
                            description=improvement_data["description"],
                            changes=[CodeChange(
                                file_path=str(file_path.relative_to(self.local_repo_path)),
                                change_type=ChangeType.CODE_REFACTORING,
                                description=improvement_data["description"],
                                old_content=content,
                                new_content=improvement_data["new_content"],
                                confidence_score=improvement_data["confidence"],
                                impact_assessment=improvement_data["impact"]
                            )],
                            priority=improvement_data["priority"],
                            estimated_impact=improvement_data["impact"]["score"],
                            risk_level=improvement_data["risk_level"],
                            created_at=datetime.now()
                        )
                        improvements.append(improvement)
            
        except Exception as e:
            logger.error(f"Error analyzing code quality: {e}")
        
        return improvements

    async def _ai_analyze_code_quality(self, file_path: str, content: str) -> Optional[Dict[str, Any]]:
        """Use AI to analyze code quality"""
        try:
            prompt = f"""
            Analyze the following Python code for quality improvements:
            
            File: {file_path}
            
            Code:
            ```python
            {content[:5000]}  # Limit content length
            ```
            
            Provide analysis in JSON format with the following structure:
            {{
                "improvements": [
                    {{
                        "title": "Brief improvement title",
                        "description": "Detailed description of the improvement",
                        "new_content": "Improved code (only the changed parts)",
                        "confidence": 0.85,
                        "priority": "high|medium|low",
                        "risk_level": "low|medium|high",
                        "impact": {{
                            "score": 0.8,
                            "readability": 0.9,
                            "maintainability": 0.8,
                            "performance": 0.7
                        }}
                    }}
                ]
            }}
            
            Focus on:
            - Code readability and clarity
            - Performance optimizations
            - Error handling improvements
            - Type hints and documentation
            - Best practices compliance
            
            Only suggest improvements with high confidence (>0.8) and clear benefits.
            """
            
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert Python code reviewer focused on quality improvements."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Error in AI code analysis: {e}")
            return None

    async def _analyze_security_issues(self) -> List[ImprovementPlan]:
        """Analyze security issues and suggest fixes"""
        improvements = []
        
        try:
            # Run security analysis tools
            security_issues = await self._run_security_scan()
            
            for issue in security_issues:
                improvement = ImprovementPlan(
                    improvement_id=f"security_{int(time.time())}_{hash(issue['file']) % 10000}",
                    title=f"Fix security issue: {issue['type']}",
                    description=issue['description'],
                    changes=[CodeChange(
                        file_path=issue['file'],
                        change_type=ChangeType.SECURITY_IMPROVEMENT,
                        description=issue['description'],
                        old_content=issue['vulnerable_code'],
                        new_content=issue['fixed_code'],
                        confidence_score=issue['confidence'],
                        impact_assessment=issue['impact']
                    )],
                    priority="high",
                    estimated_impact=0.9,
                    risk_level="low",
                    created_at=datetime.now()
                )
                improvements.append(improvement)
                
        except Exception as e:
            logger.error(f"Error analyzing security issues: {e}")
        
        return improvements

    async def _run_security_scan(self) -> List[Dict[str, Any]]:
        """Run security scanning tools"""
        issues = []
        
        try:
            # This would integrate with actual security scanning tools
            # For now, return mock data
            issues = [
                {
                    "type": "hardcoded_secret",
                    "file": "config.py",
                    "description": "Hardcoded API key detected",
                    "vulnerable_code": "API_KEY = 'sk-1234567890'",
                    "fixed_code": "API_KEY = os.getenv('API_KEY')",
                    "confidence": 0.95,
                    "impact": {"score": 0.9, "severity": "high"}
                }
            ]
            
        except Exception as e:
            logger.error(f"Error running security scan: {e}")
        
        return issues

    async def _analyze_performance_issues(self) -> List[ImprovementPlan]:
        """Analyze performance issues"""
        # Implementation would analyze code for performance bottlenecks
        return []

    async def _analyze_documentation_gaps(self) -> List[ImprovementPlan]:
        """Analyze documentation gaps"""
        # Implementation would check for missing docstrings, README updates, etc.
        return []

    async def _analyze_test_coverage(self) -> List[ImprovementPlan]:
        """Analyze test coverage and suggest improvements"""
        # Implementation would analyze test coverage and suggest new tests
        return []

    async def _should_implement_autonomously(self, improvement: ImprovementPlan) -> bool:
        """Determine if improvement should be implemented autonomously"""
        
        # Check confidence threshold
        avg_confidence = sum(change.confidence_score for change in improvement.changes) / len(improvement.changes)
        if avg_confidence < self.config["min_confidence_threshold"]:
            return False
        
        # Check risk level
        if improvement.risk_level == "high":
            return False
        
        # Check impact and complexity
        if improvement.estimated_impact < 0.3:  # Low impact changes
            return False
        
        # Check change count
        if len(improvement.changes) > self.config["max_changes_per_pr"]:
            return False
        
        return True

    async def _implement_improvement_autonomous(self, improvement: ImprovementPlan) -> Dict[str, Any]:
        """Implement improvement autonomously"""
        try:
            # Create branch
            branch_name = f"{self.config['branch_prefix']}{improvement.improvement_id}"
            
            # Apply changes
            repo = git.Repo(self.local_repo_path)
            repo.git.checkout('-b', branch_name)
            
            for change in improvement.changes:
                file_path = os.path.join(self.local_repo_path, change.file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(change.new_content)
            
            # Commit changes
            repo.git.add('.')
            repo.git.commit('-m', f"feat: {improvement.title}\n\n{improvement.description}")
            
            # Push branch
            repo.git.push('origin', branch_name)
            
            # Create pull request
            pr = self.repo.create_pull(
                title=f"🤖 Autonomous Improvement: {improvement.title}",
                body=f"""
## Autonomous Improvement

**Description:** {improvement.description}

**Improvement ID:** {improvement.improvement_id}
**Priority:** {improvement.priority}
**Estimated Impact:** {improvement.estimated_impact}
**Risk Level:** {improvement.risk_level}

### Changes Made:
{self._format_changes_for_pr(improvement.changes)}

### AI Analysis:
- **Average Confidence:** {sum(c.confidence_score for c in improvement.changes) / len(improvement.changes):.2f}
- **Change Type:** {', '.join(set(c.change_type.value for c in improvement.changes))}

---
*This improvement was implemented autonomously by Eliza AI.*
                """,
                head=branch_name,
                base="main"
            )
            
            # Auto-merge if confidence is very high
            avg_confidence = sum(c.confidence_score for c in improvement.changes) / len(improvement.changes)
            if avg_confidence >= self.config["auto_merge_threshold"] and improvement.risk_level == "low":
                # Wait a moment then merge
                await asyncio.sleep(5)
                pr.merge(commit_message=f"🤖 Auto-merge: {improvement.title}")
                
                return {
                    "success": True,
                    "pr_url": pr.html_url,
                    "commit_hash": pr.merge_commit_sha,
                    "auto_merged": True
                }
            
            return {
                "success": True,
                "pr_url": pr.html_url,
                "auto_merged": False
            }
            
        except Exception as e:
            logger.error(f"Error implementing improvement autonomously: {e}")
            return {"success": False, "error": str(e)}

    async def _create_improvement_pr(self, improvement: ImprovementPlan) -> Dict[str, Any]:
        """Create PR for manual review"""
        try:
            # Similar to autonomous implementation but without auto-merge
            branch_name = f"{self.config['branch_prefix']}{improvement.improvement_id}"
            
            repo = git.Repo(self.local_repo_path)
            repo.git.checkout('-b', branch_name)
            
            for change in improvement.changes:
                file_path = os.path.join(self.local_repo_path, change.file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(change.new_content)
            
            repo.git.add('.')
            repo.git.commit('-m', f"feat: {improvement.title}\n\n{improvement.description}")
            repo.git.push('origin', branch_name)
            
            pr = self.repo.create_pull(
                title=f"🔍 Review Required: {improvement.title}",
                body=f"""
## Improvement Requiring Review

**Description:** {improvement.description}

**Improvement ID:** {improvement.improvement_id}
**Priority:** {improvement.priority}
**Risk Level:** {improvement.risk_level}

⚠️ **This improvement requires manual review before merging.**

### Changes Made:
{self._format_changes_for_pr(improvement.changes)}

---
*This improvement was proposed by Eliza AI but requires human review.*
                """,
                head=branch_name,
                base="main"
            )
            
            return {"success": True, "pr_url": pr.html_url}
            
        except Exception as e:
            logger.error(f"Error creating improvement PR: {e}")
            return {"success": False, "error": str(e)}

    def _format_changes_for_pr(self, changes: List[CodeChange]) -> str:
        """Format changes for PR description"""
        formatted = []
        for change in changes:
            formatted.append(f"- **{change.file_path}**: {change.description} (Confidence: {change.confidence_score:.2f})")
        return '\n'.join(formatted)

    async def monitor_autonomous_changes(self) -> Dict[str, Any]:
        """Monitor the success of autonomous changes"""
        try:
            # Get recent PRs created by the bot
            prs = self.repo.get_pulls(state='all', sort='created', direction='desc')
            
            autonomous_prs = []
            for pr in prs:
                if pr.title.startswith('🤖 Autonomous Improvement:'):
                    autonomous_prs.append({
                        "title": pr.title,
                        "state": pr.state,
                        "merged": pr.merged,
                        "created_at": pr.created_at.isoformat(),
                        "url": pr.html_url
                    })
                    
                    if len(autonomous_prs) >= 20:  # Limit to recent 20
                        break
            
            # Calculate success metrics
            total_prs = len(autonomous_prs)
            merged_prs = sum(1 for pr in autonomous_prs if pr["merged"])
            success_rate = merged_prs / total_prs if total_prs > 0 else 0
            
            return {
                "total_autonomous_prs": total_prs,
                "merged_prs": merged_prs,
                "success_rate": success_rate,
                "recent_prs": autonomous_prs[:10]
            }
            
        except Exception as e:
            logger.error(f"Error monitoring autonomous changes: {e}")
            return {"error": str(e)}

# Global instance
github_improvement_engine = None

def initialize_github_integration(repo_owner: str, repo_name: str, pat_token: str):
    """Initialize GitHub integration"""
    global github_improvement_engine
    github_improvement_engine = GitHubSelfImprovementEngine(repo_owner, repo_name, pat_token)
    return github_improvement_engine

async def run_autonomous_improvement_cycle():
    """Run a complete autonomous improvement cycle"""
    if not github_improvement_engine:
        raise ValueError("GitHub integration not initialized")
    
    # Analyze repository
    improvements = await github_improvement_engine.analyze_repository_for_improvements()
    
    # Implement improvements
    results = await github_improvement_engine.implement_improvements_autonomously(improvements)
    
    # Monitor results
    monitoring_data = await github_improvement_engine.monitor_autonomous_changes()
    
    return {
        "improvements_found": len(improvements),
        "implementation_results": results,
        "monitoring_data": monitoring_data
    }

