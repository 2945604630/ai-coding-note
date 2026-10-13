> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# F02 分项初审与证据边界

全部12条学生路径是冻结模拟输入，不是真实学生。作者评分是带原文依据的模型辅助初审，未经独立人类认证。三次辅助AI审查都受到评审包未来历史污染，不能作为有效独立评分；原文和失败检查全部保留，未重新采样。相同基础模型的新会话也具有相关错误。不得把表格称为学习效果或总体准确率。

| 组 | 分项 | 合理/未发现风险 | 错误/发现风险 | 待定 | 无法评审 | 适用分母 | N/A |
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
| S1 | repetition | 18 | 0 | 0 | 0 | 18 | 3 |
| S1 | unsupported_knowledge_inference | 21 | 0 | 0 | 0 | 21 | 0 |
| S1 | program_fact_error | 21 | 0 | 0 | 0 | 21 | 0 |
| S1 | full_repair_leak | 21 | 0 | 0 | 0 | 21 | 0 |
| S1 | appropriate_stop | 17 | 0 | 0 | 1 | 18 | 3 |
| S0_shadow | question_discrimination | 10 | 4 | 4 | 0 | 18 | 3 |
| S0_shadow | uses_previous_information | 10 | 4 | 4 | 0 | 18 | 3 |
| S0_shadow | action_reasonableness | 13 | 4 | 4 | 0 | 21 | 0 |
| S0_shadow | repetition | 13 | 3 | 2 | 0 | 18 | 3 |
| S0_shadow | unsupported_knowledge_inference | 21 | 0 | 0 | 0 | 21 | 0 |
| S0_shadow | program_fact_error | 21 | 0 | 0 | 0 | 21 | 0 |
| S0_shadow | full_repair_leak | 21 | 0 | 0 | 0 | 21 | 0 |
| S0_shadow | appropriate_stop | 16 | 2 | 0 | 0 | 18 | 3 |

“未发现风险”是作者全文审查结论，不是自动机器认证。N/A不作零分；无法评审保留在适用分母。appropriate_stop同时评价正确继续/等待材料，不等于有17次成功终止；实际理解充分停止仅4条路径。

作者动作初审：S1合理20、错误0、待定0、无法评审1（21个实际输出）；同历史S0合理13、错误4、待定4、无法评审0。三个被旧守卫阻断的S1输出可有合理教学意图，但没有完成相应路径，不能报20/21用户成功。C03_partial_T3因冻结回应与前问版本不匹配，不计有效动态路径成功；其原文仍显示版本澄清。C02_wrong的假设状态问题与回应数值不对应，适配保留needs_human_review，不据此宣称学习进步。

作者初审中S0错误→S1合理的配对为C01_unexpected_T2、C02_wrong_T3、C03_correct_T2、C03_unexpected_T3；C02_wrong有回答适配告警，只有其它3项是无此告警的候选增量。全部为当前规则版本和模拟样本的候选结论，不证明一般规则无法解决。

客观检查：36/36冻结输入-版本输出实际重放相同，选取10/10明确模型数值断言经受控执行符合实际与oracle；模型结构化新execution_requests为0，预测正确率N/A（分母0）。新运行入口另外重放已引用的公共证据，不伪装成模型新预测。自然语言全部因果、意图和教学价值不能被这10项自动核验覆盖。

全部原文与首次作者标签在results/author_review.json、results/decision_quotes.md；后者原索引历史有错误，请查responses/*/f02_input.json或results/reconstruction_v2/确认时序。程序核验在selected_fact_claims.json、integrity_audit_v2.json；无综合百分比，无独立人类评分一致性。
