# 本地设置与 UI 试用

适用 Windows 10/11、Python 3.12。命令在仓库根目录执行，服务仅监听 127.0.0.1，每个数据目录一个进程。

## 首次离线启动

```powershell
git clone https://github.com/2945604630/ai-coding-note.git
cd ai-coding-note
git switch chore/project-cleanup
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-web.txt
Copy-Item .env.example .env
$env:AIC_AI_PROVIDER = 'disabled'
.\.venv\Scripts\python.exe -X utf8 -m web_lab --port 8006 --data-dir data/aic_demo
```

打开 [学习台](http://127.0.0.1:8006/)，选择 S0。环境变量优先于 .env；离线选择不改仓库默认 codex_cli。已有 .env 不要覆盖。真实 AI 按 [Provider 设置](AI_provider_setup.md) 配置并重启。

## 自由执行的前提

Docker Desktop 已运行 Linux Engine，虚拟化/WSL2 正常，需要 cgroup v2 与默认 seccomp。新机器独立构建验收，不继承其他机器或目录的 ready 收据。下面会实际运行 Docker 代表场景，不属于整理的轻量回归：

```powershell
.\.venv\Scripts\python.exe -X utf8 -m web_lab.sandbox_setup check --data-dir data/aic_demo
.\.venv\Scripts\python.exe -X utf8 -m web_lab.sandbox_setup build --data-dir data/aic_demo
.\.venv\Scripts\python.exe -X utf8 -m web_lab.sandbox_setup accept --data-dir data/aic_demo
```

失败保持自由执行关闭。镜像/策略/Engine 变化后重新验收，不采用宿主回退。范围与复验见 [沙箱实测](../validation/sandbox_test_results.md)。

## 比较两套 V3

先确保工作区干净。cleanup 未合并 V3，须切换 UI 分支；不用 V2 的学习数据库：

```powershell
git status --short --branch
git switch ui/codehelper-reference
$env:AIC_AI_PROVIDER = 'disabled'
python -X utf8 -m web_lab --port 8007 --data-dir data/aic_ui_codehelper
```

停止该 AIC 服务，检查工作区后再试方向二：

```powershell
git switch ui/agent-exploration
$env:AIC_AI_PROVIDER = 'disabled'
python -X utf8 -m web_lab --port 8008 --data-dir data/aic_ui_agent
```

每个新目录需独立 sandbox build/accept 才能自由执行。端口须空闲；启动入口发现已有 AIC 服务时可能打开旧服务，不能凭地址认定已加载新分支。改分支/Provider 后停止旧 AIC 再启动，不必重启 Docker/WSL。

UI 分支没有本轮文档迁移。比较结束且工作区干净后切回 chore/project-cleanup 阅读交接，不自动合并任一 UI。
