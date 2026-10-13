# GitHub 与分支操作

仓库：[2945604630/ai-coding-note](https://github.com/2945604630/ai-coding-note)。当前以根目录 [PROJECT_STATUS.md](../../PROJECT_STATUS.md) 和 [AGENT_HANDOFF.md](../../AGENT_HANDOFF.md) 为准。

| 分支 | 用途 | 本轮整理前提交 |
| --- | --- | --- |
| main | 稳定 V2 工程基线 | c40029c |
| ui/codehelper-reference | 已实现方向一 UI，未合并 | b194e0b |
| ui/agent-exploration | 已实现方向二 UI，未合并 | f1200ca |
| chore/project-cleanup | 从 main 创建的文档/归档整理 | 用 git log -1 查询 |

两套 UI 已分别提交；初始化时三分支相同的描述只属于历史。本轮不修改三分支，不自动合并，不 force push 或重写历史。

## 日常操作

```powershell
git status --short --branch
git fetch origin
git switch <目标工作分支>
# 审查、修改与必要测试后，明确列出文件：
git add <文件列表>
git diff --cached --check
git diff --cached
git commit -m "Describe the change"
git push -u origin <目标工作分支>
```

有未提交修改先安全保存，不通过丢弃数据解决切换冲突。按当前任务创建自己的工作分支；比较 UI 使用独立端口/数据目录，见 [本地设置](LOCAL_START.md)。

## 允许提交的范围

Web/API、沙箱代码、Provider、依赖、测试、配置示例，以及静态冻结校验所需的审核案例。experiments 保留逐文件允许清单；新增源码/案例需明确审查，再调整清单，不使用 git add -f。

docs 也采用显式文档允许清单。历史归档版脱敏私人路径和本地 chat ID，保留结果与证据强度；原始模型输出索引/完整回复、用户历史、截图和实际收据不随 Git 分发。被历史清单引用的原件留在本机原路径，归档版不能替代冻结摘要。

排除 .env/Key、SQLite/WAL/SHM、真实学习数据、Docker 收据/镜像 ID 文件、backups/output、浏览器记录、私人截图、缓存和虚拟环境。Git 中少量旧合成回复/结果属于冻结运行依赖，不是当前学习者数据，不能整体删除。

冻结路径支持 repo://，.gitattributes 保留字节，不修改摘要、schema 或审核白名单。发布检查可执行：

```powershell
python -X utf8 scripts/check_repository.py
```

新机器仍须独立 sandbox build/accept；不得复制另一机器收据。GitHub Pages 无法运行此服务器。尚无 LICENSE；公开可见性不自动授予开源复用许可。

## 网络与认证

本机直连 GitHub 曾超时，现有系统 loopback 代理可用。必要时仅为当前 Git 命令设置自己的代理：`git -c http.proxy=<已有本机代理URL> push -u origin chore/project-cleanup`。不改全局/系统设置，不关闭 TLS 校验，不打印或读取认证凭据。使用已有 Git Credential Manager 登录。

初始脱敏发布 d6e42ff、远程核对 c40029c。本轮三个主要远程分支已读取并与本地核对；整理分支单独提交/推送。当前本轮验收见 [CLEANUP_VALIDATION.md](../validation/CLEANUP_VALIDATION.md)。
