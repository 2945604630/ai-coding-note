> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# F02 CLI 离线回归

工程检查PASS，范围为本地控制流、数据保存、守卫、版本与既有真实输出回放。没有为本轮新启动导师推理，不能宣称修复后已完成新的真人在线三轮验收。

42/42项确定性回归通过，日志：unittest_stderr.log（仅本机证据：`experiments/feature_validation/F02_dynamic_questioning/validation_repair/checks/20261010T144116541394Z/unittest_stderr.log`；不随 Git 分发）。其中新运行/守卫测试25项，既有17项。首次红灯日志、扩展阶段失败日志都保留：最初缺少新运行适配器；后续1次失败是测试错误地寻找tools.*配置，实际官方CLI使用features.shell_tool/unified_exec。按现有命令核对并修正测试，没有新增推理或挑选输出。

| 检查 | 证据和范围 | 结果 |
| --- | --- | --- |
| 当前cli_guard真实进程启动 | --help和S0脚本工程冒烟，退出码0，保存反馈 | PASS |
| 第2/第3次导师输出 | 依次回放既有C02_FIRST/correct_T2/correct_T3原字节，2个既有学生回应 | PASS，离线回放 |
| 提前结束 | 既有C01_correct在第2次输出结束，无多余输入/调用 | PASS |
| 已改代码 | 既有C02_unexpected转await_new_evidence，不把旧证据认证为新版 | PASS |
| 三次预算停止 | 既有C02_partial停止且不认定理解充分 | PASS |
| 即时保存 | 最新学生原文在下一次调用启动前持久化 | PASS |
| 失败原文与连接异常 | 注入离线故障、保留部分字节/事件和此前学生回应；空失败不误记教学守卫 | PASS，故障注入 |
| 正常退出/EOF/Ctrl+C | 明确结束状态、保存耗时与已有历史 | PASS |
| 守卫与非法预测 | 三份旧误阻断重放3/3；未知版本、非法输入、错误预测等阻断 | PASS |
| 逐轮快照 | 输入history长度0/2/4，不包含当前或未来输出 | PASS |
| 版本记录 | 原始案例、审核版本和逐证据代码/证据哈希保持，未提供版本不采用 | PASS |
| 实验隔离/首次结果 | 真实体验在F02_user_trials，工程数据在本阶段；同目录不得二次覆盖 | PASS |
| 配置链 | 新exec、同gpt-6.1-sol/high、JSON/最后消息、关闭工具/记忆/联网/本地skills | 本地参数检查PASS；不保证OS级读隔离 |

当前本机只读检测：codex-cli 0.162.0-alpha.2；Logged in using ChatGPT。CLI帮助、状态和参数依据保存在preflight_read_only（仅本机证据：`experiments/feature_validation/F02_dynamic_questioning/validation_repair/preflight_read_only`；不随 Git 分发），没有读取认证文件或提取密钥。运行继续采用此前成功的官方产品登录链路，不调用Replicate。

存档：summary.json（仅本机证据：`experiments/feature_validation/F02_dynamic_questioning/validation_repair/checks/20261010T144116541394Z/summary.json`；不随 Git 分发），interaction.json（仅本机证据：`experiments/feature_validation/F02_dynamic_questioning/validation_repair/checks/20261010T144116541394Z/S1_existing_output_replay/interaction.json`；不随 Git 分发），interaction.json（仅本机证据：`experiments/feature_validation/F02_dynamic_questioning/validation_repair/engineering_runs/20261010T144117_662d9b1a/interaction.json`；不随 Git 分发）。后两者都是工程数据，不是真实学习者。工程反馈“是/否”来自脚本输入，也不是真实用户接受度。

修改只有当前cli_guard.py和新增runtime/trial_cli.py，原冻结cli.py/core.py/native.py/run.py没有修改。正式21项冻结、旧516项实验清单中的515项完全相符；唯一改变的运行入口原字节已经归档，旧完成清单自身未改写。历史F01的969项相符。

复现本轮离线核验（在项目根目录执行，生成新的checks时间目录，不覆盖原结果）：

```powershell
python -X utf8 -m experiments.feature_validation.F02_dynamic_questioning.validation_repair.run_checks
```

历史审计复现使用validation_repair.audit_history；会写新的时间后缀报告，保留本轮原始historical_audit.json。不要运行旧audit.main来覆盖旧实验审计文件。

本轮没有测新的线上连接、实际用户等待耐心或教学理解。历史正式调用中位134.99秒，范围129.15–149.30秒；官方传输的正常连接回退日志保留，不把产品内部重连算作作者重新采样。
