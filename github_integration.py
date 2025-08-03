#!/usr/bin/env python3
"""
GitHub Integration
Self-improvement and code analysis engine for XMRT-Ecosystem.
"""

import asyncio
import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from github import Github
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubIntegration:
    """GitHub self-improvement and code analysis engine."""
    
    def __init__(self):        self.github_token = os.getenv('GITHUB_PAT')
        self.repo_name = "DevGruGold/XMRT-Ecosystem"
        self.github = Github(self.github_token)
        self.repo = self.github.get_repo(self.repo_name)
        
        # Initialize OpenAI
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        self.improvement_queue = []
        self.analysis_history = []
        self.auto_pr_enabled = True
        
    async def analyze_repository(self) -> Dict[str, Any]:
        """Perform comprehensive repository analysis."""
if __name__ == "__main__":
            logger.info("Starting repository analysis...")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'code_quality': await self._analyze_code_quality(),
            'security_assessment': await self._analyze_security(),
            'performance_opportunities': await self._identify_performance_opportunities(),
            'documentation_gaps': await self._analyze_documentation(),
            'dependency_analysis': await self._analyze_dependencies(),
            'improvement_suggestions': []
        }
        
        # Generate improvement suggestions
        analysis['improvement_suggestions'] = await self._generate_improvement_suggestions(analysis)
        
        self.analysis_history.append(analysis)
        return analysis
    
    async def _analyze_code_quality(self) -> Dict[str, Any]:
        """Analyze code quality across the repository."""
        quality_metrics = {
            'python_files': 0,
            'javascript_files': 0,
            'solidity_files': 0,
            'total_lines': 0,
            'complexity_score': 0,
            'maintainability_score': 0,
            'issues': []
        }
        
        try:
            # Get all Python files
            contents = self.repo.get_contents("")
            python_files = await self._get_files_by_extension(contents, '.py')
            
            quality_metrics['python_files'] = len(python_files)
            
            # Analyze each Python file
            for file_path in python_files[:5]:  # Limit to first 5 files for demo
                file_content = self.repo.get_contents(file_path)
                code = file_content.decoded_content.decode('utf-8')
                
                # Simple quality checks
                lines = code.split('\n')
                quality_metrics['total_lines'] += len(lines)
                
                # Check for common issues
                if 'TODO' in code:
                    quality_metrics['issues'].append(f"TODO comments found in {file_path}")
                
                if len([line for line in lines if len(line) > 100]) > 0:
                    quality_metrics['issues'].append(f"Long lines detected in {file_path}")
            
            # Calculate scores
            quality_metrics['complexity_score'] = min(100, max(0, 100 - len(quality_metrics['issues']) * 10))
            quality_metrics['maintainability_score'] = min(100, max(0, 90 - len(quality_metrics['issues']) * 5))
            
        except Exception as e:
            pass  # <-- AUTO-INSERTED
if __name__ == "__main__":
                logger.error(f"Error analyzing code quality: {e}")
            quality_metrics['error'] = str(e)
        
        return quality_metrics
    
    async def _get_files_by_extension(self, contents, extension: str) -> List[str]:
        """Get all files with specified extension."""
        files = []
        
        for content in contents:
            if content.type == "file" and content.name.endswith(extension):
                files.append(content.path)
            elif content.type == "dir":
                try:
                    subcontents = self.repo.get_contents(content.path)
                    subfiles = await self._get_files_by_extension(subcontents, extension)
                    files.extend(subfiles)
                except Exception as e:
                    pass  # <-- AUTO-INSERTED
