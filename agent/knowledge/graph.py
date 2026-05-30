"""
Knowledge Graph — SQLite-backed triple store with optional NetworkX traversal.

Stores Subject-Predicate-Object triples extracted from memories and knowledge
pages.  The graph is queried by the memory_search tool to augment search
results with structured relationship context.
"""

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common.log import logger

# Optional NetworkX import — graceful degradation if not installed
try:
    import networkx as nx
    _HAS_NETWORKX = True
except ImportError:
    _HAS_NETWORKX = False


class KnowledgeGraph:
    """SQLite-backed knowledge graph with optional NetworkX in-memory traversal."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path.home() / "zvagent" / "memory" / "long-term" / "graph.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self._db_path = db_path
        self._local = threading.local()
        self._init_schema()

        # NetworkX cache (invalidated on every write)
        self._nx_graph = None
        self._graph_generation = 0
        self._write_generation = 0

    # ------------------------------------------------------------------
    # Connection helpers (thread-safe via threading.local)
    # ------------------------------------------------------------------

    def _get_conn(self) -> sqlite3.Connection:
        conn = getattr(self._local, "conn", None)
        if conn is None or self._db_path != getattr(self._local, "db_path", None):
            conn = sqlite3.connect(
                str(self._db_path),
                check_same_thread=False,
                timeout=10,
            )
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=5000")
            self._local.conn = conn
            self._local.db_path = self._db_path
        return conn

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _init_schema(self):
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS triples (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                subject     TEXT NOT NULL,
                predicate   TEXT NOT NULL,
                object      TEXT NOT NULL,
                source      TEXT,
                source_path TEXT,
                confidence  REAL DEFAULT 1.0,
                is_active   INTEGER DEFAULT 1,
                created_at  INTEGER DEFAULT (strftime('%s','now')),
                updated_at  INTEGER DEFAULT (strftime('%s','now'))
            );

            CREATE TABLE IF NOT EXISTS entities (
                name        TEXT PRIMARY KEY,
                entity_type TEXT,
                aliases     TEXT,
                metadata    TEXT,
                created_at  INTEGER DEFAULT (strftime('%s','now'))
            );

            CREATE INDEX IF NOT EXISTS idx_triples_subject ON triples(subject);
            CREATE INDEX IF NOT EXISTS idx_triples_object  ON triples(object);
            CREATE INDEX IF NOT EXISTS idx_triples_predicate ON triples(predicate);
            CREATE INDEX IF NOT EXISTS idx_triples_source ON triples(source, source_path);
            CREATE INDEX IF NOT EXISTS idx_triples_active ON triples(is_active, subject, object);
            CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
        """)

        # FTS5 (may fail on older SQLite — degrade gracefully)
        try:
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS triples_fts USING fts5(
                    subject, predicate, object,
                    id UNINDEXED, source UNINDEXED, source_path UNINDEXED,
                    content='triples', content_rowid='id'
                )
            """)
            # Triggers for auto-sync
            for sql in [
                """CREATE TRIGGER IF NOT EXISTS triples_ai AFTER INSERT ON triples BEGIN
                    INSERT INTO triples_fts(rowid, subject, predicate, object)
                    VALUES (new.id, new.subject, new.predicate, new.object);
                END""",
                """CREATE TRIGGER IF NOT EXISTS triples_ad AFTER DELETE ON triples BEGIN
                    DELETE FROM triples_fts WHERE rowid = old.id;
                END""",
                """CREATE TRIGGER IF NOT EXISTS triples_au AFTER UPDATE ON triples BEGIN
                    DELETE FROM triples_fts WHERE rowid = old.id;
                    INSERT INTO triples_fts(rowid, subject, predicate, object)
                    VALUES (new.id, new.subject, new.predicate, new.object);
                END""",
            ]:
                conn.execute(sql)
        except Exception as e:
            logger.warning(f"[KnowledgeGraph] FTS5 init failed (degraded mode): {e}")

        conn.commit()

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def add_triple(
        self,
        subject: str,
        predicate: str,
        obj: str,
        source: Optional[str] = None,
        source_path: Optional[str] = None,
        confidence: float = 1.0,
    ) -> int:
        """Insert a single triple.  Returns the row id."""
        subject = subject.strip()
        predicate = predicate.strip()
        obj = obj.strip()
        if not subject or not predicate or not obj:
            return 0

        conn = self._get_conn()
        try:
            cursor = conn.execute(
                """INSERT OR IGNORE INTO triples
                   (subject, predicate, object, source, source_path, confidence)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (subject, predicate, obj, source, source_path, confidence),
            )
            if cursor.rowcount > 0:
                self._invalidate_graph()
                return cursor.lastrowid
            return 0
        except Exception as e:
            logger.warning(f"[KnowledgeGraph] add_triple failed: {e}")
            return 0

    def add_triples_batch(
        self,
        triples: List[Dict],
        source: Optional[str] = None,
        source_path: Optional[str] = None,
    ) -> int:
        """Batch insert triples.  Returns count of newly inserted triples."""
        if not triples:
            return 0

        conn = self._get_conn()
        count = 0
        try:
            for t in triples:
                s = str(t.get("subject", "")).strip()
                p = str(t.get("predicate", "")).strip()
                o = str(t.get("object", "")).strip()
                if not s or not p or not o:
                    continue
                cursor = conn.execute(
                    """INSERT OR IGNORE INTO triples
                       (subject, predicate, object, source, source_path)
                       VALUES (?, ?, ?, ?, ?)""",
                    (s, p, o, source, source_path),
                )
                if cursor.rowcount > 0:
                    count += 1
            conn.commit()
            if count > 0:
                self._invalidate_graph()
                logger.info(f"[KnowledgeGraph] Inserted {count} triples (source={source}, path={source_path})")
            return count
        except Exception as e:
            logger.warning(f"[KnowledgeGraph] add_triples_batch failed: {e}")
            return count

    def upsert_entity(
        self,
        name: str,
        entity_type: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ):
        """Create or update an entity record."""
        conn = self._get_conn()
        try:
            aliases_json = json.dumps(aliases or [], ensure_ascii=False)
            meta_json = json.dumps(metadata or {}, ensure_ascii=False)
            conn.execute(
                """INSERT INTO entities (name, entity_type, aliases, metadata)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(name) DO UPDATE SET
                     entity_type = COALESCE(excluded.entity_type, entities.entity_type),
                     aliases = CASE
                       WHEN excluded.aliases != '[]' THEN excluded.aliases
                       ELSE entities.aliases
                     END,
                     metadata = CASE
                       WHEN excluded.metadata != '{}' THEN excluded.metadata
                       ELSE entities.metadata
                     END""",
                (name, entity_type, aliases_json, meta_json),
            )
            conn.commit()
        except Exception as e:
            logger.warning(f"[KnowledgeGraph] upsert_entity failed: {e}")

    def deactivate_source_triples(self, source_path: str):
        """Soft-delete all triples from a given source path."""
        conn = self._get_conn()
        try:
            # Deactivate triples in the main table
            conn.execute(
                "UPDATE triples SET is_active = 0, updated_at = strftime('%s','now') WHERE source_path = ?",
                (source_path,),
            )
            # Also remove from FTS index
            try:
                conn.execute(
                    "DELETE FROM triples_fts WHERE rowid IN "
                    "(SELECT id FROM triples WHERE source_path = ?)",
                    (source_path,),
                )
            except Exception:
                pass  # FTS may not exist
            conn.commit()
            self._invalidate_graph()
            logger.info(f"[KnowledgeGraph] Deactivated triples for source_path={source_path}")
        except Exception as e:
            logger.warning(f"[KnowledgeGraph] deactivate_source_triples failed: {e}")

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def query_subject(self, subject: str, predicate: Optional[str] = None) -> List[Dict]:
        """Find all active triples where subject matches."""
        conn = self._get_conn()
        if predicate:
            rows = conn.execute(
                "SELECT id, subject, predicate, object, confidence FROM triples "
                "WHERE is_active = 1 AND subject = ? AND predicate = ?",
                (subject, predicate),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, subject, predicate, object, confidence FROM triples "
                "WHERE is_active = 1 AND subject = ?",
                (subject,),
            ).fetchall()
        return [dict(r) for r in rows]

    def query_object(self, obj: str, predicate: Optional[str] = None) -> List[Dict]:
        """Find all active triples where object matches."""
        conn = self._get_conn()
        if predicate:
            rows = conn.execute(
                "SELECT id, subject, predicate, object, confidence FROM triples "
                "WHERE is_active = 1 AND object = ? AND predicate = ?",
                (obj, predicate),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, subject, predicate, object, confidence FROM triples "
                "WHERE is_active = 1 AND object = ?",
                (obj,),
            ).fetchall()
        return [dict(r) for r in rows]

    def search_triples(self, query: str, limit: int = 20) -> List[Dict]:
        """Full-text search across all triples using FTS5 (or LIKE fallback)."""
        conn = self._get_conn()
        results = []

        # Try FTS5 first
        try:
            fts_query = self._build_fts_query(query)
            if fts_query:
                rows = conn.execute(
                    "SELECT t.id, t.subject, t.predicate, t.object, t.confidence "
                    "FROM triples_fts f "
                    "JOIN triples t ON t.id = f.rowid "
                    "WHERE triples_fts MATCH ? AND t.is_active = 1 "
                    "ORDER BY rank LIMIT ?",
                    (fts_query, limit),
                ).fetchall()
                results = [dict(r) for r in rows]
        except Exception:
            pass

        # Fallback: LIKE search for CJK or when FTS returns nothing
        if not results:
            like_pattern = f"%{query}%"
            rows = conn.execute(
                "SELECT id, subject, predicate, object, confidence FROM triples "
                "WHERE is_active = 1 "
                "AND (subject LIKE ? OR predicate LIKE ? OR object LIKE ?) "
                "LIMIT ?",
                (like_pattern, like_pattern, like_pattern, limit),
            ).fetchall()
            results = [dict(r) for r in rows]

        return results

    def find_related(self, entity: str, max_depth: int = 2) -> List[Dict]:
        """Find related entities up to max_depth hops."""
        if _HAS_NETWORKX:
            result = self._find_related_nx(entity, max_depth)
            if result is not None:
                return result
        return self._find_related_sql(entity, max_depth)

    def get_context_for_entity(self, entity: str, max_hops: int = 1) -> str:
        """Generate a text summary of what we know about an entity."""
        out = []

        # Direct relationships as subject
        for t in self.query_subject(entity):
            out.append(f"{t['subject']} → {t['predicate']} → {t['object']}")

        # Direct relationships as object
        for t in self.query_object(entity):
            out.append(f"{t['subject']} → {t['predicate']} → {t['object']}")

        # Entity metadata
        ent = self._get_entity(entity)
        if ent and ent.get("entity_type"):
            out.append(f"[类型: {ent['entity_type']}]")

        if max_hops > 1:
            related = self.find_related(entity, max_depth=max_depth)
            for r in related:
                if r["node"] != entity:
                    for t in self.query_subject(r["node"]):
                        line = f"{t['subject']} → {t['predicate']} → {t['object']}"
                        if line not in out:
                            out.append(line)

        return "\n".join(out) if out else ""

    def get_entity(self, name: str) -> Optional[Dict]:
        """Get entity info."""
        return self._get_entity(name)

    def get_stats(self) -> Dict:
        """Return graph statistics."""
        conn = self._get_conn()
        try:
            triple_count = conn.execute(
                "SELECT COUNT(*) FROM triples WHERE is_active = 1"
            ).fetchone()[0]
            entity_count = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
            source_counts = {}
            for row in conn.execute(
                "SELECT source, COUNT(*) as cnt FROM triples WHERE is_active = 1 GROUP BY source"
            ):
                source_counts[row["source"] or "unknown"] = row["cnt"]
            return {
                "triples": triple_count,
                "entities": entity_count,
                "sources": source_counts,
                "networkx": _HAS_NETWORKX,
            }
        except Exception as e:
            logger.warning(f"[KnowledgeGraph] get_stats failed: {e}")
            return {"triples": 0, "entities": 0, "sources": {}, "networkx": _HAS_NETWORKX}

    # ------------------------------------------------------------------
    # NetworkX integration
    # ------------------------------------------------------------------

    def _get_or_build_nx_graph(self):
        """Build or return cached NetworkX DiGraph."""
        if not _HAS_NETWORKX:
            return None
        if self._nx_graph is not None and self._graph_generation == self._write_generation:
            return self._nx_graph

        try:
            conn = self._get_conn()
            rows = conn.execute(
                "SELECT subject, predicate, object, confidence FROM triples WHERE is_active = 1"
            ).fetchall()
            G = nx.DiGraph()
            for r in rows:
                G.add_edge(
                    r["subject"], r["object"],
                    predicate=r["predicate"], confidence=r["confidence"],
                )
            self._nx_graph = G
            self._graph_generation = self._write_generation
            return G
        except Exception as e:
            logger.warning(f"[KnowledgeGraph] NetworkX build failed: {e}")
            return None

    def _find_related_nx(self, entity: str, max_depth: int) -> Optional[List[Dict]]:
        """Use NetworkX ego_graph for multi-hop traversal."""
        G = self._get_or_build_nx_graph()
        if G is None:
            return None
        if entity not in G and entity.lower() not in {n.lower() for n in G.nodes}:
            return []
        # Case-insensitive lookup
        actual = entity
        for n in G.nodes:
            if n.lower() == entity.lower():
                actual = n
                break
        try:
            ego = nx.ego_graph(G, actual, radius=max_depth, undirected=True)
            result = []
            for node in ego:
                node_data = G.nodes.get(node, {})
                result.append({"node": node, **node_data})
            return result
        except Exception:
            return []

    def _invalidate_graph(self):
        self._write_generation += 1

    # ------------------------------------------------------------------
    # SQL fallback for multi-hop traversal
    # ------------------------------------------------------------------

    def _find_related_sql(self, entity: str, max_depth: int) -> List[Dict]:
        """Iterative SQL-based multi-hop traversal."""
        conn = self._get_conn()
        visited = set()
        result = []
        frontier = {entity}

        for depth in range(max_depth):
            if not frontier:
                break
            placeholders = ",".join("?" for _ in frontier)
            rows = conn.execute(
                f"""SELECT DISTINCT subject, object FROM triples
                    WHERE is_active = 1 AND (subject IN ({placeholders}) OR object IN ({placeholders}))""",
                (*frontier, *frontier),
            ).fetchall()

            next_frontier = set()
            for r in rows:
                for node in (r["subject"], r["object"]):
                    if node not in visited:
                        visited.add(node)
                        next_frontier.add(node)
                        result.append({"node": node, "depth": depth + 1})
            frontier = next_frontier - visited

        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_entity(self, name: str) -> Optional[Dict]:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT name, entity_type, aliases, metadata FROM entities WHERE name = ?",
            (name,),
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        try:
            d["aliases"] = json.loads(d["aliases"]) if d["aliases"] else []
        except Exception:
            d["aliases"] = []
        try:
            d["metadata"] = json.loads(d["metadata"]) if d["metadata"] else {}
        except Exception:
            d["metadata"] = {}
        return d

    @staticmethod
    def _build_fts_query(raw_query: str) -> Optional[str]:
        """Tokenize query for FTS5 MATCH."""
        tokens = [t.strip() for t in raw_query.split() if t.strip()]
        if not tokens:
            return None
        return " OR ".join(f'"{t}"' for t in tokens)

    def close(self):
        conn = getattr(self._local, "conn", None)
        if conn:
            try:
                conn.close()
            except Exception:
                pass
            self._local.conn = None
