# P1-A/P1-B 真实沙箱验收（2026-10-11）

**真实隔离环境已启动，学生自由保存源码已在网页中实际执行；运行、提交、记录查看可用，可以开始可信本机单人有限试用。**既定 Docker 方案保持不变，F01～F05 教学机制、F03/F04 白名单及 P2 研究未改动。没有在宿主 Python 中执行未知学生源码。

## 实际环境与固定镜像

| 项目 | 实测 |
|---|---|
| Windows / Python | Windows 11 10.0.26100.1457；宿主 Python 3.12.10 |
| WSL2 | 2.7.12.0；Ubuntu 与 docker-desktop 登记 VERSION=2；检查时 CLI 列为 Stopped，但 Engine 能响应且真实 Linux 容器能运行 |
| Docker | Desktop 4.94.0；Engine 29.8.2；desktop-linux；本机 named pipe；linux/amd64 |
| 内核 / 安全 | 6.18.33.2-microsoft-standard-WSL2；cgroup v2；默认 runc、内置 seccomp；Engine 未报告资源/安全 warning |
| 后端依赖 | FastAPI 0.118.3、Uvicorn 0.49.0、Pydantic 2.13.4、httpx 0.28.1 |
| 监听 | 实测仅 127.0.0.1:8006；交付时更新版服务仍可访问 |
| 镜像 | Python 3.12.15、标准库；构建关闭网络，仅复制受审核监督器/适配器；不接受用户镜像或命令 |

基础镜像解析后固定为 `python@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258`。

最终运行镜像为 `sha256:65f515c2b3870e0f288350447fe7a7d32a566b4d33543597e62935a665f89db8`，策略哈希 `842b011ed3b81e9fc1cd4410625daad6485bbeb40fdb35de67ca8f167a6c0b39`。Docker 报告镜像逻辑大小 197,172,381 字节（约 188 MiB），不代表 Docker Desktop/WSL 总磁盘占用。

最终真实验收于北京时间 19:41:57 通过，`data/aic_demo/sandbox/acceptance.json` 保存 accepted=true、Engine 指纹、镜像/策略哈希及每个检查的执行和清理结果。环境证据在 `output/p1_docker_environment.json`。本轮未修改管理员设置、重启 Windows 或降低隔离要求。

## 三个代表场景

只使用正确、错误、无限循环三个核心程序类型，另做必要良性守卫；没有恶意逃逸样本或大规模模型测试。修正后复验重新创建任务，首轮记录保留。

| 场景 | 最终真实容器验收 | 网页运行 / 提交 |
|---|---|---|
| 正确 `n*(n+1)//2` | n=3 输出 `6\n`，completed，1.393 秒 | 自定义 n=8 输出 36，completed；提交 0/1/3 全 passed |
| 错误 `n*(n-1)//2` | n=3 输出 `3\n`，与参考 6 不同，1.251 秒 | 运行 completed 并附参考 6；提交 failed，显示实际 3 / 参考 6 |
| 无限循环 | timeout，实际容器退出码 124，4.098 秒 | 运行及提交均 timeout；提交在首个超时测试停止，没有伪造其余结果 |

耗时包含容器创建、配置检查与清理；3 秒是容器内部墙钟期限，因此上述端到端耗时可超过 3 秒。循环在控制端 6 秒期限之前由容器监督器终止。所有任务均 executed=true、cleaned=true。

真实浏览器会话：`539fa65fc46746e0b72ba4b97693bc80`，标记 automated_test、S0，不调用模型。最后一次网页验收任务如下，完整版本/哈希/输入/输出/参考/容器结果见 `output/p1_evidence_audit.json`：

| 场景 | 运行任务 | 提交任务 |
|---|---|---|
| 正确 | `f5c9a10acd064539b007e01afca3e06a` | `967c6bf6751c428b8425ca732731d570` |
| 错误 | `6eebe458a8b946628ebef29630c373f7` | `083579b1384b488480602e09d469bc01` |
| 超时 | `636b9e5fab274bcbb4220a94465a9606` | `e599c4f4a9a04c7b879bca399a25bc85` |

## 安全边界与记录守卫

| 边界 | 验证方式与结果 |
|---|---|
| 每例独立、无宿主暴露 | 创建后、启动前 inspect 实际配置：固定镜像/入口；无 bind、volume、设备、端口、Docker socket 或宿主 namespace；仅 /tmp tmpfs。每例不同容器，最终不存在遗留任务容器 |
| 默认断网 | NetworkMode=none；容器只有 lo；对文档保留地址的有界连接返回 ENETUNREACH，没有外网连接成功 |
| 非特权与最小权限 | UID/GID 65534，Privileged=false、cap-drop ALL；容器 CapEff=0、NoNewPrivs=1、Seccomp=2；根文件系统只读，实际 /runner 写入失败 |
| 无密钥、无软件安装入口 | 没有传递 AIC_* / DOCKER_* 宿主变量；代理变量清空；pip 不存在；无宿主桌面、项目或 Docker socket 路径。镜像只读、非 root 且断网 |
| CPU / 内存 / swap | inspect 与容器实际 cgroup 验证 0.5 CPU、128 MiB memory.max、memory.swap.max=0；CPU rlimit 2 秒；没有放宽配额 |
| 进程与临时文件 | pids.max=32；最多尝试 34 个短寿命 sleep 子进程，在配额处返回 EAGAIN，并回收所有子进程；tmpfs 16 MiB/256 inode，有限写入在空间配额处返回 ENOSPC；超过单文件 1 MiB 写入失败；nofile=64 |
| 输出限制及清理 | ASCII 输出超限得到 output_limit，最多 16,384 字节；无效 UTF-8 替换后也不得扩张，实测 16,383 字节、output_limit。两类容器都清理成功 |
| 准确版本绑定 | 后端复算保存源码哈希，任务关联不可变 version_id；API 拒绝错误哈希、跨会话、非法输入、自选镜像；浏览器草稿禁用、切换版本不沿用结果 |
| 不复用旧执行证据 | 新请求 ID 创建新任务；真实网页跨版本复用旧请求得到 409；同一网络请求只允许相同版本/哈希/输入/合同的幂等取回；复验新任务未使用旧成功结果 |
| 失败不能变成功 | 故障注入验证异常、未确认实际执行与清理失败均 service_error；未验收或 Engine 指纹变化保持关闭。真实 Engine/固定镜像存在时，false 收据及变更指纹也不能执行 |
| 持久记录 | SQLite 保存任务、输入、结果与耗时；源码保存在准确关联版本；审核参考随结果保存，自定义未审核输入保存 expected_output=null；提交合同输入仅后端保存；完成事件包含 task_id/version_id/hash/status；JSON 导出包含任务 |
| 隐藏信息 | 当前合同没有真正隐藏测试，也不返回参考实现。守卫测试确认未来标为隐藏的输入、stdout/stderr、参考输出不会进入公开结果 |

