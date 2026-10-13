# 项目整理验收

日期：2026-10-13，Asia/Shanghai。本轮只有文档、归档、忽略规则与维护检查脚本变更，没有功能/UI/教学逻辑修改。

## 实际运行结果

| 检查 | 结果 | 范围 |
| --- | --- | --- |
| 整理前 Web/Provider/API/Demo/V2/沙箱策略回归 | 38/38 通过，69.621 秒 | 替身传输、临时数据和审核固定案例 |
| 整理前 F01～F05 核心回归 | 40/40 通过，6.121 秒 | 既有核心测试，不调用模型或自由 Docker |
| 最终干净目录回归 | 78/78 通过，70.501 秒 | 从 Git 暂存区导出，没有本机忽略文件，覆盖上述两组 |
| 干净目录 F01～F05 冻结引擎/登记目录加载 | 通过 | verify_engines、F03 load_registry、F04/F05 load；未重算摘要 |
| Git 交付文件扫描 | 332 个文件通过 | 凭据格式、私人机器路径和禁止本机工件类型检查，无匹配 |
| Markdown 本地链接 | 通过 | 全部交付 Markdown 的本地目标必须属于 Git，外部 URL 不联网验证 |
| 私人路径忽略 | 24/24 通过 | .env、数据库/WAL/SHM、学习工件、收据、备份、截图、浏览器、虚拟环境、缓存与原始 user_runs 等代表路径 |
| main 基线文件字节与路径 | 214/214 一致 | 源码、前端、测试、静态工件、冻结文件、运行入口、依赖、.env.example、.gitattributes 和保留说明 |
| 73 份已公开归档的冻结报告原件 | 73/73 原始 SHA-256 一致 | 本机旧路径原件未移动、未改写；第 74 份完整模型原文报告继续私有、不处理 |
| Git 移动/删除审查 | 29 份移动可恢复，永久删除 0 | 每个移除旧路径都能在移动前 HEAD 找到，均有归档新位置 |
| 三个主要本地分支 | 原提交一致 | main c40029c、方向一 b194e0b、方向二 f1200ca |
| Git 暂存区空白检查 | 通过 | git diff --cached --check |
| 新 Agent 阅读检查 | 10/10 问题可回答 | AGENT_HANDOFF + 状态/README/架构/限制共五份默认文件 |

最终链接数由下述仓库检查输出，验收文档补充后可能比干净目录的 333 条更多。目录树和逐文件来源见 [整理清单](CLEANUP_INVENTORY.md)，不确定删除项见 [本机留存](RETAINED_LOCAL_FILES.md)。

## 可复查命令

在仓库根目录：

```powershell
python -X utf8 scripts/check_repository.py --cleanup-baseline
python -X utf8 -m unittest web_lab.tests.test_ai_provider web_lab.tests.test_api web_lab.tests.test_demo web_lab.tests.test_learning_v2 web_lab.tests.test_sandbox
python -X utf8 -m unittest experiments.feature_validation.F01_response_adaptation.test_core experiments.feature_validation.F02_dynamic_questioning.test_core experiments.feature_validation.F03_evidence_verification.test_verifier experiments.feature_validation.F04_self_modification.test_core experiments.feature_validation.F05_independent_assessment.test_core
```

--cleanup-baseline 比较固定 main 基线 c40029c，仅用于复核本次整理的原字节；后续功能修改不应继续要求字节不变。一般发布检查省略该参数。检查脚本只读，不调用模型、Docker、学习数据库或远程 URL。

干净目录使用 git checkout-index 导出已审查的暂存内容，再在该目录初始化本机 Git 索引以检查交付文件；没有下载依赖外的新库，没有借用本机历史工件。检查日志与目录保存在忽略的整理笔记/output，未上传。

## 交接覆盖

| 新 Agent 必须回答 | 默认阅读来源 |
| --- | --- |
| 项目是什么 | AGENT_HANDOFF 首段 |
| 做到哪里、哪些功能真实 | PROJECT_STATUS 模块表与 README 已实现 |
| 哪些实验停止 | AGENT_HANDOFF / PROJECT_STATUS 的 A、B、R1 NO-GO |
| 如何启动 | AGENT_HANDOFF 的离线三行命令 |
| 安全边界 | AGENT_HANDOFF / KNOWN_LIMITATIONS |
| 各 Git 分支 | AGENT_HANDOFF 分支表 |
| 下一步最值得做什么 | AGENT_HANDOFF 推荐任务 |
| 哪些文件不要碰 | AGENT_HANDOFF 冻结/白名单/私人数据说明 |
| 系统关系 | ARCHITECTURE |
| 去哪里查历史 | AGENT_HANDOFF 的归档索引 |

## 范围与留存

没有真实模型/付费 API 调用，没有 Docker 构建、验收或任务，没有真人使用或学习效果验证；历史报告里的实测来自原开发轮次。本轮没有重启已有服务或 Docker、读取/改写真实学习数据库、改变许可证/可见性、合并 main 或重写历史。

全部本机原字节在忽略的 backups/project_cleanup_20261013/documents 留存。公开归档脱敏路径/私人 chat 标识并修复导航，不能当成历史冻结原件。完整模型原文报告、原始日志、实际收据、用户历史与私人截图继续不入 Git。遗留缓存/临时日志未作不可恢复的本机删除。

Git 采用两次提交：先检查点 12971c0 纳入 23 份可移动且未跟踪的审核文档，再提交最终归档与交接。只推送 chore/project-cleanup。远程三分支核对与推送结果以本轮最终交付及 git log/ls-remote 为准。
