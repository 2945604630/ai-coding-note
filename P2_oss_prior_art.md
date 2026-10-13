# P2 开源与研究先行技术调查

调查日期：2026-10-11。目标是判断候选机制的重合风险，不是寻找最多的仓库。本轮选择 **10 个主调查对象**，以源码、项目技术文档和原始论文为依据；未使用 Star 数作技术判断，未安装、运行、Fork 或修改任何外部项目。

**主要发现：**苏格拉底追问、状态式教学、执行支撑反馈、反例、三级帮助、认知参与和无 AI 同构题迁移都已有先行技术。A/B 只剩较窄的潜在增量，尚不能证明独立新颖性。候选定义和实验门槛见 [P2_innovation_candidates.md](<P2_innovation_candidates.md>)。

## 1. 检查方法与可信度

检索覆盖 AI Programming Tutor、Socratic Coding Tutor、Execution-Grounded Feedback、Adaptive Programming Education、Learning Transfer Assessment、AI Hint Generation、Educational Agent。先找作者或组织的原始链接，再检查论文机制、代码入口、实际调用或状态转换；不从名称推断能力。

维护信息来自调查时 GitHub 元数据和提交记录。下表日期均为 UTC 的提交日期；“近期提交”仅说明可见活动，不代表质量、持续支持或教育效果。未检查所有 issue、release、依赖安全和部署环境。源码判断是静态阅读，不是本轮运行验证。

代码许可证、论文许可证和数据许可证分别记录。GitHub license 字段为 null 时进一步检查文件与声明；没有明确授权的公开代码不按“可直接复用的开源软件”处理。对“未解决问题”的表述限于已检查路径和研究报告，不声称其他分支或整个领域都没有解决。

