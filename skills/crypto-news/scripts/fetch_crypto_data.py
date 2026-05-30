"""
Crypto News & Analysis Script

Fetches cryptocurrency market data from CoinGecko API and generates
AI-powered analysis. Supports market overview, news, coin details,
and trend analysis.

Usage:
    python fetch_crypto_data.py '{"action": "market_overview", "count": 10}'
"""

import sys
import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

try:
    import requests
except ImportError:
    print(json.dumps({"error": "requests library required. Install with: pip install requests"}))
    sys.exit(1)


# CoinGecko API endpoints (free tier)
COINGECKO_BASE = "https://api.coingecko.com/api/v3"
DEFILLAMA_BASE = "https://api.llama.fi"
DEFILLAMA_STABLECOINS_BASE = "https://stablecoins.llama.fi"
DEFILLAMA_YIELDS_BASE = "https://yields.llama.fi"


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def get_api_key() -> str:
    """Get optional CoinGecko API key from environment."""
    return os.environ.get("CRYPTO_API_KEY") or os.environ.get("COINGECKO_API_KEY", "")


def coingecko_headers() -> Dict[str, str]:
    """Build CoinGecko headers. Public endpoints work without a key."""
    headers = {"accept": "application/json"}
    api_key = get_api_key()
    if api_key:
        headers["x-cg-demo-api-key"] = api_key
    return headers


