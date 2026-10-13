> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# F01 失败与风险记录

本轮8个预设模拟回答、2道既有题，没有真实学生。语义判定是研究Agent的带原文依据作者初审，全部needs_human_review，独立人类复核0；机械事实核验另列。没有综合准确率或学习提升结论。

S1/S2均为官方Codex CLI独立新exec，gpt-6.1-sol/high，同一1200秒上限及输出格式，两组都禁止完整修复；精确后台快照未知。第一份原始回答保留，无按质量重采样。公开输入一致，旧评分、参考标签、其他回答没有提供给生成会话。工具禁用及本地渲染探针不提供OS deny-read或服务端上下文认证；不能称完全盲测。

## S0_R03

标记：teaching_ambiguity。

3的指代不清，问实际与规范的区别；不确诊认知。补充复核：固定问句同样只列两种指代，未包括末次i或循环次数等可能，和AI问句一样存在非穷尽选项风险；保留首份初审，不把它视为已确认误导。

保留的原文/失败输出（仅本机证据：`experiments/feature_validation/F01_response_adaptation/results/S0_R03.json`；不随 Git 分发）

## S1_R03

标记：teaching_ambiguity。

正确保留3的含义待定并澄清，不确认误解；列循环次数/最后值/唯一值后要求完整序列，未覆盖实际输出或规范结果等指代。没有真实回答不能断言该澄清已经误导，但存在额外任务和选项偏窄风险。

保留的原文/失败输出（仅本机证据：`experiments/feature_validation/F01_response_adaptation/responses/S1_R03/raw_response.json`；不随 Git 分发）

## S2_R03

标记：teaching_ambiguity。

合理选择澄清，未断言3的唯一含义；最后值/唯一值二选项并非穷尽可能，可能漏实际输出指代。简短不代表更准确，该风险需要真实回应或人类复核。

保留的原文/失败输出（仅本机证据：`experiments/feature_validation/F01_response_adaptation/responses/S2_R03/raw_response.json`；不随 Git 分发）

## S2_R06

标记：teaching_ambiguity。

识别当前话语而不确认最初动机，提示原列表比较范围，动作属于冻结集合且相关。复用已曝光E01/已给预期-2的输入再问应返回什么，可能只诱发复述，信息增量未明；不能视为比S1新反例更强。

保留的原文/失败输出（仅本机证据：`experiments/feature_validation/F01_response_adaptation/responses/S2_R06/raw_response.json`；不随 Git 分发）

## S2_R07

标记：teaching_ambiguity。

保留添加零意图与是否注意输入候选未知，转问规范符合性，合理。把0联系到添加行为在上下文中合理但不是唯一解释；已曝光预期值可能诱发复述，教学信息量待人类或真实回答确认。

保留的原文/失败输出（仅本机证据：`experiments/feature_validation/F01_response_adaptation/responses/S2_R07/raw_response.json`；不随 Git 分发）

## 共同限制

8个回应由实验作者设计，知道基线，词汇覆盖有选择偏差；只用两个小程序，不能评估自然回答分布。高分可能来自显式回答本已包含正确解释，不能当作AI诊断创新。未观察真实改码、接受追问的程度、步骤耗时或独立新题。

正式stderr及事件警告原样保存，传输重连与沙箱/技能扫描不冒充教学错误或工具调用；未知服务端版本、未证实文件隔离仍记录。
