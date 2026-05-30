# Skill Router 训练系统

ZVAgent skill 路由器训练系统，用于替代硬编码关键词匹配，实现数据驱动的 skill 选择。

## 目录结构

```
training/skill_router/
├── tasks.txt                    # 任务描述文件（115 个任务）
├── synthetic_data_generator.py  # Phase A: 合成数据生成
├── auto_collector.py            # Phase B: 自动对话数据收集
├── skill_quality_judge.py       # LLM Judge 质量标注
├── skill_dataset_builder.py     # 训练集构建
├── model.py                     # SkillRouter 模型定义
└── train.py                     # 训练脚本

agent/training/
├── __init__.py
└── skill_selection_collector.py # 实时 skill 选择收集器
```

## 快速开始

### Step 1: 生成合成数据（Phase A）

```bash
cd ZVagent/training/skill_router
python synthetic_data_generator.py --tasks tasks.txt --output synthetic_data.jsonl
```

- 输入：tasks.txt（115 个任务描述）
- 输出：synthetic_data.jsonl（~575 条合成数据）
- 预计时间：1-2 小时
- 成本：~$0.25（DeepSeek V4 Pro）

### Step 2: 收集真实数据（Phase B）

```bash
cd ZVagent/training/skill_router
python auto_collector.py --input synthetic_data.jsonl --output real_data.jsonl
```

- 输入：synthetic_data.jsonl
- 输出：real_data.jsonl（~100 条真实数据）
- 预计时间：30 分钟
- 前置条件：ZVAgent 可正常启动

### Step 3: 质量标注（LLM Judge）

```bash
cd ZVagent/training/skill_router
python skill_quality_judge.py --input real_data.jsonl --output labeled_data.jsonl
```

- 输入：real_data.jsonl 或 synthetic_data.jsonl
- 输出：labeled_data.jsonl（带评分的高质量数据）
- 预计时间：30 分钟
- 成本：~$0.60（600 条 × $0.001）

### Step 4: 构建训练集

```bash
cd ZVagent/training/skill_router
python skill_dataset_builder.py --synthetic synthetic_data.jsonl --real real_data.jsonl --output training_data.jsonl
```

- 输入：synthetic_data.jsonl + real_data.jsonl
- 输出：training_data.jsonl + skill_index.json
- 过滤条件：score >= 0.7, token_efficiency < 0.25

### Step 5: 训练分类器

```bash
cd ZVagent/training/skill_router
python train.py --data training_data.jsonl --output checkpoints/skill_router
```

- 输入：training_data.jsonl
- 输出：checkpoints/skill_router/best/ + final/
- 预计时间：10-20 分钟（24GB GPU）
- 显存占用：~8GB

## 配置说明

在 `config.json` 中添加：

```json
{
  "skill_router_enabled": false,
  "skill_router_model_path": "training/skill_router/checkpoints/best",
  "skill_router_top_k": 5,
  "training_data_enabled": true,
  "training_data_dir": "training/data",
  "training_judge_model": "deepseek-v4-pro"
}
```

## 模型架构

```
用户消息 → Qwen3-Embedding-0.6B (冻结) → 语义向量 → MLP 分类头 (可训练) → Top-K skills
```

- Embedding 模型：Qwen3-Embedding-0.6B（冻结，不训练）
- 分类头：MLP（256 维隐藏层，~几 MB）
- 输出：37 个 skill 的概率分数

## 训练指标

| 指标 | 含义 | 目标 |
|------|------|------|
| selection_accuracy | 分类器选的 skills vs Judge 标注的正确 skills | >80% |
| recall@3 | Top-3 选择中是否包含正确 skill | >85% |
| precision@3 | Top-3 选择中有多少是真正需要的 | >70% |
| bce_loss | BCELoss（多标签分类损失） | 持续下降 |
| token_cost | skill prompt 占 system prompt 的 token 比例 | <15% |

## API 配置

脚本默认使用以下配置：

- 模型：deepseek-v4-pro
- API Base：https://inferaichat.com
- API Key：已内置（sk-82124fde...）

可通过命令行参数覆盖：

```bash
python synthetic_data_generator.py --model deepseek-v4-pro --api-base https://api.deepseek.com
```

## 常见问题

### Q: 如何启用训练好的 SkillRouter？

A: 修改 `config.json`：
```json
{
  "skill_router_enabled": true
}
```

### Q: 训练失败怎么办？

A: 检查：
1. GPU 显存是否足够（需 8GB+）
2. 训练数据是否存在（training_data.jsonl）
3. 依赖是否安装：`pip install torch transformers tqdm`

### Q: 如何查看训练效果？

A: 查看 `checkpoints/skill_router/training_stats.json`，关注：
- train_loss：应持续下降
- val_loss：应在几个 epoch 后稳定
- train_accuracy：应逐步提升

### Q: 如何收集更多真实数据？

A: 运行 ZVAgent 时，`skill_selection_collector.py` 会自动记录 skill 选择决策到 `~/zvagent/training/data/skill_selections.jsonl`。

---

**维护说明**：本文档由 Claude Code 生成于 2026-05-23，用于指导 ZVAgent skill 路由器训练系统的使用。
