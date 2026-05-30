import re
import time

import edge_tts
import asyncio

from bridge.reply import Reply, ReplyType
from common.log import logger
from common.tmp_dir import TmpDir
from config import conf
from voice.voice import Voice


class EdgeVoice(Voice):

    def __init__(self):
        '''
        # 普通话
        zh-CN-XiaoxiaoNeural
        zh-CN-XiaoyiNeural
        zh-CN-YunjianNeural
        zh-CN-YunxiNeural
        zh-CN-YunxiaNeural
        zh-CN-YunyangNeural
        # 地方口音
        zh-CN-liaoning-XiaobeiNeural
        zh-CN-shaanxi-XiaoniNeural
        # 粤语
        zh-HK-HiuGaaiNeural
        zh-HK-HiuMaanNeural
        zh-HK-WanLungNeural
        # 湾湾腔
        zh-TW-HsiaoChenNeural
        zh-TW-HsiaoYuNeural
        zh-TW-YunJheNeural
        '''
        self.voice = conf().get("tts_voice_id") or ""
        self.rate = conf().get("tts_rate") or "-30%"
        self.volume = conf().get("tts_volume") or "+0%"
        self.pitch = conf().get("tts_pitch") or "+0Hz"

    @staticmethod
    def _detect_voice(text: str) -> str:
        if re.search(r"[\u3040-\u30ff]", text):
            return "ja-JP-NanamiNeural"
        if re.search(r"[\uac00-\ud7af]", text):
            return "ko-KR-SunHiNeural"
        if re.search(r"[A-Za-z]", text) and not re.search(r"[\u4e00-\u9fff]", text):
            return "en-US-AriaNeural"
        return "zh-CN-YunjianNeural"

    def voiceToText(self, voice_file):
        pass

    async def gen_voice(self, text, fileName):
        voice = self.voice or self._detect_voice(text)
        communicate = edge_tts.Communicate(
            text,
            voice,
            rate=self.rate,
            volume=self.volume,
            pitch=self.pitch,
        )
        await communicate.save(fileName)
        return voice

    def textToVoice(self, text):
        fileName = TmpDir().path() + "reply-" + str(int(time.time())) + "-" + str(hash(text) & 0x7FFFFFFF) + ".mp3"

        voice = asyncio.run(self.gen_voice(text, fileName))

        logger.info(
            "[EdgeTTS] textToVoice voice={} rate={} pitch={} text={} voice file name={}".format(
                voice,
                self.rate,
                self.pitch,
                text,
                fileName,
            )
        )
        return Reply(ReplyType.VOICE, fileName)