验收守卫在真实容器内得到 21 项 true；资源探针均固定次数和大小。没有进行 OOM 压力基准、CPU 性能基准、恶意逃逸或攻击测试，不把配置/良性检查称为强敌对隔离证明。

## 回归与历史保留

最终命令：

```powershell
python -X utf8 -m unittest web_lab.tests.test_api web_lab.tests.test_demo web_lab.tests.test_learning_v2 web_lab.tests.test_sandbox web_lab.tests.test_ai_provider web_lab.tests.test_sandbox_live experiments.feature_validation.F03_evidence_verification.test_verifier experiments.feature_validation.F04_self_modification.test_core -v
```

最终 56 项通过，0 失败、0 跳过，其中 3 项真实 Docker 核心场景、4 项模拟 Provider 测试、15 项旧 F03/F04 回归。日志：`output/p1_final_regression.log`。旧回归只执行既有受审核运行链，不是自由源码的宿主回退。

F01/F02 和 F04 冻结工件检查通过；真实网页「核验登记版本」仍能核验原登记代码，自由源码仍 execution_allowed=false/unverified，旧接口不执行未登记代码。新沙箱证据没有写入旧教学证据或解除旧白名单。

启动前备份：`backups/p1_docker_20261011_before`。逐行对照确认原 6 个实验、10 个源码版本、4 个轮次、4 个调用尝试、2 个笔记、63 个事件、2 个 demo 操作及 3 个验收索引未改变；68 个原 artifacts 文件 SHA-256 相同。原始记录未删除；本轮两次网页验收共 12 条新任务完整保留。审计脚本为 `output/p1_evidence_audit.py`。

浏览器验证保存/刷新、参考比较、版本切换、草稿禁用、真实超时和旧核验。脚本：`output/playwright/verify-sandbox-live.js`；日志与三张截图在 `output/playwright/`。预期的 409 守卫请求产生浏览器资源错误日志，没有页面脚本异常。JS 语法检查通过。

修复并复验两处问题：无效 UTF-8 可能扩张输出长度；服务器 `.env` 编码名称错误。浏览器验收脚本初次等待过早也已纠正，最终结果来自新任务完整执行后的断言。

## 复现与已知安全限制

启动命令与操作流程见 [README.md](README.md)；AI 设置见 [AI_provider_setup.md](AI_provider_setup.md)。需要重建或维护者复验时，先停止使用该数据目录的服务，在项目目录依次执行：

```powershell
python -X utf8 -m web_lab.sandbox_setup check --data-dir data/aic_demo
python -X utf8 -m web_lab.sandbox_setup build --data-dir data/aic_demo
python -X utf8 -m web_lab.sandbox_setup accept --data-dir data/aic_demo
```

未就绪的 check、失败的 build/accept 返回非零；accept 失败保留 accepted=false。策略/镜像/Engine 指纹变化要重新验收；清理不能确认时执行关闭并要求维护者处理。源码不会回退到宿主 Python。

- 普通 Docker 共享 WSL/Linux 内核；未验收 gVisor、Kata、microVM 或 ECI，也未完成独立镜像漏洞扫描。适用可信本机单人有限练习，不具备公网、不可信多人或恶意代码服务的安全结论。
- Docker 控制端、数据目录中的配置与验收收据必须由可信维护者保护；拥有本机账户和 Docker 控制权的人可以改策略。本轮没有增加多用户认证或外部服务授权。
- 固定 Python 标准库环境、solve(n) 与 0～8 输入合同；不支持包安装、网络、C/C++、自选镜像/命令或任意 stdin 协议。合法范围内新自由源码可实际运行，缺少 solve 或代码异常会返回异常状态。
- 三例通过只表示有限合同匹配；当前没有真正隐藏测试。异常/超时提前停止时，其余例没有执行证据。
- 监督器独立超时已在真实任务验证；没有强制关闭 Docker Desktop/重启 Windows 的故障演练。Engine 故障时清理可能需恢复后由维护者处理，不能确认清理就不生成成功结果。

当前可以开始**本机、单人、有限范围**真人试用。服务保留在 [127.0.0.1:8006](http://127.0.0.1:8006/)，自动化验收浏览器已关闭；未启动 P2/F06、扩充题库或大规模模型测试。
