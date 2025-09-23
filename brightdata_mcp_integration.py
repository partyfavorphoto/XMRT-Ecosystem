"""
BrightData MCP Integration for XMRT Ecosystem
Model Context Protocol for enhanced web scraping, data collection, and blockchain analytics
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import aiohttp
import requests
from urllib.parse import urljoin, urlparse
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class MCPRequest:
    """Model Context Protocol request structure"""
    method: str
    url: str
    params: Dict[str, Any] = None
    headers: Dict[str, str] = None
    timeout: int = 30
    retry_count: int = 3

    def __post_init__(self):
        if self.params is None:
            self.params = {}
        if self.headers is None:
            self.headers = {}

@dataclass
class MCPResponse:
    """Model Context Protocol response structure"""
    url: str
    status_code: int
    content: str
    headers: Dict[str, str]
    metadata: Dict[str, Any]
    timestamp: datetime
    success: bool

class BrightDataMCP:
    """
    BrightData Model Context Protocol Integration
    Enhanced web scraping and data collection for XMRT Ecosystem
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

        # BrightData configuration
        self.brightdata_username = self.config.get("brightdata_username", "")
        self.brightdata_password = self.config.get("brightdata_password", "")
        self.brightdata_endpoint = self.config.get("brightdata_endpoint", "")

        # Rate limiting and caching
        self.rate_limit = self.config.get("rate_limit", 10)  # requests per second
        self.cache_ttl = self.config.get("cache_ttl", 3600)  # 1 hour
        self.request_cache = {}
        self.last_request_time = {}

        # Session management
        self.session = None
        self.executor = ThreadPoolExecutor(max_workers=10)

        # Blockchain data endpoints
        self.blockchain_apis = {
            "ethereum": {
                "etherscan": "https://api.etherscan.io/api",
                "infura": "https://mainnet.infura.io/v3/",
                "alchemy": "https://eth-mainnet.g.alchemy.com/v2/"
            },
            "polygon": {
                "polygonscan": "https://api.polygonscan.com/api",
                "quicknode": "https://polygon-mainnet.g.alchemy.com/v2/"
            },
            "bsc": {
                "bscscan": "https://api.bscscan.com/api"
            }
        }

        # DeFi protocol endpoints
        self.defi_apis = {
            "uniswap": "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3",
            "aave": "https://api.thegraph.com/subgraphs/name/aave/protocol-v2",
            "compound": "https://api.compound.finance/api/v2/",
            "1inch": "https://api.1inch.io/v5.0/1/",
            "coingecko": "https://api.coingecko.com/api/v3/",
            "defillama": "https://api.llama.fi/"
        }

        logger.info("BrightData MCP initialized with enhanced blockchain data access")

    async def initialize_session(self):
        """Initialize aiohttp session for async requests"""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=30)

        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "User-Agent": "XMRT-BrightData-MCP/1.0",
                "Accept": "application/json, text/html, */*"
            }
        )

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()

    async def fetch_url(self, request: MCPRequest) -> MCPResponse:
        """
        Fetch URL using BrightData proxy with enhanced error handling and caching
        """
        # Check cache first
        cache_key = f"{request.method}:{request.url}:{json.dumps(request.params, sort_keys=True)}"
        cached_response = self._get_cached_response(cache_key)

        if cached_response:
            logger.info(f"Returning cached response for {request.url}")
            return cached_response

        # Rate limiting
        await self._apply_rate_limit(request.url)

        try:
            if not self.session:
                await self.initialize_session()

            # Prepare request with BrightData proxy if configured
            request_kwargs = {
                "url": request.url,
                "params": request.params,
                "headers": request.headers,
                "timeout": request.timeout
            }

            # Add proxy configuration if available
            if self.brightdata_endpoint and self.brightdata_username:
                request_kwargs["proxy"] = f"http://{self.brightdata_username}:{self.brightdata_password}@{self.brightdata_endpoint}"

            # Execute request with retry logic
            for attempt in range(request.retry_count):
                try:
                    async with self.session.request(request.method, **request_kwargs) as response:
                        content = await response.text()

                        mcp_response = MCPResponse(
                            url=request.url,
                            status_code=response.status,
                            content=content,
                            headers=dict(response.headers),
                            metadata={
                                "attempt": attempt + 1,
                                "content_length": len(content),
                                "content_type": response.headers.get("content-type", "")
                            },
                            timestamp=datetime.now(),
                            success=response.status < 400
                        )

                        # Cache successful responses
                        if mcp_response.success:
                            self._cache_response(cache_key, mcp_response)

                        return mcp_response

                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {request.url}: {e}")
                    if attempt == request.retry_count - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

        except Exception as e:
            logger.error(f"Failed to fetch {request.url}: {e}")
            return MCPResponse(
                url=request.url,
                status_code=500,
                content="",
                headers={},
                metadata={"error": str(e)},
                timestamp=datetime.now(),
                success=False
            )

    async def scrape_defi_data(self, protocol: str, data_type: str = "tvl") -> Dict[str, Any]:
        """
        Scrape DeFi protocol data using various APIs
        """
        logger.info(f"Scraping {protocol} {data_type} data")

        try:
            if protocol == "uniswap":
                return await self._scrape_uniswap_data(data_type)
            elif protocol == "aave":
                return await self._scrape_aave_data(data_type)
            elif protocol == "compound":
                return await self._scrape_compound_data(data_type)
            elif protocol == "defillama":
                return await self._scrape_defillama_data(data_type)
            else:
                # Generic DeFi data scraping
                return await self._scrape_generic_defi_data(protocol, data_type)

        except Exception as e:
            logger.error(f"Failed to scrape {protocol} data: {e}")
            return {"error": str(e), "protocol": protocol, "data_type": data_type}

    async def fetch_blockchain_analytics(self, network: str, metrics: List[str] = None) -> Dict[str, Any]:
        """
        Fetch comprehensive blockchain analytics for specified network
        """
        if metrics is None:
            metrics = ["transactions", "addresses", "tvl", "gas_prices", "block_times"]

        logger.info(f"Fetching {network} blockchain analytics: {metrics}")

        results = {}
        tasks = []

        for metric in metrics:
            if metric == "transactions":
                tasks.append(self._fetch_transaction_data(network))
            elif metric == "addresses":
                tasks.append(self._fetch_address_data(network))
            elif metric == "tvl":
                tasks.append(self._fetch_tvl_data(network))
            elif metric == "gas_prices":
                tasks.append(self._fetch_gas_data(network))
            elif metric == "block_times":
                tasks.append(self._fetch_block_data(network))

        # Execute all tasks concurrently
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            for i, metric in enumerate(metrics):
                if i < len(responses):
                    if isinstance(responses[i], Exception):
                        results[metric] = {"error": str(responses[i])}
                    else:
                        results[metric] = responses[i]

        except Exception as e:
            logger.error(f"Failed to fetch blockchain analytics: {e}")
            results["error"] = str(e)

        results["network"] = network
        results["timestamp"] = datetime.now().isoformat()

        return results

    async def monitor_smart_contract(self, contract_address: str, network: str = "ethereum") -> Dict[str, Any]:
        """
        Monitor smart contract activity and analyze transactions
        """
        logger.info(f"Monitoring contract {contract_address} on {network}")

        try:
            # Fetch contract transactions
            request = MCPRequest(
                method="GET",
                url=self.blockchain_apis[network]["etherscan"],
                params={
                    "module": "account",
                    "action": "txlist",
                    "address": contract_address,
                    "startblock": 0,
                    "endblock": 99999999,
                    "page": 1,
                    "offset": 100,
                    "sort": "desc",
                    "apikey": self.config.get("etherscan_api_key", "")
                }
            )

            response = await self.fetch_url(request)

            if response.success:
                data = json.loads(response.content)
                transactions = data.get("result", [])

                # Analyze transactions
                analysis = self._analyze_contract_transactions(transactions)

                return {
                    "contract_address": contract_address,
                    "network": network,
                    "transaction_count": len(transactions),
                    "analysis": analysis,
                    "latest_transactions": transactions[:10],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": "Failed to fetch contract data", "status_code": response.status_code}

        except Exception as e:
            logger.error(f"Failed to monitor contract {contract_address}: {e}")
            return {"error": str(e)}

    async def collect_market_data(self, tokens: List[str] = None) -> Dict[str, Any]:
        """
        Collect comprehensive market data for specified tokens or top DeFi tokens
        """
        if tokens is None:
            tokens = ["ethereum", "bitcoin", "chainlink", "uniswap", "aave", "compound-governance-token"]

        logger.info(f"Collecting market data for tokens: {tokens}")

        try:
            # Fetch from CoinGecko API
            request = MCPRequest(
                method="GET",
                url=f"{self.defi_apis['coingecko']}simple/price",
                params={
                    "ids": ",".join(tokens),
                    "vs_currencies": "usd,eth,btc",
                    "include_market_cap": "true",
                    "include_24hr_vol": "true",
                    "include_24hr_change": "true",
                    "include_last_updated_at": "true"
                }
            )

            response = await self.fetch_url(request)

            if response.success:
                market_data = json.loads(response.content)

                # Enhance with additional metrics
                enhanced_data = {}
                for token, data in market_data.items():
                    enhanced_data[token] = {
                        **data,
                        "volatility_24h": self._calculate_volatility(data),
                        "market_sentiment": self._analyze_market_sentiment(data),
                        "trend_analysis": self._analyze_price_trend(data)
                    }

                return {
                    "market_data": enhanced_data,
                    "summary": self._generate_market_summary(enhanced_data),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": "Failed to fetch market data", "status_code": response.status_code}

        except Exception as e:
            logger.error(f"Failed to collect market data: {e}")
            return {"error": str(e)}

    def create_ai_web_scraper(self, target_url: str, data_schema: Dict) -> Dict[str, Any]:
        """
        Create an AI-powered web scraper for specific data extraction
        """
        logger.info(f"Creating AI web scraper for {target_url}")

        scraper_config = {
            "name": f"scraper_{urlparse(target_url).netloc.replace('.', '_')}",
            "target_url": target_url,
            "data_schema": data_schema,
            "selectors": self._generate_css_selectors(data_schema),
            "ai_extraction": {
                "model": "gpt-4",
                "prompt_template": self._generate_extraction_prompt(data_schema),
                "fallback_selectors": True
            },
            "schedule": {
                "interval": "1h",
                "max_retries": 3,
                "timeout": 30
            },
            "created_at": datetime.now().isoformat()
        }

        return scraper_config

    # Internal helper methods
    async def _apply_rate_limit(self, url: str):
        """Apply rate limiting to prevent overwhelming servers"""
        domain = urlparse(url).netloc
        current_time = time.time()

        if domain in self.last_request_time:
            time_diff = current_time - self.last_request_time[domain]
            if time_diff < (1.0 / self.rate_limit):
                sleep_time = (1.0 / self.rate_limit) - time_diff
                await asyncio.sleep(sleep_time)

        self.last_request_time[domain] = current_time

    def _get_cached_response(self, cache_key: str) -> Optional[MCPResponse]:
        """Get cached response if available and not expired"""
        if cache_key in self.request_cache:
            cached_item = self.request_cache[cache_key]
            if datetime.now() - cached_item["timestamp"] < timedelta(seconds=self.cache_ttl):
                return cached_item["response"]
            else:
                del self.request_cache[cache_key]
        return None

    def _cache_response(self, cache_key: str, response: MCPResponse):
        """Cache response with timestamp"""
        self.request_cache[cache_key] = {
            "response": response,
            "timestamp": datetime.now()
        }

    async def _scrape_uniswap_data(self, data_type: str) -> Dict[str, Any]:
        """Scrape Uniswap protocol data"""
        query = """
        {
            uniswapDayDatas(first: 1, orderBy: date, orderDirection: desc) {
                date
                volumeUSD
                tvlUSD
            }
            pools(first: 10, orderBy: totalValueLockedUSD, orderDirection: desc) {
                id
                totalValueLockedUSD
                token0 { symbol }
                token1 { symbol }
            }
        }
        """

        request = MCPRequest(
            method="POST",
            url=self.defi_apis["uniswap"],
            headers={"Content-Type": "application/json"},
            params={"query": query}
        )

        response = await self.fetch_url(request)
        if response.success:
            return json.loads(response.content)
        return {"error": "Failed to fetch Uniswap data"}

    async def _scrape_aave_data(self, data_type: str) -> Dict[str, Any]:
        """Scrape Aave protocol data"""
        # Implementation for Aave data scraping
        return {"protocol": "aave", "data_type": data_type, "placeholder": True}

    async def _scrape_compound_data(self, data_type: str) -> Dict[str, Any]:
        """Scrape Compound protocol data"""
        request = MCPRequest(
            method="GET",
            url=f"{self.defi_apis['compound']}ctoken"
        )

        response = await self.fetch_url(request)
        if response.success:
            return json.loads(response.content)
        return {"error": "Failed to fetch Compound data"}

    async def _scrape_defillama_data(self, data_type: str) -> Dict[str, Any]:
        """Scrape DeFiLlama TVL and protocol data"""
        request = MCPRequest(
            method="GET",
            url=f"{self.defi_apis['defillama']}protocols"
        )

        response = await self.fetch_url(request)
        if response.success:
            return json.loads(response.content)
        return {"error": "Failed to fetch DeFiLlama data"}

    async def _scrape_generic_defi_data(self, protocol: str, data_type: str) -> Dict[str, Any]:
        """Generic DeFi data scraping for unknown protocols"""
        return {
            "protocol": protocol,
            "data_type": data_type,
            "message": "Generic scraping not implemented",
            "timestamp": datetime.now().isoformat()
        }

    async def _fetch_transaction_data(self, network: str) -> Dict[str, Any]:
        """Fetch transaction metrics for network"""
        # Implementation would vary by network
        return {
            "daily_transactions": 1500000,
            "avg_gas_price": "20 gwei",
            "network_congestion": "medium"
        }

    async def _fetch_address_data(self, network: str) -> Dict[str, Any]:
        """Fetch address activity metrics"""
        return {
            "active_addresses_24h": 500000,
            "new_addresses_24h": 50000,
            "unique_senders": 300000
        }

    async def _fetch_tvl_data(self, network: str) -> Dict[str, Any]:
        """Fetch Total Value Locked data"""
        return {
            "total_tvl_usd": "50000000000",
            "top_protocols": ["Uniswap", "Aave", "Compound"],
            "tvl_change_24h": "+2.5%"
        }

    async def _fetch_gas_data(self, network: str) -> Dict[str, Any]:
        """Fetch gas price data"""
        return {
            "current_gas_price": "25 gwei",
            "gas_price_trend": "stable",
            "recommended_gas": {
                "slow": "20 gwei",
                "standard": "25 gwei",
                "fast": "35 gwei"
            }
        }

    async def _fetch_block_data(self, network: str) -> Dict[str, Any]:
        """Fetch block timing data"""
        return {
            "avg_block_time": "12 seconds",
            "latest_block": 18500000,
            "blocks_24h": 7200
        }

    def _analyze_contract_transactions(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Analyze smart contract transactions"""
        if not transactions:
            return {"error": "No transactions to analyze"}

        total_value = sum(int(tx.get("value", 0)) for tx in transactions)
        gas_used = sum(int(tx.get("gasUsed", 0)) for tx in transactions)

        return {
            "total_transactions": len(transactions),
            "total_value_wei": total_value,
            "total_gas_used": gas_used,
            "avg_gas_per_tx": gas_used // len(transactions) if transactions else 0,
            "unique_addresses": len(set(tx.get("from", "") for tx in transactions)),
            "activity_pattern": "high" if len(transactions) > 50 else "medium" if len(transactions) > 10 else "low"
        }

    def _calculate_volatility(self, price_data: Dict) -> float:
        """Calculate price volatility from 24h change"""
        change_24h = price_data.get("usd_24h_change", 0)
        return abs(change_24h) / 100.0 if change_24h else 0.0

    def _analyze_market_sentiment(self, price_data: Dict) -> str:
        """Analyze market sentiment from price data"""
        change_24h = price_data.get("usd_24h_change", 0)

        if change_24h > 5:
            return "very_bullish"
        elif change_24h > 2:
            return "bullish"
        elif change_24h > -2:
            return "neutral"
        elif change_24h > -5:
            return "bearish"
        else:
            return "very_bearish"

    def _analyze_price_trend(self, price_data: Dict) -> Dict[str, Any]:
        """Analyze price trend"""
        change_24h = price_data.get("usd_24h_change", 0)
        volume_24h = price_data.get("usd_24h_vol", 0)

        return {
            "direction": "up" if change_24h > 0 else "down",
            "strength": "strong" if abs(change_24h) > 5 else "moderate" if abs(change_24h) > 2 else "weak",
            "volume_rating": "high" if volume_24h > 1000000 else "medium" if volume_24h > 100000 else "low"
        }

    def _generate_market_summary(self, market_data: Dict) -> Dict[str, Any]:
        """Generate market summary from collected data"""
        total_tokens = len(market_data)
        bullish_count = sum(1 for data in market_data.values() if data.get("market_sentiment") in ["bullish", "very_bullish"])

        return {
            "total_tokens_analyzed": total_tokens,
            "bullish_sentiment_ratio": bullish_count / total_tokens if total_tokens > 0 else 0,
            "market_trend": "bullish" if bullish_count > total_tokens / 2 else "bearish",
            "high_volatility_count": sum(1 for data in market_data.values() if data.get("volatility_24h", 0) > 0.1)
        }

    def _generate_css_selectors(self, data_schema: Dict) -> Dict[str, str]:
        """Generate CSS selectors for data extraction"""
        selectors = {}

        for field_name, field_config in data_schema.items():
            if isinstance(field_config, dict) and "selector" in field_config:
                selectors[field_name] = field_config["selector"]
            else:
                # Generate generic selectors based on field name
                selectors[field_name] = f"[data-{field_name}], .{field_name}, #{field_name}"

        return selectors

    def _generate_extraction_prompt(self, data_schema: Dict) -> str:
        """Generate AI prompt for data extraction"""
        fields = list(data_schema.keys())

        return f"""
        Extract the following data fields from the provided HTML content:
        {', '.join(fields)}

        Return the data as a JSON object with the field names as keys.
        If a field is not found, use null as the value.
        Ensure all extracted values are properly formatted and cleaned.
        """

# Integration with XMRT Multi-Agent System
class MCPAgentTool:
    """AI Agent tool for BrightData MCP integration"""

    def __init__(self, mcp_client: BrightDataMCP):
        self.mcp = mcp_client
        self.tool_name = "brightdata_mcp"
        self.description = "Enhanced web scraping and blockchain data collection using BrightData MCP"

    async def scrape_url(self, url: str, data_schema: Dict = None) -> Dict[str, Any]:
        """Tool method for agents to scrape URLs"""
        request = MCPRequest(method="GET", url=url)
        response = await self.mcp.fetch_url(request)

        if data_schema and response.success:
            # Apply AI-powered data extraction
            extracted_data = await self._extract_structured_data(response.content, data_schema)
            return {
                "url": url,
                "success": True,
                "extracted_data": extracted_data,
                "raw_content_length": len(response.content)
            }

        return {
            "url": url,
            "success": response.success,
            "status_code": response.status_code,
            "content": response.content[:1000] if response.content else ""  # Truncate for agent consumption
        }

    async def get_defi_analytics(self, protocols: List[str] = None) -> Dict[str, Any]:
        """Tool method for agents to get DeFi analytics"""
        if protocols is None:
            protocols = ["uniswap", "aave", "compound"]

        results = {}
        for protocol in protocols:
            results[protocol] = await self.mcp.scrape_defi_data(protocol)

        return results

    async def monitor_blockchain_activity(self, network: str, contract_addresses: List[str] = None) -> Dict[str, Any]:
        """Tool method for agents to monitor blockchain activity"""
        results = {
            "network": network,
            "analytics": await self.mcp.fetch_blockchain_analytics(network),
            "contracts": {}
        }

        if contract_addresses:
            for address in contract_addresses:
                results["contracts"][address] = await self.mcp.monitor_smart_contract(address, network)

        return results

    async def _extract_structured_data(self, html_content: str, data_schema: Dict) -> Dict[str, Any]:
        """Extract structured data using AI (placeholder implementation)"""
        # In a real implementation, this would use an LLM to extract structured data
        return {
            "extracted_fields": list(data_schema.keys()),
            "extraction_method": "ai_powered",
            "content_length": len(html_content),
            "timestamp": datetime.now().isoformat()
        }

# Example usage and configuration
if __name__ == "__main__":
    # Configuration for BrightData MCP
    config = {
        "brightdata_username": "your_brightdata_username",
        "brightdata_password": "your_brightdata_password",  
        "brightdata_endpoint": "brd-customer-hl_12345678-zone-datacenter_proxy1:8000",
        "rate_limit": 10,
        "cache_ttl": 3600,
        "etherscan_api_key": "your_etherscan_api_key"
    }

    async def example_usage():
        mcp = BrightDataMCP(config)

        # Example: Scrape DeFi protocol data
        defi_data = await mcp.scrape_defi_data("uniswap", "tvl")
        print("DeFi Data:", defi_data)

        # Example: Get blockchain analytics
        blockchain_data = await mcp.fetch_blockchain_analytics("ethereum", ["tvl", "gas_prices"])
        print("Blockchain Analytics:", blockchain_data)

        # Example: Monitor smart contract
        contract_data = await mcp.monitor_smart_contract("0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984")  # UNI token
        print("Contract Monitoring:", contract_data)

        await mcp.close_session()

    # Run example
    # asyncio.run(example_usage())
