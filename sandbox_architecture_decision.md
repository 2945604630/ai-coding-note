# AIC V2 本机沙箱决策（2026-10-11）

本轮仅实现 P1-A/P1-B，不改 F01～F05、受控执行器或冻结工件，不进入 P2/F06。

## 环境检查

Windows 11 家庭版 10.0.26100.1457；Python 3.12.10；FastAPI 0.118.3、Uvicorn 0.49.0、Pydantic 2.13.4、httpx 0.28.1。WSL 2.7.12.0，Ubuntu VERSION=2，内核 6.18.33.2 能启动。Windows PATH、Docker Desktop 默认安装位置、Ubuntu PATH 和 `/var/run/docker.sock` 均未发现 Docker。HyperVisorPresent=True；WMI 的 CPU 虚拟化字段为 False，与可启动 WSL2 不一致，不能据此要求修改 BIOS。

8000、8006 已由旧 AIC 服务占用；验证使用独立端口与数据目录，不重启旧服务、不改其数据库。Docker 安装、管理员设置、系统虚拟化与重启须由用户确认后进行，本轮不执行这些动作。

## 方案比较

| 项目 | 每任务独立 Docker | 自托管 Judge0 CE | 自托管 Piston |
|---|---|---|---|
| Windows | Docker Desktop Linux/WSL2；需验证 Engine | Linux 容器，多服务；需核对内核/cgroup 与 Isolate | Linux 容器；官方要求 cgroup v2 |
| 隔离/权限 | namespaces+cgroups+默认 seccomp；任务非 root、无 capability、无特权；控制端能控制 Docker，必须可信 | Isolate；官方 Compose 的 server/worker 使用 privileged，不能直接认定安全 | Isolate；官方单容器启动使用 privileged，不能直接认定安全 |
| Python | 单一固定标准库镜像 | 现有语言运行时 | 安装 Python runtime |
| C/C++ | 后续另审核编译镜像和编译阶段；本轮无支持 | 原生多语言编译/运行 | 原生多语言编译/运行 |
| 判题 | 本地版本绑定、已审核合同、逐例比较 | submission token、状态、stdout/stderr、expected_output、资源结果 | execute 返回 compile/run；需要应用层判题 |
| 运维 | 一个 Engine、一份镜像，无常驻执行容器 | API/worker/PostgreSQL/Redis，配置与升级面较大 | Node API、运行时包、Isolate/cgroup 配置 |
| 占用/开销 | Docker Desktop/WSL 占主要成本；每任务容器启动开销，128 MiB/0.5 CPU 上限 | 多服务及多语言镜像通常较重 | 按所装运行时增长，常驻 API |
| F03/F04 | 独立通路；旧白名单完全保留 | 需映射合同和版本，不能绕过旧审核 | 同左，且自行补判题接口 |

占用与延迟是架构推断；没有 Docker，本机未测镜像体积或真实执行延迟，不给出虚构 GB/毫秒。依据：[Docker Windows 安装](https://docs.docker.com/desktop/setup/install/windows-install/)、[Docker 安全边界](https://docs.docker.com/engine/security/)、[资源限制](https://docs.docker.com/engine/containers/resource_constraints/)、[Judge0 Compose](https://github.com/judge0/judge0/blob/master/docker-compose.yml)、[Judge0 API](https://ce.judge0.com/)、[Piston 官方说明](https://github.com/engineer-man/piston)。

## 决策与数据流

选独立 Docker 任务作为本机单人 Demo 最小方案。执行组件在 `web_lab/sandbox_runtime.py`，调度与数据库适配在 `sandbox_service.py`；复用现有仅监听 127.0.0.1 的 FastAPI 入口，不另开公网服务。

浏览器先保存源码 → 提交 version_id + SHA-256 + request_id → 后端按会话读取不可变源码、复算哈希 → 校验合同 → 写任务 → 后台创建独立容器 → 检查实际容器配置 → 传入源码与输入（stdin，无宿主挂载）→ 限量捕获 stdout/stderr → 检查容器退出码/OOM → 删除并确认容器不存在 → 写最终状态。服务异常、缺少镜像、超时、输出超限、清理失败均不会获得 passed。

任务固定 UID/GID 65534；network=none；cap-drop=ALL；no-new-privileges；只读根文件系统；默认 seccomp；CPU 0.5、内存/内存加 swap 128 MiB、pids 32、CPU 秒数 2、墙钟 3 秒（容器内监督器）及控制端 6 秒、nofile 64、单文件 1 MiB、tmpfs 16 MiB/256 inode、合并输出 16 KiB。任务无项目、桌面、数据库、密钥、Docker socket、设备或端口挂载；禁止提供自选镜像/命令。镜像中的监督器也在控制端死亡时终止任务。Docker 控制命令有独立有限超时。

固定镜像由维护者构建，基础镜像先解析成 digest；本地 image ID、镜像内容及策略哈希写入服务器数据目录。只有通过真实 Docker 三程序及守卫验收的 receipt 才开放自由源码；策略/镜像/Engine 变化、清理失败会关闭入口。配置文件和收据属于可信维护者权限范围，不允许学生修改。

运行代码展示真实 stdout/stderr 与退出状态；提交比较适配器打印的 solve 返回值与后端参考输出。stdout 额外打印也会影响比较，页面明确说明。只使用旧合同输入 0、1、3；不新增题库。当前没有真正隐藏测试。若后续另审核隐藏项，接口只给计数/状态，隐藏输入、stdout、stderr、参考输出和实现均不返回浏览器；不能将已出现在旧证据中的输入称为隐藏测试。

每个新 request_id 创建新任务，不按源码缓存证据。重复网络请求仅可取回同一输入、同一版本、同一合同的原任务；跨版本复用 request_id 被拒绝。新记录不更新旧 `execution_allowed`，不插入教学证据，不认证掌握或整体正确。

## 实施与验收顺序

1. 先写版本绑定、不可用失败记录、脱敏、Provider 替换的失败测试。
2. 实现独立 Docker runtime、固定镜像、检查/构建/真实验收命令；缺少 Docker 时拒绝执行。
3. 新增 append-only 任务表与运行/提交/历史接口，对接现有 V2 编辑器。
4. 实现 codex_cli/api/disabled Provider；保留原 CLI 传输和教学守卫。
5. 运行确定性测试、旧接口/F03/F04 回归、浏览器交互与本机 HTTP 检查；真实 Docker 三程序无法运行则明确记为未执行。

## 边界

普通 Docker 与共享 Linux 内核不是专门的强敌对多租户沙箱；没有 gVisor/Kata/microVM 或 ECI 的验证。本机单人有限试用还需要已更新 Engine/基础镜像、真实资源与终止/清理验收、可信维护者保护控制端。未经这些条件，不上线未知源码执行。不能用于公网、不可信多人或恶意逃逸测试。
