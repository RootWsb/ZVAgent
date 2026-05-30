"""
channel factory
"""
from common import const
from .channel import Channel


def split_channel_spec(channel_spec: str) -> tuple:
    """
    Split a configured channel entry into (base_type, instance_id).

    Examples:
      "weixin" -> ("weixin", "")
      "weixin:wx1" -> ("weixin", "wx1")
    """
    if not isinstance(channel_spec, str):
        return channel_spec, ""
    raw = channel_spec.strip()
    if ":" not in raw:
        return raw, ""
    base, instance_id = raw.split(":", 1)
    return base.strip(), instance_id.strip()


def create_channel(channel_type) -> Channel:
    """
    create a channel instance
    :param channel_type: channel type code
    :return: channel instance
    """
    channel_spec = channel_type
    base_type, instance_id = split_channel_spec(channel_spec)

    ch = Channel()
    if base_type == 'web':
        from channel.web.web_channel import WebChannel
        ch = WebChannel()
    elif base_type == const.QQ:
        from channel.qq.qq_channel import QQChannel
        ch = QQChannel()
    elif base_type in (const.WEIXIN, "wx"):
        from channel.weixin.weixin_channel import WeixinChannel
        ch = WeixinChannel(instance_id=instance_id)
        base_type = const.WEIXIN
    else:
        raise RuntimeError(f"Unsupported channel type: {channel_type}")
    ch.channel_type = channel_spec if instance_id else base_type
    ch.base_channel_type = base_type
    ch.instance_id = instance_id
    return ch