| 编号 | 系统 / 正式链接 | 授权核实 | 维护快照 | 证据层级 |
|---|---|---|---|---|
| P01 | [Gen-Ed / CodeHelp](https://github.com/liffiton/Gen-Ed) | 主体 AGPL-3.0-only；部分素材另有授权 | main 检查提交 2026-10-08；未归档 | 现行代码＋CodeHelp 原始论文 |
| P02 | [CodeAid](https://arxiv.org/html/2401.11314v2) | 论文 CC BY 4.0；官方代码授权未核实 | 2024 研究；未找到可确认归属的官方源码库，不能判断现行维护 | 论文与作者版 PDF |
| P03 | [Iris / edutelligence](https://github.com/ls1intum/edutelligence)＋[Artemis](https://github.com/ls1intum/Artemis) | 两仓库 MIT | 检查提交分别 2026-10-11、2026-10-10；均未归档 | 现行干预源码、模板、平台文档 |
| P04 | [OpenTutor](https://github.com/zijinz456/OpenTutor) | MIT | main 检查提交 2026-10-08；未归档 | 状态机、接入调用、核验与测验路径 |
| P05 | [SmartCode](https://github.com/mohddarwix/SmartCode) | MIT | main 检查提交 2026-06-08；未归档 | 提示生成、互动 tutor、实际提交评价代码 |
| P06 | [HKUDS DeepTutor](https://github.com/HKUDS/DeepTutor) | Apache-2.0 | 检查提交 2026-10-08；未归档 | mastery 提示、工具及计算代码 |
| P07 | [ITAP](https://github.com/krivers/ITAP-django) | MIT | master 检查提交 2017-06-22；未归档但长期无可见新提交 | AST 提示生成核心与作者研究资料 |
| P08 | [GPT4Hints-GPT3.5Val](https://github.com/machine-teaching-group/lak2024_GPT4Hints-GPT3.5Val) | 已查完整树未发现 LICENSE；代码授权未明确 | 检查提交 2024-03-11；未归档，研究快照 | 原始论文＋端到端、验证代码 |
| P09 | [Code engagement techniques](https://github.com/MajeedKazemi/code-engagement-techniques) | package.json 声明 MIT，但检查树无 LICENSE；论文 CC BY 4.0 | 检查提交 2025-01-31；未归档 | 论文＋Lead-and-Reveal、Trace-and-Predict 路由 |
| P10 | [ProgFeed](https://github.com/umass-ml4ed/progFeed-dataset-public) | 仓库 LICENSE 为 CC BY 4.0 | 检查提交 2026-06-07；未归档，近期研究数据发布 | 论文、数据字典、README、反馈生成器 |

P03 是一个集成生态，计作一个对象。P02 是有原始研究证据的系统，不冒称已确认可 Fork 的开源项目。P08/P09 的授权不足也不能从“公开可看”自动补全。

## 2. 十个重要对象的逐项判断

### P01. CodeHelp / Gen-Ed：不给完整解答的辅导护栏已经成熟

**来源与版本。** 当前官方仓库为 [liffiton/Gen-Ed](https://github.com/liffiton/Gen-Ed)，检查提交 `5f71dde8173500c8375c670070ca2da7184674f4`。原始研究为 [CodeHelp: Using Large Language Models with Guardrails for Scalable Support in Programming Classes](https://arxiv.org/pdf/2308.06921)。现行 Gen-Ed 包含 CodeHelp 与其他教学组件，不能把现行全部实现都归入 2023 年论文。

**授权与维护。** GitHub 自动识别字段未给出许可证，但实际 [AGPL-3.0-only 文件](https://github.com/liffiton/Gen-Ed/blob/5f71dde8173500c8375c670070ca2da7184674f4/LICENSES/AGPL-3.0-only.txt)及项目声明明确主体授权；素材有例外。main 检查提交时间 2026-10-08T04:15:30Z，仓库未归档，存在近期活动。

**实际机制。** [prompts.py](https://github.com/liffiton/Gen-Ed/blob/5f71dde8173500c8375c670070ca2da7184674f4/src/components/code_queries/prompts.py)区分信息是否充分、必要时请求补充，并约束不提供完整纠正代码；后续清理代码块。[helper.py](https://github.com/liffiton/Gen-Ed/blob/5f71dde8173500c8375c670070ca2da7184674f4/src/components/code_queries/helper.py)将这些步骤接入调用与记录，而非只写在宣传页。另检查 guided tutor 路径。论文提供课堂使用背景，不能由使用反馈直接外推独立迁移增益。

**重合与剩余问题。** 与 A/D 的“先澄清、少给答案、根据输入辅导”重合；否定单纯护栏 prompt 的创新主张。所查路径未证明基于多解释分区选探针，也没有暴露内容感知的迁移选题验证。护栏约束本身不保证学生理解或所有输出都无泄题。

**是否 Fork。** 当前不建议整库 Fork：F01/F02 已有响应生成与约束，AGPL 也须按其条件安排复用。值得借鉴的是强 prompt 基线、上下文充分性处理和日志，不作为我们的独立创新。若未来目标改为完整课堂部署，应再评估整库适配。

### P02. CodeAid：课堂交互研究强，但不能认领同名仓库

**来源。** [原始论文 v2](https://arxiv.org/html/2401.11314v2)、[作者版 PDF](https://austinhenley.com/pubs/Kazemitabaar2024CHI_CodeAid.pdf)。它是 CHI 2024 的编程课堂 AI 助手研究。检查到的是作者研究资料，没有核实官方开源实现；搜索结果中的其他 CodeAid 名称不能视为同一系统。

**授权与维护。** 论文标注 CC BY 4.0；不能将论文授权套给未确认的代码。论文版本为 2024 年，现行服务是否继续运行、代码维护者和代码许可证均未知。

**实际机制。** 按问题上下文提供概念解释、伪代码与逐行说明、对错误代码的注释式反馈，避免直接把完整最终解法交给学生。研究在一门约 700 人的课程中部署 12 周、记录逾 8,000 次使用；课程人数不能当成每人都实际使用，更不是随机化迁移试验。以上依据原始论文，不由名称猜测。

**重合与剩余问题。** 与 A/D 的概念帮助、反馈形式和答案约束重合。大规模课堂使用说明该产品形态早已存在；不证明按帮助内容选择有效独立迁移题，也不证明有限反例能定位学生认知原因。

**是否 Fork。** 官方源代码未核实，不能建议直接 Fork。值得借鉴交互任务分类、课堂误用/期望差异和真实研究方法，作为设计与评估参照。

### P03. Iris / Artemis：已有执行信息、版本意识与主动帮助门控

**来源与版本。** [edutelligence](https://github.com/ls1intum/edutelligence/tree/8204ac02776e915a24dbcff3f88ca24273db05db)，检查提交 `8204ac02776e915a24dbcff3f88ca24273db05db`；[Artemis](https://github.com/ls1intum/Artemis/tree/e92f350e7892b514b976b05c4f83cfcec12ec54c)，检查提交 `e92f350e7892b514b976b05c4f83cfcec12ec54c`。不是把平台功能与 tutor 功能混称一个算法。

**授权与维护。** 两仓库实际 LICENSE 为 MIT，分别见 [edutelligence LICENSE](https://github.com/ls1intum/edutelligence/blob/8204ac02776e915a24dbcff3f88ca24273db05db/LICENSE)、[Artemis LICENSE](https://github.com/ls1intum/Artemis/blob/e92f350e7892b514b976b05c4f83cfcec12ec54c/LICENSE)。检查提交时间分别为 2026-10-11T10:17:19Z、2026-10-10T11:11:54Z；未归档，有近期活动。这里是提交/源码快照，不是部署审计。

**实际机制。** [struggle_intervention_pipeline.py](https://github.com/ls1intum/edutelligence/blob/8204ac02776e915a24dbcff3f88ca24273db05db/iris/src/iris/pipeline/struggle_intervention_pipeline.py)接收卡住信号，利用上下文及代码、构建、测试工具，产出 silent/ambient/active 动作；无效输出有保守处理。[系统模板](https://github.com/ls1intum/edutelligence/blob/8204ac02776e915a24dbcff3f88ca24273db05db/iris/src/iris/pipeline/prompts/templates/struggle_intervention_system_prompt.j2)明确避免重复干预、区分本轮与旧回合帮助，注意当前编辑代码与已提交/旧构建信息不一致；工具缺失时不可假定已有数据。

**重合与剩余问题。** 强烈重合 D，并与 A 的“证据不一致、不要基于旧事实教学”重合。A 必须越过这层工程：展示竞争解释如何决定探针及改变教学路由。所查代码能证明该机制存在，不能单凭源码证明主动介入改善学生学习；也没有在所查路径确认暴露感知迁移测验。

**是否 Fork。** 不建议为少数机制案例引入整个 Artemis/Iris 生态。可借鉴动作门控、历史帮助去重、数据缺失处理和执行上下文 schema；现有 F03 继续负责本项目的有限事实核验。

### P04. OpenTutor：状态式苏格拉底教学与迁移追问已经直接重合

**来源与版本。** [OpenTutor](https://github.com/zijinz456/OpenTutor/tree/f0142f28e8ed1ab4047e16c9aee5c283a6ee98b7)，检查提交 `f0142f28e8ed1ab4047e16c9aee5c283a6ee98b7`。

**授权与维护。** [LICENSE](https://github.com/zijinz456/OpenTutor/blob/f0142f28e8ed1ab4047e16c9aee5c283a6ee98b7/LICENSE)为 MIT；main 检查提交 2026-10-08T23:19:26Z，未归档，有近期活动。

**实际机制。** [socratic_engine.py](https://github.com/zijinz456/OpenTutor/blob/f0142f28e8ed1ab4047e16c9aee5c283a6ee98b7/apps/api/services/agent/socratic_engine.py)实现 PROBE、CLARIFY、CONFRONT、SCAFFOLD、CONFIRM；依据 correct/partial/wrong/confused 转换，低掌握或高认知负荷进入脚手架，概念错误可进入反例，确认阶段已有迁移提问，持续脚手架后可提供示例。检查了 tutor 接入路径的状态读取、指令注入、回答分类和状态保存，不能把它说成纯 README 愿景。

同时检查 verifier 与 quiz_submission：前者主要是输出约束、话题/证据模式等启发式检查与修复，不等于执行器证实所有解释；后者包含编程评分/掌握更新路径。不要因模块叫 verifier 就推断事实正确性。

**重合与剩余问题。** A 的“识别理解状态再换教法”和 D 的“动态帮助”基本被覆盖，B 的“确认后迁移”也部分被覆盖。拟保留 A 的有限竞争解释与最小区分探针，必须实际胜过这样的成熟状态基线。所查路径未提供同等的暴露内容感知、首答独立性与题目等值验证；这是检查边界，不是全仓不存在的断言。

**是否 Fork。** 有条件值得作为状态式 tutor 对照原型或复用局部状态 schema，当前不需 Fork 全栈。若仅换一套 F02 prompt 而复制其状态表，不能算我们的创新。

### P05. SmartCode：三级提示与有条件的执行支撑评价

**来源与版本。** [SmartCode](https://github.com/mohddarwix/SmartCode/tree/8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d)，检查提交 `8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d`。

**授权与维护。** [LICENSE](https://github.com/mohddarwix/SmartCode/blob/8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d/LICENSE)为 MIT；main 检查提交 2026-06-08T10:32:54Z，未归档。存在 2026 年更新，不能据此保证持续维护。

**实际机制。** [hint_generator.py](https://github.com/mohddarwix/SmartCode/blob/8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d/backend/app/llm/hint_generator.py)按当前代码生成 level 1 引导、level 2 算法/不变量提示、level 3 片段；失败可回退通用提示。[interactive_tutor.py](https://github.com/mohddarwix/SmartCode/blob/8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d/backend/app/llm/interactive_tutor.py)逐步提问。

关键核实：[submission_evaluator.py](https://github.com/mohddarwix/SmartCode/blob/8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d/backend/app/llm/submission_evaluator.py)当前 `evaluate_submission` 实际先运行 Python subprocess 测试，再让 LLM补充评价，并以实际执行覆盖用例判定；不能只读旧的“mental execution”描述。**但仅已配置题有这种执行支撑；无配置时返回空运行结果，存在 LLM-only 回退。** AST“作弊”启发式也是独立规则，不是通用程序正确性证明。

**重合与剩余问题。** C/D 的普通实现高度重合。有限测试、模型代码质量评分和启发式不能证明学生理解、普遍正确性或无外援迁移；运行子进程也不自动构成恶意代码安全沙箱。本轮未部署或验证其运行隔离。

**是否 Fork。** MIT 的模块结构适合将来构造三级提示/执行反馈强基线；若从零做类似完整应用可考虑 Fork。当前 F 系统已具备对应基础，不建议换平台。借鉴层级定义与“执行判定优先”，同时显式排除无执行配置的结果。

### P06. HKUDS DeepTutor：掌握门控、提示使用记录与教学/测验分离

**来源与版本。** [HKUDS/DeepTutor](https://github.com/HKUDS/DeepTutor/tree/6cf793bd868ba5ecbe64722936d4be8fab5a01df)，检查提交 `6cf793bd868ba5ecbe64722936d4be8fab5a01df`；与其他年代的同名研究系统区分。

**授权与维护。** [LICENSE](https://github.com/HKUDS/DeepTutor/blob/6cf793bd868ba5ecbe64722936d4be8fab5a01df/LICENSE)为 Apache-2.0；检查提交 2026-10-08T03:34:42Z，未归档，有近期活动。

**实际机制。** [mastery_loop.yaml](https://github.com/HKUDS/DeepTutor/blob/6cf793bd868ba5ecbe64722936d4be8fab5a01df/deeptutor/capabilities/mastery/prompts/en/mastery_loop.yaml)约束学习目标和工具检查，测验提问结束当前回合，后续回合再评分，不以 tutor 印象随意开门。[mastery.py](https://github.com/HKUDS/DeepTutor/blob/6cf793bd868ba5ecbe64722936d4be8fab5a01df/deeptutor/learning/mastery.py)根据近期正确情况加权，并对少量尝试的置信程度作限制，不应称成 BKT。[tools.py](https://github.com/HKUDS/DeepTutor/blob/6cf793bd868ba5ecbe64722936d4be8fab5a01df/deeptutor/capabilities/mastery/tools.py)已有 assessment、grade、`hints_used` 与 `attempt_count` 等记录。

**重合与剩余问题。** D 和 B 的“把帮助量纳入掌握记录”“教学与测验分离”已有实现。所查路径不能证明跨题语义帮助暴露映射、题目等值或编程独立迁移的有效性；近期正确率也不是无偏认知掌握真值。不能说它“完全不记录帮助”。

**是否 Fork。** 完整知识/Agent 工作空间对最小机制验证过重；借鉴目标门控、测验状态与帮助计数作为强工程基线，不以 Agent 数和 RAG 规模作创新。

### P07. ITAP：没有 LLM 也能做自适应编程提示

**来源与版本。** [ITAP-django](https://github.com/krivers/ITAP-django/tree/dd6af07b02897f5b11305a1888a0b8df1f0f3d8e)，检查提交 `dd6af07b02897f5b11305a1888a0b8df1f0f3d8e`。作者研究资料可见 [论文](https://krivers.net/files/ijaied2015-paper.pdf)；本轮主要技术判断来自实际源码，不依赖论文标题推断。

**授权与维护。** [LICENSE](https://github.com/krivers/ITAP-django/blob/dd6af07b02897f5b11305a1888a0b8df1f0f3d8e/LICENSE)为 MIT；master 检查提交 2017-06-22T20:51:15Z，未归档，但长期无可见新提交。README 使用说明很少，不能当成现成可顺利部署的平台。

**实际机制。** [getHint.py](https://github.com/krivers/ITAP-django/blob/dd6af07b02897f5b11305a1888a0b8df1f0f3d8e/hintgen/getHint.py)包含 AST 清理、匿名化与规范化，选择正确目标状态与修改路径，测试后形成提示；重复同代码请求时可从 next_step、structure、half_steps 递进到 solution。这是非 LLM 的代码状态驱动帮助。

**重合与剩余问题。** 直接挑战 D 的必要 AI 主张，也为 A 提供强代码状态基线。它不意味着能可靠解释所有自然语言学生回答；旧依赖、代码变形覆盖、题目状态空间都是迁移成本。不能因年代早就忽略其机制重合。

**是否 Fork。** 不推荐把旧 Django 系统整库作为现有学习台的底座。值得借鉴透明的状态路径、逐级提示和传统非 AI 基线；保留 AI 必要性的反证价值。

### P08. GPT4Hints-GPT3.5Val：执行材料＋提示验证早有研究

**来源与版本。** [论文](https://arxiv.org/html/2310.03780v2)、[研究代码](https://github.com/machine-teaching-group/lak2024_GPT4Hints-GPT3.5Val/tree/f70a9c77f71c587c62df5de846db095d69f8f793)，检查提交 `f70a9c77f71c587c62df5de846db095d69f8f793`。最终链接使用当前仓库名，旧名称在 GitHub 返回重定向。

**授权与维护。** GitHub 未识别 license，进一步检查未截断的仓库树也未发现 LICENSE；本轮没有确认明确代码复用授权。检查提交 2024-03-11T13:16:51Z，未归档，是研究快照而非已确认持续维护产品。

**实际机制。** 使用失败测试和有效修复信息辅助生成解释/单条提示，再用 GPT-3.5 的模拟修复及测试结果筛选提示。[end_to_end.py](https://github.com/machine-teaching-group/lak2024_GPT4Hints-GPT3.5Val/blob/f70a9c77f71c587c62df5de846db095d69f8f793/src/end_to_end/end_to_end.py)连接修复、反馈、验证；[validation_pipeline.py](https://github.com/machine-teaching-group/lak2024_GPT4Hints-GPT3.5Val/blob/f70a9c77f71c587c62df5de846db095d69f8f793/src/validation/generation/validation_pipeline.py)比较有/无提示条件下的修复成功次数并筛选。

**重合与剩余问题。** C 的执行支撑和发布前验证高度重合；A 若只是“用失败用例让 AI 再想一次”也没有增量。论文的提示质量/覆盖指标不是学生独立迁移率；模拟学生能修好，不代表真实学生理解。也不能把其 LLM 验证器复制为本轮双 AI 评分。

**是否 Fork。** 在代码授权未明确前，不建议直接复用为作品底座。可借鉴公开的方法：向 tutor 提供可追溯失败事实，区分修复效果与教学效果；本项目只复用已有执行核验，不重做大规模模型模拟。

### P09. Lead-and-Reveal / Code engagement techniques：B 最接近的先行研究

**来源与版本。** [原始预印本 v1](https://arxiv.org/html/2410.08922v1)、[作者提供的 PDF](https://austinhenley.com/pubs/Kazemitabaar2025IUI_AIFriction.pdf)、[代码](https://github.com/MajeedKazemi/code-engagement-techniques/tree/4b506530f6b4ae7c7d252930c4f295516830098a)。检查提交 `4b506530f6b4ae7c7d252930c4f295516830098a`。本文依据实际取得的 2024 v1；作者 PDF 的文件名含 2025，但正文仍有预印本版本信息，不混用不同版本的效果数字。

**授权与维护。** [package.json](https://github.com/MajeedKazemi/code-engagement-techniques/blob/4b506530f6b4ae7c7d252930c4f295516830098a/package.json)声明 MIT，检查完整树未发现 LICENSE 文件：记录为“声明 MIT，授权文件不完整”，而非完全无声明或已完整核实。论文为 CC BY 4.0。检查提交 2025-01-31T00:05:30Z，未归档；持续支持未知。

**实际机制。** 研究比较多种认知参与方式，并测量无 AI 同构任务的表现与主观感受。Lead-and-Reveal 要求学生解释下一步后才揭示代码；Trace-and-Predict 要求预测跟踪结果。两项研究样本分别为 82、42 人，是研究规模而非推广效果保证。

检查 [codex-reveal-router.ts](https://github.com/MajeedKazemi/code-engagement-techniques/blob/4b506530f6b4ae7c7d252930c4f295516830098a/packages/server/routes/codex-reveal-router.ts)可见问题、回答评判与逐步揭示；[codex-tracing-router.ts](https://github.com/MajeedKazemi/code-engagement-techniques/blob/4b506530f6b4ae7c7d252930c4f295516830098a/packages/server/routes/codex-tracing-router.ts)包含变量预测、帧状态、错答提示与尝试升级；另读任务路由，不能仅依论文名称猜测交互。

**重合与剩余问题。** 它直接否定 B 的宽泛创新说法“让学生参与再做无 AI 新题”，也与 A 的事前预测、D 的帮助升级重合。拟保留 B 只能研究帮助内容如何影响后续题的测量价值，而不是复刻 Lead-and-Reveal。所查源码/论文没有提供本项目拟议的暴露内容感知选题验证；无 AI 同构题也不能自动外推所有远迁移或持久学习。

**是否 Fork。** 优先借鉴题对构造、认知参与操作和真实学生评价方法；不建议在授权文件仍不完整时直接搬入作品。它应该是 B 的重要强基线和必须承认的先行技术。

### P10. ProgFeed：反例质量与教学收益必须分开

**来源与版本。** [数据与代码](https://github.com/umass-ml4ed/progFeed-dataset-public/tree/e020c7c013187dba7b4130991eadc539d115526a)、[原始论文](https://arxiv.org/html/2606.08807v1)、[正式研究页面](https://proceedings.mlr.press/v339/heickal26a.html)。检查提交 `e020c7c013187dba7b4130991eadc539d115526a`。

**授权与维护。** [LICENSE](https://github.com/umass-ml4ed/progFeed-dataset-public/blob/e020c7c013187dba7b4130991eadc539d115526a/LICENSE)为 CC BY 4.0。检查提交 2026-06-07T18:52:15Z，未归档，是新近研究发布；不等于有持续维护教学服务。

**实际机制。** 2025 秋季 Python 课程资料包含 215 位同意参与者、43 题、17 次实验课中的 6,693 次提交；不能把合并表所有行数都算成论文分析的提交数。失败尝试可获得测试用例或自然语言提示，与无 AI 反馈对照。研究明确相关性/观察性限制，不能把分组标签直接解释为因果学习效果。

检查 [README](https://github.com/umass-ml4ed/progFeed-dataset-public/blob/e020c7c013187dba7b4130991eadc539d115526a/README.md)、[数据字典](https://github.com/umass-ml4ed/progFeed-dataset-public/blob/e020c7c013187dba7b4130991eadc539d115526a/DATA_DICTIONARY.md)、[feedback_generation.py](https://github.com/umass-ml4ed/progFeed-dataset-public/blob/e020c7c013187dba7b4130991eadc539d115526a/autograders/lab05_autograder_github_ai_abc/feedback_generation.py)：可见题目描述、学生代码、反馈类型与生成调用；`ai_feedback_type` 是分配条件，`ai_feedback_text` 才反映实际交付，交付仍不证明学生阅读或理解。不同课次的分配机制也不能一概称随机化。

**重合与剩余问题。** 强重合 C，也挑战 A 的“给反例就更有效”。研究分析表明用例可能无效或不能暴露问题，而有效反例不自动改善后续表现；没有据此证明独立迁移与保持。论文自然语言提示的部分质量判读采用模型评审，不能视作人工确认的学习真值。

**是否 Fork。** 不是适合直接 Fork 的通用 tutor。值得借鉴反馈交付/分配分开、失败用例核验、真实学生研究协议，以及把局部反馈质量与学习终点分开。本轮未下载批量学生数据或执行生成器。

## 3. 重合矩阵与可声称的增量

“强”表示有直接机制重合；“部分”表示覆盖组成环节；“—”表示不是所查路径的主要机制，**不是确认绝无该功能**。

| 对象 | A 分歧后的动态教学 | B 帮助与独立迁移 | C 可反证反馈 | D 动态帮助 |
|---|---|---|---|---|
| CodeHelp / Gen-Ed | 部分：上下文不足时澄清 | 部分：答案暴露护栏 | — | 部分 |
| CodeAid | 部分：上下文/错误反馈 | 部分：避免完整解法 | 部分 | 部分 |
| Iris / Artemis | 强：执行上下文、主动门控、版本差异 | 部分：帮助历史 | 部分：测试/构建工具 | 强 |
| OpenTutor | 强：认知状态、反例、换教法 | 部分：确认后迁移 | 部分：约束核验，非全事实核验 | 强 |
| SmartCode | 部分：互动引导、执行结果 | — | 强：已配置题真实执行 | 强 |
| DeepTutor | 部分：工具门控 | 部分：测验、提示记录 | 部分：工具检查 | 强 |
| ITAP | 部分：代码状态选择 | — | 部分：测试支持修改路径 | 强，且不依赖 LLM |
| GPT4Hints | 部分：失败事实生成提示 | — | 强 | 部分：筛选提示 |
| Lead-and-Reveal 等 | 部分：先预测/解释 | 强：无 AI 同构迁移 | — | 强：逐步揭示与参与 |
| ProgFeed | 部分：失败用例/提示 | 部分：帮助后的表现，但非独立迁移验证 | 强 | 部分：按失败尝试反馈 |

**A 的最小剩余空间：**不是发现证据冲突，而是在竞争解释下选择事前探针、用回答改变路由，并相对强基线减少错误教学决策。这个组合的新颖性仍需更完整文献和机制实验确认。

**B 的最小剩余空间：**不是新增无 AI 考试，而是暴露内容与候选题作答要求的映射，以及这种映射能否更好选择有测量价值的题。人工题标签可能足够，AI 必要性不能预设。

**C/D 的判断：**已有本地基础和多项外部实现，普通版本不值得独立立项。可靠性重要、用户需要和技术创新是不同判断。

## 4. 补充研究与非 AI 强基线

这些资料辅助候选筛选，不另计入上述 10 个主对象。

- [Faster Teaching via POMDP Planning](https://onlinelibrary.wiley.com/doi/10.1111/cogs.12290)讨论部分可观测学习状态下的教学决策。这说明 A 的状态推断、信息增益/决策规划属于已有研究传统；本文没有把经典选择准则称为原创算法。
- [Socratic debugging benchmark 论文](https://aclanthology.org/2023.bea-1.57/)与[研究仓库](https://github.com/taisazero/socratic-debugging-benchmark)提供人类苏格拉底式调试对话和问题生成评价参照。检查了指标代码；语言相似度/问句质量不是学生学习收益。已查树未发现明确代码许可证，因此只作为资料与基线定义参照。
- [Generative AI can harm learning](https://www.pnas.org/doi/10.1073/pnas.2422633122)及[作者 PDF](https://hamsabastani.github.io/education_llm.pdf)说明辅助阶段表现与无帮助测量需要区分；这是数学教育场景，不能把结果数字搬来预测本项目的编程效果，也不能据此说任何 AI tutor 都有害。
- [SocratiCode 2026 预印本](https://arxiv.org/html/2605.17857v1)是更新的苏格拉底编程教学研究参照。没有核实其可复用代码与授权，不把 prompt 参与研究误计为我们未被覆盖的新机制。

实际最小原型应优先比较：成熟 prompt tutor、教师自适应题库、人工语义标签选题、固定同构迁移测验、相同预算的三级帮助。不能再拿弱词匹配规则当唯一对手，也不能让第二 AI 的偏好成为主要结果。

## 5. 检索限制与复用决定

本轮实际遇到过错误同名链接、部分 arXiv HTML 失败、站点访问限制和匿名 GitHub API 额度限制。已通过作者链接/PDF、实际 v1 页面和可读 GitHub 接口恢复上述主要来源。没有读到的反射式提示论文全文、某些复制资料与其他论文附件，不计作已核实机制证据。CodeAid 官方源码未核实，P08/P09 授权有缺口，均在相应条目保留未知。

没有做系统性文献综述、依赖/安全审计、部署复现或全部分支搜索；不能证明某一组合“首次出现”。最近提交也不能证明所有机制在生产中有效。

| 复用层级 | 推荐对象与用途 | 当前决定 |
|---|---|---|
| 以本地代码为底座 | F02/F03/F04/F05 的结构化记录、有限核验、首答封存 | 保留，避免平台迁移消耗机制预算 |
| 借鉴机制/基线 | OpenTutor 状态、Iris 门控、SmartCode 三级提示、ITAP 非 AI 状态策略、DeepTutor 帮助计数 | 值得借鉴；依原授权选择局部代码或重新实现经典机制 |
| 借鉴研究设计 | CodeAid 课堂交互、Lead-and-Reveal 同构题与参与、ProgFeed 实际反馈交付、GPT4Hints 执行事实 | 值得借鉴方法；不照搬模拟学生验证或未经审定指标 |
| 整库 Fork | OpenTutor/SmartCode 可作为未来对照候选；其余或过重、或过旧、或授权/源码未核实 | 本阶段没有必要整库 Fork，本轮也未执行 |

这份调查降低了四个宽泛方向的新颖性预期。对 A/B 的保留是允许做一次有停止条件的研究筛查，不是确认已经找到可获奖的独立创新。
