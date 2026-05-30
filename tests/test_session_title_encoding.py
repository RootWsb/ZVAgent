from agent.chat.session_service import _repair_mojibake


def test_repair_latin1_mojibake_title():
    garbled = "å å¯è´§å¸æ°é»"
    assert _repair_mojibake(garbled) == "加密货币新闻"


def test_repair_gbk_then_latin1_mojibake_title():
    garbled = "氓聤聽氓炉聠猫麓搂氓赂聛忙聳掳茅聴禄"
    assert _repair_mojibake(garbled) == "加密货币新闻"


def test_keep_normal_chinese_title():
    assert _repair_mojibake("今日天气") == "今日天气"
