# Agent 交接入口

你接手的是 AIC AI 编程学习台：面向 Python 初学者的本机原型，连接代码编辑、Docker 执行、版本证据、AI 辅导与学习记录。工程 Demo 已有，UI 与真人交互仍待收敛。当前分支基于 V2，没有选择或合并 V3，没有新增教学机制。

## 从哪里开始

先读本文件，再依次阅读这四份文件即可开始，不需要扫描几十份历史报告：

1. [PROJECT_STATUS.md](PROJECT_STATUS.md)：当前阶段、真实能力与停止路线。
2. [README.md](README.md)：最短启动、离线回归与导航。
3. [ARCHITECTURE.md](ARCHITECTURE.md)：会话、版本、执行与教学快照。
4. [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)：执行、教学、数据与 UI 范围。

之后只读当前任务相关代码。历史入口是 [docs/archive/README.md](docs/archive/README.md)；旧报告的“下一步”“停止”“当前服务”仅适用原阶段。

## 立即启动

项目根目录执行：

```powershell
python -m pip install -r requirements-web.txt
$env:AIC_AI_PROVIDER = 'disabled'
python -X utf8 -m web_lab --port 8006 --data-dir data/aic_demo
```

打开 [127.0.0.1:8006](http://127.0.0.1:8006/)，选择固定规则 S0，不需要 Key/CLI 登录。Docker 未验收时自由执行关闭；新机器按 [本地设置](docs/setup/LOCAL_START.md) 独立 build/accept。真实 AI 配置见 [Provider 设置](docs/setup/AI_provider_setup.md)，改配置须停止旧 AIC 服务再启动。

README 有两组显式轻量回归；仓库检查是 `python -X utf8 scripts/check_repository.py`。不自动运行历史模型批处理或真实 Docker 测试。本轮未重新确认后台服务、Docker、模型的实时可用性。

## 代码入口

| 任务 | 文件 |
| --- | --- |
| HTTP 请求与本机边界 | `web_lab/app.py` |
| 会话、版本、队列、重试与教学守卫 | `web_lab/service.py`、`web_lab/teaching.py` |
| SQLite、导出、来源 | `web_lab/store.py`、`reporting.py`、`provenance.py` |
| Docker 合同、调度、运行、验收 | `web_lab/sandbox_contract.py`、`sandbox_service.py`、`sandbox_runtime.py`、`sandbox_setup.py`、`sandbox_image/` |
| 执行证据进入 AI | `web_lab/execution_context.py`、`service.py`、`teaching.py` |
| 模型适配 | `web_lab/ai_provider.py` |
| 学习 UI | `web_lab/static/`，V3 须切换对应分支 |
| F01～F05 固定引擎与案例 | `experiments/feature_validation/`，属于运行依赖 |
| 当前回归 | `web_lab/tests/`、F01～F05 原测试、`experiments/tests/` |

## 安全边界

- 不在宿主 Python 执行学生未知代码。旧宿主执行器仅接受固定审核白名单；自由保存代码走已验收 Docker，未就绪时关闭，不回退。
- Docker 只适用可信本机单人、标准库 Python 与有限 solve(n) 合同；监听 `127.0.0.1`，不转发局域网/公网，不宣称公网敌对隔离。
- 不绕过 F03/F04 的登记、哈希、合法输入与审核参考白名单；Docker 通过记录不构成旧白名单授权。
- 不泄露 API Key，不提交 `.env`、SQLite、用户学习历史、实际执行收据、浏览器数据、私人截图或备份。
- 不把指定测试通过当作学生掌握、整体修复或教学解释被认证；不把模拟/浏览器自动化当真人验证。
- 新版本不继承旧执行证据，教学快照不事后补写；原快照重试不偷偷换成新版建议。

## Git 分支

仓库：[2945604630/ai-coding-note](https://github.com/2945604630/ai-coding-note)。每次工作先检查分支和 git status。

| 分支 | 角色 | 整理前提交 |
| --- | --- | --- |
| main | 稳定 V2 工程基线 | c40029c |
| ui/codehelper-reference | 方向一：参考型工作台、错题与历史 | b194e0b |
| ui/agent-exploration | 方向二：代码优先工作台、错误/版本回顾 | f1200ca |
| chore/project-cleanup | 本次整理，基于 main | 用 git log -1 获取当前提交 |

本轮不修改三个主要分支，cleanup 单独推送，不自动合并 main。比较 V3 使用独立数据目录和端口，详见本地设置；UI 分支尚未包含本轮文档迁移。其报告只读导出到 `docs/archive/old-ui/`，不是 UI 代码合并。

## 哪些文件不要顺手改删

所有冻结/历史清单、schema、case、gold、登记目录、受控执行器、原提示/回复守卫，以及 Git 允许清单里的静态合成研究工件，都是运行或验收依赖。不能按 experiments/history/responses/results 的名称删除，也不能为了测试通过重算冻结摘要。

`data/`、`backups/`、`output/`、`.playwright-cli/`、本地 user_runs 与浏览器草稿是本机数据，不未经审查打包或入 Git。部分原始报告因历史清单引用仍在忽略的旧路径；公开归档版不替代其原字节。完整清单见 [保留本机文件](docs/validation/RETAINED_LOCAL_FILES.md)。

## 推荐下一个任务

1. 比较两个 V3 UI 的完整练习流程。
2. 由使用者选择最终方向。
3. 真人完成一次完整练习，区分真实输入、脚本、固定规则和真实 AI。
4. 修复观察到的交互问题。
5. 再准备 AIC 提交材料；日期、资格与规则届时另行核对。

不要自动恢复 P2，不继续小机制海选：A NO-GO、B NO-GO、R1 NO-GO。失败结果用于避免重走停止路线。

只克隆 Git 就能启动网页与运行轻量回归；不能由 Git 恢复私人数据库、原始调用、完整历史审计材料或有效 Docker 收据。
