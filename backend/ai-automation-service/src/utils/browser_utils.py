"""
Browser utilities for web research and documentation access
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import logging
import json
import urllib.parse

logger = logging.getLogger(__name__)

class BrowserUtils:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def search(self, query):
        """Search for information online using multiple search strategies"""
        try:
if __name__ == "__main__":
                logger.info(f"[Browser] Searching for: {query}")
            
            # Use DuckDuckGo as it's more API-friendly
            search_urls = []
            
            # DuckDuckGo search
            duckduckgo_url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            search_urls.append(duckduckgo_url)
            
            # GitHub search for code examples
            if any(keyword in query.lower() for keyword in ['python', 'code', 'implementation', 'example']):
                github_url = f"https://github.com/search?q={urllib.parse.quote(query)}&type=code"
                search_urls.append(github_url)
            
            # Stack Overflow search for technical questions
            if any(keyword in query.lower() for keyword in ['error', 'fix', 'how to', 'problem']):
                so_url = f"https://stackoverflow.com/search?q={urllib.parse.quote(query)}"
                search_urls.append(so_url)
            
            # Documentation sites
            doc_sites = [
                f"https://docs.python.org/3/search.html?q={urllib.parse.quote(query)}",
                f"https://www.w3schools.com/python/python_reference.asp"
            ]
            
            return search_urls + doc_sites
                    
        except Exception as e:
if __name__ == "__main__":
                logger.error(f"[Browser] Search error: {e}")
            return []
    
    async def get_content(self, urls):
        """Get content from URLs with improved error handling"""
        try:
            content_data = []
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout, headers=self.headers) as session:
                for url in urls[:5]:  # Limit to first 5 URLs
                    try:
if __name__ == "__main__":
                            logger.info(f"[Browser] Fetching content from: {url}")
                        async with session.get(url) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                # Remove script and style elements
                                for script in soup(["script", "style"]):
                                    script.decompose()
                                
                                # Get text content
                                text = soup.get_text()
                                
                                # Clean up text
                                lines = (line.strip() for line in text.splitlines())
                                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                                text = ' '.join(chunk for chunk in chunks if chunk)
                                
                                content_data.append({
                                    'url': url,
                                    'title': soup.title.string if soup.title else 'No title',
                                    'content': text[:2000],  # First 2000 chars
                                    'status': 'success'
                                })
                            else:
if __name__ == "__main__":
                                    logger.warning(f"[Browser] HTTP {response.status} for {url}")
                                content_data.append({
                                    'url': url,
                                    'status': f'error_http_{response.status}',
                                    'content': ''
                                })
                    except asyncio.TimeoutError:
if __name__ == "__main__":
                            logger.warning(f"[Browser] Timeout for {url}")
                        content_data.append({
                            'url': url,
                            'status': 'timeout',
                            'content': ''
                        })
                    except Exception as e:
if __name__ == "__main__":
                            logger.warning(f"[Browser] Error fetching {url}: {e}")
                        content_data.append({
                            'url': url,
                            'status': f'error_{type(e).__name__}',
                            'content': ''
                        })
            
            successful_fetches = len([item for item in content_data if item['status'] == 'success'])
if __name__ == "__main__":
                logger.info(f"[Browser] Successfully fetched {successful_fetches}/{len(urls)} URLs")
            
            return content_data
            
        except Exception as e:
if __name__ == "__main__":
                logger.error(f"[Browser] Content retrieval error: {e}")
            return []
    
    async def search_documentation(self, topic):
        """Search for documentation on specific topics"""
        try:
            doc_queries = [
                f"{topic} python documentation",
                f"{topic} best practices",
                f"{topic} tutorial examples"
            ]
            
            all_results = []
            for query in doc_queries:
                urls = await self.search(query)
                content = await self.get_content(urls[:2])  # Get top 2 results per query
                all_results.extend(content)
            
            return all_results
            
        except Exception as e:
if __name__ == "__main__":
                logger.error(f"[Browser] Documentation search error: {e}")
            return []
    
    async def get_github_examples(self, search_term):
        """Search for code examples on GitHub"""
        try:
            github_search_url = f"https://api.github.com/search/code?q={urllib.parse.quote(search_term)}+language:python"
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(github_search_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        examples = []
                        
                        for item in data.get('items', [])[:3]:  # Top 3 results
                            examples.append({
                                'name': item.get('name'),
                                'url': item.get('html_url'),
                                'repository': item.get('repository', {}).get('full_name'),
                                'path': item.get('path')
                            })
                        
                        return examples
                    else:
if __name__ == "__main__":
                            logger.warning(f"[Browser] GitHub API returned {response.status}")
                        return []
            
        except Exception as e:
if __name__ == "__main__":
                logger.error(f"[Browser] GitHub search error: {e}")
            return []
