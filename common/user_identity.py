# encoding:utf-8

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class UserIdentity:
    user_key: str
    channel_type: str
    platform_user_id: str
    account_id: str = ""
    display_name: str = ""


def safe_identity_part(value: str, default: str = "unknown") -> str:
    value = str(value or "").strip()
    if not value:
        return default
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def build_user_key(channel_type: str, platform_user_id: str, account_id: str = "") -> str:
    channel = safe_identity_part(channel_type or "unknown")
    user = safe_identity_part(platform_user_id or "anonymous", "anonymous")
    account = safe_identity_part(account_id or "", "")
    if account:
        return f"{channel}__{account}__user__{user}"
    return f"{channel}__user__{user}"


def make_identity(
    channel_type: str,
    platform_user_id: str,
    account_id: str = "",
    display_name: str = "",
) -> UserIdentity:
    return UserIdentity(
        user_key=build_user_key(channel_type, platform_user_id, account_id),
        channel_type=str(channel_type or ""),
        platform_user_id=str(platform_user_id or ""),
        account_id=str(account_id or ""),
        display_name=str(display_name or platform_user_id or ""),
    )


def apply_context_identity(
    context,
    channel_type: str,
    platform_user_id: str,
    account_id: str = "",
    display_name: str = "",
):
    identity = make_identity(channel_type, platform_user_id, account_id, display_name)
    context["user_key"] = identity.user_key
    context["user_id"] = identity.user_key
    context["platform_user_id"] = identity.platform_user_id
    context["identity_channel_type"] = identity.channel_type
    context["identity_account_id"] = identity.account_id
    context["display_name"] = identity.display_name
    return identity


def context_user_key(context) -> str:
    if not context:
        return ""
    if hasattr(context, "get"):
        for key in ("user_key", "quota_user_id", "user_id", "session_id", "receiver"):
            value = context.get(key, "")
            if value:
                return str(value)
    return "anonymous"
