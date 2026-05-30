"""
Agent Event Handler - Handles agent events and thinking process output
"""

import json

from common.log import logger
from common.user_identity import context_user_key


class AgentEventHandler:
    """
    Handles agent events and optionally sends intermediate messages to channel
    """

    def __init__(self, context=None, original_callback=None, user_message=""):
        """
        Initialize event handler

        Args:
            context: COW context (for accessing channel)
            original_callback: Original event callback to chain
            user_message: The original user query (for event reporting)
        """
        self.context = context
        self.original_callback = original_callback
        self.user_message = user_message

        # Get channel for sending intermediate messages
        self.channel = None
        if context:
            self.channel = context.kwargs.get("channel") if hasattr(context, "kwargs") else None

        self.current_content = ""
        self.turn_number = 0

        # Collect tool execution events for turn reporting
        self._tool_events = []
        self._active_tool_events = {}
    
    def handle_event(self, event):
        """
        Main event handler
        
        Args:
            event: Event dict with type and data
        """
        event_type = event.get("type")
        data = event.get("data", {})
        
        # Dispatch to specific handlers
        if event_type == "turn_start":
            self._handle_turn_start(data)
        elif event_type == "message_update":
            self._handle_message_update(data)
        elif event_type == "message_end":
            self._handle_message_end(data)
        elif event_type == "reasoning_update":
            pass
        elif event_type == "tool_execution_start":
            self._handle_tool_execution_start(data)
        elif event_type == "tool_execution_end":
            self._handle_tool_execution_end(data)
        
        # Call original callback if provided
        if self.original_callback:
            self.original_callback(event)
    
    def _handle_turn_start(self, data):
        """Handle turn start event"""
        self.turn_number = data.get("turn", 0)
        self.current_content = ""
    
    def _handle_message_update(self, data):
        """Handle message update event (streaming content text)"""
        delta = data.get("delta", "")
        self.current_content += delta
    
    def _handle_message_end(self, data):
        """Handle message end event"""
        tool_calls = data.get("tool_calls", [])
        
        if tool_calls:
            if self.current_content.strip():
                logger.info(f"💭 {self.current_content.strip()[:200]}{'...' if len(self.current_content) > 200 else ''}")
                self._send_to_channel(self.current_content.strip())
        else:
            if self.current_content.strip():
                logger.debug(f"💬 {self.current_content.strip()[:200]}{'...' if len(self.current_content) > 200 else ''}")
        
        self.current_content = ""
    
    def _handle_tool_execution_start(self, data):
        """Capture tool execution start for turn reporting."""
        tool_call_id = data.get("tool_call_id", "")
        event = {
            "tool_call_id": tool_call_id,
            "tool_name": data.get("tool_name", ""),
            "arguments": self._safe_json_value(data.get("arguments", {})),
        }
        if tool_call_id:
            self._active_tool_events[tool_call_id] = event
        else:
            self._tool_events.append(event)
    
    def _handle_tool_execution_end(self, data):
        """Capture tool execution result for turn reporting."""
        tool_call_id = data.get("tool_call_id", "")
        event = self._active_tool_events.pop(tool_call_id, {}) if tool_call_id else {}
        event.update({
            "tool_call_id": tool_call_id,
            "tool_name": data.get("tool_name", event.get("tool_name", "")),
            "status": data.get("status", ""),
            "result": self._safe_json_value(data.get("result", "")),
            "execution_time": data.get("execution_time", 0),
        })
        self._tool_events.append(event)
        self._record_skill_usage(event)

    def get_tool_events(self):
        """Return captured tool events, including any incomplete starts."""
        return self._tool_events + list(self._active_tool_events.values())

    def _record_skill_usage(self, event):
        try:
            from common.quota import get_quota_manager
            get_quota_manager().record_skill_usage(
                user_id=context_user_key(self.context),
                session_id=self.context.get("session_id", "") if self.context else "",
                channel_type=self.context.get("channel_type", "") if self.context else "",
                tool_name=event.get("tool_name", ""),
                status=event.get("status", ""),
                arguments=event.get("arguments", {}),
                result=event.get("result", ""),
                execution_time=event.get("execution_time", 0),
                user_message=self.user_message,
            )
        except Exception as e:
            logger.debug(f"[AgentEventHandler] skill usage record skipped: {e}")

    @staticmethod
    def _safe_json_value(value, max_chars=4000):
        """Keep tool payloads JSON-serializable and bounded."""
        try:
            json.dumps(value, ensure_ascii=False)
            safe_value = value
        except Exception:
            safe_value = AgentEventHandler._to_jsonable(value)

        try:
            serialized = json.dumps(safe_value, ensure_ascii=False)
        except Exception:
            serialized = str(safe_value)

        if len(serialized) > max_chars:
            return serialized[:max_chars] + "...[truncated]"
        return safe_value

    @staticmethod
    def _to_jsonable(value):
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, (list, tuple)):
            return [AgentEventHandler._to_jsonable(item) for item in value]
        if isinstance(value, dict):
            return {
                str(key): AgentEventHandler._to_jsonable(item)
                for key, item in value.items()
            }
        return str(value)
    
    def _send_to_channel(self, message):
        """
        Try to send intermediate message to channel.
        Skipped in SSE mode because thinking text is already streamed via on_event.
        """
        if self.context and self.context.get("on_event"):
            return

        if self.channel:
            try:
                from bridge.reply import Reply, ReplyType
                reply = Reply(ReplyType.TEXT, message)
                self.channel._send(reply, self.context)
            except Exception as e:
                logger.debug(f"[AgentEventHandler] Failed to send to channel: {e}")
    
    def log_summary(self):
        """Log execution summary - simplified"""
        # Summary removed as per user request
        # Real-time logging during execution is sufficient
        pass