def fetch_json(url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Any:
    """Fetch JSON with a shared timeout and clear HTTP failures."""
    response = requests.get(url, params=params, headers=headers or {"accept": "application/json"}, timeout=30)
    response.raise_for_status()
    return response.json()


def safe_float(value: Any, default: float = 0.0) -> float:
    """Convert API values into floats without failing on None or strings."""
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def strip_html(text: str) -> str:
    """Keep API descriptions short and readable for model context."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or "")).strip()


def take_top(items: List[Dict[str, Any]], count: int, sort_key: str, reverse: bool = True) -> List[Dict[str, Any]]:
    """Sort dictionaries by a numeric key and return the requested number."""
    return sorted(items, key=lambda item: safe_float(item.get(sort_key)), reverse=reverse)[:max(1, count)]


def chain_circulating_usd(value: Any) -> float:
    """Extract a USD supply value from DefiLlama stablecoin chain fields."""
    if isinstance(value, dict):
        current = value.get("current")
        if isinstance(current, dict):
            return safe_float(current.get("peggedUSD"))
        return safe_float(value.get("peggedUSD"))
    return safe_float(value)


def top_asset_chains(chain_circulating: Any, limit: int = 8) -> List[Dict[str, Any]]:
    """Return the largest chains for one stablecoin asset."""
    if not isinstance(chain_circulating, dict):
        return []
    rows = [
        {"name": name, "circulating_usd": chain_circulating_usd(value)}
        for name, value in chain_circulating.items()
    ]
    return take_top(rows, limit, "circulating_usd")


def summarize_protocol_chain_tvls(chain_tvls: Any, limit: int = 10) -> List[Dict[str, Any]]:
    """Summarize DefiLlama protocol chain TVL histories into current values."""
    if not isinstance(chain_tvls, dict):
        return []
    rows = []
    for chain, payload in chain_tvls.items():
        tvl = None
        if isinstance(payload, dict):
            history = payload.get("tvl")
            if isinstance(history, list) and history:
                tvl = history[-1].get("totalLiquidityUSD")
            else:
                tvl = payload.get("totalLiquidityUSD") or payload.get("tvl")
        rows.append({"chain": chain, "current_tvl": tvl})
    return take_top(rows, limit, "current_tvl")


def summarize_protocol_tokens(tokens: Any, limit: int = 10) -> Dict[str, Any]:
    """Return only the latest protocol token balances."""
    if not isinstance(tokens, list) or not tokens:
        return {"date": None, "tokens": {}}
    latest = tokens[-1] if isinstance(tokens[-1], dict) else {}
    token_map = latest.get("tokens") if isinstance(latest.get("tokens"), dict) else {}
    rows = [
        {"symbol": symbol, "balance": safe_float(balance)}
        for symbol, balance in token_map.items()
    ]
    return {
        "date": latest.get("date"),
        "tokens": take_top(rows, limit, "balance"),
    }


def fetch_market_overview(count: int = 10, currency: str = "usd") -> Dict[str, Any]:
    """
    Fetch top cryptocurrencies by market cap.

    :param count: Number of coins to return (1-250)
    :param currency: Quote currency
    :return: Market overview data
    """
    url = f"{COINGECKO_BASE}/coins/markets"
    params = {
        "vs_currency": currency,
        "order": "market_cap_desc",
        "per_page": min(count, 250),
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "1h,24h,7d"
    }
    data = fetch_json(url, params=params, headers=coingecko_headers())

    coins = []
    for coin in data:
        coins.append({
            "id": coin.get("id"),
            "symbol": coin.get("symbol", "").upper(),
            "name": coin.get("name"),
            "current_price": coin.get("current_price"),
            "market_cap": coin.get("market_cap"),
            "market_cap_rank": coin.get("market_cap_rank"),
            "total_volume": coin.get("total_volume"),
            "price_change_24h": coin.get("price_change_percentage_24h"),
            "price_change_7d": coin.get("price_change_percentage_7d_in_currency"),
            "price_change_1h": coin.get("price_change_percentage_1h_in_currency"),
            "ath": coin.get("ath"),
            "ath_change_percentage": coin.get("ath_change_percentage"),
            "circulating_supply": coin.get("circulating_supply"),
            "total_supply": coin.get("total_supply")
        })

    return {
        "status": "success",
        "data": {
            "market_overview": coins,
            "timestamp": utc_now(),
            "currency": currency,
            "total": len(coins),
            "source": "CoinGecko /coins/markets"
        }
    }


def fetch_global_market(currency: str = "usd") -> Dict[str, Any]:
    """
    Fetch global crypto market and DeFi aggregate metrics.

    :param currency: Quote currency for market cap and volume
    :return: Global market summary
    """
    global_data = fetch_json(f"{COINGECKO_BASE}/global", headers=coingecko_headers()).get("data", {})
    defi_data = fetch_json(f"{COINGECKO_BASE}/global/decentralized_finance_defi", headers=coingecko_headers()).get("data", {})

    market_cap = global_data.get("total_market_cap", {})
    volume = global_data.get("total_volume", {})
    market_cap_change = global_data.get("market_cap_change_percentage_24h_usd")

    summary = {
        "active_cryptocurrencies": global_data.get("active_cryptocurrencies"),
        "markets": global_data.get("markets"),
        "total_market_cap": market_cap.get(currency),
        "total_volume": volume.get(currency),
        "market_cap_change_24h_percent": market_cap_change,
        "btc_dominance_percent": global_data.get("market_cap_percentage", {}).get("btc"),
        "eth_dominance_percent": global_data.get("market_cap_percentage", {}).get("eth"),
        "defi_market_cap": defi_data.get("defi_market_cap"),
        "eth_market_cap": defi_data.get("eth_market_cap"),
        "defi_to_eth_ratio_percent": defi_data.get("defi_to_eth_ratio"),
        "defi_trading_volume_24h": defi_data.get("trading_volume_24h"),
        "defi_dominance_percent": defi_data.get("defi_dominance"),
        "top_coin_dominance": global_data.get("market_cap_percentage", {}),
    }

    return {
        "status": "success",
        "data": {
            "global_market": summary,
            "timestamp": utc_now(),
            "currency": currency,
            "source": "CoinGecko /global and /global/decentralized_finance_defi"
        }
    }


def fetch_news(count: int = 10, category: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch crypto news (using web search).

    This function would integrate with a news API. For now, we'll
    use CoinGecko's trending coins as a proxy for market activity.

    :param count: Number of news items
    :param category: Optional category filter
    :return: News data
    """
    # Get trending coins as a proxy for current market interest
    url = f"{COINGECKO_BASE}/search/trending"
    data = fetch_json(url, headers=coingecko_headers())

    trending = data.get("coins", [])[:count]

    news_items = []
    for item in trending:
        coin = item.get("item", {})
        news_items.append({
            "title": f"Trending: {coin.get('name')} ({coin.get('symbol', '').upper()})",
            "description": f"Market cap rank: {coin.get('market_cap_rank', 'N/A')}. "
                           f"Price change 24h: {coin.get('data', {}).get('price_change_percentage_24h', {}).get('usd', 'N/A')}%",
            "coin_id": coin.get("id"),
            "score": coin.get("score")
        })

    return {
        "status": "success",
        "data": {
            "news": news_items,
            "trending": trending,
            "timestamp": utc_now(),
            "category": category,
            "source": "CoinGecko /search/trending"
        }
    }


def fetch_coin_detail(coin_id: str) -> Dict[str, Any]:
    """
    Fetch detailed information about a specific coin.

    :param coin_id: CoinGecko coin ID (e.g., 'bitcoin')
    :return: Coin detail data
    """
    url = f"{COINGECKO_BASE}/coins/{coin_id}"
    params = {
        "localization": "false",
        "tickers": "false",
        "community_data": "true",
        "developer_data": "false"
    }
    data = fetch_json(url, params=params, headers=coingecko_headers())

    market_data = data.get("market_data", {})

    detail = {
        "id": data.get("id"),
        "symbol": data.get("symbol", "").upper(),
        "name": data.get("name"),
        "description": strip_html(data.get("description", {}).get("en", ""))[:700],
        "current_price": market_data.get("current_price", {}).get("usd"),
        "market_cap": market_data.get("market_cap", {}).get("usd"),
        "market_cap_rank": market_data.get("market_cap_rank"),
        "total_volume": market_data.get("total_volume", {}).get("usd"),
        "high_24h": market_data.get("high_24h", {}).get("usd"),
        "low_24h": market_data.get("low_24h", {}).get("usd"),
        "price_change_24h": market_data.get("price_change_percentage_24h"),
        "price_change_7d": market_data.get("price_change_percentage_7d"),
        "price_change_30d": market_data.get("price_change_percentage_30d"),
        "ath": market_data.get("ath", {}).get("usd"),
        "ath_change_percentage": market_data.get("ath_change_percentage", {}).get("usd"),
        "atl": market_data.get("atl", {}).get("usd"),
        "circulating_supply": market_data.get("circulating_supply"),
        "total_supply": market_data.get("total_supply"),
        "max_supply": market_data.get("max_supply"),
        "categories": data.get("categories", []),
        "homepage": data.get("links", {}).get("homepage", [None])[0],
        "genesis_date": data.get("genesis_date"),
        "sentiment_votes_up_percentage": data.get("sentiment_votes_up_percentage"),
        "community_score": data.get("community_score")
    }

    return {
        "status": "success",
        "data": {
            "coin_detail": detail,
            "timestamp": utc_now(),
            "source": f"CoinGecko /coins/{coin_id}"
        }
    }


def analyze_trend(coin_id: str) -> Dict[str, Any]:
    """
    Generate trend analysis for a coin based on historical data.

    :param coin_id: CoinGecko coin ID
    :return: Trend analysis data
    """
    # Fetch 30-day price history
    url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "30", "interval": "daily"}
    data = fetch_json(url, params=params, headers=coingecko_headers())

    prices = data.get("prices", [])
    if len(prices) < 2:
        return {"status": "error", "message": "Insufficient historical data"}

    # Calculate basic trend metrics
    current_price = prices[-1][1]
    week_ago_price = prices[-7][1] if len(prices) >= 7 else prices[0][1]
    month_start_price = prices[0][1]

    week_change = ((current_price - week_ago_price) / week_ago_price) * 100
    month_change = ((current_price - month_start_price) / month_start_price) * 100

    # Determine trend
    if week_change > 5:
        trend = "bullish"
    elif week_change < -5:
        trend = "bearish"
    else:
        trend = "neutral"

    analysis = {
        "coin_id": coin_id,
        "current_price": current_price,
        "price_7d_ago": week_ago_price,
        "price_30d_ago": month_start_price,
        "change_7d_percent": round(week_change, 2),
        "change_30d_percent": round(month_change, 2),
        "trend": trend,
        "support_level": min([p[1] for p in prices[-7:]]),
        "resistance_level": max([p[1] for p in prices[-7:]])
    }

    return {
        "status": "success",
        "data": {
            "trend_analysis": analysis,
            "historical_prices": prices[-7:],  # Last 7 days
            "timestamp": utc_now(),
            "source": f"CoinGecko /coins/{coin_id}/market_chart"
        }
    }


