import os
import re
import threading
import time
from asyncio import CancelledError
from concurrent.futures import Future, ThreadPoolExecutor

from bridge.context import *
from bridge.reply import *
from bridge.turn_event_reporter import report_turn_event
from channel.channel import Channel
from common.dequeue import Dequeue
from common import memory
from common.user_identity import apply_context_identity, context_user_key
from plugins import *

try:
    from voice.audio_convert import any_to_wav
except Exception as e:
    pass

handler_pool = ThreadPoolExecutor(max_workers=8)  # 处理消息的线程池


def markdown_to_speech_text(text: str) -> str:
    """Convert assistant Markdown into cleaner plain text for TTS."""
    if not text:
        return ""

    text = str(text)
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)

    cleaned_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append("")
            continue
        if re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?", stripped):
            continue
        stripped = re.sub(r"^\s{0,3}#{1,6}\s*", "", stripped)
        stripped = re.sub(r"^\s{0,3}>\s?", "", stripped)
        stripped = re.sub(r"^\s*[-*+]\s+", "", stripped)
        stripped = re.sub(r"^\s*\d+[.)]\s+", "", stripped)
        if "|" in stripped:
            stripped = re.sub(r"\s*\|\s*", "，", stripped.strip("| "))
        cleaned_lines.append(stripped)

    text = "\n".join(cleaned_lines)
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
    text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)
    text = re.sub(r"~~(.*?)~~", r"\1", text)
    text = re.sub(r"[$#>*_`~]+", " ", text)
    text = re.sub(r"[-=]{3,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def should_reply_with_voice(text: str) -> bool:
    """Return True only when the user explicitly asks for spoken output."""
    if not text:
        return False

    lowered = str(text).strip().lower()
    trigger_patterns = [
        r"用语音(?:回答|回复|说|读|朗读)?",
        r"语音(?:回答|回复|说|读|朗读)",
        r"(?:附带|带上|加上|生成|发送|发|给我|配)(?:一段|一个|这段|的)?语音",
        r"(?:语音版|音频版|配音版)",
        r"(?:转成|转换成|做成|输出)(?:语音|音频|mp3)",
        r"请.*(?:读出来|朗读|念出来|说出来)",
        r"(?:读一下|朗读一下|念一下|说一下)",
        r"(?:教我|练习|纠正).{0,12}发音",
        r"(?:pronounce|read aloud|speak this|voice reply|say it aloud|with audio|audio version)",
    ]
    return any(re.search(pattern, lowered) for pattern in trigger_patterns)


def strip_voice_request_text(text: str) -> str:
    """Remove channel-level voice-output instructions before sending to the LLM."""
    if not text:
        return text
    cleaned = str(text)
    patterns = [
        r"[，,。；;、\s]*(?:并|并且|同时|顺便)?(?:请)?(?:附带|带上|加上|生成|发送|发|给我|配)(?:一段|一个|这段|的)?语音[。.!！?？\s]*",
        r"[，,。；;、\s]*(?:并|并且|同时|顺便)?(?:请)?(?:转成|转换成|做成|输出)(?:语音|音频|mp3)[。.!！?？\s]*",
        r"[，,。；;、\s]*(?:语音版|音频版|配音版)[。.!！?？\s]*",
        r"^(?:请)?用语音(?:回答|回复|说|读|朗读)?[:：,，\s]*",
        r"^(?:请)?语音(?:回答|回复|说|读|朗读)[:：,，\s]*",
        r"\b(?:with audio|audio version|voice reply|read aloud|say it aloud)\b[.!?\s]*",
    ]
    for pattern in patterns:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"\s+([，,。.!！?？])", r"\1", cleaned)
    return cleaned.strip(" ，,。；;、")


