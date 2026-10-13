# AIC AI 编程学习台

面向 Python 初学者的 AI 编程练习原型，将代码编辑 → Docker 真实执行 → 版本证据 → AI 辅导 → 错误与学习记录连接起来。

新 Agent 从 [AGENT_HANDOFF.md](AGENT_HANDOFF.md) 开始；[PROJECT_STATUS.md](PROJECT_STATUS.md) 是当前进度的唯一权威摘要。系统关系见 [ARCHITECTURE.md](ARCHITECTURE.md)，使用边界见 [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)。本轮只整理工程，暂停功能开发。

## 已实现

- main 和 cleanup 保留 V2 Web：学习首页、代码编辑、教学对话、版本与记录、实验管理和导出。
- 两套 V3 UI 已分别实现于 `ui/codehelper-reference` 和 `ui/agent-exploration`，尚未选择或合并；切换对应分支才会看到 V3 页面。
- Docker sandbox 独立执行已保存的新代码。run 展示一次观察；submit 比较既有合同的指定测试。任务关联 session、version、SHA-256、输入、真实输出和清理状态。
- AI Provider 支持 `codex_cli` / 兼容 Chat Completions 的 `api` / `disabled`。服务端将当前保存版本的执行记录投影为 execution_context，再进入教学快照；版本变化会阻断旧建议。
- F01：一次回应的有限教学动作；F02：有停止条件的连续追问。原提示、格式、守卫和规则模式保留。
- F03：审核白名单的事实核验；F04：修改前后版本与回归对照；F05：首次作答、帮助来源和有限资格记录。自由代码的 Docker 通路独立于这些白名单。

## 尚未实现或证明

没有长期学习效果证据，也没有成立的独立教学算法创新。P2-A / B / R1 均已 NO-GO，不再继续小机制海选。不支持公网多人恶意代码执行；题目与 Python 合同有限。外部 API 需使用者自行配置，尚未完成真实外部 API 联通和回复质量验收。两套 V3 UI 待最终选择及真人完整练习。

## 最短本地启动

需要 Python 3.12。以下采用离线规则，不发起模型请求；Docker 未验收时网页可用，自由执行关闭。

```powershell
python -m pip install -r requirements-web.txt
$env:AIC_AI_PROVIDER = 'disabled'
python -X utf8 -m web_lab --port 8006 --data-dir data/aic_demo
```

打开 [本地学习台](http://127.0.0.1:8006/)，选择 S0。已有依赖时只需后两行；原 `start_web.bat` 沿用当前 Provider 配置，默认是 codex_cli。一个数据目录只允许一个服务进程。

首次虚拟环境、Docker build/accept 和 UI 试用见 [本地设置](docs/setup/LOCAL_START.md)；模型配置见 [AI Provider](docs/setup/AI_provider_setup.md)，示例见 [.env.example](.env.example)。Key 仅在服务器 `.env` 或环境变量。新机器必须独立验收 Docker，不能继承本机收据。

## 轻量回归

```powershell
python -m pip install -r requirements-dev.txt
python -X utf8 -m unittest web_lab.tests.test_ai_provider web_lab.tests.test_api web_lab.tests.test_demo web_lab.tests.test_learning_v2 web_lab.tests.test_sandbox
python -X utf8 -m unittest experiments.feature_validation.F01_response_adaptation.test_core experiments.feature_validation.F02_dynamic_questioning.test_core experiments.feature_validation.F03_evidence_verification.test_verifier experiments.feature_validation.F04_self_modification.test_core experiments.feature_validation.F05_independent_assessment.test_core
python -X utf8 scripts/check_repository.py
```

测试使用 Provider/沙箱传输替身，以及审核固定案例，不调用模型或启动 Docker 任务。不要以无筛选的测试发现替代：`test_sandbox_live` 与 `test_teaching_execution` 含真实 Docker 场景。

源码和测试保留原目录 `web_lab/`、`web_lab/tests/`、`experiments/feature_validation/`、`experiments/tests/`。当前设置、架构细节、验收分别在 `docs/setup/`、`docs/architecture/`、`docs/validation/`。历史从 [归档索引](docs/archive/README.md) 按需查阅。

Git 操作见 [GitHub 说明](docs/setup/GITHUB_SETUP.md)。GitHub Pages 无法运行 FastAPI、SQLite、Docker 和服务器端 Provider。尚未选择 LICENSE，依赖许可分别适用。
