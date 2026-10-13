> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# F02 验证链审计

本轮只审计、修复交互和做离线回归。新增导师推理0，新增AI评审0，新增编程题0；历史模型首次回答没有重生成，冻结学生数据没有修改。教学质量仍待人类复核，真实用户体验未完成。

审计输入涵盖21份导师原文、全部events/stderr/invocation/metadata、24条两组路径索引、64条逐轮记录、3份匿名审查包与原始评审、两版作者标签、2次历史CLI工程调用及入口代码。机器依据：historical_audit.json（仅本机证据：`experiments/feature_validation/F02_dynamic_questioning/validation_repair/historical_audit.json`；不随 Git 分发）。

原完成清单516项哈希在修复前全部相符；本轮另外固定517项旧文件（含旧完成清单自身）。修改仅限未冻结的当前cli_guard.py，修改前原字节保存在cli_guard_before.py（仅本机证据：`experiments/feature_validation/F02_dynamic_questioning/validation_repair/preserved/cli_guard_before.py`；不随 Git 分发）；原案例、gold、正式提示词、正式代码、报告、原始评分和失败全部保留。21项正式冻结核验通过，历史F01的969项没有改变。当前入口增加了薄的运行适配器，复用原F02协议、基线、执行器和正式CLI传输。

全部26份历史调用原文哈希、事件最后消息、单次完成、唯一会话标识核对通过；其中正式导师21、辅助评审3、历史CLI工程模型调用2。没有观察到工具调用。正式21份prompt与捕获f02_input一致，没有未来教师轮次进入正式导师输入。

模拟路径逐项分类如下。程序能够解析一条记录，不等于学生回应真正回答了问题；完成协议也不等于学会知识。

| 路径 | 导师输出/学生回应 | 原始结束状态 | 数据适配与可使用范围 |
| --- | --- | --- | --- |
| C01_correct | 2/1 | understanding_sufficient | 按模型建议结束；当前理解与停止合理性仍需人工复核，没有修改结果或学习效果 |
| C01_partial | 3/2 | budget_limited | 记录到达三次导师输出上限；最后问题未获回应，不能报闭合成功 |
| C01_unexpected | 2/1 | understanding_sufficient | 按模型建议结束；当前理解与停止合理性仍需人工复核，没有修改结果或学习效果 |
| C01_wrong | 2/1 | invalid_output | 原路径被守卫截断；修复后离线可展示，不补齐历史轮次 |
| C02_correct | 3/2 | understanding_sufficient | 按模型建议结束；当前理解与停止合理性仍需人工复核，没有修改结果或学习效果 |
| C02_partial | 3/2 | budget_limited | 记录到达三次导师输出上限；最后问题未获回应，不能报闭合成功 |
| C02_unexpected | 2/1 | await_new_evidence | 正确保存等待新版材料状态；未提供/执行新代码，不能认证新版输出 |
| C02_wrong | 3/2 | invalid_output | 原路径被守卫截断；修复后离线可展示，不补齐历史轮次；第二回应没有回答 s=5/i=2 的假设数值，部分相关，needs_human_review |
| C03_correct | 2/1 | understanding_sufficient | 按模型建议结束；当前理解与停止合理性仍需人工复核，没有修改结果或学习效果 |
| C03_partial | 3/2 | budget_limited | 记录到达三次导师输出上限；最后问题未获回应，不能报闭合成功；第二个学生回应说原版 +n 补偿，但上一问指定 local_patch，路径不适配，末轮两组无法评审 |
| C03_unexpected | 3/2 | budget_limited | 记录到达三次导师输出上限；最后问题未获回应，不能报闭合成功 |
| C03_wrong | 2/1 | invalid_output | 原路径被守卫截断；修复后离线可展示，不补齐历史轮次；即使放行，冻结模拟器不支持 n=1/n=3 双输入问句，不能自动补跑 |

12条S1路径中，4条按模型建议转入自行修改、1条等待新材料、4条达到预算、3条守卫截断。前5条是协议明确结束的候选路径；实际修改与学生理解都未经验证。没有可认证的“真实学生完整有效学习任务”分母。C03_partial明确不适配；C02_wrong有语义适配告警；其他路径的语义仍需人工复核。停止不足的路径不能删除或记成功。

历史64条逐轮索引有61条因共享history列表而混入当前/后续内容。这是保存与评审组织错误。正式调用的prompt/f02_input已经独立保存，未受此错误影响。64条前缀和冻结规则输出重新比对均一致；用于阅读应查responses下实际输入或results/reconstruction_v2，原坏索引保留。

