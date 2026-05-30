#!/usr/bin/env python3
"""Generate a crypto market brief from structured market data.

The script fetches current market, DeFi, stablecoin, and yield data using the
local crypto data helper. It can print a Markdown brief or archive it into a
ZVAgent workspace knowledge base.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from fetch_crypto_data import (
    analyze_trend,
    fetch_coin_detail,
    fetch_defi_overview,
    fetch_global_market,
    fetch_market_overview,
    fetch_protocol_detail,
    fetch_stablecoin_overview,
    fetch_yield_pools,
)


SOURCE_LINKS = [
    ("CoinGecko API", "https://docs.coingecko.com/reference/introduction"),
    ("DefiLlama API", "https://defillama.com/docs/api"),
]


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "crypto-brief"


def money(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    sign = "-" if number < 0 else ""
    number = abs(number)
    if number >= 1_000_000_000_000:
        return f"{sign}${number / 1_000_000_000_000:.2f}T"
    if number >= 1_000_000_000:
        return f"{sign}${number / 1_000_000_000:.2f}B"
    if number >= 1_000_000:
        return f"{sign}${number / 1_000_000:.2f}M"
    if number >= 1_000:
        return f"{sign}${number / 1_000:.2f}K"
    return f"{sign}${number:.2f}"


def price(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if number >= 1000:
        return f"${number:,.0f}"
    if number >= 1:
        return f"${number:,.2f}"
    return f"${number:,.6f}"


def pct(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    return f"{number:+.2f}%"


def number(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def get_nested(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return default if current is None else current


def require_success(name: str, result: Dict[str, Any]) -> Dict[str, Any]:
    if result.get("status") != "success":
        raise RuntimeError(f"{name} failed: {result}")
    data = result.get("data")
    if not isinstance(data, dict):
        raise RuntimeError(f"{name} returned invalid data")
    return data


def find_coin(coins: List[Dict[str, Any]], symbol: str) -> Dict[str, Any]:
    symbol = symbol.upper()
    for coin in coins:
        if (coin.get("symbol") or "").upper() == symbol:
            return coin
    return {}


def trend_label(change_24h: Any) -> str:
    try:
        value = float(change_24h)
    except (TypeError, ValueError):
        return "数据不足"
    if value > 2:
        return "风险偏好偏强"
    if value < -2:
        return "风险偏好偏弱"
    return "震荡整理"


def default_watchlist_path(workspace: str | None) -> Path | None:
    if not workspace:
        return None
    return Path(workspace).expanduser() / "knowledge" / "crypto" / "watchlist.json"


def load_watchlist(args: argparse.Namespace) -> Dict[str, Any]:
    path = Path(args.watchlist).expanduser() if args.watchlist else default_watchlist_path(args.workspace)
    if not path or not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"watchlist must be a JSON object: {path}")
    data["_path"] = str(path)
    data.setdefault("settings", {})
    data.setdefault("assets", [])
    if not isinstance(data["assets"], list):
        raise ValueError("watchlist.assets must be a list")
    return data


def collect_watchlist(args: argparse.Namespace, errors: List[str]) -> Dict[str, Any]:
    try:
        watchlist = load_watchlist(args)
    except Exception as exc:
        errors.append(f"watchlist: {exc}")
        return {}
    if not watchlist:
        return {}

    results = {
        "path": watchlist.get("_path"),
        "settings": watchlist.get("settings") or {},
        "items": [],
    }
    for asset in watchlist.get("assets", []):
        if not isinstance(asset, dict):
            continue
        kind = asset.get("type")
        try:
            if kind == "coin":
                coin_id = asset.get("id")
                if not coin_id:
                    raise ValueError("coin asset missing id")
                detail = require_success(f"watchlist coin {coin_id}", fetch_coin_detail(coin_id)).get("coin_detail", {})
                results["items"].append({"asset": asset, "detail": detail})
            elif kind == "protocol":
                slug = asset.get("slug")
                if not slug:
                    raise ValueError("protocol asset missing slug")
                detail_data = require_success(f"watchlist protocol {slug}", fetch_protocol_detail(slug))
                results["items"].append({
                    "asset": asset,
                    "detail": detail_data.get("protocol_detail", {}),
                    "recent_tvl": detail_data.get("recent_tvl", []),
                })
            else:
                errors.append(f"watchlist: unsupported asset type {kind}")
        except Exception as exc:
            errors.append(f"watchlist {asset.get('name') or asset.get('id') or asset.get('slug')}: {exc}")
    return results


def collect_data(args: argparse.Namespace) -> Tuple[Dict[str, Any], List[str]]:
    errors: List[str] = []
    results: Dict[str, Any] = {}

    calls = [
        ("global_market", lambda: fetch_global_market(args.currency)),
        ("market_overview", lambda: fetch_market_overview(args.coin_count, args.currency)),
        ("defi_overview", lambda: fetch_defi_overview(args.defi_count, args.chain_count)),
        ("stablecoin_overview", lambda: fetch_stablecoin_overview(args.stablecoin_count)),
        (
            "yield_pools",
            lambda: fetch_yield_pools(
                count=args.yield_count,
                stable_only=args.stable_yields,
                min_tvl_usd=args.min_yield_tvl,
            ),
        ),
    ]

    if args.include_trends:
        calls.extend([
            ("btc_trend", lambda: analyze_trend("bitcoin")),
            ("eth_trend", lambda: analyze_trend("ethereum")),
        ])

    for name, call in calls:
        try:
            results[name] = require_success(name, call())
        except Exception as exc:
            errors.append(f"{name}: {exc}")

    watchlist = collect_watchlist(args, errors)
    if watchlist:
        results["watchlist"] = watchlist

    return results, errors


def render_coin_line(label: str, coin: Dict[str, Any]) -> str:
    if not coin:
        return f"- {label}: n/a"
    return (
        f"- {label}: {price(coin.get('current_price'))}, "
        f"24h {pct(coin.get('price_change_24h'))}, "
        f"7d {pct(coin.get('price_change_7d'))}, "
        f"volume {money(coin.get('total_volume'))}, "
        f"mcap {money(coin.get('market_cap'))}"
    )


def render_sources() -> str:
    return "\n".join(f"- [{name}]({url})" for name, url in SOURCE_LINKS)


def coin_risk_flags(detail: Dict[str, Any], settings: Dict[str, Any]) -> List[str]:
    flags = []
    change_24h = number(detail.get("price_change_24h"))
    change_7d = number(detail.get("price_change_7d"))
    volume = number(detail.get("total_volume"))
    mcap = number(detail.get("market_cap"))
    ath_drawdown = number(detail.get("ath_change_percentage"))
    if abs(change_24h) >= number(settings.get("price_24h_alert_pct"), 5):
        flags.append(f"24h move {pct(change_24h)}")
    if abs(change_7d) >= number(settings.get("price_7d_alert_pct"), 10):
        flags.append(f"7d move {pct(change_7d)}")
    if mcap > 0 and volume / mcap < number(settings.get("volume_to_mcap_min"), 0.02):
        flags.append(f"thin turnover {volume / mcap:.2%}")
    if ath_drawdown <= -70:
        flags.append(f"deep ATH drawdown {pct(ath_drawdown)}")
    return flags or ["no threshold breach"]


def protocol_risk_flags(detail: Dict[str, Any], recent_tvl: List[Dict[str, Any]], settings: Dict[str, Any]) -> List[str]:
    flags = []
    if len(recent_tvl) >= 2:
        start = number(recent_tvl[0].get("totalLiquidityUSD"))
        end = number(recent_tvl[-1].get("totalLiquidityUSD"))
        if start > 0:
            change = (end - start) / start * 100
            if abs(change) >= number(settings.get("tvl_7d_alert_pct"), 10):
                flags.append(f"recent TVL move {pct(change)}")

    current_tvl = number(detail.get("current_tvl"))
    chain_tvls = detail.get("chain_tvls") or []
    if current_tvl > 0 and chain_tvls:
        top = number(chain_tvls[0].get("current_tvl"))
        concentration = top / current_tvl * 100
        if concentration >= number(settings.get("chain_concentration_alert_pct"), 80):
            flags.append(f"chain concentration {concentration:.1f}% on {chain_tvls[0].get('chain')}")
    if current_tvl < 10_000_000:
        flags.append(f"low TVL {money(current_tvl)}")
    return flags or ["no threshold breach"]


def render_watchlist_radar(watchlist: Dict[str, Any]) -> List[str]:
    if not watchlist:
        return []
    settings = watchlist.get("settings") or {}
    lines = [
        "",
        "## 关注列表风险雷达",
        "",
        f"- Watchlist: `{watchlist.get('path', 'inline')}`",
    ]
    items = watchlist.get("items") or []
    if not items:
        lines.append("- No watchlist assets configured.")
        return lines

    for item in items:
        asset = item.get("asset") or {}
        detail = item.get("detail") or {}
        tags = asset.get("tags") or []
        tag_text = f" tags={', '.join(tags)}" if tags else ""
        if asset.get("type") == "coin":
            flags = coin_risk_flags(detail, settings)
            name = detail.get("name") or asset.get("name") or asset.get("id")
            symbol = detail.get("symbol") or asset.get("symbol") or ""
            lines.append(
                f"- {name} ({symbol}): {price(detail.get('current_price'))}, "
                f"24h {pct(detail.get('price_change_24h'))}, "
                f"7d {pct(detail.get('price_change_7d'))}, "
                f"mcap {money(detail.get('market_cap'))}; risk: {'; '.join(flags)}{tag_text}"
            )
        elif asset.get("type") == "protocol":
            recent_tvl = item.get("recent_tvl") or []
            flags = protocol_risk_flags(detail, recent_tvl, settings)
            name = detail.get("name") or asset.get("name") or asset.get("slug")
            lines.append(
                f"- {name} ({detail.get('category', 'protocol')}): "
                f"TVL {money(detail.get('current_tvl'))}; "
                f"risk: {'; '.join(flags)}{tag_text}"
            )
        notes = asset.get("notes")
        if notes:
            lines.append(f"  - note: {notes}")
    return lines


def render_brief(args: argparse.Namespace, data: Dict[str, Any], errors: List[str]) -> str:
    generated = datetime.now().isoformat(timespec="seconds")
    global_market = get_nested(data, "global_market", "global_market", default={})
    overview = get_nested(data, "market_overview", "market_overview", default=[])
    defi = get_nested(data, "defi_overview", "defi_overview", default={})
    stable = get_nested(data, "stablecoin_overview", "stablecoin_overview", default={})
    yields = get_nested(data, "yield_pools", "yield_pools", default=[])
    watchlist = data.get("watchlist", {})
    btc = find_coin(overview, "BTC")
    eth = find_coin(overview, "ETH")
    regime = trend_label(global_market.get("market_cap_change_24h_percent"))

    top_protocols = defi.get("top_protocols") or []
    top_chains = defi.get("top_chains") or []
    top_stables = stable.get("top_stablecoins") or []
    stable_chains = stable.get("top_chains") or []

    title = args.topic or f"Crypto {args.cadence.title()} Brief"
    lines = [
        f"# {args.date} {title}",
        "",
        (
            f"> Source: automated crypto market brief. Generated: {generated}. "
            "Data from CoinGecko and DefiLlama public APIs."
        ),
        "",
        "## 结论",
        "",
        (
            f"- 当前市场状态：{regime}；总市值 24h "
            f"{pct(global_market.get('market_cap_change_24h_percent'))}，"
            f"BTC dominance {pct(global_market.get('btc_dominance_percent'))}，"
            f"ETH dominance {pct(global_market.get('eth_dominance_percent'))}。"
        ),
        (
            f"- 稳定币供给约 {money(stable.get('total_market_cap_usd'))}；"
            "可作为链上流动性和风险偏好的辅助观察，不单独解释为买卖信号。"
        ),
        (
            f"- DeFi 重点看 TVL 变化、稳定币流向、收益池 TVL/APY 是否异常，"
            "结论仅用于研究分析，不构成投资建议。"
        ),
        "",
        "## 关键数据",
        "",
        render_coin_line("BTC", btc),
        render_coin_line("ETH", eth),
        (
            f"- Total market cap: {money(global_market.get('total_market_cap'))}; "
            f"24h volume: {money(global_market.get('total_volume'))}; "
            f"active coins: {global_market.get('active_cryptocurrencies', 'n/a')}"
        ),
        (
            f"- DeFi market cap: {money(global_market.get('defi_market_cap'))}; "
            f"DeFi dominance: {pct(global_market.get('defi_dominance_percent'))}"
        ),
        "",
        "## DeFi 与稳定币",
        "",
    ]

    if top_protocols:
        lines.append("- Top protocols by TVL:")
        for item in top_protocols[:5]:
            lines.append(
                f"  - {item.get('name')} ({item.get('category')}): "
                f"TVL {money(item.get('tvl'))}, 7d {pct(item.get('change_7d_percent'))}"
            )
    else:
        lines.append("- Top protocols by TVL: n/a")

    if top_chains:
        lines.append("- Top chains by TVL:")
        for item in top_chains[:5]:
            lines.append(f"  - {item.get('name')}: {money(item.get('tvl'))}")

    if top_stables:
        lines.append("- Top stablecoins:")
        for item in top_stables[:5]:
            lines.append(f"  - {item.get('symbol')}: {money(item.get('circulating_usd'))}")

    if stable_chains:
        lines.append("- Stablecoin supply by chain:")
        for item in stable_chains[:5]:
            lines.append(f"  - {item.get('name')}: {money(item.get('circulating_usd'))}")

    lines.extend([
        "",
        "## 收益池观察",
        "",
    ])
    if yields:
        for item in yields[:5]:
            lines.append(
                f"- {item.get('project')} / {item.get('symbol')} on {item.get('chain')}: "
                f"TVL {money(item.get('tvl_usd'))}, APY {pct(item.get('apy'))}, "
                f"stablecoin={item.get('stablecoin')}, exposure={item.get('exposure')}, "
                f"IL risk={item.get('il_risk')}"
            )
    else:
        lines.append("- No yield-pool data available.")

    lines.extend(render_watchlist_radar(watchlist))

    lines.extend([
        "",
        "## 机制",
        "",
        "- BTC/ETH 与总市值变化用于观察风险偏好，但短期价格动作需要和成交量、宏观事件、监管新闻一起验证。",
        "- 稳定币供给和链分布可辅助判断链上流动性迁移；单日变化可能受发行、赎回、跨链桥和交易所钱包调整影响。",
        "- DeFi TVL 和收益池 APY 需要区分真实需求、奖励补贴、价格波动和统计口径变化。",
        "",
        "## 风险/不确定性",
        "",
        "- 这是研究分析，不是投资建议；不要把任何单一指标当作确定性买卖信号。",
        "- API 数据可能有延迟、口径调整或临时缺失；重大新闻、监管事件、黑客攻击需要用官方来源再次确认。",
        "- 高 APY 可能来自补贴、低流动性、合约风险、预言机风险、稳定币脱锚风险或退出流动性不足。",
        "",
        "## 下一步",
        "",
        "- 若要发布给用户，补充当日新闻、监管和宏观来源，再区分事实、推断与假设。",
        "- 若要归档，写入 `knowledge/crypto/briefs/`，并更新 `knowledge/index.md` 与 `knowledge/log.md`。",
        "- 对重点资产或协议另建 `knowledge/crypto/assets/` 或 `knowledge/crypto/events/` 页面。",
        "",
        "## 来源",
        "",
        render_sources(),
    ])

    if errors:
        lines.extend([
            "",
            "## 数据缺口",
            "",
            *[f"- {error}" for error in errors],
        ])

    return "\n".join(lines) + "\n"


def update_index(knowledge_dir: Path, rel_path: str, title: str) -> None:
    index_path = knowledge_dir / "index.md"
    content = index_path.read_text(encoding="utf-8") if index_path.exists() else "# Knowledge Index\n"
    line = f"- [{title}]({rel_path}) — Automated crypto market brief"
    if line in content:
        return
    heading = "## Crypto"
    if heading in content:
        content = content.replace(heading, f"{heading}\n\n{line}", 1)
    else:
        if not content.endswith("\n"):
            content += "\n"
        content += f"\n{heading}\n\n{line}\n"
    index_path.write_text(content, encoding="utf-8")


def append_log(knowledge_dir: Path, title: str) -> None:
    log_path = knowledge_dir / "log.md"
    line = f"## [{date.today().isoformat()}] synthesize | {title}\n"
    if log_path.exists() and line in log_path.read_text(encoding="utf-8"):
        return
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line)


def write_brief(args: argparse.Namespace, markdown: str) -> Path:
    if not args.workspace:
        raise ValueError("--workspace is required with --write")
    knowledge_dir = Path(args.workspace).expanduser() / "knowledge"
    target_dir = knowledge_dir / "crypto" / "briefs"
    target_dir.mkdir(parents=True, exist_ok=True)

    title = args.topic or f"Crypto {args.cadence.title()} Brief"
    filename = f"{args.date}-{slugify(title)}.md"
    target = target_dir / filename
    target.write_text(markdown, encoding="utf-8")

    rel_path = str(target.relative_to(knowledge_dir)).replace("\\", "/")
    update_index(knowledge_dir, rel_path, f"{args.date} {title}")
    append_log(knowledge_dir, f"{args.date} {title}")
    return target


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", help="ZVAgent workspace path. Required with --write.")
    parser.add_argument("--write", action="store_true", help="Write into workspace knowledge/crypto/briefs.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Brief date in YYYY-MM-DD.")
    parser.add_argument("--cadence", default="daily", choices=["daily", "weekly", "monthly", "ad-hoc"])
    parser.add_argument("--topic", default="", help="Human-readable brief title.")
    parser.add_argument("--currency", default="usd")
    parser.add_argument("--coin-count", type=int, default=20)
    parser.add_argument("--defi-count", type=int, default=10)
    parser.add_argument("--chain-count", type=int, default=8)
    parser.add_argument("--stablecoin-count", type=int, default=10)
    parser.add_argument("--yield-count", type=int, default=10)
    parser.add_argument("--min-yield-tvl", type=float, default=10_000_000)
    parser.add_argument("--stable-yields", action="store_true", help="Only include pools marked as stablecoin pools.")
    parser.add_argument("--include-trends", action="store_true", help="Also fetch 30-day BTC/ETH trend data.")
    parser.add_argument("--watchlist", help="Path to watchlist JSON. Defaults to <workspace>/knowledge/crypto/watchlist.json when --workspace is set.")
    parser.add_argument("--json", action="store_true", help="When writing, print JSON instead of a path line.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data, errors = collect_data(args)
    markdown = render_brief(args, data, errors)
    if args.write:
        target = write_brief(args, markdown)
        payload = {"status": "success", "path": str(target), "errors": errors}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False))
        else:
            print(f"Wrote {target}")
    else:
        print(markdown, end="")


if __name__ == "__main__":
    main()
