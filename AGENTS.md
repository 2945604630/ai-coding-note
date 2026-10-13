# Agent 工作入口

先读 [AGENT_HANDOFF.md](AGENT_HANDOFF.md)，再按其中四份主文档定位当前任务。

- PROJECT_STATUS.md 是当前状态唯一摘要，历史按需读，不自动恢复 P2。
- 先检查分支和工作区，当前整理在 chore/project-cleanup，不自动合并 main 或 force push。
- 未知学生代码只走已验收 Docker，禁止宿主回退或绕过 F03/F04 白名单。
- experiments/feature_validation 和允许清单内静态工件是运行依赖，保留冻结摘要、案例、原提示和原路径。
- 不提交 .env、真实数据库、用户历史、收据、私人浏览器产物，不把模拟验证称为真人效果。
- 使用 README 显式轻量测试，不自动运行真实模型或 Docker 批处理。