def fetch_defi_overview(count: int = 20, chain_count: int = 10, include_cex: bool = False) -> Dict[str, Any]:
    """
    Fetch DeFi protocol and chain TVL overview from DefiLlama.

    :param count: Number of top protocols to return
    :param chain_count: Number of top chains to return
    :param include_cex: Include centralized exchange reserves from DefiLlama protocols
    :return: DeFi TVL overview
    """
    protocols = fetch_json(f"{DEFILLAMA_BASE}/protocols")
    chains = fetch_json(f"{DEFILLAMA_BASE}/v2/chains")

    protocol_rows = []
    for protocol in protocols:
        category = protocol.get("category")
        if not include_cex and category == "CEX":
            continue
        protocol_rows.append({
            "name": protocol.get("name"),
            "slug": protocol.get("slug"),
            "category": category,
            "chains": protocol.get("chains", []),
            "tvl": protocol.get("tvl"),
            "change_1d_percent": protocol.get("change_1d"),
            "change_7d_percent": protocol.get("change_7d"),
            "mcap": protocol.get("mcap"),
            "url": protocol.get("url"),
        })

    chain_rows = []
    for chain in chains:
        chain_rows.append({
            "name": chain.get("name"),
            "tvl": chain.get("tvl"),
            "token_symbol": chain.get("tokenSymbol"),
            "change_1d_percent": chain.get("change_1d"),
            "change_7d_percent": chain.get("change_7d"),
            "change_1m_percent": chain.get("change_1m"),
        })

    top_protocols = take_top(protocol_rows, count, "tvl")
    top_chains = take_top(chain_rows, chain_count, "tvl")

    category_tvl: Dict[str, float] = {}
    for protocol in protocol_rows:
        category = protocol.get("category") or "Unknown"
        category_tvl[category] = category_tvl.get(category, 0.0) + safe_float(protocol.get("tvl"))
    top_categories = [
        {"category": category, "tvl": tvl}
        for category, tvl in sorted(category_tvl.items(), key=lambda item: item[1], reverse=True)[:10]
    ]

    return {
        "status": "success",
        "data": {
            "defi_overview": {
                "top_protocols": top_protocols,
                "top_chains": top_chains,
                "top_categories": top_categories,
                "protocol_count": len(protocol_rows),
                "include_cex": include_cex,
            },
            "timestamp": utc_now(),
            "source": "DefiLlama /protocols and /v2/chains"
        }
    }


