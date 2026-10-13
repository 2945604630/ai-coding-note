> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# 创新性重叠审查：先尝试证明方案已经存在

核验日期：2026-10-08。已重新阅读上一轮六份报告；工作目录未找到可访问的本地 AIC 指导文档，沿用已核对的[官方规则附件](https://www.aicomp.cn/wp-content/uploads/2026/08/%E9%99%84%E4%BB%B61_AIC%C2%B7AI%E5%BC%80%E6%BA%90%E7%AB%9E%E8%B5%9B%E8%A7%84%E5%88%99%E5%8F%8A%E4%BD%9C%E5%93%81%E6%8F%90%E4%BA%A4%E8%A6%81%E6%B1%820812.pdf)。**本轮不使用比赛截止时间作筛选、评分或淘汰依据。**

结论：A 的“诊断—练习—掌握更新”、B 的“执行结果进入模型并约束判决”、C 的“生成—执行—修复—接受”均已有直接先例。没有证据支持把任何一个宽泛组合称为原创。仍值得检验的，是在有限 Python 错误族内，建立可拒绝、可撤销的证据与学习观测规则，并证明它比强基线减少误诊或错误掌握记录。它是**有差异化潜力的工程与教学机制假设**，尚未得到效果验证。

## 1. 证据等级与审查边界

| 标记 | 本报告含义 | 不代表什么 |
|---|---|---|
| S：源码确认 | 成功取得固定提交的文件，读到对应实现与关键调用关系 | 本机运行成功、上线可用、教学有效 |
| P：部分实现／公开资料 | 部分模块存在，或论文／官方文档报告其系统机制，未复现完整系统 | 可以整仓直接复用、论文效果适用于本方案 |
| N：未找到明确实现证据 | 在列明的路径和检索范围内未找到所讨论机制 | 全仓绝不存在、其他项目没有、全球原创 |

本轮针对性追加五项对照：Artemis／Hyperion、SMoL Tutor、HypoCompass、CodeBenchGen、EvalPlus。后三种基准或研究系统与学习产品目标不同，但直接挑战了“假设检验”“变式训练”“测试质检”的创新主张。没有重新扩大候选池。SMoL Tutor 与 HypoCompass 按**研究先例**比较，未声称取得其完整产品源码。

原有仓库继续固定上一轮提交；新增源码固定为：Artemis `aafd3924cae763ba168ff3faa2e7681d0b662ef1`；CodeBenchGen `e6d31c14168a4eb8de56562a5e5d6b11fe22542e`；EvalPlus `26d6d00bb1fd0fa37f39c99d5290da67891d1c5e`。默认分支快照不等同已发布稳定版。未安装依赖、运行下载的源码或进行功能实验。

## 2. 对第一轮结论的关键修正

### OpenTutor 已有真实串联的闭环，不能只描述成若干独立名词

**S：** [quiz_submission.py][ot-submit] 第 143～151 行调用编程评分；第 168～201 行分类并记录错题；第 222～227 行按知识点更新概念掌握；第 251～254 行触发自动诊断题生成。`_auto_derive_diagnostic` 在第 54～83 行连接错题与派生题，并非只有 README 宣称。

**S：** [wrong_answers.py][ot-wa] 第 188～279 行已有原题／简化题的对照诊断：两题均错、简化题对、原题对、两题均对分别映射到不同诊断。未完成简化题时返回 pending。第 90～123 行原题 retry 正确后把 `mastered` 设为真。

**S：** [loom_mastery.py][ot-loom] 按题型设置 BKT guess／slip，并连接概念状态；[derive.py][ot-derive] 生成同核心概念的简化题。因此，“两题对照”“pending”“根据作答更新掌握”也不是可以独立申报的新点。

**局限，按已读路径限定：** [coding_grader.py][ot-grade] 是模型评分，未调用实际代码执行器；该路由中的掌握更新参数是正确性和题型，没有独立作答或提示暴露参数；上述对照诊断直接解释两题表现，不能由它证明学习者真实持有某种误解。其他 Agent 路径有执行器，不等于这个编程测验评分调用已经接入执行器。

### SmartCode 已考虑提示依赖，不能说现有项目完全忽略它

**S：** [submissions.py][sc-submit] 第 48～64、535～546 行统计提示次数并扣分，第 293～388 行用最终分影响技能增长，第 421～482、598 行附近连接更新后推荐。[recommendations.py][sc-rec] 读取技能和未完成题生成建议。它已有自适应练习回路。

**局限：** 提示扣分后仍允许技能增长，失败的技能增量被截为不下降；这与“辅助完成不进入独立观测”不同。不能把两者区别偷换成“已有项目没有提示记录”。

### Iris 已有确定性输出检查，不能笼统称为纯提示词

**S：** [struggle_intervention_pipeline.py][iris-struggle] 的 `_valid_anchor` 校验文件是否在模型所见快照、行号是否存在；`parse_gate_result` 校验动作、JSON 和置信度类型，异常输出可降级或失败。已有的引用存在性与输出状态检查，缩小了 B 可声称的新空间。

**边界：** 文件行存在，并不证明该行是因果根源；模型置信度不等于诊断校准；[提示合约][iris-contract] 约束不泄完整解答，也不能保证语义上绝不泄题。

## 3. 项目与机制对照

| 先例 | 已有能力与证据等级 | 对 A／B／C 的实质挑战 | 此次未确认的更窄机制 |
|---|---|---|---|
| CodeHelper Studio | S：提交执行、错题收集、AI 复盘、自评与 SM-2；[提交 IPC][ch-submit]、[复盘构造][ch-review]、[复习 IPC][ch-schedule] | A 的入口与复习产品已在；“AI 分析错题”重合。快捷提示已有同类题／反例要求 | 当前复盘输入未携带完整逐用例证据；提交表主要保存汇总；未见跨题、提示条件限定的独立验收规则 |
| OpenTutor | S：错题分类、派生题、两题对照诊断、概念掌握更新、教学状态 | A 最接近的开源闭环；②③不能只换成“迁移／独立”名称 | 已读编程评分及掌握更新路径未见运行事实约束、辅助事件隔离和盲验题资格闸门 |
| SmartCode | S：执行覆盖模型判决、三级提示、提示扣分、技能更新后推荐 | A 的自适应回路、B 的事实覆盖均重合 | 真失败时可保留模型原解释；没有因此核验解释的原因；提示扣分不同于独立验收 |
| Iris／EduTelligence | S：测试反馈上下文、提示契约、干预状态、快照锚点校验 | B 的证据引用、非泄题提示和输出门控部分已存在 | 所读路径未见逐错因预测与区分性反例组成的因果核验；不能据此断言全系统无此能力 |
| CF Compass | S：提交版本、时间线、diff 的复盘数据存储，[ai-review-storage.cjs][cf-storage] | B 的“证据化复盘报告”已有替代 | 存证和展示不等于解释核验 |
| Exercism Python | S：概念题、参考与测试映射，[概念配置][ex-config]和[边界测试][ex-test] | A 的固定概念练习，C 的可执行题包有更简单现成起点 | 不是 AI 生成器，也未提供本方案的误解确认流程 |
| Pyodide／ts-fsrs | S：执行 API／调度纯模块；[Worker 文档][py-worker]、[FSRS 接口][fsrs] | 可复用底层；调用它们或替换 SM-2 不产生新机制 | 不解决诊断真实性、题意真值或学习独立性 |
| Piston／Judge0／QDU OJ | S／P：上一轮已读执行、用例与提交路径 | ①⑥⑦的执行与回归均是成熟基础能力 | 执行服务不自动确认人的知识漏洞；不必同时接多个执行器 |
| pyKT／TuTor／Dify | S／P：追踪研究、教学操作规则、工作流框架 | 学习状态、学生自己动手、流程编排均有先例 | 换模型或叠加框架不能证明本任务的因果与教学收益 |

## 4. 五个追加对照揭示的重叠

### 4.1 Artemis／Hyperion：C 的基础流程已经完整存在

**S：** [ProgrammingVariantAdapterService.java][art-adapter] 第 318～374 行把构建和一致性检查接入核验；第 563～615 行检查 solution 和 template；第 701～720 行接语义一致性检查。[VariantAgentLoopService.java][art-loop] 将核验反馈用于下一轮编辑，并在核验前持久化修改；[核验测试源码][art-test] 也实际存在，但本轮未运行。

实现要求 solution 编译并通过全部测试；template 要实际执行测试且目标得分为 0；还核对题面任务中的测试引用。语义一致性检查不可用、失败或超时，可不产生 finding 并继续核验。官方[变式题文档][art-doc]明确仍需教师审阅教学目标。

所以，“生成题面、参考解和测试后自动检查与修复”**已有源码先例**。可能留下的差异是：针对教师指定误解的有效变异体、独立预言机、教学目标证据，以及未完成语义检查时禁止标成教学合格。但目标变异检查本身也是成熟测试思想，不能直接宣称新算法。

### 4.2 SMoL Tutor：误解诊断、同概念后续题已有研究先例

**P：** [2024 OOPSLA 论文][smol-paper] 第 6 节描述按错误选项关联误解提供解释，随后给语义相同、表面变化的输入式问题；后续模块也检查此前概念。其程序行为语义明确、误解集合经过研究整理，比“LLM 按粗标签猜漏洞”更扎实。

它不是从任意 Python 提交自动诊断的完整开源工作台；论文中的误解解释与后续检查足以推翻“确认误解后训练是新想法”。本轮未取得 Tutor 完整源码；`shriram/smol` 是相关语言实现，不能冒充 Tutor 仓库。

### 4.3 HypoCompass：区分性测试与错误解释训练已有直接研究

**P：** 固定[论文 v5][hypo-paper]第 3～4 节：学习者提出测试及错误解释，系统使用行为向量筛选不同 bug 和相似干扰解释，用能区分行为的用例反馈；生成过程中还有逐步人工核验。

这直接挑战 B 的“通过反例区分诊断”和 C 的“生成错误程序后筛选”。区别可以是处理学习者实际提交、机器可审计的诊断状态与观测隔离，而不是换成 AI 导师角色。论文学习结果没有被本轮复现，不移植为我们的效果承诺。

### 4.4 CodeBenchGen：生成测试、执行、修复和筛选已经存在

**S：** [generate_test_cases.py][cb-tests] 生成断言；[execution.py][cb-exec] 执行并保存成功／错误；[debug.py][cb-debug] 使用错误信息进行下一轮修改。它面向执行型代码基准，和教师出题目标不同。

关键限制：生成后的函数与测试可在同一个修复提示里被修改，执行成功不等于符合独立题意。其执行脚本还含自动安装依赖的路径，**本轮只读，未执行**，也不把它当现成 Windows 安全执行器。独立预言机与冻结题意是 C 必须自己补的边界。

### 4.5 EvalPlus：测试扩充、变异检测不是新的质量思想

**S：** [inputgen.py][ep-input] 同时使用 LLM 与类型感知输入变异；[evaluate.py][ep-eval] 用 canonical solution 计算期望输出；[mutation_init.py][ep-mut] 生成程序变异体、评估并记录测试能杀死哪些变异体。

必须区分**输入变异**与**程序变异测试**。EvalPlus 是代码评测基础，不是教学目标确认系统，但足以否定“加边界输入或 mutation score 即自主创新”。它也依赖可信参考，不能从任意新题自动产生绝对真值。

## 5. 分方案反向结论

| 问题 | A：学习闭环 | B：诊断引擎 | C：题目生成与质检 |
|---|---|---|---|
| 最近先例 | OpenTutor 完整串联；SmartCode 自适应回路；SMoL 教学机制 | SmartCode 执行覆盖、Iris 锚点检查；HypoCompass 区分性反馈 | Artemis／Hyperion 最接近产品；CodeBenchGen／EvalPlus 提供生成与测试机制 |
| 完全重合的基础功能 | 记录错误、解释、同概念题、答题后更新状态、复习 | 运行输入进入提示、覆盖虚构通过判决、分层提示、有效行引用 | 生成题／解／测试，执行、反馈修复、接受拒绝、测试增强 |
| 仅实现不同 | Electron 与 Web；SQLite 与其他 DB；BKT／规则；固定题与自由生成 | JSON 与文本，模型与 Provider，Worker 与 subprocess | 本地函数题与大型 CI 题包，不同语言或模型 |
| 本范围未充分确认的缺口 | 先确认人的误解再选训练；只让合格独立新题进入独立观测；更正误诊后撤回关联推荐 | 每个可检验断言绑定代码／测试／运行版本；假设须给可反驳预测；矛盾、缺证、过期有不同状态 | 冻结独立题意与预言机；目标误解变异体检查；未完成检查不能被包装成教学合格 |
| 可衡量改进 | 错误训练分配率、辅助成功被误计独立通过率、未见题表现 | 无依据归因率、矛盾断言率、正确诊断覆盖率、待定率、耗时 | 弱题误放行率、目标变异体存活率、偏题率、人工修订成本 |
| 是否值得成为核心 | 有条件值得：最有用户价值，但人的误解与迁移效果最难验证 | 有条件值得：最易独立验证并复用；须超越仅有存证／引用检查 | 有条件值得：需击败 Artemis 式硬闸门＋成熟变异测试，而不只击败裸出题提示 |
| 更简单替代 | 固定诊断问＋人工审题的新题＋规则记录，参考 SMoL／Exercism；不必全自动生成 | 确定性测试报告＋教师指出错误；Iris／SmartCode 加少量约束 | 教师写模板与预言机，用固定参数变式和已有测试／mutation 工具 |

## 6. 可保留与应撤回的创新表述

**可以作为待验证主张：** 面向有限错误族，将“执行事实、程序原因假设、学习者误解假设、独立作答观测”分别核验和存储；用区分性反例／追问控制状态更新，避免无证据诊断污染训练与掌握记录。

**不能提前写成已实现成果：** 自动知道学生为何犯错、自动证明任意代码根因、证明真实掌握、全自动保证生成题正确、世界首个闭环或首个证据导师。有限用例只能反驳或支持有限断言；新题独立通过也是一次观测，长期掌握还需延迟、跨任务验证。

下轮至少比较四个等模型、等输入强度的基线：自由文本解释；已有运行事实覆盖；引用存在性检查；完整的区分证据与状态规则。A 再加入固定诊断题＋人工映射基线，C 再加入 Artemis 式基础闸门＋通用变异测试基线。**若强基线达到同等收益，更简单方法优先，缩减创新主张。**

## 7. 获取失败与覆盖限制

Artemis GitHub 连接器的完整递归树响应超过 8 MB，被拒绝；通过只读 GitHub API 下载目录树恢复，树标记 `truncated=false`，再逐个取得上述文件。新增选取的 19 个源码／许可／说明文件均成功下载，原有项目补读了路由与掌握模块；这是获取证据，不是实验。

SMoL 作者 PDF 的网页打开失败，使用出版方可检索的正文作为研究机制证据；没有将 PDF 失败写成已成功阅读全文。HypoCompass 固定 v5 正文已取得；旧预印本与 v5 数字不同，本报告不混用效果数据。以上限定检查路径不是全仓形式化审计。

[ch-submit]: https://github.com/SuLiverse/CodeHelper-Studio/blob/23773e843d2a7bc3b04eedff59055b6c3a7afe7b/electron/ipc/problems.ts
[ch-review]: https://github.com/SuLiverse/CodeHelper-Studio/blob/23773e843d2a7bc3b04eedff59055b6c3a7afe7b/src/views/ReviewView.tsx
[ch-schedule]: https://github.com/SuLiverse/CodeHelper-Studio/blob/23773e843d2a7bc3b04eedff59055b6c3a7afe7b/electron/ipc/review.ts
[ot-submit]: https://github.com/zijinz456/OpenTutor/blob/5fea390a49be81827342caa19846fecbcf147e4a/apps/api/routers/quiz_submission.py
[ot-wa]: https://github.com/zijinz456/OpenTutor/blob/5fea390a49be81827342caa19846fecbcf147e4a/apps/api/routers/wrong_answers.py
[ot-loom]: https://github.com/zijinz456/OpenTutor/blob/5fea390a49be81827342caa19846fecbcf147e4a/apps/api/services/loom_mastery.py
[ot-derive]: https://github.com/zijinz456/OpenTutor/blob/5fea390a49be81827342caa19846fecbcf147e4a/apps/api/services/diagnosis/derive.py
[ot-grade]: https://github.com/zijinz456/OpenTutor/blob/5fea390a49be81827342caa19846fecbcf147e4a/apps/api/services/diagnosis/coding_grader.py
[sc-submit]: https://github.com/mohddarwix/SmartCode/blob/8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d/backend/app/routers/submissions.py
[sc-rec]: https://github.com/mohddarwix/SmartCode/blob/8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d/backend/app/routers/recommendations.py
[iris-struggle]: https://github.com/ls1intum/edutelligence/blob/4065add4b76b2edd283f35e31d5ac620f477077e/iris/src/iris/pipeline/struggle_intervention_pipeline.py
[iris-contract]: https://github.com/ls1intum/edutelligence/blob/4065add4b76b2edd283f35e31d5ac620f477077e/iris/src/iris/pipeline/prompts/templates/struggle_hint_contract.j2
[cf-storage]: https://github.com/Binah-Dev/cf-compass/blob/d94717313d2afd332712c7b1b4ad34d8b9a8ac2b/electron/services/ai-review-storage.cjs
[ex-config]: https://github.com/exercism/python/blob/6105f6d9d3ef66ce3d5c8f529d2882af3d76b706/exercises/concept/meltdown-mitigation/.meta/config.json
[ex-test]: https://github.com/exercism/python/blob/6105f6d9d3ef66ce3d5c8f529d2882af3d76b706/exercises/concept/meltdown-mitigation/conditionals_test.py
[py-worker]: https://github.com/pyodide/pyodide/blob/e4d3ae954d01d61a3e90531d63b881f2d33361b4/docs/usage/webworker.md
[fsrs]: https://github.com/open-spaced-repetition/ts-fsrs/blob/c8ca282edc3fe1cdfa1c24912437938b63a25cb3/packages/fsrs/src/fsrs.ts
[art-adapter]: https://github.com/ls1intum/Artemis/blob/aafd3924cae763ba168ff3faa2e7681d0b662ef1/src/main/java/de/tum/cit/aet/artemis/hyperion/service/variants/ProgrammingVariantAdapterService.java
[art-loop]: https://github.com/ls1intum/Artemis/blob/aafd3924cae763ba168ff3faa2e7681d0b662ef1/src/main/java/de/tum/cit/aet/artemis/hyperion/service/variants/VariantAgentLoopService.java
[art-test]: https://github.com/ls1intum/Artemis/blob/aafd3924cae763ba168ff3faa2e7681d0b662ef1/src/test/java/de/tum/cit/aet/artemis/hyperion/service/variants/ProgrammingVariantAdapterServiceVerifyTest.java
[art-doc]: https://docs.artemis.tum.de/instructor/exercises/variant-generation/
[smol-paper]: https://doi.org/10.1145/3649823
[hypo-paper]: https://arxiv.org/html/2310.05292v5
[cb-tests]: https://github.com/yiqingxyq/CodeBenchGen/blob/e6d31c14168a4eb8de56562a5e5d6b11fe22542e/CodeBenchGen/generate_test_cases.py
[cb-exec]: https://github.com/yiqingxyq/CodeBenchGen/blob/e6d31c14168a4eb8de56562a5e5d6b11fe22542e/CodeBenchGen/execution.py
[cb-debug]: https://github.com/yiqingxyq/CodeBenchGen/blob/e6d31c14168a4eb8de56562a5e5d6b11fe22542e/CodeBenchGen/debug.py
[ep-input]: https://github.com/evalplus/evalplus/blob/26d6d00bb1fd0fa37f39c99d5290da67891d1c5e/evalplus/inputgen.py
[ep-eval]: https://github.com/evalplus/evalplus/blob/26d6d00bb1fd0fa37f39c99d5290da67891d1c5e/evalplus/evaluate.py
[ep-mut]: https://github.com/evalplus/evalplus/blob/26d6d00bb1fd0fa37f39c99d5290da67891d1c5e/tools/tsr/mutation_init.py
