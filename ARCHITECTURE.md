# 当前系统架构

描述 main / cleanup 实际存在的 V2。两个 V3 分支主要改前端，方向二另有只读学习摘要，尚未合并。

```text
Browser：题目、草稿、运行结果、教学对话
   ↓ HTTP（127.0.0.1）
FastAPI app.py → Service
   ↓
Session + Version（不可变源码、version_id、SHA-256）
   ├─ SandboxService → DockerRuntime → 一次性容器
   │                                  ↓
   │                         Execution Evidence
   │                                  ↓
   └─ new_turn → Execution Context → public_input 教学快照
                                     ↓
                              AI Provider / 固定 S0
                                     ↓
                           回复守卫 + 当前版本复核
                                     ↓
                              Teaching Turn
   ↓
SQLite + 本机工件
```

| 实体 | 关系与存储 |
| --- | --- |
| session | SQLite experiments 行是学习会话，保存题目/合同/模型快照及当前代码版本 |
| student code / version | code_versions 保存源码、version_id、SHA-256 和审核状态；保存修改生成新版本，父子关联见 Demo 操作/事件 |
| sandbox job | sandbox_jobs 绑定 session/version/hash/request ID，保存 run/submit 合同、输入、逐例结果、状态、执行/清理和耗时 |
| execution context | 服务端选择当前保存版本最新任务，生成有限公开摘录；过期、未知、无证据和截断分别标记 |
| teaching turn | turns 保存学生原文、不可变 public_input、绑定版本和输出；attempts 保存尝试，重试沿用原快照 |
| provider | S1 走 CLI/API/disabled 适配；S0 是冻结规则，不是模型生成 |
| 学习与验收记录 | notes/events/feedback、demo_operations/demo_assessments 保存操作、修改、首次作答与帮助来源；资格不等于掌握 |

## 两条执行通路

旧 F03/F04/F05 通过 experiments/runner.py 和固定登记目录，仅执行审核源码与合法输入。旧执行器可以在宿主 Python 跑审核样例，调用端必须守住白名单与 hash，不能传未知学生代码。

自由代码使用 sandbox_contract → sandbox_service → sandbox_runtime。浏览器先保存，再提交版本/hash；后端读取源码、复算 hash、核对会话/合同后排入单执行队列。Docker 未通过本机验收时记录不可用，不执行、不回退。

自由合同只覆盖 DEMO C01/C03 求和：solve(n)，严格整数 0～8。run 观察自定义输入，有审核参考才显示参考；submit 比较 0、1、3 三例，stdout 额外打印也参与比较。

## 执行到 AI

Service.new_turn 保存教学快照时调用 execution_context.project，筛选当前版本最新任务。版本、SHA、合同、输入、结果、执行/清理标记须相符；最新失败/未完成不回退旧成功。同源码另存新版本也不继承旧任务。

模型只看到有限摘录，源码/stdout/stderr 视为不可信数据，截断有标记。execution_completed 表示完成，specified_tests_passed 表示指定提交测试通过；teaching_claim_verified 不据此变真。模型生成前与入库时复核版本；版本变化阻断旧建议，教学快照不事后补写。

## 入口与持久化

python -m web_lab 运行单进程 FastAPI/Uvicorn，固定监听 loopback。web_lab.launch/start_web.bat 是启动入口。数据目录有服务锁，SQLite 为 aic_web.sqlite3，运行工件、尝试、收据保存本机。不同 UI 使用独立目录。

teaching.py 直接依赖 F01/F02，Demo 依赖 F03～F05；package、静态工件和测试保留原路径，不改 import、不重新冻结。字段按需看 [DATA_FIELDS.md](web_lab/DATA_FIELDS.md)，接入细节见 [执行证据接入](docs/architecture/teaching_execution_integration.md)，沙箱范围见 [实测报告](docs/validation/sandbox_test_results.md)。
