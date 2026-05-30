#!/usr/bin/env python3
"""
SkillRouter 训练脚本

训练 SkillRouter 分类器：冻结的 Qwen3-Embedding-0.6B + 可训练的 MLP 分类头。

用法：
    python train.py --data training_data.jsonl --output checkpoints/skill_router

前置条件：
    1. 先运行 synthetic_data_generator.py 生成合成数据
    2. 运行 auto_collector.py 收集真实数据
    3. 运行 skill_quality_judge.py 进行质量标注
    4. 运行 skill_dataset_builder.py 构建训练集

依赖：
    pip install torch transformers tqdm scikit-learn
"""

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

# 添加项目根目录到 path
PROJECT_ROOT = Path(__file__).parent.parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))

from training.skill_router.model import SkillRouter


# ============================================
# 数据集
# ============================================

class SkillSelectionDataset(Dataset):
    """
    Skill 选择训练数据集。

    数据格式：
    [
      {
        "user_message": "...",
        "ideal_skills": ["skill-a", "skill-b"],
        "skill_labels": [1, 1, 0, 0, ...],  # one-hot 编码
        "score": 0.9,
        "token_efficiency": 0.12
      },
      ...
    ]
    """

    def __init__(
        self,
        data: List[Dict],
        tokenizer,
        max_length: int = 512,
    ):
        """
        初始化数据集。

        Args:
            data: 训练数据列表
            tokenizer: tokenizer 实例
            max_length: 最大序列长度
        """
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]

        # 编码文本
        encoding = self.tokenizer(
            item["user_message"],
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )

        # 转换为 tensors
        input_ids = encoding["input_ids"].squeeze(0)  # [seq_len]
        attention_mask = encoding["attention_mask"].squeeze(0)  # [seq_len]

        # 标签
        labels = torch.tensor(item["skill_labels"], dtype=torch.float32)  # [num_skills]

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }


# ============================================
# 训练函数
# ============================================

def compute_metrics(predictions, labels, skill_index, threshold=0.5):
    """
    计算 skill 选择的评估指标。

    Args:
        predictions: 模型输出的概率 [batch, num_skills]
        labels: 真实标签 [batch, num_skills]
        skill_index: skill 名称到索引的映射
        threshold: 二分类阈值

    Returns:
        包含各项指标的字典
    """
    pred_binary = (predictions > threshold).float()

    # Element-wise accuracy
    element_accuracy = (pred_binary == labels).float().mean().item()

    # Per-sample metrics
    batch_size = labels.shape[0]
    precisions = []
    recalls = []
    f1s = []

    for i in range(batch_size):
        pred_set = set(pred_binary[i].nonzero(as_tuple=True)[0].tolist())
        label_set = set(labels[i].nonzero(as_tuple=True)[0].tolist())

        if len(pred_set) == 0:
            precision = 0.0
        else:
            precision = len(pred_set & label_set) / len(pred_set)

        if len(label_set) == 0:
            recall = 0.0
        else:
            recall = len(pred_set & label_set) / len(label_set)

        precisions.append(precision)
        recalls.append(recall)

        if precision + recall > 0:
            f1s.append(2 * precision * recall / (precision + recall))
        else:
            f1s.append(0.0)

    # Recall@3: 在 Top-3 预测中是否包含真实标签
    recall_at_3 = 0
    for i in range(batch_size):
        top_k = min(3, predictions.shape[1])
        top_indices = predictions[i].topk(top_k).indices.tolist()
        label_indices = labels[i].nonzero(as_tuple=True)[0].tolist()
        if any(idx in label_indices for idx in top_indices):
            recall_at_3 += 1
    recall_at_3 /= batch_size

    # Precision@3: Top-3 预测中有多少是正确的
    precision_at_3 = 0
    for i in range(batch_size):
        top_k = min(3, predictions.shape[1])
        top_indices = predictions[i].topk(top_k).indices.tolist()
        label_indices = labels[i].nonzero(as_tuple=True)[0].tolist()
        correct_in_top3 = len(set(top_indices) & set(label_indices))
        precision_at_3 += correct_in_top3 / top_k
    precision_at_3 /= batch_size

    return {
        "element_accuracy": element_accuracy,
        "mean_precision": sum(precisions) / len(precisions),
        "mean_recall": sum(recalls) / len(recalls),
        "mean_f1": sum(f1s) / len(f1s),
        "recall_at_3": recall_at_3,
        "precision_at_3": precision_at_3,
    }


