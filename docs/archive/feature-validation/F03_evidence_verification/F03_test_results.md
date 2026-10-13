> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# F03 实际测试结果

2026-10-11。一次正式主测试，三个复用案例各三项核验；本轮新增模型调用 **0 次**。未生成或修改历史模型回答。

正式结果：**6 条可执行谓词，正确支持 4 条、正确反驳 2 条，错误支持/反驳 0 条；其余 3 条无法核验。** 这是显式谓词核验结果，不是自然语言诊断或教学准确率。

| 核验 | 源码版本 | 合法参数 | 实际返回 | 参考返回 | 陈述判定 | 证据 |
|---|---|---|---|---|---|---|
| A01 | original | `[3]` | 3 | 6 | 支持 | A01证据（仅本机证据：`experiments/feature_validation/F03_evidence_verification/results/formal_v1/A01/result.json`；不随 Git 分发） |
| A02 | original | `[3]` | 3 | 6 | 反驳 | A02证据（仅本机证据：`experiments/feature_validation/F03_evidence_verification/results/formal_v1/A02/result.json`；不随 Git 分发） |
| A03 | original | `[3]` | 3 | 6 | 无法核验 | A03证据（仅本机证据：`experiments/feature_validation/F03_evidence_verification/results/formal_v1/A03/result.json`；不随 Git 分发） |
| B01 | local_patch | `[1]` | 1 | 1 | 支持 | B01证据（仅本机证据：`experiments/feature_validation/F03_evidence_verification/results/formal_v1/B01/result.json`；不随 Git 分发） |
| B02 | local_patch | `[3]` | 8 | 6 | 反驳 | B02证据（仅本机证据：`experiments/feature_validation/F03_evidence_verification/results/formal_v1/B02/result.json`；不随 Git 分发） |
| B03 | local_patch | `[3]` | 未运行 | 未运行 | 无法核验 | B03证据（仅本机证据：`experiments/feature_validation/F03_evidence_verification/results/formal_v1/B03/result.json`；不随 Git 分发） |
| C01 | original | `[[-3]]` | -3 | -3 | 支持 | C01证据（仅本机证据：`experiments/feature_validation/F03_evidence_verification/results/formal_v1/C01/result.json`；不随 Git 分发） |
| C02 | original | `[[-3, 0]]` | 0 | 0 | 支持 | C02证据（仅本机证据：`experiments/feature_validation/F03_evidence_verification/results/formal_v1/C02/result.json`；不随 Git 分发） |
| C03 | original | `[[-5, -2]]` | -2 | -2 | 无法核验 | C03证据（仅本机证据：`experiments/feature_validation/F03_evidence_verification/results/formal_v1/C03/result.json`；不随 Git 分发） |

A 是边界错误。预测输出 3 可以成立，同时它不满足应输出 6 的题意。A03 的学生理解不由运行决定。

B 使用以前审核过的局部修改：n=1 返回 1，满足该输入；n=3 返回 8，而参考为 6。完整修复陈述被合法反例反驳。B03 引用原版输出 5，但要求核验局部版，执行前拦截，不把旧预测误判为该版本的错误输出。原版和局部版源码哈希不同。

C 含可疑的 `best=0`，但另有全负数处理。三个执行输入均与参考相符，模块未报告 bug；这些有限执行仍不足以确认整个输入域或唯一原因。

## 分母与来源

| 指标 | 实际计数与分母 |
|---|---|
| 可执行谓词得到明确判定 | 6/9 核验；其中支持 4/6，反驳 2/6 |
| 错误支持或错误反驳 | 0/6，按冻结显式谓词与实际执行核对 |
| 无法核验 | 3/9：学生理解、版本冲突、整体正确性陈述各 1 |
| 版本冲突拦截 | 1/9 |
| 非法输入拦截 | 正式主测试 0/9；守卫回归 4/4 非法输入 |
| 实际执行 | 8/9，成功 8/8，异常 0/8 |
| 其他冻结预期是否满足 | 9/9；不把此数当作教学准确率 |

历史真实 AI 的四条明确输出预测均获支持。两个反驳分别是作者人工负例和 AI 引用的模拟学生“完全修好”陈述，**不能报告为两条真实 AI 错误诊断**。历史 AI 的另外三条被保留为无法核验。本轮没有从选定原文中发现可用的错误数值预测，故明确使用作者负例验证反驳功能。

自然语言到结构化谓词的转换由作者明确标注，并有以下原文供人工复核；程序自动验证的是转换后的命题，不是任意自然语言语义。没有独立人类语义认证。