if __name__ == "__main__":
                        logger.warning(f"Error accessing directory {content.path}: {e}")
        
        return files
    
    async def _analyze_security(self) -> Dict[str, Any]:
        """Analyze security aspects of the repository."""
        security_analysis = {
            'secrets_exposed': False,
            'dependency_vulnerabilities': [],
            'code_security_issues': [],
            'security_score': 85
        }
        
        try:
            # Check for exposed secrets
            env_example = self.repo.get_contents(".env.example")
            env_content = env_example.decoded_content.decode('utf-8')
            
            if 'your_' not in env_content.lower():
                security_analysis['secrets_exposed'] = True
                security_analysis['code_security_issues'].append("Potential secrets in .env.example")
            
            # Check for hardcoded secrets in code
            python_files = await self._get_files_by_extension(self.repo.get_contents(""), '.py')
            
            for file_path in python_files[:3]:  # Check first 3 files
                try:
                    file_content = self.repo.get_contents(file_path)
                    code = file_content.decoded_content.decode('utf-8')
                    
                    if 'api_key' in code.lower() and '=' in code:
                        security_analysis['code_security_issues'].append(f"Potential hardcoded API key in {file_path}")
                except Exception:
                    continue
            
            # Calculate security score
            issues_count = len(security_analysis['code_security_issues'])
            security_analysis['security_score'] = max(0, 100 - issues_count * 15)
            
        except Exception as e:
            pass  # <-- AUTO-INSERTED
