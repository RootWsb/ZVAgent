"""
Memory search tool

Allows agents to search their memory using semantic and keyword search
"""

from typing import Dict, Any, Optional
from agent.tools.base_tool import BaseTool


class MemorySearchTool(BaseTool):
    """Tool for searching agent memory"""
    
    name: str = "memory_search"
    description: str = (
        "Search agent's long-term memory using semantic and keyword search. "
        "Use this to recall past conversations, preferences, and knowledge."
    )
    params: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query (can be natural language question or keywords)"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 10)",
                "default": 10
            },
            "min_score": {
                "type": "number",
                "description": "Minimum relevance score (0-1, default: 0.1)",
                "default": 0.1
            },
            "layers": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["classic", "episodic", "profile"]
                },
                "description": "Optional memory layers to search. Defaults to all available layers."
            }
        },
        "required": ["query"]
    }
    
    def __init__(self, memory_manager, user_id: Optional[str] = None):
        """
        Initialize memory search tool
        
        Args:
            memory_manager: MemoryManager instance
            user_id: Optional user ID for scoped search
        """
        super().__init__()
        self.memory_manager = memory_manager
        self.user_id = user_id

        from config import conf
        if conf().get("knowledge", True):
            self.description = (
                "Search agent's long-term memory and knowledge base using semantic and keyword search. "
                "Use this to recall past conversations, preferences, and knowledge pages."
            )
    
    def execute(self, args: dict):
        """
        Execute memory search
        
        Args:
            args: Dictionary with query, max_results, min_score
            
        Returns:
            ToolResult with formatted search results
        """
        from agent.tools.base_tool import ToolResult
        import asyncio
        
        query = args.get("query")
        max_results = args.get("max_results", 10)
        min_score = args.get("min_score", 0.1)
        layers = args.get("layers") or ["classic", "episodic", "profile"]
        
        if not query:
            return ToolResult.fail("Error: query parameter is required")
        
        try:
            # Run async search in sync context
            results = []
            if "classic" in layers:
                results = asyncio.run(self.memory_manager.search(
                    query=query,
                    user_id=self.user_id,
                    max_results=max_results,
                    min_score=min_score,
                    include_shared=True
                ))

            layered_results = {}
            layered_memory = getattr(self.memory_manager, "layered_memory", None)
            if layered_memory:
                layered_layers = [layer for layer in layers if layer in ("episodic", "profile")]
                if layered_layers:
                    layered_results = layered_memory.search(
                        query=query,
                        layers=layered_layers,
                        limit=max_results,
                    )
            
            if not results and not self._has_layered_results(layered_results):
                # Return clear message that no memories exist yet
                # This prevents infinite retry loops
                return ToolResult.success(
                    f"No memories found for '{query}'. "
                    f"This is normal if no memories have been stored yet. "
                    f"You can store new memories by writing to MEMORY.md or memory/YYYY-MM-DD.md files."
                )
            
            # Format results
            output = [f"Found {len(results)} relevant indexed memories:\n"]

            for i, result in enumerate(results, 1):
                output.append(f"\n{i}. {result.path} (lines {result.start_line}-{result.end_line})")
                output.append(f"   Score: {result.score:.3f}")
                output.append(f"   Snippet: {result.snippet}")

            layered_section = self._format_layered_results(layered_results)
            if layered_section:
                output.append(layered_section)

            # Append knowledge graph context if available
            graph_section = self._get_graph_context(query)
            if graph_section:
                output.append("\n--- 知识图谱关联 ---")
                output.append(graph_section)

            return ToolResult.success("\n".join(output))
            
        except Exception as e:
            return ToolResult.fail(f"Error searching memory: {str(e)}")

    @staticmethod
    def _has_layered_results(layered_results: dict) -> bool:
        return any(bool(values) for values in (layered_results or {}).values())

    @staticmethod
    def _format_layered_results(layered_results: dict) -> str:
        if not layered_results:
            return ""

        output = []
        episodic = layered_results.get("episodic") or []
        if episodic:
            output.append("\n--- Episodic Memory ---")
            for i, record in enumerate(episodic, 1):
                output.append(
                    f"{i}. {record.summary} "
                    f"(importance={record.importance:.2f}, targets={','.join(record.candidate_targets) or 'none'})"
                )

        profile = layered_results.get("profile") or []
        if profile:
            output.append("\n--- Profile Memory ---")
            for i, item in enumerate(profile, 1):
                value = item.get("value") or item.get("key") or str(item)
                section = item.get("_section", "profile")
                confidence = item.get("confidence")
                confidence_text = f", confidence={confidence:.2f}" if isinstance(confidence, (int, float)) else ""
                output.append(f"{i}. [{section}] {value}{confidence_text}")

        return "\n".join(output)

    def _get_graph_context(self, query: str) -> str:
        """Get knowledge graph context for a query, if graph is available."""
        graph = getattr(self.memory_manager, "knowledge_graph", None)
        if not graph:
            return ""

        try:
            triples = graph.search_triples(query, limit=10)
            if not triples:
                return ""
            lines = []
            for t in triples:
                lines.append(f"  {t['subject']} → {t['predicate']} → {t['object']}")
            return "\n".join(lines)
        except Exception:
            return ""
