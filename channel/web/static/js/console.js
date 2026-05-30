/* =====================================================================
   ZVAgent Console - Main Application Script
   ===================================================================== */

// =====================================================================
// Version - displayed in the sidebar footer
// =====================================================================
let APP_VERSION = '';

// =====================================================================
// i18n
// =====================================================================
const I18N = {
    "zh": {
        "console": "????",
        "nav_chat": "???",
        "nav_manage": "??",
        "nav_monitor": "??",
        "menu_chat": "????",
        "menu_config": "????",
        "menu_skills": "???",
        "menu_evolution": "????",
        "menu_quota": "??",
        "menu_memory": "????",
        "menu_knowledge": "?????",
        "menu_reports": "????",
        "menu_channels": "????",
        "menu_tasks": "????",
        "menu_logs": "????",
        "knowledge_title": "???",
        "knowledge_desc": "??????????",
        "knowledge_tab_docs": "??",
        "knowledge_tab_graph": "??",
        "knowledge_loading": "??????...",
        "knowledge_loading_desc": "??????????",
        "knowledge_select_hint": "????????",
        "knowledge_empty_hint": "??????",
        "knowledge_empty_guide": "??????????????? Agent???????????????",
        "knowledge_go_chat": "????",
        "welcome_subtitle": "?? AI ???????????????????????<br>???????????????????????",
        "example_sys_title": "AI ????",
        "example_sys_text": "???? AI ??????????????????",
        "example_task_title": "????",
        "example_task_text": "? research-assistant ??????????????????",
        "example_code_title": "????",
        "example_code_text": "??????????????????????????",
        "example_knowledge_title": "????",
        "example_knowledge_text": "?????????????????????",
        "example_skill_title": "Crypto ??",
        "example_skill_text": "??????????????? AI x Crypto ?????",
        "example_web_title": "????",
        "example_web_text": "?????? AI ?????????",
        "input_placeholder": "????????????????? / ??",
        "config_title": "????",
        "config_desc": "????? Agent ??",
        "config_model": "????",
        "config_agent": "Agent ??",
        "config_channel": "????",
        "config_agent_enabled": "Agent ??",
        "config_max_tokens": "????? Token",
        "config_max_tokens_hint": "??? Agent ?????? Token ?????????????",
        "config_max_turns": "??????",
        "config_max_turns_hint": "??????????????????",
        "config_max_steps": "??????",
        "config_max_steps_hint": "????? Agent ?????????",
        "config_enable_thinking": "????",
        "config_enable_thinking_hint": "??????????",
        "config_channel_type": "????",
        "config_provider": "????",
        "config_model_name": "??",
        "config_custom_model_hint": "?????????",
        "config_save": "??",
        "config_saved": "???",
        "config_save_error": "????",
        "config_custom_option": "???...",
        "config_custom_tip": "????? OpenAI API ???",
        "config_security": "????",
        "config_password": "????",
        "config_password_hint": "??????????",
        "config_password_changed": "???????????",
        "config_password_cleared": "?????",
        "skills_title": "????",
        "skills_desc": "???????? Agent ?????",
        "skills_hub_btn": "??????",
        "evolution_title": "????",
        "evolution_desc": "??????????????????",
        "skills_loading": "?????...",
        "skills_loading_desc": "???????????",
        "tools_section_title": "????",
        "tools_loading": "?????...",
        "skills_section_title": "??",
        "skill_enable": "??",
        "skill_disable": "??",
        "skill_toggle_error": "??????????",
        "memory_title": "????",
        "memory_desc": "?? Agent ???????",
        "memory_tab_files": "????",
        "memory_tab_dreams": "????",
        "memory_loading": "???????...",
        "memory_loading_desc": "??????????",
        "memory_back": "????",
        "memory_col_name": "???",
        "memory_col_type": "??",
        "memory_col_size": "??",
        "memory_col_updated": "????",
        "channels_title": "????",
        "channels_desc": "??????????",
        "channels_add": "????",
        "channels_disconnect": "??",
        "channels_save": "????",
        "channels_saved": "???",
        "channels_save_error": "????",
        "channels_restarted": "??????",
        "channels_connect_btn": "??",
        "channels_cancel": "??",
        "channels_select_placeholder": "????????...",
        "channels_empty": "????????",
        "channels_empty_desc": "?????????????????",
        "channels_disconnect_confirm": "??????????????????????",
        "channels_connected": "???",
        "channels_connecting": "???...",
        "weixin_scan_title": "??????",
        "weixin_scan_desc": "????????????",
        "weixin_scan_loading": "???????...",
        "weixin_scan_waiting": "????...",
        "weixin_scan_scanned": "???????????",
        "weixin_scan_expired": "???????????...",
        "weixin_scan_success": "???????????...",
        "weixin_scan_fail": "???????",
        "weixin_qr_tip": "???? 2 ?????",
        "wecom_scan_btn": "?????????",
        "wecom_scan_desc": "??????????????????",
        "wecom_scan_success": "???????????...",
        "wecom_scan_fail": "????",
        "wecom_mode_scan": "????",
        "wecom_mode_manual": "????",
        "feishu_scan_btn": "????????",
        "feishu_scan_desc": "???? App ??????????????",
        "feishu_scan_replace_desc": "???? App ?????????????? App ID / Secret",
        "feishu_scan_loading": "??????????...",
        "feishu_scan_waiting": "????...",
        "feishu_scan_tip": "??? 10 ????????????",
        "feishu_scan_open_link": "????????????",
        "feishu_scan_success": "?????????????...",
        "feishu_scan_expired": "??????????",
        "feishu_scan_denied": "?????",
        "feishu_scan_fail": "????",
        "feishu_scan_retry": "??",
        "feishu_mode_scan": "????",
        "feishu_mode_manual": "????",
        "tasks_title": "????",
        "tasks_desc": "?????????",
        "tasks_coming": "????",
        "tasks_coming_desc": "??????????????",
        "logs_title": "??",
        "logs_desc": "?????? (run.log)",
        "logs_live": "??",
        "logs_coming_msg": "????????????? run.log ???? tail -f ??????",
        "quota_title": "????",
        "quota_desc": "????? Token ??????????????",
        "new_chat": "???",
        "session_history": "????",
        "today": "??",
        "yesterday": "??",
        "earlier": "??",
        "delete_session_confirm": "?????????????????",
        "delete_session_title": "????",
        "untitled_session": "???",
        "context_cleared": "????????????",
        "tip_new_chat": "????",
        "tip_clear_context": "?????",
        "tip_attach_file": "????",
        "confirm_yes": "??",
        "confirm_cancel": "??",
        "error_send": "???????????",
        "error_timeout": "???????????",
        "thinking_in_progress": "???...",
        "thinking_done": "?????",
        "thinking_duration": "??"
    },
    "en": {
        "console": "Research Desk",
        "nav_chat": "Desk",
        "nav_manage": "Resources",
        "nav_monitor": "System",
        "menu_chat": "Intel Chat",
        "menu_config": "Model Settings",
        "menu_skills": "Capability Library",
        "menu_evolution": "Skill Evolution",
        "menu_quota": "Quota",
        "menu_memory": "Long-term Memory",
        "menu_knowledge": "Research Knowledge",
        "menu_reports": "Reports",
        "menu_channels": "Channels",
        "menu_tasks": "Reminders",
        "menu_logs": "Runtime Logs",
        "knowledge_title": "???",
        "knowledge_desc": "??????????",
        "knowledge_tab_docs": "??",
        "knowledge_tab_graph": "??",
        "knowledge_loading": "??????...",
        "knowledge_loading_desc": "??????????",
        "knowledge_select_hint": "????????",
        "knowledge_empty_hint": "??????",
        "knowledge_empty_guide": "??????????????? Agent???????????????",
        "knowledge_go_chat": "????",
        "welcome_subtitle": "?? AI ???????????????????????<br>???????????????????????",
        "example_sys_title": "AI ????",
        "example_sys_text": "???? AI ??????????????????",
        "example_task_title": "????",
        "example_task_text": "? research-assistant ??????????????????",
        "example_code_title": "????",
        "example_code_text": "??????????????????????????",
        "example_knowledge_title": "????",
        "example_knowledge_text": "?????????????????????",
        "example_skill_title": "Crypto ??",
        "example_skill_text": "??????????????? AI x Crypto ?????",
        "example_web_title": "????",
        "example_web_text": "?????? AI ?????????",
        "input_placeholder": "????????????????? / ??",
        "config_title": "????",
        "config_desc": "????? Agent ??",
        "config_model": "????",
        "config_agent": "Agent ??",
        "config_channel": "????",
        "config_agent_enabled": "Agent ??",
        "config_max_tokens": "????? Token",
        "config_max_tokens_hint": "??? Agent ?????? Token ?????????????",
        "config_max_turns": "??????",
        "config_max_turns_hint": "??????????????????",
        "config_max_steps": "??????",
        "config_max_steps_hint": "????? Agent ?????????",
        "config_enable_thinking": "????",
        "config_enable_thinking_hint": "??????????",
        "config_channel_type": "????",
        "config_provider": "????",
        "config_model_name": "??",
        "config_custom_model_hint": "?????????",
        "config_save": "??",
        "config_saved": "???",
        "config_save_error": "????",
        "config_custom_option": "???...",
        "config_custom_tip": "????? OpenAI API ???",
        "config_security": "????",
        "config_password": "????",
        "config_password_hint": "??????????",
        "config_password_changed": "???????????",
        "config_password_cleared": "?????",
        "skills_title": "????",
        "skills_desc": "???????? Agent ?????",
        "skills_hub_btn": "??????",
        "evolution_title": "????",
        "evolution_desc": "??????????????????",
        "skills_loading": "?????...",
        "skills_loading_desc": "???????????",
        "tools_section_title": "????",
        "tools_loading": "?????...",
        "skills_section_title": "??",
        "skill_enable": "??",
        "skill_disable": "??",
        "skill_toggle_error": "??????????",
        "memory_title": "????",
        "memory_desc": "?? Agent ???????",
        "memory_tab_files": "????",
        "memory_tab_dreams": "????",
        "memory_loading": "???????...",
        "memory_loading_desc": "??????????",
        "memory_back": "????",
        "memory_col_name": "???",
        "memory_col_type": "??",
        "memory_col_size": "??",
        "memory_col_updated": "????",
        "channels_title": "????",
        "channels_desc": "??????????",
        "channels_add": "????",
        "channels_disconnect": "??",
        "channels_save": "????",
        "channels_saved": "???",
        "channels_save_error": "????",
        "channels_restarted": "??????",
        "channels_connect_btn": "??",
        "channels_cancel": "??",
        "channels_select_placeholder": "????????...",
        "channels_empty": "????????",
        "channels_empty_desc": "?????????????????",
        "channels_disconnect_confirm": "??????????????????????",
        "channels_connected": "???",
        "channels_connecting": "???...",
        "weixin_scan_title": "??????",
        "weixin_scan_desc": "????????????",
        "weixin_scan_loading": "???????...",
        "weixin_scan_waiting": "????...",
        "weixin_scan_scanned": "???????????",
        "weixin_scan_expired": "???????????...",
        "weixin_scan_success": "???????????...",
        "weixin_scan_fail": "???????",
        "weixin_qr_tip": "???? 2 ?????",
        "wecom_scan_btn": "?????????",
        "wecom_scan_desc": "??????????????????",
        "wecom_scan_success": "???????????...",
        "wecom_scan_fail": "????",
        "wecom_mode_scan": "????",
        "wecom_mode_manual": "????",
        "feishu_scan_btn": "????????",
        "feishu_scan_desc": "???? App ??????????????",
        "feishu_scan_replace_desc": "???? App ?????????????? App ID / Secret",
        "feishu_scan_loading": "??????????...",
        "feishu_scan_waiting": "????...",
        "feishu_scan_tip": "??? 10 ????????????",
        "feishu_scan_open_link": "????????????",
        "feishu_scan_success": "?????????????...",
        "feishu_scan_expired": "??????????",
        "feishu_scan_denied": "?????",
        "feishu_scan_fail": "????",
        "feishu_scan_retry": "??",
        "feishu_mode_scan": "????",
        "feishu_mode_manual": "????",
        "tasks_title": "????",
        "tasks_desc": "?????????",
        "tasks_coming": "????",
        "tasks_coming_desc": "??????????????",
        "logs_title": "??",
        "logs_desc": "?????? (run.log)",
        "logs_live": "??",
        "logs_coming_msg": "????????????? run.log ???? tail -f ??????",
        "quota_title": "????",
        "quota_desc": "????? Token ??????????????",
        "new_chat": "???",
        "session_history": "????",
        "today": "??",
        "yesterday": "??",
        "earlier": "??",
        "delete_session_confirm": "?????????????????",
        "delete_session_title": "????",
        "untitled_session": "???",
        "context_cleared": "????????????",
        "tip_new_chat": "????",
        "tip_clear_context": "?????",
        "tip_attach_file": "????",
        "confirm_yes": "??",
        "confirm_cancel": "??",
        "error_send": "???????????",
        "error_timeout": "???????????",
        "thinking_in_progress": "???...",
        "thinking_done": "?????",
        "thinking_duration": "??"
    }
};

I18N.zh = Object.assign(I18N.zh, {
    "console": "\u7814\u7a76\u7ec8\u7aef",
    "nav_chat": "\u7814\u7a76\u53f0",
    "nav_manage": "\u8d44\u6e90",
    "nav_monitor": "\u7cfb\u7edf",
    "menu_chat": "\u60c5\u62a5\u5bf9\u8bdd",
    "menu_config": "\u6a21\u578b\u8bbe\u7f6e",
    "menu_skills": "\u80fd\u529b\u5e93",
    "menu_evolution": "\u80fd\u529b\u8fdb\u5316",
    "menu_quota": "\u989d\u5ea6",
    "menu_memory": "\u957f\u671f\u8bb0\u5fc6",
    "menu_knowledge": "\u7814\u7a76\u77e5\u8bc6\u5e93",
    "menu_reports": "\u62a5\u544a",
    "menu_channels": "\u63a5\u5165\u901a\u9053",
    "menu_tasks": "\u4efb\u52a1\u63d0\u9192",
    "menu_logs": "\u8fd0\u884c\u65e5\u5fd7",
    "session_history": "\u5386\u53f2\u4f1a\u8bdd",
    "new_chat": "\u65b0\u5bf9\u8bdd",
    "config_title": "\u914d\u7f6e\u7ba1\u7406",
    "config_desc": "\u7ba1\u7406\u6a21\u578b\u548c Agent \u914d\u7f6e",
    "config_model": "\u6a21\u578b\u914d\u7f6e",
    "config_agent": "Agent \u914d\u7f6e",
    "config_provider": "\u6a21\u578b\u5382\u5546",
    "config_model_name": "\u6a21\u578b",
    "config_agent_enabled": "Agent \u6a21\u5f0f",
    "config_max_tokens": "\u6700\u5927\u4e0a\u4e0b\u6587 Token",
    "config_max_turns": "\u6700\u5927\u8bb0\u5fc6\u8f6e\u6b21",
    "config_max_steps": "\u6700\u5927\u6267\u884c\u6b65\u6570",
    "config_enable_thinking": "\u6df1\u5ea6\u601d\u8003",
    "config_save": "\u4fdd\u5b58",
    "config_security": "\u5b89\u5168\u8bbe\u7f6e",
    "config_password": "\u8bbf\u95ee\u5bc6\u7801",
    "config_password_hint": "\u7559\u7a7a\u5219\u4e0d\u542f\u7528\u5bc6\u7801\u4fdd\u62a4",
    "skills_title": "\u6280\u80fd\u7ba1\u7406",
    "skills_desc": "\u67e5\u770b\u3001\u542f\u7528\u6216\u7981\u7528 Agent \u6280\u80fd",
    "skills_hub_btn": "\u63a2\u7d22\u6280\u80fd\u5e7f\u573a",
    "tools_section_title": "\u5185\u7f6e\u5de5\u5177",
    "tools_loading": "\u52a0\u8f7d\u5de5\u5177\u4e2d...",
    "skills_section_title": "\u6280\u80fd",
    "skills_loading": "\u52a0\u8f7d\u6280\u80fd\u4e2d...",
    "skills_loading_desc": "\u6280\u80fd\u52a0\u8f7d\u540e\u5c06\u663e\u793a\u5728\u6b64\u5904",
    "memory_title": "\u8bb0\u5fc6\u7ba1\u7406",
    "memory_desc": "\u67e5\u770b Agent \u8bb0\u5fc6\u6587\u4ef6\u548c\u5185\u5bb9",
    "memory_tab_files": "\u8bb0\u5fc6\u6587\u4ef6",
    "memory_tab_dreams": "\u68a6\u5883\u65e5\u8bb0",
    "memory_loading": "\u52a0\u8f7d\u8bb0\u5fc6\u6587\u4ef6\u4e2d...",
    "memory_loading_desc": "\u8bb0\u5fc6\u6587\u4ef6\u5c06\u663e\u793a\u5728\u6b64\u5904",
    "memory_col_name": "\u6587\u4ef6\u540d",
    "memory_col_type": "\u7c7b\u578b",
    "memory_col_size": "\u5927\u5c0f",
    "memory_col_updated": "\u66f4\u65b0\u65f6\u95f4",
    "memory_back": "\u8fd4\u56de\u5217\u8868",
    "knowledge_title": "\u77e5\u8bc6\u5e93",
    "knowledge_desc": "\u6d4f\u89c8\u548c\u63a2\u7d22\u4f60\u7684\u77e5\u8bc6\u5e93",
    "knowledge_tab_docs": "\u6587\u6863",
    "knowledge_tab_graph": "\u56fe\u8c31",
    "knowledge_loading": "\u52a0\u8f7d\u77e5\u8bc6\u5e93\u4e2d...",
    "knowledge_loading_desc": "\u77e5\u8bc6\u9875\u9762\u5c06\u663e\u793a\u5728\u8fd9\u91cc",
    "knowledge_empty_guide": "\u5728\u5bf9\u8bdd\u4e2d\u53d1\u9001\u6587\u6863\u3001\u94fe\u63a5\u6216\u4e3b\u9898\u7ed9 Agent\uff0c\u5b83\u4f1a\u81ea\u52a8\u6574\u7406\u5230\u4f60\u7684\u77e5\u8bc6\u5e93\u4e2d\u3002",
    "knowledge_go_chat": "\u5f00\u59cb\u5bf9\u8bdd",
    "knowledge_select_hint": "\u9009\u62e9\u4e00\u4e2a\u6587\u6863\u67e5\u770b",
    "channels_title": "\u901a\u9053\u7ba1\u7406",
    "channels_desc": "\u7ba1\u7406\u5df2\u63a5\u5165\u7684\u6d88\u606f\u901a\u9053",
    "channels_add": "\u63a5\u5165\u901a\u9053",
    "tasks_title": "\u5b9a\u65f6\u4efb\u52a1",
    "tasks_desc": "\u67e5\u770b\u548c\u7ba1\u7406\u5b9a\u65f6\u4efb\u52a1",
    "logs_title": "\u65e5\u5fd7",
    "logs_desc": "\u5b9e\u65f6\u65e5\u5fd7\u8f93\u51fa (run.log)",
    "logs_live": "\u5b9e\u65f6",
    "logs_coming_msg": "\u65e5\u5fd7\u6d41\u5373\u5c06\u5728\u6b64\u63d0\u4f9b\u3002\u5c06\u8fde\u63a5 run.log \u5b9e\u73b0\u7c7b\u4f3c tail -f \u7684\u5b9e\u65f6\u8f93\u51fa\u3002",
    "input_placeholder": "\u8f93\u5165\u7814\u7a76\u95ee\u9898\u3001\u8bba\u6587\u94fe\u63a5\u3001\u4ee3\u7801\u4ed3\u5e93\u6216 / \u547d\u4ee4",
    "welcome_subtitle": "\u9762\u5411 AI \u6280\u672f\u3001\u5b66\u672f\u8bba\u6587\u4e0e\u52a0\u5bc6\u8d27\u5e01\u7684\u4e2a\u4eba\u7814\u7a76\u60c5\u62a5\u5de5\u4f5c\u53f0\u3002<br>\u628a\u4fe1\u606f\u83b7\u53d6\u3001\u7406\u89e3\u3001\u5224\u65ad\u548c\u6c89\u6dc0\u653e\u5728\u540c\u4e00\u4e2a\u754c\u9762\u91cc\u3002"
});

I18N.zh = Object.assign(I18N.zh, {
    "console": "控制台",
    "nav_chat": "对话",
    "nav_manage": "管理",
    "nav_monitor": "监控",
    "menu_chat": "对话",
    "menu_config": "配置",
    "menu_skills": "技能",
    "menu_evolution": "技能进化",
    "menu_quota": "额度",
    "menu_memory": "记忆",
    "menu_knowledge": "知识",
    "menu_reports": "报告",
    "menu_channels": "通道",
    "menu_tasks": "定时",
    "menu_logs": "日志",
    "welcome_subtitle": "我可以帮你解答问题、管理计算机、创造和执行技能，并通过<br>长期记忆和知识库不断成长",
    "example_sys_title": "系统管理",
    "example_sys_text": "查看工作空间里有哪些文件",
    "example_task_title": "定时任务",
    "example_task_text": "1分钟后提醒我检查服务器",
    "example_code_title": "编程助手",
    "example_code_text": "搜索 AI 资讯并生成可视化网页报告",
    "example_knowledge_title": "知识库",
    "example_knowledge_text": "查看知识库当前文档情况",
    "example_skill_title": "技能系统",
    "example_skill_text": "查看所有支持的工具和技能",
    "example_web_title": "指令中心",
    "example_web_text": "查看全部命令",
    "input_placeholder": "输入消息，或使用 / 命令",
    "config_title": "配置管理",
    "config_desc": "管理模型和 Agent 配置",
    "config_model": "模型配置",
    "config_agent": "Agent 配置",
    "config_channel": "通道配置",
    "config_agent_enabled": "Agent 模式",
    "config_max_tokens": "最大上下文 Token",
    "config_max_tokens_hint": "设置 Agent 可使用的最大上下文 Token 数量",
    "config_max_turns": "最大记忆轮次",
    "config_max_turns_hint": "设置对话中保留的历史轮次数量",
    "config_max_steps": "最大执行步数",
    "config_max_steps_hint": "限制 Agent 单次任务的最大执行步数",
    "config_enable_thinking": "深度思考",
    "config_enable_thinking_hint": "启用后模型会进行更充分的推理",
    "config_channel_type": "通道类型",
    "config_provider": "模型厂商",
    "config_model_name": "模型",
    "config_custom_model_hint": "输入自定义模型名称",
    "config_save": "保存",
    "config_saved": "已保存",
    "config_save_error": "保存失败",
    "config_custom_option": "自定义...",
    "config_custom_tip": "接口需遵循 OpenAI API 协议",
    "config_security": "安全设置",
    "config_password": "访问密码",
    "config_password_hint": "留空则不启用密码保护",
    "config_password_changed": "访问密码已更新",
    "config_password_cleared": "访问密码已清除",
    "skills_title": "技能管理",
    "skills_desc": "查看、启用或禁用 Agent 技能",
    "skills_hub_btn": "探索技能广场",
    "evolution_title": "技能进化",
    "evolution_desc": "查看和管理技能自动进化记录",
    "skills_loading": "加载技能中...",
    "skills_loading_desc": "技能加载后将显示在此处",
    "tools_section_title": "内置工具",
    "tools_loading": "加载工具中...",
    "skills_section_title": "技能",
    "skill_enable": "启用",
    "skill_disable": "禁用",
    "skill_toggle_error": "切换技能状态失败",
    "memory_title": "记忆管理",
    "memory_desc": "查看 Agent 记忆文件和内容",
    "memory_tab_files": "记忆文件",
    "memory_tab_dreams": "梦境日记",
    "memory_loading": "加载记忆文件中...",
    "memory_loading_desc": "记忆文件将显示在此处",
    "memory_back": "返回列表",
    "memory_col_name": "文件名",
    "memory_col_type": "类型",
    "memory_col_size": "大小",
    "memory_col_updated": "更新时间",
    "knowledge_title": "知识库",
    "knowledge_desc": "浏览和探索你的知识库",
    "knowledge_tab_docs": "文档",
    "knowledge_tab_graph": "图谱",
    "knowledge_loading": "加载知识库中...",
    "knowledge_loading_desc": "知识页面将显示在这里",
    "knowledge_select_hint": "选择一个文档查看",
    "knowledge_empty_hint": "暂无知识库内容",
    "knowledge_empty_guide": "在对话中发送文档、链接或主题给 Agent，它会自动整理到你的知识库中。",
    "knowledge_go_chat": "开始对话",
    "channels_title": "通道管理",
    "channels_desc": "管理已接入的消息通道",
    "channels_add": "接入通道",
    "channels_disconnect": "断开",
    "channels_save": "保存配置",
    "channels_saved": "已保存",
    "channels_save_error": "保存失败",
    "channels_restarted": "通道已重启",
    "channels_connect_btn": "连接",
    "channels_cancel": "取消",
    "channels_select_placeholder": "请选择通道...",
    "channels_empty": "暂无接入通道",
    "channels_empty_desc": "添加一个通道后即可在这里管理",
    "channels_disconnect_confirm": "确定要断开这个通道吗？",
    "channels_connected": "已连接",
    "channels_connecting": "连接中...",
    "weixin_scan_title": "微信扫码登录",
    "weixin_scan_desc": "请使用微信扫描二维码",
    "weixin_scan_loading": "正在获取二维码...",
    "weixin_scan_waiting": "等待扫码...",
    "weixin_scan_scanned": "已扫码，请在手机上确认",
    "weixin_scan_expired": "二维码已过期，正在刷新...",
    "weixin_scan_success": "登录成功，正在连接...",
    "weixin_scan_fail": "扫码登录失败",
    "weixin_qr_tip": "二维码约 2 分钟内有效",
    "wecom_scan_btn": "企业微信扫码登录",
    "wecom_scan_desc": "请使用企业微信扫描二维码",
    "wecom_scan_success": "登录成功，正在连接...",
    "wecom_scan_fail": "连接失败",
    "wecom_mode_scan": "扫码",
    "wecom_mode_manual": "手动",
    "feishu_scan_btn": "飞书扫码登录",
    "feishu_scan_desc": "请使用飞书 App 扫码完成授权",
    "feishu_scan_replace_desc": "请使用飞书 App 扫码，或填写 App ID / Secret",
    "feishu_scan_loading": "正在获取授权二维码...",
    "feishu_scan_waiting": "等待扫码...",
    "feishu_scan_tip": "授权链接约 10 分钟内有效",
    "feishu_scan_open_link": "打开授权链接",
    "feishu_scan_success": "授权成功，正在连接...",
    "feishu_scan_expired": "授权已过期",
    "feishu_scan_denied": "授权被取消",
    "feishu_scan_fail": "授权失败",
    "feishu_scan_retry": "重试",
    "feishu_mode_scan": "扫码",
    "feishu_mode_manual": "手动",
    "tasks_title": "定时任务",
    "tasks_desc": "查看和管理定时任务",
    "tasks_coming": "即将推出",
    "tasks_coming_desc": "定时任务管理功能正在开发中",
    "logs_title": "日志",
    "logs_desc": "实时日志输出 (run.log)",
    "logs_live": "实时",
    "logs_coming_msg": "日志流即将在此提供。将连接 run.log 实现类似 tail -f 的实时输出。",
    "quota_title": "额度管理",
    "quota_desc": "查看 Token 使用量和额度状态",
    "new_chat": "新对话",
    "session_history": "历史会话",
    "today": "今天",
    "yesterday": "昨天",
    "earlier": "更早",
    "delete_session_confirm": "确定要删除这个会话吗？",
    "delete_session_title": "删除会话",
    "delete_turn_confirm": "确定要删除这一轮对话及其生成的文件吗？",
    "delete_turn_title": "删除消息",
    "untitled_session": "未命名会话",
    "context_cleared": "上下文已清空",
    "tip_new_chat": "新对话",
    "tip_clear_context": "清空上下文",
    "tip_attach_file": "添加附件",
    "tip_cancel_request": "取消本次指令",
    "tip_edit_message": "编辑并重新发送",
    "request_cancelled": "已取消本次指令",
    "confirm_yes": "确定",
    "confirm_cancel": "取消",
    "error_send": "发送失败，请稍后重试",
    "error_timeout": "请求超时，请稍后重试",
    "thinking_in_progress": "思考中...",
    "thinking_done": "思考完成",
    "thinking_duration": "用时"
});

I18N.en = Object.assign(I18N.en, {
    "console": "Console",
    "nav_chat": "Chat",
    "nav_manage": "Manage",
    "nav_monitor": "Monitor",
    "menu_chat": "Chat",
    "menu_config": "Config",
    "menu_skills": "Skills",
    "menu_evolution": "Skill Evolution",
    "menu_quota": "Quota",
    "menu_memory": "Memory",
    "menu_knowledge": "Knowledge",
    "menu_reports": "Reports",
    "menu_channels": "Channels",
    "menu_tasks": "Schedules",
    "menu_logs": "Logs",
    "welcome_subtitle": "I can help answer questions, manage your computer, create and run skills,<br>and keep growing through long-term memory and the knowledge base.",
    "example_sys_title": "System",
    "example_sys_text": "Show me what files are in the workspace",
    "example_task_title": "Schedule",
    "example_task_text": "Remind me to check the server in 1 minute",
    "example_code_title": "Coding",
    "example_code_text": "Search AI news and generate a visual web report",
    "example_knowledge_title": "Knowledge",
    "example_knowledge_text": "Show the current knowledge base documents",
    "example_skill_title": "Skills",
    "example_skill_text": "Show all supported tools and skills",
    "example_web_title": "Commands",
    "example_web_text": "Show all commands",
    "input_placeholder": "Type a message, or use / commands",
    "config_title": "Config",
    "config_desc": "Manage model and Agent settings",
    "config_model": "Model Config",
    "config_agent": "Agent Config",
    "config_channel": "Channel Config",
    "config_agent_enabled": "Agent Mode",
    "config_max_tokens": "Max Context Tokens",
    "config_max_tokens_hint": "Set the maximum context tokens available to the Agent",
    "config_max_turns": "Max Memory Turns",
    "config_max_turns_hint": "Set how many history turns to keep in conversation",
    "config_max_steps": "Max Steps",
    "config_max_steps_hint": "Limit the maximum execution steps for one Agent task",
    "config_enable_thinking": "Deep Thinking",
    "config_enable_thinking_hint": "Allow the model to reason more thoroughly",
    "config_channel_type": "Channel Type",
    "config_provider": "Provider",
    "config_model_name": "Model",
    "config_custom_model_hint": "Enter a custom model name",
    "config_save": "Save",
    "config_saved": "Saved",
    "config_save_error": "Save failed",
    "config_custom_option": "Custom...",
    "config_custom_tip": "The endpoint must follow the OpenAI API protocol",
    "config_security": "Security",
    "config_password": "Access Password",
    "config_password_hint": "Leave empty to disable password protection",
    "config_password_changed": "Password updated",
    "config_password_cleared": "Password cleared",
    "skills_title": "Skills",
    "skills_desc": "View, enable, or disable Agent skills",
    "skills_hub_btn": "Explore Skill Hub",
    "evolution_title": "Skill Evolution",
    "evolution_desc": "View and manage automatic skill evolution records",
    "skills_loading": "Loading skills...",
    "skills_loading_desc": "Skills will appear here after loading",
    "tools_section_title": "Built-in Tools",
    "tools_loading": "Loading tools...",
    "skills_section_title": "Skills",
    "skill_enable": "Enable",
    "skill_disable": "Disable",
    "skill_toggle_error": "Failed to change skill status",
    "memory_title": "Memory",
    "memory_desc": "View Agent memory files and content",
    "memory_tab_files": "Memory Files",
    "memory_tab_dreams": "Dream Journal",
    "memory_loading": "Loading memory files...",
    "memory_loading_desc": "Memory files will appear here",
    "memory_back": "Back to List",
    "memory_col_name": "Name",
    "memory_col_type": "Type",
    "memory_col_size": "Size",
    "memory_col_updated": "Updated",
    "knowledge_title": "Knowledge Base",
    "knowledge_desc": "Browse and explore your knowledge base",
    "knowledge_tab_docs": "Docs",
    "knowledge_tab_graph": "Graph",
    "knowledge_loading": "Loading knowledge base...",
    "knowledge_loading_desc": "Knowledge content will appear here",
    "knowledge_select_hint": "Select a document to view",
    "knowledge_empty_hint": "No knowledge content yet",
    "knowledge_empty_guide": "Send documents, links, or topics to the Agent in chat and it will organize them into your knowledge base.",
    "knowledge_go_chat": "Start Chat",
    "channels_title": "Channels",
    "channels_desc": "Manage connected message channels",
    "channels_add": "Add Channel",
    "channels_disconnect": "Disconnect",
    "channels_save": "Save Config",
    "channels_saved": "Saved",
    "channels_save_error": "Save failed",
    "channels_restarted": "Channel restarted",
    "channels_connect_btn": "Connect",
    "channels_cancel": "Cancel",
    "channels_select_placeholder": "Select a channel...",
    "channels_empty": "No channels connected",
    "channels_empty_desc": "Add a channel to manage it here",
    "channels_disconnect_confirm": "Disconnect this channel?",
    "channels_connected": "Connected",
    "channels_connecting": "Connecting...",
    "weixin_scan_title": "WeChat QR Login",
    "weixin_scan_desc": "Scan the QR code with WeChat",
    "weixin_scan_loading": "Loading QR code...",
    "weixin_scan_waiting": "Waiting for scan...",
    "weixin_scan_scanned": "Scanned, confirm on your phone",
    "weixin_scan_expired": "QR code expired, refreshing...",
    "weixin_scan_success": "Login succeeded, connecting...",
    "weixin_scan_fail": "QR login failed",
    "weixin_qr_tip": "The QR code is valid for about 2 minutes",
    "wecom_scan_btn": "WeCom QR Login",
    "wecom_scan_desc": "Scan the QR code with WeCom",
    "wecom_scan_success": "Login succeeded, connecting...",
    "wecom_scan_fail": "Connection failed",
    "wecom_mode_scan": "Scan",
    "wecom_mode_manual": "Manual",
    "feishu_scan_btn": "Feishu QR Login",
    "feishu_scan_desc": "Scan with the Feishu app to authorize",
    "feishu_scan_replace_desc": "Scan with the Feishu app, or enter App ID / Secret",
    "feishu_scan_loading": "Loading authorization QR...",
    "feishu_scan_waiting": "Waiting for scan...",
    "feishu_scan_tip": "Authorization link is valid for about 10 minutes",
    "feishu_scan_open_link": "Open authorization link",
    "feishu_scan_success": "Authorization succeeded, connecting...",
    "feishu_scan_expired": "Authorization expired",
    "feishu_scan_denied": "Authorization canceled",
    "feishu_scan_fail": "Authorization failed",
    "feishu_scan_retry": "Retry",
    "feishu_mode_scan": "Scan",
    "feishu_mode_manual": "Manual",
    "tasks_title": "Schedules",
    "tasks_desc": "View and manage scheduled tasks",
    "tasks_coming": "Coming Soon",
    "tasks_coming_desc": "Scheduled task management is under development",
    "logs_title": "Logs",
    "logs_desc": "Live log output (run.log)",
    "logs_live": "Live",
    "logs_coming_msg": "Log streaming will be available here. It will connect to run.log for tail -f style live output.",
    "quota_title": "Quota",
    "quota_desc": "View token usage and quota status",
    "new_chat": "New Chat",
    "session_history": "Chat History",
    "today": "Today",
    "yesterday": "Yesterday",
    "earlier": "Earlier",
    "delete_session_confirm": "Delete this session?",
    "delete_session_title": "Delete Session",
    "delete_turn_confirm": "Delete this message pair and generated files?",
    "delete_turn_title": "Delete Message",
    "untitled_session": "Untitled Session",
    "context_cleared": "Context cleared",
    "tip_new_chat": "New chat",
    "tip_clear_context": "Clear context",
    "tip_attach_file": "Attach file",
    "tip_cancel_request": "Cancel this request",
    "tip_edit_message": "Edit and resend",
    "request_cancelled": "Request cancelled",
    "confirm_yes": "Confirm",
    "confirm_cancel": "Cancel",
    "error_send": "Failed to send, please try again",
    "error_timeout": "Request timed out, please try again",
    "thinking_in_progress": "Thinking...",
    "thinking_done": "Thinking complete",
    "thinking_duration": "Duration"
});

I18N.zh = Object.assign(I18N.zh, {
    "console": "控制台",
    "nav_chat": "对话",
    "nav_manage": "管理",
    "nav_monitor": "监控",
    "menu_chat": "对话",
    "menu_config": "配置",
    "menu_skills": "技能",
    "menu_evolution": "技能进化",
    "menu_quota": "额度",
    "menu_memory": "记忆",
    "menu_knowledge": "知识",
    "menu_reports": "报告",
    "menu_channels": "通道",
    "menu_tasks": "定时",
    "menu_logs": "日志",
    "welcome_subtitle": "我可以帮你解答问题、管理计算机、创造和执行技能，并通过<br>长期记忆和知识库不断成长",
    "example_sys_title": "系统管理",
    "example_sys_text": "查看工作空间里有哪些文件",
    "example_task_title": "定时任务",
    "example_task_text": "1分钟后提醒我检查服务器",
    "example_code_title": "编程助手",
    "example_code_text": "搜索 AI 资讯并生成可视化网页报告",
    "example_knowledge_title": "知识库",
    "example_knowledge_text": "查看知识库当前文档情况",
    "example_skill_title": "技能系统",
    "example_skill_text": "查看所有支持的工具和技能",
    "example_web_title": "指令中心",
    "example_web_text": "查看全部命令",
    "input_placeholder": "输入消息，或使用 / 命令",
    "config_title": "配置管理",
    "config_desc": "管理模型和 Agent 配置",
    "config_model": "模型配置",
    "config_agent": "Agent 配置",
    "config_channel": "通道配置",
    "config_agent_enabled": "Agent 模式",
    "config_max_tokens": "最大上下文 Token",
    "config_max_tokens_hint": "设置 Agent 可使用的最大上下文 Token 数量",
    "config_max_turns": "最大记忆轮次",
    "config_max_turns_hint": "设置对话中保留的历史轮次数量",
    "config_max_steps": "最大执行步数",
    "config_max_steps_hint": "限制 Agent 单次任务的最大执行步数",
    "config_enable_thinking": "深度思考",
    "config_enable_thinking_hint": "启用后模型会进行更充分的推理",
    "config_channel_type": "通道类型",
    "config_provider": "模型厂商",
    "config_model_name": "模型",
    "config_custom_model_hint": "输入自定义模型名称",
    "config_save": "保存",
    "config_saved": "已保存",
    "config_save_error": "保存失败",
    "config_custom_option": "自定义...",
    "config_custom_tip": "接口需遵循 OpenAI API 协议",
    "config_security": "安全设置",
    "config_password": "访问密码",
    "config_password_hint": "留空则不启用密码保护",
    "config_password_changed": "访问密码已更新",
    "config_password_cleared": "访问密码已清除",
    "skills_title": "技能管理",
    "skills_desc": "查看、启用或禁用 Agent 技能",
    "skills_hub_btn": "探索技能广场",
    "evolution_title": "技能进化",
    "evolution_desc": "查看和管理技能自动进化记录",
    "skills_loading": "加载技能中...",
    "skills_loading_desc": "技能加载后将显示在此处",
    "tools_section_title": "内置工具",
    "tools_loading": "加载工具中...",
    "skills_section_title": "技能",
    "skill_enable": "启用",
    "skill_disable": "禁用",
    "skill_toggle_error": "切换技能状态失败",
    "memory_title": "记忆管理",
    "memory_desc": "查看 Agent 记忆文件和内容",
    "memory_tab_files": "记忆文件",
    "memory_tab_dreams": "梦境日记",
    "memory_loading": "加载记忆文件中...",
    "memory_loading_desc": "记忆文件将显示在此处",
    "memory_back": "返回列表",
    "memory_col_name": "文件名",
    "memory_col_type": "类型",
    "memory_col_size": "大小",
    "memory_col_updated": "更新时间",
    "knowledge_title": "知识库",
    "knowledge_desc": "浏览和探索你的知识库",
    "knowledge_tab_docs": "文档",
    "knowledge_tab_graph": "图谱",
    "knowledge_loading": "加载知识库中...",
    "knowledge_loading_desc": "知识页面将显示在这里",
    "knowledge_select_hint": "选择一个文档查看",
    "knowledge_empty_hint": "暂无知识库内容",
    "knowledge_empty_guide": "在对话中发送文档、链接或主题给 Agent，它会自动整理到你的知识库中。",
    "knowledge_go_chat": "开始对话",
    "channels_title": "通道管理",
    "channels_desc": "管理已接入的消息通道",
    "channels_add": "接入通道",
    "channels_disconnect": "断开",
    "channels_save": "保存配置",
    "channels_saved": "已保存",
    "channels_save_error": "保存失败",
    "channels_restarted": "通道已重启",
    "channels_connect_btn": "连接",
    "channels_cancel": "取消",
    "channels_select_placeholder": "请选择通道...",
    "channels_empty": "暂无接入通道",
    "channels_empty_desc": "添加一个通道后即可在这里管理",
    "channels_disconnect_confirm": "确定要断开这个通道吗？",
    "channels_connected": "已连接",
    "channels_connecting": "连接中...",
    "weixin_scan_title": "微信扫码登录",
    "weixin_scan_desc": "请使用微信扫描二维码",
    "weixin_scan_loading": "正在获取二维码...",
    "weixin_scan_waiting": "等待扫码...",
    "weixin_scan_scanned": "已扫码，请在手机上确认",
    "weixin_scan_expired": "二维码已过期，正在刷新...",
    "weixin_scan_success": "登录成功，正在连接...",
    "weixin_scan_fail": "扫码登录失败",
    "weixin_qr_tip": "二维码约 2 分钟内有效",
    "wecom_scan_btn": "企业微信扫码登录",
    "wecom_scan_desc": "请使用企业微信扫描二维码",
    "wecom_scan_success": "登录成功，正在连接...",
    "wecom_scan_fail": "连接失败",
    "wecom_mode_scan": "扫码",
    "wecom_mode_manual": "手动",
    "feishu_scan_btn": "飞书扫码登录",
    "feishu_scan_desc": "请使用飞书 App 扫码完成授权",
    "feishu_scan_replace_desc": "请使用飞书 App 扫码，或填写 App ID / Secret",
    "feishu_scan_loading": "正在获取授权二维码...",
    "feishu_scan_waiting": "等待扫码...",
    "feishu_scan_tip": "授权链接约 10 分钟内有效",
    "feishu_scan_open_link": "打开授权链接",
    "feishu_scan_success": "授权成功，正在连接...",
    "feishu_scan_expired": "授权已过期",
    "feishu_scan_denied": "授权已取消",
    "feishu_scan_fail": "授权失败",
    "feishu_scan_retry": "重试",
    "feishu_mode_scan": "扫码",
    "feishu_mode_manual": "手动",
    "tasks_title": "定时任务",
    "tasks_desc": "查看和管理定时任务",
    "tasks_coming": "即将推出",
    "tasks_coming_desc": "定时任务管理功能正在开发中",
    "logs_title": "日志",
    "logs_desc": "实时日志输出 (run.log)",
    "logs_live": "实时",
    "logs_coming_msg": "日志流即将在此提供。将连接 run.log 实现类似 tail -f 的实时输出。",
    "quota_title": "额度管理",
    "quota_desc": "查看 Token 使用量和额度状态",
    "new_chat": "新对话",
    "session_history": "历史会话",
    "today": "今天",
    "yesterday": "昨天",
    "earlier": "更早",
    "delete_session_confirm": "确定要删除这个会话吗？",
    "delete_session_title": "删除会话",
    "untitled_session": "未命名会话",
    "context_cleared": "上下文已清空",
    "tip_new_chat": "新对话",
    "tip_clear_context": "清空上下文",
    "tip_attach_file": "添加附件",
    "tip_cancel_request": "取消本次指令",
    "tip_edit_message": "编辑并重新发送",
    "request_cancelled": "已取消本次指令",
    "confirm_yes": "确定",
    "confirm_cancel": "取消",
    "error_send": "发送失败，请稍后重试",
    "error_timeout": "请求超时，请稍后重试",
    "thinking_in_progress": "思考中...",
    "thinking_done": "思考完成",
    "thinking_duration": "用时"
});

let currentLang = localStorage.getItem('zvagent_lang') || 'zh';
if (!I18N[currentLang]) currentLang = 'zh';
if (currentLang === 'en') {
    currentLang = 'zh';
    localStorage.setItem('zvagent_lang', 'zh');
}
function t(key) {
    return (I18N[currentLang] && I18N[currentLang][key]) || (I18N.en[key]) || key;
}

function applyI18n() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        el.textContent = t(el.dataset.i18n);
    });
    document.querySelectorAll('[data-i18n-html]').forEach(el => {
        el.innerHTML = t(el.dataset.i18nHtml);
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        el.placeholder = t(el.dataset['i18nPlaceholder']);
    });
    document.querySelectorAll('[data-tip-key]').forEach(el => {
        el.setAttribute('data-tooltip', t(el.dataset.tipKey));
    });
    installCfgTipPortal();
    document.documentElement.setAttribute('lang', currentLang);
    const langLabel = document.getElementById('lang-label');
    if (langLabel) langLabel.textContent = currentLang === 'zh' ? '\u4e2d\u6587' : 'EN';
}

function toggleLanguage() {
    currentLang = currentLang === 'zh' ? 'en' : 'zh';
    localStorage.setItem('zvagent_lang', currentLang);
    applyI18n();
    _applyInputTooltips();
}

// Floating tooltip portal for [data-tip-key] elements. Tooltip nodes are
// appended to <body> so they aren't clipped by overflow:hidden ancestors
// (e.g. the config panel's scroll container).
let _cfgTipPortalEl = null;
let _cfgTipPortalInstalled = false;
function installCfgTipPortal() {
    if (_cfgTipPortalInstalled) return;
    _cfgTipPortalInstalled = true;

    const showTip = (target) => {
        const text = target.getAttribute('data-tooltip');
        if (!text) return;
        if (!_cfgTipPortalEl) {
            _cfgTipPortalEl = document.createElement('div');
            _cfgTipPortalEl.className = 'cfg-tip-floating';
            document.body.appendChild(_cfgTipPortalEl);
        }
        _cfgTipPortalEl.textContent = text;
        const rect = target.getBoundingClientRect();
        // Render once to measure, then position above the target, centered.
        _cfgTipPortalEl.style.left = '0px';
        _cfgTipPortalEl.style.top = '0px';
        _cfgTipPortalEl.classList.add('show');
        const tipRect = _cfgTipPortalEl.getBoundingClientRect();
        let left = rect.left + rect.width / 2 - tipRect.width / 2;
        // Clamp horizontally to the viewport with an 8px gutter.
        left = Math.max(8, Math.min(left, window.innerWidth - tipRect.width - 8));
        const top = rect.top - tipRect.height - 6;
        _cfgTipPortalEl.style.left = left + 'px';
        _cfgTipPortalEl.style.top = top + 'px';
    };
    const hideTip = () => {
        if (_cfgTipPortalEl) _cfgTipPortalEl.classList.remove('show');
    };

    document.addEventListener('mouseover', (e) => {
        const target = e.target.closest('[data-tip-key]');
        if (target) showTip(target);
    });
    document.addEventListener('mouseout', (e) => {
        const target = e.target.closest('[data-tip-key]');
        if (target) hideTip();
    });
    // Hide on scroll/resize so the tooltip doesn't drift away from its anchor.
    window.addEventListener('scroll', hideTip, true);
    window.addEventListener('resize', hideTip);
}

// =====================================================================
// Theme
// =====================================================================
let currentTheme = localStorage.getItem('zvagent_theme') || 'dark';

function applyTheme() {
    const root = document.documentElement;
    if (currentTheme === 'dark') {
        root.classList.add('dark');
        document.getElementById('theme-icon').className = 'fas fa-sun';
        document.getElementById('hljs-light').disabled = true;
        document.getElementById('hljs-dark').disabled = false;
    } else {
        root.classList.remove('dark');
        document.getElementById('theme-icon').className = 'fas fa-moon';
        document.getElementById('hljs-light').disabled = false;
        document.getElementById('hljs-dark').disabled = true;
    }
}

function toggleTheme() {
    currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('zvagent_theme', currentTheme);
    applyTheme();
}

// =====================================================================
// Sidebar & Navigation
// =====================================================================
const VIEW_META = {
    chat:     { group: 'nav_chat',    page: 'menu_chat' },
    config:   { group: 'nav_manage',  page: 'menu_config' },
    skills:   { group: 'nav_manage',  page: 'menu_skills' },
    evolution:{ group: 'nav_manage',  page: 'menu_evolution' },
    quota:    { group: 'nav_manage',  page: 'menu_quota' },
    memory:   { group: 'nav_manage',  page: 'menu_memory' },
    knowledge:{ group: 'nav_manage',  page: 'menu_knowledge' },
    reports:  { group: 'nav_manage',  page: 'menu_reports' },
    channels: { group: 'nav_manage',  page: 'menu_channels' },
    tasks:    { group: 'nav_manage',  page: 'menu_tasks' },
    logs:     { group: 'nav_monitor', page: 'menu_logs' },
};

let currentView = 'chat';

function navigateTo(viewId) {
    if (!VIEW_META[viewId]) return;
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    const target = document.getElementById('view-' + viewId);
    if (target) target.classList.add('active');
    document.querySelectorAll('.sidebar-item').forEach(item => {
        item.classList.toggle('active', item.dataset.view === viewId);
    });
    const meta = VIEW_META[viewId];
    document.getElementById('breadcrumb-group').textContent = t(meta.group);
    document.getElementById('breadcrumb-group').dataset.i18n = meta.group;
    document.getElementById('breadcrumb-page').textContent = t(meta.page);
    document.getElementById('breadcrumb-page').dataset.i18n = meta.page;
    currentView = viewId;
    if (window.innerWidth < 1024) closeSidebar();
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const isOpen = !sidebar.classList.contains('-translate-x-full');
    if (isOpen) {
        closeSidebar();
    } else {
        sidebar.classList.remove('-translate-x-full');
        overlay.classList.remove('hidden');
    }
}

function closeSidebar() {
    document.getElementById('sidebar').classList.add('-translate-x-full');
    document.getElementById('sidebar-overlay').classList.add('hidden');
}

document.querySelectorAll('.menu-group > button').forEach(btn => {
    btn.addEventListener('click', () => {
        btn.parentElement.classList.toggle('open');
    });
});

document.querySelectorAll('.sidebar-item').forEach(item => {
    item.addEventListener('click', () => navigateTo(item.dataset.view));
});

function ensureEvolutionView() {
    if (!document.querySelector('.sidebar-item[data-view="evolution"]')) {
        const skillsItem = document.querySelector('.sidebar-item[data-view="skills"]');
        if (skillsItem) {
            const item = document.createElement('a');
            item.className = 'sidebar-item flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-all duration-150 hover:bg-white/5 hover:text-neutral-200 text-[14px]';
            item.dataset.view = 'evolution';
            item.innerHTML = `
                <i class="fas fa-code-branch item-icon text-xs w-5 text-center"></i>
                <span data-i18n="menu_evolution">${t('menu_evolution')}</span>
            `;
            item.addEventListener('click', () => navigateTo('evolution'));
            skillsItem.insertAdjacentElement('afterend', item);
        }
    }

    if (!document.getElementById('view-evolution')) {
        const view = document.createElement('div');
        view.id = 'view-evolution';
        view.className = 'view';
        view.innerHTML = `
            <div class="flex-1 overflow-y-auto p-4 md:p-6">
                <div class="max-w-6xl mx-auto">
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-5">
                        <div>
                            <h2 class="text-xl font-bold text-slate-800 dark:text-slate-100" data-i18n="evolution_title">${t('evolution_title')}</h2>
                            <p class="text-sm text-slate-500 dark:text-slate-400 mt-1" data-i18n="evolution_desc">${t('evolution_desc')}</p>
                        </div>
                        <button onclick="loadEvolutionView(true)"
                                class="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-200 dark:border-white/10
                                       text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10
                                       text-sm font-medium cursor-pointer transition-colors">
                            <i class="fas fa-rotate text-xs"></i><span>刷新</span>
                        </button>
                    </div>

                    <div id="evolution-status" class="hidden mb-4 px-4 py-3 rounded-lg text-sm"></div>

                    <section class="bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 overflow-hidden mb-4">
                        <div class="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-white/10">
                            <div class="flex items-center gap-2">
                                <i class="fas fa-heart-pulse text-rose-400 text-sm"></i>
                                <h3 class="font-semibold text-slate-800 dark:text-slate-100 text-sm">技能健康度</h3>
                            </div>
                            <div class="flex items-center gap-3">
                                <button onclick="evolutionRunCycle()"
                                        class="text-xs text-indigo-600 dark:text-indigo-300 hover:text-indigo-700 dark:hover:text-indigo-200 cursor-pointer">运行一轮</button>
                                <button onclick="evolutionAutoQueue()"
                                        class="text-xs text-emerald-600 dark:text-emerald-300 hover:text-emerald-700 dark:hover:text-emerald-200 cursor-pointer">自动排队</button>
                                <button onclick="evolutionAutoApplySafe()"
                                        class="text-xs text-violet-600 dark:text-violet-300 hover:text-violet-700 dark:hover:text-violet-200 cursor-pointer">安全自动应用</button>
                                <button onclick="loadEvolutionView(true)"
                                        class="text-xs text-primary-500 hover:text-primary-600 cursor-pointer">刷新</button>
                            </div>
                        </div>
                        <div id="evo-health" class="grid gap-3 p-4 md:grid-cols-2 xl:grid-cols-3">
                            <div class="text-sm text-slate-400 dark:text-slate-500">正在加载技能健康度...</div>
                        </div>
                    </section>

                    <div class="grid gap-4 lg:grid-cols-[320px_1fr]">
                        <section class="bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 p-4">
                            <div class="flex items-center gap-2 mb-3">
                                <i class="fas fa-bolt text-amber-400 text-sm"></i>
                                <h3 class="font-semibold text-slate-800 dark:text-slate-100 text-sm">技能</h3>
                            </div>
                            <select id="evo-skill-select"
                                    class="w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600
                                           bg-slate-50 dark:bg-white/5 text-sm text-slate-800 dark:text-slate-100
                                           focus:outline-none focus:border-primary-500"></select>
                            <div id="evo-skill-list" class="mt-3 max-h-64 overflow-y-auto space-y-1"></div>
                            <div class="grid grid-cols-3 gap-2 mt-3">
                                <button onclick="evolutionSuggest()"
                                        class="px-3 py-2 rounded-lg bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium cursor-pointer transition-colors">
                                    建议
                                </button>
                                <button onclick="evolutionDraft()"
                                        class="px-3 py-2 rounded-lg border border-slate-200 dark:border-white/10 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10 text-sm font-medium cursor-pointer transition-colors">
                                    草稿
                                </button>
                                <button onclick="evolutionAutoLearn()"
                                        class="px-3 py-2 rounded-lg border border-emerald-200 dark:border-emerald-900/40 text-emerald-600 dark:text-emerald-300 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 text-sm font-medium cursor-pointer transition-colors">
                                    自动
                                </button>
                            </div>
                            <div class="mt-4">
                                <div class="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-2">建议</div>
                                <div id="evo-suggestions" class="text-sm text-slate-600 dark:text-slate-300 space-y-2">
                                    <p class="text-slate-400 dark:text-slate-500">选择一个技能后生成建议。</p>
                                </div>
                            </div>
                        </section>

                        <section class="space-y-4">
                            <div class="bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 overflow-hidden">
                                <div class="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-white/10">
                                    <div class="flex items-center gap-2">
                                        <i class="fas fa-code-branch text-primary-400 text-sm"></i>
                                        <h3 class="font-semibold text-slate-800 dark:text-slate-100 text-sm">提案</h3>
                                    </div>
                                </div>
                                <div id="evo-proposals" class="divide-y divide-slate-100 dark:divide-white/5"></div>
                            </div>

                            <div class="bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 overflow-hidden">
                                <div class="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-white/10">
                                    <div class="flex items-center gap-2">
                                        <i class="fas fa-clock-rotate-left text-sky-400 text-sm"></i>
                                        <h3 class="font-semibold text-slate-800 dark:text-slate-100 text-sm">备份</h3>
                                    </div>
                                    <button onclick="evolutionLoadBackups()"
                                            class="text-xs text-primary-500 hover:text-primary-600 cursor-pointer">加载</button>
                                </div>
                                <div id="evo-backups" class="divide-y divide-slate-100 dark:divide-white/5">
                                    <div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500">选择一个技能后加载备份。</div>
                                </div>
                            </div>
                        </section>
                    </div>

                    <section class="bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 overflow-hidden mt-4">
                        <div class="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-white/10">
                            <div class="flex items-center gap-2">
                                <i class="fas fa-timeline text-indigo-400 text-sm"></i>
                                <h3 class="font-semibold text-slate-800 dark:text-slate-100 text-sm">进化时间线</h3>
                            </div>
                            <button onclick="loadEvolutionEvents(1)"
                                    class="text-xs text-primary-500 hover:text-primary-600 cursor-pointer">加载</button>
                        </div>
                        <div class="px-4 py-3 border-b border-slate-200 dark:border-white/10 grid gap-3 md:grid-cols-[1fr_1fr_auto] md:items-end">
                            <label class="text-xs text-slate-500 dark:text-slate-400">
                                开始时间
                                <input id="evo-events-start" type="datetime-local"
                                       class="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-sm text-slate-700 dark:text-slate-200 focus:outline-none focus:border-primary-500">
                            </label>
                            <label class="text-xs text-slate-500 dark:text-slate-400">
                                结束时间
                                <input id="evo-events-end" type="datetime-local"
                                       class="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 text-sm text-slate-700 dark:text-slate-200 focus:outline-none focus:border-primary-500">
                            </label>
                            <div class="flex items-center gap-2">
                                <button onclick="evolutionSearchEvents()"
                                        class="px-3 py-2 rounded-lg bg-primary-500 hover:bg-primary-600 text-xs text-white cursor-pointer">检索</button>
                                <button onclick="evolutionResetEventFilters()"
                                        class="px-3 py-2 rounded-lg border border-slate-200 dark:border-white/10 text-xs text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10 cursor-pointer">重置</button>
                            </div>
                        </div>
                        <div id="evo-events" class="divide-y divide-slate-100 dark:divide-white/5">
                            <div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500">正在加载事件...</div>
                        </div>
                        <div id="evo-events-pager" class="hidden px-4 py-3 border-t border-slate-200 dark:border-white/10"></div>
                    </section>
                </div>
            </div>
        `;
        document.getElementById('content-area').appendChild(view);
    }
}

ensureEvolutionView();

function ensureQuotaView() {
    if (!document.querySelector('.sidebar-item[data-view="quota"]')) {
        const evolutionItem = document.querySelector('.sidebar-item[data-view="evolution"]')
            || document.querySelector('.sidebar-item[data-view="skills"]');
        if (evolutionItem) {
            const item = document.createElement('a');
            item.className = 'sidebar-item flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-all duration-150 hover:bg-white/5 hover:text-neutral-200 text-[14px]';
            item.dataset.view = 'quota';
            item.innerHTML = `
                <i class="fas fa-coins item-icon text-xs w-5 text-center"></i>
                <span data-i18n="menu_quota">${t('menu_quota')}</span>
            `;
            item.addEventListener('click', () => navigateTo('quota'));
            evolutionItem.insertAdjacentElement('afterend', item);
        }
    }

    if (!document.getElementById('view-quota')) {
        const view = document.createElement('div');
        view.id = 'view-quota';
        view.className = 'view';
        view.innerHTML = `
            <div class="flex-1 overflow-y-auto p-4 md:p-6">
                <div class="max-w-6xl mx-auto">
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-5">
                        <div>
                            <h2 class="text-xl font-bold text-slate-800 dark:text-slate-100" data-i18n="quota_title">${t('quota_title')}</h2>
                            <p class="text-sm text-slate-500 dark:text-slate-400 mt-1" data-i18n="quota_desc">${t('quota_desc')}</p>
                        </div>
                        <button onclick="loadQuotaView(true)"
                                class="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-200 dark:border-white/10
                                       text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10
                                       text-sm font-medium cursor-pointer transition-colors">
                            <i class="fas fa-rotate text-xs"></i><span>刷新</span>
                        </button>
                    </div>

                    <div id="quota-status" class="hidden mb-4 px-4 py-3 rounded-lg text-sm"></div>

                    <div class="grid gap-4 lg:grid-cols-[340px_1fr]">
                        <section class="bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 p-4">
                            <div class="flex items-center gap-2 mb-3">
                                <i class="fas fa-sliders text-primary-400 text-sm"></i>
                                <h3 class="font-semibold text-slate-800 dark:text-slate-100 text-sm">额度设置</h3>
                            </div>
                            <label class="flex items-center justify-between gap-3 py-2">
                                <span class="text-sm text-slate-600 dark:text-slate-300">启用额度限制</span>
                                <input id="quota-enabled" type="checkbox" class="w-4 h-4">
                            </label>
                            <label class="block mt-3">
                                <span class="text-xs text-slate-400 dark:text-slate-500">新用户默认 Token 数</span>
                                <input id="quota-default-tokens" type="number" min="0" step="1000"
                                       class="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-white/5 text-sm text-slate-800 dark:text-slate-100">
                            </label>
                            <label class="block mt-3">
                                <span class="text-xs text-slate-400 dark:text-slate-500">每次请求最低扣费 Token</span>
                                <input id="quota-min-request" type="number" min="1" step="100"
                                       class="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-white/5 text-sm text-slate-800 dark:text-slate-100">
                            </label>
                            <button onclick="saveQuotaConfig()"
                                    class="mt-4 w-full px-3 py-2 rounded-lg bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium cursor-pointer transition-colors">
                                保存设置
                            </button>

                            <div class="mt-6 pt-4 border-t border-slate-200 dark:border-white/10">
                                <div class="flex items-center gap-2 mb-3">
                                    <i class="fas fa-user-plus text-emerald-400 text-sm"></i>
                                    <h3 class="font-semibold text-slate-800 dark:text-slate-100 text-sm">用户额度</h3>
                                </div>
                                <label class="block">
                                    <span class="text-xs text-slate-400 dark:text-slate-500">用户 ID / 会话 ID</span>
                                    <input id="quota-user-id" type="text" placeholder="session_xxx 或 weixin__wx1__..."
                                           class="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-white/5 text-sm text-slate-800 dark:text-slate-100">
                                </label>
                                <label class="block mt-3">
                                    <span class="text-xs text-slate-400 dark:text-slate-500">Token 数</span>
                                    <input id="quota-token-value" type="number" min="0" step="1000" value="100000"
                                           class="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-white/5 text-sm text-slate-800 dark:text-slate-100">
                                </label>
                                <div class="grid grid-cols-2 gap-2 mt-3">
                                    <button onclick="quotaSetUserQuota()"
                                            class="px-3 py-2 rounded-lg bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium cursor-pointer transition-colors">
                                        设置
                                    </button>
                                    <button onclick="quotaAddUserQuota()"
                                            class="px-3 py-2 rounded-lg border border-slate-200 dark:border-white/10 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10 text-sm font-medium cursor-pointer transition-colors">
                                        增加
                                    </button>
                                </div>
                            </div>
                            <div class="mt-6 pt-4 border-t border-slate-200 dark:border-white/10">
                                <div class="flex items-center gap-2 mb-3">
                                    <i class="fas fa-ticket text-amber-400 text-sm"></i>
                                    <h3 class="font-semibold text-slate-800 dark:text-slate-100 text-sm">兑换码生成</h3>
                                </div>
                                <label class="block">
                                    <span class="text-xs text-slate-400 dark:text-slate-500">每个兑换码充值 Token 数</span>
                                    <input id="quota-code-tokens" type="number" min="1" step="1000" value="100000"
                                           class="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-white/5 text-sm text-slate-800 dark:text-slate-100">
                                </label>
                                <label class="block mt-3">
                                    <span class="text-xs text-slate-400 dark:text-slate-500">生成数量</span>
                                    <input id="quota-code-count" type="number" min="1" max="100" step="1" value="1"
                                           class="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-white/5 text-sm text-slate-800 dark:text-slate-100">
                                </label>
                                <button onclick="quotaGenerateCodes()"
                                        class="mt-3 w-full px-3 py-2 rounded-lg bg-amber-500 hover:bg-amber-600 text-white text-sm font-medium cursor-pointer transition-colors">
                                    生成兑换码
                                </button>
                                <div id="quota-generated-codes" class="mt-3 space-y-1"></div>
                            </div>
                        </section>

                        <section class="space-y-4">
                            <div id="quota-stats" class="grid gap-3 md:grid-cols-4"></div>
                            <div class="bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 overflow-hidden">
                                <div class="px-4 py-3 border-b border-slate-200 dark:border-white/10 flex items-center justify-between gap-3">
                                    <h3 class="font-semibold text-slate-800 dark:text-slate-100 text-sm">用户列表</h3>
                                    <span id="quota-enabled-badge" class="px-2 py-1 rounded-full text-xs"></span>
                                </div>
                                <div id="quota-users" class="overflow-x-auto"></div>
                            </div>
                            <div class="bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 overflow-hidden">
                                <div class="px-4 py-3 border-b border-slate-200 dark:border-white/10">
                                    <h3 class="font-semibold text-slate-800 dark:text-slate-100 text-sm">最近兑换码</h3>
                                </div>
                                <div id="quota-redeem-codes" class="overflow-x-auto"></div>
                            </div>
                            <div class="bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 overflow-hidden">
                                <div class="px-4 py-3 border-b border-slate-200 dark:border-white/10">
                                    <h3 class="font-semibold text-slate-800 dark:text-slate-100 text-sm">最近用量</h3>
                                </div>
                                <div id="quota-logs" class="divide-y divide-slate-100 dark:divide-white/5">
                                    <div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500">选择一个用户查看用量日志。</div>
                                </div>
                            </div>
                        </section>
                    </div>
                </div>
            </div>
        `;
        document.getElementById('content-area').appendChild(view);
    }
}

ensureQuotaView();

function ensureReportsView() {
    if (!document.querySelector('.sidebar-item[data-view="reports"]')) {
        const knowledgeItem = document.querySelector('.sidebar-item[data-view="knowledge"]')
            || document.querySelector('.sidebar-item[data-view="memory"]');
        if (knowledgeItem) {
            const item = document.createElement('a');
            item.className = 'sidebar-item flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-all duration-150 hover:bg-white/5 hover:text-neutral-200 text-[14px]';
            item.dataset.view = 'reports';
            item.innerHTML = `
                <i class="fas fa-file-pdf item-icon text-xs w-5 text-center"></i>
                <span>报告</span>
            `;
            item.addEventListener('click', () => navigateTo('reports'));
            knowledgeItem.insertAdjacentElement('afterend', item);
        }
    }

    if (!document.getElementById('view-reports')) {
        const view = document.createElement('div');
        view.id = 'view-reports';
        view.className = 'view';
        view.innerHTML = `
            <div class="flex-1 overflow-y-auto p-4 md:p-6">
                <div class="max-w-6xl mx-auto">
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-5">
                        <div>
                            <h2 class="text-xl font-bold text-slate-800 dark:text-slate-100">报告管理</h2>
                            <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">查看微信端生成的研究报告、来源和 PDF 文件</p>
                        </div>
                        <button onclick="loadReportsView(true)"
                                class="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-200 dark:border-white/10
                                       text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10
                                       text-sm font-medium cursor-pointer transition-colors">
                            <i class="fas fa-rotate text-xs"></i><span>刷新</span>
                        </button>
                    </div>
                    <div id="reports-summary" class="grid gap-3 sm:grid-cols-4 mb-4"></div>
                    <div id="reports-list" class="grid gap-3"></div>
                </div>
            </div>
        `;
        document.getElementById('content-area').appendChild(view);
    }
}

ensureReportsView();

window.addEventListener('resize', () => {
    if (window.innerWidth >= 1024) {
        document.getElementById('sidebar').classList.remove('-translate-x-full');
        document.getElementById('sidebar-overlay').classList.add('hidden');
    } else {
        if (!document.getElementById('sidebar').classList.contains('-translate-x-full')) {
            closeSidebar();
        }
    }
});

// =====================================================================
// Markdown Renderer
// =====================================================================
function createMd() {
    const md = window.markdownit({
        html: false, breaks: true, linkify: true, typographer: true,
        highlight: function(str, lang) {
            if (lang && hljs.getLanguage(lang)) {
                try { return hljs.highlight(str, { language: lang }).value; } catch (_) {}
            }
            return hljs.highlightAuto(str).value;
        }
    });
    if (window.texmath && window.katex) {
        md.use(window.texmath, {
            engine: window.katex,
            delimiters: 'dollars',
            katexOptions: {
                throwOnError: false,
                strict: false,
                trust: false,
                output: 'html'
            }
        });
    }
    const defaultLinkOpen = md.renderer.rules.link_open || function(tokens, idx, options, env, self) {
        return self.renderToken(tokens, idx, options);
    };
    md.renderer.rules.link_open = function(tokens, idx, options, env, self) {
        tokens[idx].attrPush(['target', '_blank']);
        tokens[idx].attrPush(['rel', 'noopener noreferrer']);
        return defaultLinkOpen(tokens, idx, options, env, self);
    };
    return md;
}

const md = createMd();
let mermaidRenderSeq = 0;

if (window.mermaid) {
    window.mermaid.initialize({
        startOnLoad: false,
        securityLevel: 'strict',
        theme: document.documentElement.classList.contains('dark') ? 'dark' : 'default',
        flowchart: { useMaxWidth: true, htmlLabels: false }
    });
}

const VIDEO_EXT_RE = /\.(?:mp4|webm|mov|avi|mkv)$/i;  // tested against URL without query string
const AUDIO_EXT_RE = /\.(?:mp3|wav|ogg|m4a|flac|aac|wma)$/i;  // tested against URL without query string
const IMAGE_EXT_RE = /\.(?:jpg|jpeg|png|gif|webp|bmp|svg)$/i;  // tested against URL without query string
const LATEX_COMMAND_RE = /\\(?:frac|sum|prod|int|sqrt|hat|bar|tilde|vec|dot|ddot|left|right|begin|end|text|mathrm|mathbf|mathbb|mathcal|sigma|mu|alpha|beta|gamma|delta|theta|lambda|leq|geq|neq|cdot|times|infty|partial|nabla|forall|exists)\b/;

function _isLocalFileRef(url) {
    if (!url) return false;
    if (/^(?:https?:|data:|blob:|#|mailto:|javascript:)/i.test(url)) return false;
    if (url.startsWith('/api/') || url.startsWith('/assets/') || url.startsWith('/uploads/')) return false;
    return /^(?:file:\/\/\/|[A-Za-z]:[\\/]|\/[A-Za-z]|\.{0,2}\/|[\w.-]+[\\/]|[\w.-]+$)/.test(url);
}

function _toWebUrl(url) {
    try {
        url = decodeURIComponent(url);
    } catch (_) {}
    if (_isLocalFileRef(url)) {
        return '/api/file?path=' + encodeURIComponent(url.replace(/^file:\/\/\//i, '/'));
    }
    if (/^\/[A-Za-z]/.test(url) && !url.startsWith('/api/')) {
        return '/api/file?path=' + encodeURIComponent(url);
    }
    if (/^file:\/\/\//i.test(url)) {
        return '/api/file?path=' + encodeURIComponent(url.replace(/^file:\/\/\//i, '/'));
    }
    return url;
}

function _buildVideoHtml(url) {
    const webUrl = _toWebUrl(url);
    const fileName = url.split('/').pop().split('?')[0];
    return `<div style="margin:10px 0;">` +
        `<video controls preload="metadata" ` +
        `style="max-width:100%;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.15);display:block;">` +
        `<source src="${webUrl}"></video>` +
        `<a href="${webUrl}" target="_blank" ` +
        `style="display:inline-flex;align-items:center;gap:4px;margin-top:4px;font-size:12px;color:#8b8fa8;text-decoration:none;">` +
        `<i class="fas fa-download"></i> ${escapeHtml(fileName)}</a></div>`;
}

function _buildAudioHtml(url, fileName) {
    const webUrl = _toWebUrl(url);
    const label = fileName || url.split('/').pop().split('?')[0] || 'audio';
    return `<div style="margin:10px 0;max-width:520px;">` +
        `<audio controls preload="metadata" src="${webUrl}" ` +
        `style="width:100%;display:block;"></audio>` +
        `<a href="${webUrl}" target="_blank" download="${escapeHtml(label)}" ` +
        `style="display:inline-flex;align-items:center;gap:4px;margin-top:4px;font-size:12px;color:#8b8fa8;text-decoration:none;">` +
        `<i class="fas fa-download"></i> ${escapeHtml(label)}</a></div>`;
}

function _openImageLightbox(src) {
    let overlay = document.getElementById('zvagent-lightbox');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'zvagent-lightbox';
        overlay.style.cssText = 'position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,0.85);display:flex;align-items:center;justify-content:center;cursor:zoom-out;opacity:0;transition:opacity .2s';
        overlay.onclick = () => { overlay.style.opacity = '0'; setTimeout(() => overlay.style.display = 'none', 200); };
        const img = document.createElement('img');
        img.id = 'zvagent-lightbox-img';
        img.style.cssText = 'max-width:92vw;max-height:92vh;border-radius:8px;box-shadow:0 4px 24px rgba(0,0,0,0.5);object-fit:contain;';
        img.onclick = (e) => e.stopPropagation();
        overlay.appendChild(img);
        document.body.appendChild(overlay);
    }
    overlay.querySelector('#zvagent-lightbox-img').src = src;
    overlay.style.display = 'flex';
    requestAnimationFrame(() => overlay.style.opacity = '1');
}

function _buildImageHtml(url) {
    const webUrl = _toWebUrl(url);
    const safeUrl = webUrl.replace(/"/g, '&quot;');
    return `<div style="margin:10px 0;">` +
        `<img src="${safeUrl}" alt="image" loading="lazy" ` +
        `onclick="_openImageLightbox(this.src)" ` +
        `style="max-width:520px;width:100%;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.15);display:block;cursor:zoom-in;">` +
        `</div>`;
}

function injectVideoPlayers(html) {
    // Step 1: replace markdown-it anchor tags whose href points to a video file.
    const step1 = html.replace(
        /<a\s+href="(https?:\/\/[^"]+)"[^>]*>[^<]*<\/a>/gi,
        (match, url) => VIDEO_EXT_RE.test(url.split('?')[0]) ? _buildVideoHtml(url) : match
    );
    // Step 2: replace any remaining bare video URLs in text nodes (not inside HTML tags).
    // Split on HTML tags to avoid touching src/href attributes already in markup.
    return step1.split(/(<[^>]+>)/).map((chunk, idx) => {
        // Even indices are text nodes; odd indices are HTML tags 闁?leave them untouched.
        if (idx % 2 !== 0) return chunk;
        return chunk.replace(/https?:\/\/\S+/gi, (url) => {
            const bare = url.replace(/[),.\s]+$/, '');  // strip trailing punctuation
            return VIDEO_EXT_RE.test(bare.split('?')[0]) ? _buildVideoHtml(bare) : url;
        });
    }).join('');
}

// Convert image URLs into inline <img> previews. Mirrors injectVideoPlayers but for images.
// Handles three cases produced by markdown-it:
//   1. <a href="...image.jpg">...</a>  (bare URL or autolink that linkify turned into an anchor)
//   2. <img src="...">                  (markdown image syntax) 闁?leave as-is, but normalize style
//   3. raw URL still present in a text node                    闁?only as a safety net
function injectImagePreviews(html) {
    // Step 1: anchor whose href points to an image file -> replace with <img> preview.
    const step1 = html.replace(
        /<a\s+href="(https?:\/\/[^"]+)"[^>]*>[^<]*<\/a>/gi,
        (match, url) => IMAGE_EXT_RE.test(url.split('?')[0]) ? _buildImageHtml(url) : match
    );
    // Step 2: bare image URLs left in text nodes (rare 闁?markdown-it's linkify usually catches them).
    return step1.split(/(<[^>]+>)/).map((chunk, idx) => {
        if (idx % 2 !== 0) return chunk;
        return chunk.replace(/https?:\/\/\S+/gi, (url) => {
            const bare = url.replace(/[),.\s]+$/, '');
            return IMAGE_EXT_RE.test(bare.split('?')[0]) ? _buildImageHtml(bare) : url;
        });
    }).join('');
}

function _rewriteLocalImgSrc(html) {
    return html.replace(/<img\s([^>]*?)src="([^"]+)"([^>]*?)>/gi, (match, pre, src, post) => {
        const webSrc = _toWebUrl(src);
        const safeSrc = webSrc.replace(/"/g, '&quot;');
        const hasClick = /onclick/i.test(pre + post);
        const hasError = /onerror/i.test(pre + post);
        const clickAttr = hasClick ? '' : ` onclick="_openImageLightbox(this.src)" style="cursor:zoom-in;"`;
        const errorAttr = hasError ? '' : ` onerror="_handleBrokenImage(this)"`;
        return `<img ${pre}src="${safeSrc}"${post}${clickAttr}${errorAttr}>`;
    });
}

function injectAudioPlayers(html) {
    const step1 = html.replace(
        /<a\s+href="([^"]+)"[^>]*>[^<]*<\/a>/gi,
        (match, url) => AUDIO_EXT_RE.test(url.split('?')[0]) ? _buildAudioHtml(url) : match
    );
    return step1.split(/(<[^>]+>)/).map((chunk, idx) => {
        if (idx % 2 !== 0) return chunk;
        return chunk.replace(/(?:https?:\/\/|file:\/\/\/|[A-Za-z]:[\\/]|\/)[^\s<>()"]+/gi, (url) => {
            const bare = url.replace(/[),.\s]+$/, '');
            return AUDIO_EXT_RE.test(bare.split('?')[0]) ? _buildAudioHtml(bare) : url;
        });
    }).join('');
}

function _handleBrokenImage(img) {
    if (!img || img.dataset.brokenHandled === '1') return;
    img.dataset.brokenHandled = '1';
    const box = document.createElement('div');
    box.className = 'broken-image-card';
    const rawSrc = img.getAttribute('src') || '';
    const alt = img.getAttribute('alt') || 'image';
    box.innerHTML = `
        <div class="broken-image-title"><i class="fas fa-image"></i><span>${escapeHtml(alt)}</span></div>
        <div class="broken-image-hint">图表文件没有生成或路径不可访问。后续概念图将优先使用 Mermaid 直接渲染。</div>
        <code>${escapeHtml(rawSrc)}</code>
    `;
    img.replaceWith(box);
}

function renderMermaidDiagrams(container) {
    if (!window.mermaid || !container) return;
    const blocks = container.querySelectorAll('pre code.language-mermaid, pre code.lang-mermaid');
    blocks.forEach(codeEl => {
        const preEl = codeEl.closest('pre');
        if (!preEl || preEl.dataset.mermaidRendered === '1') return;
        preEl.dataset.mermaidRendered = '1';
        const source = codeEl.textContent || '';
        const wrapper = document.createElement('div');
        wrapper.className = 'mermaid-diagram';
        preEl.replaceWith(wrapper);
        const id = `mermaid-${Date.now()}-${mermaidRenderSeq++}`;
        window.mermaid.render(id, source).then(({ svg }) => {
            wrapper.innerHTML = svg;
        }).catch((err) => {
            wrapper.classList.add('mermaid-error');
            wrapper.textContent = `Mermaid 图表渲染失败：${err && err.message ? err.message : err}`;
        });
    });
}

function _normalizeMathDelimiters(text) {
    if (!text) return '';
    const fenceSplit = text.split(/(```[\s\S]*?```|~~~[\s\S]*?~~~)/g);
    return fenceSplit.map((chunk, idx) => {
        if (idx % 2 === 1) return chunk;
        let normalized = chunk
            .replace(/\\\[([\s\S]*?)\\\]/g, (_, formula) => `\n\n$$\n${formula.trim()}\n$$\n\n`)
            .replace(/\\\(([\s\S]*?)\\\)/g, (_, formula) => `$${formula.trim()}$`);

        const lines = normalized.split('\n');
        const rebuilt = [];
        for (let i = 0; i < lines.length; i += 1) {
            if (lines[i].trim() !== '[') {
                rebuilt.push(lines[i]);
                continue;
            }

            const block = [];
            let end = -1;
            for (let j = i + 1; j < lines.length; j += 1) {
                if (lines[j].trim() === ']') {
                    end = j;
                    break;
                }
                block.push(lines[j]);
            }

            const body = block.join('\n').trim();
            if (end !== -1 && LATEX_COMMAND_RE.test(body)) {
                rebuilt.push('$$', body, '$$');
                i = end;
            } else {
                rebuilt.push(lines[i]);
            }
        }
        return rebuilt.join('\n');
    }).join('');
}

function renderMarkdown(text) {
    try {
        let html = md.render(_normalizeMathDelimiters(text));
        html = _rewriteLocalImgSrc(html);
        // Order matters: video/audio first (more specific), then image.
        return injectImagePreviews(injectAudioPlayers(injectVideoPlayers(html)));
    }
    catch (e) { return text.replace(/\n/g, '<br>'); }
}

// =====================================================================
// Chat Module
// =====================================================================
let isPolling = false;
let pollGeneration = 0;   // incremented on each restart to cancel stale poll loops
let loadingContainers = {};
let activeStreams = {};   // request_id -> EventSource
let activeRequests = {};  // client_id -> current user request metadata
let isComposing = false;
let appConfig = { use_agent: false, title: 'ZVAgent', subtitle: '', providers: {}, api_bases: {} };

const SESSION_ID_KEY = 'zvagent_session_id';

function generateSessionId() {
    return 'session_' + ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
}

// Restore session_id from localStorage so conversation history survives page refresh.
// A new id is only generated when the user explicitly starts a new chat.
function loadOrCreateSessionId() {
    const stored = localStorage.getItem(SESSION_ID_KEY);
    if (stored) return stored;
    const fresh = generateSessionId();
    localStorage.setItem(SESSION_ID_KEY, fresh);
    return fresh;
}

let sessionId = loadOrCreateSessionId();

// ---- Conversation history state ----
let historyPage = 0;       // last page fetched (0 = nothing fetched yet)
let historyHasMore = false;
let historyLoading = false;

fetch('/config').then(r => r.json()).then(data => {
    if (data.status === 'success') {
        appConfig = data;
        const title = data.title || 'ZVAgent';
        document.getElementById('welcome-title').textContent = title;
        initConfigView(data);
    }
    loadHistory(1);
}).catch(() => { loadHistory(1); });

// Start polling immediately so scheduler/push messages are received at any time
startPolling();

const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const messagesDiv = document.getElementById('chat-messages');
const fileInput = document.getElementById('file-input');

// Smart auto-scroll: pause when user scrolls up, resume when near bottom
let _autoScrollEnabled = true;
const _SCROLL_THRESHOLD = 80; // px from bottom to re-enable auto-scroll

messagesDiv.addEventListener('scroll', () => {
    const distFromBottom = messagesDiv.scrollHeight - messagesDiv.scrollTop - messagesDiv.clientHeight;
    _autoScrollEnabled = distFromBottom <= _SCROLL_THRESHOLD;
    _updateScrollToBottomBtn();
});

// Intercept internal navigation links in chat messages
messagesDiv.addEventListener('click', (e) => {
    const userActionBtn = e.target.closest('.user-msg-action');
    if (userActionBtn) {
        e.preventDefault();
        const msgRoot = userActionBtn.closest('.user-message');
        if (!msgRoot) return;
        const clientId = msgRoot.dataset.clientId;
        const rawText = msgRoot.dataset.rawMessage || '';
        const action = userActionBtn.dataset.action;

        if (action === 'cancel') {
            cancelUserRequest(clientId, { edit: false });
            return;
        }

        if (action === 'edit') {
            if (clientId && activeRequests[clientId]) {
                cancelUserRequest(clientId, { edit: true });
            } else {
                restoreMessageToInput(rawText);
            }
            return;
        }
    }

    const copyBtn = e.target.closest('.copy-msg-btn');
    if (copyBtn) {
        e.preventDefault();
        const msgRoot = copyBtn.closest('.flex.gap-3');
        const answerEl = msgRoot && msgRoot.querySelector('.answer-content');
        const rawMd = answerEl && answerEl.dataset.rawMd;
        if (rawMd) {
            navigator.clipboard.writeText(rawMd).then(() => {
                const icon = copyBtn.querySelector('i');
                if (icon) { icon.className = 'fas fa-check'; setTimeout(() => { icon.className = 'fas fa-copy'; }, 1500); }
            });
        }
        return;
    }
    const a = e.target.closest('a');
    if (!a) return;
    const href = a.getAttribute('href') || '';
    if (href === '/memory/dreams') {
        e.preventDefault();
        navigateTo('memory');
        setTimeout(() => switchMemoryTab('dreams'), 50);
    } else if (href === '/memory/MEMORY.md') {
        e.preventDefault();
        navigateTo('memory');
        setTimeout(() => { switchMemoryTab('files'); openMemoryFile('MEMORY.md', 'memory'); }, 50);
    }
});
const attachmentPreview = document.getElementById('attachment-preview');

// Pending attachments: [{file_path, file_name, file_type, preview_url}]
// Items with _uploading=true are still in flight.
let pendingAttachments = [];
let uploadingCount = 0;

// Input history (like terminal arrow-key recall)
const inputHistory = [];
let historyIdx = -1;
let historySavedDraft = '';

function updateSendBtnState() {
    sendBtn.disabled = uploadingCount > 0 || (!chatInput.value.trim() && pendingAttachments.length === 0);
}

function renderAttachmentPreview() {
    if (pendingAttachments.length === 0) {
        attachmentPreview.classList.add('hidden');
        attachmentPreview.innerHTML = '';
        updateSendBtnState();
        return;
    }
    attachmentPreview.classList.remove('hidden');
    attachmentPreview.innerHTML = pendingAttachments.map((att, idx) => {
        if (att._uploading) {
            return `<div class="att-chip att-uploading" data-idx="${idx}">
                <i class="fas fa-spinner fa-spin"></i>
                <span class="att-name">${escapeHtml(att.file_name)}</span>
            </div>`;
        }
        if (att.file_type === 'image') {
            return `<div class="att-thumb" data-idx="${idx}">
                <img src="${att.preview_url}" alt="${escapeHtml(att.file_name)}">
                <button class="att-remove" onclick="removeAttachment(${idx})">&times;</button>
            </div>`;
        }
        const icon = att.file_type === 'video' ? 'fa-film' : 'fa-file-alt';
        return `<div class="att-chip" data-idx="${idx}">
            <i class="fas ${icon}"></i>
            <span class="att-name">${escapeHtml(att.file_name)}</span>
            <button class="att-remove" onclick="removeAttachment(${idx})">&times;</button>
        </div>`;
    }).join('');
    updateSendBtnState();
}

function removeAttachment(idx) {
    if (pendingAttachments[idx]?._uploading) return;
    pendingAttachments.splice(idx, 1);
    renderAttachmentPreview();
}

async function handleFileSelect(files) {
    if (!files || files.length === 0) return;
    const tasks = [];
    for (const file of files) {
        const placeholder = { file_name: file.name, file_type: 'file', _uploading: true };
        pendingAttachments.push(placeholder);
        uploadingCount++;
        renderAttachmentPreview();

        tasks.push((async () => {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('session_id', sessionId);
            try {
                const resp = await fetch('/upload', { method: 'POST', body: formData });
                const data = await resp.json();
                if (data.status === 'success') {
                    placeholder.file_path = data.file_path;
                    placeholder.file_name = data.file_name;
                    placeholder.file_type = data.file_type;
                    placeholder.preview_url = data.preview_url;
                    delete placeholder._uploading;
                } else {
                    const i = pendingAttachments.indexOf(placeholder);
                    if (i !== -1) pendingAttachments.splice(i, 1);
                }
            } catch (e) {
                console.error('Upload failed:', e);
                const i = pendingAttachments.indexOf(placeholder);
                if (i !== -1) pendingAttachments.splice(i, 1);
            }
            uploadingCount--;
            renderAttachmentPreview();
        })());
    }
    await Promise.all(tasks);
}

fileInput.addEventListener('change', function() {
    handleFileSelect(this.files);
    this.value = '';
});

// Drag-and-drop support on chat input area
const chatInputArea = chatInput.closest('.flex-shrink-0');
chatInputArea.addEventListener('dragover', (e) => { e.preventDefault(); e.stopPropagation(); chatInputArea.classList.add('drag-over'); });
chatInputArea.addEventListener('dragleave', (e) => { e.preventDefault(); e.stopPropagation(); chatInputArea.classList.remove('drag-over'); });
chatInputArea.addEventListener('drop', (e) => {
    e.preventDefault(); e.stopPropagation();
    chatInputArea.classList.remove('drag-over');
    if (e.dataTransfer.files.length) handleFileSelect(e.dataTransfer.files);
});

// Paste image support
chatInput.addEventListener('paste', (e) => {
    const items = e.clipboardData?.items;
    if (!items) return;
    const files = [];
    for (const item of items) {
        if (item.kind === 'file') {
            files.push(item.getAsFile());
        }
    }
    if (files.length) {
        e.preventDefault();
        handleFileSelect(files);
    }
});

chatInput.addEventListener('compositionstart', () => { isComposing = true; });
chatInput.addEventListener('compositionend', () => { setTimeout(() => { isComposing = false; }, 100); });

// 闁冲厜鍋撻柍鍏夊亾 Slash Command Menu 闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋撻柍鍏夊亾闁冲厜鍋?
const SLASH_COMMANDS = [
    { cmd: '/help',                desc: 'Show help' },
    { cmd: '/status',              desc: 'Show runtime status' },
    { cmd: '/context',             desc: 'Show current context' },
    { cmd: '/context clear',       desc: 'Clear context' },
    { cmd: '/skill list',          desc: 'List local skills' },
    { cmd: '/skill list --remote', desc: 'List remote skills' },
    { cmd: '/skill search ',       desc: 'Search skills' },
    { cmd: '/skill install ',      desc: 'Install a skill' },
    { cmd: '/skill uninstall ',    desc: 'Uninstall a skill' },
    { cmd: '/skill info ',         desc: 'Show skill details' },
    { cmd: '/skill enable ',       desc: 'Enable a skill' },
    { cmd: '/skill disable ',      desc: 'Disable a skill' },
    { cmd: '/memory dream ',       desc: 'Open dream memory' },
    { cmd: '/knowledge',           desc: 'Open knowledge base' },
    { cmd: '/knowledge list',      desc: 'List knowledge pages' },
    { cmd: '/knowledge on',        desc: 'Enable knowledge capture' },
    { cmd: '/knowledge off',       desc: 'Disable knowledge capture' },
    { cmd: '/config',              desc: 'Open configuration' },
    { cmd: '/logs',                desc: 'Open logs' },
    { cmd: '/version',             desc: 'Show version' },
    { cmd: '/报告 ',               desc: '生成 PDF 研究报告' },
    { cmd: '/报告状态 ',           desc: '查询报告进度' },
    { cmd: '/报告列表',            desc: '查看最近报告' },
];

const slashMenu = document.getElementById('slash-menu');
let slashActiveIdx = 0;
let slashFiltered = [];
let slashJustSelected = false;
let slashLastFilter = '';
let slashLastMouseX = -1;
let slashLastMouseY = -1;

function showSlashMenu(filter) {
    const q = filter.toLowerCase();
    if (q === slashLastFilter && !slashMenu.classList.contains('hidden')) return;
    slashLastFilter = q;

    const newFiltered = SLASH_COMMANDS.filter(c => c.cmd.toLowerCase().startsWith(q));
    if (newFiltered.length === 0) {
        hideSlashMenu();
        return;
    }

    const changed = newFiltered.length !== slashFiltered.length ||
        newFiltered.some((c, i) => c.cmd !== slashFiltered[i]?.cmd);
    slashFiltered = newFiltered;
    if (changed) slashActiveIdx = 0;
    slashActiveIdx = Math.min(slashActiveIdx, slashFiltered.length - 1);

    slashNavByKeyboard = true;
    renderSlashItems();
    slashMenu.classList.remove('hidden');
}

function hideSlashMenu() {
    slashMenu.classList.add('hidden');
    slashMenu.innerHTML = '';
    slashFiltered = [];
    slashActiveIdx = -1;
    slashLastFilter = '';
    slashNavByKeyboard = false;
    slashLastMouseX = -1;
    slashLastMouseY = -1;
}

function isSlashMenuVisible() {
    return !slashMenu.classList.contains('hidden') && slashFiltered.length > 0;
}

function renderSlashItems() {
    slashMenu.innerHTML =
        '<div class="slash-menu-header">Commands</div>' +
        slashFiltered.map((c, i) =>
            `<div class="slash-menu-item${i === slashActiveIdx ? ' active' : ''}" data-idx="${i}">` +
            `<span class="cmd">${escapeHtml(c.cmd)}</span>` +
            `<span class="desc">${escapeHtml(c.desc)}</span></div>`
        ).join('');

    const activeEl = slashMenu.querySelector('.slash-menu-item.active');
    if (activeEl) activeEl.scrollIntoView({ block: 'nearest' });
}

// Delegated events on the persistent slashMenu container (not destroyed by innerHTML)
// Use coordinate comparison to distinguish real mouse movement from DOM-rebuild phantom events.
slashMenu.addEventListener('mousemove', (e) => {
    if (e.clientX === slashLastMouseX && e.clientY === slashLastMouseY) return;
    slashLastMouseX = e.clientX;
    slashLastMouseY = e.clientY;
    if (!slashNavByKeyboard) return;
    slashNavByKeyboard = false;
    const item = e.target.closest('.slash-menu-item');
    if (!item) return;
    const idx = parseInt(item.dataset.idx);
    if (idx === slashActiveIdx) return;
    slashActiveIdx = idx;
    slashMenu.querySelectorAll('.slash-menu-item').forEach(el => {
        el.classList.toggle('active', parseInt(el.dataset.idx) === idx);
    });
});

slashMenu.addEventListener('mouseover', (e) => {
    if (slashNavByKeyboard) return;
    const item = e.target.closest('.slash-menu-item');
    if (!item) return;
    const idx = parseInt(item.dataset.idx);
    if (idx === slashActiveIdx) return;
    slashActiveIdx = idx;
    slashMenu.querySelectorAll('.slash-menu-item').forEach(el => {
        el.classList.toggle('active', parseInt(el.dataset.idx) === idx);
    });
});

slashMenu.addEventListener('mousedown', (e) => {
    const item = e.target.closest('.slash-menu-item');
    if (!item) return;
    e.preventDefault();
    selectSlashCommand(parseInt(item.dataset.idx));
});

function selectSlashCommand(idx) {
    if (idx < 0 || idx >= slashFiltered.length) return;
    const chosen = slashFiltered[idx].cmd;
    slashJustSelected = true;
    chatInput.value = chosen;
    chatInput.dispatchEvent(new Event('input'));
    hideSlashMenu();
    chatInput.focus();
    chatInput.selectionStart = chatInput.selectionEnd = chosen.length;
}

chatInput.addEventListener('input', function() {
    this.style.height = '42px';
    const scrollH = this.scrollHeight;
    const newH = Math.min(scrollH, 180);
    this.style.height = newH + 'px';
    this.style.overflowY = scrollH > 180 ? 'auto' : 'hidden';
    updateSendBtnState();

    const val = this.value;
    if (slashJustSelected) {
        slashJustSelected = false;
    } else if (val.startsWith('/')) {
        showSlashMenu(val);
    } else {
        hideSlashMenu();
    }
});

chatInput.addEventListener('keydown', function(e) {
    if (e.keyCode === 229 || e.isComposing || isComposing) return;

    if (isSlashMenuVisible()) {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            slashNavByKeyboard = true;
            slashActiveIdx = Math.min(slashActiveIdx + 1, slashFiltered.length - 1);
            renderSlashItems();
            return;
        }
        if (e.key === 'ArrowUp') {
            e.preventDefault();
            slashNavByKeyboard = true;
            slashActiveIdx = Math.max(slashActiveIdx - 1, 0);
            renderSlashItems();
            return;
        }
        if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey) {
            e.preventDefault();
            selectSlashCommand(slashActiveIdx);
            return;
        }
        if (e.key === 'Escape') {
            e.preventDefault();
            hideSlashMenu();
            return;
        }
        if (e.key === 'Tab') {
            e.preventDefault();
            selectSlashCommand(slashActiveIdx);
            return;
        }
    }

    // Arrow-key history recall (only when input is empty or already browsing history)
    if (e.key === 'ArrowUp' && inputHistory.length > 0 && !isSlashMenuVisible()) {
        const curVal = this.value.trim();
        const isSingleLine = !this.value.includes('\n');
        if (isSingleLine && (curVal === '' || historyIdx >= 0)) {
            e.preventDefault();
            if (historyIdx < 0) {
                historySavedDraft = this.value;
                historyIdx = inputHistory.length - 1;
            } else if (historyIdx > 0) {
                historyIdx--;
            }
            this.value = inputHistory[historyIdx];
            slashJustSelected = true;
            this.dispatchEvent(new Event('input'));
            hideSlashMenu();
            this.selectionStart = this.selectionEnd = this.value.length;
            return;
        }
    }
    if (e.key === 'ArrowDown' && historyIdx >= 0 && !isSlashMenuVisible()) {
        const isSingleLine = !this.value.includes('\n');
        if (isSingleLine) {
            e.preventDefault();
            if (historyIdx < inputHistory.length - 1) {
                historyIdx++;
                this.value = inputHistory[historyIdx];
            } else {
                historyIdx = -1;
                this.value = historySavedDraft;
                historySavedDraft = '';
            }
            slashJustSelected = true;
            this.dispatchEvent(new Event('input'));
            hideSlashMenu();
            this.selectionStart = this.selectionEnd = this.value.length;
            return;
        }
    }

    if ((e.ctrlKey || e.shiftKey) && e.key === 'Enter') {
        const start = this.selectionStart;
        const end = this.selectionEnd;
        this.value = this.value.substring(0, start) + '\n' + this.value.substring(end);
        this.selectionStart = this.selectionEnd = start + 1;
        this.dispatchEvent(new Event('input'));
        e.preventDefault();
    } else if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey) {
        sendMessage();
        e.preventDefault();
    }
});

chatInput.addEventListener('blur', () => {
    setTimeout(hideSlashMenu, 150);
});

document.querySelectorAll('.example-card').forEach(card => {
    card.addEventListener('click', () => {
        // data-send overrides the visible text (e.g. show "闁哄被鍎冲﹢鍛村礂閵娾晛鍔ラ柛娑欏灊閹? but send "/help")
        const sendText = card.dataset.send;
        if (sendText) {
            chatInput.value = sendText;
            chatInput.dispatchEvent(new Event('input'));
            chatInput.focus();
            return;
        }
        const textEl = card.querySelector('[data-i18n*="text"]');
        if (textEl) {
            chatInput.value = textEl.textContent;
            chatInput.dispatchEvent(new Event('input'));
            chatInput.focus();
        }
    });
});

function sendMessage() {
    const text = chatInput.value.trim();
    if (!text && pendingAttachments.length === 0) return;

    if (text) {
        inputHistory.push(text);
        historyIdx = -1;
        historySavedDraft = '';
    }

    const ws = document.getElementById('welcome-screen');
    const isFirstMessage = !!ws;
    if (ws) ws.remove();

    const titleInfo = (isFirstMessage && text) ? { sid: sessionId, userMsg: text } : null;

    const timestamp = new Date();
    const attachments = [...pendingAttachments];
    const clientId = generateClientRequestId();
    const userEl = addUserMessage(text, timestamp, attachments, { clientId });
    setUserRequestActive(userEl, true);

    const loadingEl = addLoadingIndicator();
    const controller = new AbortController();
    activeRequests[clientId] = {
        clientId,
        requestId: clientId,
        text,
        timestamp,
        attachments,
        userEl,
        loadingEl,
        botEl: null,
        controller,
        cancelled: false,
    };

    chatInput.value = '';
    chatInput.style.height = '42px';
    chatInput.style.overflowY = 'hidden';
    pendingAttachments = [];
    renderAttachmentPreview();
    sendBtn.disabled = true;

    const body = { session_id: sessionId, request_id: clientId, message: text, stream: true, timestamp: timestamp.toISOString() };
    if (attachments.length > 0) {
        body.attachments = attachments.map(a => ({
            file_path: a.file_path,
            file_name: a.file_name,
            file_type: a.file_type,
        }));
    }

    const MAX_RETRIES = 2;
    const RETRY_DELAY_MS = 1000;

    function postWithRetry(attempt) {
        const meta = activeRequests[clientId];
        if (!meta || meta.cancelled) return;
        fetch('/message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
            signal: controller.signal
        })
        .then(r => r.json())
        .then(data => {
            const meta = activeRequests[clientId];
            if (!meta || meta.cancelled) return;
            if (data.status === 'success') {
                meta.requestId = data.request_id;
                if (data.stream) {
                    startSSE(data.request_id, loadingEl, timestamp, titleInfo, clientId);
                } else {
                    loadingContainers[data.request_id] = loadingEl;
                }
            } else if (data.status === 'cancelled') {
                loadingEl.remove();
                setUserRequestActive(userEl, false);
                delete activeRequests[clientId];
            } else {
                loadingEl.remove();
                setUserRequestActive(userEl, false);
                delete activeRequests[clientId];
                addBotMessage(t('error_send'), new Date());
            }
        })
        .catch(err => {
            if (err.name === 'AbortError') {
                loadingEl.remove();
                setUserRequestActive(userEl, false);
                delete activeRequests[clientId];
                return;
            }
            if (attempt < MAX_RETRIES) {
                console.warn(`[sendMessage] attempt ${attempt + 1} failed, retrying...`, err);
                setTimeout(() => postWithRetry(attempt + 1), RETRY_DELAY_MS * (attempt + 1));
                return;
            }
            loadingEl.remove();
            setUserRequestActive(userEl, false);
            delete activeRequests[clientId];
            addBotMessage(t('error_send'), new Date());
        });
    }

    postWithRetry(0);
}

function startSSE(requestId, loadingEl, timestamp, titleInfo, clientId = null) {
    let botEl = null;
    let stepsEl = null;    // .agent-steps  (thinking summaries + tool indicators)
    let contentEl = null;  // .answer-content (final streaming answer)
    let mediaEl = null;    // .media-content (images & file attachments)
    let accumulatedText = '';
    let currentToolEl = null;
    let currentReasoningEl = null;  // live reasoning bubble
    let reasoningText = '';
    let reasoningStartTime = 0;
    let done = false;

    const MAX_RECONNECTS = 10;
    const RECONNECT_BASE_MS = 1000;
    let reconnectCount = 0;

    function ensureBotEl() {
        if (botEl) return;
        if (loadingEl) { loadingEl.remove(); loadingEl = null; }
        botEl = document.createElement('div');
        botEl.className = 'flex gap-3 px-4 sm:px-6 py-3';
        botEl.dataset.requestId = requestId;
        botEl.innerHTML = `
            <img src="assets/custom-logo.png" alt="ZVAgent" class="w-8 h-8 rounded-lg flex-shrink-0 object-cover">
            <div class="min-w-0 flex-1 max-w-[85%]">
                <div class="bg-white dark:bg-[#1A1A1A] border border-slate-200 dark:border-white/10 rounded-2xl px-4 py-3 text-sm leading-relaxed msg-content text-slate-700 dark:text-slate-200">
                    <div class="agent-steps"></div>
                    <div class="answer-content sse-streaming"></div>
                    <div class="media-content"></div>
                </div>
                <div class="flex items-center gap-2 mt-1.5">
                    <span class="text-xs text-slate-400 dark:text-slate-500">${formatTime(timestamp)}</span>
                    <button class="copy-msg-btn text-xs text-slate-300 dark:text-slate-600 hover:text-slate-500 dark:hover:text-slate-400 transition-colors cursor-pointer" title="Copy" style="display:none">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>
            </div>
        `;
        messagesDiv.appendChild(botEl);
        if (clientId && activeRequests[clientId]) {
            activeRequests[clientId].botEl = botEl;
        }
        stepsEl = botEl.querySelector('.agent-steps');
        contentEl = botEl.querySelector('.answer-content');
        mediaEl = botEl.querySelector('.media-content');
    }

    function connect() {
        const es = new EventSource(`/stream?request_id=${encodeURIComponent(requestId)}`);
        activeStreams[requestId] = es;

        es.onmessage = function(e) {
            const meta = clientId ? activeRequests[clientId] : null;
            if (clientId && (!meta || meta.cancelled)) {
                es.close();
                delete activeStreams[requestId];
                return;
            }
            let item;
            try { item = JSON.parse(e.data); } catch (_) { return; }

            // Successful data received, reset reconnect counter
            reconnectCount = 0;

            if (item.type === 'cancelled') {
                done = true;
                es.close();
                delete activeStreams[requestId];
                if (clientId && activeRequests[clientId]) {
                    setUserRequestActive(activeRequests[clientId].userEl, false);
                    delete activeRequests[clientId];
                }
                if (loadingEl) { loadingEl.remove(); loadingEl = null; }
                return;

            } else if (item.type === 'reasoning') {
                ensureBotEl();
                reasoningText += item.content;
                if (!currentReasoningEl) {
                    reasoningStartTime = Date.now();
                    currentReasoningEl = document.createElement('div');
                    currentReasoningEl.className = 'agent-step agent-thinking-step';
                    // During streaming, use a <pre> with a single text node and
                    // append-only updates. This avoids re-parsing markdown and
                    // re-setting innerHTML on every chunk, which is what causes
                    // the page to crash on long chains-of-thought.
                    currentReasoningEl.innerHTML = `
                        <div class="thinking-header" onclick="this.parentElement.classList.toggle('expanded')">
                            <i class="fas fa-lightbulb text-amber-400 flex-shrink-0"></i>
                            <span class="thinking-summary">${t('thinking_in_progress')}</span>
                            <i class="fas fa-chevron-right thinking-chevron"></i>
                        </div>
                        <div class="thinking-full"><pre class="thinking-stream-pre"></pre></div>`;
                    stepsEl.appendChild(currentReasoningEl);
                    const preEl = currentReasoningEl.querySelector('.thinking-stream-pre');
                    preEl.appendChild(document.createTextNode(''));
                    currentReasoningEl._streamTextNode = preEl.firstChild;
                    currentReasoningEl._streamPendingText = '';
                    currentReasoningEl._streamRafScheduled = false;
                    currentReasoningEl._streamCharsRendered = 0;
                    currentReasoningEl._streamCapped = false;
                }
                // Hard cap: once REASONING_RENDER_CAP chars are in the DOM, stop
                // appending further deltas. The full text is still kept in
                // `reasoningText` for finalize-time head+tail rendering.
                if (!currentReasoningEl._streamCapped) {
                    currentReasoningEl._streamPendingText += item.content;
                    if (!currentReasoningEl._streamRafScheduled) {
                        currentReasoningEl._streamRafScheduled = true;
                        const elRef = currentReasoningEl;
                        requestAnimationFrame(() => {
                            elRef._streamRafScheduled = false;
                            if (!elRef.isConnected || !elRef._streamTextNode) return;
                            let pending = elRef._streamPendingText;
                            elRef._streamPendingText = '';
                            if (!pending) return;
                            const remaining = REASONING_RENDER_CAP - elRef._streamCharsRendered;
                            if (remaining <= 0) {
                                elRef._streamCapped = true;
                            } else {
                                if (pending.length > remaining) {
                                    pending = pending.slice(0, remaining);
                                    elRef._streamCapped = true;
                                }
                                elRef._streamTextNode.appendData(pending);
                                elRef._streamCharsRendered += pending.length;
                                if (elRef._streamCapped) {
                                    elRef._streamTextNode.appendData(
                                        '\n\n... [reasoning truncated for display] ...'
                                    );
                                }
                            }
                            scrollChatToBottom();
                        });
                    }
                }

            } else if (item.type === 'delta') {
                ensureBotEl();
                if (currentReasoningEl) {
                    finalizeThinking(currentReasoningEl, reasoningStartTime, reasoningText);
                    currentReasoningEl = null;
                    reasoningText = '';
                }
                accumulatedText += item.content;
                contentEl.innerHTML = renderMarkdown(accumulatedText);
                scrollChatToBottom();

            } else if (item.type === 'message_end') {
                if (item.has_tool_calls && accumulatedText.trim()) {
                    ensureBotEl();
                    const frozenEl = document.createElement('div');
                    frozenEl.className = 'agent-step agent-content-step';
                    frozenEl.innerHTML = `<div class="agent-content-body">${renderMarkdown(accumulatedText.trim())}</div>`;
                    stepsEl.appendChild(frozenEl);
                    accumulatedText = '';
                    contentEl.innerHTML = '';
                    scrollChatToBottom();
                }

            } else if (item.type === 'tool_start') {
                ensureBotEl();
                if (currentReasoningEl) {
                    finalizeThinking(currentReasoningEl, reasoningStartTime, reasoningText);
                    currentReasoningEl = null;
                    reasoningText = '';
                }
                accumulatedText = '';
                contentEl.innerHTML = '';

                // Add tool execution indicator (collapsible)
                currentToolEl = document.createElement('div');
                currentToolEl.className = 'agent-step agent-tool-step';
                const argsStr = formatToolArgs(item.arguments || {});
                currentToolEl.innerHTML = `
                    <div class="tool-header" onclick="this.parentElement.classList.toggle('expanded')">
                        <i class="fas fa-cog fa-spin text-primary-400 flex-shrink-0 tool-icon"></i>
                        <span class="tool-name">${item.tool}</span>
                        <i class="fas fa-chevron-right tool-chevron"></i>
                    </div>
                    <div class="tool-detail">
                        <div class="tool-detail-section">
                            <div class="tool-detail-label">Input</div>
                            <pre class="tool-detail-content">${argsStr}</pre>
                        </div>
                        <div class="tool-detail-section tool-output-section"></div>
                    </div>`;
                stepsEl.appendChild(currentToolEl);

                scrollChatToBottom();

            } else if (item.type === 'tool_end') {
                if (currentToolEl) {
                    const isError = item.status !== 'success';
                    const icon = currentToolEl.querySelector('.tool-icon');
                    icon.className = isError
                        ? 'fas fa-times text-red-400 flex-shrink-0 tool-icon'
                        : 'fas fa-check text-primary-400 flex-shrink-0 tool-icon';

                    // Show execution time
                    const nameEl = currentToolEl.querySelector('.tool-name');
                    if (item.execution_time !== undefined) {
                        nameEl.innerHTML += ` <span class="tool-time">${item.execution_time}s</span>`;
                    }

                    // Fill output section
                    const outputSection = currentToolEl.querySelector('.tool-output-section');
                    if (outputSection && item.result) {
                        outputSection.innerHTML = `
                            <div class="tool-detail-label">${isError ? 'Error' : 'Output'}</div>
                            <pre class="tool-detail-content ${isError ? 'tool-error-text' : ''}">${escapeHtml(String(item.result))}</pre>`;
                    }

                    if (isError) currentToolEl.classList.add('tool-failed');
                    currentToolEl = null;
                }

            } else if (item.type === 'image') {
                ensureBotEl();
                const imgEl = document.createElement('img');
                imgEl.src = item.content;
                imgEl.alt = 'screenshot';
                imgEl.style.cssText = 'max-width:600px;border-radius:8px;margin:8px 0;cursor:zoom-in;box-shadow:0 1px 4px rgba(0,0,0,0.1);';
                imgEl.onclick = () => _openImageLightbox(imgEl.src);
                mediaEl.appendChild(imgEl);
                scrollChatToBottom();

            } else if (item.type === 'text') {
                // Intermediate text sent before media items; display it but keep SSE open.
                ensureBotEl();
                contentEl.classList.remove('sse-streaming');
                const textContent = item.content || accumulatedText;
                if (textContent) contentEl.innerHTML = renderMarkdown(textContent);
                applyHighlighting(botEl);
                scrollChatToBottom();

            } else if (item.type === 'video') {
                ensureBotEl();
                const wrapper = document.createElement('div');
                wrapper.innerHTML = _buildVideoHtml(item.content);
                mediaEl.appendChild(wrapper.firstElementChild || wrapper);
                scrollChatToBottom();

            } else if (item.type === 'audio') {
                ensureBotEl();
                const wrapper = document.createElement('div');
                wrapper.innerHTML = _buildAudioHtml(item.content, item.file_name);
                mediaEl.appendChild(wrapper.firstElementChild || wrapper);
                scrollChatToBottom();

            } else if (item.type === 'file') {
                ensureBotEl();
                const fileName = item.file_name || item.content.split('/').pop();
                const fileEl = document.createElement('a');
                fileEl.href = item.content;
                fileEl.download = fileName;
                fileEl.target = '_blank';
                fileEl.className = 'file-attachment';
                fileEl.style.cssText = 'display:inline-flex;align-items:center;gap:6px;padding:8px 14px;margin:8px 0;border-radius:8px;background:var(--bg-secondary,#f3f4f6);color:var(--text-primary,#374151);text-decoration:none;font-size:14px;border:1px solid var(--border-color,#e5e7eb);';
                fileEl.innerHTML = `<i class="fas fa-file-download" style="color:#6b7280;"></i> ${fileName}`;
                mediaEl.appendChild(fileEl);
                scrollChatToBottom();

            } else if (item.type === 'phase') {
                // Coarse progress (e.g. zv install-browser); must not close SSE (unlike "done")
                ensureBotEl();
                const wrap = document.createElement('div');
                wrap.className = 'text-xs sm:text-sm text-slate-600 dark:text-slate-400 border-l-2 border-primary-400 pl-2 py-1 my-0.5';
                wrap.textContent = String(item.content || '');
                stepsEl.appendChild(wrap);
                scrollChatToBottom();

            } else if (item.type === 'done') {
                done = true;
                es.close();
                delete activeStreams[requestId];
                if (clientId && activeRequests[clientId]) {
                    setUserRequestActive(activeRequests[clientId].userEl, false);
                    delete activeRequests[clientId];
                }

                // item.content may be empty when "done" is only a stream-close signal after media.
                const finalText = item.content || accumulatedText;

                if (!botEl && finalText) {
                    if (loadingEl) { loadingEl.remove(); loadingEl = null; }
                    addBotMessage(finalText, new Date((item.timestamp || Date.now() / 1000) * 1000), requestId);
                } else if (botEl) {
                    contentEl.classList.remove('sse-streaming');
                    if (finalText) contentEl.innerHTML = renderMarkdown(finalText);
                    contentEl.dataset.rawMd = finalText || '';
                    const copyBtn = botEl.querySelector('.copy-msg-btn');
                    if (copyBtn && finalText) copyBtn.style.display = '';
                    applyHighlighting(botEl);
                }
                scrollChatToBottom();

                if (titleInfo) {
                    generateSessionTitle(titleInfo.sid, titleInfo.userMsg, '');
                    titleInfo = null;
                } else if (sessionPanelOpen) {
                    loadSessionList();
                }

            } else if (item.type === 'error') {
                done = true;
                es.close();
                delete activeStreams[requestId];
                if (clientId && activeRequests[clientId]) {
                    setUserRequestActive(activeRequests[clientId].userEl, false);
                    delete activeRequests[clientId];
                }
                if (loadingEl) { loadingEl.remove(); loadingEl = null; }
                addBotMessage(t('error_send'), new Date());
            }
        };

        es.onerror = function() {
            es.close();
            delete activeStreams[requestId];

            const meta = clientId ? activeRequests[clientId] : null;
            if (clientId && (!meta || meta.cancelled)) return;
            if (done) return;

            if (currentReasoningEl) {
                finalizeThinking(currentReasoningEl, reasoningStartTime, reasoningText);
                currentReasoningEl = null;
                reasoningText = '';
            }

            if (reconnectCount < MAX_RECONNECTS) {
                reconnectCount++;
                const delay = Math.min(RECONNECT_BASE_MS * reconnectCount, 5000);
                console.warn(`[SSE] connection lost for ${requestId}, reconnecting in ${delay}ms (attempt ${reconnectCount}/${MAX_RECONNECTS})`);
                setTimeout(connect, delay);
                return;
            }

            // Exhausted retries, show whatever we have
            if (loadingEl) { loadingEl.remove(); loadingEl = null; }
            if (clientId && activeRequests[clientId]) {
                setUserRequestActive(activeRequests[clientId].userEl, false);
                delete activeRequests[clientId];
            }
            if (!botEl) {
                addBotMessage(t('error_send'), new Date());
            } else if (accumulatedText) {
                contentEl.classList.remove('sse-streaming');
                contentEl.innerHTML = renderMarkdown(accumulatedText);
                applyHighlighting(botEl);
                bindChatKnowledgeLinks(botEl);
            }
        };
    }

    connect();
}

function startPolling() {
    const gen = ++pollGeneration;
    isPolling = true;
    let pollInFlight = false;

    function poll() {
        if (gen !== pollGeneration) return;
        if (pollInFlight) return;
        if (document.hidden) { setTimeout(poll, 10000); return; }

        pollInFlight = true;
        fetch('/poll', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        })
        .then(r => r.json())
        .then(data => {
            pollInFlight = false;
            if (gen !== pollGeneration) return;
            if (data.status === 'success' && data.has_content) {
                const rid = data.request_id;
                if (loadingContainers[rid]) {
                    loadingContainers[rid].remove();
                    delete loadingContainers[rid];
                }
                const welcomeScreen = document.getElementById('welcome-screen');
                if (welcomeScreen) welcomeScreen.remove();
                if (data.type === 'audio') {
                    const el = addBotMessage('', new Date(data.timestamp * 1000), rid);
                    const mediaEl = el.querySelector('.media-content');
                    if (mediaEl) {
                        const wrapper = document.createElement('div');
                        wrapper.innerHTML = _buildAudioHtml(data.content, data.file_name);
                        mediaEl.appendChild(wrapper.firstElementChild || wrapper);
                    }
                } else {
                    addBotMessage(data.content, new Date(data.timestamp * 1000), rid);
                }
                scrollChatToBottom();
            }
            const delay = (data.status === 'success' && data.has_content) ? 5000 : 10000;
            setTimeout(poll, delay);
        })
        .catch(() => { pollInFlight = false; setTimeout(poll, 10000); });
    }
    poll();
}

function createUserMessageEl(content, timestamp, attachments, options = {}) {
    const el = document.createElement('div');
    el.className = 'user-message flex justify-end px-4 sm:px-6 py-3';
    if (options.clientId) el.dataset.clientId = options.clientId;
    if (options.seq !== undefined && options.seq !== null) el.dataset.seq = options.seq;
    el.dataset.rawMessage = content || '';

    let attachHtml = '';
    if (attachments && attachments.length > 0) {
        const items = attachments.map(a => {
            if (a.file_type === 'image') {
                return `<img src="${a.preview_url}" alt="${escapeHtml(a.file_name)}" class="user-msg-image">`;
            }
            const icon = a.file_type === 'video' ? 'fa-film' : 'fa-file-alt';
            return `<div class="user-msg-file"><i class="fas ${icon}"></i> ${escapeHtml(a.file_name)}</div>`;
        }).join('');
        attachHtml = `<div class="user-msg-attachments">${items}</div>`;
    }

    const textHtml = content ? renderMarkdown(content) : '';
    el.innerHTML = `
        <div class="max-w-[75%] sm:max-w-[60%]">
            <div class="bg-primary-400 text-white rounded-2xl px-4 py-2.5 text-sm leading-relaxed msg-content user-bubble">
                ${attachHtml}${textHtml}
            </div>
            <div class="user-msg-meta">
                <button class="user-msg-action user-msg-cancel hidden" data-action="cancel" title="${t('tip_cancel_request')}">
                    <i class="fas fa-stop"></i>
                </button>
                <button class="user-msg-action" data-action="edit" title="${t('tip_edit_message')}">
                    <i class="fas fa-pen"></i>
                </button>
                <span class="user-msg-status"></span>
                <span>${formatTime(timestamp)}</span>
            </div>
        </div>
    `;
    return el;
}

function renderToolCallsHtml(toolCalls) {
    if (!toolCalls || toolCalls.length === 0) return '';
    return toolCalls.map(tc => {
        const argsStr = formatToolArgs(tc.arguments || {});
        const resultStr = tc.result ? escapeHtml(String(tc.result)) : '';
        const hasResult = !!resultStr;
        return `
<div class="agent-step agent-tool-step">
    <div class="tool-header" onclick="this.parentElement.classList.toggle('expanded')">
        <i class="fas fa-check text-primary-400 flex-shrink-0 tool-icon"></i>
        <span class="tool-name">${escapeHtml(tc.name || '')}</span>
        <i class="fas fa-chevron-right tool-chevron"></i>
    </div>
    <div class="tool-detail">
        <div class="tool-detail-section">
            <div class="tool-detail-label">Input</div>
            <pre class="tool-detail-content">${argsStr}</pre>
        </div>
        ${hasResult ? `
        <div class="tool-detail-section tool-output-section">
            <div class="tool-detail-label">Output</div>
            <pre class="tool-detail-content">${resultStr}</pre>
        </div>` : ''}
    </div>
</div>`;
    }).join('');
}

// Cap for rendering reasoning content in the bubble. Beyond this size,
// we skip markdown rendering entirely and show plain text head + tail to
// keep the page responsive (very long chains-of-thought can otherwise
// stall or crash the browser when re-parsed by marked.js).
// Keep this in sync with backend MAX_STORED_REASONING_CHARS and
// MAX_REASONING_STREAM_CHARS so storage / SSE / display stay aligned.
const REASONING_RENDER_CAP = 4 * 1024; // 4 KB

function _truncateReasoningForDisplay(text) {
    if (!text || text.length <= REASONING_RENDER_CAP) return { text, truncated: false, omitted: 0 };
    const half = Math.floor(REASONING_RENDER_CAP / 2);
    const head = text.slice(0, half);
    const tail = text.slice(-half);
    return {
        text: head + '\n\n... [' + (text.length - head.length - tail.length) + ' chars omitted] ...\n\n' + tail,
        truncated: true,
        omitted: text.length - head.length - tail.length,
    };
}

function _renderReasoningBody(text) {
    // For short reasoning, render as markdown. For long ones, fall back to
    // an escaped <pre> block to avoid expensive markdown parsing.
    const { text: shown, truncated } = _truncateReasoningForDisplay(text);
    if (truncated || shown.length > REASONING_RENDER_CAP) {
        return '<pre class="thinking-stream-pre">' + escapeHtml(shown) + '</pre>';
    }
    return renderMarkdown(shown);
}

function finalizeThinking(el, startTime, text) {
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    el.querySelector('.thinking-summary').textContent = t('thinking_done');
    const fullDiv = el.querySelector('.thinking-full');
    fullDiv.innerHTML = `<div class="thinking-duration">${t('thinking_duration')} ${elapsed}s</div>` + _renderReasoningBody(text);
}

function renderThinkingHtml(text) {
    if (!text || !text.trim()) return '';
    const full = text.trim();
    return `
<div class="agent-step agent-thinking-step">
    <div class="thinking-header" onclick="this.parentElement.classList.toggle('expanded')">
        <i class="fas fa-lightbulb text-amber-400 flex-shrink-0"></i>
        <span class="thinking-summary">${t('thinking_done')}</span>
        <i class="fas fa-chevron-right thinking-chevron"></i>
    </div>
    <div class="thinking-full">${_renderReasoningBody(full)}</div>
</div>`;
}

function renderStepsHtml(steps) {
    if (!steps || steps.length === 0) return { stepsHtml: '', finalContent: '' };

    // Find the index of the last content step 闁?it becomes the main answer, not a step
    let lastContentIdx = -1;
    for (let i = steps.length - 1; i >= 0; i--) {
        if (steps[i].type === 'content') { lastContentIdx = i; break; }
    }

    let html = '';
    let lastContentText = '';
    for (let i = 0; i < steps.length; i++) {
        const step = steps[i];
        if (step.type === 'thinking') {
            html += renderThinkingHtml(step.content);
        } else if (step.type === 'content') {
            if (i === lastContentIdx) {
                lastContentText = step.content;
            } else {
                html += `<div class="agent-step agent-content-step"><div class="agent-content-body">${renderMarkdown(step.content)}</div></div>`;
            }
        } else if (step.type === 'tool') {
            const argsStr = formatToolArgs(step.arguments || {});
            const resultStr = step.result ? escapeHtml(String(step.result)) : '';
            html += `
<div class="agent-step agent-tool-step">
    <div class="tool-header" onclick="this.parentElement.classList.toggle('expanded')">
        <i class="fas fa-check text-primary-400 flex-shrink-0 tool-icon"></i>
        <span class="tool-name">${escapeHtml(step.name || '')}</span>
        <i class="fas fa-chevron-right tool-chevron"></i>
    </div>
    <div class="tool-detail">
        <div class="tool-detail-section">
            <div class="tool-detail-label">Input</div>
            <pre class="tool-detail-content">${argsStr}</pre>
        </div>
        ${resultStr ? `
        <div class="tool-detail-section tool-output-section">
            <div class="tool-detail-label">Output</div>
            <pre class="tool-detail-content">${resultStr}</pre>
        </div>` : ''}
    </div>
</div>`;
            // If this tool sent a file (send/read tool), render the media inline
            // so it persists across page refreshes (SSE-only file events are not stored).
            const mediaHtml = _renderSentFileFromToolResult(step);
            if (mediaHtml) html += mediaHtml;
        } else if (step.type === 'audio') {
            const audioPath = step.path || step.url || '';
            if (audioPath) {
                const fileName = step.file_name || audioPath.split('/').pop();
                html += `<div class="agent-step">${_buildAudioHtml(audioPath, fileName)}</div>`;
            }
        }
    }
    return { stepsHtml: html, lastContentText };
}

// Extract file-to-send metadata from a tool's result and render an inline preview.
// Returns '' if the result isn't a file_to_send payload.
function _renderSentFileFromToolResult(step) {
    if (!step || !step.result) return '';
    let payload;
    try {
        payload = typeof step.result === 'string' ? JSON.parse(step.result) : step.result;
    } catch (_) { return ''; }
    if (!payload || payload.type !== 'file_to_send' || !payload.path) return '';
    const webUrl = _toWebUrl(payload.path);
    const fileType = payload.file_type || 'file';
    const fileName = payload.file_name || payload.path.split('/').pop();
    if (fileType === 'image') {
        return `<div class="agent-step">${_buildImageHtml(webUrl)}</div>`;
    }
    if (fileType === 'video') {
        return `<div class="agent-step">${_buildVideoHtml(webUrl)}</div>`;
    }
    if (fileType === 'audio') {
        return `<div class="agent-step">${_buildAudioHtml(webUrl, fileName)}</div>`;
    }
    return `<div class="agent-step"><a href="${webUrl}" download="${escapeHtml(fileName)}" target="_blank" ` +
        `style="display:inline-flex;align-items:center;gap:6px;padding:8px 14px;margin:8px 0;border-radius:8px;` +
        `background:var(--bg-secondary,#f3f4f6);color:var(--text-primary,#374151);text-decoration:none;font-size:14px;` +
        `border:1px solid var(--border-color,#e5e7eb);">` +
        `<i class="fas fa-file-download" style="color:#6b7280;"></i> ${escapeHtml(fileName)}</a></div>`;
}

function createBotMessageEl(content, timestamp, requestId, msg) {
    const el = document.createElement('div');
    el.className = 'flex gap-3 px-4 sm:px-6 py-3';
    if (requestId) el.dataset.requestId = requestId;
    if (msg && msg._seq !== undefined && msg._seq !== null) el.dataset.seq = msg._seq;

    let stepsHtml = '';
    let displayContent = content;

    if (msg && msg.steps && msg.steps.length > 0) {
        // New format: ordered steps with interleaved content
        const result = renderStepsHtml(msg.steps);
        stepsHtml = result.stepsHtml;
        // The final content (last text after all steps) is the main answer
        displayContent = content || result.lastContentText;
    } else {
        // Legacy format: separate tool_calls + optional reasoning
        const toolCalls = msg && msg.tool_calls;
        const reasoning = msg && msg.reasoning;
        stepsHtml = renderThinkingHtml(reasoning) + renderToolCallsHtml(toolCalls);
    }

    el.innerHTML = `
        <img src="assets/custom-logo.png" alt="ZVAgent" class="w-8 h-8 rounded-lg flex-shrink-0 object-cover">
        <div class="min-w-0 flex-1 max-w-[85%]">
            <div class="bg-white dark:bg-[#1A1A1A] border border-slate-200 dark:border-white/10 rounded-2xl px-4 py-3 text-sm leading-relaxed msg-content text-slate-700 dark:text-slate-200">
                ${stepsHtml ? `<div class="agent-steps">${stepsHtml}</div>` : ''}
                <div class="answer-content">${renderMarkdown(displayContent)}</div>
                <div class="media-content"></div>
            </div>
            <div class="flex items-center gap-2 mt-1.5">
                <span class="text-xs text-slate-400 dark:text-slate-500">${formatTime(timestamp)}</span>
                <button class="copy-msg-btn text-xs text-slate-300 dark:text-slate-600 hover:text-slate-500 dark:hover:text-slate-400 transition-colors cursor-pointer" title="Copy">
                    <i class="fas fa-copy"></i>
                </button>
            </div>
        </div>
    `;
    el.querySelector('.answer-content').dataset.rawMd = displayContent;
    applyHighlighting(el);
    bindChatKnowledgeLinks(el);
    return el;
}

function addUserMessage(content, timestamp, attachments, options = {}) {
    const el = createUserMessageEl(content, timestamp, attachments, options);
    messagesDiv.appendChild(el);
    _autoScrollEnabled = true;
    scrollChatToBottom(true);
    return el;
}

function addBotMessage(content, timestamp, requestId) {
    const el = createBotMessageEl(content, timestamp, requestId);
    messagesDiv.appendChild(el);
    scrollChatToBottom();
}

function generateClientRequestId() {
    return 'client_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 8);
}

function setUserRequestActive(userEl, active) {
    if (!userEl) return;
    const cancelBtn = userEl.querySelector('.user-msg-cancel');
    if (cancelBtn) cancelBtn.classList.toggle('hidden', !active);
    userEl.classList.toggle('user-message-active', active);
}

function restoreMessageToInput(text, attachments = []) {
    if (!text && (!attachments || attachments.length === 0)) return;
    chatInput.value = text;
    if (attachments && attachments.length > 0) {
        pendingAttachments = attachments.map(a => ({ ...a, _uploading: false }));
        renderAttachmentPreview();
    }
    chatInput.dispatchEvent(new Event('input'));
    chatInput.focus();
    chatInput.selectionStart = chatInput.selectionEnd = chatInput.value.length;
}

function cancelUserRequest(clientId, options = {}) {
    const meta = clientId ? activeRequests[clientId] : null;
    if (!meta || meta.cancelled) {
        if (options.edit && meta) restoreMessageToInput(meta.text || '', meta.attachments || []);
        return;
    }

    meta.cancelled = true;
    setUserRequestActive(meta.userEl, false);

    if (meta.controller) {
        try { meta.controller.abort(); } catch (_) {}
    }
    if (meta.requestId && activeStreams[meta.requestId]) {
        try { activeStreams[meta.requestId].close(); } catch (_) {}
        delete activeStreams[meta.requestId];
    }
    if (meta.loadingEl && meta.loadingEl.isConnected) meta.loadingEl.remove();
    if (meta.botEl && meta.botEl.isConnected) meta.botEl.remove();

    if (meta.requestId) {
        fetch('/cancel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, request_id: meta.requestId })
        }).catch(() => {});
    }

    const status = meta.userEl && meta.userEl.querySelector('.user-msg-status');
    if (status) status.textContent = t('request_cancelled');
    if (options.edit) restoreMessageToInput(meta.text || '', meta.attachments || []);
    delete activeRequests[clientId];
}

// Load conversation history from the server (page 1 = most recent messages).
// Subsequent pages prepend older messages when the user scrolls to the top.
function loadHistory(page) {
    if (historyLoading) return;
    historyLoading = true;

    fetch(`/api/history?session_id=${encodeURIComponent(sessionId)}&page=${page}&page_size=20`)
        .then(r => r.json())
        .then(data => {
            if (data.status !== 'success' || data.messages.length === 0) return;

            const prevScrollHeight = messagesDiv.scrollHeight;
            const isFirstLoad = page === 1;

            // On first load, remove the welcome screen if history exists
            if (isFirstLoad) {
                const ws = document.getElementById('welcome-screen');
                if (ws) ws.remove();
            }

            // Build a fragment of history message elements in chronological order
            const fragment = document.createDocumentFragment();

            if (data.has_more && page > 1) {
                // Keep the "load more" sentinel in place (inserted below)
            }

            const ctxStartSeq = data.context_start_seq || 0;
            let dividerInserted = false;

            data.messages.forEach(msg => {
                const hasContent = msg.content && msg.content.trim();
                const hasToolCalls = msg.role === 'assistant' && msg.tool_calls && msg.tool_calls.length > 0;
                const hasSteps = msg.role === 'assistant' && msg.steps && msg.steps.length > 0;
                if (!hasContent && !hasToolCalls && !hasSteps) return;

                // Insert context divider when transitioning from above to below boundary
                if (ctxStartSeq > 0 && !dividerInserted && msg._seq !== undefined && msg._seq >= ctxStartSeq) {
                    dividerInserted = true;
                    const divider = document.createElement('div');
                    divider.className = 'context-divider';
                    divider.innerHTML = `<span>${t('context_cleared')}</span>`;
                    fragment.appendChild(divider);
                }

                const ts = new Date(msg.created_at * 1000);
                const el = msg.role === 'user'
                    ? createUserMessageEl(msg.content, ts, [], { seq: msg._seq })
                    : createBotMessageEl(msg.content || '', ts, null, msg);
                if (msg.role === 'user' && msg._seq !== undefined && msg._seq !== null) {
                    const meta = el.querySelector('.user-msg-meta');
                    if (meta) {
                        const btn = document.createElement('button');
                        btn.className = 'user-msg-action user-msg-delete';
                        btn.dataset.action = 'delete';
                        btn.title = t('delete_turn_title');
                        btn.innerHTML = '<i class="fas fa-trash-can"></i>';
                        btn.onclick = (event) => {
                            event.stopPropagation();
                            deleteHistoryTurn(sessionId, msg._seq, el);
                        };
                        meta.insertBefore(btn, meta.firstChild);
                    }
                }
                fragment.appendChild(el);
            });

            // If context was cleared but no new messages exist yet, append divider at the end
            if (ctxStartSeq > 0 && !dividerInserted) {
                const divider = document.createElement('div');
                divider.className = 'context-divider';
                divider.innerHTML = `<span>${t('context_cleared')}</span>`;
                fragment.appendChild(divider);
            }

            // Prepend history above any existing messages
            const sentinel = document.getElementById('history-load-more');
            const insertBefore = sentinel ? sentinel.nextSibling : messagesDiv.firstChild;
            messagesDiv.insertBefore(fragment, insertBefore);

            // Manage the "load more" sentinel at the very top
            if (data.has_more) {
                if (!document.getElementById('history-load-more')) {
                    const btn = document.createElement('div');
                    btn.id = 'history-load-more';
                    btn.className = 'flex justify-center py-3';
                    btn.innerHTML = `<button class="text-xs text-slate-400 dark:text-slate-500 hover:text-primary-400 transition-colors" onclick="loadHistory(historyPage + 1)">Load earlier messages</button>`;
                    messagesDiv.insertBefore(btn, messagesDiv.firstChild);
                }
            } else {
                const sentinel = document.getElementById('history-load-more');
                if (sentinel) sentinel.remove();
            }

            historyHasMore = data.has_more;
            historyPage = page;

            if (isFirstLoad) {
                // Use requestAnimationFrame to ensure the DOM has fully rendered
                // before scrolling, otherwise scrollHeight may not reflect new content.
                requestAnimationFrame(() => scrollChatToBottom(true));
            } else {
                // Restore scroll position so loading older messages doesn't jump the view
                messagesDiv.scrollTop = messagesDiv.scrollHeight - prevScrollHeight;
            }
        })
        .catch(() => {})
        .finally(() => { historyLoading = false; });
}

function addLoadingIndicator() {
    const el = document.createElement('div');
    el.className = 'flex gap-3 px-4 sm:px-6 py-3';
    el.innerHTML = `
        <img src="assets/custom-logo.png" alt="ZVAgent" class="w-8 h-8 rounded-lg flex-shrink-0 object-cover">
        <div class="bg-white dark:bg-[#1A1A1A] border border-slate-200 dark:border-white/10 rounded-2xl px-4 py-3">
            <div class="flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-primary-400 animate-pulse-dot" style="animation-delay: 0s"></span>
                <span class="w-2 h-2 rounded-full bg-primary-400 animate-pulse-dot" style="animation-delay: 0.2s"></span>
                <span class="w-2 h-2 rounded-full bg-primary-400 animate-pulse-dot" style="animation-delay: 0.4s"></span>
            </div>
        </div>
    `;
    messagesDiv.appendChild(el);
    scrollChatToBottom();
    return el;
}

function newChat() {
    Object.keys(activeRequests).forEach(clientId => cancelUserRequest(clientId, { edit: false }));
    // Close all active SSE connections for the current session
    Object.values(activeStreams).forEach(es => { try { es.close(); } catch (_) {} });
    activeStreams = {};
    activeRequests = {};

    // Generate a fresh session and persist it so the next page load also starts clean
    sessionId = generateSessionId();
    localStorage.setItem(SESSION_ID_KEY, sessionId);
    loadingContainers = {};
    startPolling();  // bump generation so old loop self-cancels, new loop uses fresh sessionId
    messagesDiv.innerHTML = '';
    const ws = document.createElement('div');
    ws.id = 'welcome-screen';
    ws.className = 'flex flex-col items-center justify-center h-full px-6 pb-16';
    ws.style.paddingTop = '6vh';
    ws.innerHTML = `
        <img src="assets/custom-logo.png" alt="ZVAgent" class="w-16 h-16 rounded-2xl mb-6 shadow-lg shadow-primary-500/20 object-cover">
        <h1 class="text-2xl font-bold text-slate-800 dark:text-slate-100 mb-3">${appConfig.title || 'ZVAgent'}</h1>
        <p class="text-slate-500 dark:text-slate-400 text-center max-w-lg leading-relaxed" data-i18n="welcome_subtitle">${t('welcome_subtitle')}</p>
    `;
    messagesDiv.appendChild(ws);
    if (currentView !== 'chat') navigateTo('chat');

    // Show panel and load full session list, then prepend the new session on top
    const panel = document.getElementById('session-panel');
    if (panel && !sessionPanelOpen) {
        sessionPanelOpen = true;
        panel.classList.remove('hidden');
        _showSessionOverlay();
        _persistPanelState();
    }
    const newSid = sessionId;
    loadSessionList(() => _addOptimisticSessionItem(newSid));
}

// =====================================================================
// Session Panel
// =====================================================================

const SESSION_PANEL_KEY = 'zvagent_session_panel_open';
let sessionPanelOpen = localStorage.getItem(SESSION_PANEL_KEY) === '1';

function _persistPanelState() {
    localStorage.setItem(SESSION_PANEL_KEY, sessionPanelOpen ? '1' : '0');
}

function _isMobileView() {
    return window.innerWidth <= 768;
}

function _showSessionOverlay() {
    if (!_isMobileView()) return;
    const overlay = document.getElementById('session-panel-overlay');
    if (overlay) overlay.classList.remove('hidden');
}

function _hideSessionOverlay() {
    const overlay = document.getElementById('session-panel-overlay');
    if (overlay) overlay.classList.add('hidden');
}

function closeSessionPanel() {
    const panel = document.getElementById('session-panel');
    if (!panel || !sessionPanelOpen) return;
    sessionPanelOpen = false;
    panel.classList.add('hidden');
    _hideSessionOverlay();
    _persistPanelState();
}

function toggleSessionPanel() {
    const panel = document.getElementById('session-panel');
    if (!panel) return;
    sessionPanelOpen = !sessionPanelOpen;
    panel.classList.toggle('hidden', !sessionPanelOpen);
    if (sessionPanelOpen) {
        _showSessionOverlay();
    } else {
        _hideSessionOverlay();
    }
    _persistPanelState();
    if (sessionPanelOpen) loadSessionList();
}

function openSessionPanel() {
    const panel = document.getElementById('session-panel');
    if (!panel || sessionPanelOpen) return;
    sessionPanelOpen = true;
    panel.classList.remove('hidden');
    _showSessionOverlay();
    _persistPanelState();
    loadSessionList();
}

function _restoreSessionPanel() {
    const panel = document.getElementById('session-panel');
    if (!panel) return;
    if (sessionPanelOpen && !_isMobileView()) {
        panel.classList.remove('hidden');
        _showSessionOverlay();
        loadSessionList();
    } else {
        panel.classList.add('hidden');
        _hideSessionOverlay();
    }
}

function _applyInputTooltips() {
    const set = (id, key, pos) => {
        const el = document.getElementById(id);
        if (!el) return;
        el.setAttribute('data-tooltip', t(key));
        el.removeAttribute('title');
        if (pos) el.setAttribute('data-tooltip-pos', pos);
    };
    set('new-chat-btn', 'tip_new_chat');
    set('clear-context-btn', 'tip_clear_context');
    set('attach-btn', 'tip_attach_file');
    set('session-toggle-btn', 'session_history', 'bottom');
}

function _addOptimisticSessionItem(sid) {
    const container = document.getElementById('session-list');
    if (!container) return;

    const emptyEl = container.querySelector('.session-empty');
    if (emptyEl) emptyEl.remove();

    document.querySelectorAll('.session-item.active').forEach(el => el.classList.remove('active'));

    const todayLabel = t('today');
    let firstGroup = container.querySelector('.session-group-label');
    if (!firstGroup || firstGroup.textContent !== todayLabel) {
        const header = document.createElement('div');
        header.className = 'session-group-label';
        header.textContent = todayLabel;
        container.prepend(header);
        firstGroup = header;
    }

    const title = t('new_chat');
    const item = document.createElement('div');
    item.className = 'session-item active';
    item.dataset.sessionId = sid;
    item.innerHTML = `
        <i class="fas fa-message session-icon"></i>
        <span class="session-title" title="${escapeHtml(title)}">${escapeHtml(title)}</span>
        <button class="session-delete" onclick="event.stopPropagation(); deleteSession('${sid}')" title="Delete">
            <i class="fas fa-trash-can"></i>
        </button>
    `;
    item.addEventListener('click', () => switchSession(sid));
    firstGroup.insertAdjacentElement('afterend', item);
}

function _repairSessionTitleMojibake(text) {
    if (!text) return text;
    const suspiciousRe = /[閼存瑨鍓归懞鎺撶毘韫囨瑨骞楅悮顐ュ瘶閻╁弶鐏囬惇澶庡妧閼存繆鍔呴懘鐘哄妵]|[\u5fd9\u6c13\u732b\u8305\u9e93\u6402\u804a-\u807f]/g;
    const score = (text.match(suspiciousRe) || []).length + (text.match(/\ufffd/g) || []).length * 2;
    if (score < 2 || score / Math.max(text.length, 1) < 0.15) return text;

    const tryDecode = (value, encoding) => {
        try {
            const bytes = new Uint8Array([...value].map(ch => ch.charCodeAt(0)));
            return new TextDecoder(encoding, { fatal: true }).decode(bytes).trim();
        } catch (_) {
            return '';
        }
    };

    const candidates = [text];
    const latin = tryDecode(text, 'utf-8');
    if (latin) candidates.push(latin);
    const gbk = tryDecode(text, 'gb18030');
    if (gbk) {
        candidates.push(gbk);
        const gbkThenLatin = tryDecode(gbk, 'utf-8');
        if (gbkThenLatin) candidates.push(gbkThenLatin);
    }

    return candidates.reduce((best, candidate) => {
        const bestScore = (best.match(suspiciousRe) || []).length;
        const candidateScore = (candidate.match(suspiciousRe) || []).length;
        return candidateScore < bestScore ? candidate : best;
    }, text);
}

function _sessionTimeGroup(ts) {
    const now = new Date();
    const d = new Date(ts * 1000);
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today); yesterday.setDate(today.getDate() - 1);
    if (d >= today) return t('today');
    if (d >= yesterday) return t('yesterday');
    return t('earlier');
}

let _sessionPage = 1;
let _sessionHasMore = false;
let _sessionLoading = false;
const _SESSION_PAGE_SIZE = 50;

function loadSessionList(onDone) {
    const container = document.getElementById('session-list');
    if (!container) return;

    _sessionPage = 1;
    _sessionHasMore = false;

    _fetchSessionPage(1, true, onDone);
}

function _fetchSessionPage(page, clear, onDone) {
    if (_sessionLoading) return;
    _sessionLoading = true;

    const container = document.getElementById('session-list');
    if (!container) { _sessionLoading = false; return; }

    // Remove existing "load more" sentinel before fetching
    const oldSentinel = container.querySelector('.session-load-more');
    if (oldSentinel) oldSentinel.remove();

    fetch(`/api/sessions?page=${page}&page_size=${_SESSION_PAGE_SIZE}`)
        .then(r => r.json())
        .then(data => {
            _sessionLoading = false;
            if (data.status !== 'success') return;

            if (clear) container.innerHTML = '';

            const sessions = data.sessions || [];
            _sessionPage = page;
            _sessionHasMore = !!data.has_more;

            if (sessions.length === 0 && page === 1) {
                container.innerHTML = '<div class="session-empty">' + t('untitled_session') + '</div>';
                if (typeof onDone === 'function') onDone();
                return;
            }

            // Track last group label already in the container
            const existingLabels = container.querySelectorAll('.session-group-label');
            let lastGroup = existingLabels.length > 0
                ? existingLabels[existingLabels.length - 1].textContent
                : '';

            sessions.forEach(s => {
                const group = _sessionTimeGroup(s.last_active);
                if (group !== lastGroup) {
                    lastGroup = group;
                    const header = document.createElement('div');
                    header.className = 'session-group-label';
                    header.textContent = group;
                    container.appendChild(header);
                }

                const item = document.createElement('div');
                const isActive = s.session_id === sessionId;
                item.className = 'session-item' + (isActive ? ' active' : '');
                item.dataset.sessionId = s.session_id;

                const title = _repairSessionTitleMojibake(s.title) || t('untitled_session');
                item.innerHTML = `
                    <i class="fas fa-message session-icon"></i>
                    <span class="session-title" title="${escapeHtml(title)}">${escapeHtml(title)}</span>
                    <button class="session-delete" onclick="event.stopPropagation(); deleteSession('${s.session_id}')" title="Delete">
                        <i class="fas fa-trash-can"></i>
                    </button>
                `;
                item.addEventListener('click', () => switchSession(s.session_id));
                container.appendChild(item);
            });

            if (typeof onDone === 'function') onDone();
        })
        .catch(() => { _sessionLoading = false; });
}

function _onSessionListScroll() {
    if (!_sessionHasMore || _sessionLoading) return;
    const container = document.getElementById('session-list');
    if (!container) return;
    // Trigger when scrolled near the bottom (within 60px)
    if (container.scrollHeight - container.scrollTop - container.clientHeight < 60) {
        _fetchSessionPage(_sessionPage + 1, false);
    }
}

// Attach scroll listener once DOM is ready
(function _initSessionScroll() {
    const el = document.getElementById('session-list');
    if (el) {
        el.addEventListener('scroll', _onSessionListScroll);
    } else {
        document.addEventListener('DOMContentLoaded', () => {
            const el2 = document.getElementById('session-list');
            if (el2) el2.addEventListener('scroll', _onSessionListScroll);
        });
    }
})();

function switchSession(newSessionId) {
    if (newSessionId === sessionId) {
        if (currentView !== 'chat') navigateTo('chat');
        return;
    }

    // Switching sessions is only a view change. Do not call /cancel here:
    // in-flight turns should keep running and be persisted to their original
    // session when they finish. The SSE handlers may continue updating detached
    // DOM nodes, but they still consume the stream so backend queues can close.
    loadingContainers = {};

    sessionId = newSessionId;
    localStorage.setItem(SESSION_ID_KEY, sessionId);

    historyPage = 0;
    historyHasMore = false;
    historyLoading = false;

    messagesDiv.innerHTML = '';
    loadHistory(1);
    startPolling();

    document.querySelectorAll('.session-item').forEach(el => {
        el.classList.toggle('active', el.dataset.sessionId === sessionId);
    });

    if (_isMobileView()) closeSessionPanel();
    if (currentView !== 'chat') navigateTo('chat');
}

function deleteSession(sid) {
    showConfirmModal(t('delete_session_title'), t('delete_session_confirm'), () => {
        fetch(`/api/sessions/${encodeURIComponent(sid)}`, { method: 'DELETE' })
            .then(r => r.json())
            .then(data => {
                if (data.status !== 'success') return;
                if (sid === sessionId) {
                    newChat();
                } else {
                    loadSessionList();
                }
            })
            .catch(() => {});
    });
}

function showConfirmModal(title, message, onConfirm) {
    let overlay = document.getElementById('confirm-modal-overlay');
    if (overlay) overlay.remove();

    overlay = document.createElement('div');
    overlay.id = 'confirm-modal-overlay';
    overlay.className = 'confirm-overlay';

    const modal = document.createElement('div');
    modal.className = 'confirm-modal';
    modal.innerHTML = `
        <div class="confirm-title">${escapeHtml(title)}</div>
        <div class="confirm-message">${escapeHtml(message)}</div>
        <div class="confirm-actions">
            <button class="confirm-btn confirm-btn-cancel">${t('confirm_cancel')}</button>
            <button class="confirm-btn confirm-btn-ok">${t('confirm_yes')}</button>
        </div>
    `;
    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    requestAnimationFrame(() => overlay.classList.add('visible'));

    const close = () => {
        overlay.classList.remove('visible');
        setTimeout(() => overlay.remove(), 200);
    };

    overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });
    modal.querySelector('.confirm-btn-cancel').addEventListener('click', close);
    modal.querySelector('.confirm-btn-ok').addEventListener('click', () => {
        close();
        onConfirm();
    });
}

function clearContext() {
    fetch(`/api/sessions/${encodeURIComponent(sessionId)}/clear_context`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.status !== 'success') return;
            // Insert a visual divider in the chat
            const divider = document.createElement('div');
            divider.className = 'context-divider';
            divider.innerHTML = `<span>${t('context_cleared')}</span>`;
            messagesDiv.appendChild(divider);
            scrollChatToBottom();
        })
        .catch(() => {});
}

function generateSessionTitle(sid, userMsg, assistantReply) {
    fetch(`/api/sessions/${encodeURIComponent(sid)}/generate_title`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_message: userMsg, assistant_reply: assistantReply }),
    })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success' && sessionPanelOpen) {
                loadSessionList();
            }
        })
        .catch(() => {});
}

// =====================================================================
// Utilities
// =====================================================================
function formatTime(date) {
    const now = new Date();
    const sameDay = date.getFullYear() === now.getFullYear()
        && date.getMonth() === now.getMonth()
        && date.getDate() === now.getDate();
    const time = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    if (sameDay) return time;
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    if (date.getFullYear() === now.getFullYear()) return `${m}-${d} ${time}`;
    return `${date.getFullYear()}-${m}-${d} ${time}`;
}

function deleteHistoryTurn(sid, seq, userEl) {
    if (seq === undefined || seq === null) return;
    showConfirmModal(t('delete_turn_title'), t('delete_turn_confirm'), () => {
        fetch(`/api/history/${encodeURIComponent(sid)}/${encodeURIComponent(seq)}`, { method: 'DELETE' })
            .then(r => r.json())
            .then(data => {
                if (data.status !== 'success') return;
                let current = userEl;
                const toRemove = [];
                while (current) {
                    toRemove.push(current);
                    current = current.nextElementSibling;
                    if (current && current.classList && current.classList.contains('user-message')) break;
                    if (current && current.id === 'history-load-more') break;
                }
                toRemove.forEach(el => {
                    if (el && el.isConnected) el.remove();
                });
                if (sessionPanelOpen) loadSessionList();
            })
            .catch(() => {});
    });
}

function formatDateTime(ts) {
    const n = Number(ts || 0);
    return n ? formatTime(new Date(n * 1000)) : '-';
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}

function ChannelsHandler_maskSecret(val) {
    if (!val || val.length <= 8) return val;
    return val.slice(0, 4) + '*'.repeat(val.length - 8) + val.slice(-4);
}

function formatToolArgs(args) {
    if (!args || Object.keys(args).length === 0) return '(none)';
    try {
        return escapeHtml(JSON.stringify(args, null, 2));
    } catch (_) {
        return escapeHtml(String(args));
    }
}

function scrollChatToBottom(force) {
    if (force || _autoScrollEnabled) {
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
}

function _updateScrollToBottomBtn() {
    const btn = document.getElementById('scroll-to-bottom-btn');
    if (!btn) return;
    const distFromBottom = messagesDiv.scrollHeight - messagesDiv.scrollTop - messagesDiv.clientHeight;
    btn.classList.toggle('hidden', distFromBottom <= _SCROLL_THRESHOLD);
}

function applyHighlighting(container) {
    const root = container || document;
    setTimeout(() => {
        root.querySelectorAll('pre code').forEach(block => {
            if (block.classList.contains('language-mermaid') || block.classList.contains('lang-mermaid')) return;
            if (!block.classList.contains('hljs')) {
                hljs.highlightElement(block);
            }
        });
        renderMermaidDiagrams(root);
    }, 0);
}

// =====================================================================
// Config View
// =====================================================================
let configProviders = {};
let configApiBases = {};
let configApiKeys = {};
let configCurrentModel = '';
let cfgProviderValue = '';
let cfgModelValue = '';

// --- Custom dropdown helper ---
function initDropdown(el, options, selectedValue, onChange) {
    const textEl = el.querySelector('.cfg-dropdown-text');
    const menuEl = el.querySelector('.cfg-dropdown-menu');
    const selEl = el.querySelector('.cfg-dropdown-selected');

    el._ddValue = selectedValue || '';
    el._ddOnChange = onChange;

    function render() {
        menuEl.innerHTML = '';
        options.forEach(opt => {
            const item = document.createElement('div');
            item.className = 'cfg-dropdown-item' + (opt.value === el._ddValue ? ' active' : '');
            item.textContent = opt.label;
            item.dataset.value = opt.value;
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                el._ddValue = opt.value;
                textEl.textContent = opt.label;
                menuEl.querySelectorAll('.cfg-dropdown-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                el.classList.remove('open');
                if (el._ddOnChange) el._ddOnChange(opt.value);
            });
            menuEl.appendChild(item);
        });
        const sel = options.find(o => o.value === el._ddValue);
        textEl.textContent = sel ? sel.label : (options[0] ? options[0].label : '--');
        if (!sel && options[0]) el._ddValue = options[0].value;
    }

    render();

    if (!el._ddBound) {
        selEl.addEventListener('click', (e) => {
            e.stopPropagation();
            document.querySelectorAll('.cfg-dropdown.open').forEach(d => { if (d !== el) d.classList.remove('open'); });
            el.classList.toggle('open');
        });
        el._ddBound = true;
    }
}

document.addEventListener('click', () => {
    document.querySelectorAll('.cfg-dropdown.open').forEach(d => d.classList.remove('open'));
});

function getDropdownValue(el) { return el._ddValue || ''; }

// --- Config init ---
function initConfigView(data) {
    configProviders = data.providers || {};
    configApiBases = data.api_bases || {};
    configApiKeys = data.api_keys || {};
    configCurrentModel = data.model || '';

    const providerEl = document.getElementById('cfg-provider');
    const providerOpts = Object.entries(configProviders).map(([pid, p]) => ({ value: pid, label: p.label }));

    // if use_linkai is enabled, always select linkai as the provider
    // Otherwise prefer bot_type from config, fall back to model-based detection
    const detected = data.use_linkai ? 'linkai'
        : (data.bot_type && configProviders[data.bot_type] ? data.bot_type : detectProvider(configCurrentModel));
    cfgProviderValue = detected || (providerOpts[0] ? providerOpts[0].value : '');

    initDropdown(providerEl, providerOpts, cfgProviderValue, onProviderChange);

    onProviderChange(cfgProviderValue);
    syncModelSelection(configCurrentModel);

    document.getElementById('cfg-max-tokens').value = data.agent_max_context_tokens || 50000;
    document.getElementById('cfg-max-turns').value = data.agent_max_context_turns || 20;
    document.getElementById('cfg-max-steps').value = data.agent_max_steps || 20;
    document.getElementById('cfg-enable-thinking').checked = data.enable_thinking === true;
    const pwdInput = document.getElementById('cfg-password');
    const maskedPwd = data.web_password_masked || '';
    pwdInput.value = maskedPwd;
    pwdInput.dataset.masked = maskedPwd ? '1' : '';
    pwdInput.dataset.maskedVal = maskedPwd;
    pwdInput.classList.toggle('cfg-key-masked', !!maskedPwd);

    if (maskedPwd) {
        pwdInput.placeholder = 'Password is set';
    } else {
        pwdInput.placeholder = '';
    }

    if (!pwdInput._cfgBound) {
        pwdInput.addEventListener('focus', function() {
            if (this.dataset.masked === '1') {
                this.value = '';
                this.dataset.masked = '';
                this.classList.remove('cfg-key-masked');
            }
        });
        pwdInput.addEventListener('input', function() {
            this.dataset.masked = '';
        });
        pwdInput._cfgBound = true;
    }
}

function detectProvider(model) {
    if (!model) return Object.keys(configProviders)[0] || '';
    for (const [pid, p] of Object.entries(configProviders)) {
        if (pid === 'linkai') continue;
        if (p.models && p.models.includes(model)) return pid;
    }
    return Object.keys(configProviders)[0] || '';
}

function onProviderChange(pid) {
    cfgProviderValue = pid || getDropdownValue(document.getElementById('cfg-provider'));
    const p = configProviders[cfgProviderValue];
    if (!p) return;

    const customTip = document.getElementById('cfg-custom-tip');
    if (customTip) customTip.classList.toggle('hidden', cfgProviderValue !== 'custom');

    const modelEl = document.getElementById('cfg-model-select');
    const modelOpts = (p.models || []).map(m => ({ value: m, label: m }));
    modelOpts.push({ value: '__custom__', label: t('config_custom_option') });

    initDropdown(modelEl, modelOpts, modelOpts[0] ? modelOpts[0].value : '', onModelSelectChange);

    // API Key
    const keyField = p.api_key_field;
    const keyWrap = document.getElementById('cfg-api-key-wrap');
    const keyInput = document.getElementById('cfg-api-key');
    if (keyField) {
        keyWrap.classList.remove('hidden');
        keyInput.classList.add('cfg-key-masked');
        const maskedVal = configApiKeys[keyField] || '';
        keyInput.value = maskedVal;
        keyInput.dataset.field = keyField;
        keyInput.dataset.masked = maskedVal ? '1' : '';
        keyInput.dataset.maskedVal = maskedVal;
        const toggleIcon = document.querySelector('#cfg-api-key-toggle i');
        if (toggleIcon) toggleIcon.className = 'fas fa-eye text-xs';

        if (!keyInput._cfgBound) {
            keyInput.addEventListener('focus', function() {
                if (this.dataset.masked === '1') {
                    this.value = '';
                    this.dataset.masked = '';
                    this.classList.remove('cfg-key-masked');
                }
            });
            keyInput.addEventListener('blur', function() {
                if (!this.value.trim() && this.dataset.maskedVal) {
                    this.value = this.dataset.maskedVal;
                    this.dataset.masked = '1';
                    this.classList.add('cfg-key-masked');
                }
            });
            keyInput.addEventListener('input', function() {
                this.dataset.masked = '';
            });
            keyInput._cfgBound = true;
        }
    } else {
        keyWrap.classList.add('hidden');
        keyInput.value = '';
        keyInput.dataset.field = '';
    }

    // API Base
    const apiBaseInput = document.getElementById('cfg-api-base');
    if (p.api_base_key) {
        document.getElementById('cfg-api-base-wrap').classList.remove('hidden');
        apiBaseInput.value = configApiBases[p.api_base_key] || p.api_base_default || '';
        // Hint the version-path tail (e.g. /v1) so users are reminded to
        // include it themselves. We don't auto-rewrite anything server-side.
        apiBaseInput.placeholder = p.api_base_placeholder || 'https://...';
    } else {
        document.getElementById('cfg-api-base-wrap').classList.add('hidden');
        apiBaseInput.value = '';
        apiBaseInput.placeholder = 'https://...';
    }

    onModelSelectChange(modelOpts[0] ? modelOpts[0].value : '');
}

function onModelSelectChange(val) {
    cfgModelValue = val || getDropdownValue(document.getElementById('cfg-model-select'));
    const customWrap = document.getElementById('cfg-model-custom-wrap');
    if (cfgModelValue === '__custom__') {
        customWrap.classList.remove('hidden');
        document.getElementById('cfg-model-custom').focus();
    } else {
        customWrap.classList.add('hidden');
        document.getElementById('cfg-model-custom').value = '';
    }
}

function syncModelSelection(model) {
    const p = configProviders[cfgProviderValue];
    if (!p) return;

    const modelEl = document.getElementById('cfg-model-select');
    if (p.models && p.models.includes(model)) {
        const modelOpts = (p.models || []).map(m => ({ value: m, label: m }));
        modelOpts.push({ value: '__custom__', label: t('config_custom_option') });
        initDropdown(modelEl, modelOpts, model, onModelSelectChange);
        cfgModelValue = model;
        document.getElementById('cfg-model-custom-wrap').classList.add('hidden');
    } else {
        cfgModelValue = '__custom__';
        const modelOpts = (p.models || []).map(m => ({ value: m, label: m }));
        modelOpts.push({ value: '__custom__', label: t('config_custom_option') });
        initDropdown(modelEl, modelOpts, '__custom__', onModelSelectChange);
        document.getElementById('cfg-model-custom-wrap').classList.remove('hidden');
        document.getElementById('cfg-model-custom').value = model;
    }
}

function getSelectedModel() {
    if (cfgModelValue === '__custom__') {
        return document.getElementById('cfg-model-custom').value.trim();
    }
    return cfgModelValue;
}

function toggleApiKeyVisibility() {
    const input = document.getElementById('cfg-api-key');
    const icon = document.querySelector('#cfg-api-key-toggle i');
    if (input.classList.contains('cfg-key-masked')) {
        input.classList.remove('cfg-key-masked');
        icon.className = 'fas fa-eye-slash text-xs';
    } else {
        input.classList.add('cfg-key-masked');
        icon.className = 'fas fa-eye text-xs';
    }
}

function showStatus(elId, msgKey, isError) {
    const el = document.getElementById(elId);
    el.textContent = t(msgKey);
    el.classList.toggle('text-red-500', !!isError);
    el.classList.toggle('text-primary-500', !isError);
    el.classList.remove('opacity-0');
    setTimeout(() => el.classList.add('opacity-0'), 2500);
}

function saveModelConfig() {
    const model = getSelectedModel();
    if (!model) return;

    const updates = { model: model };
    const p = configProviders[cfgProviderValue];
    updates.use_linkai = (cfgProviderValue === 'linkai');
    if (cfgProviderValue === 'linkai') {
        updates.bot_type = '';
    } else {
        updates.bot_type = cfgProviderValue;
    }
    if (p && p.api_base_key) {
        const base = document.getElementById('cfg-api-base').value.trim();
        if (base) updates[p.api_base_key] = base;
    }
    if (p && p.api_key_field) {
        const keyInput = document.getElementById('cfg-api-key');
        const rawVal = keyInput.value.trim();
        if (rawVal && keyInput.dataset.masked !== '1') {
            updates[p.api_key_field] = rawVal;
        }
    }

    const btn = document.getElementById('cfg-model-save');
    btn.disabled = true;
    fetch('/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ updates })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            configCurrentModel = model;
            if (data.applied) {
                const keyInput = document.getElementById('cfg-api-key');
                Object.entries(data.applied).forEach(([k, v]) => {
                    if (k === 'model') return;
                    if (k.includes('api_key')) {
                        const masked = v.length > 8
                            ? v.substring(0, 4) + '*'.repeat(v.length - 8) + v.substring(v.length - 4)
                            : v;
                        configApiKeys[k] = masked;
                        if (keyInput.dataset.field === k) {
                            keyInput.value = masked;
                            keyInput.dataset.masked = '1';
                            keyInput.dataset.maskedVal = masked;
                            keyInput.classList.add('cfg-key-masked');
                            const toggleIcon = document.querySelector('#cfg-api-key-toggle i');
                            if (toggleIcon) toggleIcon.className = 'fas fa-eye text-xs';
                        }
                    } else {
                        configApiBases[k] = v;
                    }
                });
            }
            showStatus('cfg-model-status', 'config_saved', false);
        } else {
            showStatus('cfg-model-status', 'config_save_error', true);
        }
    })
    .catch(() => showStatus('cfg-model-status', 'config_save_error', true))
    .finally(() => { btn.disabled = false; });
}

function saveAgentConfig() {
    const updates = {
        agent_max_context_tokens: parseInt(document.getElementById('cfg-max-tokens').value) || 50000,
        agent_max_context_turns: parseInt(document.getElementById('cfg-max-turns').value) || 20,
        agent_max_steps: parseInt(document.getElementById('cfg-max-steps').value) || 20,
        enable_thinking: document.getElementById('cfg-enable-thinking').checked,
    };

    const btn = document.getElementById('cfg-agent-save');
    btn.disabled = true;
    fetch('/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ updates })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            showStatus('cfg-agent-status', 'config_saved', false);
        } else {
            showStatus('cfg-agent-status', 'config_save_error', true);
        }
    })
    .catch(() => showStatus('cfg-agent-status', 'config_save_error', true))
    .finally(() => { btn.disabled = false; });
}

function savePasswordConfig() {
    const input = document.getElementById('cfg-password');
    if (input.dataset.masked === '1') {
        showStatus('cfg-password-status', 'config_saved', false);
        return;
    }
    const newPwd = input.value.trim();
    const btn = document.getElementById('cfg-password-save');
    btn.disabled = true;
    fetch('/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ updates: { web_password: newPwd } })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            if (newPwd) {
                showStatus('cfg-password-status', 'config_password_changed', false);
                setTimeout(() => { window.location.reload(); }, 1500);
            } else {
                input.dataset.masked = '';
                input.dataset.maskedVal = '';
                input.classList.remove('cfg-key-masked');
                showStatus('cfg-password-status', 'config_password_cleared', false);
            }
        } else {
            showStatus('cfg-password-status', 'config_save_error', true);
        }
    })
    .catch(() => showStatus('cfg-password-status', 'config_save_error', true))
    .finally(() => { btn.disabled = false; });
}

function loadConfigView() {
    fetch('/config').then(r => r.json()).then(data => {
        if (data.status !== 'success') return;
        appConfig = data;
        initConfigView(data);
    }).catch(() => {});
}

// =====================================================================
// Skills View
// =====================================================================
let toolsLoaded = false;

const TOOL_ICONS = {
    bash: 'fa-terminal',
    edit: 'fa-pen-to-square',
    read: 'fa-file-lines',
    write: 'fa-file-pen',
    ls: 'fa-folder-open',
    send: 'fa-paper-plane',
    web_search: 'fa-magnifying-glass',
    browser: 'fa-globe',
    env_config: 'fa-key',
    scheduler: 'fa-clock',
    memory_get: 'fa-brain',
    memory_search: 'fa-brain',
};

function getToolIcon(name) {
    return TOOL_ICONS[name] || 'fa-wrench';
}

function loadSkillsView() {
    loadToolsSection();
    loadSkillsSection();
}

function loadToolsSection() {
    if (toolsLoaded) return;
    const emptyEl = document.getElementById('tools-empty');
    const listEl = document.getElementById('tools-list');
    const badge = document.getElementById('tools-count-badge');

    fetch('/api/tools').then(r => r.json()).then(data => {
        if (data.status !== 'success') return;
        const tools = data.tools || [];
        emptyEl.classList.add('hidden');
        if (tools.length === 0) {
            emptyEl.classList.remove('hidden');
            emptyEl.innerHTML = `<span class="text-sm text-slate-400 dark:text-slate-500">No built-in tools</span>`;
            return;
        }
        badge.textContent = tools.length;
        badge.classList.remove('hidden');
        listEl.innerHTML = '';
        tools.forEach(tool => {
            const card = document.createElement('div');
            card.className = 'bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 p-4 flex items-start gap-3';
            card.innerHTML = `
                <div class="w-9 h-9 rounded-lg bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center flex-shrink-0">
                    <i class="fas ${getToolIcon(tool.name)} text-blue-500 dark:text-blue-400 text-sm"></i>
                </div>
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2">
                        <span class="font-medium text-sm text-slate-700 dark:text-slate-200 font-mono">${escapeHtml(tool.name)}</span>
                    </div>
                    <p class="text-xs text-slate-400 dark:text-slate-500 mt-1 line-clamp-2">${escapeHtml(tool.description || '--')}</p>
                </div>`;
            listEl.appendChild(card);
        });
        listEl.classList.remove('hidden');
        toolsLoaded = true;
    }).catch(() => {
        emptyEl.classList.remove('hidden');
        emptyEl.innerHTML = `<span class="text-sm text-slate-400 dark:text-slate-500">Failed to load</span>`;
    });
}

function loadSkillsSection() {
    const emptyEl = document.getElementById('skills-empty');
    const listEl = document.getElementById('skills-list');
    const badge = document.getElementById('skills-count-badge');

    fetch('/api/skills').then(r => r.json()).then(data => {
        if (data.status !== 'success') return;
        const skills = data.skills || [];
        if (skills.length === 0) {
            const p = emptyEl.querySelector('p');
            if (p) p.textContent = 'No skills found';
            return;
        }
        badge.textContent = skills.length;
        badge.classList.remove('hidden');
        emptyEl.classList.add('hidden');
        listEl.innerHTML = '';

        skills.forEach(sk => {
            const card = document.createElement('div');
            card.className = 'bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 p-4 flex items-start gap-3 transition-opacity';
            card.dataset.skillName = sk.name;
            card.dataset.skillDesc = sk.description || '';
            card.dataset.enabled = sk.enabled ? '1' : '0';
            renderSkillCard(card, sk);
            listEl.appendChild(card);
        });
    }).catch(() => {});
}

function renderSkillCard(card, sk) {
    const enabled = sk.enabled;
    const iconColor = enabled ? 'text-primary-400' : 'text-slate-300 dark:text-slate-600';
    const trackClass = enabled
        ? 'bg-primary-400'
        : 'bg-slate-200 dark:bg-slate-700';
    const thumbTranslate = enabled ? 'translate-x-3' : 'translate-x-0.5';
    card.innerHTML = `
        <div class="w-9 h-9 rounded-lg bg-amber-50 dark:bg-amber-900/20 flex items-center justify-center flex-shrink-0">
            <i class="fas fa-bolt ${iconColor} text-sm"></i>
        </div>
        <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
                <span class="font-medium text-sm text-slate-700 dark:text-slate-200 truncate flex-1">${escapeHtml(sk.display_name || sk.name)}</span>
                <button
                    role="switch"
                    aria-checked="${enabled}"
                    onclick="toggleSkill('${escapeHtml(sk.name)}', ${enabled})"
                    class="relative inline-flex h-4 w-7 flex-shrink-0 cursor-pointer rounded-full transition-colors duration-200 ease-in-out focus:outline-none ${trackClass}"
                    title="${enabled ? 'Click to disable' : 'Click to enable'}"
                >
                    <span class="inline-block h-3 w-3 mt-0.5 rounded-full bg-white shadow transform transition-transform duration-200 ease-in-out ${thumbTranslate}"></span>
                </button>
            </div>
            <p class="text-xs text-slate-400 dark:text-slate-500 line-clamp-2">${escapeHtml(sk.description || '--')}</p>
        </div>`;
}

function toggleSkill(name, currentlyEnabled) {
    const action = currentlyEnabled ? 'close' : 'open';
    const card = document.querySelector(`[data-skill-name="${CSS.escape(name)}"]`);
    if (card) card.style.opacity = '0.5';

    fetch('/api/skills', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, name })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            if (card) {
                const desc = card.dataset.skillDesc || '';
                card.dataset.enabled = currentlyEnabled ? '0' : '1';
                card.style.opacity = '1';
                renderSkillCard(card, { name, description: desc, enabled: !currentlyEnabled });
            }
        } else {
            if (card) card.style.opacity = '1';
            alert('Operation failed, please try again');
        }
    })
    .catch(() => {
        if (card) card.style.opacity = '1';
            alert('Operation failed, please try again');
    });
}

// =====================================================================
// Skill Evolution View
// =====================================================================
let evolutionLoaded = false;
let evolutionSkills = [];
let evolutionProposals = [];
let evolutionScores = [];
let evolutionEventsPage = 1;
const evolutionEventsPageSize = 5;

function evolutionStatus(message, isError) {
    const el = document.getElementById('evolution-status');
    if (!el) return;
    el.textContent = message || '';
    el.className = 'mb-4 px-4 py-3 rounded-lg text-sm ' + (
        isError
            ? 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-300'
            : 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
    );
    el.classList.toggle('hidden', !message);
    if (message) setTimeout(() => el.classList.add('hidden'), 3500);
}

function selectedEvolutionSkill() {
    const el = document.getElementById('evo-skill-select');
    return el ? el.value : '';
}

function loadEvolutionView(force) {
    if (evolutionLoaded && !force) return;
    fetch('/api/skill-evolution?action=overview')
        .then(r => r.json())
        .then(data => {
            if (data.status !== 'success') {
                evolutionStatus(data.message || '技能进化数据加载失败', true);
                return;
            }
            evolutionLoaded = true;
            evolutionSkills = data.skills || [];
            evolutionProposals = data.proposals || [];
            evolutionScores = data.scores || [];
            renderEvolutionHealth();
            renderEvolutionSkills();
            renderEvolutionProposals(evolutionProposals);
            loadEvolutionEvents();
        })
        .catch(() => evolutionStatus('技能进化数据加载失败', true));
}

function loadEvolutionEvents() {
    const container = document.getElementById('evo-events');
    if (!container) return;
    container.innerHTML = '<div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500"><i class="fas fa-spinner fa-spin mr-2"></i>正在加载事件...</div>';
    fetch('/api/skill-evolution?action=events&limit=100')
        .then(r => r.json())
        .then(data => {
            if (data.status !== 'success') {
                container.innerHTML = `<div class="px-4 py-5 text-sm text-red-500">${escapeHtml(data.message || '事件加载失败')}</div>`;
                return;
            }
            renderEvolutionEvents(data.events || []);
        })
        .catch(() => {
            container.innerHTML = '<div class="px-4 py-5 text-sm text-red-500">事件加载失败。</div>';
        });
}

function renderEvolutionEvents(events) {
    const container = document.getElementById('evo-events');
    if (!container) return;
    if (!events.length) {
        container.innerHTML = '<div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500">暂无进化事件。</div>';
        return;
    }
    container.innerHTML = events.slice(0, 100).map(event => {
        const details = event.details || {};
        const time = event.created_at ? new Date(event.created_at * 1000).toLocaleString() : '';
        const status = event.status || 'success';
        const statusCls = status === 'failed'
            ? 'bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-300'
            : 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-300';
        const summary = evolutionEventSummary(event);
        return `
            <div class="px-4 py-3 flex flex-col md:flex-row md:items-start gap-2">
                <div class="md:w-44 flex-shrink-0 text-xs text-slate-400 dark:text-slate-500">${escapeHtml(time)}</div>
                <div class="flex-1 min-w-0">
                    <div class="flex flex-wrap items-center gap-2">
                        <span class="font-medium text-sm text-slate-800 dark:text-slate-100">${escapeHtml(evolutionActionLabel(event.action || ''))}</span>
                        <span class="px-2 py-0.5 rounded-full text-[11px] ${statusCls}">${escapeHtml(evolutionEventStatusLabel(status))}</span>
                        ${event.skill_name ? `<span class="text-xs text-slate-500 dark:text-slate-400 font-mono">${escapeHtml(event.skill_name)}</span>` : ''}
                        ${event.proposal_id ? `<span class="text-xs text-slate-400 dark:text-slate-500 font-mono">${escapeHtml(event.proposal_id)}</span>` : ''}
                    </div>
                    ${summary ? `<div class="mt-1 text-xs text-slate-500 dark:text-slate-400">${escapeHtml(summary)}</div>` : ''}
                    ${details.backup_id || details.backup_path ? `<div class="mt-1 text-xs text-slate-400 dark:text-slate-500 font-mono truncate">${escapeHtml(details.backup_id || details.backup_path || '')}</div>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

function evolutionActionLabel(action) {
    const labels = {
        auto_queue_completed: '自动排队完成',
        auto_apply_safe_completed: '安全自动应用完成',
        replay_checked: '回放检查',
        validation_checked: '验证检查',
        ai_rewrite_completed: 'AI 改写完成',
        proposal_applied: '提案已应用',
        backup_restored: '备份已恢复',
        evidence_collected: '证据已收集',
        suggestions_generated: '建议已生成'
    };
    return labels[action] || action;
}

function evolutionEventStatusLabel(status) {
    const labels = {
        success: '成功',
        failed: '失败',
        warning: '警告',
        skipped: '已跳过'
    };
    return labels[status] || status;
}

function evolutionEventSummary(event) {
    const d = event.details || {};
    if (event.action === 'auto_queue_completed') {
        return `已创建 ${d.created_count || 0} 个，已跳过 ${d.skipped_count || 0} 个`;
    }
    if (event.action === 'auto_apply_safe_completed') {
        return `已应用 ${d.applied_count || 0} 个，已跳过 ${d.skipped_count || 0} 个`;
    }
    if (event.action === 'replay_checked') {
        const s = d.summary || {};
        return `通过 ${s.passed || 0}，警告 ${s.warnings || 0}，失败 ${s.failed || 0}`;
    }
    if (event.action === 'validate_checked') {
        return d.ok ? '验证通过' : `验证失败（${(d.errors || []).length} 个错误）`;
    }
    if (event.action === 'ai_rewrite_completed') {
        const s = d.replay_summary || {};
        return `AI 改写完成，回放失败 ${s.failed || 0}，警告 ${s.warnings || 0}`;
    }
    if (event.action === 'apply_completed') {
        return '提案已应用并完成备份';
    }
    if (event.action === 'rollback_completed') {
        return `已从备份 ${d.backup_id || ''} 恢复`;
    }
    if (event.action === 'auto_learn_created') {
        const s = d.evidence_summary || {};
        return `证据：${s.matched_count || 0} 次匹配，${s.failure_count || 0} 次失败`;
    }
    if (event.action === 'draft_created') {
        return `建议 ${d.suggestions_count || 0} 条`;
    }
    return '';
}

function evolutionEventFilterParams() {
    const startEl = document.getElementById('evo-events-start');
    const endEl = document.getElementById('evo-events-end');
    const params = new URLSearchParams({
        action: 'events',
        limit: String(evolutionEventsPageSize),
        offset: String((Math.max(1, evolutionEventsPage) - 1) * evolutionEventsPageSize),
    });
    const startValue = startEl ? startEl.value : '';
    const endValue = endEl ? endEl.value : '';
    if (startValue) {
        const startTs = Math.floor(new Date(startValue).getTime() / 1000);
        if (!Number.isNaN(startTs)) params.set('start_at', String(startTs));
    }
    if (endValue) {
        const endTs = Math.floor(new Date(endValue).getTime() / 1000);
        if (!Number.isNaN(endTs)) params.set('end_at', String(endTs));
    }
    return params;
}

function evolutionSearchEvents() {
    evolutionEventsPage = 1;
    loadEvolutionEvents(1);
}

function evolutionResetEventFilters() {
    const startEl = document.getElementById('evo-events-start');
    const endEl = document.getElementById('evo-events-end');
    if (startEl) startEl.value = '';
    if (endEl) endEl.value = '';
    evolutionEventsPage = 1;
    loadEvolutionEvents(1);
}

function loadEvolutionEvents(page) {
    const container = document.getElementById('evo-events');
    const pager = document.getElementById('evo-events-pager');
    if (!container) return;
    evolutionEventsPage = Math.max(1, Number(page || evolutionEventsPage || 1));
    if (pager) pager.classList.add('hidden');
    container.innerHTML = '<div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500"><i class="fas fa-spinner fa-spin mr-2"></i>正在加载事件...</div>';
    fetch(`/api/skill-evolution?${evolutionEventFilterParams().toString()}`)
        .then(r => r.json())
        .then(data => {
            if (data.status !== 'success') {
                container.innerHTML = `<div class="px-4 py-5 text-sm text-red-500">${escapeHtml(data.message || '事件加载失败')}</div>`;
                return;
            }
            renderEvolutionEvents(data.events || [], data);
        })
        .catch(() => {
            container.innerHTML = '<div class="px-4 py-5 text-sm text-red-500">事件加载失败。</div>';
        });
}

function renderEvolutionEvents(events, meta) {
    const container = document.getElementById('evo-events');
    if (!container) return;
    if (!events.length) {
        container.innerHTML = '<div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500">暂无进化事件。</div>';
        renderEvolutionEventPager(meta || { total: 0, limit: evolutionEventsPageSize, offset: 0 });
        return;
    }
    container.innerHTML = events.map(event => {
        const details = event.details || {};
        const time = event.created_at ? new Date(event.created_at * 1000).toLocaleString() : '';
        const status = event.status || 'success';
        const statusCls = status === 'failed'
            ? 'bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-300'
            : 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-300';
        const summary = evolutionEventSummary(event);
        return `
            <div class="px-4 py-3 flex flex-col md:flex-row md:items-start gap-2">
                <div class="md:w-44 flex-shrink-0 text-xs text-slate-400 dark:text-slate-500">${escapeHtml(time)}</div>
                <div class="flex-1 min-w-0">
                    <div class="flex flex-wrap items-center gap-2">
                        <span class="font-medium text-sm text-slate-800 dark:text-slate-100">${escapeHtml(evolutionActionLabel(event.action || ''))}</span>
                        <span class="px-2 py-0.5 rounded-full text-[11px] ${statusCls}">${escapeHtml(evolutionEventStatusLabel(status))}</span>
                        ${event.skill_name ? `<span class="text-xs text-slate-500 dark:text-slate-400 font-mono">${escapeHtml(event.skill_name)}</span>` : ''}
                        ${event.proposal_id ? `<span class="text-xs text-slate-400 dark:text-slate-500 font-mono">${escapeHtml(event.proposal_id)}</span>` : ''}
                    </div>
                    ${summary ? `<div class="mt-1 text-xs text-slate-500 dark:text-slate-400">${escapeHtml(summary)}</div>` : ''}
                    ${details.backup_id || details.backup_path ? `<div class="mt-1 text-xs text-slate-400 dark:text-slate-500 font-mono truncate">${escapeHtml(details.backup_id || details.backup_path || '')}</div>` : ''}
                </div>
            </div>
        `;
    }).join('');
    renderEvolutionEventPager(meta || {});
}

function renderEvolutionEventPager(meta) {
    const pager = document.getElementById('evo-events-pager');
    if (!pager) return;
    const total = Number(meta.total || 0);
    const limit = Number(meta.limit || evolutionEventsPageSize);
    const offset = Number(meta.offset || 0);
    const page = Math.floor(offset / limit) + 1;
    const totalPages = Math.max(1, Math.ceil(total / limit));
    const start = total ? offset + 1 : 0;
    const end = Math.min(offset + limit, total);
    evolutionEventsPage = page;
    pager.classList.remove('hidden');
    pager.innerHTML = `
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div class="text-xs text-slate-500 dark:text-slate-400">
                每页 5 条，第 ${escapeHtml(String(page))} / ${escapeHtml(String(totalPages))} 页，共 ${escapeHtml(String(total))} 条，当前 ${escapeHtml(String(start))}-${escapeHtml(String(end))}
            </div>
            <div class="flex items-center gap-2">
                <button onclick="loadEvolutionEvents(${page - 1})"
                        ${page <= 1 ? 'disabled' : ''}
                        class="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-white/10 text-xs text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer">上一页</button>
                <button onclick="loadEvolutionEvents(${page + 1})"
                        ${page >= totalPages ? 'disabled' : ''}
                        class="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-white/10 text-xs text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer">下一页</button>
            </div>
        </div>
    `;
}

function renderEvolutionSkills() {
    const select = document.getElementById('evo-skill-select');
    if (!select) return;
    const previous = select.value;
    select.innerHTML = '';
    const listEl = document.getElementById('evo-skill-list');
    if (listEl) listEl.innerHTML = '';
    if (evolutionSkills.length === 0) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = '未找到已安装技能';
        select.appendChild(opt);
        select.disabled = true;
        if (listEl) {
            listEl.innerHTML = '<div class="px-3 py-3 rounded-lg bg-slate-50 dark:bg-white/5 text-sm text-slate-400 dark:text-slate-500">未找到已安装技能。请先安装技能，然后刷新。</div>';
        }
        return;
    }
    select.disabled = false;
    evolutionSkills.forEach(sk => {
        const opt = document.createElement('option');
        opt.value = sk.name;
        opt.textContent = sk.display_name && sk.display_name !== sk.name
            ? `${sk.display_name} (${sk.name})`
            : sk.name;
        select.appendChild(opt);
    });
    if (previous && evolutionSkills.some(s => s.name === previous)) select.value = previous;
    else if (evolutionSkills.some(s => s.name === 'wechat-article-search')) select.value = 'wechat-article-search';
    select.onchange = () => {
        renderEvolutionSkillList();
        document.getElementById('evo-suggestions').innerHTML =
            '<p class="text-slate-400 dark:text-slate-500">为这个技能生成建议。</p>';
        evolutionLoadBackups();
    };
    renderEvolutionSkillList();
    if (select.value) evolutionLoadBackups();
}

function evolutionScoreFor(name) {
    return evolutionScores.find(item => item.skill_name === name) || null;
}

function renderEvolutionHealth() {
    const container = document.getElementById('evo-health');
    if (!container) return;
    const activeScores = (evolutionScores || []).filter(item => item.calls > 0);
    const rows = activeScores.length ? activeScores.slice(0, 6) : (evolutionScores || []).slice(0, 6);
    if (!rows.length) {
        container.innerHTML = '<div class="text-sm text-slate-400 dark:text-slate-500">暂无技能健康数据。</div>';
        return;
    }
    container.innerHTML = rows.map(item => {
        const score = Number(item.score || 0);
        const color = score < 60
            ? 'text-red-500'
            : score < 80
                ? 'text-amber-500'
                : 'text-emerald-500';
        const bar = score < 60
            ? 'bg-red-500'
            : score < 80
                ? 'bg-amber-500'
                : 'bg-emerald-500';
        const priority = item.priority && item.priority !== 'none'
            ? `<span class="px-2 py-0.5 rounded-full text-[11px] bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-300">${escapeHtml(item.priority)}</span>`
            : '';
        return `
            <div class="rounded-lg border border-slate-200 dark:border-white/10 p-3 bg-slate-50 dark:bg-white/[0.03]">
                <div class="flex items-start justify-between gap-3">
                    <div class="min-w-0">
                        <div class="font-medium text-sm text-slate-800 dark:text-slate-100 truncate">${escapeHtml(item.skill_name || '')}</div>
                        <div class="mt-1 text-xs text-slate-400 dark:text-slate-500">
                            调用 ${escapeHtml(String(item.calls || 0))} | 失败 ${escapeHtml(String(item.failures || 0))} | 平均 ${escapeHtml(String(item.avg_time || 0))} 秒
                        </div>
                    </div>
                    <div class="flex items-center gap-2">
                        ${priority}
                        <span class="font-semibold ${color}">${escapeHtml(String(score))}</span>
                    </div>
                </div>
                <div class="mt-3 h-1.5 rounded-full bg-slate-200 dark:bg-white/10 overflow-hidden">
                    <div class="h-full ${bar}" style="width:${Math.max(0, Math.min(100, score))}%"></div>
                </div>
                <div class="mt-3 flex justify-end">
                    <button onclick="evolutionSelectSkill('${escapeHtml(item.skill_name || '')}'); evolutionAutoLearn('${escapeHtml(item.skill_name || '')}')"
                            class="text-xs text-emerald-600 dark:text-emerald-300 hover:text-emerald-700 dark:hover:text-emerald-200 cursor-pointer">
                        自动学习
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function renderEvolutionSkillList() {
    const listEl = document.getElementById('evo-skill-list');
    const select = document.getElementById('evo-skill-select');
    if (!listEl || !select) return;
    const selected = select.value;
    listEl.innerHTML = evolutionSkills.map(sk => {
        const active = sk.name === selected;
        const display = sk.display_name && sk.display_name !== sk.name ? sk.display_name : sk.name;
        const source = sk.source || '';
        const health = evolutionScoreFor(sk.name);
        const scoreBadge = health
            ? `<span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 dark:bg-white/10 text-slate-400">${escapeHtml(String(health.score))}</span>`
            : '';
        return `
            <button onclick="evolutionSelectSkill('${escapeHtml(sk.name)}')"
                    class="w-full text-left px-3 py-2 rounded-lg border transition-colors cursor-pointer
                           ${active ? 'border-primary-400 bg-primary-50 dark:bg-primary-900/20' : 'border-transparent hover:bg-slate-50 dark:hover:bg-white/5'}">
                <div class="flex items-center justify-between gap-2">
                    <span class="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">${escapeHtml(display)}</span>
                    <span class="flex items-center gap-1">
                        ${scoreBadge}
                        ${source ? `<span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 dark:bg-white/10 text-slate-400">${escapeHtml(source)}</span>` : ''}
                    </span>
                </div>
                <div class="text-xs text-slate-400 dark:text-slate-500 font-mono truncate">${escapeHtml(sk.name)}</div>
            </button>
        `;
    }).join('');
}

function evolutionSelectSkill(name) {
    const select = document.getElementById('evo-skill-select');
    if (!select) return;
    select.value = name;
    renderEvolutionSkillList();
    document.getElementById('evo-suggestions').innerHTML =
        '<p class="text-slate-400 dark:text-slate-500">为这个技能生成建议。</p>';
    evolutionLoadBackups(name);
}

function evolutionSuggest() {
    const name = selectedEvolutionSkill();
    if (!name) return evolutionStatus('请先选择一个技能。', true);
    const box = document.getElementById('evo-suggestions');
    box.innerHTML = '<div class="text-slate-400 dark:text-slate-500"><i class="fas fa-spinner fa-spin mr-2"></i>正在加载...</div>';
    fetch(`/api/skill-evolution?action=suggest&name=${encodeURIComponent(name)}`)
        .then(r => r.json())
        .then(data => {
            if (data.status !== 'success') {
                box.innerHTML = `<p class="text-red-500">${escapeHtml(data.message || '失败')}</p>`;
                return;
            }
            const suggestions = data.suggestions || [];
            box.innerHTML = suggestions.length
                ? suggestions.map((s, i) => `<div class="flex gap-2"><span class="text-xs text-slate-400 mt-0.5">${i + 1}.</span><span>${escapeHtml(s)}</span></div>`).join('')
                : '<p class="text-slate-400 dark:text-slate-500">暂无建议。</p>';
        })
        .catch(() => {
            box.innerHTML = '<p class="text-red-500">建议生成失败。</p>';
        });
}

function evolutionDraft() {
    const name = selectedEvolutionSkill();
    if (!name) return evolutionStatus('请先选择一个技能。', true);
    fetch('/api/skill-evolution', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'draft', name }),
    })
    .then(r => r.json())
    .then(data => {
        if (data.status !== 'success') {
            evolutionStatus(data.message || '草稿创建失败', true);
            return;
        }
        evolutionStatus(`草稿已创建：${data.proposal_id}`, false);
        evolutionLoaded = false;
        loadEvolutionView(true);
    })
    .catch(() => evolutionStatus('草稿创建失败', true));
}

function evolutionAutoLearn(nameOverride) {
    const name = nameOverride || selectedEvolutionSkill();
    if (!name) return evolutionStatus('请先选择一个技能。', true);
    evolutionStatus('正在基于最近使用记录学习并创建提案...', false);
    fetch('/api/skill-evolution', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'auto_learn', name }),
    })
    .then(r => r.json())
    .then(data => {
        if (data.status !== 'success') {
            evolutionStatus(data.message || '自动学习失败', true);
            return;
        }
        const evidence = data.evidence || {};
        evolutionStatus(`自动提案已创建：${data.proposal_id}（匹配 ${evidence.matched_count || 0} 次）`, false);
        const box = document.getElementById('evo-suggestions');
        if (box) {
            const suggestions = data.suggestions || [];
            box.innerHTML = `
                <div class="rounded-lg border border-emerald-200 dark:border-emerald-900/40 bg-emerald-50 dark:bg-emerald-900/10 p-3">
                    <div class="font-medium text-emerald-700 dark:text-emerald-300 mb-2">自动学习提案已生成</div>
                    <div class="text-xs text-emerald-700/80 dark:text-emerald-300/80">
                        扫描日志：${escapeHtml(String(evidence.sample_size || 0))} |
                        匹配：${escapeHtml(String(evidence.matched_count || 0))} |
                        失败：${escapeHtml(String(evidence.failure_count || 0))}
                    </div>
                </div>
                ${suggestions.map((s, i) => `<div class="flex gap-2"><span class="text-xs text-slate-400 mt-0.5">${i + 1}.</span><span>${escapeHtml(s)}</span></div>`).join('')}
            `;
        }
        evolutionLoaded = false;
        loadEvolutionView(true);
    })
    .catch(() => evolutionStatus('自动学习失败', true));
}

function evolutionAutoQueue() {
    evolutionStatus('正在为低健康度技能创建自动学习提案...', false);
    fetch('/api/skill-evolution', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'auto_queue', max_items: 3 }),
    })
    .then(r => r.json())
    .then(data => {
        if (data.status !== 'success') {
            evolutionStatus(data.message || '自动排队失败', true);
            return;
        }
        const created = data.created || [];
        const skipped = data.skipped || [];
        evolutionStatus(`自动排队完成：创建 ${created.length} 个提案，跳过 ${skipped.length} 个。`, false);
        const box = document.getElementById('evo-suggestions');
        if (box) {
            const createdList = created.length
                ? created.map(item => `<div class="flex gap-2"><span class="text-emerald-500">+</span><span>${escapeHtml(item.skill_name || '')}: ${escapeHtml(item.proposal_id || '')}</span></div>`).join('')
                : '<p class="text-slate-400 dark:text-slate-500">没有创建新提案。</p>';
            const skippedList = skipped.length
                ? `<div class="mt-2 text-xs text-slate-400 dark:text-slate-500">已跳过 ${escapeHtml(String(skipped.length))} 个技能：已有待处理自动提案或创建失败。</div>`
                : '';
            box.innerHTML = `
                <div class="rounded-lg border border-emerald-200 dark:border-emerald-900/40 bg-emerald-50 dark:bg-emerald-900/10 p-3">
                    <div class="font-medium text-emerald-700 dark:text-emerald-300 mb-2">自动排队完成</div>
                    <div class="text-sm text-emerald-700/90 dark:text-emerald-300/90 space-y-1">${createdList}</div>
                    ${skippedList}
                </div>
            `;
        }
        evolutionLoaded = false;
        loadEvolutionView(true);
    })
    .catch(() => evolutionStatus('自动排队失败', true));
}

function evolutionAutoApplySafe() {
    showConfirmDialog({
        title: '安全自动应用',
        message: '只自动应用低风险提案：仅修改 SKILL.md、验证通过、回放无失败。是否继续？',
        okText: '自动应用',
        cancelText: t('confirm_cancel'),
        onConfirm: () => {
            evolutionStatus('正在应用安全提案...', false);
            fetch('/api/skill-evolution', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'auto_apply_safe', max_items: 3 }),
            })
            .then(r => r.json())
            .then(data => {
                if (data.status !== 'success') {
                    evolutionStatus(data.message || '自动应用失败', true);
                    return;
                }
                const applied = data.applied || [];
                const skipped = data.skipped || [];
                evolutionStatus(`安全自动应用完成：应用 ${applied.length} 个提案，跳过 ${skipped.length} 个。`, false);
                renderEvolutionAutoApplyResult(data);
                evolutionLoaded = false;
                loadEvolutionView(true);
            })
            .catch(() => evolutionStatus('自动应用失败', true));
        }
    });
}

function renderEvolutionAutoApplyResult(data) {
    const box = document.getElementById('evo-suggestions');
    if (!box) return;
    const applied = data.applied || [];
    const skipped = data.skipped || [];
    const appliedList = applied.length
        ? applied.map(item => `<div class="flex gap-2"><span class="text-emerald-500">+</span><span>${escapeHtml(item.skill_name || '')}: ${escapeHtml(item.proposal_id || '')} | 备份 ${escapeHtml(item.backup_id || '')}</span></div>`).join('')
        : '<p class="text-slate-400 dark:text-slate-500">没有可安全应用的提案。</p>';
    const skippedList = skipped.length
        ? `<div class="mt-3 text-xs text-slate-500 dark:text-slate-400">${escapeHtml(String(skipped.length))} 个提案被安全检查跳过。</div>`
        : '';
    box.innerHTML = `
        <div class="rounded-lg border border-violet-200 dark:border-violet-900/40 bg-violet-50 dark:bg-violet-900/10 p-3">
            <div class="font-medium text-violet-700 dark:text-violet-300 mb-2">安全自动应用完成</div>
            <div class="text-sm text-violet-700/90 dark:text-violet-300/90 space-y-1">${appliedList}</div>
            ${skippedList}
        </div>
    `;
}

function evolutionRunCycle() {
    showConfirmDialog({
        title: '运行进化循环',
        message: '为低健康度技能依次执行自动排队、AI 改写、回放、验证和安全自动应用。是否继续？',
        okText: '运行一轮',
        cancelText: t('confirm_cancel'),
        onConfirm: () => {
            evolutionStatus('正在运行进化循环...', false);
            fetch('/api/skill-evolution', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: 'run_cycle',
                    max_queue: 3,
                    max_apply: 3,
                    enable_ai_rewrite: true,
                }),
            })
            .then(r => r.json())
            .then(data => {
                if (data.status !== 'success') {
                    evolutionStatus(data.message || '进化循环失败', true);
                    return;
                }
                const summary = data.summary || {};
                evolutionStatus(`进化循环完成：排队 ${summary.queued || 0} 个，改写 ${summary.rewritten || 0} 个，应用 ${summary.applied || 0} 个。`, false);
                renderEvolutionCycleResult(data);
                evolutionLoaded = false;
                loadEvolutionView(true);
            })
            .catch(() => evolutionStatus('进化循环失败', true));
        }
    });
}

function renderEvolutionCycleResult(data) {
    const box = document.getElementById('evo-suggestions');
    if (!box) return;
    const summary = data.summary || {};
    const queue = data.queue || {};
    const applied = (data.auto_apply && data.auto_apply.applied) || [];
    const rewriteFailures = (data.rewrites || []).filter(item => !item.ok);
    const queuedList = (queue.created || []).length
        ? (queue.created || []).map(item => `<div class="flex gap-2"><span class="text-indigo-500">+</span><span>${escapeHtml(item.skill_name || '')}: ${escapeHtml(item.proposal_id || '')}</span></div>`).join('')
        : '<p class="text-slate-400 dark:text-slate-500">没有新提案进入队列。</p>';
    const appliedList = applied.length
        ? applied.map(item => `<div class="flex gap-2"><span class="text-emerald-500">✓</span><span>${escapeHtml(item.skill_name || '')}: 备份 ${escapeHtml(item.backup_id || '')}</span></div>`).join('')
        : '<p class="text-slate-400 dark:text-slate-500">没有自动应用提案。</p>';
    const failureText = rewriteFailures.length
        ? `<div class="mt-2 text-xs text-red-500">${escapeHtml(String(rewriteFailures.length))} 个 AI 改写失败。</div>`
        : '';
    box.innerHTML = `
        <div class="rounded-lg border border-indigo-200 dark:border-indigo-900/40 bg-indigo-50 dark:bg-indigo-900/10 p-3">
            <div class="font-medium text-indigo-700 dark:text-indigo-300 mb-2">进化循环完成</div>
            <div class="text-xs text-indigo-700/80 dark:text-indigo-300/80 mb-3">
                排队 ${escapeHtml(String(summary.queued || 0))} |
                改写 ${escapeHtml(String(summary.rewritten || 0))} |
                应用 ${escapeHtml(String(summary.applied || 0))} |
                跳过 ${escapeHtml(String((summary.queue_skipped || 0) + (summary.apply_skipped || 0)))}
            </div>
            <div class="text-sm text-indigo-700/90 dark:text-indigo-300/90 space-y-1">
                <div class="font-medium">已排队</div>
                ${queuedList}
                <div class="font-medium mt-3">已应用</div>
                ${appliedList}
                ${failureText}
            </div>
        </div>
    `;
}

function renderEvolutionProposals(proposals) {
    const container = document.getElementById('evo-proposals');
    if (!container) return;
    if (!proposals || proposals.length === 0) {
        container.innerHTML = '<div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500">暂无提案。</div>';
        return;
    }
    container.innerHTML = '';
    proposals.forEach(p => {
        const item = document.createElement('div');
        item.className = 'px-4 py-4';
        const applied = p.status === 'applied';
        const autoLearned = p.mode === 'auto_learn' || p.status === 'auto_learned';
        const evidence = p.evidence_summary || {};
        const evidenceText = autoLearned
            ? `日志 ${evidence.matched_count || 0}，失败 ${evidence.failure_count || 0}`
            : '';
        const replaySummary = (p.last_replay && p.last_replay.summary) ? p.last_replay.summary : null;
        const replayText = replaySummary
            ? `回放 ${replaySummary.passed || 0}/${replaySummary.total || 0}，警告 ${replaySummary.warnings || 0}`
            : '';
        const aiRewrite = p.last_ai_rewrite || null;
        const aiText = aiRewrite ? 'AI 已改写' : '';
        item.innerHTML = `
            <div class="flex flex-col md:flex-row md:items-center gap-3">
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2">
                        <span class="font-mono text-sm text-slate-700 dark:text-slate-200 truncate">${escapeHtml(p.proposal_id)}</span>
                        <span class="px-2 py-0.5 rounded-full text-[11px] ${applied ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-300' : 'bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-300'}">${escapeHtml(evolutionStatusLabel(p.status || 'draft'))}</span>
                        ${autoLearned ? '<span class="px-2 py-0.5 rounded-full text-[11px] bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-300">自动</span>' : ''}
                    </div>
                    <div class="text-xs text-slate-400 dark:text-slate-500 mt-1">${escapeHtml(p.skill_name)} | ${escapeHtml(p.path || '')}${evidenceText ? ` | ${escapeHtml(evidenceText)}` : ''}${replayText ? ` | ${escapeHtml(replayText)}` : ''}${aiText ? ` | ${escapeHtml(aiText)}` : ''}</div>
                </div>
                <div class="flex items-center gap-2 flex-shrink-0">
                    <button onclick="evolutionViewDiff('${escapeHtml(p.proposal_id)}')"
                            class="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-white/10 text-xs text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10 cursor-pointer">差异</button>
                    <button onclick="evolutionReplay('${escapeHtml(p.proposal_id)}')"
                            class="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-white/10 text-xs text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10 cursor-pointer">回放</button>
                    <button onclick="evolutionAIRewrite('${escapeHtml(p.proposal_id)}')"
                            class="px-3 py-1.5 rounded-lg border border-violet-200 dark:border-violet-900/40 text-violet-600 dark:text-violet-300 hover:bg-violet-50 dark:hover:bg-violet-900/20 text-xs cursor-pointer">AI</button>
                    <button onclick="evolutionValidate('${escapeHtml(p.proposal_id)}')"
                            class="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-white/10 text-xs text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10 cursor-pointer">验证</button>
                    <button onclick="evolutionApply('${escapeHtml(p.proposal_id)}')"
                            class="px-3 py-1.5 rounded-lg bg-primary-500 hover:bg-primary-600 text-xs text-white cursor-pointer">应用</button>
                </div>
            </div>
        `;
        container.appendChild(item);
    });
}

function evolutionValidate(proposalId) {
    fetch('/api/skill-evolution', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'validate', proposal_id: proposalId }),
    })
    .then(r => r.json())
    .then(data => {
        if (data.ok) {
            const warnings = (data.warnings || []).length ? ` 警告：${(data.warnings || []).join('; ')}` : '';
            evolutionStatus(`验证通过。${warnings}`, false);
        } else {
            evolutionStatus(`验证失败：${(data.errors || [data.message || '未知错误']).join('; ')}`, true);
        }
    })
    .catch(() => evolutionStatus('验证失败', true));
}

function evolutionReplay(proposalId) {
    evolutionStatus('正在回放历史检查...', false);
    fetch(`/api/skill-evolution?action=replay&proposal_id=${encodeURIComponent(proposalId)}`)
        .then(r => r.json())
        .then(data => {
            if (data.status !== 'success') {
                evolutionStatus(data.message || '回放失败', true);
                return;
            }
            const summary = data.summary || {};
            evolutionStatus(`回放：通过 ${summary.passed || 0}，警告 ${summary.warnings || 0}，失败 ${summary.failed || 0}。`, (summary.failed || 0) > 0);
            renderEvolutionReplayResult(data);
            evolutionLoaded = false;
            loadEvolutionView(true);
        })
        .catch(() => evolutionStatus('回放失败', true));
}

function renderEvolutionReplayResult(data) {
    const box = document.getElementById('evo-suggestions');
    if (!box) return;
    const summary = data.summary || {};
    const checks = data.checks || [];
    const rows = checks.map(check => {
        const color = check.status === 'passed'
            ? 'text-emerald-600 dark:text-emerald-300'
            : check.status === 'warning'
                ? 'text-amber-600 dark:text-amber-300'
                : 'text-red-600 dark:text-red-300';
        const icon = check.status === 'passed'
            ? 'fa-circle-check'
            : check.status === 'warning'
                ? 'fa-triangle-exclamation'
                : 'fa-circle-xmark';
        return `
            <div class="flex gap-2">
                <i class="fas ${icon} ${color} text-xs mt-1"></i>
                <div class="min-w-0">
                    <div class="font-medium ${color}">${escapeHtml(evolutionReplayTitleLabel(check.title || ''))}</div>
                    <div class="text-xs text-slate-500 dark:text-slate-400">${escapeHtml(evolutionReplayMessageLabel(check.message || ''))}</div>
                </div>
            </div>
        `;
    }).join('');
    box.innerHTML = `
        <div class="rounded-lg border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/[0.03] p-3">
            <div class="font-medium text-slate-800 dark:text-slate-100 mb-2">回放检查：${escapeHtml(data.proposal_id || '')}</div>
            <div class="text-xs text-slate-500 dark:text-slate-400 mb-3">
                通过 ${escapeHtml(String(summary.passed || 0))} |
                警告 ${escapeHtml(String(summary.warnings || 0))} |
                失败 ${escapeHtml(String(summary.failed || 0))}
            </div>
            <div class="space-y-2 text-sm">${rows}</div>
        </div>
    `;
}

function evolutionAIRewrite(proposalId) {
    showConfirmDialog({
        title: 'AI 改写提案',
        message: '这会调用当前模型，只改写提案副本中的 SKILL.md。是否继续？',
        okText: 'AI 改写',
        cancelText: t('confirm_cancel'),
        onConfirm: () => {
            evolutionStatus('AI 正在改写提案 SKILL.md...', false);
            fetch('/api/skill-evolution', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'ai_rewrite', proposal_id: proposalId }),
            })
            .then(r => r.json())
            .then(data => {
                if (data.status !== 'success') {
                    evolutionStatus(data.message || 'AI 改写失败', true);
                    return;
                }
                const validation = data.validation || {};
                const replay = data.replay || {};
                const summary = replay.summary || {};
                evolutionStatus(`AI 改写完成。验证：${validation.ok ? '通过' : '失败'}，回放警告：${summary.warnings || 0}。`, !validation.ok);
                renderEvolutionAIRewriteResult(data);
                evolutionLoaded = false;
                loadEvolutionView(true);
            })
            .catch(() => evolutionStatus('AI 改写失败', true));
        }
    });
}

function evolutionStatusLabel(status) {
    const labels = {
        applied: '已应用',
        draft: '草稿',
        auto_learned: '自动学习',
        ai_rewritten: 'AI 改写',
        unknown: '未知'
    };
    return labels[status] || status || '草稿';
}

function evolutionReplayTitleLabel(title) {
    const labels = {
        'Invocation guidance': '调用条件',
        'Input guidance': '输入说明',
        'Output guidance': '输出说明',
        'Fallback guidance': '失败处理'
    };
    const historical = String(title || '').match(/^Historical (request|failure) (\d+)$/);
    if (historical) return historical[1] === 'request' ? `历史请求 ${historical[2]}` : `历史失败 ${historical[2]}`;
    return labels[title] || title;
}

function evolutionReplayMessageLabel(message) {
    const labels = {
        'Skill instructions mention when to use the skill.': '技能说明已包含何时使用该技能。',
        'Skill instructions do not clearly describe invocation conditions.': '技能说明没有清楚描述调用条件。',
        'Skill instructions mention required inputs.': '技能说明已包含所需输入。',
        'Skill instructions do not clearly describe required inputs.': '技能说明没有清楚描述所需输入。',
        'Skill instructions mention expected outputs.': '技能说明已包含预期输出。',
        'Skill instructions do not clearly describe expected outputs.': '技能说明没有清楚描述预期输出。',
        'Skill instructions mention fallback or error handling.': '技能说明已包含失败处理或兜底方案。',
        'Skill instructions do not mention fallback or error handling.': '技能说明没有提到失败处理或兜底方案。'
    };
    return labels[message] || message;
}

function renderEvolutionAIRewriteResult(data) {
    const box = document.getElementById('evo-suggestions');
    if (!box) return;
    const validation = data.validation || {};
    const replay = data.replay || {};
    const summary = replay.summary || {};
    const errors = (validation.errors || []).map(item => `<div class="text-xs text-red-500">${escapeHtml(item)}</div>`).join('');
    box.innerHTML = `
        <div class="rounded-lg border border-violet-200 dark:border-violet-900/40 bg-violet-50 dark:bg-violet-900/10 p-3">
            <div class="font-medium text-violet-700 dark:text-violet-300 mb-2">AI 改写完成</div>
            <div class="text-xs text-violet-700/80 dark:text-violet-300/80">
                备份：${escapeHtml(data.backup_path || '')}
            </div>
            <div class="mt-3 text-sm text-slate-600 dark:text-slate-300">
                验证：${validation.ok ? '通过' : '失败'} |
                回放：通过 ${escapeHtml(String(summary.passed || 0))}，
                警告 ${escapeHtml(String(summary.warnings || 0))}，
                失败 ${escapeHtml(String(summary.failed || 0))}
            </div>
            ${errors ? `<div class="mt-2">${errors}</div>` : ''}
            <div class="mt-3 text-xs text-slate-500 dark:text-slate-400">应用前请先查看差异。</div>
        </div>
    `;
}

function ensureEvolutionDiffModal() {
    let overlay = document.getElementById('evolution-diff-overlay');
    if (overlay) return overlay;
    overlay = document.createElement('div');
    overlay.id = 'evolution-diff-overlay';
    overlay.className = 'fixed inset-0 z-[80] hidden bg-black/50 backdrop-blur-sm p-3 md:p-6';
    overlay.innerHTML = `
        <div class="h-full max-w-6xl mx-auto bg-white dark:bg-[#111111] border border-slate-200 dark:border-white/10 rounded-xl shadow-2xl flex flex-col overflow-hidden">
            <div class="px-4 py-3 border-b border-slate-200 dark:border-white/10 flex items-center gap-3">
                <div class="min-w-0 flex-1">
                    <h3 id="evolution-diff-title" class="font-semibold text-slate-800 dark:text-slate-100 truncate">提案差异</h3>
                    <p id="evolution-diff-subtitle" class="text-xs text-slate-400 dark:text-slate-500 truncate"></p>
                </div>
                <button onclick="closeEvolutionDiff()"
                        class="w-9 h-9 rounded-lg border border-slate-200 dark:border-white/10 text-slate-500 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10">
                    <i class="fas fa-xmark"></i>
                </button>
            </div>
            <div id="evolution-diff-body" class="flex-1 overflow-auto bg-slate-50 dark:bg-black p-4"></div>
        </div>
    `;
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeEvolutionDiff();
    });
    document.body.appendChild(overlay);
    return overlay;
}

function closeEvolutionDiff() {
    const overlay = document.getElementById('evolution-diff-overlay');
    if (overlay) overlay.classList.add('hidden');
}

function evolutionViewDiff(proposalId) {
    const overlay = ensureEvolutionDiffModal();
    const body = document.getElementById('evolution-diff-body');
    document.getElementById('evolution-diff-title').textContent = `提案差异：${proposalId}`;
    document.getElementById('evolution-diff-subtitle').textContent = '';
    body.innerHTML = '<div class="text-sm text-slate-400 dark:text-slate-500"><i class="fas fa-spinner fa-spin mr-2"></i>正在加载差异...</div>';
    overlay.classList.remove('hidden');
    fetch(`/api/skill-evolution?action=diff&proposal_id=${encodeURIComponent(proposalId)}`)
        .then(r => r.json())
        .then(data => {
            if (data.status !== 'success') {
                body.innerHTML = `<div class="text-sm text-red-500">${escapeHtml(data.message || '差异加载失败')}</div>`;
                return;
            }
            document.getElementById('evolution-diff-subtitle').textContent =
                `${data.skill_name || ''} · ${data.editable_skill_dir || ''}`;
            const files = data.files || [];
            if (!files.length) {
                body.innerHTML = '<div class="text-sm text-slate-400 dark:text-slate-500">这个提案没有文件改动。</div>';
                return;
            }
            body.innerHTML = files.map(file => renderEvolutionDiffFile(file)).join('');
        })
        .catch(() => {
            body.innerHTML = '<div class="text-sm text-red-500">差异加载失败。</div>';
        });
}

function renderEvolutionDiffFile(file) {
    const lines = String(file.diff || '').split('\n');
    const rendered = lines.map(line => {
        let cls = 'text-slate-500 dark:text-slate-400';
        if (line.startsWith('+') && !line.startsWith('+++')) cls = 'bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-300';
        else if (line.startsWith('-') && !line.startsWith('---')) cls = 'bg-red-50 dark:bg-red-950/30 text-red-700 dark:text-red-300';
        else if (line.startsWith('@@')) cls = 'bg-slate-100 dark:bg-white/10 text-slate-600 dark:text-slate-300';
        return `<div class="px-3 whitespace-pre-wrap break-words ${cls}">${escapeHtml(line || ' ')}</div>`;
    }).join('');
    return `
        <section class="mb-4 rounded-lg border border-slate-200 dark:border-white/10 bg-white dark:bg-[#111111] overflow-hidden">
            <div class="px-3 py-2 border-b border-slate-200 dark:border-white/10 flex items-center justify-between gap-3">
                <span class="font-mono text-xs text-slate-700 dark:text-slate-200 truncate">${escapeHtml(file.path || '')}</span>
                <span class="text-[11px] px-2 py-0.5 rounded-full bg-slate-100 dark:bg-white/10 text-slate-500 dark:text-slate-400">${escapeHtml(evolutionFileStatusLabel(file.status || 'modified'))}</span>
            </div>
            <pre class="m-0 py-2 text-xs leading-5 font-mono overflow-x-auto">${rendered}</pre>
        </section>
    `;
}

function evolutionFileStatusLabel(status) {
    const labels = {
        modified: '已修改',
        added: '新增',
        deleted: '删除',
        renamed: '重命名'
    };
    return labels[status] || status;
}

function evolutionApply(proposalId) {
    showConfirmDialog({
        title: '应用提案',
        message: '这会先备份当前技能，然后替换线上技能。是否继续？',
        okText: '应用',
        cancelText: t('confirm_cancel'),
        onConfirm: () => {
            fetch('/api/skill-evolution', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'apply', proposal_id: proposalId }),
            })
            .then(r => r.json())
            .then(data => {
                if (data.status !== 'success') {
                    evolutionStatus(data.message || '应用失败', true);
                    return;
                }
                evolutionStatus(`已应用。备份：${data.backup_id}`, false);
                evolutionLoaded = false;
                loadEvolutionView(true);
                evolutionLoadBackups(data.skill_name);
            })
            .catch(() => evolutionStatus('应用失败', true));
        }
    });
}

function evolutionLoadBackups(name) {
    name = name || selectedEvolutionSkill();
    const container = document.getElementById('evo-backups');
    if (!container || !name) return;
    container.innerHTML = '<div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500"><i class="fas fa-spinner fa-spin mr-2"></i>正在加载...</div>';
    fetch(`/api/skill-evolution?action=backups&name=${encodeURIComponent(name)}`)
        .then(r => r.json())
        .then(data => {
            if (data.status !== 'success') {
                container.innerHTML = `<div class="px-4 py-5 text-sm text-red-500">${escapeHtml(data.message || '加载失败')}</div>`;
                return;
            }
            const backups = data.backups || [];
            if (backups.length === 0) {
                container.innerHTML = '<div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500">暂无备份。</div>';
                return;
            }
            container.innerHTML = backups.map(b => `
                <div class="px-4 py-3 flex flex-col md:flex-row md:items-center gap-2">
                    <div class="flex-1 min-w-0">
                        <div class="font-mono text-sm text-slate-700 dark:text-slate-200 truncate">${escapeHtml(b.backup_id)}</div>
                        <div class="text-xs text-slate-400 dark:text-slate-500 truncate">${escapeHtml(b.path || '')}</div>
                    </div>
                    <button onclick="evolutionRollback('${escapeHtml(name)}', '${escapeHtml(b.backup_id)}')"
                            class="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-white/10 text-xs text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10 cursor-pointer">回滚</button>
                </div>
            `).join('');
        })
        .catch(() => {
            container.innerHTML = '<div class="px-4 py-5 text-sm text-red-500">备份加载失败。</div>';
        });
}

function evolutionRollback(name, backupId) {
    showConfirmDialog({
        title: '回滚技能',
        message: `是否将 ${name} 恢复到备份 ${backupId}？`,
        okText: '回滚',
        cancelText: t('confirm_cancel'),
        onConfirm: () => {
            fetch('/api/skill-evolution', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'rollback', name, backup_id: backupId }),
            })
            .then(r => r.json())
            .then(data => {
                if (data.status !== 'success') {
                    evolutionStatus(data.message || '回滚失败', true);
                    return;
                }
                evolutionStatus(`已回滚。安全备份：${data.safety_backup_id}`, false);
                evolutionLoadBackups(name);
            })
            .catch(() => evolutionStatus('回滚失败', true));
        }
    });
}

// =====================================================================
// Quota View
// =====================================================================
let quotaLoaded = false;
let quotaUsers = [];

function formatTokenCount(n) {
    n = Number(n || 0);
    if (n >= 1000000) return (n / 1000000).toFixed(2) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return String(n);
}

function quotaStatus(message, isError) {
    const el = document.getElementById('quota-status');
    if (!el) return;
    el.textContent = message || '';
    el.className = 'mb-4 px-4 py-3 rounded-lg text-sm ' + (
        isError
            ? 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-300'
            : 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
    );
    el.classList.toggle('hidden', !message);
    if (message) setTimeout(() => el.classList.add('hidden'), 3500);
}

function loadQuotaView(force) {
    if (quotaLoaded && !force) return;
    fetch('/api/quota?action=overview')
        .then(r => r.json())
        .then(data => {
            if (data.status !== 'success') {
                quotaStatus(data.message || '加载额度数据失败', true);
                return;
            }
            quotaLoaded = true;
            quotaUsers = data.users || [];
            const enabledEl = document.getElementById('quota-enabled');
            const defaultEl = document.getElementById('quota-default-tokens');
            const minEl = document.getElementById('quota-min-request');
            if (enabledEl) enabledEl.checked = !!data.enabled;
            if (defaultEl) defaultEl.value = data.default_tokens || 0;
            if (minEl) minEl.value = data.min_request_tokens || 1000;
            renderQuotaStats(data.stats || {});
            renderQuotaUsers(quotaUsers);
            renderQuotaRedeemCodes(data.redeem_codes || []);
            renderQuotaEnabledBadge(!!data.enabled);
        })
        .catch(() => quotaStatus('加载额度数据失败', true));
}

function renderQuotaRedeemCodes(codes) {
    const el = document.getElementById('quota-redeem-codes');
    if (!el) return;
    if (!codes || codes.length === 0) {
        el.innerHTML = '<div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500">暂无兑换码。</div>';
        return;
    }
    el.innerHTML = `
        <table class="w-full text-sm">
            <thead class="bg-slate-50 dark:bg-white/5 text-xs text-slate-400">
                <tr>
                    <th class="text-left font-medium px-4 py-2">Token 数</th>
                    <th class="text-left font-medium px-4 py-2">状态</th>
                    <th class="text-left font-medium px-4 py-2">兑换用户</th>
                    <th class="text-left font-medium px-4 py-2">创建时间</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-white/5">
                ${codes.map(c => `
                    <tr>
                        <td class="px-4 py-3 text-slate-700 dark:text-slate-200">${formatTokenCount(c.token_amount || 0)}</td>
                        <td class="px-4 py-3 text-slate-500 dark:text-slate-400">${escapeHtml(c.status || '')}</td>
                        <td class="px-4 py-3 font-mono text-xs text-slate-500 dark:text-slate-400 max-w-[220px] truncate">${escapeHtml(c.redeemed_by || '-')}</td>
                        <td class="px-4 py-3 text-slate-500 dark:text-slate-400">${c.created_at ? formatDateTime(c.created_at) : '-'}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderQuotaEnabledBadge(enabled) {
    const badge = document.getElementById('quota-enabled-badge');
    if (!badge) return;
    badge.textContent = enabled ? '已启用' : '未启用';
    badge.className = 'px-2 py-1 rounded-full text-xs ' + (
        enabled
            ? 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-300'
            : 'bg-slate-100 dark:bg-white/10 text-slate-500 dark:text-slate-400'
    );
}

function renderQuotaStats(stats) {
    const el = document.getElementById('quota-stats');
    if (!el) return;
    const cards = [
        ['用户数', stats.total_users || 0],
        ['启用用户', stats.active_users || 0],
        ['总额度', formatTokenCount(stats.total_quota || 0)],
        ['已使用', formatTokenCount(stats.total_used || 0)],
    ];
    el.innerHTML = cards.map(([label, value]) => `
        <div class="bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 p-4">
            <div class="text-xs text-slate-400 dark:text-slate-500">${label}</div>
            <div class="mt-1 text-xl font-semibold text-slate-800 dark:text-slate-100">${escapeHtml(String(value))}</div>
        </div>
    `).join('');
}

function renderQuotaUsers(users) {
    const el = document.getElementById('quota-users');
    if (!el) return;
    if (!users || users.length === 0) {
        el.innerHTML = '<div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500">暂无用户。启用额度后，用户发消息会自动出现在这里；你也可以手动设置用户额度。</div>';
        return;
    }
    el.innerHTML = `
        <table class="min-w-full text-sm">
            <thead class="bg-slate-50 dark:bg-white/5 text-slate-400 dark:text-slate-500">
                <tr>
                    <th class="text-left font-medium px-4 py-2">用户</th>
                    <th class="text-left font-medium px-4 py-2">通道</th>
                    <th class="text-right font-medium px-4 py-2">总额度</th>
                    <th class="text-right font-medium px-4 py-2">已使用</th>
                    <th class="text-right font-medium px-4 py-2">剩余</th>
                    <th class="text-left font-medium px-4 py-2">状态</th>
                    <th class="text-right font-medium px-4 py-2">操作</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-white/5">
                ${users.map(u => `
                    <tr class="hover:bg-slate-50 dark:hover:bg-white/5">
                        <td class="px-4 py-3 font-mono text-xs text-slate-700 dark:text-slate-200 max-w-[260px] truncate">${escapeHtml(u.user_id)}</td>
                        <td class="px-4 py-3 text-slate-500 dark:text-slate-400">${escapeHtml(u.channel_type || '')}</td>
                        <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-200">${formatTokenCount(u.quota_tokens)}</td>
                        <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-200">${formatTokenCount(u.used_tokens)}</td>
                        <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-200">${formatTokenCount(u.remaining_tokens)}</td>
                        <td class="px-4 py-3">
                            <span class="px-2 py-0.5 rounded-full text-[11px] ${u.status === 'active' ? 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-300' : 'bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-300'}">${escapeHtml(u.status || 'active')}</span>
                        </td>
                        <td class="px-4 py-3 text-right whitespace-nowrap">
                            <button onclick="quotaSelectUser('${escapeHtml(u.user_id)}')" class="text-xs text-primary-500 hover:text-primary-600 mr-3">日志</button>
                            <button onclick="quotaToggleStatus('${escapeHtml(u.user_id)}', '${u.status === 'active' ? 'disabled' : 'active'}')" class="text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-200">${u.status === 'active' ? '停用' : '启用'}</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function saveQuotaConfig() {
    const enabled = !!document.getElementById('quota-enabled')?.checked;
    const defaultTokens = Number(document.getElementById('quota-default-tokens')?.value || 0);
    const minRequest = Number(document.getElementById('quota-min-request')?.value || 1000);
    fetch('/api/quota', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            action: 'set_config',
            enabled,
            default_tokens: defaultTokens,
            min_request_tokens: minRequest,
        }),
    })
    .then(r => r.json())
    .then(data => {
        if (data.status !== 'success') return quotaStatus(data.message || '保存失败', true);
        quotaLoaded = false;
        quotaStatus('额度设置已保存。', false);
        loadQuotaView(true);
    })
    .catch(() => quotaStatus('保存失败', true));
}

function quotaUserPayload(action) {
    const userId = (document.getElementById('quota-user-id')?.value || '').trim();
    const value = Number(document.getElementById('quota-token-value')?.value || 0);
    if (!userId) {
        quotaStatus('请输入用户 ID。', true);
        return null;
    }
    return action === 'set_quota'
        ? { action, user_id: userId, quota_tokens: value }
        : { action, user_id: userId, delta_tokens: value };
}

function quotaSetUserQuota() {
    const payload = quotaUserPayload('set_quota');
    if (!payload) return;
    quotaPostUser(payload, '额度已设置。');
}

function quotaAddUserQuota() {
    const payload = quotaUserPayload('add_quota');
    if (!payload) return;
    quotaPostUser(payload, '额度已增加。');
}

function quotaGenerateCodes() {
    const tokenAmount = Number(document.getElementById('quota-code-tokens')?.value || 0);
    const count = Number(document.getElementById('quota-code-count')?.value || 1);
    fetch('/api/quota', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'generate_redeem', token_amount: tokenAmount, count })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status !== 'success') return quotaStatus(data.message || '生成失败', true);
        const box = document.getElementById('quota-generated-codes');
        if (box) {
            box.innerHTML = (data.codes || []).map(c =>
                `<div class="px-2 py-1 rounded bg-slate-100 dark:bg-white/5 font-mono text-xs text-slate-700 dark:text-slate-200 select-all">${escapeHtml(c.code)}</div>`
            ).join('');
        }
        quotaLoaded = false;
        quotaStatus('兑换码已生成。请发送给用户，明文兑换码只会在这里显示一次。', false);
        loadQuotaView(true);
    })
    .catch(() => quotaStatus('生成失败', true));
}

function quotaPostUser(payload, successText) {
    fetch('/api/quota', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    })
    .then(r => r.json())
    .then(data => {
        if (data.status !== 'success') return quotaStatus(data.message || '操作失败', true);
        quotaLoaded = false;
        quotaStatus(successText, false);
        loadQuotaView(true);
    })
    .catch(() => quotaStatus('操作失败', true));
}

function quotaToggleStatus(userId, status) {
    quotaPostUser({ action: 'set_status', user_id: userId, status }, status === 'active' ? '用户已启用。' : '用户已停用。');
}

function quotaSelectUser(userId) {
    const input = document.getElementById('quota-user-id');
    if (input) input.value = userId;
    const logsEl = document.getElementById('quota-logs');
    if (logsEl) logsEl.innerHTML = '<div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500"><i class="fas fa-spinner fa-spin mr-2"></i>加载中...</div>';
    fetch(`/api/quota?action=detail&user_id=${encodeURIComponent(userId)}`)
        .then(r => r.json())
        .then(data => {
            if (data.status !== 'success') {
                if (logsEl) logsEl.innerHTML = `<div class="px-4 py-5 text-sm text-red-500">${escapeHtml(data.message || '加载失败')}</div>`;
                return;
            }
            renderQuotaLogs(data.logs || []);
        })
        .catch(() => {
            if (logsEl) logsEl.innerHTML = '<div class="px-4 py-5 text-sm text-red-500">加载日志失败。</div>';
        });
}

function renderQuotaLogs(logs) {
    const el = document.getElementById('quota-logs');
    if (!el) return;
    if (!logs.length) {
        el.innerHTML = '<div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500">该用户暂无用量日志。</div>';
        return;
    }
    el.innerHTML = logs.map(log => `
        <div class="px-4 py-3 flex flex-col md:flex-row md:items-center gap-2">
            <div class="flex-1 min-w-0">
                <div class="text-sm text-slate-700 dark:text-slate-200">${formatTokenCount(log.total_tokens)} Token <span class="text-xs text-slate-400 dark:text-slate-500">(输入 ${formatTokenCount(log.input_tokens)} / 输出 ${formatTokenCount(log.output_tokens)})</span></div>
                <div class="text-xs text-slate-400 dark:text-slate-500 font-mono truncate">${escapeHtml(log.session_id || '')}</div>
            </div>
            <div class="text-xs text-slate-400 dark:text-slate-500">${formatTime(log.created_at * 1000)}</div>
        </div>
    `).join('');
}

function loadQuotaView(force) {
    if (quotaLoaded && !force) return;
    fetch('/api/quota?action=overview')
        .then(r => r.json())
        .then(data => {
            if (data.status !== 'success') {
                quotaStatus(data.message || '加载额度数据失败', true);
                return;
            }
            quotaLoaded = true;
            quotaUsers = data.users || [];
            const enabledEl = document.getElementById('quota-enabled');
            const defaultEl = document.getElementById('quota-default-tokens');
            const minEl = document.getElementById('quota-min-request');
            if (enabledEl) enabledEl.checked = !!data.enabled;
            if (defaultEl) defaultEl.value = data.default_tokens || 0;
            if (minEl) minEl.value = data.min_request_tokens || 1000;
            renderQuotaStats(data.stats || {});
            renderQuotaUsers(quotaUsers);
            renderQuotaRedeemCodes(data.redeem_codes || []);
            renderQuotaEnabledBadge(!!data.enabled);
        })
        .catch(() => quotaStatus('加载额度数据失败', true));
}

function renderQuotaRedeemCodes(codes) {
    const el = document.getElementById('quota-redeem-codes');
    if (!el) return;
    if (!codes || codes.length === 0) {
        el.innerHTML = '<div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500">暂无兑换码。</div>';
        return;
    }
    el.innerHTML = `
        <table class="w-full text-sm">
            <thead class="bg-slate-50 dark:bg-white/5 text-xs text-slate-400">
                <tr>
                    <th class="text-left font-medium px-4 py-2">Token 数</th>
                    <th class="text-left font-medium px-4 py-2">状态</th>
                    <th class="text-left font-medium px-4 py-2">兑换用户</th>
                    <th class="text-left font-medium px-4 py-2">创建时间</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-white/5">
                ${codes.map(c => `
                    <tr>
                        <td class="px-4 py-3 text-slate-700 dark:text-slate-200">${formatTokenCount(c.token_amount || 0)}</td>
                        <td class="px-4 py-3 text-slate-500 dark:text-slate-400">${escapeHtml(c.status || '')}</td>
                        <td class="px-4 py-3 font-mono text-xs text-slate-500 dark:text-slate-400 max-w-[220px] truncate">${escapeHtml(c.redeemed_by || '-')}</td>
                        <td class="px-4 py-3 text-slate-500 dark:text-slate-400">${c.created_at ? formatDateTime(c.created_at) : '-'}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderQuotaEnabledBadge(enabled) {
    const badge = document.getElementById('quota-enabled-badge');
    if (!badge) return;
    badge.textContent = enabled ? '已启用' : '未启用';
    badge.className = 'px-2 py-1 rounded-full text-xs ' + (
        enabled
            ? 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-300'
            : 'bg-slate-100 dark:bg-white/10 text-slate-500 dark:text-slate-400'
    );
}

function renderQuotaStats(stats) {
    const el = document.getElementById('quota-stats');
    if (!el) return;
    const cards = [
        ['用户数', stats.total_users || 0],
        ['启用用户', stats.active_users || 0],
        ['总额度', formatTokenCount(stats.total_quota || 0)],
        ['已使用', formatTokenCount(stats.total_used || 0)],
    ];
    el.innerHTML = cards.map(([label, value]) => `
        <div class="bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 p-4">
            <div class="text-xs text-slate-400 dark:text-slate-500">${label}</div>
            <div class="mt-1 text-xl font-semibold text-slate-800 dark:text-slate-100">${escapeHtml(String(value))}</div>
        </div>
    `).join('');
}

function renderQuotaUsers(users) {
    const el = document.getElementById('quota-users');
    if (!el) return;
    if (!users || users.length === 0) {
        el.innerHTML = '<div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500">暂无用户。启用额度后，用户发消息会自动出现在这里；你也可以手动设置用户额度。</div>';
        return;
    }
    el.innerHTML = `
        <table class="min-w-full text-sm">
            <thead class="bg-slate-50 dark:bg-white/5 text-slate-400 dark:text-slate-500">
                <tr>
                    <th class="text-left font-medium px-4 py-2">用户</th>
                    <th class="text-left font-medium px-4 py-2">通道</th>
                    <th class="text-right font-medium px-4 py-2">总额度</th>
                    <th class="text-right font-medium px-4 py-2">已使用</th>
                    <th class="text-right font-medium px-4 py-2">剩余</th>
                    <th class="text-left font-medium px-4 py-2">状态</th>
                    <th class="text-right font-medium px-4 py-2">操作</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-white/5">
                ${users.map(u => `
                    <tr class="hover:bg-slate-50 dark:hover:bg-white/5">
                        <td class="px-4 py-3 font-mono text-xs text-slate-700 dark:text-slate-200 max-w-[260px] truncate">${escapeHtml(u.user_id)}</td>
                        <td class="px-4 py-3 text-slate-500 dark:text-slate-400">${escapeHtml(u.channel_type || '')}</td>
                        <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-200">${formatTokenCount(u.quota_tokens)}</td>
                        <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-200">${formatTokenCount(u.used_tokens)}</td>
                        <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-200">${formatTokenCount(u.remaining_tokens)}</td>
                        <td class="px-4 py-3">
                            <span class="px-2 py-0.5 rounded-full text-[11px] ${u.status === 'active' ? 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-300' : 'bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-300'}">${escapeHtml(u.status || 'active')}</span>
                        </td>
                        <td class="px-4 py-3 text-right whitespace-nowrap">
                            <button onclick="quotaSelectUser('${escapeHtml(u.user_id)}')" class="text-xs text-primary-500 hover:text-primary-600 mr-3">日志</button>
                            <button onclick="quotaToggleStatus('${escapeHtml(u.user_id)}', '${u.status === 'active' ? 'disabled' : 'active'}')" class="text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-200">${u.status === 'active' ? '停用' : '启用'}</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function saveQuotaConfig() {
    const enabled = !!document.getElementById('quota-enabled')?.checked;
    const defaultTokens = Number(document.getElementById('quota-default-tokens')?.value || 0);
    const minRequest = Number(document.getElementById('quota-min-request')?.value || 1000);
    fetch('/api/quota', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            action: 'set_config',
            enabled,
            default_tokens: defaultTokens,
            min_request_tokens: minRequest,
        }),
    })
    .then(r => r.json())
    .then(data => {
        if (data.status !== 'success') return quotaStatus(data.message || '保存失败', true);
        quotaLoaded = false;
        quotaStatus('额度设置已保存。', false);
        loadQuotaView(true);
    })
    .catch(() => quotaStatus('保存失败', true));
}

function quotaUserPayload(action) {
    const userId = (document.getElementById('quota-user-id')?.value || '').trim();
    const value = Number(document.getElementById('quota-token-value')?.value || 0);
    if (!userId) {
        quotaStatus('请输入用户 ID。', true);
        return null;
    }
    return action === 'set_quota'
        ? { action, user_id: userId, quota_tokens: value }
        : { action, user_id: userId, delta_tokens: value };
}

function quotaSetUserQuota() {
    const payload = quotaUserPayload('set_quota');
    if (!payload) return;
    quotaPostUser(payload, '额度已设置。');
}

function quotaAddUserQuota() {
    const payload = quotaUserPayload('add_quota');
    if (!payload) return;
    quotaPostUser(payload, '额度已增加。');
}

function quotaGenerateCodes() {
    const tokenAmount = Number(document.getElementById('quota-code-tokens')?.value || 0);
    const count = Number(document.getElementById('quota-code-count')?.value || 1);
    fetch('/api/quota', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'generate_redeem', token_amount: tokenAmount, count })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status !== 'success') return quotaStatus(data.message || '生成失败', true);
        const box = document.getElementById('quota-generated-codes');
        if (box) {
            box.innerHTML = (data.codes || []).map(c =>
                `<div class="px-2 py-1 rounded bg-slate-100 dark:bg-white/5 font-mono text-xs text-slate-700 dark:text-slate-200 select-all">${escapeHtml(c.code)}</div>`
            ).join('');
        }
        quotaLoaded = false;
        quotaStatus('兑换码已生成。请发送给用户，明文兑换码只会在这里显示一次。', false);
        loadQuotaView(true);
    })
    .catch(() => quotaStatus('生成失败', true));
}

function quotaPostUser(payload, successText) {
    fetch('/api/quota', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    })
    .then(r => r.json())
    .then(data => {
        if (data.status !== 'success') return quotaStatus(data.message || '操作失败', true);
        quotaLoaded = false;
        quotaStatus(successText, false);
        loadQuotaView(true);
    })
    .catch(() => quotaStatus('操作失败', true));
}

function quotaToggleStatus(userId, status) {
    quotaPostUser({ action: 'set_status', user_id: userId, status }, status === 'active' ? '用户已启用。' : '用户已停用。');
}

function quotaSelectUser(userId) {
    const input = document.getElementById('quota-user-id');
    if (input) input.value = userId;
    const logsEl = document.getElementById('quota-logs');
    if (logsEl) logsEl.innerHTML = '<div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500"><i class="fas fa-spinner fa-spin mr-2"></i>加载中...</div>';
    fetch(`/api/quota?action=detail&user_id=${encodeURIComponent(userId)}`)
        .then(r => r.json())
        .then(data => {
            if (data.status !== 'success') {
                if (logsEl) logsEl.innerHTML = `<div class="px-4 py-5 text-sm text-red-500">${escapeHtml(data.message || '加载失败')}</div>`;
                return;
            }
            renderQuotaLogs(data.logs || []);
        })
        .catch(() => {
            if (logsEl) logsEl.innerHTML = '<div class="px-4 py-5 text-sm text-red-500">加载日志失败。</div>';
        });
}

function renderQuotaLogs(logs) {
    const el = document.getElementById('quota-logs');
    if (!el) return;
    if (!logs.length) {
        el.innerHTML = '<div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500">该用户暂无用量日志。</div>';
        return;
    }
    el.innerHTML = logs.map(log => `
        <div class="px-4 py-3 flex flex-col md:flex-row md:items-center gap-2">
            <div class="flex-1 min-w-0">
                <div class="text-sm text-slate-700 dark:text-slate-200">${formatTokenCount(log.total_tokens)} Token <span class="text-xs text-slate-400 dark:text-slate-500">(输入 ${formatTokenCount(log.input_tokens)} / 输出 ${formatTokenCount(log.output_tokens)})</span></div>
                <div class="text-xs text-slate-400 dark:text-slate-500 font-mono truncate">${escapeHtml(log.session_id || '')}</div>
            </div>
            <div class="text-xs text-slate-400 dark:text-slate-500">${formatTime(log.created_at * 1000)}</div>
        </div>
    `).join('');
}

function quotaUserLabel(user) {
    return (user.display_name || '').trim() || quotaFriendlyUserId(user.user_id || '');
}

function quotaFriendlyUserId(userId) {
    const text = String(userId || '');
    const m = text.match(/^weixin__(.+?)__user__(.+)$/);
    if (m) {
        const tail = m[2].length > 10 ? m[2].slice(0, 10) + '...' : m[2];
        return `微信 ${m[1]} · ${tail}`;
    }
    return text.length > 18 ? text.slice(0, 18) + '...' : text;
}

function quotaJsArg(value) {
    return JSON.stringify(String(value || '')).replace(/</g, '\\u003c');
}

function quotaRenameUser(userId, currentName) {
    const nextName = window.prompt('请输入这个用户的显示名 / 备注名：', currentName || '');
    if (nextName === null) return;
    quotaPostUser(
        { action: 'set_display_name', user_id: userId, display_name: nextName.trim() },
        '用户显示名已更新。'
    );
}

function quotaDeleteUser(userId, displayName) {
    showConfirmDialog({
        title: '删除用户',
        message: `确定删除「${displayName || userId}」吗？该用户会从额度列表中移除，用量日志也会被清理；如果这个微信用户后续再次发消息，会重新创建用户记录。`,
        okText: '删除',
        cancelText: t('confirm_cancel'),
        onConfirm: () => quotaPostUser(
            { action: 'delete_user', user_id: userId },
            '用户已删除。'
        ),
    });
}

function renderQuotaStats(stats) {
    const el = document.getElementById('quota-stats');
    if (!el) return;
    const cards = [
        ['用户数', stats.total_users || 0],
        ['启用用户', stats.active_users || 0],
        ['总额度', formatTokenCount(stats.total_quota || 0)],
        ['已使用', formatTokenCount(stats.total_used || 0)],
    ];
    el.innerHTML = cards.map(([label, value]) => `
        <div class="bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 p-4">
            <div class="text-xs text-slate-400 dark:text-slate-500">${label}</div>
            <div class="mt-1 text-xl font-semibold text-slate-800 dark:text-slate-100">${escapeHtml(String(value))}</div>
        </div>
    `).join('');
}

function renderQuotaUsers(users) {
    const el = document.getElementById('quota-users');
    if (!el) return;
    if (!users || users.length === 0) {
        el.innerHTML = '<div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500">暂无用户。启用额度后，用户发消息会自动出现在这里；你也可以手动设置用户额度。</div>';
        return;
    }
    el.innerHTML = `
        <table class="min-w-full text-sm">
            <thead class="bg-slate-50 dark:bg-white/5 text-slate-400 dark:text-slate-500">
                <tr>
                    <th class="text-left font-medium px-4 py-2">用户</th>
                    <th class="text-left font-medium px-4 py-2">通道</th>
                    <th class="text-right font-medium px-4 py-2">总额度</th>
                    <th class="text-right font-medium px-4 py-2">已使用</th>
                    <th class="text-right font-medium px-4 py-2">剩余</th>
                    <th class="text-left font-medium px-4 py-2">状态</th>
                    <th class="text-right font-medium px-4 py-2">操作</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-white/5">
                ${users.map(u => {
                    const label = quotaUserLabel(u);
                    const rawId = u.user_id || '';
                    const statusText = u.status === 'active' ? 'active' : 'disabled';
                    return `
                        <tr class="hover:bg-slate-50 dark:hover:bg-white/5">
                            <td class="px-4 py-3 max-w-[300px]">
                                <div class="font-medium text-slate-800 dark:text-slate-100 truncate" title="${escapeHtml(label)}">${escapeHtml(label)}</div>
                                <div class="mt-0.5 font-mono text-[11px] text-slate-400 dark:text-slate-500 truncate" title="${escapeHtml(rawId)}">${escapeHtml(rawId)}</div>
                            </td>
                            <td class="px-4 py-3 text-slate-500 dark:text-slate-400">${escapeHtml(u.channel_type || '')}</td>
                            <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-200">${formatTokenCount(u.quota_tokens)}</td>
                            <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-200">${formatTokenCount(u.used_tokens)}</td>
                            <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-200">${formatTokenCount(u.remaining_tokens)}</td>
                            <td class="px-4 py-3">
                                <span class="px-2 py-0.5 rounded-full text-[11px] ${u.status === 'active' ? 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-300' : 'bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-300'}">${escapeHtml(statusText)}</span>
                            </td>
                            <td class="px-4 py-3 text-right whitespace-nowrap">
                                <button onclick="quotaSelectUser(${quotaJsArg(rawId)})" class="text-xs text-primary-500 hover:text-primary-600 mr-3">日志</button>
                                <button onclick="quotaRenameUser(${quotaJsArg(rawId)}, ${quotaJsArg(u.display_name || '')})" class="text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-200 mr-3">重命名</button>
                                <button onclick="quotaToggleStatus(${quotaJsArg(rawId)}, ${quotaJsArg(u.status === 'active' ? 'disabled' : 'active')})" class="text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-200 mr-3">${u.status === 'active' ? '停用' : '启用'}</button>
                                <button onclick="quotaDeleteUser(${quotaJsArg(rawId)}, ${quotaJsArg(label)})" class="text-xs text-red-500 hover:text-red-600">删除</button>
                            </td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;
}

function quotaUserLabel(user) {
    return (user.display_name || '').trim() || quotaFriendlyUserId(user.user_id || '');
}

function quotaFriendlyUserId(userId) {
    const text = String(userId || '');
    const m = text.match(/^weixin__(.+?)__user__(.+)$/);
    if (m) {
        const tail = m[2].length > 10 ? m[2].slice(0, 10) + '...' : m[2];
        return `微信 ${m[1]} · ${tail}`;
    }
    return text.length > 18 ? text.slice(0, 18) + '...' : text;
}

function quotaRenameUser(userId, currentName) {
    const nextName = window.prompt('请输入这个用户的显示名 / 备注名：', currentName || '');
    if (nextName === null) return;
    quotaPostUser(
        { action: 'set_display_name', user_id: userId, display_name: nextName.trim() },
        '用户显示名已更新。'
    );
}

function quotaDeleteUser(userId, displayName) {
    showConfirmDialog({
        title: '删除用户',
        message: `确定删除「${displayName || userId}」吗？该用户会从额度列表中移除，用量日志也会被清理；如果这个微信用户后续再次发消息，会重新创建用户记录。`,
        okText: '删除',
        cancelText: t('confirm_cancel'),
        onConfirm: () => quotaPostUser(
            { action: 'delete_user', user_id: userId },
            '用户已删除。'
        ),
    });
}

function renderQuotaStats(stats) {
    const el = document.getElementById('quota-stats');
    if (!el) return;
    const cards = [
        ['用户数', stats.total_users || 0],
        ['启用用户', stats.active_users || 0],
        ['总额度', formatTokenCount(stats.total_quota || 0)],
        ['已使用', formatTokenCount(stats.total_used || 0)],
    ];
    el.innerHTML = cards.map(([label, value]) => `
        <div class="bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 p-4">
            <div class="text-xs text-slate-400 dark:text-slate-500">${label}</div>
            <div class="mt-1 text-xl font-semibold text-slate-800 dark:text-slate-100">${escapeHtml(String(value))}</div>
        </div>
    `).join('');
}

function renderQuotaUsers(users) {
    const el = document.getElementById('quota-users');
    if (!el) return;
    if (!users || users.length === 0) {
        el.innerHTML = '<div class="px-4 py-5 text-sm text-slate-400 dark:text-slate-500">暂无用户。启用额度后，用户发消息会自动出现在这里；你也可以手动设置用户额度。</div>';
        return;
    }
    el.innerHTML = `
        <table class="min-w-full text-sm">
            <thead class="bg-slate-50 dark:bg-white/5 text-slate-400 dark:text-slate-500">
                <tr>
                    <th class="text-left font-medium px-4 py-2">用户</th>
                    <th class="text-left font-medium px-4 py-2">通道</th>
                    <th class="text-right font-medium px-4 py-2">总额度</th>
                    <th class="text-right font-medium px-4 py-2">已使用</th>
                    <th class="text-right font-medium px-4 py-2">剩余</th>
                    <th class="text-left font-medium px-4 py-2">状态</th>
                    <th class="text-right font-medium px-4 py-2">操作</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-white/5">
                ${users.map(u => {
                    const label = quotaUserLabel(u);
                    const rawId = u.user_id || '';
                    const statusText = u.status === 'active' ? 'active' : 'disabled';
                    return `
                        <tr class="hover:bg-slate-50 dark:hover:bg-white/5">
                            <td class="px-4 py-3 max-w-[300px]">
                                <div class="font-medium text-slate-800 dark:text-slate-100 truncate" title="${escapeHtml(label)}">${escapeHtml(label)}</div>
                                <div class="mt-0.5 font-mono text-[11px] text-slate-400 dark:text-slate-500 truncate" title="${escapeHtml(rawId)}">${escapeHtml(rawId)}</div>
                            </td>
                            <td class="px-4 py-3 text-slate-500 dark:text-slate-400">${escapeHtml(u.channel_type || '')}</td>
                            <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-200">${formatTokenCount(u.quota_tokens)}</td>
                            <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-200">${formatTokenCount(u.used_tokens)}</td>
                            <td class="px-4 py-3 text-right text-slate-700 dark:text-slate-200">${formatTokenCount(u.remaining_tokens)}</td>
                            <td class="px-4 py-3">
                                <span class="px-2 py-0.5 rounded-full text-[11px] ${u.status === 'active' ? 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-300' : 'bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-300'}">${escapeHtml(statusText)}</span>
                            </td>
                            <td class="px-4 py-3 text-right whitespace-nowrap">
                                <button type="button" data-quota-action="logs" data-user-id="${escapeHtml(rawId)}" class="text-xs text-primary-500 hover:text-primary-600 mr-3">日志</button>
                                <button type="button" data-quota-action="rename" data-user-id="${escapeHtml(rawId)}" data-display-name="${escapeHtml(u.display_name || '')}" class="text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-200 mr-3">重命名</button>
                                <button type="button" data-quota-action="toggle" data-user-id="${escapeHtml(rawId)}" data-next-status="${escapeHtml(u.status === 'active' ? 'disabled' : 'active')}" class="text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-200 mr-3">${u.status === 'active' ? '停用' : '启用'}</button>
                                <button type="button" data-quota-action="delete" data-user-id="${escapeHtml(rawId)}" data-display-name="${escapeHtml(label)}" class="text-xs text-red-500 hover:text-red-600">删除</button>
                            </td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;
    el.querySelectorAll('[data-quota-action]').forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.quotaAction;
            const userId = btn.dataset.userId || '';
            if (action === 'logs') quotaSelectUser(userId);
            if (action === 'rename') quotaRenameUser(userId, btn.dataset.displayName || '');
            if (action === 'toggle') quotaToggleStatus(userId, btn.dataset.nextStatus || 'active');
            if (action === 'delete') quotaDeleteUser(userId, btn.dataset.displayName || userId);
        });
    });
}

// =====================================================================
// Memory View
// =====================================================================
let memoryPage = 1;
let memoryCategory = 'memory';   // 'memory' | 'dream'
const memoryPageSize = 10;

function switchMemoryTab(tab) {
    document.querySelectorAll('.memory-tab').forEach(el => el.classList.remove('active'));
    document.getElementById('memory-tab-' + tab).classList.add('active');
    memoryCategory = tab === 'dreams' ? 'dream' : 'memory';
    loadMemoryView(1);
}

function loadMemoryView(page) {
    page = page || 1;
    memoryPage = page;
    fetch(`/api/memory?page=${page}&page_size=${memoryPageSize}&category=${memoryCategory}`).then(r => r.json()).then(data => {
        if (data.status !== 'success') return;
        const emptyEl = document.getElementById('memory-empty');
        const listEl = document.getElementById('memory-list');
        const files = data.list || [];
        const total = data.total || 0;

        if (total === 0) {
            const emptyIcon = emptyEl.querySelector('i');
            const emptyTitle = emptyEl.querySelector('p');
            if (memoryCategory === 'dream') {
                emptyIcon.className = 'fas fa-moon text-purple-400 text-xl';
                emptyTitle.textContent = 'No dream diaries yet';
            } else {
                emptyIcon.className = 'fas fa-brain text-purple-400 text-xl';
                emptyTitle.textContent = 'No memory files';
            }
            emptyEl.classList.remove('hidden');
            listEl.classList.add('hidden');
            return;
        }
        emptyEl.classList.add('hidden');
        listEl.classList.remove('hidden');

        const tbody = document.getElementById('memory-table-body');
        tbody.innerHTML = '';
        files.forEach(f => {
            const tr = document.createElement('tr');
            tr.className = 'border-b border-slate-100 dark:border-white/5 hover:bg-slate-50 dark:hover:bg-white/5 cursor-pointer transition-colors';
            tr.onclick = () => openMemoryFile(f.filename, memoryCategory);
            let typeLabel;
            if (f.type === 'global') {
                typeLabel = '<span class="px-2 py-0.5 rounded-full text-xs bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400">Global</span>';
            } else if (f.type === 'dream') {
                typeLabel = '<span class="px-2 py-0.5 rounded-full text-xs bg-violet-50 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400">Dream</span>';
            } else {
                typeLabel = '<span class="px-2 py-0.5 rounded-full text-xs bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400">Daily</span>';
            }
            const sizeStr = f.size < 1024 ? f.size + ' B' : (f.size / 1024).toFixed(1) + ' KB';
            tr.innerHTML = `
                <td class="px-4 py-3 text-sm font-mono text-slate-700 dark:text-slate-200">${escapeHtml(f.filename)}</td>
                <td class="px-4 py-3 text-sm">${typeLabel}</td>
                <td class="px-4 py-3 text-sm text-slate-500 dark:text-slate-400">${sizeStr}</td>
                <td class="px-4 py-3 text-sm text-slate-500 dark:text-slate-400">${escapeHtml(f.updated_at)}</td>`;
            tbody.appendChild(tr);
        });

        // Pagination
        const totalPages = Math.ceil(total / memoryPageSize);
        const pagEl = document.getElementById('memory-pagination');
        if (totalPages <= 1) { pagEl.innerHTML = ''; return; }
        let pagHtml = `<span>${page} / ${totalPages}</span><div class="flex gap-2">`;
        if (page > 1) pagHtml += `<button onclick="loadMemoryView(${page - 1})" class="px-3 py-1 rounded-lg border border-slate-200 dark:border-white/10 hover:bg-slate-100 dark:hover:bg-white/10 text-xs">Prev</button>`;
        if (page < totalPages) pagHtml += `<button onclick="loadMemoryView(${page + 1})" class="px-3 py-1 rounded-lg border border-slate-200 dark:border-white/10 hover:bg-slate-100 dark:hover:bg-white/10 text-xs">Next</button>`;
        pagHtml += '</div>';
        pagEl.innerHTML = pagHtml;
    }).catch(() => {});
}

function openMemoryFile(filename, category) {
    category = category || 'memory';
    fetch(`/api/memory/content?filename=${encodeURIComponent(filename)}&category=${category}`).then(r => r.json()).then(data => {
        if (data.status !== 'success') return;
        document.getElementById('memory-panel-list').classList.add('hidden');
        const panel = document.getElementById('memory-panel-viewer');
        document.getElementById('memory-viewer-title').textContent = filename;
        document.getElementById('memory-viewer-content').innerHTML = renderMarkdown(data.content || '');
        panel.classList.remove('hidden');
        applyHighlighting(panel);
    }).catch(() => {});
}

function closeMemoryViewer() {
    document.getElementById('memory-panel-viewer').classList.add('hidden');
    document.getElementById('memory-panel-list').classList.remove('hidden');
}

// =====================================================================
// Custom Confirm Dialog
// =====================================================================
function showConfirmDialog({ title, message, okText, cancelText, onConfirm }) {
    const overlay = document.getElementById('confirm-dialog-overlay');
    document.getElementById('confirm-dialog-title').textContent = title || '';
    document.getElementById('confirm-dialog-message').textContent = message || '';
    document.getElementById('confirm-dialog-ok').textContent = okText || 'OK';
    document.getElementById('confirm-dialog-cancel').textContent = cancelText || t('channels_cancel');

    function cleanup() {
        overlay.classList.add('hidden');
        okBtn.removeEventListener('click', onOk);
        cancelBtn.removeEventListener('click', onCancel);
        overlay.removeEventListener('click', onOverlayClick);
    }
    function onOk() { cleanup(); if (onConfirm) onConfirm(); }
    function onCancel() { cleanup(); }
    function onOverlayClick(e) { if (e.target === overlay) cleanup(); }

    const okBtn = document.getElementById('confirm-dialog-ok');
    const cancelBtn = document.getElementById('confirm-dialog-cancel');
    okBtn.addEventListener('click', onOk);
    cancelBtn.addEventListener('click', onCancel);
    overlay.addEventListener('click', onOverlayClick);
    overlay.classList.remove('hidden');
}

// =====================================================================
// Channels View
// =====================================================================
let channelsData = [];

function loadChannelsView() {
    const container = document.getElementById('channels-content');
    container.innerHTML = `<div class="flex items-center gap-2 py-8 justify-center text-slate-400 dark:text-slate-500 text-sm">
        <i class="fas fa-spinner fa-spin text-xs"></i><span>Loading...</span></div>`;

    fetch('/api/channels').then(r => r.json()).then(data => {
        if (data.status !== 'success') return;
        channelsData = data.channels || [];
        renderActiveChannels();
    }).catch(() => {
        container.innerHTML = '<p class="text-sm text-red-400 py-8 text-center">Failed to load channels</p>';
    });
}

function renderActiveChannels() {
    stopWeixinQrPoll();
    stopWeixinStatusPoll();
    const container = document.getElementById('channels-content');
    container.innerHTML = '';
    closeAddChannelPanel();

    const activeChannels = channelsData.filter(ch => ch.active);

    if (activeChannels.length === 0) {
        container.innerHTML = `
            <div class="flex flex-col items-center justify-center py-20">
                <div class="w-16 h-16 rounded-2xl bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center mb-4">
                    <i class="fas fa-tower-broadcast text-blue-400 text-xl"></i>
                </div>
                <p class="text-slate-500 dark:text-slate-400 font-medium">${t('channels_empty')}</p>
                <p class="text-sm text-slate-400 dark:text-slate-500 mt-1">${t('channels_empty_desc')}</p>
            </div>`;
        return;
    }

    activeChannels.forEach(ch => {
        const label = (typeof ch.label === 'object') ? (ch.label[currentLang] || ch.label.en) : ch.label;
        const card = document.createElement('div');
        card.className = 'bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 p-6';
        card.id = `channel-card-${ch.name}`;

        const fieldsHtml = buildChannelFieldsHtml(ch.name, ch.fields || []);
        const hasFields = (ch.fields || []).length > 0;

        const isWeixin = ch.name === 'weixin' || ch.name.startsWith('weixin:');
        const weixinWaiting = isWeixin && ch.login_status && ch.login_status !== 'logged_in';
        const wecomNeedsCreds = ch.name === 'wecom_bot' && !_wecomBotHasCreds(ch);
        // 濡炲鍋橀崝?active 闁告绱曟晶鏍с€掗崣澶屽帬閻?Tab 闁?panel闁挎稒纰嶆晶婊堝礉閵娿儻缍栭柛?+ 闁规鍋嗛悥婊堟煂瀹ュ懐绱﹂柨娑樼墣椤╊偊鎯勯弽顐㈢疀闁哄牆顦甸崢銈囩磾椤曞棛绀?
        const isFeishu = ch.name === 'feishu';
        let statusDot, statusText;
        if (weixinWaiting) {
            statusDot = 'bg-amber-400 animate-pulse';
            statusText = ch.login_status === 'scanned'
                ? `<span data-weixin-status-text class="text-xs text-primary-500">${t('weixin_scan_scanned')}</span>`
                : `<span data-weixin-status-text class="text-xs text-amber-500">${t('weixin_scan_waiting')}</span>`;
        } else if (wecomNeedsCreds) {
            statusDot = 'bg-amber-400 animate-pulse';
            statusText = `<span class="text-xs text-amber-500">${t('channels_connecting')}</span>`;
        } else {
            statusDot = 'bg-primary-400';
            statusText = `<span class="text-xs text-primary-500">${t('channels_connected')}</span>`;
        }

        card.innerHTML = `
            <div class="flex items-center gap-4${hasFields || weixinWaiting || wecomNeedsCreds || isFeishu ? ' mb-5' : ''}">
                <div class="w-10 h-10 rounded-xl bg-${ch.color}-50 dark:bg-${ch.color}-900/20 flex items-center justify-center flex-shrink-0">
                    <i class="fas ${ch.icon} text-${ch.color}-500 text-base"></i>
                </div>
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2">
                        <span class="font-semibold text-slate-800 dark:text-slate-100">${escapeHtml(label)}</span>
                        <span ${weixinWaiting ? 'data-weixin-status-dot' : ''} class="w-2 h-2 rounded-full ${statusDot}"></span>
                        ${statusText}
                    </div>
                    <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-mono">${escapeHtml(ch.name)}</p>
                </div>
                <button onclick="disconnectChannel('${ch.name}')"
                    class="px-3 py-1.5 rounded-lg text-xs font-medium
                           bg-red-50 dark:bg-red-900/20 text-red-500 dark:text-red-400
                           hover:bg-red-100 dark:hover:bg-red-900/40
                           cursor-pointer transition-colors flex-shrink-0">
                    ${t('channels_disconnect')}
                </button>
            </div>
            ${weixinWaiting ? `<div id="${weixinActiveQrContainerId(ch.name)}" class="flex flex-col items-center py-2">
                <button onclick="showWeixinActiveQr('${escapeHtml(ch.name)}')"
                    class="px-4 py-2 rounded-lg bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium
                           cursor-pointer transition-colors duration-150">
                    ${t('weixin_scan_title')}
                </button>
            </div>` : ''}
            ${wecomNeedsCreds ? `<div id="wecom-active-auth" class="flex flex-col items-center py-2">
                <p class="text-sm text-slate-500 dark:text-slate-400 mb-3">${t('wecom_scan_desc')}</p>
                <button onclick="startWecomBotAuthInCard()"
                    class="px-5 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-medium
                           cursor-pointer transition-colors duration-150">
                    <i class="fas fa-qrcode mr-2"></i>${t('wecom_scan_btn')}
                </button>
                <div id="wecom-card-scan-status" class="mt-3"></div>
            </div>` : ''}
            ${isFeishu ? buildFeishuPanel(ch, true) : (hasFields ? `<div class="space-y-4">
                ${fieldsHtml}
                <div class="flex items-center justify-end gap-3 pt-1">
                    <span id="ch-status-${ch.name}" class="text-xs text-primary-500 opacity-0 transition-opacity duration-300"></span>
                    <button onclick="saveChannelConfig('${ch.name}')"
                        class="px-4 py-2 rounded-lg bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium
                               cursor-pointer transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                        id="ch-save-${ch.name}">${t('channels_save')}</button>
                </div>
            </div>` : '')}`;

        container.appendChild(card);
        bindSecretFieldEvents(card);

        if (weixinWaiting) {
            startWeixinActiveStatusPoll(ch.name);
        }
    });
}

function buildChannelFieldsHtml(chName, fields) {
    let html = '';
    fields.forEach(f => {
        const inputId = `ch-${chName}-${f.key}`;
        let inputHtml = '';
        if (f.type === 'bool') {
            const checked = f.value ? 'checked' : '';
            inputHtml = `<label class="relative inline-flex items-center cursor-pointer">
                <input id="${inputId}" type="checkbox" ${checked} class="sr-only peer" data-field="${f.key}" data-ch="${chName}">
                <div class="w-9 h-5 bg-slate-200 dark:bg-slate-700 peer-checked:bg-primary-400 rounded-full
                            after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white
                            after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-full"></div>
            </label>`;
        } else if (f.type === 'secret') {
            inputHtml = `<input id="${inputId}" type="text" value="${escapeHtml(String(f.value || ''))}"
                data-field="${f.key}" data-ch="${chName}" data-masked="${f.value ? '1' : ''}"
                class="w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600
                       bg-slate-50 dark:bg-white/5 text-sm text-slate-800 dark:text-slate-100
                       focus:outline-none focus:border-primary-500 font-mono transition-colors
                       ${f.value ? 'cfg-key-masked' : ''}"
                placeholder="${escapeHtml(f.label)}">`;
        } else {
            const inputType = f.type === 'number' ? 'number' : 'text';
            inputHtml = `<input id="${inputId}" type="${inputType}" value="${escapeHtml(String(f.value ?? f.default ?? ''))}"
                data-field="${f.key}" data-ch="${chName}"
                class="w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600
                       bg-slate-50 dark:bg-white/5 text-sm text-slate-800 dark:text-slate-100
                       focus:outline-none focus:border-primary-500 font-mono transition-colors"
                placeholder="${escapeHtml(f.label)}">`;
        }
        html += `<div>
            <label class="block text-sm font-medium text-slate-600 dark:text-slate-400 mb-1.5">${escapeHtml(f.label)}</label>
            ${inputHtml}
        </div>`;
    });
    return html;
}

function bindSecretFieldEvents(container) {
    container.querySelectorAll('input[data-masked="1"]').forEach(inp => {
        inp.addEventListener('focus', function() {
            if (this.dataset.masked === '1') {
                this.value = '';
                this.dataset.masked = '';
                this.classList.remove('cfg-key-masked');
            }
        });
    });
}

function showChannelStatus(chName, msgKey, isError) {
    const el = document.getElementById(`ch-status-${chName}`);
    if (!el) return;
    el.textContent = t(msgKey);
    el.classList.toggle('text-red-500', !!isError);
    el.classList.toggle('text-primary-500', !isError);
    el.classList.remove('opacity-0');
    setTimeout(() => el.classList.add('opacity-0'), 2500);
}

function saveChannelConfig(chName) {
    const card = document.getElementById(`channel-card-${chName}`);
    if (!card) return;

    const updates = {};
    card.querySelectorAll('input[data-ch="' + chName + '"]').forEach(inp => {
        const key = inp.dataset.field;
        if (inp.type === 'checkbox') {
            updates[key] = inp.checked;
        } else {
            if (inp.dataset.masked === '1') return;
            updates[key] = inp.value;
        }
    });

    const btn = document.getElementById(`ch-save-${chName}`);
    if (btn) btn.disabled = true;

    fetch('/api/channels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'save', channel: chName, config: updates })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            showChannelStatus(chName, data.restarted ? 'channels_restarted' : 'channels_saved', false);
        } else {
            showChannelStatus(chName, 'channels_save_error', true);
        }
    })
    .catch(() => showChannelStatus(chName, 'channels_save_error', true))
    .finally(() => { if (btn) btn.disabled = false; });
}

function disconnectChannel(chName) {
    const ch = channelsData.find(c => c.name === chName);
    const label = ch ? ((typeof ch.label === 'object') ? (ch.label[currentLang] || ch.label.en) : ch.label) : chName;

    showConfirmDialog({
        title: t('channels_disconnect'),
        message: t('channels_disconnect_confirm'),
        okText: t('channels_disconnect'),
        cancelText: t('channels_cancel'),
        onConfirm: () => {
            fetch('/api/channels', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'disconnect', channel: chName })
            })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    if (ch) ch.active = false;
                    renderActiveChannels();
                }
            })
            .catch(() => {});
        }
    });
}

// --- Add channel panel ---
function openAddChannelPanel() {
    const panel = document.getElementById('channels-add-panel');
    const activeNames = new Set(channelsData.filter(c => c.active).map(c => c.name));
    const available = channelsData.filter(c => !activeNames.has(c.name));

    const content = document.getElementById('channels-content');
    if (activeNames.size === 0 && content) content.classList.add('hidden');

    if (available.length === 0) {
        panel.innerHTML = `<div class="bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 p-6 text-center">
            <p class="text-sm text-slate-500 dark:text-slate-400">All channels are already connected</p>
            <button onclick="closeAddChannelPanel()" class="mt-3 text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 cursor-pointer">${t('channels_cancel')}</button>
        </div>`;
        panel.classList.remove('hidden');
        return;
    }

    const ddOptions = [
        { value: '', label: t('channels_select_placeholder') },
        ...available.map(ch => {
            const label = (typeof ch.label === 'object') ? (ch.label[currentLang] || ch.label.en) : ch.label;
            return { value: ch.name, label: `${label} (${ch.name})` };
        })
    ];

    panel.innerHTML = `
        <div class="bg-white dark:bg-[#1A1A1A] rounded-xl border border-primary-200 dark:border-primary-800 p-6">
            <div class="flex items-center gap-3 mb-5">
                <div class="w-9 h-9 rounded-lg bg-primary-50 dark:bg-primary-900/30 flex items-center justify-center">
                    <i class="fas fa-plus text-primary-500 text-sm"></i>
                </div>
                <h3 class="font-semibold text-slate-800 dark:text-slate-100">${t('channels_add')}</h3>
            </div>
            <div class="mb-4">
                <div id="add-channel-select" class="cfg-dropdown" tabindex="0">
                    <div class="cfg-dropdown-selected">
                        <span class="cfg-dropdown-text">--</span>
                        <i class="fas fa-chevron-down cfg-dropdown-arrow"></i>
                    </div>
                    <div class="cfg-dropdown-menu"></div>
                </div>
            </div>
            <div id="add-channel-fields" class="space-y-4"></div>
            <div id="add-channel-actions" class="hidden flex items-center justify-end gap-3 pt-4">
                <button onclick="closeAddChannelPanel()"
                    class="px-4 py-2 rounded-lg border border-slate-200 dark:border-white/10
                           text-slate-600 dark:text-slate-300 text-sm font-medium
                           hover:bg-slate-50 dark:hover:bg-white/5
                           cursor-pointer transition-colors duration-150">${t('channels_cancel')}</button>
                <button id="add-channel-submit" onclick="submitAddChannel()"
                    class="px-4 py-2 rounded-lg bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium
                           cursor-pointer transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed">${t('channels_connect_btn')}</button>
            </div>
        </div>`;
    panel.classList.remove('hidden');
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    const ddEl = document.getElementById('add-channel-select');
    initDropdown(ddEl, ddOptions, '', onAddChannelSelect);
}

function closeAddChannelPanel() {
    stopWeixinQrPoll();
    stopFeishuRegisterPoll();
    const panel = document.getElementById('channels-add-panel');
    if (panel) {
        panel.classList.add('hidden');
        panel.innerHTML = '';
    }
    const content = document.getElementById('channels-content');
    if (content) content.classList.remove('hidden');
}

function onAddChannelSelect(chName) {
    stopWeixinQrPoll();
    stopFeishuRegisterPoll();
    const fieldsContainer = document.getElementById('add-channel-fields');
    const actions = document.getElementById('add-channel-actions');

    if (!chName) {
        fieldsContainer.innerHTML = '';
        actions.classList.add('hidden');
        return;
    }

    if (chName === 'weixin' || String(chName).startsWith('weixin:')) {
        actions.classList.add('hidden');
        fieldsContainer.innerHTML = `
            <div id="${weixinQrPanelId(chName)}" class="flex flex-col items-center py-4">
                <p class="text-sm text-slate-500 dark:text-slate-400 mb-4">${t('weixin_scan_loading')}</p>
            </div>`;
        startWeixinQrLogin(chName);
        return;
    }

    if (chName === 'wecom_bot') {
        actions.classList.add('hidden');
        const ch = channelsData.find(c => c.name === chName);
        fieldsContainer.innerHTML = buildWecomBotPanel(ch);
        return;
    }

    if (chName === 'feishu') {
        actions.classList.add('hidden');
        const ch = channelsData.find(c => c.name === chName);
        fieldsContainer.innerHTML = buildFeishuPanel(ch);
        return;
    }

    const ch = channelsData.find(c => c.name === chName);
    if (!ch) return;

    fieldsContainer.innerHTML = buildChannelFieldsHtml(chName, ch.fields || []);
    bindSecretFieldEvents(fieldsContainer);
    actions.classList.remove('hidden');
}

function submitAddChannel() {
    const ddEl = document.getElementById('add-channel-select');
    const chName = getDropdownValue(ddEl);
    if (!chName) return;

    const fieldsContainer = document.getElementById('add-channel-fields');
    const updates = {};
    fieldsContainer.querySelectorAll('input[data-ch="' + chName + '"]').forEach(inp => {
        const key = inp.dataset.field;
        if (inp.type === 'checkbox') {
            updates[key] = inp.checked;
        } else {
            if (inp.dataset.masked === '1') return;
            updates[key] = inp.value;
        }
    });

    const btn = document.getElementById('add-channel-submit');
    if (btn) { btn.disabled = true; btn.textContent = t('channels_connecting'); }

    fetch('/api/channels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'connect', channel: chName, config: updates })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            const ch = channelsData.find(c => c.name === chName);
            if (ch) {
                ch.active = true;
                (ch.fields || []).forEach(f => {
                    if (updates[f.key] !== undefined) {
                        f.value = f.type === 'secret' ? ChannelsHandler_maskSecret(updates[f.key]) : updates[f.key];
                    }
                });
            }
            renderActiveChannels();
        } else {
            if (btn) { btn.disabled = false; btn.textContent = t('channels_connect_btn'); }
        }
    })
    .catch(() => {
        if (btn) { btn.disabled = false; btn.textContent = t('channels_connect_btn'); }
    });
}

// =====================================================================
// WeChat QR Login
// =====================================================================
let _weixinQrPollTimers = {};
let _weixinStatusPollTimers = {};

function weixinChannelDomKey(channelName = 'weixin') {
    return String(channelName || 'weixin').replace(/[^A-Za-z0-9_-]/g, '_');
}

function weixinActiveQrContainerId(channelName = 'weixin') {
    return `weixin-active-qr-${weixinChannelDomKey(channelName)}`;
}

function weixinQrPanelId(channelName = 'weixin') {
    return `weixin-qr-panel-${weixinChannelDomKey(channelName)}`;
}

function getWeixinQrPanel(channelName = 'weixin') {
    return document.getElementById(weixinQrPanelId(channelName));
}

function stopWeixinStatusPoll(channelName = null) {
    if (channelName) {
        if (_weixinStatusPollTimers[channelName]) {
            clearTimeout(_weixinStatusPollTimers[channelName]);
            delete _weixinStatusPollTimers[channelName];
        }
        return;
    }
    Object.values(_weixinStatusPollTimers).forEach(timer => clearTimeout(timer));
    _weixinStatusPollTimers = {};
}

function updateWeixinCardStatus(channelName, loginStatus) {
    const card = document.getElementById(`channel-card-${channelName}`);
    if (!card) return;

    const dot = card.querySelector('[data-weixin-status-dot]');
    const text = card.querySelector('[data-weixin-status-text]');
    if (!dot || !text) return;

    dot.className = 'w-2 h-2 rounded-full bg-amber-400 animate-pulse';
    text.className = loginStatus === 'scanned'
        ? 'text-xs text-primary-500'
        : 'text-xs text-amber-500';
    text.textContent = loginStatus === 'scanned'
        ? t('weixin_scan_scanned')
        : t('weixin_scan_waiting');
}

function refreshWeixinActiveQr(channelName = 'weixin') {
    const panel = getWeixinQrPanel(channelName);
    if (!panel || panel.dataset.source !== 'channel') return;

    const account = weixinAccountFromChannel(channelName);
    const url = account ? `/api/weixin/qrlogin?account=${encodeURIComponent(account)}` : '/api/weixin/qrlogin';
    fetch(url)
        .then(r => r.json())
        .then(data => {
            if (data.status !== 'success' || data.source !== 'channel') return;
            const img = panel.querySelector('img');
            if (img && data.qr_image && img.src !== data.qr_image) {
                renderWeixinQr(data.qr_image, 'waiting', channelName, 'channel');
            }
        })
        .catch(() => {});
}

function startWeixinActiveStatusPoll(channelName = 'weixin') {
    stopWeixinStatusPoll(channelName);
    _weixinStatusPollTimers[channelName] = setTimeout(() => {
        fetch('/api/channels').then(r => r.json()).then(data => {
            if (data.status !== 'success') return;
            const wx = (data.channels || []).find(c => c.name === channelName);
            if (!wx || !wx.active) {
                stopWeixinStatusPoll(channelName);
                return;
            }
            if (wx.login_status === 'logged_in') {
                stopWeixinStatusPoll(channelName);
                channelsData = data.channels;
                renderActiveChannels();
            } else {
                const ch = channelsData.find(c => c.name === channelName);
                if (ch) ch.login_status = wx.login_status;
                updateWeixinCardStatus(channelName, wx.login_status);
                refreshWeixinActiveQr(channelName);
                startWeixinActiveStatusPoll(channelName);
            }
        }).catch(() => { startWeixinActiveStatusPoll(channelName); });
    }, 3000);
}

function stopWeixinQrPoll(channelName = null) {
    if (channelName) {
        if (_weixinQrPollTimers[channelName]) {
            clearTimeout(_weixinQrPollTimers[channelName]);
            delete _weixinQrPollTimers[channelName];
        }
        return;
    }
    Object.values(_weixinQrPollTimers).forEach(timer => clearTimeout(timer));
    _weixinQrPollTimers = {};
}

function weixinAccountFromChannel(channelName = 'weixin') {
    return String(channelName || '').startsWith('weixin:') ? String(channelName).split(':').slice(1).join(':') : '';
}

function showWeixinActiveQr(channelName = 'weixin') {
    const container = document.getElementById(weixinActiveQrContainerId(channelName)) || document.getElementById('weixin-active-qr');
    if (!container) return;
    container.innerHTML = `
        <div id="${weixinQrPanelId(channelName)}" class="flex flex-col items-center py-2">
            <p class="text-sm text-slate-500 dark:text-slate-400 mb-4">${t('weixin_scan_loading')}</p>
        </div>`;
    stopWeixinStatusPoll(channelName);
    startWeixinQrLogin(channelName, true);
}

function startWeixinQrLogin(channelName = 'weixin', forceNew = false) {
    stopWeixinQrPoll(channelName);
    const account = weixinAccountFromChannel(channelName);
    const params = new URLSearchParams();
    if (account) params.set('account', account);
    if (forceNew) params.set('force', '1');
    const qs = params.toString();
    const url = qs ? `/api/weixin/qrlogin?${qs}` : '/api/weixin/qrlogin';
    fetch(url)
        .then(r => r.json())
        .then(data => {
            const panel = getWeixinQrPanel(channelName);
            if (!panel) return;
            if (data.status !== 'success') {
                panel.innerHTML = `<p class="text-sm text-red-500">${t('weixin_scan_fail')}: ${data.message || ''}</p>`;
                return;
            }
            renderWeixinQr(data.qr_image || data.qrcode_url, 'waiting', channelName, data.source || '');
            if (data.source === 'channel') {
                startWeixinActiveStatusPoll(channelName);
            } else {
                pollWeixinQrStatus(channelName);
            }
        })
        .catch(() => {
            const panel = getWeixinQrPanel(channelName);
            if (panel) panel.innerHTML = `<p class="text-sm text-red-500">${t('weixin_scan_fail')}</p>`;
        });
}

function renderWeixinQr(qrcodeUrl, status, channelName = 'weixin', source = '') {
    const panel = getWeixinQrPanel(channelName);
    if (!panel) return;
    if (source) panel.dataset.source = source;

    if (status !== 'confirmed' && (!qrcodeUrl || !String(qrcodeUrl).startsWith('data:image/'))) {
        panel.innerHTML = `
            <div class="flex flex-col items-center py-4 text-center">
                <div class="w-12 h-12 rounded-full bg-amber-50 dark:bg-amber-900/30 flex items-center justify-center mb-3">
                    <i class="fas fa-triangle-exclamation text-amber-500 text-lg"></i>
                </div>
                <p class="text-sm font-medium text-amber-600 dark:text-amber-400">${t('weixin_scan_fail')}</p>
                <p class="text-xs text-slate-400 dark:text-slate-500 mt-2 max-w-sm">
                    QR image was not generated. Install qrcode and Pillow in the current Python environment, then restart ZVAgent.
                </p>
                <button onclick="startWeixinQrLogin('${escapeHtml(channelName)}')"
                        class="mt-4 px-3 py-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800">
                    Retry
                </button>
            </div>`;
        return;
    }

    let statusText = t('weixin_scan_waiting');
    let statusColor = 'text-slate-500 dark:text-slate-400';
    if (status === 'scanned') {
        statusText = t('weixin_scan_scanned');
        statusColor = 'text-primary-500';
    } else if (status === 'expired') {
        statusText = t('weixin_scan_expired');
        statusColor = 'text-amber-500';
    } else if (status === 'confirmed') {
        statusText = t('weixin_scan_success');
        statusColor = 'text-primary-500';
    }

    panel.innerHTML = `
        <div class="flex flex-col items-center">
            <p class="text-sm font-medium text-slate-700 dark:text-slate-200 mb-1">${t('weixin_scan_title')}</p>
            <p class="text-xs text-slate-400 dark:text-slate-500 mb-4">${t('weixin_scan_desc')}</p>
            <div class="bg-white p-3 rounded-xl shadow-sm border border-slate-100 dark:border-slate-700 mb-3">
                <img src="${escapeHtml(qrcodeUrl)}" alt="QR Code" class="w-52 h-52" style="image-rendering: pixelated;"/>
            </div>
            <p class="text-xs ${statusColor} mb-1">${statusText}</p>
            <p class="text-xs text-slate-400 dark:text-slate-500">${t('weixin_qr_tip')}</p>
        </div>`;
}

function pollWeixinQrStatus(channelName = 'weixin') {
    const account = weixinAccountFromChannel(channelName);
    stopWeixinQrPoll(channelName);
    _weixinQrPollTimers[channelName] = setTimeout(() => {
        fetch('/api/weixin/qrlogin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'poll', account })
        })
        .then(r => r.json())
        .then(data => {
            const panel = getWeixinQrPanel(channelName);
            if (!panel) { stopWeixinQrPoll(channelName); return; }

            if (data.status !== 'success') {
                pollWeixinQrStatus(channelName);
                return;
            }

            const qrStatus = data.qr_status;
            if (qrStatus === 'confirmed') {
                renderWeixinQr('', 'confirmed', channelName);
                stopWeixinQrPoll(channelName);
                panel.innerHTML = `
                    <div class="flex flex-col items-center py-4">
                        <div class="w-12 h-12 rounded-full bg-primary-50 dark:bg-primary-900/30 flex items-center justify-center mb-3">
                            <i class="fas fa-check text-primary-500 text-lg"></i>
                        </div>
                        <p class="text-sm font-medium text-primary-600 dark:text-primary-400">${t('weixin_scan_success')}</p>
                    </div>`;
                connectWeixinAfterQr(channelName);
            } else if (qrStatus === 'expired' && (data.qr_image || data.qrcode_url)) {
                renderWeixinQr(data.qr_image || data.qrcode_url, 'waiting', channelName);
                pollWeixinQrStatus(channelName);
            } else if (qrStatus === 'scaned') {
                const img = panel.querySelector('img');
                const currentSrc = img ? img.src : '';
                renderWeixinQr(currentSrc, 'scanned', channelName);
                pollWeixinQrStatus(channelName);
            } else {
                pollWeixinQrStatus(channelName);
            }
        })
        .catch(() => {
            pollWeixinQrStatus(channelName);
        });
    }, 2000);
}

function connectWeixinAfterQr(channelName = 'weixin') {
    fetch('/api/channels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'connect', channel: channelName, config: {} })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            const ch = channelsData.find(c => c.name === channelName);
            if (ch) ch.active = true;
            setTimeout(() => renderActiveChannels(), 1500);
        }
    })
    .catch(() => {});
}

// =====================================================================
// WeCom Bot QR Auth
// =====================================================================
const WECOM_BOT_SDK_URL = 'https://wwcdn.weixin.qq.com/node/wework/js/wecom-aibot-sdk@0.1.0.min.js';
const WECOM_BOT_SOURCE = 'zvagent';
let _wecomSdkLoaded = false;

function ensureWecomSdkLoaded() {
    return new Promise((resolve, reject) => {
        if (_wecomSdkLoaded && window.WecomAIBotSDK) { resolve(); return; }
        if (document.querySelector(`script[src="${WECOM_BOT_SDK_URL}"]`)) {
            _wecomSdkLoaded = true; resolve(); return;
        }
        const s = document.createElement('script');
        s.src = WECOM_BOT_SDK_URL;
        s.onload = () => { _wecomSdkLoaded = true; resolve(); };
        s.onerror = () => reject(new Error('Failed to load WecomAIBotSDK'));
        document.head.appendChild(s);
    });
}

function _wecomBotHasCreds(ch) {
    if (!ch || !ch.fields) return false;
    const idField = ch.fields.find(f => f.key === 'wecom_bot_id');
    const secretField = ch.fields.find(f => f.key === 'wecom_bot_secret');
    return !!(idField && idField.value && secretField && secretField.value);
}

function buildWecomBotPanel(ch) {
    const scanLabel = t('wecom_mode_scan');
    const manualLabel = t('wecom_mode_manual');
    const hasCreds = _wecomBotHasCreds(ch);
    const defaultMode = hasCreds ? 'manual' : 'scan';
    return `
        <div id="wecom-bot-panel" data-default-mode="${defaultMode}">
            <div class="flex items-center justify-center gap-1 mb-5 bg-slate-100 dark:bg-white/5 rounded-lg p-1">
                <button id="wecom-tab-scan" onclick="switchWecomBotMode('scan')"
                    class="flex-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors
                           bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm">
                    ${scanLabel}
                </button>
                <button id="wecom-tab-manual" onclick="switchWecomBotMode('manual')"
                    class="flex-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors
                           text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200">
                    ${manualLabel}
                </button>
            </div>
            <div id="wecom-mode-content"></div>
        </div>`;
}

function switchWecomBotMode(mode) {
    const scanTab = document.getElementById('wecom-tab-scan');
    const manualTab = document.getElementById('wecom-tab-manual');
    const content = document.getElementById('wecom-mode-content');
    const actions = document.getElementById('add-channel-actions');
    if (!scanTab || !manualTab || !content) return;

    const activeClasses = 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm';
    const inactiveClasses = 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200';

    if (mode === 'scan') {
        scanTab.className = scanTab.className.replace(/text-slate-500[^\s]*/g, '').replace(/hover:\S+/g, '');
        scanTab.className = `flex-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${activeClasses}`;
        manualTab.className = `flex-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${inactiveClasses}`;
        actions.classList.add('hidden');
        content.innerHTML = `
            <div class="flex flex-col items-center py-4">
                <p class="text-sm text-slate-600 dark:text-slate-300 mb-2">${t('wecom_scan_desc')}</p>
                <button onclick="startWecomBotAuth()"
                    class="mt-3 px-6 py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-medium
                           cursor-pointer transition-colors duration-150">
                    <i class="fas fa-qrcode mr-2"></i>${t('wecom_scan_btn')}
                </button>
                <div id="wecom-scan-status" class="mt-3"></div>
            </div>`;
    } else {
        manualTab.className = `flex-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${activeClasses}`;
        scanTab.className = `flex-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${inactiveClasses}`;
        const ch = channelsData.find(c => c.name === 'wecom_bot');
        content.innerHTML = `<div class="space-y-4">${buildChannelFieldsHtml('wecom_bot', ch ? ch.fields || [] : [])}</div>`;
        bindSecretFieldEvents(content);
        actions.classList.remove('hidden');
    }
}

function startWecomBotAuth() {
    const statusEl = document.getElementById('wecom-scan-status');
    ensureWecomSdkLoaded().then(() => {
        WecomAIBotSDK.openBotInfoAuthWindow({
            source: WECOM_BOT_SOURCE,
            onCreated: function(bot) {
                if (statusEl) {
                    statusEl.innerHTML = `
                        <div class="flex flex-col items-center py-2">
                            <div class="w-10 h-10 rounded-full bg-emerald-50 dark:bg-emerald-900/30 flex items-center justify-center mb-2">
                                <i class="fas fa-check text-emerald-500 text-lg"></i>
                            </div>
                            <p class="text-sm font-medium text-emerald-600 dark:text-emerald-400">${t('wecom_scan_success')}</p>
                        </div>`;
                }
                connectWecomBotAfterAuth(bot.botid, bot.secret);
            },
            onError: function(err) {
                if (statusEl) {
                    statusEl.innerHTML = `<p class="text-sm text-red-500">${t('wecom_scan_fail')}: ${err.message || err.code || ''}</p>`;
                }
            }
        });
    }).catch(err => {
        if (statusEl) {
            statusEl.innerHTML = `<p class="text-sm text-red-500">SDK load failed: ${err.message}</p>`;
        }
    });
}

function connectWecomBotAfterAuth(botId, secret) {
    fetch('/api/channels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            action: 'connect',
            channel: 'wecom_bot',
            config: { wecom_bot_id: botId, wecom_bot_secret: secret }
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            const ch = channelsData.find(c => c.name === 'wecom_bot');
            if (ch) {
                ch.active = true;
                (ch.fields || []).forEach(f => {
                    if (f.key === 'wecom_bot_id') f.value = botId;
                    if (f.key === 'wecom_bot_secret') f.value = ChannelsHandler_maskSecret(secret);
                });
            }
            setTimeout(() => renderActiveChannels(), 1500);
        }
    })
    .catch(() => {});
}

function startWecomBotAuthInCard() {
    const statusEl = document.getElementById('wecom-card-scan-status');
    ensureWecomSdkLoaded().then(() => {
        WecomAIBotSDK.openBotInfoAuthWindow({
            source: WECOM_BOT_SOURCE,
            onCreated: function(bot) {
                if (statusEl) {
                    statusEl.innerHTML = `
                        <div class="flex flex-col items-center py-2">
                            <div class="w-10 h-10 rounded-full bg-emerald-50 dark:bg-emerald-900/30 flex items-center justify-center mb-2">
                                <i class="fas fa-check text-emerald-500 text-lg"></i>
                            </div>
                            <p class="text-sm font-medium text-emerald-600 dark:text-emerald-400">${t('wecom_scan_success')}</p>
                        </div>`;
                }
                connectWecomBotAfterAuth(bot.botid, bot.secret);
            },
            onError: function(err) {
                if (statusEl) {
                    statusEl.innerHTML = `<p class="text-sm text-red-500">${t('wecom_scan_fail')}: ${err.message || err.code || ''}</p>`;
                }
            }
        });
    }).catch(err => {
        if (statusEl) {
            statusEl.innerHTML = `<p class="text-sm text-red-500">SDK load failed: ${err.message}</p>`;
        }
    });
}

// Initialize wecom bot panel with correct default mode when inserted into DOM
document.addEventListener('DOMContentLoaded', function() {
    const observer = new MutationObserver(function() {
        const wecomPanel = document.getElementById('wecom-bot-panel');
        if (wecomPanel && !wecomPanel.dataset.initialized) {
            wecomPanel.dataset.initialized = '1';
            switchWecomBotMode(wecomPanel.dataset.defaultMode || 'scan');
        }
        const feishuPanel = document.getElementById('feishu-panel');
        if (feishuPanel && !feishuPanel.dataset.initialized) {
            feishuPanel.dataset.initialized = '1';
            switchFeishuMode(feishuPanel.dataset.defaultMode || 'scan');
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
});

// =====================================================================
// Feishu One-click App Registration (lark-oapi register_app)
// =====================================================================
let _feishuRegisterPollTimer = null;

function _feishuHasCreds(ch) {
    if (!ch || !ch.fields) return false;
    const idField = ch.fields.find(f => f.key === 'feishu_app_id');
    const secretField = ch.fields.find(f => f.key === 'feishu_app_secret');
    return !!(idField && idField.value && secretField && secretField.value);
}

function buildFeishuPanel(ch, isActive) {
    const scanLabel = t('feishu_mode_scan');
    const manualLabel = t('feishu_mode_manual');
    // 鐎圭寮跺﹢渚€宕欓鐔风ウ闁哄啫鐖肩划顖滄媼閵堝牏绠婚柛蹇嬪劜婢ф粓宕?Tab闁挎稑鏈弻鐔哥瑹婢跺憡鍙忛柡鈧惂鍝ュ耿闁告熬绠戦崹顖炲箳閵娿劌绀冮柟娈垮亞閻?
    const defaultMode = _feishuHasCreds(ch) ? 'manual' : 'scan';
    const activeAttr = isActive ? 'data-active="1"' : '';
    return `
        <div id="feishu-panel" data-default-mode="${defaultMode}" ${activeAttr}>
            <div class="flex items-center justify-center gap-1 mb-5 bg-slate-100 dark:bg-white/5 rounded-lg p-1">
                <button id="feishu-tab-scan" onclick="switchFeishuMode('scan')"
                    class="flex-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors
                           bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm">
                    ${scanLabel}
                </button>
                <button id="feishu-tab-manual" onclick="switchFeishuMode('manual')"
                    class="flex-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors
                           text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200">
                    ${manualLabel}
                </button>
            </div>
            <div id="feishu-mode-content"></div>
        </div>`;
}

function switchFeishuMode(mode) {
    const panel = document.getElementById('feishu-panel');
    const scanTab = document.getElementById('feishu-tab-scan');
    const manualTab = document.getElementById('feishu-tab-manual');
    const content = document.getElementById('feishu-mode-content');
    if (!scanTab || !manualTab || !content) return;

    // 鐎圭寮剁缓鍝劽烘繝姘ｅ亾濮樻湹澹曢柛妤嬬磿婢ф牗绋夐鐐点偟闁稿繈鍎查?panel 闁哄啳顔愮槐婵嗏柦閳╁啯绠?add-channel-actions闁挎稑鐗呯换姘扁偓娑櫳戠€垫粓鏌﹂鍏肩殤閺夆晜鍨剁憰鍡涘蓟閹垮嫮绀?
    const isActive = panel && panel.dataset.active === '1';
    const actions = isActive ? null : document.getElementById('add-channel-actions');

    const activeClasses = 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm';
    const inactiveClasses = 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200';

    stopFeishuRegisterPoll();

    if (mode === 'scan') {
        scanTab.className = `flex-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${activeClasses}`;
        manualTab.className = `flex-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${inactiveClasses}`;
        if (actions) actions.classList.add('hidden');
        // active 闁告绱曟晶鏍ㄧ▔鐎ｎ偄顥囬柣顔荤劍濞存盯骞戦姀銏＄暠闁圭粯鍔楅妵姘跺棘閸ヮ煈鏀抽柨娑樿嫰瀹歌京鎷?闁告帗绋戠紓鎾诲棘閻楀牊绨氶柛锝冨妺濮瑰瀵煎鎰佹船闁烩晜鐗滈獮鍥嫉婢舵劕甯崇紓?
        const desc = isActive
            ? t('feishu_scan_replace_desc')
            : t('feishu_scan_desc');
        content.innerHTML = `
            <div id="feishu-scan-panel" class="flex flex-col items-center py-4">
                <p class="text-sm text-slate-600 dark:text-slate-300 mb-3 text-center">${desc}</p>
                <button onclick="startFeishuRegister()"
                    class="mt-2 px-6 py-2.5 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-medium
                           cursor-pointer transition-colors duration-150">
                    <i class="fas fa-qrcode mr-2"></i>${t('feishu_scan_btn')}
                </button>
                <div id="feishu-scan-status" class="mt-4 w-full"></div>
            </div>`;
    } else {
        manualTab.className = `flex-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${activeClasses}`;
        scanTab.className = `flex-1 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${inactiveClasses}`;
        const ch = channelsData.find(c => c.name === 'feishu');
        const fieldsHtml = buildChannelFieldsHtml('feishu', ch ? ch.fields || [] : []);
        if (isActive) {
            // 鐎圭寮剁敮鎾礂閵夈儱骞㈤柣妤€娴勭槐浼村礃閸涱垳鏋傚ǎ鍥ㄧ箓閻°劑骞愭径鎰唉闁挎稑鑻ˇ鏌ユ偨?saveChannelConfig 閻?update 婵炵繝鑳堕埢?
            content.innerHTML = `
                <div class="space-y-4">
                    ${fieldsHtml}
                    <div class="flex items-center justify-end gap-3 pt-1">
                        <span id="ch-status-feishu" class="text-xs text-primary-500 opacity-0 transition-opacity duration-300"></span>
                        <button onclick="saveChannelConfig('feishu')"
                            class="px-4 py-2 rounded-lg bg-primary-500 hover:bg-primary-600 text-white text-sm font-medium
                                   cursor-pointer transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                            id="ch-save-feishu">${t('channels_save')}</button>
                    </div>
                </div>`;
        } else {
            content.innerHTML = `<div class="space-y-4">${fieldsHtml}</div>`;
            if (actions) actions.classList.remove('hidden');
        }
        bindSecretFieldEvents(content);
    }
}

function stopFeishuRegisterPoll() {
    if (_feishuRegisterPollTimer) {
        clearTimeout(_feishuRegisterPollTimer);
        _feishuRegisterPollTimer = null;
    }
}

function startFeishuRegister(targetStatusId) {
    const statusId = targetStatusId || 'feishu-scan-status';
    const statusEl = document.getElementById(statusId);
    if (statusEl) {
        statusEl.innerHTML = `<p class="text-sm text-slate-500 dark:text-slate-400 text-center">${t('feishu_scan_loading')}</p>`;
    }
    stopFeishuRegisterPoll();
    fetch('/api/feishu/register')
        .then(r => r.json())
        .then(data => {
            if (data.status !== 'success') {
                renderFeishuRegisterError(statusId, data.message || t('feishu_scan_fail'));
                return;
            }
            renderFeishuQr(statusId, data.qr_image, data.qrcode_url);
            pollFeishuRegisterStatus(statusId);
        })
        .catch(err => {
            renderFeishuRegisterError(statusId, err.message || t('feishu_scan_fail'));
        });
}

function renderFeishuQr(statusId, qrImage, qrUrl) {
    const statusEl = document.getElementById(statusId);
    if (!statusEl) return;
    const imgHtml = qrImage
        ? `<img src="${qrImage}" alt="QR" class="w-44 h-44 rounded-lg border border-slate-200 dark:border-white/10 bg-white p-2"/>`
        : `<div class="w-44 h-44 rounded-lg border border-dashed border-slate-300 flex items-center justify-center text-xs text-slate-400">QR</div>`;
    statusEl.innerHTML = `
        <div class="flex flex-col items-center gap-3">
            ${imgHtml}
            <p class="text-xs text-amber-500">${t('feishu_scan_waiting')}</p>
            <p class="text-xs text-slate-400 dark:text-slate-500">${t('feishu_scan_tip')}</p>
            ${qrUrl ? `<a href="${qrUrl}" target="_blank" rel="noopener"
                class="text-xs text-blue-500 hover:text-blue-600 underline">${t('feishu_scan_open_link')}</a>` : ''}
        </div>`;
}

function renderFeishuRegisterError(statusId, message) {
    const statusEl = document.getElementById(statusId);
    if (!statusEl) return;
    statusEl.innerHTML = `
        <div class="flex flex-col items-center gap-2 py-2">
            <p class="text-sm text-red-500 text-center">${message}</p>
            <button onclick="startFeishuRegister('${statusId}')"
                class="mt-1 px-4 py-1.5 rounded-md text-xs font-medium
                       bg-slate-100 dark:bg-white/10 text-slate-700 dark:text-slate-200
                       hover:bg-slate-200 dark:hover:bg-white/20 cursor-pointer">
                <i class="fas fa-rotate-right mr-1"></i>${t('feishu_scan_retry')}
            </button>
        </div>`;
}

function pollFeishuRegisterStatus(statusId) {
    stopFeishuRegisterPoll();
    _feishuRegisterPollTimer = setTimeout(() => {
        fetch('/api/feishu/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'poll' })
        })
        .then(r => r.json())
        .then(data => {
            if (data.status !== 'success') {
                renderFeishuRegisterError(statusId, data.message || t('feishu_scan_fail'));
                return;
            }
            const rs = data.register_status;
            if (rs === 'done') {
                const statusEl = document.getElementById(statusId);
                if (statusEl) {
                    statusEl.innerHTML = `
                        <div class="flex flex-col items-center py-2">
                            <div class="w-10 h-10 rounded-full bg-emerald-50 dark:bg-emerald-900/30 flex items-center justify-center mb-2">
                                <i class="fas fa-check text-emerald-500 text-lg"></i>
                            </div>
                            <p class="text-sm font-medium text-emerald-600 dark:text-emerald-400">${t('feishu_scan_success')}</p>
                        </div>`;
                }
                connectFeishuAfterRegister(data.app_id, data.app_secret);
            } else if (rs === 'expired') {
                renderFeishuRegisterError(statusId, t('feishu_scan_expired'));
            } else if (rs === 'denied') {
                renderFeishuRegisterError(statusId, t('feishu_scan_denied'));
            } else if (rs === 'error') {
                renderFeishuRegisterError(statusId, data.message || t('feishu_scan_fail'));
            } else {
                pollFeishuRegisterStatus(statusId);
            }
        })
        .catch(() => {
            pollFeishuRegisterStatus(statusId);
        });
    }, 2000);
}

function connectFeishuAfterRegister(appId, appSecret) {
    fetch('/api/channels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            action: 'connect',
            channel: 'feishu',
            config: { feishu_app_id: appId, feishu_app_secret: appSecret }
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            const ch = channelsData.find(c => c.name === 'feishu');
            if (ch) {
                ch.active = true;
                (ch.fields || []).forEach(f => {
                    if (f.key === 'feishu_app_id') f.value = appId;
                    if (f.key === 'feishu_app_secret') f.value = ChannelsHandler_maskSecret(appSecret);
                });
            }
            setTimeout(() => renderActiveChannels(), 1500);
        }
    })
    .catch(() => {});
}

// =====================================================================
// Scheduler View
// =====================================================================
let tasksLoaded = false;
function loadTasksView() {
    if (tasksLoaded) return;
    fetch('/api/scheduler').then(r => r.json()).then(data => {
        if (data.status !== 'success') return;
        const emptyEl = document.getElementById('tasks-empty');
        const listEl = document.getElementById('tasks-list');
        const allTasks = data.tasks || [];
        // Only show active (enabled) tasks
        const tasks = allTasks.filter(t => t.enabled !== false);
        if (tasks.length === 0) {
            emptyEl.querySelector('p').textContent = 'No scheduled tasks';
            return;
        }
        emptyEl.classList.add('hidden');
        listEl.classList.remove('hidden');
        listEl.innerHTML = '';

        tasks.forEach(task => {
            const card = document.createElement('div');
            card.className = 'bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 p-4';
            const typeLabel = task.type === 'cron'
                ? `<span class="text-xs font-mono text-slate-400">${escapeHtml(task.cron || '')}</span>`
                : `<span class="text-xs text-slate-400">${escapeHtml(task.type || 'once')}</span>`;
            let nextRun = '--';
            if (task.next_run_at) {
                // next_run_at is an ISO string, not a Unix timestamp
                const d = new Date(task.next_run_at);
                if (!isNaN(d.getTime())) nextRun = d.toLocaleString();
            }
            card.innerHTML = `
                <div class="flex items-center gap-2 mb-2">
                    <span class="w-2 h-2 rounded-full bg-primary-400"></span>
                    <span class="font-medium text-sm text-slate-700 dark:text-slate-200">${escapeHtml(task.name || task.id || '--')}</span>
                    <div class="flex-1"></div>
                    ${typeLabel}
                </div>
                <p class="text-xs text-slate-500 dark:text-slate-400 mb-2 line-clamp-2">${escapeHtml(task.prompt || task.description || '')}</p>
                <div class="flex items-center gap-4 text-xs text-slate-400 dark:text-slate-500">
                    <span><i class="fas fa-clock mr-1"></i>Next run: ${nextRun}</span>
                </div>`;
            listEl.appendChild(card);
        });
        tasksLoaded = true;
    }).catch(() => {});
}

// =====================================================================
// Reports View
// =====================================================================
let _reportsLoaded = false;

function loadReportsView(force = false) {
    const list = document.getElementById('reports-list');
    const summary = document.getElementById('reports-summary');
    if (!list || !summary) return;
    if (_reportsLoaded && !force) return;
    _reportsLoaded = true;

    summary.innerHTML = '';
    list.innerHTML = `<div class="flex items-center gap-2 py-8 justify-center text-slate-400 dark:text-slate-500 text-sm">
        <i class="fas fa-spinner fa-spin text-xs"></i><span>加载报告中...</span></div>`;

    fetch('/api/reports?page=1&page_size=80').then(r => r.json()).then(data => {
        if (data.status !== 'success') throw new Error(data.message || 'load failed');
        renderReportsSummary(data.items || [], data.total || 0);
        renderReportsList(data.items || []);
    }).catch(() => {
        list.innerHTML = '<p class="text-sm text-red-400 py-8 text-center">报告加载失败</p>';
    });
}

function renderReportsSummary(items, total) {
    const summary = document.getElementById('reports-summary');
    if (!summary) return;
    const done = items.filter(x => x.status === 'done').length;
    const running = items.filter(x => ['queued', 'researching', 'writing', 'rendering', 'running'].includes(x.status)).length;
    const failed = items.filter(x => x.status === 'failed').length;
    const stats = [
        ['全部报告', total, 'fa-file-lines', 'text-slate-500'],
        ['已完成', done, 'fa-circle-check', 'text-primary-500'],
        ['进行中', running, 'fa-spinner', 'text-amber-500'],
        ['失败', failed, 'fa-triangle-exclamation', 'text-red-500'],
    ];
    summary.innerHTML = stats.map(([label, value, icon, color]) => `
        <div class="bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 p-4">
            <div class="flex items-center justify-between">
                <span class="text-xs text-slate-400 dark:text-slate-500">${label}</span>
                <i class="fas ${icon} ${color} text-sm"></i>
            </div>
            <div class="mt-2 text-2xl font-semibold text-slate-800 dark:text-slate-100">${value}</div>
        </div>
    `).join('');
}

function renderReportsList(items) {
    const list = document.getElementById('reports-list');
    if (!list) return;
    if (!items.length) {
        list.innerHTML = `
            <div class="flex flex-col items-center justify-center py-20">
                <div class="w-16 h-16 rounded-2xl bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center mb-4">
                    <i class="fas fa-file-pdf text-blue-400 text-xl"></i>
                </div>
                <p class="text-slate-500 dark:text-slate-400 font-medium">暂无报告</p>
                <p class="text-sm text-slate-400 dark:text-slate-500 mt-1">在微信发送 /报告 主题 后会显示在这里</p>
            </div>`;
        return;
    }
    list.innerHTML = items.map(job => renderReportCard(job)).join('');
}

function renderReportCard(job) {
    const statusInfo = reportStatusInfo(job.status);
    const sourceCount = job.source_count ?? 0;
    const sourceLabel = job.source_label || (sourceCount > 0 ? `${sourceCount} 个外部来源` : '外部来源待补充');
    const sourceTitle = job.source_notice || sourceLabel;
    const created = formatReportTime(job.created_at);
    const user = job.display_name || job.user_id || '';
    const canDownload = job.status === 'done';
    const percent = Math.max(0, Math.min(100, Number(job.progress_percent ?? (canDownload ? 100 : 0)) || 0));
    const options = job.options || {};
    const optionText = options.label
        ? `${options.label} / 约 ${options.target_words || 3000} 字 / 最多 ${options.max_sources || sourceCount || 10} 个来源`
        : (job.version ? `${job.version}` : '');
    return `
        <div class="bg-white dark:bg-[#1A1A1A] rounded-xl border border-slate-200 dark:border-white/10 p-4">
            <div class="flex flex-col md:flex-row md:items-start justify-between gap-3">
                <div class="min-w-0 flex-1">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs ${statusInfo.className}">
                            <i class="fas ${statusInfo.icon} text-[10px]"></i>${statusInfo.label}
                        </span>
                        <span class="text-xs text-slate-400 dark:text-slate-500 font-mono">${escapeHtml(job.job_id || '')}</span>
                    </div>
                    <h3 class="font-semibold text-slate-800 dark:text-slate-100 truncate">${escapeHtml(job.title || job.topic || '未命名报告')}</h3>
                    <div class="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-400 dark:text-slate-500">
                        <span><i class="fas fa-user mr-1"></i>${escapeHtml(user)}</span>
                        <span><i class="fas fa-clock mr-1"></i>${escapeHtml(created)}</span>
                        <span title="${escapeHtml(sourceTitle)}"><i class="fas fa-link mr-1"></i>${escapeHtml(sourceLabel)}</span>
                        ${optionText ? `<span><i class="fas fa-sliders mr-1"></i>${escapeHtml(optionText)}</span>` : ''}
                    </div>
                    ${job.progress ? `<p class="mt-2 text-xs text-slate-500 dark:text-slate-400">${escapeHtml(job.progress)}</p>` : ''}
                    <div class="mt-3 h-1.5 rounded-full bg-slate-100 dark:bg-white/10 overflow-hidden">
                        <div class="h-full rounded-full ${job.status === 'failed' ? 'bg-red-500' : 'bg-primary-500'}" style="width:${percent}%"></div>
                    </div>
                    ${job.error ? `<p class="mt-2 text-xs text-red-500">${escapeHtml(job.error)}</p>` : ''}
                </div>
                <div class="flex items-center gap-2 flex-shrink-0">
                    <button onclick="openReportDetail('${escapeHtml(job.job_id || '')}')"
                        class="inline-flex items-center justify-center w-9 h-9 rounded-lg border border-slate-200 dark:border-white/10 text-slate-500 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10"
                        title="查看详情"><i class="fas fa-eye text-sm"></i></button>
                    ${canDownload ? `<a href="/api/reports/download/${encodeURIComponent(job.job_id || '')}" target="_blank"
                        class="inline-flex items-center justify-center w-9 h-9 rounded-lg border border-slate-200 dark:border-white/10 text-slate-500 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10"
                        title="下载 PDF"><i class="fas fa-file-arrow-down text-sm"></i></a>` : ''}
                    <button onclick="openReportSources('${escapeHtml(job.job_id || '')}')"
                        class="inline-flex items-center justify-center w-9 h-9 rounded-lg border border-slate-200 dark:border-white/10 text-slate-500 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10"
                        title="查看来源"><i class="fas fa-list-check text-sm"></i></button>
                    <button onclick="deleteReport('${escapeHtml(job.job_id || '')}')"
                        class="inline-flex items-center justify-center w-9 h-9 rounded-lg border border-red-100 dark:border-red-900/40 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20"
                        title="删除"><i class="fas fa-trash text-sm"></i></button>
                </div>
            </div>
        </div>`;
}

function reportStatusInfo(status) {
    const map = {
        done: ['已完成', 'fa-circle-check', 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400'],
        failed: ['失败', 'fa-triangle-exclamation', 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400'],
        researching: ['调研中', 'fa-magnifying-glass', 'bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400'],
        writing: ['写作中', 'fa-pen-nib', 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'],
        rendering: ['排版中', 'fa-file-pdf', 'bg-violet-50 dark:bg-violet-900/20 text-violet-600 dark:text-violet-400'],
        queued: ['排队中', 'fa-clock', 'bg-slate-100 dark:bg-white/10 text-slate-500 dark:text-slate-300'],
    };
    const item = map[status] || ['未知', 'fa-circle', 'bg-slate-100 dark:bg-white/10 text-slate-500 dark:text-slate-300'];
    return { label: item[0], icon: item[1], className: item[2] };
}

function formatReportTime(value) {
    if (!value) return '';
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return value;
    return d.toLocaleString();
}

function ensureReportDetailModal() {
    let overlay = document.getElementById('report-detail-overlay');
    if (overlay) return overlay;
    overlay = document.createElement('div');
    overlay.id = 'report-detail-overlay';
    overlay.className = 'fixed inset-0 z-[80] hidden bg-black/50 backdrop-blur-sm p-3 md:p-6';
    overlay.innerHTML = `
        <div class="h-full max-w-6xl mx-auto bg-white dark:bg-[#111111] border border-slate-200 dark:border-white/10 rounded-xl shadow-2xl flex flex-col overflow-hidden">
            <div class="px-4 py-3 border-b border-slate-200 dark:border-white/10 flex items-start gap-3">
                <div class="min-w-0 flex-1">
                    <h3 id="report-detail-title" class="font-semibold text-slate-800 dark:text-slate-100 truncate">报告详情</h3>
                    <p id="report-detail-meta" class="text-xs text-slate-400 dark:text-slate-500 mt-1"></p>
                </div>
                <button onclick="closeReportDetail()"
                        class="w-9 h-9 rounded-lg border border-slate-200 dark:border-white/10 text-slate-500 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10">
                    <i class="fas fa-xmark"></i>
                </button>
            </div>
            <div class="px-4 pt-3 flex gap-2 border-b border-slate-200 dark:border-white/10">
                <button class="report-detail-tab px-3 py-2 text-sm border-b-2 border-primary-500 text-primary-500" data-tab="markdown" onclick="switchReportDetailTab('markdown')">正文</button>
                <button class="report-detail-tab px-3 py-2 text-sm border-b-2 border-transparent text-slate-500 dark:text-slate-400" data-tab="sources" onclick="switchReportDetailTab('sources')">来源</button>
                <button class="report-detail-tab px-3 py-2 text-sm border-b-2 border-transparent text-slate-500 dark:text-slate-400" data-tab="plan" onclick="switchReportDetailTab('plan')">计划</button>
            </div>
            <div class="flex-1 overflow-y-auto p-4">
                <div id="report-detail-loading" class="py-12 text-center text-sm text-slate-400 dark:text-slate-500">
                    <i class="fas fa-spinner fa-spin mr-2"></i>加载中...
                </div>
                <article id="report-detail-markdown" class="hidden prose prose-slate dark:prose-invert max-w-none text-sm"></article>
                <div id="report-detail-sources" class="hidden grid gap-3"></div>
                <pre id="report-detail-plan" class="hidden text-xs whitespace-pre-wrap bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg p-3 overflow-x-auto"></pre>
            </div>
        </div>
    `;
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeReportDetail();
    });
    document.body.appendChild(overlay);
    return overlay;
}

function closeReportDetail() {
    const overlay = document.getElementById('report-detail-overlay');
    if (overlay) overlay.classList.add('hidden');
}

function switchReportDetailTab(tab) {
    document.querySelectorAll('.report-detail-tab').forEach(btn => {
        const active = btn.dataset.tab === tab;
        btn.classList.toggle('border-primary-500', active);
        btn.classList.toggle('text-primary-500', active);
        btn.classList.toggle('border-transparent', !active);
        btn.classList.toggle('text-slate-500', !active);
        btn.classList.toggle('dark:text-slate-400', !active);
    });
    ['markdown', 'sources', 'plan'].forEach(name => {
        const el = document.getElementById('report-detail-' + name);
        if (el) el.classList.toggle('hidden', name !== tab);
    });
}

function openReportDetail(jobId) {
    if (!jobId) return;
    const overlay = ensureReportDetailModal();
    overlay.classList.remove('hidden');
    document.getElementById('report-detail-title').textContent = '报告详情';
    document.getElementById('report-detail-meta').textContent = jobId;
    document.getElementById('report-detail-loading').classList.remove('hidden');
    ['markdown', 'sources', 'plan'].forEach(name => {
        const el = document.getElementById('report-detail-' + name);
        if (el) el.classList.add('hidden');
    });

    fetch(`/api/reports/detail/${encodeURIComponent(jobId)}`).then(r => r.json()).then(data => {
        if (data.status !== 'success') throw new Error(data.message || 'load failed');
        const job = data.job || {};
        const options = job.options || {};
        document.getElementById('report-detail-title').textContent = job.title || job.topic || '报告详情';
        document.getElementById('report-detail-meta').textContent = [
            job.job_id || '',
            job.display_name || job.user_id || '',
            options.label ? `${options.label}模式` : '',
            formatReportTime(job.created_at)
        ].filter(Boolean).join(' · ');

        const markdownEl = document.getElementById('report-detail-markdown');
        markdownEl.innerHTML = data.markdown
            ? renderMarkdown(data.markdown)
            : '<p class="text-slate-400 dark:text-slate-500">正文尚未生成。</p>';
        applyHighlighting(markdownEl);

        const sources = (data.sources && data.sources.sources) || [];
        const sourcesEl = document.getElementById('report-detail-sources');
        sourcesEl.innerHTML = sources.length ? sources.map((src, idx) => {
            const title = escapeHtml(src.title || '无标题');
            const url = escapeHtml(src.url || '');
            const snippet = escapeHtml(src.snippet || src.summary || src.content_excerpt || '');
            return `
                <div class="border border-slate-200 dark:border-white/10 rounded-lg p-3 bg-slate-50 dark:bg-white/5">
                    <div class="flex items-start gap-2">
                        <span class="text-xs font-mono text-primary-500">[${idx + 1}]</span>
                        <div class="min-w-0 flex-1">
                            <div class="font-medium text-sm text-slate-800 dark:text-slate-100">${title}</div>
                            ${url ? `<a href="${url}" target="_blank" rel="noopener noreferrer" class="block truncate text-xs text-primary-500 mt-1">${url}</a>` : ''}
                            ${snippet ? `<p class="text-xs text-slate-500 dark:text-slate-400 mt-2 line-clamp-3">${snippet}</p>` : ''}
                        </div>
                    </div>
                </div>`;
        }).join('') : '<p class="text-sm text-slate-400 dark:text-slate-500 py-8 text-center">暂无来源记录</p>';

        document.getElementById('report-detail-plan').textContent = JSON.stringify(data.plan || {}, null, 2);
        document.getElementById('report-detail-loading').classList.add('hidden');
        switchReportDetailTab('markdown');
    }).catch(() => {
        document.getElementById('report-detail-loading').innerHTML = '<span class="text-red-500">报告详情加载失败</span>';
    });
}

function openReportSources(jobId) {
    if (!jobId) return;
    window.open(`/api/reports/sources/${encodeURIComponent(jobId)}`, '_blank');
}

function deleteReport(jobId) {
    if (!jobId) return;
    showConfirmDialog({
        title: '删除报告',
        message: '确定要删除这份报告及其文件吗？',
        okText: '删除',
        cancelText: t('channels_cancel'),
        onConfirm: () => {
            fetch('/api/reports', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_id: jobId })
            }).then(r => r.json()).then(data => {
                if (data.status === 'success') loadReportsView(true);
            }).catch(() => {});
        }
    });
}

// =====================================================================
// Logs View
// =====================================================================
let logEventSource = null;

function logLevelClass(line) {
    if (/\[CRITICAL\]/.test(line)) return 'log-line-critical';
    if (/\[ERROR\]/.test(line))    return 'log-line-error';
    if (/\[WARNING\]/.test(line))  return 'log-line-warning';
    if (/\[INFO\]/.test(line))     return 'log-line-info';
    if (/\[DEBUG\]/.test(line))    return 'log-line-debug';
    return '';
}

function getHiddenLevels() {
    const hidden = new Set();
    document.querySelectorAll('.log-filter-cb').forEach(function(cb) {
        if (!cb.checked) hidden.add('log-line-' + cb.dataset.level);
    });
    return hidden;
}

function applyLogFilter() {
    const hidden = getHiddenLevels();
    document.querySelectorAll('#log-output .log-line').forEach(function(span) {
        const level = span.classList[1] || '';
        span.style.display = hidden.has(level) ? 'none' : '';
    });
}

function appendLogLines(output, text) {
    const hidden = getHiddenLevels();
    let lastLevelClass = '';
    const lines = text.split('\n');
    lines.forEach(function(line, i) {
        if (i === lines.length - 1 && line === '') return;
        const span = document.createElement('span');
        const levelClass = logLevelClass(line) || lastLevelClass;
        if (logLevelClass(line)) lastLevelClass = levelClass;
        span.className = 'log-line ' + levelClass;
        span.textContent = line + '\n';
        if (hidden.has(levelClass)) span.style.display = 'none';
        output.appendChild(span);
    });
}

document.addEventListener('change', function(e) {
    if (e.target.classList.contains('log-filter-cb')) applyLogFilter();
});

function startLogStream() {
    if (logEventSource) return;
    const output = document.getElementById('log-output');
    output.innerHTML = '';

    logEventSource = new EventSource('/api/logs');
    logEventSource.onmessage = function(e) {
        let item;
        try { item = JSON.parse(e.data); } catch (_) { return; }

        if (item.type === 'init') {
            output.innerHTML = '';
            appendLogLines(output, item.content || '');
            output.scrollTop = output.scrollHeight;
        } else if (item.type === 'line') {
            appendLogLines(output, item.content);
            output.scrollTop = output.scrollHeight;
        } else if (item.type === 'error') {
            output.textContent = item.message || 'Error loading logs';
        }
    };
    logEventSource.onerror = function() {
        logEventSource.close();
        logEventSource = null;
    };
}

function stopLogStream() {
    if (logEventSource) {
        logEventSource.close();
        logEventSource = null;
    }
}

// =====================================================================
// View Navigation Hook
// =====================================================================
const _origNavigateTo = navigateTo;
navigateTo = function(viewId) {
    // Stop log stream when leaving logs view
    if (currentView === 'logs' && viewId !== 'logs') stopLogStream();

    _origNavigateTo(viewId);

    // Lazy-load view data
    if (viewId === 'config') loadConfigView();
    else if (viewId === 'skills') loadSkillsView();
    else if (viewId === 'evolution') loadEvolutionView();
    else if (viewId === 'quota') loadQuotaView();
    else if (viewId === 'memory') {
        document.getElementById('memory-panel-viewer').classList.add('hidden');
        document.getElementById('memory-panel-list').classList.remove('hidden');
        switchMemoryTab('files');
    }
    else if (viewId === 'knowledge') loadKnowledgeView();
    else if (viewId === 'reports') loadReportsView();
    else if (viewId === 'channels') loadChannelsView();
    else if (viewId === 'tasks') loadTasksView();
    else if (viewId === 'logs') startLogStream();
};

// =====================================================================
// Knowledge View
// =====================================================================
let _knowledgeTreeData = [];
let _knowledgeRootFiles = [];
let _knowledgeCurrentFile = null;
let _knowledgeGraphLoaded = false;

function loadKnowledgeView() {
    // Reset to docs tab
    switchKnowledgeTab('docs');
    _knowledgeGraphLoaded = false;
    _knowledgeCurrentFile = null;

    fetch('/api/knowledge/list').then(r => r.json()).then(data => {
        if (data.status !== 'success') return;

        const emptyEl = document.getElementById('knowledge-empty');
        const docsPanel = document.getElementById('knowledge-panel-docs');
        const statsEl = document.getElementById('knowledge-stats');

        const tree = data.tree || [];
        const rootFiles = data.root_files || [];
        _knowledgeTreeData = tree;
        _knowledgeRootFiles = rootFiles;
        const stats = data.stats || {};
        const totalPages = stats.pages || 0;
        const sizeStr = stats.size < 1024 ? stats.size + ' B' : (stats.size / 1024).toFixed(1) + ' KB';

        statsEl.textContent = totalPages + ' pages - ' + sizeStr;

        if (totalPages === 0) {
            emptyEl.querySelector('p').textContent = t('knowledge_empty_hint');
            const guideEl = document.getElementById('knowledge-empty-guide');
            if (guideEl) guideEl.classList.remove('hidden');
            emptyEl.classList.remove('hidden');
            docsPanel.classList.add('hidden');
            return;
        }
        emptyEl.classList.add('hidden');
        docsPanel.classList.remove('hidden');

        renderKnowledgeTree(tree, rootFiles);

        // Auto-select the first file (desktop only)
        if (window.innerWidth >= 768) {
            const firstFile = rootFiles.length > 0 ? rootFiles[0] : null;
            const firstGroup = !firstFile ? tree.find(g => g.files && g.files.length > 0) : null;
            if (firstFile) {
                openKnowledgeFile(firstFile.name, firstFile.title);
            } else if (firstGroup) {
                const gf = firstGroup.files[0];
                openKnowledgeFile(firstGroup.dir + '/' + gf.name, gf.title);
            }
        } else {
            document.getElementById('knowledge-content-placeholder').classList.add('hidden');
            document.getElementById('knowledge-content-viewer').classList.add('hidden');
        }
    }).catch(() => {});
}

function renderKnowledgeTree(tree, rootFilesOrFilter, filter) {
    const container = document.getElementById('knowledge-tree');
    container.innerHTML = '';
    let rootFiles, lowerFilter;
    if (typeof rootFilesOrFilter === 'string') {
        rootFiles = _knowledgeRootFiles;
        lowerFilter = (rootFilesOrFilter || '').toLowerCase();
    } else {
        rootFiles = rootFilesOrFilter || _knowledgeRootFiles;
        lowerFilter = (filter || '').toLowerCase();
    }
    (rootFiles || []).forEach(f => {
        if (lowerFilter && !f.title.toLowerCase().includes(lowerFilter) && !f.name.toLowerCase().includes(lowerFilter)) return;
        const fbtn = document.createElement('button');
        fbtn.className = 'knowledge-tree-file' + (_knowledgeCurrentFile === f.name ? ' active' : '');
        fbtn.dataset.path = f.name;
        fbtn.innerHTML = `<i class="fas fa-file-lines text-[10px] text-slate-400"></i><span class="truncate">${escapeHtml(f.title)}</span>`;
        fbtn.onclick = () => openKnowledgeFile(f.name, f.title);
        container.appendChild(fbtn);
    });
    _renderKnowledgeGroups(container, tree, '', lowerFilter, 0);
}

function _renderKnowledgeGroups(container, groups, parentPath, lowerFilter, depth) {
    const indent = depth * 12;
    groups.forEach(group => {
        const groupPath = parentPath ? parentPath + '/' + group.dir : group.dir;
        const files = (group.files || []).filter(f =>
            !lowerFilter || f.title.toLowerCase().includes(lowerFilter) || f.name.toLowerCase().includes(lowerFilter)
        );
        const children = group.children || [];
        const hasMatchingChildren = lowerFilter ? _hasFilterMatch(children, lowerFilter) : children.length > 0;
        if (files.length === 0 && !hasMatchingChildren && lowerFilter) return;

        const div = document.createElement('div');
        div.className = 'knowledge-tree-group open';

        const fileCount = _countFiles(group);
        const btn = document.createElement('button');
        btn.className = 'knowledge-tree-group-btn';
        btn.style.paddingLeft = (8 + indent) + 'px';
        btn.innerHTML = `<i class="fas fa-chevron-right chevron"></i><i class="fas fa-folder text-amber-400 text-[11px]"></i><span>${escapeHtml(group.dir)}</span><span class="ml-auto text-[10px] text-slate-400">${fileCount}</span>`;
        btn.onclick = () => div.classList.toggle('open');
        div.appendChild(btn);

        const items = document.createElement('div');
        items.className = 'knowledge-tree-group-items';
        files.forEach(f => {
            const fbtn = document.createElement('button');
            const fpath = groupPath + '/' + f.name;
            fbtn.className = 'knowledge-tree-file' + (_knowledgeCurrentFile === fpath ? ' active' : '');
            fbtn.dataset.path = fpath;
            fbtn.style.paddingLeft = (24 + indent) + 'px';
            fbtn.innerHTML = `<i class="fas fa-file-lines text-[10px] text-slate-400"></i><span class="truncate">${escapeHtml(f.title)}</span>`;
            fbtn.onclick = () => openKnowledgeFile(fpath, f.title);
            items.appendChild(fbtn);
        });
        if (children.length > 0) {
            _renderKnowledgeGroups(items, children, groupPath, lowerFilter, depth + 1);
        }
        div.appendChild(items);
        container.appendChild(div);
    });
}

function _hasFilterMatch(groups, lowerFilter) {
    for (const g of groups) {
        for (const f of (g.files || [])) {
            if (f.title.toLowerCase().includes(lowerFilter) || f.name.toLowerCase().includes(lowerFilter)) return true;
        }
        if (_hasFilterMatch(g.children || [], lowerFilter)) return true;
    }
    return false;
}

function _countFiles(group) {
    let count = (group.files || []).length;
    for (const child of (group.children || [])) {
        count += _countFiles(child);
    }
    return count;
}

function filterKnowledgeTree(query) {
    renderKnowledgeTree(_knowledgeTreeData, _knowledgeRootFiles, query);
}

function resolveKnowledgePath(currentFilePath, relativeHref) {
    // currentFilePath: e.g. "concepts/mcp-protocol.md"
    // relativeHref: e.g. "../entities/openai.md"
    const parts = currentFilePath.split('/');
    parts.pop(); // remove filename, keep directory
    const segments = [...parts, ...relativeHref.split('/')];
    const resolved = [];
    for (const seg of segments) {
        if (seg === '..') resolved.pop();
        else if (seg !== '.' && seg !== '') resolved.push(seg);
    }
    return resolved.join('/');
}

function bindKnowledgeLinks(container, currentFilePath) {
    container.querySelectorAll('a').forEach(a => {
        const href = a.getAttribute('href');
        if (!href || !href.endsWith('.md')) return;
        // Skip absolute URLs
        if (/^https?:\/\//.test(href)) return;

        a.addEventListener('click', (e) => {
            e.preventDefault();
            const resolved = resolveKnowledgePath(currentFilePath, href);
            const linkTitle = a.textContent.trim() || resolved.replace(/\.md$/, '').split('/').pop();
            openKnowledgeFile(resolved, linkTitle);
        });
        a.style.cursor = 'pointer';
        a.classList.add('text-primary-500', 'hover:underline');
    });
}

function bindChatKnowledgeLinks(container) {
    if (!container) return;
    container.querySelectorAll('a').forEach(a => {
        const href = a.getAttribute('href');
        if (!href || !href.endsWith('.md')) return;
        if (/^https?:\/\//.test(href)) return;

        // Determine knowledge path
        let knowledgePath = null;
        if (href.startsWith('knowledge/')) {
            // Full path from workspace root: knowledge/concepts/moe.md
            knowledgePath = href.replace(/^knowledge\//, '');
        } else if (/^[a-z0-9_-]+\/[a-z0-9_.-]+\.md$/i.test(href)) {
            // Looks like category/file.md pattern without knowledge/ prefix
            knowledgePath = href;
        } else if (href.includes('/') && !href.startsWith('/')) {
            // Relative path like ../entities/deepseek.md 闁?extract filename and search
            const filename = href.split('/').pop();
            knowledgePath = '__search__:' + filename;
        }
        if (!knowledgePath) return;

        a.addEventListener('click', (e) => {
            e.preventDefault();
            if (knowledgePath.startsWith('__search__:')) {
                const filename = knowledgePath.replace('__search__:', '');
                // Find the file in cached tree data
                const found = _findKnowledgeFileByName(filename);
                if (found) {
                    navigateTo('knowledge');
                    setTimeout(() => openKnowledgeFile(found.path, found.title), 100);
                }
            } else {
                navigateTo('knowledge');
                const linkTitle = a.textContent.trim() || knowledgePath.replace(/\.md$/, '').split('/').pop();
                setTimeout(() => openKnowledgeFile(knowledgePath, linkTitle), 100);
            }
        });
        a.style.cursor = 'pointer';
        a.classList.add('text-primary-500', 'hover:underline');
    });
}

function _findKnowledgeFileByName(filename) {
    for (const f of _knowledgeRootFiles) {
        if (f.name === filename) return { path: f.name, title: f.title };
    }
    return _searchFileInGroups(_knowledgeTreeData, '', filename);
}

function _searchFileInGroups(groups, parentPath, filename) {
    for (const group of groups) {
        const groupPath = parentPath ? parentPath + '/' + group.dir : group.dir;
        for (const f of (group.files || [])) {
            if (f.name === filename) {
                return { path: groupPath + '/' + f.name, title: f.title };
            }
        }
        const found = _searchFileInGroups(group.children || [], groupPath, filename);
        if (found) return found;
    }
    return null;
}

function openKnowledgeFile(path, title) {
    _knowledgeCurrentFile = path;
    // Update active state in tree via data-path
    document.querySelectorAll('.knowledge-tree-file').forEach(el => {
        el.classList.toggle('active', el.dataset.path === path);
    });

    // Immediately hide placeholder
    document.getElementById('knowledge-content-placeholder').classList.add('hidden');

    fetch(`/api/knowledge/read?path=${encodeURIComponent(path)}`).then(r => r.json()).then(data => {
        if (data.status !== 'success') return;
        const viewer = document.getElementById('knowledge-content-viewer');
        document.getElementById('knowledge-viewer-title').textContent = title;
        document.getElementById('knowledge-viewer-path').textContent = path;
        const bodyEl = document.getElementById('knowledge-viewer-body');
        bodyEl.innerHTML = renderMarkdown(data.content || '');
        viewer.classList.remove('hidden');
        applyHighlighting(viewer);
        bindKnowledgeLinks(bodyEl, path);

        // Mobile: hide sidebar, show content
        if (window.innerWidth < 768) {
            document.getElementById('knowledge-sidebar').classList.add('hidden');
        }
    }).catch(() => {});
}

function knowledgeMobileBack() {
    document.getElementById('knowledge-sidebar').classList.remove('hidden');
    document.getElementById('knowledge-content-viewer').classList.add('hidden');
}

function switchKnowledgeTab(tab) {
    document.querySelectorAll('.knowledge-tab').forEach(el => el.classList.remove('active'));
    document.getElementById('knowledge-tab-' + tab).classList.add('active');

    const docsPanel = document.getElementById('knowledge-panel-docs');
    const graphPanel = document.getElementById('knowledge-panel-graph');

    if (tab === 'docs') {
        docsPanel.classList.remove('hidden');
        graphPanel.classList.add('hidden');
    } else {
        docsPanel.classList.add('hidden');
        graphPanel.classList.remove('hidden');
        if (!_knowledgeGraphLoaded) {
            loadKnowledgeGraph();
        }
    }
}

function loadKnowledgeGraph() {
    _knowledgeGraphLoaded = true;
    const container = document.getElementById('knowledge-graph-container');
    container.innerHTML = '';

    fetch('/api/knowledge/graph').then(r => r.json()).then(data => {
        const nodes = data.nodes || [];
        const links = data.links || [];
        if (nodes.length === 0) {
            container.innerHTML = `<div class="flex flex-col items-center justify-center h-full text-slate-400"><i class="fas fa-diagram-project text-3xl mb-3 opacity-40"></i><p class="text-sm">${t('knowledge_empty_hint')}</p></div>`;
            return;
        }
        renderKnowledgeGraph(container, nodes, links);
    }).catch(() => {
        container.innerHTML = '<div class="flex items-center justify-center h-full text-slate-400 text-sm">Failed to load graph</div>';
    });
}

function renderKnowledgeGraph(container, nodes, links) {
    const width = container.clientWidth;
    const height = container.clientHeight || 600;

    const categories = [...new Set(nodes.map(n => n.category))];
    const colorScale = d3.scaleOrdinal(d3.schemeTableau10).domain(categories);

    // Connection count for sizing
    const connCount = {};
    nodes.forEach(n => connCount[n.id] = 0);
    links.forEach(l => {
        connCount[l.source] = (connCount[l.source] || 0) + 1;
        connCount[l.target] = (connCount[l.target] || 0) + 1;
    });

    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    const g = svg.append('g');

    // Zoom with adaptive label visibility
    let currentZoomScale = 1;
    const zoom = d3.zoom()
        .scaleExtent([0.2, 5])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
            currentZoomScale = event.transform.k;
            updateLabelVisibility();
        });
    svg.call(zoom);

    function updateLabelVisibility() {
        if (!label) return;
        if (currentZoomScale < 0.8) {
            label.attr('opacity', 0);
        } else {
            const baseFontSize = Math.min(12, 10 / Math.max(currentZoomScale * 0.7, 0.5));
            label.attr('opacity', 1).attr('font-size', baseFontSize);
        }
    }

    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(90))
        .force('charge', d3.forceManyBody().strength(-180))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('x', d3.forceX(width / 2).strength(0.06))
        .force('y', d3.forceY(height / 2).strength(0.06))
        .force('collision', d3.forceCollide().radius(d => getNodeRadius(d) + 30));

    function getNodeRadius(d) {
        return Math.max(5, Math.min(16, 5 + (connCount[d.id] || 0) * 2));
    }

    const link = g.append('g')
        .selectAll('line')
        .data(links)
        .join('line')
        .attr('stroke', '#94a3b8')
        .attr('stroke-opacity', 0.3)
        .attr('stroke-width', 1);

    const node = g.append('g')
        .selectAll('circle')
        .data(nodes)
        .join('circle')
        .attr('r', d => getNodeRadius(d))
        .attr('fill', d => colorScale(d.category))
        .attr('stroke', '#fff')
        .attr('stroke-width', 1.5)
        .style('cursor', 'pointer')
        .call(d3.drag()
            .on('start', (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
            .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
            .on('end', (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
        );

    const label = g.append('g')
        .selectAll('text')
        .data(nodes)
        .join('text')
        .text(d => d.label.length > 15 ? d.label.slice(0, 14) + '...' : d.label)
        .attr('font-size', 9)
        .attr('dx', d => getNodeRadius(d) + 4)
        .attr('dy', 3)
        .attr('fill', '#64748b')
        .style('pointer-events', 'none');

    // Tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'knowledge-graph-tooltip';
    container.style.position = 'relative';
    container.appendChild(tooltip);

    node.on('mouseover', (event, d) => {
        tooltip.textContent = d.label + ' (' + d.category + ')';
        tooltip.style.opacity = '1';
        tooltip.style.left = (event.offsetX + 12) + 'px';
        tooltip.style.top = (event.offsetY - 8) + 'px';
        // Highlight connections
        link.attr('stroke-opacity', l => (l.source.id === d.id || l.target.id === d.id) ? 0.8 : 0.1);
        node.attr('opacity', n => n.id === d.id || links.some(l => (l.source.id === d.id && l.target.id === n.id) || (l.target.id === d.id && l.source.id === n.id)) ? 1 : 0.2);
        label.attr('opacity', n => n.id === d.id || links.some(l => (l.source.id === d.id && l.target.id === n.id) || (l.target.id === d.id && l.source.id === n.id)) ? 1 : 0.1);
    }).on('mousemove', (event) => {
        tooltip.style.left = (event.offsetX + 12) + 'px';
        tooltip.style.top = (event.offsetY - 8) + 'px';
    }).on('mouseout', () => {
        tooltip.style.opacity = '0';
        link.attr('stroke-opacity', 0.3);
        node.attr('opacity', 1);
        label.attr('opacity', 1);
    }).on('click', (event, d) => {
        // Switch to docs tab and open the file
        switchKnowledgeTab('docs');
        openKnowledgeFile(d.id, d.label);
    });

    simulation.on('tick', () => {
        link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
        node.attr('cx', d => d.x).attr('cy', d => d.y);
        label.attr('x', d => d.x).attr('y', d => d.y);
    });

    // Auto fit-to-view when simulation settles
    simulation.on('end', () => {
        const pad = 16;
        let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
        nodes.forEach(n => {
            if (n.x < x0) x0 = n.x;
            if (n.y < y0) y0 = n.y;
            if (n.x > x1) x1 = n.x;
            if (n.y > y1) y1 = n.y;
        });
        const bw = x1 - x0 + pad * 2;
        const bh = y1 - y0 + pad * 2;
        if (bw > 0 && bh > 0) {
            const scale = Math.min(width / bw, height / bh, 4);
            const tx = width / 2 - (x0 + x1) / 2 * scale;
            const ty = height / 2 - (y0 + y1) / 2 * scale;
            svg.transition().duration(500).call(
                zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(scale)
            );
        }
    });

    // Legend
    const legendDiv = document.createElement('div');
    legendDiv.className = 'knowledge-graph-legend';
    categories.forEach(cat => {
        const item = document.createElement('span');
        item.className = 'knowledge-graph-legend-item';
        item.innerHTML = `<span class="knowledge-graph-legend-dot" style="background:${colorScale(cat)}"></span>${escapeHtml(cat)}`;
        legendDiv.appendChild(item);
    });
    container.appendChild(legendDiv);
}

// =====================================================================
// Authentication
// =====================================================================
function toggleLoginPassword() {
    const input = document.getElementById('login-password');
    const icon = document.querySelector('#login-toggle-pwd i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}
window.toggleLoginPassword = toggleLoginPassword;

function showLoginScreen() {
    const overlay = document.getElementById('login-overlay');
    if (!overlay) return;
    overlay.classList.remove('hidden');
    document.getElementById('app').classList.add('hidden');

    const subtitle = document.getElementById('login-subtitle');
    const loginBtn = document.getElementById('login-btn');
    if (currentLang === 'en') {
        subtitle.textContent = 'Enter password to access the console';
        loginBtn.textContent = 'Login';
    } else {
        subtitle.textContent = '请输入密码以访问控制台';
        loginBtn.textContent = '登录';
    }

    const form = document.getElementById('login-form');
    const pwdInput = document.getElementById('login-password');
    pwdInput.focus();

    form.onsubmit = function(e) {
        e.preventDefault();
        const pwd = pwdInput.value;
        if (!pwd) return;
        const btn = document.getElementById('login-btn');
        const errEl = document.getElementById('login-error');
        btn.disabled = true;
        errEl.classList.add('hidden');

        fetch('/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({password: pwd})
        }).then(r => r.json()).then(data => {
            if (data.status === 'success') {
                overlay.classList.add('hidden');
                document.getElementById('app').classList.remove('hidden');
                initApp();
            } else {
                errEl.textContent = currentLang === 'en' ? 'Wrong password' : '密码错误';
                errEl.classList.remove('hidden');
                pwdInput.value = '';
                pwdInput.focus();
            }
            btn.disabled = false;
        }).catch(() => {
            errEl.textContent = currentLang === 'en' ? 'Network error, please retry' : '网络错误，请重试';
            errEl.classList.remove('hidden');
            btn.disabled = false;
        });
        return false;
    };
}

// Intercept 401 responses globally to show login screen on session expiry
const _originalFetch = window.fetch;
window.fetch = function(...args) {
    return _originalFetch.apply(this, args).then(response => {
        if (response.status === 401) {
            const url = typeof args[0] === 'string' ? args[0] : (args[0]?.url || '');
            if (!url.startsWith('/auth/')) {
                showLoginScreen();
            }
        }
        return response;
    });
};

function initApp() {
    applyI18n();
    _applyInputTooltips();
    _restoreSessionPanel();

    fetch('/api/knowledge/list').then(r => r.json()).then(data => {
        if (data.status === 'success') {
            _knowledgeTreeData = data.tree || [];
            _knowledgeRootFiles = data.root_files || [];
        }
    }).catch(() => {});

    APP_VERSION = 'v1.0';
    document.getElementById('sidebar-version').textContent = `ZVAgent ${APP_VERSION}`;
    chatInput.focus();
}

// =====================================================================
// Initialization
// =====================================================================
applyTheme();
applyI18n();

fetch('/auth/check').then(r => r.json()).then(data => {
    if (data.auth_required && !data.authenticated) {
        showLoginScreen();
    } else {
        initApp();
    }
}).catch(() => {
    initApp();
});

requestAnimationFrame(() => {
    document.body.classList.add('transition-colors', 'duration-200');
});
