# encoding:utf-8
"""zv quota - Token quota management commands."""

import click

from common.quota import ACTIVE, DISABLED, get_quota_manager
from config import conf, load_config


def _ensure_config_loaded():
    if not conf():
        load_config()


def _fmt_tokens(value: int) -> str:
    value = int(value or 0)
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


@click.group()
def quota():
    """Manage per-user token quotas."""


@quota.command(name="list")
@click.option("--limit", default=200, show_default=True, help="Maximum users to show.")
def list_users(limit):
    """List quota users."""
    _ensure_config_loaded()
    manager = get_quota_manager()
    users = manager.list_users(limit=limit)
    enabled = "enabled" if conf().get("quota_enabled", False) else "disabled"
    click.echo(f"Quota is {enabled}. Users: {len(users)}")
    if not users:
        click.echo("No users yet.")
        return
    click.echo("")
    click.echo(f"{'USER':40} {'STATUS':9} {'CHANNEL':12} {'QUOTA':>10} {'USED':>10} {'LEFT':>10}")
    for user in users:
        click.echo(
            f"{user['user_id'][:40]:40} {user['status'][:9]:9} {str(user.get('channel_type') or '')[:12]:12} "
            f"{_fmt_tokens(user['quota_tokens']):>10} {_fmt_tokens(user['used_tokens']):>10} {_fmt_tokens(user['remaining_tokens']):>10}"
        )


@quota.command()
@click.argument("user_id")
@click.argument("tokens", type=int)
def set(user_id, tokens):
    """Set a user's total token quota."""
    _ensure_config_loaded()
    user = get_quota_manager().set_quota(user_id, tokens)
    click.echo(f"Set {user['user_id']} quota to {user['quota_tokens']} tokens. Remaining: {user['remaining_tokens']}")


@quota.command()
@click.argument("user_id")
@click.argument("tokens", type=int)
def add(user_id, tokens):
    """Add tokens to a user's quota."""
    _ensure_config_loaded()
    user = get_quota_manager().add_quota(user_id, tokens)
    click.echo(f"Added {tokens} tokens to {user['user_id']}. Remaining: {user['remaining_tokens']}")


@quota.command(name="status")
@click.argument("user_id")
@click.argument("status_value", type=click.Choice([ACTIVE, DISABLED]))
def set_status(user_id, status_value):
    """Set user status to active or disabled."""
    _ensure_config_loaded()
    user = get_quota_manager().set_status(user_id, status_value)
    click.echo(f"{user['user_id']} status: {user['status']}")


@quota.command()
@click.argument("user_id")
@click.option("--limit", default=20, show_default=True, help="Maximum logs to show.")
def logs(user_id, limit):
    """Show recent usage logs for one user."""
    _ensure_config_loaded()
    logs = get_quota_manager().usage_logs(user_id=user_id, limit=limit)
    if not logs:
        click.echo("No usage logs.")
        return
    click.echo(f"{'TIME':12} {'TOTAL':>8} {'INPUT':>8} {'OUTPUT':>8} {'MODEL':20} SESSION")
    for row in logs:
        click.echo(
            f"{row['created_at']:12} {_fmt_tokens(row['total_tokens']):>8} "
            f"{_fmt_tokens(row['input_tokens']):>8} {_fmt_tokens(row['output_tokens']):>8} "
            f"{str(row.get('model') or '')[:20]:20} {row.get('session_id') or ''}"
        )
