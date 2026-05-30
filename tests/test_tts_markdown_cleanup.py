from channel.chat_channel import markdown_to_speech_text, should_reply_with_voice


def test_markdown_to_speech_text_removes_markdown_controls():
    source = """# **Title**

| 项目 | 说明 |
|---|---|
| **嘴型** | 张大 |

Please read **this sentence** and [open docs](https://example.com).

```python
print("do not read this")
```
"""

    cleaned = markdown_to_speech_text(source)

    assert "星号" not in cleaned
    assert "**" not in cleaned
    assert "|---|" not in cleaned
    assert "https://example.com" not in cleaned
    assert "print" not in cleaned
    assert "Title" in cleaned
    assert "this sentence" in cleaned
    assert "open docs" in cleaned


def test_should_reply_with_voice_requires_explicit_trigger():
    assert not should_reply_with_voice("今日热门 AI 技术文章")
    assert not should_reply_with_voice("帮我查询当日新闻")
    assert should_reply_with_voice("用语音回答这段内容")
    assert should_reply_with_voice("读一下：あいうえお")
    assert should_reply_with_voice("教我日语发音")