def fetch_protocol_detail(slug: str) -> Dict[str, Any]:
    """
    Fetch detail for one DeFi protocol by DefiLlama slug.

    :param slug: DefiLlama protocol slug, e.g. 'lido', 'aave-v3'
    :return: Protocol summary and recent TVL history
    """
    data = fetch_json(f"{DEFILLAMA_BASE}/protocol/{slug}")
    tvl_history = data.get("tvl") or []
    recent_tvl = tvl_history[-14:] if isinstance(tvl_history, list) else []

    detail = {
        "name": data.get("name"),
        "slug": data.get("slug") or slug,
        "category": data.get("category"),
        "chains": data.get("chains", []),
        "description": data.get("description"),
        "url": data.get("url"),
        "twitter": data.get("twitter"),
        "current_tvl": recent_tvl[-1].get("totalLiquidityUSD") if recent_tvl else data.get("tvl"),
        "chain_tvls": summarize_protocol_chain_tvls(data.get("chainTvls")),
        "latest_token_balances": summarize_protocol_tokens(data.get("tokens")),
        "governance_id": data.get("governanceID"),
    }

    return {
        "status": "success",
        "data": {
            "protocol_detail": detail,
            "recent_tvl": recent_tvl,
            "timestamp": utc_now(),
            "source": f"DefiLlama /protocol/{slug}"
        }
    }


def fetch_stablecoin_overview(count: int = 20) -> Dict[str, Any]:
    """
    Fetch stablecoin supply overview from DefiLlama.

    :param count: Number of top stablecoins to return
    :return: Stablecoin aggregate and top assets
    """
    stablecoins = fetch_json(f"{DEFILLAMA_STABLECOINS_BASE}/stablecoins", params={"includePrices": "true"})
    chains = fetch_json(f"{DEFILLAMA_STABLECOINS_BASE}/stablecoinchains")

    assets = []
    for asset in stablecoins.get("peggedAssets", []):
        circulating = asset.get("circulating", {}) or {}
        circulating_usd = circulating.get("peggedUSD")
        change = asset.get("change_1d") or {}
        assets.append({
            "id": asset.get("id"),
            "name": asset.get("name"),
            "symbol": asset.get("symbol"),
            "peg_type": asset.get("pegType"),
            "price_source": asset.get("priceSource"),
            "circulating_usd": circulating_usd,
            "change_1d": change,
            "top_chains": top_asset_chains(asset.get("chainCirculating")),
        })

    chain_rows = []
    for chain in chains:
        chain_rows.append({
            "name": chain.get("name"),
            "circulating_usd": chain.get("totalCirculatingUSD", {}).get("peggedUSD"),
            "change_1d_percent": chain.get("change_1d"),
            "change_7d_percent": chain.get("change_7d"),
        })

    total_market_cap_usd = (
        (stablecoins.get("totalCirculating") or {}).get("peggedUSD")
        or (stablecoins.get("totalCirculatingUSD") or {}).get("peggedUSD")
        or sum(safe_float(asset.get("circulating_usd")) for asset in assets)
    )

    return {
        "status": "success",
        "data": {
            "stablecoin_overview": {
                "total_market_cap_usd": total_market_cap_usd,
                "top_stablecoins": take_top(assets, count, "circulating_usd"),
                "top_chains": take_top(chain_rows, 10, "circulating_usd"),
            },
            "timestamp": utc_now(),
            "source": "DefiLlama stablecoins /stablecoins and /stablecoinchains"
        }
    }


