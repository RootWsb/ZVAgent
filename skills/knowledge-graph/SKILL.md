---
name: knowledge-graph
description: 管理知识图谱。查询实体关系、查看图谱统计、手动添加事实。当需要探索人物、概念、项目之间的关联，或用户询问"A和B有什么关系"时使用。
---

# Knowledge Graph

知识图谱以三元组（主语-谓词-宾语）的形式存储结构化事实，支持实体关系查询和多跳遍历。

## 工具

使用 `graph_query` 工具操作知识图谱：

### 查询关联实体

```
graph_query(action="related", entity="实体名", max_depth=2)
```

返回与指定实体直接或间接关联的所有实体。

### 全文搜索三元组

```
graph_query(action="search", query="搜索文本")
```

在所有三元组的主语、谓词、宾语中搜索匹配文本。

### 查看实体详情

```
graph_query(action="entity_info", entity="实体名")
```

返回该实体的所有直接关系和元数据。

### 查看图谱统计

```
graph_query(action="stats")
```

返回三元组数量、实体数量、来源分布等统计信息。

### 手动添加事实

```
graph_query(action="add", entity="主语", predicate="谓词", object="宾语")
```

手动向图谱添加一个三元组。仅用于补充 LLM 自动抽取遗漏的重要事实。

## 使用场景

- **探索关联**: "DeepSeek 和哪些项目有关？" → `graph_query(action="related", entity="DeepSeek")`
- **查找事实**: "ZVAgent 支持哪些模型？" → `graph_query(action="search", query="模型")`
- **补充知识**: 用户明确告知的事实可手动添加
- **查看全貌**: `graph_query(action="stats")` 了解图谱覆盖范围

## 注意事项

- 图谱事实由 LLM 自动从记忆和知识库中抽取，无需手动维护
- 自动抽取在记忆蒸馏（Deep Dream）和记忆同步时触发
- 三元组去重：相同的（主语, 谓词, 宾语, 来源）不会重复存储
- 软删除：当源文件更新时，旧三元组会被标记为失效，新三元组会被抽取
