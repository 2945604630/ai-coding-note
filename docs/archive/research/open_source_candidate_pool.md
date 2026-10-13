> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# 开源项目候选池：14 项检索与筛选

核验日期：2026-10-08（Asia/Shanghai）。只读检索与静态检查；未 Fork、安装上游依赖或运行上游脚本。Star 和发布信息会变化，以下为本次实际取得的 GitHub API 快照，不按 Star 排序。

## 1. 比赛依据与检索方法

工作目录和已检查父级未发现《AIC_AI开源比赛指导文档_2026 (1).md》，因此采用用户提供的比赛原则，并核对 [2026 AIC 官方赛题通知](https://www.aicomp.cn/tracks/tracks-5/4924.html)及其两份附件。六项权重与用户提示一致：场景 15、创新 20、AI 与开源 20、完成度与效果 25、开放成果 15、表达 5。选型评分另见 project_comparison.md，不是官方预测得分。

**时限影响：官网初赛提交截止为 2026-10-15 20:00。2～4 周计划不能默认用于本届初赛；复赛评审不是承诺提供额外开发期。** 申报作品需要在截止前有可核验成果。

检索覆盖 AI 编程导师、错题与学习追踪、浏览器执行、服务端 OJ、复习调度、概念练习、知识追踪和 Agent 教学。通过 GitHub／官网搜索发现候选，随后实际取得元数据、默认分支最新提交、Release 列表、目录树、LICENSE、依赖清单及代表源码。没有只读 README 决定入选。

标记含义：**源码已验证**指取得并读过对应代码，不代表运行成功；**文档声称**指尚未独立验证；**判断／待验证**指调研结论或假设。Iris 的历史 Pyris 与当前 EduTelligence 合并；Judge0／Piston 为执行器替代选项；CodeHelper／CF Compass 为桌面替代选项，避免同类产品堆叠。

## 2. 动态信息快照

提交和发布时刻按 API 的 UTC 原值记录。最近提交取默认分支 commits[0]，不是 updated_at 或 pushed_at；无 Release 表示已成功取得空列表，不表示仓库无版本或不可用。下表发布优先列已核验 stable latest，未另查 stable 的列最近一条发布记录。

| 项目 | Star | 默认分支最新提交（UTC） | Release（UTC） | 根许可／API 标识 | 初筛角色 |
|---|---:|---|---|---|---|
| [CodeHelper Studio](https://github.com/SuLiverse/CodeHelper-Studio) | 0 | 2026-08-01T20:58:08Z | v2.4.2；2026-08-01T20:39:37Z | MIT | 重点深挖；桌面 Fork 候选 |
| [SmartCode](https://github.com/mohddarwix/SmartCode) | 0 | 2026-06-08T10:32:54Z | 无 GitHub Release | MIT | 小型 Python 教学应用；低 Star 高匹配样本 |
| [OpenTutor（zijinz456）](https://github.com/zijinz456/OpenTutor) | 133 | 2026-10-06T23:12:24Z | 无 GitHub Release | MIT | 综合学习平台；学习机制参考 |
| [EduTelligence／Iris](https://github.com/ls1intum/edutelligence) | 17 | 2026-10-07T19:46:42Z | v3.1；2026-10-05T07:33:59Z | MIT | 独特教学与提示机制；不把历史 Pyris 重复计数 |
| [Pyodide](https://github.com/pyodide/pyodide) | 14880 | 2026-09-22T03:43:22Z | 314.0.7；2026-09-14T05:06:54Z | MPL-2.0 | 可独立复用的浏览器 Python 运行时 |
| [ts-fsrs](https://github.com/open-spaced-repetition/ts-fsrs) | 809 | 2026-09-02T02:18:51Z | v5.4.2；2026-09-01T02:23:29Z | MIT | 可独立复用的复习调度器 |
| [Exercism Python Track](https://github.com/exercism/python) | 2511 | 2026-09-30T20:13:24Z | 无 GitHub Release | MIT | 概念练习、测试与评测材料 |
| [CF Compass](https://github.com/Binah-Dev/cf-compass) | 120 | 2026-10-04T01:55:39Z | v4.3.4；2026-10-04T02:14:35Z | MIT | 近期维护的 Windows 桌面训练／复盘参考 |
| [Piston](https://github.com/engineer-man/piston) | 2827 | 2026-07-31T15:06:41Z | pkgs；2021-03-15T06:11:36Z | MIT | 多语言执行 API；与 Judge0 合并为执行器选项 |
| [Judge0](https://github.com/judge0/judge0) | 4461 | 2026-09-30T13:02:29Z | v1.13.1；2024-04-18T00:13:27Z | GPL-3.0 | 服务端多语言评测引擎；执行器对照 |
| [QDU OnlineJudge](https://github.com/QingdaoU/OnlineJudge) | 6548 | 2024-10-23T03:05:08Z | v1.6.1+api.1.6.1；2024-04-07T13:23:14Z | MIT | 传统 OJ 平台；判题与错题机制对照 |
| [pyKT Toolkit](https://github.com/pykt-team/pykt-toolkit) | 442 | 2026-09-22T06:03:56Z | v1.0.0；2023-02-10T08:06:51Z | MIT | 知识追踪研究与离线基线 |
| [TuTor](https://github.com/kevinnio/tutor) | 6 | 2026-09-22T06:23:34Z | 无 GitHub Release | MIT | 轻量 Agent 教学 Skill；低 Star 机制样本 |
| [Dify](https://github.com/langgenius/dify) | 158069 | 2026-10-08T07:09:40Z | 1.17.1；2026-09-10T10:04:06Z | NOASSERTION | 可见源码工作流平台；许可条件筛选样本 |

Pyodide 的最近列表条目是 0.27.8（2026-09-16），stable latest 为 314.0.7（2026-09-14）；不同版本线不能简单按数字或列表位置判断当前稳定版。Judge0 的列表首条是 v1.13.1-extra，stable latest 是 v1.13.1。Piston 的 pkgs 是包资产发布。所有仓库 API 均返回未 archived，但这不保证积极维护。

MIT 的共通义务：复制或分发适用代码时保留版权与许可文本；依赖、数据、题面、素材与模型条款仍需分别检查。MPL-2.0 为文件层级义务；GPL-3.0 分发衍生部分需符合相应源码和许可要求；Dify 按实际附加条款处理，不等同标准 Apache-2.0。更细的组合边界见 reuse_strategy.md。

## 3. 逐项调查

### 1. CodeHelper Studio

- **定位与架构：** Electron＋React／TypeScript＋Zustand；主进程 IPC；better-sqlite3；OpenAI 兼容接口和本地 Provider 配置。
- **核心能力：** 源码已验证：CodeMirror、逐用例执行、失败自动收集、SM-2、自评、AI 复盘、FTS5／n-gram 检索、审批和审计。
- **复用价值：** 桌面 shell、编辑器、提交／错题服务、数据库保护、AI 请求生命周期；runner 需连同监督与平台代码评估。
- **改造难度：** 中高。应用完整，但草稿、工作区、课程、IPC 和状态有耦合；隐藏功能比彻底拆除便宜。
- **主要风险：** 原生 SQLite ABI、工具链与打包尚未本机复现；题面来源需逐项核验；最新提交约两个月前。
- **参赛潜力：** 适合补充真实失败证据和独立迁移验收。已有错题、AI 分析、SM-2、RAG、Agent 均不能再当原创。
- **筛选结果：** 进入六项比较；是否 Fork 以目标 Windows 基线验证为条件。

实际检查证据：[package.json](https://github.com/SuLiverse/CodeHelper-Studio/blob/23773e843d2a7bc3b04eedff59055b6c3a7afe7b/package.json)；[electron/ipc/problems.ts](https://github.com/SuLiverse/CodeHelper-Studio/blob/23773e843d2a7bc3b04eedff59055b6c3a7afe7b/electron/ipc/problems.ts)；[electron/ipc/review.ts](https://github.com/SuLiverse/CodeHelper-Studio/blob/23773e843d2a7bc3b04eedff59055b6c3a7afe7b/electron/ipc/review.ts)；[src/views/ReviewView.tsx](https://github.com/SuLiverse/CodeHelper-Studio/blob/23773e843d2a7bc3b04eedff59055b6c3a7afe7b/src/views/ReviewView.tsx)；[LICENSE](https://github.com/SuLiverse/CodeHelper-Studio/blob/23773e843d2a7bc3b04eedff59055b6c3a7afe7b/LICENSE)。

### 2. SmartCode

- **定位与架构：** React／JS＋Vite＋Monaco；FastAPI＋SQLAlchemy＋MySQL；google-genai 接入。
- **核心能力：** 源码已验证：诊断题评分、三级提示、技能历史、弱技能选题、Python 用例运行、模型评价与实际结果覆盖。
- **复用价值：** submission_evaluator 的“运行结果覆盖模型判决”设计、诊断 JSON、hint_level、推荐降级；不是完整安全 sandbox。
- **改造难度：** 中。代码树仅 99 个文件，比通用平台小；本地 MySQL、认证和预定义题目执行配置增加成本。
- **主要风险：** 0 Star、无 Release、只看到一个冒烟测试文件；无 sandbox 配置的题可回退 LLM-only；subprocess 源码明确并非安全隔离。
- **参赛潜力：** 可做专项 Python 原型；但技能分数被 floor 为不下降，不能把评分曲线直接当真实掌握程度。
- **筛选结果：** 进入六项比较；推荐参考评测边界，整仓 Fork 为次选。

实际检查证据：[package.json](https://github.com/mohddarwix/SmartCode/blob/8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d/package.json)；[backend/requirements.txt](https://github.com/mohddarwix/SmartCode/blob/8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d/backend/requirements.txt)；[backend/app/llm/submission_evaluator.py](https://github.com/mohddarwix/SmartCode/blob/8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d/backend/app/llm/submission_evaluator.py)；[backend/app/routers/submissions.py](https://github.com/mohddarwix/SmartCode/blob/8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d/backend/app/routers/submissions.py)；[backend/app/sandbox/python_runner.py](https://github.com/mohddarwix/SmartCode/blob/8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d/backend/app/sandbox/python_runner.py)；[LICENSE](https://github.com/mohddarwix/SmartCode/blob/8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d/LICENSE)。

### 3. OpenTutor（zijinz456）

- **定位与架构：** Next.js／React／TypeScript；FastAPI、异步 SQLAlchemy、SQLite 本地模式；Compose 含 Redis；Ollama 与多 Provider 适配。
- **核心能力：** 源码已验证：错题 retry／derive、结构化错因分类、BKT、苏格拉底状态机、FSRS 类调度、跨课程迁移机会启发式。
- **复用价值：** BKT 纯函数、教学状态机、诊断／派生题协议和错题 API 的设计；运行与真实教学效果需另验。
- **改造难度：** 高（整仓），中（抽模块）。前后端、Agent、资料解析、认证和多类学习数据相连。
- **主要风险：** README 将 Windows 标为 community-supported；进程 runner 使用 resource 和 signal.alarm，不能直接当 Windows 原生方案；编程测验评分模块纯 LLM，不执行代码。
- **参赛潜力：** 适合设计 AI 教学反馈；已有结构化诊断、同概念派生题与掌握估计，因此本作品应增加可执行验证而非复制名词。
- **筛选结果：** 进入六项比较；优先抽取／参考，不推荐一周内改完整平台。

实际检查证据：[apps/api/pyproject.toml](https://github.com/zijinz456/OpenTutor/blob/5fea390a49be81827342caa19846fecbcf147e4a/apps/api/pyproject.toml)；[apps/api/database.py](https://github.com/zijinz456/OpenTutor/blob/5fea390a49be81827342caa19846fecbcf147e4a/apps/api/database.py)；[apps/api/services/learning_science/knowledge_tracer.py](https://github.com/zijinz456/OpenTutor/blob/5fea390a49be81827342caa19846fecbcf147e4a/apps/api/services/learning_science/knowledge_tracer.py)；[apps/api/services/diagnosis/classifier.py](https://github.com/zijinz456/OpenTutor/blob/5fea390a49be81827342caa19846fecbcf147e4a/apps/api/services/diagnosis/classifier.py)；[apps/api/services/diagnosis/derive.py](https://github.com/zijinz456/OpenTutor/blob/5fea390a49be81827342caa19846fecbcf147e4a/apps/api/services/diagnosis/derive.py)；[apps/api/services/diagnosis/coding_grader.py](https://github.com/zijinz456/OpenTutor/blob/5fea390a49be81827342caa19846fecbcf147e4a/apps/api/services/diagnosis/coding_grader.py)；[LICENSE](https://github.com/zijinz456/OpenTutor/blob/5fea390a49be81827342caa19846fecbcf147e4a/LICENSE)。

### 4. EduTelligence／Iris

- **定位与架构：** 单仓包含 Iris、Athena、Atlas、Logos 等服务；重点读取 Iris：Python >=3.13、FastAPI、LangChain、Weaviate 与模型配置。前端和学生流程主要依赖 Artemis 等宿主。
- **核心能力：** 源码已验证：代码／测试反馈上下文、限制泄露答案的提示阶梯、回答审查模板、学习受阻干预及置信度处理。
- **复用价值：** 提示合约、测试反馈 DTO、non-spoiler 检查和不确定回答处理；Iris 的模型 token confidence 不是学习者 mastery。
- **改造难度：** 高（完整部署），中（参考协议）。宿主 API、回调、向量服务和依赖链不适合初学者短期整合。
- **主要风险：** 部分 README 保留 Pyris 旧称；要固定当前 Iris 路径和依赖，不照搬旧 Python 3.12 安装说明。提示约束本身不能保证不泄题。
- **参赛潜力：** 适合“会提示但不代写”的专项辅导。原项目已提供提示阶梯，不得将三级提示直接写成自主创新。
- **筛选结果：** 进入六项比较；机制参考价值高，部署推荐度低。

实际检查证据：[iris/pyproject.toml](https://github.com/ls1intum/edutelligence/blob/4065add4b76b2edd283f35e31d5ac620f477077e/iris/pyproject.toml)；[iris/src/iris/pipeline/chat/code_feedback_pipeline.py](https://github.com/ls1intum/edutelligence/blob/4065add4b76b2edd283f35e31d5ac620f477077e/iris/src/iris/pipeline/chat/code_feedback_pipeline.py)；[iris/src/iris/pipeline/prompts/templates/struggle_hint_contract.j2](https://github.com/ls1intum/edutelligence/blob/4065add4b76b2edd283f35e31d5ac620f477077e/iris/src/iris/pipeline/prompts/templates/struggle_hint_contract.j2)；[iris/src/iris/pipeline/shared/confidence_scoring.py](https://github.com/ls1intum/edutelligence/blob/4065add4b76b2edd283f35e31d5ac620f477077e/iris/src/iris/pipeline/shared/confidence_scoring.py)；[LICENSE](https://github.com/ls1intum/edutelligence/blob/4065add4b76b2edd283f35e31d5ac620f477077e/LICENSE)。

### 5. Pyodide

- **定位与架构：** CPython＋WebAssembly／Emscripten；JavaScript／TypeScript API。无产品前端、数据库或内置 AI。
- **核心能力：** 源码已验证：runPythonAsync、标准流 API、JS/Python 交互、Worker 示例及 Worker 测试。
- **复用价值：** 使用官方发布运行时，通过 Web Worker 执行小型 Python 题；不需要 Fork 或从源码编译 CPython。
- **改造难度：** 低中（消费包）；高（自行构建）。需自己实现判题协议、取消／超时、stdout 捕获和状态重置。
- **主要风险：** 首次加载、缓存、stdin 与包兼容待测；Worker 是执行线程，不是完整敌对代码隔离。js 桥接与网络不能无条件开放。
- **参赛潜力：** 省掉服务端执行器，适合 Windows 浏览器小 Demo。它不会自动诊断或给学习建议，AI 核心仍须自主设计。
- **筛选结果：** 进入六项比较；优先模块。稳定 Release 为 314.0.7；最新列表记录 0.27.8 是另一版本线，不能混搭示例与包。

实际检查证据：[src/js/api.ts](https://github.com/pyodide/pyodide/blob/e4d3ae954d01d61a3e90531d63b881f2d33361b4/src/js/api.ts)；[src/js/pyodide.ts](https://github.com/pyodide/pyodide/blob/e4d3ae954d01d61a3e90531d63b881f2d33361b4/src/js/pyodide.ts)；[docs/usage/webworker.md](https://github.com/pyodide/pyodide/blob/e4d3ae954d01d61a3e90531d63b881f2d33361b4/docs/usage/webworker.md)；[src/tests/test_webworker.py](https://github.com/pyodide/pyodide/blob/e4d3ae954d01d61a3e90531d63b881f2d33361b4/src/tests/test_webworker.py)；[LICENSE](https://github.com/pyodide/pyodide/blob/e4d3ae954d01d61a3e90531d63b881f2d33361b4/LICENSE)。

### 6. ts-fsrs

- **定位与架构：** TypeScript toolkit；scheduler 与可选 optimizer 分包；Node >=20；不依赖应用数据库或 LLM。
- **核心能力：** 源码已验证：Card／ReviewLog、repeat／next、rollback、重排程；有算法、边界与版本测试。
- **复用价值：** 复习状态转移、排程和日志类型；首版只用 scheduler，无需加载训练 binding。
- **改造难度：** 低。接口较独立；自己的数据库仍须正确保存日期、rating 和审计日志。
- **主要风险：** 算法预测针对回忆事件，不能自然推成编程能力；自评质量和冷启动影响大；旧 SM-2 历史不能无损转成完整 FSRS 状态。
- **参赛潜力：** 很适合辅助调度，但替换 SM-2 或调用 FSRS 本身不是创新；需独立新题结果或提示依赖度观测。
- **筛选结果：** 进入六项比较；优先模块，训练和优化延后。

实际检查证据：[packages/fsrs/package.json](https://github.com/open-spaced-repetition/ts-fsrs/blob/c8ca282edc3fe1cdfa1c24912437938b63a25cb3/packages/fsrs/package.json)；[packages/fsrs/src/fsrs.ts](https://github.com/open-spaced-repetition/ts-fsrs/blob/c8ca282edc3fe1cdfa1c24912437938b63a25cb3/packages/fsrs/src/fsrs.ts)；[packages/fsrs/src/models.ts](https://github.com/open-spaced-repetition/ts-fsrs/blob/c8ca282edc3fe1cdfa1c24912437938b63a25cb3/packages/fsrs/src/models.ts)；[packages/fsrs/__tests__/FSRS-6.test.ts](https://github.com/open-spaced-repetition/ts-fsrs/blob/c8ca282edc3fe1cdfa1c24912437938b63a25cb3/packages/fsrs/__tests__/FSRS-6.test.ts)；[LICENSE](https://github.com/open-spaced-repetition/ts-fsrs/blob/c8ca282edc3fe1cdfa1c24912437938b63a25cb3/LICENSE)。

### 7. Exercism Python Track

- **定位与架构：** Python 练习文件、概念文档、config.json、pytest／unittest 测试；不是 Exercism 全站源码，无独立前后端或 AI。
- **核心能力：** 源码已验证：概念练习的 solution／test／exemplar 映射、条件判断边界测试、二分查找测试。
- **复用价值：** 少量许可清楚的概念练习、测试组织与边界案例；题意、协议和运行时仍需适配。
- **改造难度：** 低中。迁移小题和测试容易，完整学习平台需自行做。
- **主要风险：** 函数式测试不能原样塞进 stdin/stdout OJ；框架依赖、测试可见性、练习来源与保留署名需处理。仓库没有 Release 不代表缺少可用题。
- **参赛潜力：** 开放概念案例集、迁移题和可复现评测很有价值。不能把原练习或测试列为自主题目。
- **筛选结果：** 保留为内容与测试模块；不作为完整平台 Fork。

实际检查证据：[config.json](https://github.com/exercism/python/blob/6105f6d9d3ef66ce3d5c8f529d2882af3d76b706/config.json)；[exercises/concept/meltdown-mitigation/.meta/config.json](https://github.com/exercism/python/blob/6105f6d9d3ef66ce3d5c8f529d2882af3d76b706/exercises/concept/meltdown-mitigation/.meta/config.json)；[exercises/concept/meltdown-mitigation/conditionals_test.py](https://github.com/exercism/python/blob/6105f6d9d3ef66ce3d5c8f529d2882af3d76b706/exercises/concept/meltdown-mitigation/conditionals_test.py)；[exercises/practice/binary-search/binary_search_test.py](https://github.com/exercism/python/blob/6105f6d9d3ef66ce3d5c8f529d2882af3d76b706/exercises/practice/binary-search/binary_search_test.py)；[LICENSE](https://github.com/exercism/python/blob/6105f6d9d3ef66ce3d5c8f529d2882af3d76b706/LICENSE)。

### 8. CF Compass

- **定位与架构：** Electron＋React／JavaScript＋Vite；本地 JSON 数据（README 描述）；Codeforces 公开 API 与按需 AI 服务。
- **核心能力：** 源码已验证：复习队列处理、ContestAiReview 组件、sourceTimeline／sourceDiffs 的证据持久化清洗；文档另声称个性化训练和完整源码增强复盘。
- **复用价值：** 提交时间线、相邻版本差异和复盘证据展示；纯源码复盘可参考，不迁移整套 CF 网络集成。
- **改造难度：** 中高。若继续服务 CF 用户适合 Fork；转成基础 Python 学习会面对平台、账号、数据和竞技评分耦合。
- **主要风险：** Codeforces API 可用性、受保护源码访问与授权；“有时间线／diff”不等于已核验根因；第三方素材不全受根 MIT 覆盖。
- **参赛潜力：** 对竞技编程复盘方向有潜力，原项目已经做证据化 AI 复盘，不能把“有 diff 的报告”包装成新机制。
- **筛选结果：** 保留为备选 Fork；与 CodeHelper 同属桌面类型，未重复占六项深比较名额。

实际检查证据：[package.json](https://github.com/Binah-Dev/cf-compass/blob/d94717313d2afd332712c7b1b4ad34d8b9a8ac2b/package.json)；[src/lib/review.js](https://github.com/Binah-Dev/cf-compass/blob/d94717313d2afd332712c7b1b4ad34d8b9a8ac2b/src/lib/review.js)；[src/components/ContestAiReview.jsx](https://github.com/Binah-Dev/cf-compass/blob/d94717313d2afd332712c7b1b4ad34d8b9a8ac2b/src/components/ContestAiReview.jsx)；[electron/services/ai-review-storage.cjs](https://github.com/Binah-Dev/cf-compass/blob/d94717313d2afd332712c7b1b4ad34d8b9a8ac2b/electron/services/ai-review-storage.cjs)；[CREDITS.md](https://github.com/Binah-Dev/cf-compass/blob/d94717313d2afd332712c7b1b4ad34d8b9a8ac2b/CREDITS.md)；[LICENSE](https://github.com/Binah-Dev/cf-compass/blob/d94717313d2afd332712c7b1b4ad34d8b9a8ac2b/LICENSE)。

### 9. Piston

- **定位与架构：** Node.js API、isolate、Linux 容器和语言包；不自带学习前端、错题数据库或 AI。
- **核心能力：** 源码已验证：Job 执行、isolate box、编译／执行资源限制；Compose 使用 privileged。
- **复用价值：** HTTP 执行协议与 stdout／stderr／退出码；首版多语言必要时考虑独立服务。
- **改造难度：** 高（Windows 本机整合）；中（已有 Linux 执行服务）。需要 Docker／WSL2、运行包与安全维护。
- **主要风险：** 不能 Windows 原生直接运行；公众 API 访问政策和额度未核验，不作为免费必需依赖；pkgs Release 是语言包发布，不是 API 应用稳定版。
- **参赛潜力：** 能支撑核心判题，但本身不形成教育创新。Python-only 首版已有更小的 Pyodide 路线。
- **筛选结果：** 暂缓整合；保留执行 API 设计参考。

实际检查证据：[api/package.json](https://github.com/engineer-man/piston/blob/de2b365ac759670a3a0d13ea208a0869a92c7e64/api/package.json)；[api/src/job.js](https://github.com/engineer-man/piston/blob/de2b365ac759670a3a0d13ea208a0869a92c7e64/api/src/job.js)；[docker-compose.yaml](https://github.com/engineer-man/piston/blob/de2b365ac759670a3a0d13ea208a0869a92c7e64/docker-compose.yaml)；[license](https://github.com/engineer-man/piston/blob/de2b365ac759670a3a0d13ea208a0869a92c7e64/license)。

### 10. Judge0

- **定位与架构：** Ruby／Rails API、PostgreSQL、Redis、isolate／Linux；Compose server、worker、db、redis；无内置 LLM。
- **核心能力：** 源码已验证：isolate job 与配置；仓库文档声称多语言、批量提交和丰富资源控制。
- **复用价值：** 提交状态和资源控制协议；与专项应用通过服务接口交互，不优先复制实现。
- **改造难度：** 高。服务栈、镜像、Linux 沙箱及运维超出个人小 Demo 所需。
- **主要风险：** GPL-3.0；分发修改／衍生部分需符合源码和许可义务；Compose 有 privileged，稳定 Release 仍为 2024 年版本；本轮未运行或做漏洞审计。
- **参赛潜力：** 适合既有 Linux 环境和多语言场景；对一周 Windows 参赛作品不优先。
- **筛选结果：** 暂缓；与 Piston 不重复堆叠部署。

实际检查证据：[Gemfile](https://github.com/judge0/judge0/blob/491be91bdd2c5c699d47adc3c9e48019d3074229/Gemfile)；[app/jobs/isolate_job.rb](https://github.com/judge0/judge0/blob/491be91bdd2c5c699d47adc3c9e48019d3074229/app/jobs/isolate_job.rb)；[docker-compose.yml](https://github.com/judge0/judge0/blob/491be91bdd2c5c699d47adc3c9e48019d3074229/docker-compose.yml)；[LICENSE](https://github.com/judge0/judge0/blob/491be91bdd2c5c699d47adc3c9e48019d3074229/LICENSE)。

### 11. QDU OnlineJudge

- **定位与架构：** 本仓为 Django／DRF 后端、PostgreSQL 依赖、Redis／任务队列及独立 JudgeServer；Vue 前端是 README 指向的另仓，未核验其源码。
- **核心能力：** 源码已验证：judge dispatcher、submission models；文档声称竞赛、题库、排名、权限与多语言支持。
- **复用价值：** 题目／提交／判题服务的职责边界；不将整个传统 OJ 当成智能学习机制。
- **改造难度：** 高。多个仓库、后台权限、比赛和部署依赖不利于精简。
- **主要风险：** 默认分支最近提交为 2024-10-23；requirements 仍为 Django 3.2.25 等旧依赖；配套 JudgeServer 许可证和当前运行条件未检查。
- **参赛潜力：** 需要班级赛事管理才有明显价值；当前个人专项应用不优先。
- **筛选结果：** 淘汰出重点底座；保留架构对照。

实际检查证据：[deploy/requirements.txt](https://github.com/QingdaoU/OnlineJudge/blob/df873278ab1b29510aa3a0979677d7aa9a53ca0e/deploy/requirements.txt)；[judge/dispatcher.py](https://github.com/QingdaoU/OnlineJudge/blob/df873278ab1b29510aa3a0979677d7aa9a53ca0e/judge/dispatcher.py)；[submission/models.py](https://github.com/QingdaoU/OnlineJudge/blob/df873278ab1b29510aa3a0979677d7aa9a53ca0e/submission/models.py)；[LICENSE](https://github.com/QingdaoU/OnlineJudge/blob/df873278ab1b29510aa3a0979677d7aa9a53ca0e/LICENSE)。

### 12. pyKT Toolkit

- **定位与架构：** Python／PyTorch、numpy、pandas、scikit-learn、wandb；无产品前端、应用数据库或 LLM Provider。
- **核心能力：** 源码已验证：DKT 的 embedding／LSTM／概率输出，以及 evaluate_model 中预测和 AUC 计算；其他模型仅按仓库目录与文档确认存在。
- **复用价值：** 时间序列切分、预测评测和数据格式设计；不在首版训练深度知识追踪模型。
- **改造难度：** 高（训练并落地）；低中（参考评测）。需足够带概念标签的交互记录，数据迁移难于模型调用。
- **主要风险：** 少量个人记录不足以校准；教学域与已有数据集不同；代码 MIT 不代表数据集许可统一；AUC 预测好不等于干预能提升学习。
- **参赛潜力：** 后期用于严谨验证，当前可用透明规则／小型 BKT 作为对照，避免训练负担。
- **筛选结果：** 后期研究候选；当前不选为运行底座。

实际检查证据：[setup.py](https://github.com/pykt-team/pykt-toolkit/blob/77c3e90fdb807542194b989656ccac10e5d92e12/setup.py)；[pykt/models/dkt.py](https://github.com/pykt-team/pykt-toolkit/blob/77c3e90fdb807542194b989656ccac10e5d92e12/pykt/models/dkt.py)；[pykt/models/evaluate_model.py](https://github.com/pykt-team/pykt-toolkit/blob/77c3e90fdb807542194b989656ccac10e5d92e12/pykt/models/evaluate_model.py)；[LICENSE](https://github.com/pykt-team/pykt-toolkit/blob/77c3e90fdb807542194b989656ccac10e5d92e12/LICENSE)。

### 13. TuTor

- **定位与架构：** 主要是 SKILL.md、Agent 适配和示例说明；没有应用前后端、数据库、执行引擎或模型服务。
- **核心能力：** 文件已验证：一步一操作、读操作确认进展、禁止代写、保留会话检查单等教学规则。它是提示约束，未取得强制执行实现或效果实验。
- **复用价值：** “学生亲自做一步，工具只验证一步”的学习机制和提示组织；如复制文本应保留许可。
- **改造难度：** 低（参考提示）；中（做真正可验证的产品）。不能安装一个 Skill 就视为自主参赛成果。
- **主要风险：** 规则依赖 Agent 遵循，无法保证不越界或不泄题；本轮将其作为研究对象读取，未安装或激活其指令。
- **参赛潜力：** 适合 AI 使用后独立掌握检查、按步骤留证；创新必须在客观验收和行为记录上。
- **筛选结果：** 机制参考；与 Iris 合并考虑，不重复建设通用聊天平台。

实际检查证据：[SKILL.md](https://github.com/kevinnio/tutor/blob/f0ad1ee514a034b720a4af4a36b5767f473a5994/SKILL.md)；[LICENSE](https://github.com/kevinnio/tutor/blob/f0ad1ee514a034b720a4af4a36b5767f473a5994/LICENSE)。

### 14. Dify

- **定位与架构：** Next.js／React 前端、Python API 与 workflow_entry；PostgreSQL／Redis 及可选向量、sandbox 等 Compose 服务；多模型工作流。
- **核心能力：** 源码已验证：工作流入口和运行配置结构；文档声称可视化编排、RAG、工具、Agent。未核验各节点完整行为。
- **复用价值：** 已有自托管环境可快速编排诊断原型；优先导出自己的协议、prompt 和测试样本，不迁移整个平台。
- **改造难度：** 高（整仓），中（已有服务上的原型）。服务多，依赖和后台复杂。
- **主要风险：** API SPDX 为 NOASSERTION；LICENSE 是附加条件的 Apache 2.0 改版，限制多租户及前端 LOGO／版权修改，不能标成标准 Apache-2.0 或 MIT。
- **参赛潜力：** 能验证 API 工作流，通常不足以单独形成创新。根许可和代码边界不利于自由改名分发专项底座。
- **筛选结果：** 排除直接 Fork 推荐；只在已有合规部署时作为短期原型备选。

实际检查证据：[LICENSE](https://github.com/langgenius/dify/blob/c21f5ce070652932b158afd934abbb181ef3040e/LICENSE)；[web/package.json](https://github.com/langgenius/dify/blob/c21f5ce070652932b158afd934abbb181ef3040e/web/package.json)；[api/pyproject.toml](https://github.com/langgenius/dify/blob/c21f5ce070652932b158afd934abbb181ef3040e/api/pyproject.toml)；[api/core/workflow/workflow_entry.py](https://github.com/langgenius/dify/blob/c21f5ce070652932b158afd934abbb181ef3040e/api/core/workflow/workflow_entry.py)；[docker/docker-compose.yaml](https://github.com/langgenius/dify/blob/c21f5ce070652932b158afd934abbb181ef3040e/docker/docker-compose.yaml)。

## 4. 明确取舍

| 优先级 | 项目／组合 | 理由 |
|---|---|---|
| 条件性 Fork／原型 | CodeHelper | Windows 桌面和学习闭环已齐；先证实运行，再围绕一个缺口改造 |
| 轻模块优先 | Pyodide、ts-fsrs、少量 Exercism Python | 执行、排程和授权题集可分别消费，减少整个平台维护 |
| 机制深入参考 | SmartCode、OpenTutor、EduTelligence／Iris | 有实际教学设计源码，也揭示诊断、评分与执行的边界 |
| 场景备选 | CF Compass | 若目标转为 Codeforces 赛后复盘再提高优先级 |
| 后期／特定条件 | Piston、Judge0、pyKT | 多语言 Linux 服务或训练数据需求明确后再引入 |
| 当前不选底座 | QDU OJ、Dify、TuTor 单独成品 | 分别存在维护／部署规模、附加许可、仅提示规则等不匹配 |

低 Star 保留理由：CodeHelper 的目标场景与 Windows 架构高度匹配；SmartCode 有真实判题覆盖模型评价的可读实现；Iris 的提示合约可复用；TuTor 提供轻量操作验证机制。它们的低 Star 和运行证据不足同时计入风险，没有用低 Star 推断优秀，也未用高 Star 推断适配。

## 5. 快照与复查入口

元数据端点为 https://api.github.com/repos/{owner}/{repo}，最新提交使用 /commits?per_page=1，发布列表使用 /releases?per_page=1。Pyodide、Judge0 另核验 /releases/latest。以下固定提交对应本轮读取的原始文件：

- [SuLiverse/CodeHelper-Studio @ 23773e8](https://github.com/SuLiverse/CodeHelper-Studio/commit/23773e843d2a7bc3b04eedff59055b6c3a7afe7b)；完整 SHA：23773e843d2a7bc3b04eedff59055b6c3a7afe7b。
- [mohddarwix/SmartCode @ 8b7a3e5](https://github.com/mohddarwix/SmartCode/commit/8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d)；完整 SHA：8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d。
- [zijinz456/OpenTutor @ 5fea390](https://github.com/zijinz456/OpenTutor/commit/5fea390a49be81827342caa19846fecbcf147e4a)；完整 SHA：5fea390a49be81827342caa19846fecbcf147e4a。
- [ls1intum/edutelligence @ 4065add](https://github.com/ls1intum/edutelligence/commit/4065add4b76b2edd283f35e31d5ac620f477077e)；完整 SHA：4065add4b76b2edd283f35e31d5ac620f477077e。
- [pyodide/pyodide @ e4d3ae9](https://github.com/pyodide/pyodide/commit/e4d3ae954d01d61a3e90531d63b881f2d33361b4)；完整 SHA：e4d3ae954d01d61a3e90531d63b881f2d33361b4。
- [open-spaced-repetition/ts-fsrs @ c8ca282](https://github.com/open-spaced-repetition/ts-fsrs/commit/c8ca282edc3fe1cdfa1c24912437938b63a25cb3)；完整 SHA：c8ca282edc3fe1cdfa1c24912437938b63a25cb3。
- [exercism/python @ 6105f6d](https://github.com/exercism/python/commit/6105f6d9d3ef66ce3d5c8f529d2882af3d76b706)；完整 SHA：6105f6d9d3ef66ce3d5c8f529d2882af3d76b706。
- [Binah-Dev/cf-compass @ d947173](https://github.com/Binah-Dev/cf-compass/commit/d94717313d2afd332712c7b1b4ad34d8b9a8ac2b)；完整 SHA：d94717313d2afd332712c7b1b4ad34d8b9a8ac2b。
- [engineer-man/piston @ de2b365](https://github.com/engineer-man/piston/commit/de2b365ac759670a3a0d13ea208a0869a92c7e64)；完整 SHA：de2b365ac759670a3a0d13ea208a0869a92c7e64。
- [judge0/judge0 @ 491be91](https://github.com/judge0/judge0/commit/491be91bdd2c5c699d47adc3c9e48019d3074229)；完整 SHA：491be91bdd2c5c699d47adc3c9e48019d3074229。
- [QingdaoU/OnlineJudge @ df87327](https://github.com/QingdaoU/OnlineJudge/commit/df873278ab1b29510aa3a0979677d7aa9a53ca0e)；完整 SHA：df873278ab1b29510aa3a0979677d7aa9a53ca0e。
- [pykt-team/pykt-toolkit @ 77c3e90](https://github.com/pykt-team/pykt-toolkit/commit/77c3e90fdb807542194b989656ccac10e5d92e12)；完整 SHA：77c3e90fdb807542194b989656ccac10e5d92e12。
- [kevinnio/tutor @ f0ad1ee](https://github.com/kevinnio/tutor/commit/f0ad1ee514a034b720a4af4a36b5767f473a5994)；完整 SHA：f0ad1ee514a034b720a4af4a36b5767f473a5994。
- [langgenius/dify @ c21f5ce](https://github.com/langgenius/dify/commit/c21f5ce070652932b158afd934abbb181ef3040e)；完整 SHA：c21f5ce070652932b158afd934abbb181ef3040e。

## 6. 访问限制与研究局限

Dify 全量递归树请求未成功，改为读取根目录、workflow 目录及 workflow_entry.py；旧 graph_engine 路径 404，未把失败内容作为证据。CodeHelper 的两个猜测路径也 404，之后按目录确认并读取 src/store.ts 和 resources/problems/leetcode.json。GNU 官方许可页面访问超时，GPL 结论依据实际读到的 Judge0 LICENSE；Mozilla MPL FAQ 已取得。

搜索索引与 CodeHelper API 的规范地址、Star 和旧编辑器描述不一致；采用固定提交与实际 package，不混用旧项目。README 的“测试通过”“学习有效”“本地免费”等主张没有本轮运行复现。13 个仓库取得完整非 truncated 树；Dify 为定向目录检查。已实际取得代表源文件及全部 14 个根许可；不是全仓安全审计、许可证依赖审计或教学效果实验。

本轮不计算获奖概率，不决定最终选题。下一轮优先补目标系统运行、真实用户需求、诊断标注集和作品时限；不会继续无限扩展候选池。
