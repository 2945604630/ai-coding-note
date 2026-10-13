# AIC 学习台 V3 · 自主探索型 UI

当前分支 `ui/agent-exploration` 从原 V2 基线独立实现。采用代码为主、结果在下、辅导在旁的工作台：编辑器保留在当前练习，错误回顾可返回实际失败版本，历史代码恢复为新草稿后再保存。首页只展示现有两道练习，开发测试记录默认隐藏。设计选择和验收见 [UI_DIRECTION_2_REPORT.md](UI_DIRECTION_2_REPORT.md)。

方向二本地启动（独立开发数据，端口 8008）：

```powershell
python -X utf8 -m web_lab --port 8008 --data-dir output/aic-v3-test
```

打开 [方向二 V3 学习台](http://127.0.0.1:8008/)，也可双击 `start_v3.bat`。已保存版本才可运行；编辑草稿、历史版本查看和未完成运行会阻止发送辅导。快捷键：代码区 Ctrl+S 保存，Ctrl+Enter 运行；辅导区 Ctrl+Enter 发送。AIProvider、Docker 安全策略和 F01～F05 沿用 V2。新机器须按下方流程对独立目录自行 build/accept，不得继承另一机器的收据；沙箱不可用时页面会如实禁用执行。

本轮验收临时禁用真实模型并使用 S0 固定规则；交付服务恢复原 `codex_cli` Provider，没有真实模型或付费 API 调用。下方保留 V2 的安装、安全边界和功能说明；V2 稳定代码仍在 `main`。

## V2 基线与运行边界

AIC 是一个将代码版本、真实执行记录和 AI 教学对话关联起来的本地 Python 编程练习台。包含 F01～F05、学习页面与实验管理、Docker 沙箱、AIProvider，以及当前版本执行证据投影。运行完成、指定测试通过、教学主张核验分别记录；不自动认定学习者掌握或程序整体正确。

## 首次安装与启动

要求 Windows 10/11、Python 3.12、Git；自由代码执行还要求已启用虚拟化和 WSL2 的 Docker Desktop、可用的 Linux Engine、cgroup v2 与默认 seccomp。安装和管理员设置由使用者完成。Codex CLI 是可选的服务器端依赖；使用 `codex_cli` 时需自行安装兼容 CLI 并通过产品登录。离线使用 `disabled` 与 S0。

```powershell
git clone https://github.com/2945604630/ai-coding-note.git
cd ai-coding-note
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-web.txt
Copy-Item .env.example .env
# Docker Desktop 启动并切换到 Linux 容器后，首次在此机器构建、验收：
.\.venv\Scripts\python.exe -X utf8 -m web_lab.sandbox_setup check --data-dir data/aic_demo
.\.venv\Scripts\python.exe -X utf8 -m web_lab.sandbox_setup build --data-dir data/aic_demo
.\.venv\Scripts\python.exe -X utf8 -m web_lab.sandbox_setup accept --data-dir data/aic_demo
.\.venv\Scripts\python.exe -X utf8 -m web_lab --port 8006 --data-dir data/aic_demo
```

首次验收只执行已定义的代表场景及必要安全守卫，不调用 AI。本机镜像和验收收据不随仓库上传；新克隆不能继承其他机器的安全验收。验收失败时自由执行保持关闭，禁止主机执行回退。网页和离线功能仍可启动。已有环境的一条启动命令见下文；也可运行 `start_web.bat`。

轻量回归使用模拟 Provider/执行传输，不产生付费请求或 Docker 压力测试：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -X utf8 -m unittest web_lab.tests.test_ai_provider web_lab.tests.test_api web_lab.tests.test_demo web_lab.tests.test_learning_v2 web_lab.tests.test_sandbox
```

`test_teaching_execution` 的真实 Docker A/B/C 验收代码另行保留，只应在本机沙箱验收后按需运行；本次 GitHub 初始化不重复执行。历史验收文档中的本地收据、模型输出和数据库未上传，不能以文档替代新机器的验收。

## 当前能力与操作

2026-10-11 已构建固定 Python 镜像并通过真实 Docker 隔离验收。网页现在可以运行和提交新保存、未登记的 Python 源码。F03/F04 原白名单与历史数据保留；AIProvider 已支持 codex_cli/api/disabled，本轮没有付费 API 调用。

2026-10-12 已接入当前版本执行上下文：保存代码，等待运行或提交结束，再向右侧 AI 发送疑问，服务器会自动带入准确版本/hash 与已保存的 Docker 结果。无新版运行、失败、超时与过期记录都有独立标记；生成期间保存新版会阻断该轮建议。完整验收与限制见 [teaching_execution_integration.md](teaching_execution_integration.md)。本轮使用 Provider 替身验收，未调用真实模型。

在项目目录执行一条启动命令：

```powershell
python -X utf8 -m web_lab --port 8006 --data-dir data/aic_demo
```

打开 [本地学习台](http://127.0.0.1:8006/)。交付时服务已在该地址运行，重复执行会打开现有服务。数据位于 `data/aic_demo`。修改配置后须先停止现有 AIC 进程再启动；不要用两个进程或多个 worker 共享此目录。依赖见 `requirements-web.txt`。

先保存修改，再使用「运行代码」或「提交测试」。代码需要定义 `solve(n)`；输入是 0～8 的整数，布尔值不合法。运行使用自定义输入，展示 stdout/stderr 和函数返回值；审核输入会附参考输出，其余输入记录空参考，不作判题。提交只比较既有合同的 0、1、3 三例；额外打印也参与比较。输出与记录在代码面板内，向下滚动可查看全部测试；运行历史可展开、刷新恢复。

每次点击生成独立任务，保存源码版本和 SHA-256、输入、实际/参考输出、状态、耗时及执行/清理证据。未保存草稿不能运行；切换版本只展示该版本结果。新沙箱记录不把自由源码变成 F03/F04 审核版本，也不证明掌握或整体正确。

新证据辅导使用 S1；固定 S0 规则仍为原算法。AI 只收到带来源和截断标记的有限摘录，原始记录保留。先完成本次运行再发送；教学快照不会在任务结束后回填。仍保留首次引导加最多两次后续回复，因版本变化阻断后的原快照重试不能沿用为新版，请新建会话继续。

默认 AI 继续使用已登录 Codex CLI。需要离线时在服务器 `.env` 或环境变量设置 `AIC_AI_PROVIDER=disabled`；未来 API 配置见 [AI_provider_setup.md](AI_provider_setup.md)，示例不含真实密钥。

当前验收仅适合可信本机单人有限练习。服务固定监听 127.0.0.1；普通 Docker 共享 Linux 内核，没有验收 gVisor/Kata/microVM/ECI。Python 仅标准库，不能安装依赖、联网、使用 C/C++ 或自选启动命令；每例限制 0.5 CPU、128 MiB、32 进程、容器内 3 秒及控制端 6 秒、合并输出 16 KiB、临时空间 16 MiB、单文件 1 MiB。不要将此服务转发到局域网或公网。

[sandbox_test_results.md](sandbox_test_results.md)记录实测结果、证据、复验步骤及剩余安全限制。镜像、执行策略或 Engine 变化后入口会关闭，须重新 build/accept；没有通过验收时不会回退到宿主 Python。

## GitHub 与 UI 分支

仓库只分发源码及必要静态工件。GitHub Pages 无法运行 FastAPI、SQLite、Docker 或服务器端 AIProvider，因此不能完整部署本项目；不要公开转发本地执行服务。

`main` 保存稳定 V2；`ui/codehelper-reference` 用于后续参考编程练习、错题记录和教学交互理念，不复制未授权代码或素材；`ui/agent-exploration` 用于后续独立调研和实现 UI/UX。两条分支从同一首次提交开始，本轮没有 UI 修改。开发规范、发布脱敏与排除范围见 [GITHUB_SETUP.md](GITHUB_SETUP.md)。

当前未选择 LICENSE，不声明新的开源授权。未捆绑第三方实现或 CodeHelper 素材；Python/FastAPI/Uvicorn/httpx、Docker 基础镜像和可选 CLI 的许可证及使用条件分别适用。公开复用或后续引入第三方素材前，应由项目所有者确认许可证。