def load_training_data(data_path: str) -> Tuple[List[Dict], Dict[str, int]]:
    """
    加载训练数据和 skill 索引。

    Args:
        data_path: 训练数据路径

    Returns:
        (data, skill_index)
    """
    data = []
    with open(data_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    # 加载 skill 索引
    skill_index_path = Path(data_path).parent / "skill_index.json"
    if skill_index_path.exists():
        with open(skill_index_path, "r", encoding="utf-8") as f:
            skill_index = json.load(f)
    else:
        # 从数据中构建
        all_skills = set()
        for item in data:
            for skill in item.get("ideal_skills", []):
                all_skills.add(skill)
        skill_index = {skill: idx for idx, skill in enumerate(sorted(all_skills))}

    return data, skill_index


def train_model(
    model: SkillRouter,
    train_data: List[Dict],
    skill_index: Dict[str, int],
    val_data: Optional[List[Dict]] = None,
    output_dir: str = "checkpoints/skill_router",
    num_epochs: int = 10,
    batch_size: int = 32,
    learning_rate: float = 1e-4,
    weight_decay: float = 0.01,
    warmup_steps: int = 100,
    device: Optional[str] = None,
):
    """
    训练 SkillRouter 模型。

    Args:
        model: SkillRouter 模型
        train_data: 训练数据
        skill_index: skill 名称到索引的映射
        val_data: 验证数据（可选）
        output_dir: 输出目录
        num_epochs: 训练轮数
        batch_size: 批次大小
        learning_rate: 学习率
        weight_decay: 权重衰减
        warmup_steps: 预热步数
        device: 设备
    """
    # 设备
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用设备: {device}")
    model = model.to(device)

    # 创建数据集
    train_dataset = SkillSelectionDataset(
        train_data,
        model.tokenizer,
        max_length=512,
    )
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
    )

    val_loader = None
    if val_data:
        val_dataset = SkillSelectionDataset(
            val_data,
            model.tokenizer,
            max_length=512,
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=0,
        )

    # 优化器
    optimizer = torch.optim.AdamW(
        model.classifier.parameters(),
        lr=learning_rate,
        weight_decay=weight_decay,
    )

    # 学习率调度器（带 warmup）
    total_steps = len(train_loader) * num_epochs
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer,
        max_lr=learning_rate,
        total_steps=total_steps,
        pct_start=warmup_steps / total_steps if warmup_steps < total_steps else 0.1,
    )

    # 损失函数
    criterion = nn.BCELoss()

    # 训练
    best_val_loss = float("inf")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "skill_index.json", "w", encoding="utf-8") as f:
        json.dump(skill_index, f, ensure_ascii=False, indent=2)

    print(f"\n开始训练...")
    print(f"  训练集大小: {len(train_data)}")
    if val_data:
        print(f"  验证集大小: {len(val_data)}")
    print(f"  Epochs: {num_epochs}")
    print(f"  Batch size: {batch_size}")
    print(f"  Learning rate: {learning_rate}")
    print()

    for epoch in range(num_epochs):
        # 训练阶段
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs}")
        for batch in pbar:
            # 移动到设备
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            # 前向传播
            logits = model(input_ids, attention_mask)
            loss = criterion(logits, labels)

            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            scheduler.step()

            # 统计
            train_loss += loss.item()
            predictions = (logits > 0.5).float()
            train_correct += (predictions == labels).sum().item()
            train_total += labels.numel()

            pbar.set_postfix({
                "loss": f"{loss.item():.4f}",
                "lr": f"{scheduler.get_last_lr()[0]:.6f}",
            })

        train_loss /= len(train_loader)
        train_accuracy = train_correct / train_total

        # 验证阶段
        val_loss = 0.0
        val_accuracy = 0.0
        val_metrics = {}
        if val_loader:
            model.eval()
            val_correct = 0
            val_total = 0
            all_preds = []
            all_labels = []

            with torch.no_grad():
                for batch in val_loader:
                    input_ids = batch["input_ids"].to(device)
                    attention_mask = batch["attention_mask"].to(device)
                    labels = batch["labels"].to(device)

                    logits = model(input_ids, attention_mask)
                    loss = criterion(logits, labels)

                    val_loss += loss.item()
                    predictions = (logits > 0.5).float()
                    val_correct += (predictions == labels).sum().item()
                    val_total += labels.numel()

                    all_preds.append(logits.cpu())
                    all_labels.append(labels.cpu())

            val_loss /= len(val_loader)
            val_accuracy = val_correct / val_total

            # 计算详细的评估指标
            all_preds = torch.cat(all_preds, dim=0)
            all_labels = torch.cat(all_labels, dim=0)
            val_metrics = compute_metrics(all_preds, all_labels, skill_index)

        # 打印统计
        print(
            f"Epoch {epoch+1}/{num_epochs}: "
            f"train_loss={train_loss:.4f}, train_acc={train_accuracy:.4f}"
        )
        if val_loader:
            print(f"  val_loss={val_loss:.4f}, val_acc={val_accuracy:.4f}")

        # 保存最佳模型
        if val_loader and val_loss < best_val_loss:
            best_val_loss = val_loss
            model.save_classifier(output_dir / "best")
            print(f"  OK 保存最佳模型 (val_loss={val_loss:.4f})")
        elif not val_loader and epoch == num_epochs - 1:
            # 没有验证集时，保存最后一个 epoch
            model.save_classifier(output_dir / "best")

    # 保存最终模型
    model.save_classifier(output_dir / "final")

    # 保存训练统计
    stats = {
        "num_epochs": num_epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "train_size": len(train_data),
        "val_size": len(val_data) if val_data else 0,
        "best_val_loss": best_val_loss if val_loader else None,
        "final_train_loss": train_loss,
        "final_train_accuracy": train_accuracy,
        "final_val_metrics": val_metrics if val_metrics else None,
    }
    with open(output_dir / "training_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print(f"\n训练完成!")
    print(f"  最佳模型保存到: {output_dir / 'best'}")
    print(f"  最终模型保存到: {output_dir / 'final'}")
    print(f"  训练统计保存到: {output_dir / 'training_stats.json'}")


# ============================================
# 主函数
# ============================================

def main():
    parser = argparse.ArgumentParser(description="SkillRouter 训练脚本")
    parser.add_argument(
        "--data",
        default=str(Path(__file__).parent / "training_data.jsonl"),
        help="训练数据路径（默认: training_data.jsonl）",
    )
    parser.add_argument(
        "--output",
        default=str(Path(__file__).parent / "checkpoints" / "skill_router"),
        help="输出目录（默认: checkpoints/skill_router）",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=10,
        help="训练轮数（默认: 10）",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="批次大小（默认: 32）",
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=1e-4,
        help="学习率（默认: 1e-4）",
    )
    parser.add_argument(
        "--val-split",
        type=float,
        default=0.1,
        help="验证集比例（默认: 0.1）",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="设备（默认: auto）",
    )
    parser.add_argument(
        "--embedding-model",
        default="Qwen/Qwen3-Embedding-0.6B",
        help="Embedding 模型名或本地路径（默认: Qwen/Qwen3-Embedding-0.6B）",
    )
    parser.add_argument(
        "--hf-endpoint",
        default=None,
        help="Hugging Face endpoint/mirror，例如 https://hf-mirror.com",
    )
    parser.add_argument(
        "--hf-cache-dir",
        default=None,
        help="Hugging Face 模型缓存目录（可选）",
    )
    parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="只从本地缓存或本地模型路径加载，不联网下载",
    )

    args = parser.parse_args()

    if args.hf_endpoint:
        os.environ["HF_ENDPOINT"] = args.hf_endpoint
        print(f"使用 Hugging Face endpoint: {args.hf_endpoint}")

    # 检查数据文件
    if not os.path.exists(args.data):
        print(f"错误: 训练数据文件不存在: {args.data}")
        print("请先运行 skill_dataset_builder.py 构建训练集")
        return

    # 加载数据
    print(f"加载训练数据: {args.data}")
    data, skill_index = load_training_data(args.data)
    print(f"  数据量: {len(data)} 条")
    print(f"  Skill 数量: {len(skill_index)}")

    # 分割训练集和验证集
    import random
    random.seed(42)
    random.shuffle(data)

    split_idx = int(len(data) * (1 - args.val_split))
    train_data = data[:split_idx]
    val_data = data[split_idx:]

    print(f"  训练集: {len(train_data)} 条")
    print(f"  验证集: {len(val_data)} 条")

    # 创建模型
    model = SkillRouter(
        num_skills=len(skill_index),
        embedding_model=args.embedding_model,
        cache_dir=args.hf_cache_dir,
        local_files_only=args.local_files_only,
    )

    # 训练
    train_model(
        model=model,
        train_data=train_data,
        skill_index=skill_index,
        val_data=val_data,
        output_dir=args.output,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        device=args.device,
    )


if __name__ == "__main__":
    main()
