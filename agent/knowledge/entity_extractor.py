"""
Entity Extractor — LLM-based entity and triple extraction for the knowledge graph.

Extracts structured Subject-Predicate-Object triples from text using an LLM,
then feeds them into the KnowledgeGraph store.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from common.log import logger

# Reuse the existing chunker for large texts
from agent.memory.chunker import TextChunker

EXTRACTION_SYSTEM_PROMPT = """你是一个知识图谱提取助手。从给定文本中提取实体和关系三元组。

## 提取规则

1. 实体类型: person(人物), concept(概念), tool(工具), project(项目), org(组织), event(事件), technology(技术), metric(指标)
2. 关系谓词用简短中文描述，如"属于"、"开发"、"使用"、"位于"、"创建于"、"依赖"、"版本"、"架构"等
3. 实体名称保持原文，不翻译不缩写
4. 每个三元组一个 (主语, 谓词, 宾语) 元组
5. 只提取文本中明确陈述的事实，不推断、不猜测
6. 实体归一化: 同一实体使用统一名称（如 "OpenAI" 和 "openai" 统一为 "OpenAI"）
7. 控制数量: 最多提取 15 个三元组，优先提取最重要的事实

## 输出格式

严格按JSON输出，不要添加其他文字:
{
  "entities": [
    {"name": "实体名", "type": "entity_type"}
  ],
  "triples": [
    {"subject": "主语", "predicate": "谓词", "object": "宾语"}
  ]
}

如果文本中没有可提取的知识，输出:
{"entities": [], "triples": []}"""


class EntityExtractor:
    """Extracts entities and triples from text using LLM."""

    def __init__(self, llm_model: Any = None):
        """
        Args:
            llm_model: LLMModel instance for extraction calls.
                        If None, extraction will return empty results.
        """
        self.llm_model = llm_model
        self._chunker = TextChunker(max_tokens=500, overlap_tokens=50)

    def extract_from_text(
        self,
        text: str,
        source: Optional[str] = None,
        source_path: Optional[str] = None,
    ) -> List[Dict]:
        """
        Extract entities and triples from text.

        Args:
            text: Input text (may be long — auto-chunked if needed).
            source: Provenance label ("memory", "knowledge", "conversation").
            source_path: File path or session id.

        Returns:
            List of triple dicts: [{"subject": ..., "predicate": ..., "object": ...}, ...]
        """
        if not self.llm_model or not text or not text.strip():
            return []

        # Chunk large texts
        chunks = self._chunker.chunk_text(text)
        if not chunks:
            return []

        all_triples = []
        all_entities = []

        for chunk in chunks:
            chunk_text = chunk.text.strip()
            if len(chunk_text) < 20:
                continue
            result = self._call_llm(chunk_text)
            if result:
                all_triples.extend(result.get("triples", []))
                all_entities.extend(result.get("entities", []))

        # Dedup triples
        seen = set()
        deduped = []
        for t in all_triples:
            key = (t.get("subject", "").strip().lower(),
                   t.get("predicate", "").strip().lower(),
                   t.get("object", "").strip().lower())
            if key not in seen:
                seen.add(key)
                deduped.append(t)

        if deduped:
            logger.info(
                f"[EntityExtractor] Extracted {len(deduped)} triples, "
                f"{len(all_entities)} entities from {source_path or 'text'}"
            )

        return deduped

    def _call_llm(self, text: str) -> Optional[Dict]:
        """Call LLM with extraction prompt, parse JSON response."""
        try:
            response = self.llm_model.call_with_tools(
                messages=[{"role": "user", "content": text}],
                system=EXTRACTION_SYSTEM_PROMPT,
                max_tokens=2000,
            )

            # Extract text content from response
            raw = ""
            if isinstance(response, dict):
                content = response.get("content", "")
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            raw += block.get("text", "")
                elif isinstance(content, str):
                    raw = content
            elif isinstance(response, str):
                raw = response

            return self._parse_json(raw)

        except Exception as e:
            logger.debug(f"[EntityExtractor] LLM call failed: {e}")
            return None

    @staticmethod
    def _parse_json(raw: str) -> Optional[Dict]:
        """Parse LLM JSON response, handling common formatting issues."""
        if not raw:
            return None

        # Strip markdown code fences
        raw = raw.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        try:
            result = json.loads(raw)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

        # Try to find JSON object in the response
        match = re.search(r"\{[\s\S]*\}", raw)
        if match:
            try:
                result = json.loads(match.group())
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                pass

        return None
