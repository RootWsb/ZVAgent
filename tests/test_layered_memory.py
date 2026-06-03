import json

from agent.memory.config import MemoryConfig
from agent.memory.layered import (
    EpisodicMemoryStore,
    LayeredMemoryService,
    ProfileMemoryStore,
)
from agent.prompt.builder import _build_memory_section


def test_episodic_memory_appends_jsonl_and_reports_stats(tmp_path):
    config = MemoryConfig(workspace_root=str(tmp_path), episodic_max_items=10)
    store = EpisodicMemoryStore(config)

    record = store.append(
        "用户希望将记忆层拆成中期事件、用户画像和长期记忆。",
        session_id="web_test",
        importance=1.2,
        stability=-1,
        candidate_targets=["profile", "long_term"],
    )

    assert record.id.startswith("evt_")
    assert record.importance == 1.0
    assert record.stability == 0.0

    files = list((tmp_path / "memory" / "episodic").glob("*.jsonl"))
    assert len(files) == 1

    payload = json.loads(files[0].read_text(encoding="utf-8").strip())
    assert payload["summary"] == "用户希望将记忆层拆成中期事件、用户画像和长期记忆。"
    assert payload["session_id"] == "web_test"
    assert payload["candidate_targets"] == ["profile", "long_term"]

    stats = store.stats()
    assert stats["items"] == 1
    assert stats["estimated_tokens"] > 0
    assert stats["should_compact"] is False


def test_episodic_memory_should_compact_after_item_threshold(tmp_path):
    config = MemoryConfig(workspace_root=str(tmp_path), episodic_max_items=2)
    store = EpisodicMemoryStore(config)

    store.append("first memory")
    store.append("second memory")
    assert store.stats()["should_compact"] is False

    store.append("third memory")
    assert store.stats()["should_compact"] is True


def test_profile_memory_generates_summary_and_history(tmp_path):
    config = MemoryConfig(workspace_root=str(tmp_path))
    store = ProfileMemoryStore(config)

    profile = store.load()
    profile["identity"]["language"] = "zh-CN"
    profile["identity"]["timezone"] = "Asia/Shanghai"
    profile["preferences"].append({
        "key": "memory_architecture",
        "value": "偏好显式用户画像层",
        "confidence": 0.9,
        "status": "active",
    })
    profile["goals"].append({
        "value": "训练中期和长期记忆层",
        "confidence": 0.9,
        "status": "active",
    })

    saved = store.save(profile, reason="test")
    summary = store.read_summary()

    assert saved["updated_at"]
    assert "language=zh-CN" in summary
    assert "偏好显式用户画像层" in summary
    assert "训练中期和长期记忆层" in summary
    assert store.history_path.read_text(encoding="utf-8").strip()


def test_layered_memory_service_status_includes_thresholds(tmp_path):
    config = MemoryConfig(workspace_root=str(tmp_path), episodic_max_items=3)
    service = LayeredMemoryService(config)
    service.episodic.append("用户正在设计包含用户画像层的可训练分层记忆系统。")

    status = service.get_status()

    assert status["episodic"]["items"] == 1
    assert status["profile"]["summary_tokens"] == 0
    assert status["thresholds"]["episodic_max_items"] == 3


def test_layered_memory_searches_episodic_and_profile(tmp_path):
    config = MemoryConfig(workspace_root=str(tmp_path))
    service = LayeredMemoryService(config)
    service.episodic.append("用户正在设计包含用户画像层的可训练分层记忆系统。")

    profile = service.profile.load()
    profile["preferences"].append({
        "key": "memory_architecture",
        "value": "偏好显式用户画像层",
        "confidence": 0.9,
        "status": "active",
    })
    service.profile.save(profile, reason="test")

    result = service.search("用户画像", layers=["episodic", "profile"], limit=5)

    assert result["episodic"]
    assert result["profile"][0]["_section"] == "preferences"


def test_layered_memory_runs_compaction_job_when_threshold_exceeded(tmp_path):
    config = MemoryConfig(
        workspace_root=str(tmp_path),
        episodic_max_items=1,
        episodic_keep_recent_items=1,
    )
    service = LayeredMemoryService(config)

    records = service.append_episodic_from_summary(
        "- 用户正在设计分层记忆系统。\n- 用户希望自动压缩中期记忆。",
        reason="trim",
    )

    assert len(records) == 2
    queue = tmp_path / "memory" / "jobs" / "compaction_queue.jsonl"
    assert queue.exists()
    payload = json.loads(queue.read_text(encoding="utf-8").strip())
    assert payload["layer"] == "episodic"
    assert payload["status"] == "done"
    assert payload["result"]["status"] == "compacted"


def test_process_compaction_queue_compacts_old_episodic_records(tmp_path):
    config = MemoryConfig(
        workspace_root=str(tmp_path),
        episodic_max_items=10,
        episodic_keep_recent_items=1,
    )
    service = LayeredMemoryService(config)

    service.append_episodic_from_summary(
        "- first architecture decision\n- second profile preference\n- third recent event",
        reason="trim",
    )
    service.enqueue_compaction_job(layer="episodic", reason="test")

    result = service.process_compaction_queue(force=True)

    assert result["processed"] == 1
    assert result["compacted"] == 1

    active = service.episodic.list_all()
    assert len(active) == 1
    assert active[0].summary == "third recent event"

    compacted_dir = tmp_path / "memory" / "episodic" / "compacted"
    md_files = list(compacted_dir.glob("*.md"))
    raw_files = list(compacted_dir.glob("*.jsonl"))
    assert len(md_files) == 1
    assert len(raw_files) == 1
    assert "first architecture decision" in md_files[0].read_text(encoding="utf-8")
    assert "third recent event" not in md_files[0].read_text(encoding="utf-8")

    queue = tmp_path / "memory" / "jobs" / "compaction_queue.jsonl"
    job = json.loads(queue.read_text(encoding="utf-8").strip())
    assert job["status"] == "done"
    assert job["result"]["status"] == "compacted"


class _DummyTool:
    name = "memory_search"


class _DummyMemoryManager:
    def __init__(self, layered_memory):
        self.layered_memory = layered_memory


def test_memory_prompt_injects_profile_summary(tmp_path):
    config = MemoryConfig(workspace_root=str(tmp_path))
    service = LayeredMemoryService(config)
    profile = service.profile.load()
    profile["goals"].append({
        "value": "训练中期和长期记忆层",
        "confidence": 0.9,
        "status": "active",
    })
    service.profile.save(profile, reason="test")

    lines = _build_memory_section(_DummyMemoryManager(service), [_DummyTool()], "zh")
    prompt = "\n".join(lines)

    assert "User Profile Summary" in prompt
    assert "训练中期和长期记忆层" in prompt
    assert "memory/episodic/*.jsonl" in prompt