if __name__ == "__main__":
                logger.error(f"Error in security analysis: {e}")
            security_analysis['error'] = str(e)
        
        return security_analysis
    
    async def _identify_performance_opportunities(self) -> Dict[str, Any]:
        """Identify performance optimization opportunities."""
        performance_analysis = {
            'optimization_opportunities': [],
            'caching_suggestions': [],
            'database_optimizations': [],
            'performance_score': 80
        }
        
        # Simulate performance analysis
        performance_analysis['optimization_opportunities'] = [
            "Consider implementing connection pooling for database operations",
            "Add caching layer for frequently accessed data",
            "Optimize API response times with pagination"
        ]
        
        performance_analysis['caching_suggestions'] = [
            "Implement Redis caching for governance proposals",
            "Add browser caching headers for static assets"
        ]
        
        return performance_analysis
    
    async def _analyze_documentation(self) -> Dict[str, Any]:
        """Analyze documentation completeness and quality."""
        doc_analysis = {
            'readme_quality': 0,
            'api_documentation': False,
            'code_comments': 0,
            'missing_docs': [],
            'documentation_score': 0
        }
        
        try:
            # Check README
            readme = self.repo.get_contents("README.md")
            readme_content = readme.decoded_content.decode('utf-8')
            
            # Simple quality metrics
            doc_analysis['readme_quality'] = min(100, len(readme_content) // 100)
            
            # Check for API documentation
            try:
                api_docs = self.repo.get_contents("docs")
                doc_analysis['api_documentation'] = True
            except:
                doc_analysis['missing_docs'].append("API documentation")
            
            # Calculate documentation score
            doc_analysis['documentation_score'] = (
                doc_analysis['readme_quality'] * 0.4 +
                (100 if doc_analysis['api_documentation'] else 0) * 0.6
            )
            
        except Exception as e:
            pass  # <-- AUTO-INSERTED
if __name__ == "__main__":
                logger.error(f"Error analyzing documentation: {e}")
            doc_analysis['error'] = str(e)
        
        return doc_analysis
    
    async def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies."""
        dependency_analysis = {
            'outdated_dependencies': [],
            'security_vulnerabilities': [],
            'unused_dependencies': [],
            'dependency_score': 90
        }
        
        try:
            # Check package.json
            package_json = self.repo.get_contents("package.json")
            package_content = json.loads(package_json.decoded_content.decode('utf-8'))
            
            dependencies = package_content.get('dependencies', {})
            dev_dependencies = package_content.get('devDependencies', {})
            
            # Simulate dependency analysis
            if len(dependencies) > 20:
                dependency_analysis['outdated_dependencies'].append("Consider reviewing large number of dependencies")
            
            # Check requirements.txt
            try:
                requirements = self.repo.get_contents("requirements.txt")
                req_content = requirements.decoded_content.decode('utf-8')
                
                if 'flask' in req_content.lower():
                    dependency_analysis['security_vulnerabilities'].append("Ensure Flask is updated to latest secure version")
            except:
                pass
            
        except Exception as e:
            pass  # <-- AUTO-INSERTED
if __name__ == "__main__":
                logger.error(f"Error analyzing dependencies: {e}")
            dependency_analysis['error'] = str(e)
        
        return dependency_analysis
    
    async def _generate_improvement_suggestions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate improvement suggestions based on analysis."""
        suggestions = []
        
        # Code quality improvements
        code_quality = analysis.get('code_quality', {})
        if code_quality.get('complexity_score', 100) < 80:
            suggestions.append({
                'type': 'code_quality',
                'priority': 'high',
                'title': 'Improve code complexity',
                'description': 'Refactor complex functions to improve maintainability',
                'estimated_effort': 'medium'
            })
        
        # Security improvements
        security = analysis.get('security_assessment', {})
        if security.get('security_score', 100) < 90:
            suggestions.append({
                'type': 'security',
                'priority': 'critical',
                'title': 'Address security issues',
                'description': 'Fix identified security vulnerabilities',
                'estimated_effort': 'high'
            })
        
        # Performance improvements
        performance = analysis.get('performance_opportunities', {})
        if performance.get('optimization_opportunities'):
            suggestions.append({
                'type': 'performance',
                'priority': 'medium',
                'title': 'Implement performance optimizations',
                'description': 'Add caching and optimize database queries',
                'estimated_effort': 'medium'
            })
        
        # Documentation improvements
        documentation = analysis.get('documentation_gaps', {})
        if documentation.get('documentation_score', 100) < 80:
            suggestions.append({
                'type': 'documentation',
                'priority': 'low',
                'title': 'Improve documentation',
                'description': 'Add missing API documentation and code comments',
                'estimated_effort': 'low'
            })
        
        return suggestions
    
    async def create_improvement_pr(self, improvement: Dict[str, Any]) -> Optional[str]:
        """Create a pull request for an improvement."""
        if not self.auto_pr_enabled:
if __name__ == "__main__":
                logger.info("Auto PR creation is disabled")
            return None
        
        try:
            # Create a new branch
            branch_name = f"auto-improvement-{int(datetime.now().timestamp())}"
            base_branch = self.repo.get_branch(self.repo.default_branch)
            
            self.repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base_branch.commit.sha
            )
            
            # Create improvement file
            improvement_content = self._generate_improvement_code(improvement)
            
            if improvement_content:
                file_path = f"improvements/{improvement['type']}_{int(datetime.now().timestamp())}.py"
                
                self.repo.create_file(
                    path=file_path,
                    message=f"Auto-improvement: {improvement['title']}",
                    content=improvement_content,
                    branch=branch_name
                )
                
                # Create pull request
                pr = self.repo.create_pull(
                    title=f"🤖 Auto-improvement: {improvement['title']}",
                    body=f"""
## Autonomous Improvement

**Type:** {improvement['type']}
**Priority:** {improvement['priority']}

### Description
{improvement['description']}

### Estimated Effort
{improvement['estimated_effort']}

### Changes Made
- Added improvement implementation
- Automated code enhancement
- Self-improvement cycle execution

This PR was automatically generated by the GitHub Integration autonomous system.
                    """,
                    head=branch_name,
                    base=self.repo.default_branch
                )
                
if __name__ == "__main__":
                    logger.info(f"Created improvement PR: {pr.html_url}")
                return pr.html_url
            
        except Exception as e:
            pass  # <-- AUTO-INSERTED
if __name__ == "__main__":
                logger.error(f"Error creating improvement PR: {e}")
            return None
    
    def _generate_improvement_code(self, improvement: Dict[str, Any]) -> Optional[str]:
        """Generate code for the improvement."""
        if improvement['type'] == 'performance':
            return 