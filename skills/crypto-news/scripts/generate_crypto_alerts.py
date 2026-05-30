#!/usr/bin/env python3
"""Generate watchlist alerts with optional social narrative signals.

The script combines structured market data from CoinGecko/DefiLlama with an
optional social-hot-topics JSON file. Social signals are treated as narrative
and risk context, not as standalone buy/sell instructions.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from fetch_crypto_data import (
    fetch_coin_detail,
    fetch_global_market,
    fetch_protocol_detail,
    fetch_stablecoin_overview,
)


DEFAULT_SETTINGS = {
    "currency": "usd",
    "price_24h_alert_pct": 5,
    "price_7d_alert_pct": 10,
    "tvl_7d_alert_pct": 10,
    "volume_to_mcap_min": 0.02,
    "chain_concentration_alert_pct": 80,
    "ath_drawdown_alert_pct": -70,
    "stablecoin_1d_alert_pct": 1.5,
    "social_mentions_alert_min": 1000,
    "social_velocity_alert_pct": 150,
    "social_sentiment_abs_alert": 0.65,
}

SOURCE_LINKS = [
    ("CoinGecko API", "https://docs.coingecko.com/reference/introduction"),
    ("DefiLlama API", "https://defillama.com/docs/api"),
]

SEVERITY_RANK = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def expand_path(path: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(path))).resolve()


def default_watchlist_path(workspace: str | None) -> Path | None:
    if not workspace:
        return None
    return expand_path(workspace) / "knowledge" / "crypto" / "watchlist.json"


def default_social_path(workspace: str | None) -> Path | None:
    if not workspace:
        return None
    return expand_path(workspace) / "knowledge" / "crypto" / "social_hot_topics.json"


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "crypto-alerts"


def number(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def pct(value: Any) -> str:
    try:
        return f"{float(value):+.2f}%"
    except (TypeError, ValueError):
        return "n/a"


def money(value: Any) -> str:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return "n/a"
    sign = "-" if amount < 0 else ""
    amount = abs(amount)
    if amount >= 1_000_000_000_000:
        return f"{sign}${amount / 1_000_000_000_000:.2f}T"
    if amount >= 1_000_000_000:
        return f"{sign}${amount / 1_000_000_000:.2f}B"
    if amount >= 1_000_000:
        return f"{sign}${amount / 1_000_000:.2f}M"
    if amount >= 1_000:
        return f"{sign}${amount / 1_000:.2f}K"
    return f"{sign}${amount:.2f}"


def price(value: Any) -> str:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if amount >= 1000:
        return f"${amount:,.0f}"
    if amount >= 1:
        return f"${amount:,.2f}"
    return f"${amount:,.6f}"


def require_success(name: str, result: Dict[str, Any]) -> Dict[str, Any]:
    if result.get("status") != "success":
        raise RuntimeError(f"{name} failed: {result}")
    data = result.get("data")
    if not isinstance(data, dict):
        raise RuntimeError(f"{name} returned invalid data")
    return data


def load_json_object(path: Path, label: str) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{label} must be a JSON object: {path}")
    return data


def load_watchlist(args: argparse.Namespace) -> Dict[str, Any]:
    path = expand_path(args.watchlist) if args.watchlist else default_watchlist_path(args.workspace)
    if not path or not path.exists():
        return {"settings": dict(DEFAULT_SETTINGS), "assets": [], "_path": str(path) if path else ""}
    data = load_json_object(path, "watchlist")
    settings = dict(DEFAULT_SETTINGS)
    settings.update(data.get("settings") or {})
    assets = data.get("assets") or []
    if not isinstance(assets, list):
        raise ValueError("watchlist.assets must be a list")
    return {"settings": settings, "assets": assets, "_path": str(path)}


def load_social(args: argparse.Namespace) -> Dict[str, Any]:
    path = expand_path(args.social_json) if args.social_json else default_social_path(args.workspace)
    if not path or not path.exists():
        return {"topics": [], "sources": [], "_path": str(path) if path else ""}
    data = load_json_object(path, "social topics")
    topics = data.get("topics") or []
    sources = data.get("sources") or []
    if not isinstance(topics, list):
        raise ValueError("social topics must contain a list field: topics")
    if not isinstance(sources, list):
        raise ValueError("social topics sources must be a list")
    data["_path"] = str(path)
    data["topics"] = topics
    data["sources"] = sources
    return data


def asset_label(asset: Dict[str, Any], detail: Dict[str, Any] | None = None) -> str:
    detail = detail or {}
    return (
        detail.get("name")
        or asset.get("name")
        or asset.get("symbol")
        or asset.get("id")
        or asset.get("slug")
        or "unknown"
    )


def normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def token_set(values: Iterable[Any]) -> set[str]:
    return {normalize_text(value) for value in values if normalize_text(value)}


def asset_aliases(asset: Dict[str, Any], detail: Dict[str, Any] | None = None) -> set[str]:
    detail = detail or {}
    aliases = token_set([
        asset.get("id"),
        asset.get("slug"),
        asset.get("symbol"),
        asset.get("name"),
        detail.get("id"),
        detail.get("slug"),
        detail.get("symbol"),
        detail.get("name"),
    ])
    return aliases


def topic_matches_asset(topic: Dict[str, Any], asset: Dict[str, Any], detail: Dict[str, Any] | None = None) -> bool:
    aliases = asset_aliases(asset, detail)
    explicit = token_set([
        topic.get("coin_id"),
        topic.get("protocol_slug"),
        topic.get("asset"),
        topic.get("symbol"),
        topic.get("name"),
    ])
    if aliases & explicit:
        return True
    topic_text = normalize_text(topic.get("topic") or topic.get("title"))
    if not topic_text:
        return False
    words = set(re.findall(r"[a-z0-9][a-z0-9-]{1,}", topic_text))
    return bool(aliases & words)


def split_social_topics(
    topics: List[Dict[str, Any]],
    asset: Dict[str, Any],
    detail: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    return [topic for topic in topics if isinstance(topic, dict) and topic_matches_asset(topic, asset, detail)]


def sentiment_value(topic: Dict[str, Any]) -> Tuple[str, float]:
    raw = normalize_text(topic.get("sentiment"))
    score = number(topic.get("sentiment_score"), 0.0)
    if not raw:
        if score > 0.15:
            raw = "positive"
        elif score < -0.15:
            raw = "negative"
        else:
            raw = "neutral"
    if raw in {"bearish", "fear", "panic"}:
        raw = "negative"
    if raw in {"bullish", "greed", "hype"}:
        raw = "positive"
    return raw, score


def add_alert(
    alerts: List[Dict[str, Any]],
    severity: str,
    asset: str,
    category: str,
    title: str,
    evidence: List[str],
    next_step: str,
) -> None:
    alerts.append({
        "severity": severity,
        "asset": asset,
        "category": category,
        "title": title,
        "evidence": evidence,
        "next_step": next_step,
    })


def raise_severity(base: str, escalated: str) -> str:
    return escalated if SEVERITY_RANK[escalated] > SEVERITY_RANK[base] else base


def evaluate_coin(
    asset: Dict[str, Any],
    detail: Dict[str, Any],
    settings: Dict[str, Any],
    social_topics: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    alerts: List[Dict[str, Any]] = []
    label = f"{asset_label(asset, detail)} ({detail.get('symbol') or asset.get('symbol') or asset.get('id')})"
    change_24h = number(detail.get("price_change_24h"))
    change_7d = number(detail.get("price_change_7d"))
    volume = number(detail.get("total_volume"))
    market_cap = number(detail.get("market_cap"))
    ath_drawdown = number(detail.get("ath_change_percentage"))

    if abs(change_24h) >= number(settings.get("price_24h_alert_pct"), 5):
        severity = "high" if abs(change_24h) >= number(settings.get("price_24h_alert_pct"), 5) * 2 else "medium"
        add_alert(
            alerts,
            severity,
            label,
            "market",
            "24h price move crossed watchlist threshold",
            [
                f"Current price {price(detail.get('current_price'))}",
                f"24h change {pct(change_24h)}",
                f"threshold {pct(settings.get('price_24h_alert_pct'))}",
            ],
            "Check whether the move is confirmed by volume, liquidation/news flow, and official project updates.",
        )

    if abs(change_7d) >= number(settings.get("price_7d_alert_pct"), 10):
        severity = "high" if abs(change_7d) >= number(settings.get("price_7d_alert_pct"), 10) * 1.8 else "medium"
        add_alert(
            alerts,
            severity,
            label,
            "market",
            "7d price trend crossed watchlist threshold",
            [
                f"7d change {pct(change_7d)}",
                f"market cap {money(market_cap)}",
                f"24h volume {money(volume)}",
            ],
            "Compare the trend with BTC/ETH beta and the asset's own catalyst calendar.",
        )

    turnover = volume / market_cap if market_cap > 0 else 0
    if market_cap > 0 and turnover < number(settings.get("volume_to_mcap_min"), 0.02):
        add_alert(
            alerts,
            "low",
            label,
            "liquidity",
            "Thin turnover relative to market cap",
            [
                f"24h volume / market cap {turnover:.2%}",
                f"minimum watchlist threshold {number(settings.get('volume_to_mcap_min'), 0.02):.2%}",
            ],
            "Treat price moves with extra caution because low turnover can exaggerate slippage and noise.",
        )

    if ath_drawdown <= number(settings.get("ath_drawdown_alert_pct"), -70):
        add_alert(
            alerts,
            "low",
            label,
            "drawdown",
            "Deep drawdown from ATH",
            [f"ATH drawdown {pct(ath_drawdown)}", f"ATH {price(detail.get('ath'))}"],
            "Separate long-term impairment risk from ordinary cycle drawdown before forming scenarios.",
        )

    alerts.extend(evaluate_social(label, social_topics, settings, change_24h, change_7d, None))
    return alerts


def recent_tvl_change(recent_tvl: List[Dict[str, Any]], days: int = 7) -> float | None:
    if not isinstance(recent_tvl, list) or len(recent_tvl) < 2:
        return None
    latest = number((recent_tvl[-1] or {}).get("totalLiquidityUSD"))
    previous_index = max(0, len(recent_tvl) - days - 1)
    previous = number((recent_tvl[previous_index] or {}).get("totalLiquidityUSD"))
    if previous <= 0:
        return None
    return (latest - previous) / previous * 100


def evaluate_protocol(
    asset: Dict[str, Any],
    detail: Dict[str, Any],
    recent_tvl: List[Dict[str, Any]],
    settings: Dict[str, Any],
    social_topics: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    alerts: List[Dict[str, Any]] = []
    label = f"{asset_label(asset, detail)} ({detail.get('category') or 'protocol'})"
    tvl_change = recent_tvl_change(recent_tvl)
    current_tvl = number(detail.get("current_tvl"))

    if tvl_change is not None and abs(tvl_change) >= number(settings.get("tvl_7d_alert_pct"), 10):
        severity = "high" if abs(tvl_change) >= number(settings.get("tvl_7d_alert_pct"), 10) * 1.8 else "medium"
        add_alert(
            alerts,
            severity,
            label,
            "defi",
            "7d TVL move crossed watchlist threshold",
            [f"Current TVL {money(current_tvl)}", f"7d TVL change {pct(tvl_change)}"],
            "Verify whether TVL moved because of token price, incentives, withdrawals, exploit risk, or methodology changes.",
        )

    chain_tvls = detail.get("chain_tvls") or []
    total_chain_tvl = sum(number(row.get("current_tvl")) for row in chain_tvls if isinstance(row, dict))
    if total_chain_tvl > 0 and chain_tvls:
        top = max(chain_tvls, key=lambda row: number(row.get("current_tvl")))
        concentration = number(top.get("current_tvl")) / total_chain_tvl * 100
        if concentration >= number(settings.get("chain_concentration_alert_pct"), 80):
            add_alert(
                alerts,
                "low",
                label,
                "concentration",
                "Protocol TVL is concentrated on one chain",
                [
                    f"Top chain {top.get('chain')}: {pct(concentration)} of summarized TVL",
                    f"current TVL {money(current_tvl)}",
                ],
                "Monitor chain-specific outages, bridge risk, incentive changes, and governance proposals.",
            )

    alerts.extend(evaluate_social(label, social_topics, settings, None, None, tvl_change))
    return alerts


def evaluate_social(
    label: str,
    topics: List[Dict[str, Any]],
    settings: Dict[str, Any],
    change_24h: float | None,
    change_7d: float | None,
    tvl_change: float | None,
) -> List[Dict[str, Any]]:
    alerts: List[Dict[str, Any]] = []
    for topic in topics:
        sentiment, score = sentiment_value(topic)
        mentions = number(topic.get("mentions"))
        velocity = number(topic.get("velocity_24h_pct"))
        topic_name = topic.get("topic") or topic.get("title") or "social topic"
        if (
            mentions < number(settings.get("social_mentions_alert_min"), 1000)
            and velocity < number(settings.get("social_velocity_alert_pct"), 150)
            and abs(score) < number(settings.get("social_sentiment_abs_alert"), 0.65)
        ):
            continue

        severity = "medium"
        if velocity >= number(settings.get("social_velocity_alert_pct"), 150) * 2 or abs(score) >= 0.85:
            severity = "high"
        if mentions >= number(settings.get("social_mentions_alert_min"), 1000) * 5:
            severity = raise_severity(severity, "high")

        confirmation = "No direct market/on-chain confirmation in this snapshot; treat as a watch-only narrative spike."
        if sentiment == "negative":
            if (change_24h is not None and change_24h < 0) or (change_7d is not None and change_7d < 0) or (tvl_change is not None and tvl_change < 0):
                confirmation = "Negative social pressure is directionally confirmed by price/TVL weakness."
                severity = raise_severity(severity, "high")
        elif sentiment == "positive":
            if (change_24h is not None and change_24h > 0) or (change_7d is not None and change_7d > 0) or (tvl_change is not None and tvl_change > 0):
                confirmation = "Positive social momentum is directionally confirmed by price/TVL strength."

        links = topic.get("sample_links") or topic.get("links") or []
        if isinstance(links, str):
            links = [links]
        evidence = [
            f"Topic: {topic_name}",
            f"sentiment={sentiment}, score={score:.2f}",
            f"mentions={mentions:.0f}, 24h velocity={pct(velocity)}",
            confirmation,
        ]
        evidence.extend(str(link) for link in links[:3])
        note = topic.get("notes")
        if note:
            evidence.append(f"notes: {note}")

        add_alert(
            alerts,
            severity,
            label,
            "social",
            "Social narrative spike detected",
            evidence,
            "Cross-check with official announcements, exchange/listing data, liquidation data, and credible news before using this signal.",
        )
    return alerts


def evaluate_global_liquidity(settings: Dict[str, Any], errors: List[str]) -> List[Dict[str, Any]]:
    alerts: List[Dict[str, Any]] = []
    try:
        stable_data = require_success("stablecoin_overview", fetch_stablecoin_overview(10))
        stable = stable_data.get("stablecoin_overview") or {}
        top_chains = stable.get("top_chains") or []
        for chain in top_chains[:5]:
            change = number(chain.get("change_1d_percent"))
            if abs(change) >= number(settings.get("stablecoin_1d_alert_pct"), 1.5):
                add_alert(
                    alerts,
                    "medium",
                    f"{chain.get('name')} stablecoin supply",
                    "liquidity",
                    "Stablecoin supply moved sharply on a major chain",
                    [
                        f"1d supply change {pct(change)}",
                        f"circulating supply {money(chain.get('circulating_usd'))}",
                    ],
                    "Check whether the move reflects mint/redeem flows, bridge movement, exchange wallets, or data methodology changes.",
                )
    except Exception as exc:
        errors.append(f"stablecoin_overview: {exc}")
    return alerts


def collect_alerts(args: argparse.Namespace) -> Tuple[Dict[str, Any], List[str]]:
    errors: List[str] = []
    watchlist = load_watchlist(args)
    social = load_social(args)
    settings = watchlist.get("settings") or dict(DEFAULT_SETTINGS)
    alerts: List[Dict[str, Any]] = []
    snapshots: List[Dict[str, Any]] = []

    for asset in watchlist.get("assets", []):
        if not isinstance(asset, dict):
            continue
        kind = asset.get("type")
        try:
            if kind == "coin":
                coin_id = asset.get("id")
                if not coin_id:
                    raise ValueError("coin asset missing id")
                detail = require_success(f"coin {coin_id}", fetch_coin_detail(coin_id)).get("coin_detail") or {}
                topics = split_social_topics(social.get("topics") or [], asset, detail)
                alerts.extend(evaluate_coin(asset, detail, settings, topics))
                snapshots.append({"asset": asset, "detail": detail, "social_topics": len(topics)})
            elif kind == "protocol":
                slug = asset.get("slug")
                if not slug:
                    raise ValueError("protocol asset missing slug")
                data = require_success(f"protocol {slug}", fetch_protocol_detail(slug))
                detail = data.get("protocol_detail") or {}
                recent_tvl = data.get("recent_tvl") or []
                topics = split_social_topics(social.get("topics") or [], asset, detail)
                alerts.extend(evaluate_protocol(asset, detail, recent_tvl, settings, topics))
                snapshots.append({"asset": asset, "detail": detail, "social_topics": len(topics)})
            else:
                errors.append(f"watchlist: unsupported asset type {kind}")
        except Exception as exc:
            topics = split_social_topics(social.get("topics") or [], asset, {})
            if topics:
                label = f"{asset_label(asset)} (unverified)"
                alerts.extend(evaluate_social(label, topics, settings, None, None, None))
                snapshots.append({"asset": asset, "detail": {}, "social_topics": len(topics), "unverified": True})
            errors.append(f"watchlist {asset.get('name') or asset.get('id') or asset.get('slug')}: {exc}")

    if args.include_liquidity:
        alerts.extend(evaluate_global_liquidity(settings, errors))

    if not watchlist.get("assets"):
        errors.append("watchlist has no assets; add coins/protocols with manage_crypto_watchlist.py")

    global_market: Dict[str, Any] = {}
    try:
        global_market = require_success("global_market", fetch_global_market(settings.get("currency", "usd"))).get("global_market") or {}
    except Exception as exc:
        errors.append(f"global_market: {exc}")

    alerts.sort(key=lambda item: SEVERITY_RANK.get(item.get("severity", "info"), 0), reverse=True)
    return {
        "watchlist": watchlist,
        "social": social,
        "settings": settings,
        "alerts": alerts,
        "snapshots": snapshots,
        "global_market": global_market,
    }, errors


def severity_summary(alerts: List[Dict[str, Any]]) -> str:
    if not alerts:
        return "No threshold alerts in this snapshot"
    counts: Dict[str, int] = {}
    for alert in alerts:
        counts[alert.get("severity", "info")] = counts.get(alert.get("severity", "info"), 0) + 1
    return ", ".join(f"{key}={counts[key]}" for key in ["critical", "high", "medium", "low", "info"] if key in counts)


def render_sources(social: Dict[str, Any]) -> List[str]:
    lines = [f"- [{name}]({url})" for name, url in SOURCE_LINKS]
    for source in social.get("sources") or []:
        if not isinstance(source, dict):
            continue
        name = source.get("name") or "Social source"
        url = source.get("url")
        if url:
            lines.append(f"- [{name}]({url})")
        else:
            lines.append(f"- {name}")
    if social.get("_path"):
        lines.append(f"- Local social input: `{social.get('_path')}`")
    return lines


def render_social_contract() -> str:
    sample = {
        "timestamp": "2026-05-22T09:00:00+08:00",
        "sources": [{"name": "X/Twitter", "url": "https://x.com/search?q=BTC"}],
        "topics": [
            {
                "asset": "BTC",
                "coin_id": "bitcoin",
                "topic": "ETF flow discussion",
                "mentions": 1200,
                "sentiment": "positive",
                "sentiment_score": 0.68,
                "velocity_24h_pct": 240,
                "sample_links": ["https://example.com/post"],
                "notes": "Short context for the discussion spike.",
            }
        ],
    }
    return json.dumps(sample, ensure_ascii=False, indent=2)


def render_markdown(args: argparse.Namespace, data: Dict[str, Any], errors: List[str]) -> str:
    generated = datetime.now().isoformat(timespec="seconds")
    title = args.topic or "Crypto Watchlist Alerts"
    alerts = data.get("alerts") or []
    social = data.get("social") or {}
    watchlist = data.get("watchlist") or {}
    global_market = data.get("global_market") or {}
    social_topics = social.get("topics") or []

    if alerts:
        main_line = f"{severity_summary(alerts)}; social topics loaded={len(social_topics)}."
    else:
        main_line = f"No threshold alerts; social topics loaded={len(social_topics)}."

    lines = [
        f"# {args.date} {title}",
        "",
        (
            f"> Source: automated crypto watchlist alert. Generated: {generated}. "
            "Social media is used only as a narrative/risk input."
        ),
        "",
        "## 结论",
        "",
        f"- {main_line}",
        (
            f"- Total crypto market cap 24h change: "
            f"{pct(global_market.get('market_cap_change_24h_percent'))}; "
            f"BTC dominance {pct(global_market.get('btc_dominance_percent'))}."
        ),
        "- This is research analysis, not investment advice. No single social or market indicator should be treated as a deterministic trade signal.",
        "",
        "## 依据",
        "",
        f"- Watchlist: `{watchlist.get('_path') or 'not configured'}`",
        f"- Social input: `{social.get('_path') or 'not configured'}`",
        f"- Assets checked: {len(watchlist.get('assets') or [])}",
        f"- Social topics loaded: {len(social_topics)}",
        "",
        "## 告警",
        "",
    ]

    if not alerts:
        lines.append("- No alert crossed configured thresholds in this snapshot.")
    else:
        for alert in alerts:
            lines.append(f"### [{alert.get('severity')}] {alert.get('asset')} - {alert.get('title')}")
            lines.append("")
            lines.append(f"- Category: {alert.get('category')}")
            for item in alert.get("evidence") or []:
                lines.append(f"- Evidence: {item}")
            lines.append(f"- Next check: {alert.get('next_step')}")
            lines.append("")

    lines.extend([
        "## 社交热点数据契约",
        "",
        "Use this optional JSON contract for X/Twitter, Reddit, Telegram, Discord, Farcaster, or Chinese-community trend collectors. The alert engine treats it as auxiliary context and requires cross-checking.",
        "",
        "```json",
        render_social_contract(),
        "```",
        "",
        "## 风险",
        "",
        "- Social discussion can be manipulated by bots, paid promotion, coordinated campaigns, or exchange/liquidation narratives.",
        "- Positive discussion without price/TVL/liquidity confirmation is a watch-only narrative spike, not a buy signal.",
        "- Negative discussion with price/TVL weakness is a stress-confirmation signal, but still needs official sources and market structure checks.",
        "- API data may be delayed, missing, or affected by methodology changes.",
        "",
        "## 下一步",
        "",
        "- Connect social collectors to write `knowledge/crypto/social_hot_topics.json` before each alert run.",
        "- Cross-check high-severity alerts with official project channels, exchange announcements, credible news, liquidation data, and on-chain dashboards.",
        "- Archive durable events under `knowledge/crypto/events/` and keep routine market noise out of long-term notes.",
        "",
        "## 来源",
        "",
        *render_sources(social),
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
    line = f"- [{title}]({rel_path}) - Automated crypto watchlist alerts"
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
    line = f"## [{date.today().isoformat()}] alert | {title}\n"
    if log_path.exists() and line in log_path.read_text(encoding="utf-8"):
        return
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line)


def write_alert(args: argparse.Namespace, markdown: str) -> Path:
    if not args.workspace:
        raise ValueError("--workspace is required with --write")
    knowledge_dir = expand_path(args.workspace) / "knowledge"
    target_dir = knowledge_dir / "crypto" / "alerts"
    target_dir.mkdir(parents=True, exist_ok=True)
    title = args.topic or "Crypto Watchlist Alerts"
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
    parser.add_argument("--watchlist", help="Path to watchlist JSON. Defaults to <workspace>/knowledge/crypto/watchlist.json.")
    parser.add_argument("--social-json", help="Path to optional social hot topics JSON. Defaults to <workspace>/knowledge/crypto/social_hot_topics.json.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Report date in YYYY-MM-DD.")
    parser.add_argument("--topic", default="", help="Human-readable alert title.")
    parser.add_argument("--include-liquidity", action="store_true", help="Also check major-chain stablecoin supply moves.")
    parser.add_argument("--write", action="store_true", help="Write into workspace knowledge/crypto/alerts.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        data, errors = collect_alerts(args)
        markdown = render_markdown(args, data, errors)
        target = write_alert(args, markdown) if args.write else None
        if args.json:
            payload = {
                "status": "success",
                "path": str(target) if target else None,
                "alerts": len(data.get("alerts") or []),
                "summary": severity_summary(data.get("alerts") or []),
                "errors": errors,
            }
            if not target:
                payload["markdown"] = markdown
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            if target:
                print(f"Wrote {target}")
            else:
                print(markdown, end="")
    except Exception as exc:
        if args.json:
            print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        else:
            raise


if __name__ == "__main__":
    main()
