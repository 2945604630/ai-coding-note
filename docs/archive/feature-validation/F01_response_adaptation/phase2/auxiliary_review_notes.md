> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# F01 第二阶段匿名辅助审查

所有教学语义成绩是作者模型辅助初审，全部needs_human_review；独立人类复核0，真实学生0。辅助AI评审同基础模型、新会话，不能认证真值或学习提升。困难样本由知晓原规则的作者设计，属于小规模对抗机制测试。

预先选定H01/H04/H07/H08/H10/H12，每例一名新会话评审，逐维直接评分，不选赢家；三份回答随机A/B/C，身份映射仅父进程保存。工作目录只提供当前审查包与schema，未供gold、允许集合、初审或旧评分。文字风格可能暴露来源，未验证OS隔离，不能称完全盲审。

| 维度 | 有效辅助标签数 | 与作者相同 | 不同 |
| --- | --- | --- | --- |
| understanding | 18 | 17 | 1 |
| action | 18 | 18 | 0 |
| omissions | 18 | 18 | 0 |
| knowledge_overreach | 18 | 18 | 0 |
| unnecessary_repeat | 18 | 18 | 0 |
| program_contradiction | 18 | 18 | 0 |
| explanation | 18 | 18 | 0 |
| repair_leak | 18 | 16 | 2 |

各维单独分母，标签一致只反映模型辅助意见一致性，不能转换教学正确率。

## H04 S0 understanding

作者：uncertain；辅助AI：error。

> 你指出本次规范最大值是-2，并说明额外零与输入的区别。

学生本轮没有重新指出规范最大值为-2，而是要求不要重复解释它；核心表达是询问非空时保底的意义。该解释把背景数值当作本轮主要表达，未识别实际请求。

保留needs_human_review，不多数表决。

## H12 S2 repair_leak

作者：1；辅助AI：0。

> 请按这个约定自行修改提交的函数。

仅澄清目标契约并要求自行修改，没有给出端点编辑、补项操作或代码。末项由调用者补的说法已由学生提出，回答否定该评测假设不构成新增关键修复。

保留needs_human_review，不多数表决。

## H12 S1 repair_leak

作者：1；辅助AI：0。

> 请你自行修改，让这个函数独立满足题目要求，并简述修改思路。

仅规定结果责任并请求自主修改，没有提供如何调整range或在哪里补项的关键操作。提到调用者补末项是回应学生已有说法，不是新增修复方案。

保留needs_human_review，不多数表决。

全部恢复身份评分：auxiliary_review_restored.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/results/auxiliary_review_restored.json`；不随 Git 分发）。原始首次回答：

| 案例 | 原文 | 引用/结构核验 |
| --- | --- | --- |
| H01 | raw_response.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/judge_responses/H01/raw_response.json`；不随 Git 分发） | judge_validity_H01.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/results/judge_validity_H01.json`；不随 Git 分发） |
| H04 | raw_response.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/judge_responses/H04/raw_response.json`；不随 Git 分发） | judge_validity_H04.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/results/judge_validity_H04.json`；不随 Git 分发） |
| H07 | raw_response.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/judge_responses/H07/raw_response.json`；不随 Git 分发） | judge_validity_H07.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/results/judge_validity_H07.json`；不随 Git 分发） |
| H08 | raw_response.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/judge_responses/H08/raw_response.json`；不随 Git 分发） | judge_validity_H08.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/results/judge_validity_H08.json`；不随 Git 分发） |
| H10 | raw_response.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/judge_responses/H10/raw_response.json`；不随 Git 分发） | judge_validity_H10.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/results/judge_validity_H10.json`；不随 Git 分发） |
| H12 | raw_response.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/judge_responses/H12/raw_response.json`；不随 Git 分发） | judge_validity_H12.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/results/judge_validity_H12.json`；不随 Git 分发） |
