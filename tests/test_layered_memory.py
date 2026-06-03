import json

from agent.memory.config import MemoryConfig
from agent.memory.layered import (
    EpisodicMemoryStore,
    LayeredMemoryService,
    ProfileMemoryStore,
)


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
    service.episodic.append("用户正在设计可训练的分层记忆系统。")

    status = service.get_status()

    assert status["episodic"]["items"] == 1
    assert status["profile"]["summary_tokens"] == 0
    assert status["thresholds"]["episodic_max_items"] == 3
