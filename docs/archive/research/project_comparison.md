> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# 六个重点项目横向比较

核验日期：2026-10-08（Asia/Shanghai）。本表基于固定提交的静态检查；动态信息、完整 SHA 和首轮 14 项筛选见 [候选池](<open_source_candidate_pool.md>)，CodeHelper 细节见 [深度分析](<codehelper_deep_analysis.md>)。未运行参考项目。

## 1. 评分口径

分数表示**初级开发者＋Coding Agent、Windows、本地优先、低训练成本、小型可验证作品**条件下的技术适配性，不是 AIC 官方评分或获奖概率。

| 维度 | 1 分 | 3 分 | 5 分 |
|---|---|---|---|
| 技术适配性 | 与目标明显不符 | 有条件适配 | 直接服务核心闭环 |
| 模块可复用性 | 强耦合、难拆 | 可拆但需改边界 | 独立接口与依赖清楚 |
| 差异化空间 | 难找到实质变化 | 有改进但易同质化 | 有具体可实现的缺口与对照 |
| 开发成本 | 成本／风险很高 | 可在有限范围改造 | 很小代价即可复用；分数高代表成本低 |
| 开源合规性 | 许可不明或明显限制 | 条件较多 | 许可清楚，适用代码改编便利 |
| 可验证性 | 缺少可观测输出 | 可测试但基线或数据薄弱 | 核心输出确定，易重复与对比 |

2、4 分位于相邻条件之间。合规评分只评价已检查根许可与复用路径，不保证所有依赖、数据、素材合规。测试文件存在不等于测试通过。

## 2. 评分表与项目角色

| 项目 | 技术 | 模块 | 差异 | 成本 | 合规 | 验证 | 合计 /30 | 推荐使用方式 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| CodeHelper Studio | 4 | 4 | 4 | 3 | 5 | 4 | 24 | 条件性 Fork／快速桌面原型 |
| SmartCode | 4 | 3 | 3 | 3 | 5 | 3 | 21 | 参考评价协议；小范围 Fork 为备选 |
| OpenTutor | 4 | 4 | 3 | 2 | 5 | 4 | 22 | 参考／抽取教学机制 |
| EduTelligence／Iris | 4 | 3 | 3 | 2 | 5 | 4 | 21 | 提示合约和反馈流程参考 |
| Pyodide | 5 | 5 | 4 | 4 | 4 | 5 | 27 | 消费发布运行时，不 Fork |
| ts-fsrs | 4 | 5 | 3 | 5 | 5 | 5 | 27 | 消费 scheduler，不引入训练 binding |

**合计不能用来判断哪个项目应整仓 Fork。** Pyodide 和 ts-fsrs 是范围很小的模块，没有产品闭环；完整应用的部署、数据和界面成本自然更高。这里列合计便于审查各项取舍，而不是把模块与平台排成产品质量排行榜。

## 3. 逐项评分依据

### CodeHelper Studio：保留已有闭环，补可验证学习机制

- **技术 4：** Electron、CodeMirror、SQLite 和运行器直接对应桌面编程练习；依赖原生 ABI 和目标工具链，尚未确认本机跑通。
- **模块 4：** IPC、服务层与 db 分层清楚；runner、草稿和工作区有跨模块依赖，不能单文件复制。
- **差异 4：** 复盘入口未纳入真实失败用例；自评 repetitions 作为 mastered；跨题证据结构缺失。这些可形成明确对照。
- **成本 3：** 可新增一个诊断面板，全面删除课程、宠物和工作区却需修改状态、IPC、构建和迁移。
- **合规 5：** 根 MIT 清楚，代码修改便利；全量外部题库授权仍须另查，当前优先替换小题集。
- **验证 4：** 有 runner／判题／SM-2／IPC 测试可作为工程基础；没有本轮实测或可信学习增益数据。