def fetch_yield_pools(
    count: int = 20,
    chain: Optional[str] = None,
    project: Optional[str] = None,
    stable_only: bool = False,
    min_tvl_usd: float = 1_000_000,
) -> Dict[str, Any]:
    """
    Fetch yield pools from DefiLlama and filter by basic risk dimensions.

    :param count: Number of pools to return
    :param chain: Optional chain filter
    :param project: Optional project filter
    :param stable_only: If true, include only pools marked as stablecoin pools
    :param min_tvl_usd: Minimum TVL filter
    :return: Yield pool list sorted by TVL
    """
    payload = fetch_json(f"{DEFILLAMA_YIELDS_BASE}/pools")
    pools = payload.get("data", [])

    filtered = []
    seen_pools = set()
    for pool in pools:
        pool_id = pool.get("pool")
        if pool_id and pool_id in seen_pools:
            continue
        if pool_id:
            seen_pools.add(pool_id)
        if chain and (pool.get("chain") or "").lower() != chain.lower():
            continue
        if project and (pool.get("project") or "").lower() != project.lower():
            continue
        if stable_only and not pool.get("stablecoin"):
            continue
        if safe_float(pool.get("tvlUsd")) < min_tvl_usd:
            continue
        filtered.append({
            "pool": pool.get("pool"),
            "project": pool.get("project"),
            "chain": pool.get("chain"),
            "symbol": pool.get("symbol"),
            "tvl_usd": pool.get("tvlUsd"),
            "apy": pool.get("apy"),
            "apy_base": pool.get("apyBase"),
            "apy_reward": pool.get("apyReward"),
            "stablecoin": pool.get("stablecoin"),
            "il_risk": pool.get("ilRisk"),
            "exposure": pool.get("exposure"),
            "underlying_tokens": pool.get("underlyingTokens"),
            "reward_tokens": pool.get("rewardTokens"),
        })

    return {
        "status": "success",
        "data": {
            "yield_pools": take_top(filtered, count, "tvl_usd"),
            "filters": {
                "chain": chain,
                "project": project,
                "stable_only": stable_only,
                "min_tvl_usd": min_tvl_usd,
            },
            "timestamp": utc_now(),
            "source": "DefiLlama yields /pools"
        }
    }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python fetch_crypto_data.py '<json_args>'"}))
        sys.exit(1)

    try:
        args = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON arguments: {e}"}))
        sys.exit(1)

    action = args.get("action")
    if not action:
        print(json.dumps({"error": "Missing required parameter: action"}))
        sys.exit(1)

    try:
        if action == "market_overview":
            result = fetch_market_overview(
                count=args.get("count", 10),
                currency=args.get("currency", "usd")
            )
        elif action == "global_market":
            result = fetch_global_market(currency=args.get("currency", "usd"))
        elif action == "news":
            result = fetch_news(
                count=args.get("count", 10),
                category=args.get("category")
            )
        elif action == "coin_detail":
            coin_id = args.get("coin_id")
            if not coin_id:
                result = {"status": "error", "message": "Missing coin_id parameter"}
            else:
                result = fetch_coin_detail(coin_id)
        elif action == "trend_analysis":
            coin_id = args.get("coin_id")
            if not coin_id:
                result = {"status": "error", "message": "Missing coin_id parameter"}
            else:
                result = analyze_trend(coin_id)
        elif action == "defi_overview":
            result = fetch_defi_overview(
                count=args.get("count", 20),
                chain_count=args.get("chain_count", 10),
                include_cex=bool(args.get("include_cex", False)),
            )
        elif action == "protocol_detail":
            slug = args.get("slug") or args.get("protocol")
            if not slug:
                result = {"status": "error", "message": "Missing slug parameter"}
            else:
                result = fetch_protocol_detail(slug)
        elif action == "stablecoin_overview":
            result = fetch_stablecoin_overview(count=args.get("count", 20))
        elif action == "yield_pools":
            result = fetch_yield_pools(
                count=args.get("count", 20),
                chain=args.get("chain"),
                project=args.get("project"),
                stable_only=bool(args.get("stable_only", False)),
                min_tvl_usd=safe_float(args.get("min_tvl_usd"), 1_000_000),
            )
        else:
            result = {"status": "error", "message": f"Unknown action: {action}"}

        print(json.dumps(result, ensure_ascii=False))

    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": f"API request failed: {str(e)}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {str(e)}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
