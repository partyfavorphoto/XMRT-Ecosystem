"""
Repository Discovery Service - XMRT Ecosystem Analysis
Discovers and analyzes repositories in the XMRT ecosystem for learning opportunities.
"""

import asyncio
import logging
import aiohttp
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
import json
import re

@dataclass
class RepositoryInfo:
    """Information about a discovered repository"""
    name: str
    full_name: str
    url: str
    description: str
    language: str
    stars: int
    forks: int
    last_updated: datetime
    topics: List[str]
    readme_content: str = ""
    repo_type: str = "general"
    complexity_score: float = 0.5
    integration_score: float = 0.5
    commit_frequency: float = 0.0

class RepositoryDiscoveryService:
    """
    Service for discovering and analyzing XMRT ecosystem repositories

    Features:
    - GitHub API integration for repository discovery
    - Repository classification and scoring
    - Integration potential analysis
    - Learning opportunity assessment
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None

        # GitHub API configuration
        self.github_api_base = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "XMRT-Enhanced-Eliza-Agent"
        }

        # Repository classification patterns
        self.classification_patterns = {
            'ai_agent': [
                r'eliza', r'agent', r'ai', r'llm', r'neural', r'ml', r'model', 
                r'chat', r'conversation', r'nlp', r'language'
            ],
            'networking': [
                r'network', r'mesh', r'p2p', r'protocol', r'socket', r'tcp', 
                r'udp', r'http', r'websocket', r'api', r'rpc'
            ],
            'governance': [
                r'governance', r'dao', r'voting', r'proposal', r'democracy',
                r'consensus', r'multisig', r'treasury', r'council'
            ],
            'defi': [
                r'defi', r'dex', r'swap', r'liquidity', r'yield', r'farming',
                r'staking', r'lending', r'borrowing', r'amm'
            ],
            'nft': [
                r'nft', r'token', r'erc721', r'erc1155', r'collectible',
                r'marketplace', r'metadata', r'opensea'
            ],
            'infrastructure': [
                r'infra', r'deploy', r'docker', r'kubernetes', r'ci/cd',
                r'pipeline', r'monitoring', r'logging', r'metrics'
            ]
        }

        # Cache for discovered repositories
        self.repository_cache: Dict[str, RepositoryInfo] = {}
        self.cache_expiry = timedelta(hours=6)
        self.last_cache_update = datetime.min

    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=30)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=self.headers
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def discover_xmrt_repositories(self) -> List[Dict[str, Any]]:
        """
        Discover all XMRT-related repositories

        Returns:
            List of repository information dictionaries
        """
        try:
            # Check cache first
            if self._is_cache_valid():
                self.logger.info("Using cached repository data")
                return [repo.__dict__ for repo in self.repository_cache.values()]

            self.logger.info("Starting XMRT repository discovery")

            # Ensure session is available
            if not self.session:
                await self.__aenter__()

            discovered_repos = []

            # Search strategies
            search_queries = [
                "xmrt",
                "xmrt-ecosystem", 
                "eliza xmrt",
                "user:DevGruGold xmrt",
                "org:DevGruGold"
            ]

            for query in search_queries:
                repos = await self._search_repositories(query)
                discovered_repos.extend(repos)

            # Remove duplicates and enrich data
            unique_repos = self._deduplicate_repositories(discovered_repos)
            enriched_repos = await self._enrich_repository_data(unique_repos)

            # Update cache
            self._update_cache(enriched_repos)

            self.logger.info(f"Discovered {len(enriched_repos)} XMRT repositories")

            return [repo.__dict__ for repo in enriched_repos]

        except Exception as e:
            self.logger.error(f"Repository discovery failed: {e}")
            return []

    async def _search_repositories(self, query: str) -> List[Dict[str, Any]]:
        """Search GitHub repositories by query"""
        try:
            url = f"{self.github_api_base}/search/repositories"
            params = {
                "q": query,
                "sort": "updated",
                "order": "desc",
                "per_page": 100
            }

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('items', [])
                elif response.status == 403:
                    # Rate limited - wait and retry
                    self.logger.warning("GitHub API rate limited, waiting...")
                    await asyncio.sleep(60)
                    return []
                else:
                    self.logger.warning(f"GitHub search failed: {response.status}")
                    return []

        except Exception as e:
            self.logger.error(f"Repository search failed for query '{query}': {e}")
            return []

    def _deduplicate_repositories(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate repositories based on full name"""
        seen = set()
        unique_repos = []

        for repo in repos:
            full_name = repo.get('full_name', '')
            if full_name and full_name not in seen:
                seen.add(full_name)
                unique_repos.append(repo)

        return unique_repos

    async def _enrich_repository_data(self, repos: List[Dict[str, Any]]) -> List[RepositoryInfo]:
        """Enrich repository data with additional analysis"""
        enriched_repos = []

        # Process repositories in batches to avoid rate limiting
        batch_size = 10
        for i in range(0, len(repos), batch_size):
            batch = repos[i:i + batch_size]

            tasks = []
            for repo in batch:
                task = self._analyze_single_repository(repo)
                tasks.append(task)

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, RepositoryInfo):
                    enriched_repos.append(result)
                elif isinstance(result, Exception):
                    self.logger.warning(f"Repository analysis failed: {result}")

            # Rate limiting delay
            if i + batch_size < len(repos):
                await asyncio.sleep(1)

        return enriched_repos

    async def _analyze_single_repository(self, repo_data: Dict[str, Any]) -> RepositoryInfo:
        """Analyze a single repository and create RepositoryInfo"""
        try:
            # Extract basic info
            name = repo_data.get('name', '')
            full_name = repo_data.get('full_name', '')
            url = repo_data.get('html_url', '')
            description = repo_data.get('description', '') or ''
            language = repo_data.get('language', '') or 'Unknown'
            stars = repo_data.get('stargazers_count', 0)
            forks = repo_data.get('forks_count', 0)
            topics = repo_data.get('topics', [])

            # Parse last updated
            updated_at = repo_data.get('updated_at', '')
            try:
                last_updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            except:
                last_updated = datetime.utcnow()

            # Get README content
            readme_content = await self._fetch_readme(full_name)

            # Classify repository type
            repo_type = self._classify_repository(name, description, readme_content, topics)

            # Calculate scores
            complexity_score = self._calculate_complexity_score(repo_data, readme_content)
            integration_score = self._calculate_integration_score(repo_data, repo_type)
            commit_frequency = await self._calculate_commit_frequency(full_name)

            return RepositoryInfo(
                name=name,
                full_name=full_name,
                url=url,
                description=description,
                language=language,
                stars=stars,
                forks=forks,
                last_updated=last_updated,
                topics=topics,
                readme_content=readme_content[:1000],  # Truncate for storage
                repo_type=repo_type,
                complexity_score=complexity_score,
                integration_score=integration_score,
                commit_frequency=commit_frequency
            )

        except Exception as e:
            self.logger.error(f"Failed to analyze repository {repo_data.get('name', 'unknown')}: {e}")
            # Return minimal repository info on error
            return RepositoryInfo(
                name=repo_data.get('name', 'unknown'),
                full_name=repo_data.get('full_name', ''),
                url=repo_data.get('html_url', ''),
                description=repo_data.get('description', '') or '',
                language=repo_data.get('language', '') or 'Unknown',
                stars=repo_data.get('stargazers_count', 0),
                forks=repo_data.get('forks_count', 0),
                last_updated=datetime.utcnow(),
                topics=repo_data.get('topics', [])
            )

    async def _fetch_readme(self, full_name: str) -> str:
        """Fetch README content from repository"""
        try:
            url = f"{self.github_api_base}/repos/{full_name}/readme"

            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # README content is base64 encoded
                    import base64
                    content = base64.b64decode(data.get('content', '')).decode('utf-8')
                    return content
                else:
                    return ""

        except Exception as e:
            self.logger.debug(f"Failed to fetch README for {full_name}: {e}")
            return ""

    def _classify_repository(self, name: str, description: str, readme: str, topics: List[str]) -> str:
        """Classify repository type based on name, description, README, and topics"""
        text_to_analyze = f"{name} {description} {readme} {' '.join(topics)}".lower()

        scores = {}
        for repo_type, patterns in self.classification_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_to_analyze))
                score += matches
            scores[repo_type] = score

        # Return type with highest score, default to 'general'
        if not scores or max(scores.values()) == 0:
            return 'general'

        return max(scores.items(), key=lambda x: x[1])[0]

    def _calculate_complexity_score(self, repo_data: Dict[str, Any], readme: str) -> float:
        """Calculate repository complexity score (0.0 to 1.0)"""
        try:
            score = 0.0

            # Size indicators
            size = repo_data.get('size', 0)  # KB
            if size > 10000:  # > 10MB
                score += 0.3
            elif size > 1000:  # > 1MB
                score += 0.2
            elif size > 100:  # > 100KB
                score += 0.1

            # Language complexity
            language = repo_data.get('language', '').lower()
            complex_languages = ['rust', 'cpp', 'c++', 'haskell', 'scala', 'erlang']
            moderate_languages = ['python', 'javascript', 'typescript', 'go', 'java']

            if language in complex_languages:
                score += 0.3
            elif language in moderate_languages:
                score += 0.2

            # README complexity (documentation quality)
            if len(readme) > 5000:
                score += 0.2
            elif len(readme) > 1000:
                score += 0.1

            # Community engagement
            stars = repo_data.get('stargazers_count', 0)
            forks = repo_data.get('forks_count', 0)

            if stars > 100 or forks > 50:
                score += 0.2
            elif stars > 10 or forks > 5:
                score += 0.1

            return min(score, 1.0)

        except Exception:
            return 0.5  # Default moderate complexity

    def _calculate_integration_score(self, repo_data: Dict[str, Any], repo_type: str) -> float:
        """Calculate integration potential score (0.0 to 1.0)"""
        try:
            score = 0.0

            # Repository type weight
            type_weights = {
                'ai_agent': 1.0,
                'networking': 0.9,
                'governance': 0.8,
                'defi': 0.7,
                'infrastructure': 0.8,
                'nft': 0.6,
                'general': 0.4
            }
            score += type_weights.get(repo_type, 0.4)

            # Language compatibility
            language = repo_data.get('language', '').lower()
            if language in ['python', 'javascript', 'typescript']:
                score += 0.3
            elif language in ['rust', 'go', 'java']:
                score += 0.2

            # Recent activity
            updated_at = repo_data.get('updated_at', '')
            if updated_at:
                try:
                    last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    days_since_update = (datetime.utcnow() - last_update).days

                    if days_since_update < 7:
                        score += 0.2
                    elif days_since_update < 30:
                        score += 0.1
                except:
                    pass

            # Has issues/discussions (indicates active development)
            if repo_data.get('has_issues', False):
                score += 0.1

            return min(score / 1.6, 1.0)  # Normalize to 0-1 range

        except Exception:
            return 0.5  # Default moderate integration potential

    async def _calculate_commit_frequency(self, full_name: str) -> float:
        """Calculate recent commit frequency (commits per week)"""
        try:
            # Get commits from last 4 weeks
            since_date = (datetime.utcnow() - timedelta(weeks=4)).isoformat()
            url = f"{self.github_api_base}/repos/{full_name}/commits"
            params = {
                "since": since_date,
                "per_page": 100
            }

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    commits = await response.json()
                    return len(commits) / 4.0  # commits per week
                else:
                    return 0.0

        except Exception as e:
            self.logger.debug(f"Failed to calculate commit frequency for {full_name}: {e}")
            return 0.0

    def _is_cache_valid(self) -> bool:
        """Check if repository cache is still valid"""
        return (
            self.repository_cache and 
            datetime.utcnow() - self.last_cache_update < self.cache_expiry
        )

    def _update_cache(self, repos: List[RepositoryInfo]):
        """Update repository cache"""
        self.repository_cache.clear()
        for repo in repos:
            self.repository_cache[repo.full_name] = repo
        self.last_cache_update = datetime.utcnow()

    async def get_repository_by_name(self, name: str) -> Optional[RepositoryInfo]:
        """Get specific repository information by name"""
        # Check cache first
        for repo in self.repository_cache.values():
            if repo.name.lower() == name.lower():
                return repo

        # If not in cache, search specifically
        repos = await self.discover_xmrt_repositories()
        for repo_dict in repos:
            if repo_dict['name'].lower() == name.lower():
                return RepositoryInfo(**repo_dict)

        return None

    async def get_high_value_repositories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get repositories with highest learning/integration value"""
        repos = await self.discover_xmrt_repositories()

        # Sort by combined score (integration potential + complexity)
        def score_repo(repo):
            return (repo['integration_score'] * 0.6 + 
                   repo['complexity_score'] * 0.3 + 
                   min(repo['commit_frequency'] / 10.0, 1.0) * 0.1)

        sorted_repos = sorted(repos, key=score_repo, reverse=True)
        return sorted_repos[:limit]

# Test the service
async def test_repository_discovery():
    """Test the repository discovery service"""
    async with RepositoryDiscoveryService() as discovery:
        repos = await discovery.discover_xmrt_repositories()
        print(f"Discovered {len(repos)} repositories")

        if repos:
            high_value = await discovery.get_high_value_repositories(5)
            print(f"Top 5 high-value repositories:")
            for i, repo in enumerate(high_value, 1):
                print(f"{i}. {repo['name']} - {repo['repo_type']} "
                      f"(Integration: {repo['integration_score']:.2f}, "
                      f"Complexity: {repo['complexity_score']:.2f})")

if __name__ == "__main__":
    asyncio.run(test_repository_discovery())