三个评审包C01_wrong、C02_correct、C03_unexpected均使用了上述前视历史。32+48+48=128项首次模型辅助评价全部标为无效，接纳0项；不能只删掉冲突项后采纳其余评分。附带材料ID协议没有枚举限定，但解析器要求裸A/B，模型使用带案例前缀的ID又引起unknown_material_turn/rating_coverage，这也是组织协议问题。没有重新启动AI评审。auxiliary_review_validity_final.json（仅本机证据：`experiments/feature_validation/F02_dynamic_questioning/results/auxiliary_review_validity_final.json`；不随 Git 分发）保留原结论，reviews（仅本机证据：`experiments/feature_validation/F02_dynamic_questioning/reviews`；不随 Git 分发）保留原始包和首次结果。

分母审计：3个案例首问各调用一次，18个后续调用，合计21份真实输出；共享首问展开到路径后有30个S1记录，不能当30次独立推理。S0自身路径34条展开记录，去除重复首问后25项；同历史S0影子基线去重后21项。64条存储索引=30+34；67个评分决策=21+21+25。严格旧守卫18/21放行，3/21阻断，JSON结构21/21。20/21是作者动作初评的合理数，不是用户成功率。

以下是已有v2作者标签的正确统计，**本轮没有将其提升为认证准确率**。N/A剔出适用分母；无法评审保留并单列。appropriate_stop包含合理继续与等待材料，不是17次成功停止。

| 方法 | 指标 | 合理/未发现 | 错误/发现 | 待定 | 无法评审 | 适用分母 | N/A |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S0_own | question_discrimination | 10 | 8 | 4 | 0 | 22 | 3 |
| S0_own | uses_previous_information | 10 | 9 | 3 | 0 | 22 | 3 |
| S0_own | action_reasonableness | 13 | 9 | 3 | 0 | 25 | 0 |
| S0_own | repetition | 13 | 7 | 2 | 0 | 22 | 3 |
| S0_own | unsupported_knowledge_inference | 25 | 0 | 0 | 0 | 25 | 0 |
| S0_own | program_fact_error | 25 | 0 | 0 | 0 | 25 | 0 |
| S0_own | full_repair_leak | 25 | 0 | 0 | 0 | 25 | 0 |
| S0_own | appropriate_stop | 18 | 4 | 0 | 0 | 22 | 3 |
| S1 | question_discrimination | 15 | 0 | 0 | 1 | 16 | 5 |
| S1 | uses_previous_information | 17 | 0 | 0 | 1 | 18 | 3 |
| S1 | action_reasonableness | 20 | 0 | 0 | 1 | 21 | 0 |
| S1 | repetition | 17 | 0 | 0 | 1 | 18 | 3 |
| S1 | unsupported_knowledge_inference | 21 | 0 | 0 | 0 | 21 | 0 |
| S1 | program_fact_error | 21 | 0 | 0 | 0 | 21 | 0 |
| S1 | full_repair_leak | 21 | 0 | 0 | 0 | 21 | 0 |
| S1 | appropriate_stop | 17 | 0 | 0 | 1 | 18 | 3 |
| S0_shadow | question_discrimination | 9 | 4 | 4 | 1 | 18 | 3 |
| S0_shadow | uses_previous_information | 9 | 4 | 4 | 1 | 18 | 3 |
| S0_shadow | action_reasonableness | 12 | 4 | 4 | 1 | 21 | 0 |
| S0_shadow | repetition | 12 | 3 | 2 | 1 | 18 | 3 |
| S0_shadow | unsupported_knowledge_inference | 21 | 0 | 0 | 0 | 21 | 0 |
| S0_shadow | program_fact_error | 21 | 0 | 0 | 0 | 21 | 0 |
| S0_shadow | full_repair_leak | 21 | 0 | 0 | 0 | 21 | 0 |
| S0_shadow | appropriate_stop | 15 | 2 | 0 | 1 | 18 | 3 |

旧首次作者标签仍在author_review.json，后续修正版在author_review_v2.json。C03_partial_T3对S1和同历史S0同时排除有效成功，避免只惩罚一组。C02_wrong_T3仍有回答适配风险，其作者合理标签不能证明该路径有效。当前4项作者候选增量仅有3项无这个告警，全部依赖有限规则版本，没有有效独立教学评分支持优势。

36/36输入—版本程序输出重新受控执行相符；10/10既有作者选取的原文数值断言再执行相符。断言选择和自然语言到结构化请求的映射是作者判断，不能称全文自动事实认证。正式模型新execution_requests为0，预测正确率分母0，应记N/A。守卫重放公共证据不能改写成模型提出了新预测。

结论：工程原始推理证据可信；评审包污染，独立教学评分无效；模拟对话闭合性与教学可靠性未获认证。[F02_final_readiness.md](<F02_final_readiness.md>)给出分层验收状态。
