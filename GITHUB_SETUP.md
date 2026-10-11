# AIC V2 GitHub 版本管理

仓库：https://github.com/2945604630/ai-coding-note 。初始化时远程为空且为 Public；保持已有可见性。GitHub CLI 未安装，本次通过 Git Credential Manager 的既有登录推送，不读取或打印凭据。

## 稳定基线与分支

- `main`：原始 V2 的发布基线，保留 F01～F05、现有页面、沙箱、Provider 和执行证据接入。
- `ui/codehelper-reference`：后续参考合理可用的交互理念，不直接复制未授权代码或素材。
- `ui/agent-exploration`：后续独立调研与设计实现。

初始化的三条分支指向同一个首次提交；以 `git rev-list --max-parents=0 main` 查询可追溯基线。两个 UI 分支本轮没有任何界面修改。后续先切换自己的分支、检查状态、提交后再推送；不直接在 main 上试验。

```powershell
git status --short
git switch ui/codehelper-reference
# 修改、检查差异与测试后：
git add <明确的源码文件>
git diff --cached
git commit -m "Describe the UI change"
git push -u origin ui/codehelper-reference
```

另一条分支使用 `git switch ui/agent-exploration`。工作区有未提交修改时先提交或安全保存，禁止通过丢弃数据解决切换冲突。合并稳定版本前审查差异和测试；不要强制推送、删除远程分支或重写既有历史。更改仓库可见性、创建新仓库和选择 LICENSE 需所有者确认。

## 上传安全范围

上传 Web 后端、前端资源、Dockerfile/沙箱源码、服务器配置示例、依赖、测试、运行与验收说明，以及冻结校验必需的已审核静态案例。`.gitignore` 对 experiments 使用逐文件允许清单，保留极少量旧 F03～F05 启动校验必需的合成研究工件；这些工件不是当前学习者记录或当前 Docker 收据。添加实验源码或静态案例时显式审查并调整允许清单，不使用 `git add -f`。

排除服务器 `.env`、密钥、SQLite 与 WAL/SHM、用户代码和会话/学习记录、真实 Docker 任务/收据/镜像 ID、backups/output、浏览器记录/截图、缓存、虚拟环境、模型调用原始日志，以及无需发布的历史研究/P2 工件。全部原件保留在本地。初始化前 Git 没有提交、没有追踪文件，因而不存在需要清理的旧 Git 历史。

必要的冻结元数据内本机路径已改为 `repo://`；摘要工具仅增加受项目目录约束的路径解析，原绝对路径兼容保留。必要历史元数据的外部本机路径已脱敏。冻结清单同步计算发布文件摘要，未取消完整性检查、源码哈希或审核白名单。原始字节与变更摘要保存在忽略的 `backups/github_original_*` 和 `output/github_sanitization.json`。这些发布文件不应被解释为未经脱敏的原始验收收据。

旧 CLI 本机技能清单改为无个人路径的空配置；既有禁用工具/插件、跳过本机技能发现、空工作目录、schema 和回复守卫保留。`.gitattributes` 禁止自动换行转换，确保克隆后 SHA-256 校验一致。

## 复现与限制

安装、启动和轻量测试见 README。新机器需独立构建并通过沙箱验收；不要复制另一机器的通过收据或公开服务。默认仅 127.0.0.1、单进程与单人可信本机有限使用。AI Key 仅在服务器 `.env` 或环境变量配置；不要提交或放入数据库/浏览器/日志。

没有新增 LICENSE，也没有引入第三方 UI 资产。公开仓库并不代表本项目已授予开源复用许可。后续需要开源时，由所有者选择许可证；依赖的许可与使用条件单独适用。

初始化验证（2026-10-12）：222 个上传文件约 1.6 MB；凭据格式、私钥、含凭据 URL、本机用户路径和私人邮箱扫描未发现匹配，禁止文件类型检查通过。原工作区 53 项轻量回归通过，独立干净目录 9 项回归通过；F01～F05 冻结/目录校验与无模型调用的 CLI 命令构造通过，清单路径逃逸被阻断。现有 8006 服务健康、沙箱仍 ready。未进行真实模型调用、未构建镜像或重复 Docker 压力验收。扫描是发布前检查，后续提交仍须复查；本仓库不附带当前本机学习与执行数据。

实际已通过普通原子推送创建三条远程分支；首次提交为 `d6e42ffd65f13dfe8c5e2b956a2c44f29d84b102`。远程重新克隆的 222 个文件与测试过的发布文件逐字节一致，冻结/目录校验通过。后续这份说明的补充提交也同步到两条 UI 分支，当前共同基线可用 `git rev-parse main ui/codehelper-reference ui/agent-exploration` 核对。

本机直连 GitHub 443 曾超时；系统本地代理可用但 Git 未自动继承。推送使用命令级 `git -c http.proxy=<本机已配置的代理URL> push --atomic origin main ui/codehelper-reference ui/agent-exploration` 成功。后续若网络相同，使用自己的代理地址；不改系统/全局配置，不关闭证书校验，也不使用强制推送。

发布路径支持要求已有 Python 进程重新加载模块。本次确认无执行中任务、备份数据库后按原端口/数据目录重新启动网页服务；Docker、镜像、Provider 配置保持原状。重启后 7 个原会话详情均 HTTP 200，10 张数据库表的全部原始行摘要一致，沙箱继续 ready。后续更新代码或冻结元数据时也须停止旧网页进程再启动，不用重启 Docker/WSL。
