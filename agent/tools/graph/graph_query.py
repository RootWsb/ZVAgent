"""
Graph Query Tool — Direct access to the knowledge graph for structured relationship exploration.
"""

from typing import Any, Optional
from agent.tools.base_tool import BaseTool


class GraphQueryTool(BaseTool):
    """Tool for directly querying the knowledge graph."""

    name: str = "graph_query"
    description: str = (
        "Query the knowledge graph for entity relationships. "
        "Find what is related to an entity, trace relationship chains, "
        "search for facts, or view graph statistics. "
        "Use memory_search for general semantic queries; "
        "this tool is for structured relationship exploration."
    )
    params: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["related", "search", "entity_info", "stats", "add"],
                "description": (
                    "Query action: "
                    "'related' — find entities connected to an entity; "
                    "'search' — full-text search across all triples; "
                    "'entity_info' — detailed info about an entity and its relationships; "
                    "'stats' — graph statistics; "
                    "'add' — manually add a triple"
                ),
            },
            "entity": {
                "type": "string",
                "description": "Entity name (required for related / entity_info)",
            },
            "query": {
                "type": "string",
                "description": "Search query text (required for search / add)",
            },
            "predicate": {
                "type": "string",
                "description": "Relationship predicate (required for add)",
            },
            "object": {
                "type": "string",
                "description": "Object entity (required for add)",
            },
            "max_depth": {
                "type": "integer",
                "description": "Max traversal depth for 'related' (default: 2)",
                "default": 2,
            },
        },
        "required": ["action"],
    }

    def __init__(self, knowledge_graph: Any = None):
        super().__init__()
        self.knowledge_graph = knowledge_graph

    def execute(self, args: dict):
        from agent.tools.base_tool import ToolResult

        if not self.knowledge_graph:
            return ToolResult.fail("Knowledge graph is not available")

        action = args.get("action", "")
        try:
            if action == "related":
                return self._do_related(args)
            elif action == "search":
                return self._do_search(args)
            elif action == "entity_info":
                return self._do_entity_info(args)
            elif action == "stats":
                return self._do_stats()
            elif action == "add":
                return self._do_add(args)
            else:
                return ToolResult.fail(f"Unknown action: {action}")
        except Exception as e:
            return ToolResult.fail(f"Graph query error: {e}")

    def _do_related(self, args: dict) -> "ToolResult":
        from agent.tools.base_tool import ToolResult

        entity = args.get("entity")
        if not entity:
            return ToolResult.fail("'entity' parameter is required for 'related' action")

        max_depth = args.get("max_depth", 2)
        related = self.knowledge_graph.find_related(entity, max_depth=max_depth)

        if not related:
            return ToolResult.success(f"No relationships found for '{entity}'")

        output = [f"Related to '{entity}' ({len(related)} nodes):\n"]
        for r in related:
            node = r["node"]
            if node == entity:
                continue
            # Show direct triples for this node
            triples = self.knowledge_graph.query_subject(node)
            if triples:
                for t in triples:
                    output.append(f"  {t['subject']} → {t['predicate']} → {t['object']}")
            else:
                triples = self.knowledge_graph.query_object(node)
                for t in triples:
                    output.append(f"  {t['subject']} → {t['predicate']} → {t['object']}")

        return ToolResult.success("\n".join(output))

    def _do_search(self, args: dict) -> "ToolResult":
        from agent.tools.base_tool import ToolResult

        query = args.get("query")
        if not query:
            return ToolResult.fail("'query' parameter is required for 'search' action")

        results = self.knowledge_graph.search_triples(query, limit=20)
        if not results:
            return ToolResult.success(f"No triples found matching '{query}'")

        output = [f"Found {len(results)} triples matching '{query}':\n"]
        for t in results:
            output.append(f"  {t['subject']} → {t['predicate']} → {t['object']}")

        return ToolResult.success("\n".join(output))

    def _do_entity_info(self, args: dict) -> "ToolResult":
        from agent.tools.base_tool import ToolResult

        entity = args.get("entity")
        if not entity:
            return ToolResult.fail("'entity' parameter is required for 'entity_info' action")

        context = self.knowledge_graph.get_context_for_entity(entity, max_hops=2)
        if not context:
            # Try case-insensitive lookup
            ent = self.knowledge_graph.get_entity(entity)
            if ent:
                context = f"Entity: {ent['name']}"
                if ent.get("entity_type"):
                    context += f"\nType: {ent['entity_type']}"
            else:
                return ToolResult.success(f"Entity '{entity}' not found in the knowledge graph")

        return ToolResult.success(f"Entity: {entity}\n\n{context}")

    def _do_stats(self) -> "ToolResult":
        from agent.tools.base_tool import ToolResult

        stats = self.knowledge_graph.get_stats()
        output = [
            "Knowledge Graph Statistics:",
            f"  Triples: {stats['triples']}",
            f"  Entities: {stats['entities']}",
            f"  NetworkX: {'available' if stats['networkx'] else 'not installed (SQL fallback)'}",
        ]
        if stats.get("sources"):
            output.append("  Sources:")
            for src, cnt in stats["sources"].items():
                output.append(f"    {src}: {cnt}")

        return ToolResult.success("\n".join(output))

    def _do_add(self, args: dict) -> "ToolResult":
        from agent.tools.base_tool import ToolResult

        subject = args.get("entity") or args.get("subject", "")
        predicate = args.get("predicate", "")
        obj = args.get("object", "")

        if not subject or not predicate or not obj:
            return ToolResult.fail("'entity/subject', 'predicate', and 'object' are all required for 'add'")

        triple_id = self.knowledge_graph.add_triple(
            subject=subject,
            predicate=predicate,
            obj=obj,
            source="conversation",
            source_path="manual",
        )
        if triple_id:
            return ToolResult.success(f"Added triple: {subject} → {predicate} → {obj} (id={triple_id})")
        else:
            return ToolResult.fail("Failed to add triple (may already exist)")
