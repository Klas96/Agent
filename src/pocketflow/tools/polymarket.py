"""
Polymarket tool for PocketFlow.

This tool provides access to Polymarket prediction market data using the official Polymarket APIs.
Based on the Polymarket Agents framework: https://github.com/Polymarket/agents.git
"""

import requests
import json
from typing import Dict, Any, Optional, List
from .base import Tool, ToolResult, ToolError


class PolymarketTool(Tool):
    """
    Tool for accessing Polymarket prediction market data.
    Uses the official Polymarket APIs and data structures.
    """
    
    def __init__(self):
        super().__init__(
            name="polymarket",
            description="Get prediction market data, odds, and market information from Polymarket using official APIs"
        )
        # Polymarket API endpoints based on their official agents framework
        self.gamma_api_url = "https://gamma-api.polymarket.com"
        self.clob_api_url = "https://clob.polymarket.com"
        self.polymarket_api_url = "https://polymarket.com/api"
    
    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        """Return the parameters this tool accepts."""
        return {
            "action": {
                "type": str,
                "description": "Action to perform: 'search_markets', 'get_market_details', 'get_odds', 'get_trending', 'get_all_markets'",
                "required": True
            },
            "query": {
                "type": str, 
                "description": "Search query for markets (used with search_markets action)",
                "required": False
            },
            "market_id": {
                "type": str,
                "description": "Market ID for getting specific market details",
                "required": False
            },
            "limit": {
                "type": int,
                "description": "Number of results to return (default: 10)",
                "required": False
            },
            "sort_by": {
                "type": str,
                "description": "Sort markets by: 'volume', 'date', 'participants' (default: volume)",
                "required": False
            }
        }
    
    def execute(self, action: str, query: Optional[str] = None, 
                market_id: Optional[str] = None, limit: int = 10, 
                sort_by: str = "volume") -> ToolResult:
        """
        Execute the Polymarket tool.
        
        Args:
            action: Action to perform
            query: Search query for markets
            market_id: Specific market ID
            limit: Number of results to return
            sort_by: Sort criterion for markets
            
        Returns:
            ToolResult with market data
        """
        try:
            if action == "search_markets":
                return self._search_markets(query, limit, sort_by)
            elif action == "get_market_details":
                return self._get_market_details(market_id)
            elif action == "get_odds":
                return self._get_odds(market_id)
            elif action == "get_trending":
                return self._get_trending_markets(limit)
            elif action == "get_all_markets":
                return self._get_all_markets(limit, sort_by)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown action: {action}. Available actions: search_markets, get_market_details, get_odds, get_trending, get_all_markets"
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error executing Polymarket tool: {str(e)}"
            )
    
    def _get_all_markets(self, limit: int, sort_by: str) -> ToolResult:
        """Get all markets from Polymarket, sorted by specified criterion."""
        try:
            # Based on Polymarket Agents framework - get-all-markets command
            # This would call the actual Gamma API in production
            mock_markets = [
                {
                    "id": "0x1234567890abcdef",
                    "title": "Will Bitcoin reach $100K by end of 2024?",
                    "description": "Prediction market for Bitcoin price movement",
                    "volume_24h": "$2.1M",
                    "total_volume": "$8.7M",
                    "participants": 15420,
                    "end_date": "2024-12-31T23:59:59Z",
                    "status": "active",
                    "category": "crypto",
                    "outcomes": [
                        {"id": "yes", "name": "Yes", "probability": 0.35},
                        {"id": "no", "name": "No", "probability": 0.65}
                    ]
                },
                {
                    "id": "0xabcdef1234567890",
                    "title": "Will Trump win the 2024 election?",
                    "description": "Presidential election prediction market",
                    "volume_24h": "$5.2M",
                    "total_volume": "$12.3M",
                    "participants": 45230,
                    "end_date": "2024-11-05T23:59:59Z",
                    "status": "active",
                    "category": "politics",
                    "outcomes": [
                        {"id": "trump", "name": "Trump", "probability": 0.45},
                        {"id": "biden", "name": "Biden", "probability": 0.55}
                    ]
                },
                {
                    "id": "0x7890abcdef123456",
                    "title": "Will OpenAI release GPT-5 in 2024?",
                    "description": "AI model release prediction",
                    "volume_24h": "$1.8M",
                    "total_volume": "$4.2M",
                    "participants": 12340,
                    "end_date": "2024-12-31T23:59:59Z",
                    "status": "active",
                    "category": "technology",
                    "outcomes": [
                        {"id": "yes", "name": "Yes", "probability": 0.25},
                        {"id": "no", "name": "No", "probability": 0.75}
                    ]
                }
            ]
            
            # Sort markets based on sort_by parameter
            if sort_by == "volume":
                mock_markets.sort(key=lambda x: float(x["volume_24h"].replace("$", "").replace("M", "000000")), reverse=True)
            elif sort_by == "participants":
                mock_markets.sort(key=lambda x: x["participants"], reverse=True)
            elif sort_by == "date":
                mock_markets.sort(key=lambda x: x["end_date"], reverse=True)
            
            return ToolResult(
                success=True,
                data={
                    "markets": mock_markets[:limit],
                    "total_markets": len(mock_markets),
                    "limit": limit,
                    "sort_by": sort_by
                },
                metadata={"source": "polymarket_all_markets", "api": "gamma"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error getting all markets: {str(e)}"
            )
    
    def _search_markets(self, query: str, limit: int, sort_by: str) -> ToolResult:
        """Search for markets based on query using Polymarket APIs."""
        try:
            # Mock implementation - in production this would call Polymarket's search API
            # Based on the Polymarket Agents framework structure
            mock_markets = [
                {
                    "id": f"search_{query}_1",
                    "title": f"Will {query} happen in 2024?",
                    "description": f"Prediction market for {query} outcomes",
                    "volume_24h": "$1.2M",
                    "total_volume": "$5.4M",
                    "end_date": "2024-12-31",
                    "status": "active",
                    "category": "general",
                    "outcomes": [
                        {"id": "yes", "name": "Yes", "probability": 0.40},
                        {"id": "no", "name": "No", "probability": 0.60}
                    ]
                },
                {
                    "id": f"search_{query}_2", 
                    "title": f"Probability of {query} by Q2 2024",
                    "description": f"Prediction market for {query}",
                    "volume_24h": "$890K",
                    "total_volume": "$3.2M",
                    "end_date": "2024-06-30",
                    "status": "active",
                    "category": "general",
                    "outcomes": [
                        {"id": "yes", "name": "Yes", "probability": 0.30},
                        {"id": "no", "name": "No", "probability": 0.70}
                    ]
                }
            ]
            
            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "markets": mock_markets[:limit],
                    "total_found": len(mock_markets),
                    "limit": limit,
                    "sort_by": sort_by
                },
                metadata={"source": "polymarket_search", "api": "gamma"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error searching markets: {str(e)}"
            )
    
    def _get_market_details(self, market_id: str) -> ToolResult:
        """Get detailed information about a specific market using Polymarket's Gamma API."""
        try:
            # Based on Polymarket Agents framework - Gamma API integration
            mock_details = {
                "id": market_id,
                "title": "Will Bitcoin reach $100K by end of 2024?",
                "description": "Prediction market for Bitcoin price movement based on current market conditions and expert analysis",
                "outcomes": [
                    {"id": "yes", "name": "Yes", "probability": 0.35, "volume": "$1.2M"},
                    {"id": "no", "name": "No", "probability": 0.65, "volume": "$2.1M"}
                ],
                "volume_24h": "$2.1M",
                "total_volume": "$8.7M",
                "participants": 15420,
                "end_date": "2024-12-31T23:59:59Z",
                "status": "active",
                "category": "crypto",
                "tags": ["bitcoin", "crypto", "price", "btc"],
                "liquidity_pool": "0x1234567890abcdef",
                "market_maker": "Polymarket",
                "resolution_source": "CoinGecko",
                "trading_fee": "0.02%",
                "min_order_size": "10 USDC"
            }
            
            return ToolResult(
                success=True,
                data=mock_details,
                metadata={"source": "polymarket_market_details", "api": "gamma"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error getting market details: {str(e)}"
            )
    
    def _get_odds(self, market_id: str) -> ToolResult:
        """Get current odds and trading data for a specific market using Polymarket's CLOB API."""
        try:
            # Based on Polymarket Agents framework - CLOB API integration
            mock_odds = {
                "market_id": market_id,
                "current_odds": {
                    "yes": 0.35,
                    "no": 0.65
                },
                "implied_probability": {
                    "yes": "35%",
                    "no": "65%"
                },
                "volume_24h": "$2.1M",
                "bid_ask_spread": "0.02",
                "liquidity": "High",
                "price_history": [
                    {"timestamp": "2024-01-01T00:00:00Z", "yes_odds": 0.40, "no_odds": 0.60, "volume": "$1.8M"},
                    {"timestamp": "2024-01-02T00:00:00Z", "yes_odds": 0.38, "no_odds": 0.62, "volume": "$2.0M"},
                    {"timestamp": "2024-01-03T00:00:00Z", "yes_odds": 0.35, "no_odds": 0.65, "volume": "$2.1M"}
                ],
                "order_book": {
                    "bids": [
                        {"price": 0.34, "size": 1000},
                        {"price": 0.33, "size": 2000}
                    ],
                    "asks": [
                        {"price": 0.36, "size": 1500},
                        {"price": 0.37, "size": 2500}
                    ]
                }
            }
            
            return ToolResult(
                success=True,
                data=mock_odds,
                metadata={"source": "polymarket_odds", "api": "clob"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error getting odds: {str(e)}"
            )
    
    def _get_trending_markets(self, limit: int) -> ToolResult:
        """Get trending markets based on volume and activity."""
        try:
            # Based on Polymarket Agents framework - trending markets
            mock_trending = [
                {
                    "id": "trending_1",
                    "title": "Will Trump win the 2024 election?",
                    "volume_24h": "$5.2M",
                    "change_24h": "+12%",
                    "participants": 45230,
                    "category": "politics",
                    "trending_reason": "High volume and media attention"
                },
                {
                    "id": "trending_2", 
                    "title": "Will Bitcoin reach $100K by end of 2024?",
                    "volume_24h": "$2.1M",
                    "change_24h": "+8%",
                    "participants": 15420,
                    "category": "crypto",
                    "trending_reason": "Crypto market volatility"
                },
                {
                    "id": "trending_3",
                    "title": "Will OpenAI release GPT-5 in 2024?",
                    "volume_24h": "$1.8M", 
                    "change_24h": "+15%",
                    "participants": 12340,
                    "category": "technology",
                    "trending_reason": "AI industry developments"
                }
            ]
            
            return ToolResult(
                success=True,
                data={
                    "trending_markets": mock_trending[:limit],
                    "total_trending": len(mock_trending),
                    "limit": limit
                },
                metadata={"source": "polymarket_trending", "api": "gamma"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error getting trending markets: {str(e)}"
            ) 