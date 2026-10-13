> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# 自动执行报告

正式批次取得 16/16 份真实非空回答，16 个不同 thread ID。所有正式输出只取第一次完整 turn，不根据内容重生成。两次零线程配置失败与一次旧审计器误分类全部保留，正式生成选择口径见下文。

**这是一组存在文件/宿主上下文隔离限制的探索性比较，语义初评未获独立人类复核。**

CLI `0.162.0-alpha.2`；CLI 登录检查显示 `Logged in using ChatGPT`。统一请求模型 `gpt-6.1-sol`、思考 `xhigh`。这些参数由每份 invocation.json 记录；事件流不回传精确后端快照，后台版本 unknown。官方 `exec` 提供独立启动、JSONL 和最后消息输出；脚本只使用正常 CLI。[官方非交互说明](https://learn.chatgpt.com/docs/non-interactive-mode)。

每次在项目之外的新临时 work 目录，只有一份原提示，使用 stdin 原字节，未 resume/fork。关闭 shell、联网搜索、插件、apps、hooks、记忆、子代理及其他外部工具；正式事件流未观察到模型工具调用，work 最终仍只有 prompt.md。源提示、CLI 输出和 archive SHA 已核对。

Windows native sandbox 检查返回 helper_unknown_error: setup refresh had errors，不能证明原项目/gold 在 OS 层不可读；只读模式不构成全目录拒读证明。stderr 还显示本地技能加载，宿主额外指令未证实隔离，所有正式记录 contamination_risk=true、custom_instructions_isolated=null。没有观察到模型主动读取 gold，但不能用零工具日志排除宿主自动读取或服务端背景。[官方权限边界说明](https://learn.chatgpt.com/docs/permissions)。

初次配置键 tools.view_image 被严格配置检查拒绝（无线程/事件/回答）；去掉该不兼容别名后得到 S1_01。原审计器误把连接警告当失败和工具，追加更正保留原记录。传输覆盖 model_providers.openai 又被本机拒绝（S2 零线程配置失败）。之后完全保持成功 S1 的原生 Provider 配置，按原顺序完成尚未生成的 S2 与其余样本，没有再次生成 S1。CLI 内部 WebSocket 超时/重连并回退 HTTPS 原样保存，不绕过认证或用量限制。总计18次exec进程启动，包含2次未进入真实模型线程的配置失败和16个完成的模型线程；不声称后台恰好只有16个HTTP请求。失败原记录：S1配置失败（仅本机证据：`experiments/round5_ui_model/results/cli_automation_20261009T094458357107Z/S1_01/result.json`；不随 Git 分发）、S2配置失败（仅本机证据：`experiments/round5_ui_model/results/cli_automation_20261009T094819533718Z/S2_01/result.json`；不随 Git 分发）；每条旁边保留stderr、空输出及导入记录。

旧 archive primary 标记未改；两份空配置失败仍在历史 primary 中。正式数据按 actual_model_selection（仅本机证据：`experiments/round5_ui_model/results/cli_automation_20261009T094819533718Z/actual_model_selection_16.json`；不随 Git 分发） 选择每槽第一次真实模型线程，每个选择附原 import_record 和追加审计说明。旧 root-level 手工索引不是本批全部收件目录；真实文件位于 responses 下的两个版本子目录。

旧 collector 在重复导入时留下 17 条元数据差异提示：它会补UI默认字段，并把提示复制依据写为operator_report_only，与首次CLI归档的精确字节依据不同。同SHA原文仍使用原归档，未覆盖 metadata 或新增优选回答；明确资格修正另存 audit_correction_v3.json。旧评分器 summary 中 model_calls_by_this_harness=0 指离线评分器本身，phase_two_reports_generated=false指它未写最终报告；本次五份报告由新包装器生成。package_validation 继承阶段一的 no_live_AI_response_claim、stage_two_analysis_executed 等字段不是自动批次状态。批次状态以 状态范围补充（仅本机证据：`experiments/round5_ui_model/results/cli_automation_20261009T094819533718Z/analysis_scope_addendum.json`；不随 Git 分发） 和 final_actual_model_summary 为准。

正式 CLI 进程合计 2414.754 秒，中位数 148.953 秒；观察到输入 220940 token、输出 14391 token，输出含推理 token（若字段存在）。这些是 CLI 回报统计，不是精确后台重试计费统计。订阅摊销成本 unknown，不能写成零成本；本实验未使用付费 API Key。

模型请求 token 包括 Codex 产品额外上下文，不能当作仅有用户提示的裸 API 测试。两组都要求不超过600字符，使用同一模型、思考设置及工具配置；CLI 未提供本实验使用的统一硬 token 上限或 temperature 设置，记录 unknown，不冒称严格 token 预算等价。连接开销主要影响本机链路，不能从总耗时推导提示策略效率或正式产品延迟。

16份输出均非空且未超过600字符，失败/截断为 0；没有补写缺失回答。原始工件：批次记录（仅本机证据：`experiments/round5_ui_model/results/cli_automation_20261009T094819533718Z/final_actual_model_summary.json`；不随 Git 分发）；机械分析（仅本机证据：`experiments/round5_ui_model/results/analysis_20261009T103645496898Z_808fc6/summary.json`；不随 Git 分发）。历史 271 个文件哈希未变，旧冻结输入和 S0 未覆盖。

复现和代码版本：

```powershell
python -m unittest experiments.round5_ui_model.automation.test_runner_v2 experiments.round5_ui_model.automation.test_audit_v3 experiments.round5_ui_model.automation.test_analysis -v
python -m experiments.round5_ui_model.automation.analyze_batch --run-dir "<project-root>\experiments\round5_ui_model\results\cli_automation_20261009T094819533718Z" --preliminary "<project-root>\experiments\round5_ui_model\results\cli_automation_20261009T094819533718Z\preliminary_author_review"
```

分析器保留旧结果，新运行生成新目录；同名分析指针会拒绝覆盖。生成器的运行命令在每份 invocation.json 中，已有模型输出时拒绝重生成。请先审核报告，不自动启动下一轮。