# 抽象类, 它包含了与消息通道无关的通用处理逻辑
class ChatChannel(Channel):
    name = None  # 登录的用户名
    user_id = None  # 登录的用户id

    def __init__(self):
        super().__init__()
        # Instance-level attributes so each channel subclass has its own
        # independent session queue and lock. Previously these were class-level,
        # which caused contexts from one channel (e.g. Feishu) to be consumed
        # by another channel's consume() thread (e.g. Web), leading to errors
        # like "No request_id found in context".
        self.futures = {}
        self.sessions = {}
        self.lock = threading.Lock()
        _thread = threading.Thread(target=self.consume)
        _thread.setDaemon(True)
        _thread.start()

    # 根据消息构造context，消息内容相关的触发项写在这里
    def _compose_context(self, ctype: ContextType, content, **kwargs):
        context = Context(ctype, content)
        context.kwargs = kwargs
        if "channel_type" not in context:
            context["channel_type"] = self.channel_type
        if "origin_ctype" not in context:
            context["origin_ctype"] = ctype
        # context首次传入时，receiver是None，根据类型设置receiver
        first_in = "receiver" not in context
        # 群名匹配过程，设置session_id和receiver
        if first_in:  # context首次传入时，receiver是None，根据类型设置receiver
            config = conf()
            cmsg = context["msg"]
            user_data = conf().get_user_data(cmsg.from_user_id)
            context["openai_api_key"] = user_data.get("openai_api_key")
            context["gpt_model"] = user_data.get("gpt_model")
            if context.get("isgroup", False):
                group_name = cmsg.other_user_nickname
                group_id = cmsg.other_user_id

                group_name_white_list = config.get("group_name_white_list", [])
                group_name_keyword_white_list = config.get("group_name_keyword_white_list", [])
                if any(
                    [
                        group_name in group_name_white_list,
                        "ALL_GROUP" in group_name_white_list,
                        check_contain(group_name, group_name_keyword_white_list),
                    ]
                ):
                    # Check global group_shared_session config first
                    group_shared_session = conf().get("group_shared_session", True)
                    if group_shared_session:
                        # All users in the group share the same session
                        session_id = group_id
                    else:
                        # Check group-specific whitelist (legacy behavior)
                        group_chat_in_one_session = conf().get("group_chat_in_one_session", [])
                        session_id = cmsg.actual_user_id
                        if any(
                            [
                                group_name in group_chat_in_one_session,
                                "ALL_GROUP" in group_chat_in_one_session,
                            ]
                        ):
                            session_id = group_id
                else:
                    logger.debug(f"No need reply, groupName not in whitelist, group_name={group_name}")
                    return None
                context["session_id"] = session_id
                context["receiver"] = group_id
            else:
                context["session_id"] = cmsg.other_user_id
                context["receiver"] = cmsg.other_user_id
            e_context = PluginManager().emit_event(EventContext(Event.ON_RECEIVE_MESSAGE, {"channel": self, "context": context}))
            context = e_context["context"]
            if e_context.is_pass() or context is None:
                return context
            if "user_key" not in context:
                platform_user_id = getattr(cmsg, "actual_user_id", "") or getattr(cmsg, "from_user_id", "") or context.get("session_id", "")
                account_id = getattr(self, "instance_id", "") or getattr(self, "account_id", "")
                display_name = getattr(cmsg, "actual_user_nickname", "") or getattr(cmsg, "from_user_nickname", "") or platform_user_id
                apply_context_identity(context, self.channel_type, platform_user_id, account_id, display_name)
            if cmsg.from_user_id == self.user_id and not config.get("trigger_by_self", True):
                logger.debug("[chat_channel]self message skipped")
                return None

        # 消息内容匹配过程，并处理content
        if ctype == ContextType.TEXT:
            if first_in and "」\n- - - - - - -" in content:  # 初次匹配 过滤引用消息
                logger.debug(content)
                logger.debug("[chat_channel]reference query skipped")
                return None

            nick_name_black_list = conf().get("nick_name_black_list", [])
            if context.get("isgroup", False):  # 群聊
                # 校验关键字
                match_prefix = check_prefix(content, conf().get("group_chat_prefix"))
                match_contain = check_contain(content, conf().get("group_chat_keyword"))
                flag = False
                if context["msg"].to_user_id != context["msg"].actual_user_id:
                    if match_prefix is not None or match_contain is not None:
                        flag = True
                        if match_prefix:
                            content = content.replace(match_prefix, "", 1).strip()
                    if context["msg"].is_at:
                        nick_name = context["msg"].actual_user_nickname
                        if nick_name and nick_name in nick_name_black_list:
                            # 黑名单过滤
                            logger.warning(f"[chat_channel] Nickname {nick_name} in In BlackList, ignore")
                            return None

                        logger.info("[chat_channel]receive group at")
                        if not conf().get("group_at_off", False):
                            flag = True
                        self.name = self.name if self.name is not None else ""  # 部分渠道self.name可能没有赋值
                        pattern = f"@{re.escape(self.name)}(\u2005|\u0020)"
                        subtract_res = re.sub(pattern, r"", content)
                        if isinstance(context["msg"].at_list, list):
                            for at in context["msg"].at_list:
                                pattern = f"@{re.escape(at)}(\u2005|\u0020)"
                                subtract_res = re.sub(pattern, r"", subtract_res)
                        if subtract_res == content and context["msg"].self_display_name:
                            # 前缀移除后没有变化，使用群昵称再次移除
                            pattern = f"@{re.escape(context['msg'].self_display_name)}(\u2005|\u0020)"
                            subtract_res = re.sub(pattern, r"", content)
                        content = subtract_res
                if not flag:
                    if context["origin_ctype"] == ContextType.VOICE:
                        logger.info("[chat_channel]receive group voice, but checkprefix didn't match")
                    return None
            else:  # 单聊
                nick_name = context["msg"].from_user_nickname
                if nick_name and nick_name in nick_name_black_list:
                    # 黑名单过滤
                    logger.warning(f"[chat_channel] Nickname '{nick_name}' in In BlackList, ignore")
                    return None

                match_prefix = check_prefix(content, conf().get("single_chat_prefix", [""]))
                if match_prefix is not None:  # 判断如果匹配到自定义前缀，则返回过滤掉前缀+空格后的内容
                    content = content.replace(match_prefix, "", 1).strip()
                elif context["origin_ctype"] == ContextType.VOICE:  # 如果源消息是私聊的语音消息，允许不匹配前缀，放宽条件
                    pass
                else:
                    logger.info("[chat_channel]receive single chat msg, but checkprefix didn't match")
                    return None
            content = content.strip()
            img_match_prefix = check_prefix(content, conf().get("image_create_prefix",[""]))
            if img_match_prefix:
                content = content.replace(img_match_prefix, "", 1)
                context.type = ContextType.IMAGE_CREATE
            else:
                context.type = ContextType.TEXT
            context.content = content.strip()
            if "desire_rtype" not in context and conf().get("always_reply_voice") and ReplyType.VOICE not in self.NOT_SUPPORT_REPLYTYPE:
                context["desire_rtype"] = ReplyType.VOICE
            if "desire_rtype" not in context and should_reply_with_voice(context.content) and ReplyType.VOICE not in self.NOT_SUPPORT_REPLYTYPE:
                context["desire_rtype"] = ReplyType.VOICE
                spoken_content = strip_voice_request_text(context.content)
                if spoken_content:
                    context.content = spoken_content
        elif context.type == ContextType.VOICE:
            if "desire_rtype" not in context and conf().get("voice_reply_voice") and ReplyType.VOICE not in self.NOT_SUPPORT_REPLYTYPE:
                context["desire_rtype"] = ReplyType.VOICE
        return context

    def _handle(self, context: Context):
        if context is None or not context.content:
            return
        logger.debug("[chat_channel] handling context: {}".format(context))
        command_reply = self._handle_builtin_user_command(context)
        if command_reply is not None:
            self._send_reply(context, command_reply)
            return
        quota_precheck = self._quota_precheck(context)
        if quota_precheck is not None:
            self._send_reply(context, quota_precheck)
            self._report_turn_event(context, quota_precheck)
            return
        # reply的构建步骤
        reply = self._generate_reply(context)

        logger.debug("[chat_channel] decorating reply: {}".format(reply))

        # reply的包装步骤
        if reply and reply.content:
            reply = self._decorate_reply(context, reply)
            self._quota_record_usage(context, reply)

            # reply的发送步骤
            self._persist_web_chat_turn(context, reply)
            self._send_reply(context, reply)
            self._report_turn_event(context, reply)

    def _quota_precheck(self, context: Context):
        try:
            from common.quota import QuotaManager, estimate_context_tokens, get_quota_manager, resolve_user_id
            if not QuotaManager.enabled():
                return None
            manager = get_quota_manager()
            user_id = resolve_user_id(context)
            channel_type = context.get("channel_type", "")
            estimated = max(
                estimate_context_tokens(context),
                int(conf().get("quota_min_request_tokens", 1000) or 1),
            )
            result = manager.check(
                user_id,
                estimated,
                channel_type=channel_type,
                display_name=context.get("display_name", ""),
            )
            if result.allowed:
                context["quota_user_id"] = result.user_id
                context["quota_input_estimate"] = estimated
                return None
            logger.info(f"[quota] blocked user={result.user_id}, remaining={result.remaining_tokens}, estimated={estimated}")
            return Reply(ReplyType.ERROR, result.message)
        except Exception as e:
            logger.error(f"[quota] precheck failed, allowing request: {e}", exc_info=True)
            return None

    def _quota_record_usage(self, context: Context, reply: Reply):
        try:
            from common.quota import QuotaManager, estimate_context_tokens, estimate_text_tokens, extract_reply_text, get_quota_manager, resolve_user_id
            if not QuotaManager.enabled():
                return
            input_tokens = int(context.get("quota_input_estimate", 0) or 0)
            if input_tokens <= 0:
                input_tokens = estimate_context_tokens(context)
            output_tokens = estimate_text_tokens(extract_reply_text(reply))
            min_tokens = int(conf().get("quota_min_request_tokens", 1000) or 1)
            total_tokens = max(min_tokens, input_tokens + output_tokens)
            user_id = context.get("quota_user_id") or resolve_user_id(context)
            get_quota_manager().record_usage(
                user_id=user_id,
                session_id=context.get("session_id", ""),
                channel_type=context.get("channel_type", ""),
                model=context.get("gpt_model") or conf().get("model", ""),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                reason="chat",
            )
        except Exception as e:
            logger.warning(f"[quota] record usage failed: {e}")

    def _handle_builtin_user_command(self, context: Context):
        if context.type != ContextType.TEXT:
            return None
        text = str(context.content or "").strip()
        if not text:
            return None
        lowered = text.lower()
        if not (lowered.startswith("/redeem") or lowered.startswith("兑换码")):
            return None
        if lowered.startswith("/redeem"):
            code = text[len("/redeem"):].strip()
        else:
            code = text[len("兑换码"):].strip()
            code = code.lstrip(":：").strip()
        if not code:
            return Reply(ReplyType.TEXT, "请发送：/redeem 你的兑换码")
        try:
            from common.quota import get_quota_manager
            result = get_quota_manager().redeem_code(
                code,
                context_user_key(context),
                channel_type=context.get("channel_type", ""),
                display_name=context.get("display_name", ""),
            )
            if result.get("status") == "success":
                user = result.get("user") or {}
                return Reply(
                    ReplyType.TEXT,
                    f"充值成功，已到账 {result.get('token_amount', 0)} Token。当前剩余额度：{user.get('remaining_tokens', 0)} Token。"
                )
            return Reply(ReplyType.TEXT, result.get("message", "兑换失败，请检查兑换码"))
        except Exception as e:
            logger.error(f"[quota] redeem command failed: {e}", exc_info=True)
            return Reply(ReplyType.TEXT, "兑换失败，请稍后再试")

    def _generate_reply(self, context: Context, reply: Reply = Reply()) -> Reply:
        e_context = PluginManager().emit_event(
            EventContext(
                Event.ON_HANDLE_CONTEXT,
                {"channel": self, "context": context, "reply": reply},
            )
        )
        reply = e_context["reply"]
        if not e_context.is_pass():
            logger.debug("[chat_channel] type={}, content={}".format(context.type, context.content))
            if context.type == ContextType.TEXT or context.type == ContextType.IMAGE_CREATE:  # 文字和图片消息
                context["channel"] = e_context["channel"]
                reply = super().build_reply_content(context.content, context)
            elif context.type == ContextType.VOICE:  # 语音消息
                cmsg = context["msg"]
                cmsg.prepare()
                file_path = context.content
                wav_path = os.path.splitext(file_path)[0] + ".wav"
                try:
                    any_to_wav(file_path, wav_path)
                except Exception as e:  # 转换失败，直接使用mp3，对于某些api，mp3也可以识别
                    logger.warning("[chat_channel]any to wav error, use raw path. " + str(e))
                    wav_path = file_path
                # 语音识别
                reply = super().build_voice_to_text(wav_path)
                # 删除临时文件
                try:
                    os.remove(file_path)
                    if wav_path != file_path:
                        os.remove(wav_path)
                except Exception as e:
                    pass
                    # logger.warning("[chat_channel]delete temp file error: " + str(e))

                if reply.type == ReplyType.TEXT:
                    new_context = self._compose_context(ContextType.TEXT, reply.content, **context.kwargs)
                    if new_context:
                        reply = self._generate_reply(new_context)
                    else:
                        return
            elif context.type == ContextType.IMAGE:  # 图片消息，当前仅做下载保存到本地的逻辑
                memory.USER_IMAGE_CACHE[context["session_id"]] = {
                    "path": context.content,
                    "msg": context.get("msg")
                }
            elif context.type == ContextType.SHARING:  # 分享信息，当前无默认逻辑
                pass
            elif context.type == ContextType.FUNCTION or context.type == ContextType.FILE:  # 文件消息及函数调用等，当前无默认逻辑
                pass
            else:
                logger.warning("[chat_channel] unknown context type: {}".format(context.type))
                return
        return reply

    def _decorate_reply(self, context: Context, reply: Reply) -> Reply:
        if reply and reply.type:
            e_context = PluginManager().emit_event(
                EventContext(
                    Event.ON_DECORATE_REPLY,
                    {"channel": self, "context": context, "reply": reply},
                )
            )
            reply = e_context["reply"]
            desire_rtype = context.get("desire_rtype")
            if not e_context.is_pass() and reply and reply.type:
                if reply.type in self.NOT_SUPPORT_REPLYTYPE:
                    logger.error("[chat_channel]reply type not support: " + str(reply.type))
                    reply.type = ReplyType.ERROR
                    reply.content = "不支持发送的消息类型: " + str(reply.type)

                if reply.type == ReplyType.TEXT:
                    reply_text = reply.content
                    if desire_rtype == ReplyType.VOICE and ReplyType.VOICE not in self.NOT_SUPPORT_REPLYTYPE:
                        speech_text = markdown_to_speech_text(reply.content)
                        original_text = reply.content
                        reply = super().build_text_to_voice(speech_text or reply.content)
                        if reply and reply.type == ReplyType.VOICE:
                            reply.text_content = original_text
                        return self._decorate_reply(context, reply)
                    if context.get("isgroup", False):
                        if not context.get("no_need_at", False):
                            reply_text = "@" + context["msg"].actual_user_nickname + "\n" + reply_text.strip()
                        reply_text = conf().get("group_chat_reply_prefix", "") + reply_text + conf().get("group_chat_reply_suffix", "")
                    else:
                        reply_text = conf().get("single_chat_reply_prefix", "") + reply_text + conf().get("single_chat_reply_suffix", "")
                    reply.content = reply_text
                elif reply.type == ReplyType.ERROR or reply.type == ReplyType.INFO:
                    reply.content = "[" + str(reply.type) + "]\n" + reply.content
                elif reply.type == ReplyType.IMAGE_URL or reply.type == ReplyType.VOICE or reply.type == ReplyType.IMAGE or reply.type == ReplyType.FILE or reply.type == ReplyType.VIDEO or reply.type == ReplyType.VIDEO_URL:
                    pass
                else:
                    logger.error("[chat_channel] unknown reply type: {}".format(reply.type))
                    return
            if desire_rtype and desire_rtype != reply.type and reply.type not in [ReplyType.ERROR, ReplyType.INFO]:
                logger.warning("[chat_channel] desire_rtype: {}, but reply type: {}".format(context.get("desire_rtype"), reply.type))
            return reply

    def _send_reply(self, context: Context, reply: Reply):
        if reply and reply.type:
            e_context = PluginManager().emit_event(
                EventContext(
                    Event.ON_SEND_REPLY,
                    {"channel": self, "context": context, "reply": reply},
                )
            )
            reply = e_context["reply"]
            if not e_context.is_pass() and reply and reply.type:
                logger.debug("[chat_channel] sending reply: {}, context: {}".format(reply, context))
                
                # 如果是文本回复，尝试提取并发送图片
                # Web channel renders images/videos inline via renderMarkdown,
                # so skip the extract-and-send step to avoid duplicate media.
                if reply.type == ReplyType.TEXT and context.get("channel_type") != "web":
                    self._extract_and_send_images(reply, context)
                elif reply.type == ReplyType.TEXT:
                    self._send(reply, context)
                # 如果是图片回复但带有文本内容，先发文本再发图片
                elif reply.type == ReplyType.IMAGE_URL and hasattr(reply, 'text_content') and reply.text_content:
                    # 先发送文本
                    text_reply = Reply(ReplyType.TEXT, reply.text_content)
                    self._send(text_reply, context)
                    # 短暂延迟后发送图片
                    time.sleep(0.3)
                    self._send(reply, context)
                else:
                    self._send(reply, context)
    
    def _extract_and_send_images(self, reply: Reply, context: Context):
        """
        从文本回复中提取图片/视频URL并单独发送
        支持格式：[图片: /path/to/image.png], [视频: /path/to/video.mp4], ![](url), <img src="url">
        最多发送5个媒体文件
        """
        content = reply.content
        media_items = []  # [(url, type), ...]
        
        # 正则提取各种格式的媒体URL
        patterns = [
            (r'\[图片:\s*([^\]]+)\]', 'image'),   # [图片: /path/to/image.png]
            (r'\[视频:\s*([^\]]+)\]', 'video'),   # [视频: /path/to/video.mp4]
            (r'!\[.*?\]\(([^\)]+)\)', 'image'),   # ![alt](url) - 默认图片
            (r'<img[^>]+src=["\']([^"\']+)["\']', 'image'),  # <img src="url">
            (r'<video[^>]+src=["\']([^"\']+)["\']', 'video'),  # <video src="url">
            (r'https?://[^\s]+\.(?:jpg|jpeg|png|gif|webp)', 'image'),  # 直接的图片URL
            (r'https?://[^\s]+\.(?:mp4|avi|mov|wmv|flv)', 'video'),  # 直接的视频URL
        ]
        
        for pattern, media_type in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                media_items.append((match, media_type))
        
        # 去重（保持顺序）并限制最多5个
        seen = set()
        unique_items = []
        for url, mtype in media_items:
            if url not in seen:
                seen.add(url)
                unique_items.append((url, mtype))
        media_items = unique_items[:5]
        
        if media_items:
            logger.info(f"[chat_channel] Extracted {len(media_items)} media item(s) from reply")
            
            # Send text first (the frontend will embed video players via renderMarkdown).
            logger.info(f"[chat_channel] Sending text content before media: {reply.content[:100]}...")
            self._send(reply, context)
            logger.info(f"[chat_channel] Text sent, now sending {len(media_items)} media item(s)")
            
            for i, (url, media_type) in enumerate(media_items):
                try:
                    # Determine whether it is a remote URL or a local file.
                    if url.startswith(('http://', 'https://')):
                        if media_type == 'video':
                            media_reply = Reply(ReplyType.FILE, url)
                            media_reply.file_name = os.path.basename(url)
                        else:
                            media_reply = Reply(ReplyType.IMAGE_URL, url)
                    elif os.path.exists(url):
                        if media_type == 'video':
                            media_reply = Reply(ReplyType.FILE, f"file://{url}")
                            media_reply.file_name = os.path.basename(url)
                        else:
                            media_reply = Reply(ReplyType.IMAGE_URL, f"file://{url}")
                    else:
                        logger.warning(f"[chat_channel] Media file not found or invalid URL: {url}")
                        continue
                    
                    if i > 0:
                        time.sleep(0.5)
                    self._send(media_reply, context)
                    logger.info(f"[chat_channel] Sent {media_type} {i+1}/{len(media_items)}: {url[:50]}...")
                    
                except Exception as e:
                    logger.error(f"[chat_channel] Failed to send {media_type} {url}: {e}")
        else:
            # 没有媒体文件，正常发送文本
                self._send(reply, context)

    def _send(self, reply: Reply, context: Context, retry_cnt=0):
        try:
            self.send(reply, context)
        except Exception as e:
            logger.error("[chat_channel] sendMsg error: {}".format(str(e)))
            if isinstance(e, NotImplementedError):
                return
            logger.exception(e)
            if retry_cnt < 2:
                time.sleep(3 + 3 * retry_cnt)
                self._send(reply, context, retry_cnt + 1)

    def _success_callback(self, session_id, **kwargs):  # 线程正常结束时的回调函数
        logger.debug("Worker return success, session_id = {}".format(session_id))

    def _fail_callback(self, session_id, exception, **kwargs):  # 线程异常结束时的回调函数
        logger.exception("Worker return exception: {}".format(exception))

    def _report_turn_event(self, context: Context, reply: Reply):
        """Report a completed user/assistant turn to the local bypass endpoint."""
        try:
            if not context or not reply:
                return
            if context.type not in [ContextType.TEXT, ContextType.IMAGE_CREATE, ContextType.VOICE]:
                return

            user_message = context.content or ""
            agent_response = getattr(reply, "agent_response", None)
            if agent_response is None:
                if hasattr(reply, "text_content") and reply.text_content:
                    agent_response = reply.text_content
                elif reply.type in [ReplyType.TEXT, ReplyType.INFO, ReplyType.ERROR, ReplyType.TEXT_]:
                    agent_response = reply.content or ""
                else:
                    agent_response = str(reply.content or "")

            report_turn_event(
                user_message=str(user_message),
                agent_response=str(agent_response),
                tool_events=getattr(reply, "tool_events", []),
                session_id=context.get("session_id", ""),
                user_id=context_user_key(context),
            )
        except Exception as e:
            logger.debug(f"[chat_channel] turn event report skipped: {e}")

    def _persist_web_chat_turn(self, context: Context, reply: Reply):
        """Persist non-agent Web chat turns so refresh can restore them."""
        try:
            if conf().get("agent", False):
                return
            if not conf().get("conversation_persistence", True):
                return
            if not context or not reply or context.get("channel_type") != "web":
                return
            if context.type not in [ContextType.TEXT, ContextType.IMAGE_CREATE, ContextType.VOICE]:
                return

            user_text = str(context.content or "").strip()
            if not user_text:
                return

            if reply.type in [ReplyType.TEXT, ReplyType.INFO, ReplyType.ERROR, ReplyType.TEXT_]:
                assistant_text = str(reply.content or "").strip()
            elif hasattr(reply, "text_content") and reply.text_content:
                assistant_text = str(reply.text_content).strip()
            else:
                assistant_text = str(reply.content or "").strip()

            if not assistant_text:
                return

            from agent.memory import get_conversation_store
            get_conversation_store().append_messages(
                context.get("session_id", ""),
                [
                    {"role": "user", "content": [{"type": "text", "text": user_text}]},
                    {"role": "assistant", "content": [{"type": "text", "text": assistant_text}]},
                ],
                channel_type="web",
            )
        except Exception as e:
            logger.warning(f"[chat_channel] failed to persist web chat turn: {e}")

    def _thread_pool_callback(self, session_id, **kwargs):
        def func(worker: Future):
            try:
                worker_exception = worker.exception()
                if worker_exception:
                    self._fail_callback(session_id, exception=worker_exception, **kwargs)
                else:
                    self._success_callback(session_id, **kwargs)
            except CancelledError as e:
                logger.info("Worker cancelled, session_id = {}".format(session_id))
            except Exception as e:
                logger.exception("Worker raise exception: {}".format(e))
            with self.lock:
                self.sessions[session_id][1].release()

        return func

    def produce(self, context: Context):
        session_id = context["session_id"]
        with self.lock:
            if session_id not in self.sessions:
                self.sessions[session_id] = [
                    Dequeue(),
                    threading.BoundedSemaphore(conf().get("concurrency_in_session", 1)),
                ]
            if context.type == ContextType.TEXT and context.content.startswith("#"):
                self.sessions[session_id][0].putleft(context)  # 优先处理管理命令
            else:
                self.sessions[session_id][0].put(context)

    # 消费者函数，单独线程，用于从消息队列中取出消息并处理
    def consume(self):
        while True:
            with self.lock:
                session_ids = list(self.sessions.keys())
            for session_id in session_ids:
                with self.lock:
                    context_queue, semaphore = self.sessions[session_id]
                if semaphore.acquire(blocking=False):  # 等线程处理完毕才能删除
                    if not context_queue.empty():
                        context = context_queue.get()
                        logger.debug("[chat_channel] consume context: {}".format(context))
                        future: Future = handler_pool.submit(self._handle, context)
                        future.add_done_callback(self._thread_pool_callback(session_id, context=context))
                        with self.lock:
                            if session_id not in self.futures:
                                self.futures[session_id] = []
                            self.futures[session_id].append(future)
                    elif semaphore._initial_value == semaphore._value + 1:  # 除了当前，没有任务再申请到信号量，说明所有任务都处理完毕
                        with self.lock:
                            self.futures[session_id] = [t for t in self.futures[session_id] if not t.done()]
                            assert len(self.futures[session_id]) == 0, "thread pool error"
                            del self.sessions[session_id]
                    else:
                        semaphore.release()
            time.sleep(0.2)

    # 取消session_id对应的所有任务，只能取消排队的消息和已提交线程池但未执行的任务
    def cancel_session(self, session_id):
        with self.lock:
            if session_id in self.sessions:
                for future in self.futures[session_id]:
                    future.cancel()
                cnt = self.sessions[session_id][0].qsize()
                if cnt > 0:
                    logger.info("Cancel {} messages in session {}".format(cnt, session_id))
                self.sessions[session_id][0] = Dequeue()

    def cancel_all_session(self):
        with self.lock:
            for session_id in self.sessions:
                for future in self.futures[session_id]:
                    future.cancel()
                cnt = self.sessions[session_id][0].qsize()
                if cnt > 0:
                    logger.info("Cancel {} messages in session {}".format(cnt, session_id))
                self.sessions[session_id][0] = Dequeue()


def check_prefix(content, prefix_list):
    if not prefix_list:
        return None
    for prefix in prefix_list:
        if content.startswith(prefix):
            return prefix
    return None


def check_contain(content, keyword_list):
    if not keyword_list:
        return None
    for ky in keyword_list:
        if content.find(ky) != -1:
            return True
    return None