最有价值的是桌面与数据生命周期，最应补的是“提交证据→诊断假设→新题验证”。[判题及收集](https://github.com/SuLiverse/CodeHelper-Studio/blob/23773e843d2a7bc3b04eedff59055b6c3a7afe7b/electron/ipc/problems.ts)、[复盘入口](https://github.com/SuLiverse/CodeHelper-Studio/blob/23773e843d2a7bc3b04eedff59055b6c3a7afe7b/src/views/ReviewView.tsx#L255-L286)、[复习统计](https://github.com/SuLiverse/CodeHelper-Studio/blob/23773e843d2a7bc3b04eedff59055b6c3a7afe7b/electron/ipc/review.ts#L198-L238)。

### SmartCode：运行事实优先，但适用范围和评分有局限

- **技术 4：** Python 初学者诊断、提示、选题很贴合；FastAPI＋MySQL 比单机 SQLite 增加环境成本。
- **模块 3：** LLM grader／hint／recommender 分文件；沙箱通过问题 slug 对应执行配置，迁移任意新题要重做适配。
- **差异 3：** 已有多级提示、技能历史和实际结果覆盖，不能重复包装；可改技能更新与未知题严格拒判。
- **成本 3：** 99 文件小应用较易读；认证、种子数据、MySQL、Gemini SDK 都需处理。
- **合规 5：** 根 MIT；算法题来源与依赖仍单独核查。
- **验证 3：** 实际 interpreter 结果覆盖 LLM case verdict 很有价值；无配置题可退化到 LLM-only，测试只看到冒烟层。

值得参考 `_overlay_sandbox` 的边界。但 `_apply_skill_updates` 将 bump 限制为不小于 0，失败不会降低技能分；这是一种积分策略，不能作为已校准知识追踪。源码头部的“LLM mentally execute”描述也不能覆盖后面的实际运行实现，两条路径要分开解释。[评价覆盖](https://github.com/mohddarwix/SmartCode/blob/8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d/backend/app/llm/submission_evaluator.py#L199-L340)、[技能更新](https://github.com/mohddarwix/SmartCode/blob/8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d/backend/app/routers/submissions.py#L280-L360)。

### OpenTutor：机制丰富，整个平台过大

- **技术 4：** 本地 SQLite、错题、诊断、BKT 和教学状态都相关；通用资料学习比编程运行更成熟。
- **模块 4：** BKT 与 SocraticEngine 相对独立；持久化接口、Agent 和课程模型仍需隔离。
- **差异 3：** 已有结构化错因、派生同概念诊断题、掌握估计，泛化“自适应错题本”空间小；可在执行验证上形成差异。
- **成本 2：** Next.js＋FastAPI、Redis、资料导入和多 Agent；Windows 是社区支持，进程执行路径有 POSIX 依赖。
- **合规 5：** 根 MIT；论文引用不能自动授权其数据、模型或素材。
- **验证 4：** 有 BKT、Socratic、性质测试与 E2E；生成诊断题正确性、掌握估计校准和学习提升仍需独立测。

`knowledge_tracer.py` 默认猜对率含四选一假设，不应原封不动套到编程题；`coding_grader.py` 明确纯 LLM、无执行；`derive.py` 验 JSON 并落表，已读路径未对派生题进行 interpreter 验收。另一个 CodeExecutionAgent 存在并不能证明测验 grader 实际使用了它。[BKT](https://github.com/zijinz456/OpenTutor/blob/5fea390a49be81827342caa19846fecbcf147e4a/apps/api/services/learning_science/knowledge_tracer.py)、[编程评分](https://github.com/zijinz456/OpenTutor/blob/5fea390a49be81827342caa19846fecbcf147e4a/apps/api/services/diagnosis/coding_grader.py)、[派生题](https://github.com/zijinz456/OpenTutor/blob/5fea390a49be81827342caa19846fecbcf147e4a/apps/api/services/diagnosis/derive.py#L100-L165)。

### EduTelligence／Iris：教学约束值得参考，宿主依赖不适合整仓搬运

- **技术 4：** 从学生代码、测试反馈和对话生成引导，与专项编程辅导高度相关。
- **模块 3：** 模板和 DTO 可参考；pipeline 依赖 Artemis 语境、模型管理、回调和检索服务。
- **差异 3：** non-spoiler 提示阶梯、受阻干预、回答审查已存在；本作品需在中文 Python 场景与可量化泄题率等方面改善。
- **成本 2：** Iris 的当前 Python >=3.13 和 FastAPI／LangChain／Weaviate 依赖多；全部微服务更重。
- **合规 5：** 已读根 MIT；只迁移选定文本／协议时仍保留必要署名。
- **验证 4：** 已有 struggle、confidence、feedback 工程测试；教学提升和提示合约实际遵守率不能由模板推定。

置信度模块处理 token logprob 或模型自报 confidence，是**回答置信度**，不是学习者掌握度；不能把两者相互替代。论文支持研究机制的价值，不证明当前仓库在本场景有效。[提示合约](https://github.com/ls1intum/edutelligence/blob/4065add4b76b2edd283f35e31d5ac620f477077e/iris/src/iris/pipeline/prompts/templates/struggle_hint_contract.j2)、[代码反馈](https://github.com/ls1intum/edutelligence/blob/4065add4b76b2edd283f35e31d5ac620f477077e/iris/src/iris/pipeline/chat/code_feedback_pipeline.py)、[Iris 原论文](https://arxiv.org/abs/2405.08008)。

### Pyodide：降低 Python Demo 的执行部署成本

- **技术 5：** Windows 浏览器即可承载核心 Python 执行，不需服务端判题或全量编译工具链。
- **模块 5：** 官方运行时及 JS API 独立，不需移植 UI／数据模型。
- **差异 4：** 自己可围绕真实测试反馈做诊断、反例缩减或学习验收；这些不是运行时直接提供的产品功能。
- **成本 4：** 消费发布包的成本低；加载、stdin、超时、内存、序列化和状态重置仍需开发，故不是 5。
- **合规 4：** MPL-2.0 清楚，可与独立 MIT 文件组合；分发运行时及修改受覆盖文件要履行源码／通知义务。
- **验证 5：** 正确程序、错误程序、死循环、输出和执行状态均可确定性比较；没有内置教学效果保证。

只用稳定运行时，首版限制为纯 Python 小题。使用 module Worker 保持 UI 可响应，但还需明确网络和 JS 桥接权限、不可将运行时与 Worker 称为完整安全沙箱。[API 源码](https://github.com/pyodide/pyodide/blob/e4d3ae954d01d61a3e90531d63b881f2d33361b4/src/js/api.ts)、[Worker 文档](https://pyodide.org/en/stable/usage/webworker.html)、[MPL FAQ](https://www.mozilla.org/en-US/MPL/2.0/FAQ/)。

### ts-fsrs：简单复用排程，创新不在更换算法

- **技术 4：** 适合安排概念／反例复习；编程任务耗时和独立作答条件不天然符合记忆卡片观测。
- **模块 5：** Card／ReviewLog、repeat／next 等接口独立，数据持久化可由自己的应用处理。
- **差异 3：** 成熟算法本身不是作品创新；应改任务选择、观测事件、提示依赖和新题验收。
- **成本 5：** 仅 scheduler 的集成很小；默认参数即可开始，不要求训练或 Rust binding。
- **合规 5：** MIT 清楚，保留版权及许可即可满足适用代码基本分发义务。
- **验证 5：** 排程、日志、回滚、日期与边界可反复测试；长期学习效果需真实观察。

最值得保留的是成熟状态转移，最不值得首轮做的是重新实现 FSRS 或训练自定义参数。[package](https://github.com/open-spaced-repetition/ts-fsrs/blob/c8ca282edc3fe1cdfa1c24912437938b63a25cb3/packages/fsrs/package.json)、[接口](https://github.com/open-spaced-repetition/ts-fsrs/blob/c8ca282edc3fe1cdfa1c24912437938b63a25cb3/packages/fsrs/src/fsrs.ts)、[日志类型](https://github.com/open-spaced-repetition/ts-fsrs/blob/c8ca282edc3fe1cdfa1c24912437938b63a25cb3/packages/fsrs/src/models.ts)。

## 4. 按使用场景推荐

| 需求 | 首选 | 备选 | 当前不优先 |
|---|---|---|---|
| Windows 桌面编程闭环已齐 | CodeHelper，先验证基线 | SmartCode 浏览器应用；CF Compass 仅竞技复盘方向 | 完整 Artemis／EduTelligence |
| Python 小题独立专项应用 | Pyodide＋自己的轻 UI 和数据 | 已有可信本机 runner | Judge0／Piston 多语言服务 |
| 辅导方式与误解诊断 | OpenTutor、SmartCode、Iris 的具体模块 | TuTor 的逐步验证规则 | 仅套一个通用聊天模板 |
| 成熟复习算法 | 首轮保留已有 SM-2；独立项目用 ts-fsrs | 参考 OpenTutor 的学习状态 | 从零实现 FSRS 或训练 pyKT |
| 有可归属开放成果 | 自拟诊断案例、可执行变式、评测工具、学习事件协议 | 核验后引用少量 Exercism 题集 | 复制整库题面再声称自研 |

推荐顺序是**先固定问题和观测，再选最小底座**。不要先组合全部六个项目。可行组合、兼容性、时限与实施顺序见 [复用路线](<reuse_strategy.md>)。

## 5. 评估局限

尚无目标 Windows 上的运行、构建、Provider 成本或用户研究结果。工时分数受项目安装质量和 Coding Agent 修改可靠性影响，若基线无法快速跑通，CodeHelper／SmartCode 成本分应下调。没有将论文、README 或测试存在当成实际学习提升，也没有给出 AIC 获奖概率。
