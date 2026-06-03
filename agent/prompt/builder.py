"""
System Prompt Builder - 系统提示词构建器

实现模块化的系统提示词构建，支持工具、技能、记忆等多个子系统
"""

from __future__ import annotations
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from common.log import logger
from config import conf


@dataclass
class ContextFile:
    """上下文文件"""
    path: str
    content: str


class PromptBuilder:
    """提示词构建器"""
    
    def __init__(self, workspace_dir: str, language: str = "zh"):
        """
        初始化提示词构建器
        
        Args:
            workspace_dir: 工作空间目录
            language: 语言 ("zh" 或 "en")
        """
        self.workspace_dir = workspace_dir
        self.language = language
    
    def build(
        self,
        base_persona: Optional[str] = None,
        user_identity: Optional[Dict[str, str]] = None,
        tools: Optional[List[Any]] = None,
        context_files: Optional[List[ContextFile]] = None,
        skill_manager: Any = None,
        memory_manager: Any = None,
        runtime_info: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        构建完整的系统提示词
        
        Args:
            base_persona: 基础人格描述（会被context_files中的AGENT.md覆盖）
            user_identity: 用户身份信息
            tools: 工具列表
            context_files: 上下文文件列表（AGENT.md, USER.md, RULE.md, BOOTSTRAP.md等）
            skill_manager: 技能管理器
            memory_manager: 记忆管理器
            runtime_info: 运行时信息
            **kwargs: 其他参数
            
        Returns:
            完整的系统提示词
        """
        return build_agent_system_prompt(
            workspace_dir=self.workspace_dir,
            language=self.language,
            base_persona=base_persona,
            user_identity=user_identity,
            tools=tools,
            context_files=context_files,
            skill_manager=skill_manager,
            memory_manager=memory_manager,
            runtime_info=runtime_info,
            **kwargs
        )


def build_agent_system_prompt(
    workspace_dir: str,
    language: str = "zh",
    base_persona: Optional[str] = None,
    user_identity: Optional[Dict[str, str]] = None,
    tools: Optional[List[Any]] = None,
    context_files: Optional[List[ContextFile]] = None,
    skill_manager: Any = None,
    memory_manager: Any = None,
    runtime_info: Optional[Dict[str, Any]] = None,
    **kwargs
) -> str:
    """
    构建Agent系统提示词
    
    顺序说明（按重要性和逻辑关系排列）:
    1. 工具系统 - 核心能力，最先介绍
    2. 技能系统 - 紧跟工具，因为技能需要用 read 工具读取
    3. 记忆系统 - 记忆检索与写入引导
    3.5 知识系统 - 结构化知识库（knowledge/index.md 注入）
    4. 工作空间 - 工作环境说明
    5. 用户身份 - 用户信息（可选）
    6. 项目上下文 - AGENT.md, USER.md, RULE.md, MEMORY.md, BOOTSTRAP.md
    7. 运行时信息 - 元信息（时间、模型等）
    
    Args:
        workspace_dir: 工作空间目录
        language: 语言 ("zh" 或 "en")
        base_persona: 基础人格描述（已废弃，由AGENT.md定义）
        user_identity: 用户身份信息
        tools: 工具列表
        context_files: 上下文文件列表
        skill_manager: 技能管理器
        memory_manager: 记忆管理器
        runtime_info: 运行时信息
        **kwargs: 其他参数
        
    Returns:
        完整的系统提示词
    """
    sections = []
    
    # 1. 工具系统（最重要，放在最前面）
    if tools:
        sections.extend(_build_tooling_section(tools, language))
    
    # 2. 技能系统（紧跟工具，因为需要用 read 工具）
    if skill_manager:
        sections.extend(_build_skills_section(
            skill_manager,
            tools,
            language,
            skill_filter=kwargs.get("skill_filter"),
        ))
    
    # 3. 记忆系统（独立的记忆能力）
    if memory_manager:
        sections.extend(_build_memory_section(memory_manager, tools, language))

    # 3.5 知识系统（结构化知识库）
    if conf().get("knowledge", True):
        sections.extend(_build_knowledge_section(workspace_dir, language))

    # 3.6 垂直助手输出协议
    sections.extend(_build_vertical_contract_section(language))
    
    # 4. 工作空间（工作环境说明）
    sections.extend(_build_workspace_section(workspace_dir, language))
    
    # 5. 用户身份（如果有）
    if user_identity:
        sections.extend(_build_user_identity_section(user_identity, language))
    
    # 6. 项目上下文文件（AGENT.md, USER.md, RULE.md - 定义人格）
    if context_files:
        sections.extend(_build_context_files_section(context_files, language))
    
    # 7. 运行时信息（元信息，放在最后）
    if runtime_info:
        sections.extend(_build_runtime_section(runtime_info, language))
    
    return "\n".join(sections)


def _build_identity_section(base_persona: Optional[str], language: str) -> List[str]:
    """构建基础身份section - 不再需要，身份由AGENT.md定义"""
    # 不再生成基础身份section，完全由AGENT.md定义
    return []


def _build_tooling_section(tools: List[Any], language: str) -> List[str]:
    """Build tooling section with concise tool list and call style guide."""
    # One-line summaries for known tools (details are in the tool schema)
    core_summaries = {
        "read": "读取文件内容",
        "write": "创建或覆盖文件",
        "edit": "精确编辑文件",
        "ls": "列出目录内容",
        "grep": "搜索文件内容",
        "find": "按模式查找文件",
        "bash": "执行shell命令",
        "terminal": "管理后台进程",
        "web_search": "网络搜索",
        "web_fetch": "获取URL内容",
        "browser": "控制浏览器（关键结果或需要协助可截图发送给用户）",
        "memory_search": "搜索记忆",
        "memory_get": "读取记忆内容",
        "env_config": "管理API密钥和技能配置",
        "scheduler": "管理定时任务和提醒",
        "send": "发送本地文件给用户（仅限本地文件，URL直接放在回复文本中）",
        "vision": "分析图片内容（识别、描述、OCR文字提取等）",
    }

    # Preferred display order
    tool_order = [
        "read", "write", "edit", "ls", "grep", "find",
        "bash", "terminal",
        "web_search", "web_fetch", "browser",
        "memory_search", "memory_get",
        "env_config", "scheduler", "send", "vision",
    ]

    # Build name -> summary mapping for available tools
    available = {}
    for tool in tools:
        name = tool.name if hasattr(tool, 'name') else str(tool)
        available[name] = core_summaries.get(name, "")

    # Generate tool lines: ordered tools first, then extras
    tool_lines = []
    for name in tool_order:
        if name in available:
            summary = available.pop(name)
            tool_lines.append(f"- {name}: {summary}" if summary else f"- {name}")
    for name in sorted(available):
        summary = available[name]
        tool_lines.append(f"- {name}: {summary}" if summary else f"- {name}")

    lines = [
        "## 🔧 工具系统",
        "",
        "可用工具（名称大小写敏感，严格按列表调用）:",
        "\n".join(tool_lines),
        "",
        "工具调用风格：",
        "",
        "- 多步骤任务、复杂决策、敏感操作时，应简要说明当前在做什么、为什么这样做，让用户了解关键进展",
        "- 持续推进直到任务完成，完成后向用户报告结果",
        "- 回复中涉及密钥、令牌等敏感信息必须脱敏",
        "- URL链接直接放在回复文本中即可，系统会自动处理和渲染。无需下载后使用send工具发送",
        "",
    ]

    return lines


def _build_skills_section(
    skill_manager: Any,
    tools: Optional[List[Any]],
    language: str,
    skill_filter: Optional[List[str]] = None,
) -> List[str]:
    """构建技能系统section"""
    if not skill_manager:
        return []
    
    # 获取read工具名称
    read_tool_name = "read"
    if tools:
        for tool in tools:
            tool_name = tool.name if hasattr(tool, 'name') else str(tool)
            if tool_name.lower() == "read":
                read_tool_name = tool_name
                break
    
    lines = [
        "## 🧩 技能系统（mandatory）",
        "",
        "在回复之前：扫描下方 <available_skills> 中每个技能的 <description>。",
        "",
        f"- 如果有技能的描述与用户需求匹配：使用 `{read_tool_name}` 工具读取其 <location> 路径的 SKILL.md 文件，然后严格遵循文件中的指令。"
        "当有匹配的技能时，应优先使用技能",
        "- 如果多个技能都适用则选择最匹配的一个，然后读取并遵循。",
        "- 如果没有技能明确适用：不要读取任何 SKILL.md，直接使用通用工具。",
        "",
        f"**重要**: 技能不是工具，不能直接调用。使用技能的唯一方式是用 `{read_tool_name}` 读取 SKILL.md 文件，然后按文件内容操作。"
        "永远不要一次性读取多个技能，只在选择后再读取。",
        "",
        "以下是可用技能："
    ]
    lines[4:4] = [
        "- 如果 <candidate_skill_summaries> 存在，先用它缩小候选范围，但不要把摘要当成完整执行手册。",
    ]
    lines[10:10] = [
        "- 摘要只能用于路由和预判；真正执行 skill 前，必须读取完整 SKILL.md。",
    ]
    
    # 添加技能列表（通过skill_manager获取）
    try:
        skills_prompt = skill_manager.build_skills_prompt(skill_filter=skill_filter)
        logger.debug(f"[PromptBuilder] Skills prompt length: {len(skills_prompt) if skills_prompt else 0}")
        if skills_prompt:
            lines.append(skills_prompt.strip())
            lines.append("")
        else:
            logger.warning("[PromptBuilder] No skills prompt generated - skills_prompt is empty")
    except Exception as e:
        logger.warning(f"Failed to build skills prompt: {e}")
        import traceback
        logger.debug(f"Skills prompt error traceback: {traceback.format_exc()}")
    
    return lines


def _build_memory_section(memory_manager: Any, tools: Optional[List[Any]], language: str) -> List[str]:
    """构建记忆系统section"""
    if not memory_manager:
        return []

    has_memory_tools = False
    if tools:
        tool_names = [tool.name if hasattr(tool, 'name') else str(tool) for tool in tools]
        has_memory_tools = any(name in ['memory_search', 'memory_get'] for name in tool_names)

    if not has_memory_tools:
        return []

    from datetime import datetime
    today_file = datetime.now().strftime("%Y-%m-%d") + ".md"
    profile_summary = ""
    layered_memory = getattr(memory_manager, "layered_memory", None)
    if layered_memory:
        try:
            profile_summary = layered_memory.profile.read_summary()
        except Exception:
            profile_summary = ""

    lines = [
        "## 🧠 记忆系统",
        "",
        "### Memory Recall（mandatory）",
        "",
        "当用户询问过往事件、引用之前的决定、提到人物关系、偏好、待办、或你对某事不确定时，**必须先检索记忆再回答**。",
        "如果 MEMORY.md 中已有相关信息则无需重复检索。完整内容和每日记忆需要通过工具检索。",
        "",
        "1. 不确定位置 → `memory_search` 关键词/语义检索",
        "2. 已知位置 → `memory_get` 直接读取对应行",
        "3. search 无结果 → `memory_get` 读最近两天记忆",
        "4. 关系查询 → `graph_query` 探索实体关系（当需要了解人物、概念、项目之间的关联时）",
        "",
        "**记忆文件结构**:",
        "- `MEMORY.md`: 长期记忆索引（已自动加载到上下文，核心信息、偏好、决策等）",
        f"- `memory/YYYY-MM-DD.md`: 每日记忆，今天是 `memory/{today_file}`",
        "- `memory/episodic/*.jsonl`: 中期事件记忆，用于回忆最近发生过什么",
        "- `memory/profile/user_profile.json`: 用户画像，记录稳定偏好、目标、约束和沟通风格",
        "- `knowledge/`: 结构化知识库（见下方知识系统）",
        "",
        "### 分层检索路由",
        "",
        "- 最近、上次、刚才、之前发生的事件 → `memory_search` 搜索 `episodic`",
        "- 用户偏好、目标、习惯、约束、身份信息 → `memory_search` 搜索 `profile`",
        "- 项目决策、长期事实、可复用经验 → `memory_search` 搜索 `classic` / `MEMORY.md`",
        "",
        "### 写入记忆",
        "",
        "遇到以下情况时，**主动**将信息写入记忆文件（无需告知用户）：",
        "",
        "- 用户要求记住某些信息，或使用了「记住」「以后」「总是」「不要」「偏好」等表达",
        "- 用户分享了重要的个人偏好、习惯、决策",
        "- 对话中产生了重要的结论、方案、约定",
        "- 完成了复杂任务，值得记录关键步骤和结果",
        "",
        "**存储规则**:",
        f"- 长期核心信息 → `MEMORY.md`",
        f"- 当天事件/进展 → `memory/{today_file}`",
        "- 结构化知识 → `knowledge/`（见知识系统）",
        "- 追加 → `edit` 工具，oldText 留空",
        "- 修改 → `edit` 工具，oldText 填写要替换的文本",
        "- **禁止写入敏感信息**（API密钥、令牌等）",
        "",
        "**使用原则**: 自然使用记忆，就像你本来就知道；不用刻意提起，除非用户问起。",
        "",
    ]

    if profile_summary:
        lines[2:2] = [
            "### User Profile Summary",
            "",
            profile_summary,
            "",
        ]

    return lines


def _build_knowledge_section(workspace_dir: str, language: str) -> List[str]:
    """Build knowledge wiki section. Injects knowledge/index.md when present."""
    index_path = os.path.join(workspace_dir, "knowledge", "index.md")
    if not os.path.exists(index_path):
        return []

    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read().strip()
    except Exception:
        return []

    lines = [
        "## 📚 知识系统",
        "",
        "你拥有一个持续积累的个人知识库 `knowledge/`，这是你的长期结构化知识存储。",
        "",
        "### 自动写入规则（mandatory）",
        "",
        "以下场景**必须**在回复的同时写入知识库，**直接写入，不要询问用户是否需要**：",
        "",
        "1. **用户分享了文章/链接/文档** → 阅读理解后，按领域写入 `knowledge/research/`、`knowledge/crypto/`、`knowledge/economics/` 或 `knowledge/ai-tech/`",
        "2. **深度讨论产生了结论/方案** → 按领域整理为可复用的 brief、note、theme 或 analysis 页面",
        "3. **对话横跨多个领域** → 写入 `knowledge/cross-domain/`，并链接到已存在的相关领域页面",
        "4. **讨论了长期有价值的实体、技术概念或方法论** → 在对应领域目录下创建或更新页面",
        "",
        "每次写入知识页面后，**必须同步更新** `knowledge/index.md` 添加一行索引。",
        "详细的页面格式和操作规范，请读取技能 `knowledge-wiki` 的 SKILL.md。",
        "",
        "⚠️ 不要问「要不要存到知识库」——符合上述场景就直接写入，这是你的本能行为。",
        "",
    ]

    if index_content:
        lines.extend([
            "### 当前知识索引",
            "",
            index_content,
            "",
        ])

    lines.extend([
        "**查询方式**：用 `read` 读取知识页面，或用 `memory_search` 检索（知识已纳入向量索引）。",
        "",
    ])

    return lines


def _build_vertical_contract_section(language: str) -> List[str]:
    """Build the shared response contract for the vertical assistant."""
    return [
        "## 垂直助手输出协议",
        "",
        "你是一个面向科研、加密货币、经济分析和 AI 技术文章的垂直研究助手。处理分析型问题时，先判断领域，再选择最匹配的技能和输出结构。",
        "",
        "### 领域路由",
        "",
        "- 科研论文、文献综述、公式解释、代码复现、实验计划 → `research-assistant`",
        "- 论文PDF下载、保存全文、按 DOI/arXiv/PMCID 获取开放获取论文 → `paper-download`",
        "- Bitcoin、Ethereum、DeFi、监管、交易所、链上叙事、币种风险 → `crypto-news`",
        "- CPI、GDP、就业、利率、央行、汇率、大宗商品、跨资产影响 → `economic-analysis`",
        "- AI 模型发布、技术文章、开源项目、RAG、Agent、推理、训练、评测 → `ai-tech-digest`",
        "- 日报、周报、月报、定时简报、自动归档 → `brief-automation`",
        "- 任务路由、quick/brief/deep/archive 选择、检索预算、输出预算 → `task-budget-router`",
        "- 数据源选择、官方来源核验、证据计划 → `source-registry`",
        "- 输出质量检查、失败保护、发布前验证 → `quality-guardrails`",
        "- 用户反馈、偏好记忆、常用任务模板、回答长度、token 节省 → `usage-learning-optimizer`",
        "- 反馈闭环、模板进化、偏好/模板变更提案与应用 → `feedback-template-evolver`",
        "- 知识库压缩、重复检测、轻量索引、上下文包、token 优化 → `knowledge-compression-indexer`",
        "- 知识沉淀、索引、复用、查询 → `knowledge-wiki`",
        "- 跨领域或开放式问题 → 先用 `vertical-research-orchestrator` 规划，再组合相关技能",
        "",
        "### 默认输出骨架",
        "",
        "除非用户要求特定格式，简报和分析默认使用：",
        "",
        "```markdown",
        "## 结论",
        "...",
        "",
        "## 依据",
        "- ...",
        "",
        "## 机制",
        "- ...",
        "",
        "## 风险/不确定性",
        "- ...",
        "",
        "## 下一步",
        "- ...",
        "```",
        "",
        "### 质量要求",
        "",
        "- 明确区分事实、推断和假设。",
        "- 非平凡分析先用 `task-budget-router` 的预算思路：选择最小有效模式、限制本地阅读页数和新来源数量，再按需扩展。",
        "- 涉及今天、最新、价格、政策、模型发布、排行榜、API、法规时，先用 `source-registry` 选源，再核验当前信息。",
        "- 对金融和加密问题给研究分析和风险框架，不给确定性买卖指令。",
        "- 用户给出稳定偏好或反馈时，用 `usage-learning-optimizer` 维护 `knowledge/profile/`，以后优先复用短上下文而不是重复解释。",
        "- 当反馈要改变未来行为时，用 `feedback-template-evolver` 先生成可审阅提案，再应用到偏好、模板或预算规则。",
        "- 从大量本地知识回答前，优先用 `knowledge-compression-indexer` 选择小型上下文包，避免通读全部笔记。",
        "- 自动化简报、知识库归档或对外发布前，优先用 `quality-guardrails` 做结构和证据自检。",
        "- 有长期价值的结论、资料和专题简报写入 `knowledge/`，并维护 `knowledge/index.md` 与 `knowledge/log.md`。",
        "",
    ]


def _build_user_identity_section(user_identity: Dict[str, str], language: str) -> List[str]:
    """构建用户身份section"""
    if not user_identity:
        return []
    
    lines = [
        "## 👤 用户身份",
        "",
    ]
    
    if user_identity.get("name"):
        lines.append(f"**用户姓名**: {user_identity['name']}")
    if user_identity.get("nickname"):
        lines.append(f"**称呼**: {user_identity['nickname']}")
    if user_identity.get("timezone"):
        lines.append(f"**时区**: {user_identity['timezone']}")
    if user_identity.get("notes"):
        lines.append(f"**备注**: {user_identity['notes']}")
    
    lines.append("")
    
    return lines


def _build_docs_section(workspace_dir: str, language: str) -> List[str]:
    """构建文档路径section - 已移除，不再需要"""
    # 不再生成文档section
    return []


def _build_workspace_section(workspace_dir: str, language: str) -> List[str]:
    """构建工作空间section"""
    lines = [
        "## 📂 工作空间",
        "",
        f"你的工作目录是: `{workspace_dir}`",
        "",
        "**路径使用规则** (非常重要):",
        "",
        f"1. **相对路径的基准目录**: 所有相对路径都是相对于 `{workspace_dir}` 而言的",
        f"   - ✅ 正确: 访问工作空间内的文件用相对路径，如 `AGENT.md`",
        f"   - ❌ 错误: 用相对路径访问其他目录的文件 (如果它不在 `{workspace_dir}` 内)",
        "",
        "2. **访问其他目录**: 如果要访问工作空间之外的目录（如项目代码、系统文件），**必须使用绝对路径**",
        f"   - ✅ 正确: 例如 `~/chatgpt-on-wechat`、`/usr/local/`",
        f"   - ❌ 错误: 假设相对路径会指向其他目录",
        "",
        "3. **路径解析示例**:",
        f"   - 相对路径 `memory/` → 实际路径 `{workspace_dir}/memory/`",
        f"   - 绝对路径 `~/chatgpt-on-wechat/docs/` → 实际路径 `~/chatgpt-on-wechat/docs/`",
        "",
        "4. **不确定时**: 先用 `bash pwd` 确认当前目录，或用 `ls .` 查看当前位置",
        "",
        "**重要说明 - 文件已自动加载**:",
        "",
        "以下文件在会话启动时**已经自动加载**到系统提示词中，你**无需再用 read 工具读取**：",
        "",
        "- ✅ `AGENT.md`: 已加载 - 你的人格和灵魂设定，请严格遵循。当你的名字、性格或交流风格发生变化时，主动用 `edit` 更新此文件",
        "- ✅ `USER.md`: 已加载 - 用户的身份信息。当用户修改称呼、姓名等身份信息时，用 `edit` 更新此文件",
        "- ✅ `RULE.md`: 已加载 - 工作空间使用指南和规则，请严格遵循",
        "- ✅ `MEMORY.md`: 已加载 - 长期记忆索引",
        "",
        "**💬 交流规范**:",
        "",
        "- 记忆相关操作无需暴露文件名，用自然语言表达即可。例如说「我已记住」而非「已更新 MEMORY.md」",
        "- 任务执行过程中的关键决策和步骤应该告知用户，让用户了解你在做什么、为什么这么做",
        "- 做真正有帮助的助手，而不是表演式的客套，尽可能帮忙解决问题",
        "- 回复应结构清晰、重点突出。善用 **加粗**、列表、分段等格式让信息一目了然",
        "- 适当使用 emoji 让表达更生动自然 🎯，但不要过度堆砌",
        "",
    ]

    # Cloud deployment: inject websites directory info and access URL
    cloud_website_lines = _build_cloud_website_section(workspace_dir)
    if cloud_website_lines:
        lines.extend(cloud_website_lines)
    
    return lines


def _build_cloud_website_section(workspace_dir: str) -> List[str]:
    """Build cloud website access prompt when cloud deployment is configured."""
    try:
        from common.cloud_client import build_website_prompt
        return build_website_prompt(workspace_dir)
    except Exception:
        return []


def _build_context_files_section(context_files: List[ContextFile], language: str) -> List[str]:
    """构建项目上下文文件section"""
    if not context_files:
        return []
    
    # 检查是否有AGENT.md
    has_agent = any(
        f.path.lower().endswith('agent.md') or 'agent.md' in f.path.lower()
        for f in context_files
    )
    
    lines = [
        "# 📋 项目上下文",
        "",
        "以下项目上下文文件已被加载：",
        "",
    ]
    
    if has_agent:
        lines.append("**`AGENT.md` 是你的灵魂文件** 🪞：严格遵循其中定义的人格、语气和设定，做真实的自己，避免僵硬、模板化的回复。")
        lines.append("当用户通过对话透露了对你性格、风格、职责、能力边界的新期望，你应该主动用 `edit` 更新 AGENT.md 以反映这些演变。")
        lines.append("")
    
    # 添加每个文件的内容
    for file in context_files:
        lines.append(f"## {file.path}")
        lines.append("")
        lines.append(file.content)
        lines.append("")
    
    return lines


def _build_runtime_section(runtime_info: Dict[str, Any], language: str) -> List[str]:
    """构建运行时信息section - 支持动态时间"""
    if not runtime_info:
        return []
    
    lines = [
        "## ⚙️ 运行时信息",
        "",
    ]
    
    # Add current time if available
    # Support dynamic time via callable function
    if callable(runtime_info.get("_get_current_time")):
        try:
            time_info = runtime_info["_get_current_time"]()
            time_line = f"当前时间: {time_info['time']} {time_info['weekday']} ({time_info['timezone']})"
            lines.append(time_line)
            lines.append("")
        except Exception as e:
            logger.warning(f"[PromptBuilder] Failed to get dynamic time: {e}")
    elif runtime_info.get("current_time"):
        # Fallback to static time for backward compatibility
        time_str = runtime_info["current_time"]
        weekday = runtime_info.get("weekday", "")
        timezone = runtime_info.get("timezone", "")
        
        time_line = f"当前时间: {time_str}"
        if weekday:
            time_line += f" {weekday}"
        if timezone:
            time_line += f" ({timezone})"
        
        lines.append(time_line)
        lines.append("")
    
    # Add other runtime info
    runtime_parts = []
    # Support dynamic model via callable, fallback to static value
    if callable(runtime_info.get("_get_model")):
        try:
            runtime_parts.append(f"模型={runtime_info['_get_model']()}")
        except Exception:
            if runtime_info.get("model"):
                runtime_parts.append(f"模型={runtime_info['model']}")
    elif runtime_info.get("model"):
        runtime_parts.append(f"模型={runtime_info['model']}")
    if runtime_info.get("workspace"):
        runtime_parts.append(f"工作空间={runtime_info['workspace']}")
    # Only add channel if it's not the default "web"
    if runtime_info.get("channel") and runtime_info.get("channel") != "web":
        runtime_parts.append(f"渠道={runtime_info['channel']}")
    
    if runtime_parts:
        lines.append("运行时: " + " | ".join(runtime_parts))
        lines.append("")
    
    return lines