- A01：“E3 显示实际返回 3，而题目要求返回 6。”。来源：[decision_basis](<../../../../experiments/feature_validation/F02_dynamic_questioning/responses/S1_C01_FIRST/raw_response.json>)。
- A02：“原版solve(3)返回6。”。来源：作者负例，非模型输出。
- A03：“尚不清楚学生如何理解 range 的终点边界。”。来源：[uncertainties/0](<../../../../experiments/feature_validation/F02_dynamic_questioning/responses/S1_C01_FIRST/raw_response.json>)。
- B01：“local_patch 在 n=1 时通过”。来源：[student_message](<../../../../experiments/feature_validation/F02_dynamic_questioning/responses/S1_C03_wrong_T2/raw_response.json>)。
- B02：“局部改动版在n=1通过，说明它已经修好了，其它返回部分不用看。”。来源：[answer_quotes/0](<../../../../experiments/feature_validation/F02_dynamic_questioning/responses/S1_C03_wrong_T2/raw_response.json>)；模型引用的冻结模拟学生话语，不是模型自己的结论。
- B03：“原版的 5”。来源：[student_message](<../../../../experiments/feature_validation/F02_dynamic_questioning/responses/S1_C03_unexpected_T2/raw_response.json>)。
- C01：“预测`solve([-3])`返回`-3`”。来源：[历史原文](<../../../../experiments/round5_ui_model/responses/generation_v4/S2_05.md>)。
- C02：“`solve([-3,0])`返回`0`”。来源：[历史原文](<../../../../experiments/round5_ui_model/responses/generation_v4/S2_05.md>)。
- C03：“未发现符合题目输入前提的正确性错误”。来源：[历史原文](<../../../../experiments/round5_ui_model/responses/generation_v4/S1_05.md>)。

## 受控执行与记录

复用既有 `experiments.runner.execute`、输入合同与独立 `common.oracle`。正式执行为 Python 3.12.10 / Windows。8/8 执行包报告 1.5 秒、8192 字节、128 MiB 内存限制已建立，Windows Job 活动进程限制 1。本次执行成功项含哈希校验的接口耗时 53.385～57.211 ms，中位数 54.611 ms；不据此宣称任意程序的延迟稳定性。

每项保存请求、实际源码及哈希、实际执行器返回包、参考来源、原文及其来源哈希、核验状态和证据路径。版本冲突项保留请求与失败记录，没有执行结果。未公开的底层进程 stderr 不被冒称为完整原始字节日志。

采用白名单审核代码；Job、AST 限制与超时不构成针对恶意代码的文件/网络隔离，不能执行任意用户或 AI 新代码。当前结果可信范围限于已审核版本、合法输入与已审核参考合同。

## 必要修复与确定性回归

首次冻结准备因旧清单的反斜杠路径发生 KeyError，正式主测试尚未开始。修复为两侧路径统一，且只允许空目录恢复；未改动案例或历史结果。见 prepare_failure_01.log（仅本机证据：`experiments/feature_validation/F03_evidence_verification/results/prepare_failure_01.log`；不随 Git 分发）。实现前红测试失败保留在 tests_red.log（仅本机证据：`experiments/feature_validation/F03_evidence_verification/results/tests_red.log`；不随 Git 分发）。正式主测试未出现需要重跑的客观核验错误。

回归 **9/9 测试方法通过**，产生 17 条独立核验记录、7 次实际执行，另验证一次拒绝覆盖：非法输入 4 条，未知版本/哈希/陈述版本冲突各 1 条；参考冲突 1 条、放宽限制 2 条均在执行前拦截。三个既有守卫夹具实际触发 timeout、IndexError、output_limit，各 1 次；全部保留包和失败日志，均不支持或反驳输出预测。bool 预测不被当作整数 0；单个局部修改通过仍保持整体正确性待定。

见 regression_command.log（仅本机证据：`experiments/feature_validation/F03_evidence_verification/results/regression_command.log`；不随 Git 分发）、回归归档索引（仅本机证据：`experiments/feature_validation/F03_evidence_verification/results/regression_v1/archived_path_map.json`；不随 Git 分发）。归档包保持临时路径原文，索引提供当前存储位置与哈希。

CLI 从项目目录外实际运行成功，证据路径均存在；见 cli_smoke_status.json（仅本机证据：`experiments/feature_validation/F03_evidence_verification/results/cli_smoke_status.json`；不随 Git 分发）。此单次接口冒烟检查不混入正式九项分母。没有重采样、替换失败样本或追加教学案例。

汇总和完整命令见 summary.json（仅本机证据：`experiments/feature_validation/F03_evidence_verification/results/formal_v1/summary.json`；不随 Git 分发）、formal_command.log（仅本机证据：`experiments/feature_validation/F03_evidence_verification/results/formal_command.log`；不随 Git 分发）。是否保留功能见 [F03_next_step_decision.md](<F03_next_step_decision.md>)。
