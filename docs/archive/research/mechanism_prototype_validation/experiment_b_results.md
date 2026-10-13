> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# 实验 B：可信错因核验的真实执行与覆盖代价

日期：2026-10-08。Python 3.12.10／Windows，本轮仅实现机制实验。真实模型实验 `not_run`，未检测到当前进程的 Provider 环境配置；实际 API 调用、token 和费用均为 0。没有访问私有凭据，也没有生成参赛产品、UI、Fork 或部署。

**结论：有限核验器可运行；相对 B1 能过滤注入错误，但追加执行的诊断增量尚未成立。** B2 接受 9 个有效原因、覆盖 9/10 个错误程序；B1 放行的 4 个错误原因均未获 B2 支持。事后 AST 对照也达到 0 个错误原因、9/10 覆盖，且覆盖更多真实原因。因此不能把本轮结果概括为“执行反证使 AI 更准确”。

程序错误标签、固定诊断、学习事件及题包均由本助手按源码和自拟题意编写，**不是外部人类独立标注、真实学生数据或真实模型输出**。独立参考指预先固定、不取自候选答案的函数规范 oracle；尚未经过第二名专家复核。

## 1. 冻结、对照与可信边界

原协议和 15 程序／24 断言先冻结于 [frozen_manifest.json](<../../../../experiments/data/frozen_manifest.json>)。首次 B 结果保留于 原始 v1 结果（仅本机证据：`experiments/results/B_20261008T145025027028Z_912bf9/summary.json`；不随 Git 分发）。b09 原本意在表达前提不足，却因初值替换后仍从 xs[1:] 遍历，使 `[3,2]` 实测为 2、参考为 3。这是样本设计错误。原始结果不用于支持该场景。

按 公开修订说明（仅本机证据：`experiments/PROTOCOL_AMENDMENT_B_V2.md`；不随 Git 分发） 只把 b09 遍历改为 xs，并更新 h16 的代码哈希；其他案例、输入、标签和规则不变，新文件重新冻结后才重跑。v1 的 B1 曾接受 18 条，v2 为 17 条；B0/B2 的关键计数未变。

最终复核又发现 b09 题面沿用“允许全负数”，与 unknown_sign 矛盾。按 第二次公开修订（仅本机证据：`experiments/PROTOCOL_AMENDMENT_B_V3.md`；不随 Git 分发） 仅更正该题面为负数前提尚未说明、h16 下一步为澄清前提；源码、输入、标签和算法不变。v3 先重新冻结再重跑 B 与 AST 对照，计数与 v2 相同。前提不足结论仅采用 v3。两次修订均保留原文件和结果，不能称零修订的预注册研究。

B0：接受同一组固定候选，近似没有核验器的自由分析输出。B1：结构、执行事实、引用、版本检查；已有失败才允许原因输出。B2：同一候选增加合法 probe、真实行为预测验证及局部 AST 单缺陷干预，干预须修复至少一个已观察失败且不破坏已通过用例。所有事实输入一致，追加执行预算不同并单列。这些是本地规则近似，没有启动 SmartCode/Iris，更没有真实模型三组对照。

支持状态仅为 `supported_local`：这个局部机制在选定输入上有贡献性证据，不证明全域正确、根因唯一、程序已完全修好或学习者不懂该概念。`refuted` 指当前具体断言和预测冲突；坏引用或非法 probe 拒绝的是该证据包，不证明真实原因不存在。

## 2. 全部初始实测输入输出

| 案例 | 规范 | 实际调用参数 | 可信预期 | 实际值／异常 | 预设程序标签 | 覆盖目的 |
| --- | --- | --- | --- | --- | --- | --- |
| b01 | max | [[[-5,-2]],[[2,9]]] | [-2,9] | [0,9] | ["init_zero"] | 全负数初值缺陷，正确原因及无依据原因／认知断言 |
| b02 | inclusive_sum | [[3],[1]] | [6,1] | [3,0] | ["loop_end_excluded"] | n=3 与覆盖程序同为 3；用 n=4 区分；坏引用攻击 |
| b03 | inclusive_sum | [[3],[1]] | [6,1] | [3,1] | ["accumulator_overwrite"] | 同症状异因：覆盖累加器 |
| b04 | copy_items | [[[2]],[[]]] | [[2],[]] | ["IndexError: list index out of range","IndexError: list index out of range"] | ["index_off_by_one"] | 合法输入下 IndexError 与修复对照 |
| b05 | inclusive_sum | [[3],[1]] | [6,1] | [2,0] | ["loop_end_excluded","accumulator_overwrite"] | 多个缺陷；单干预可被其他缺陷遮蔽 |
| b06 | max | [[[-5,-2]],[[2,9]]] | [-2,9] | [-2,9] | 正确 | 正确极值程序被误诊 |
| b07 | inclusive_sum | [[0],[4]] | [0,10] | [0,10] | 正确 | 正确 inclusive 循环被误诊 |
| b08 | copy_items | [[[]],[[1,2]]] | [[],[1,2]] | [[],[1,2]] | 正确 | 正确程序＋不存在的证据 |
| b09 | max | [[[1,5]],[[3,2]]] | [5,3] | [5,3] | 前提不明 | 仅非负观察，负数前提未说明；不能唯一确定错误 |
| b10 | max | [[[-5,-2]],[[2,9]]] | [-2,9] | [0,9] | ["init_zero"] | 同类真实缺陷但不在核验器 AST 模板覆盖内 |
| b11 | min | [[[2,7]],[[-3,-1]]] | [2,-3] | [0,-1] | ["init_zero"] | 最小值的范围假设与非法空输入 |
| b12 | sum_items | [[[1,2,3]],[[]]] | [6,0] | [3,0] | ["accumulator_overwrite"] | 列表累计被覆盖，允许空列表 |
| b13 | inclusive_sum | [[0],[3]] | [0,6] | [0,3] | ["loop_end_excluded"] | 从零开始的等价循环，不能只按代码字符串匹配 |
| b14 | copy_items | [[[]],[[1,2]]] | [[],[1,2]] | [[],"IndexError: list index out of range"] | ["index_off_by_one"] | 空输入通过、非空越界；不可把正确症状当根因 |
| b15 | sum_items | [[[1]],[[1,2]],[[]]] | [1,3,0] | [1,3,0] | 正确 | 正确 builtin sum 被当作覆盖累加器 |

所有源码、前提和禁止结论见 [b_cases_v3.json](<../../../../experiments/data/b_cases_v3.json>)；31 次初始函数执行的状态、输入、版本、耗时、资源设置见 raw_evidence.json（仅本机证据：`experiments/results/B_20261008T152444211466Z_482758/raw_evidence.json`；不随 Git 分发）。b01 和 b09 源码／前提不同；b02/b03 在 n=3 都输出 3，但 n=1 已不同，新增 n=4 也能区分。不能说该组必须追加 probe 才能区分。

## 3. 原始计数与有效覆盖

| 指标 | B0 固定输出 | B1 基础核验 | B2 执行核验 | B_syntax 事后探索 |
| --- | --- | --- | --- | --- |
| 输出获接受 | 24 | 17 | 9 | 10 |
| 其中正确程序原因（可含重复） | 14 | 12 | 9 | 10 |
| 错误程序原因断言 | 8 | 4 | 0 | 0 |
| 无证据的学习者断言 | 1 | 1 | 0 | 0 |
| 前提不足却输出 | 1 | 0 | 0 | 0 |
| 正确程序误报／4 | 4 | 0 | 0 | 0 |
| 覆盖错误程序／10 | 10 | 10 | 9 | 9 |
| 覆盖不同真实原因／11 | 11 | 11 | 9 | 10 |
| 未接受／24 | 0 | 7 | 15 | 14 |
| 预测经实际执行符合 | 0 | 0 | 13 | 0 |
| 预测符合但原因未获支持 | 0 | 0 | 4 | 0 |
| 有效行为反证 | 0 | 0 | 5 | 0 |
| 追加函数执行 | 0 | 0 | 48 | 0 |
| 追加子进程批次 | 0 | 0 | 28 | 0 |
| 核验总毫秒 | 0.053 | 0.163 | 1704.404 | 5.941 |

B2 未接受 15/24（62.5%）：5 待定、5 预测反证、2 坏引用、1 旧版本、2 非法 probe。B1 为 7/24（29.2%）。可判定的程序原因断言正确比例为 B0 14/22、B1 12/16、B2 9/9；它们是刻意注入的固定断言计数，不能估计真实模型准确率。

程序覆盖从 B1 的 10/10 降至 B2 的 9/10；真实原因覆盖从 11/11 降至 9/11。正确程序误报 B1 已为 0，B2 没有此项新增收益。3 个坏／旧引用 B0 全放行，B1/B2 全拒绝，这项收益归基础引用检查。初始共享执行 31 次／15 批，B2 追加 48 次／28 批，合计 79 次／43 批；延迟含 Python 子进程启动，单次本机测量不作性能基准。所有模型调用为 0。

## 4. 每条断言的核验结果

| 案例／断言 | 声明原因及层次 | probe 参数及预测 | B1 | B2 | B2 的理由 |
| --- | --- | --- | --- | --- | --- |
| b01/h01 | program: init_zero | [[[-4,-1]],{"status":"ok","value":0}] | accepted_unverified | supported_local | single local intervention fixes observed failures without observed regression |
| b01/h02 | program: comparison_reversed | [[[-4,-1]],{"status":"ok","value":0}] | accepted_unverified | inconclusive | matching symptoms without a supported local mechanism |
| b01/h03 | learner: does_not_understand_invariants | [[[-4,-1]],{"status":"ok","value":0}] | accepted_unverified | inconclusive | program behavior does not verify learner understanding |
| b02/h04 | program: loop_end_excluded | [[4],{"status":"ok","value":6}] | accepted_unverified | supported_local | single local intervention fixes observed failures without observed regression |
| b02/h05 | program: accumulator_overwrite | [[4],{"status":"ok","value":4}] | accepted_unverified | refuted | real program behavior contradicts the hypothesis prediction |
| b02/h06 | program: loop_end_excluded | [[4],{"status":"ok","value":6}] | invalid_reference | invalid_reference | citation or version check |
| b02/h07 | program: loop_end_excluded | [[4],{"status":"ok","value":6}] | stale | stale | citation or version check |
| b03/h08 | program: accumulator_overwrite | [[4],{"status":"ok","value":4}] | accepted_unverified | supported_local | single local intervention fixes observed failures without observed regression |
| b03/h09 | program: loop_end_excluded | [[4],{"status":"ok","value":6}] | accepted_unverified | refuted | real program behavior contradicts the hypothesis prediction |
| b04/h10 | program: index_off_by_one | [[[-1,4]],{"status":"runtime_error","error_type":"IndexError"}] | accepted_unverified | supported_local | single local intervention fixes observed failures without observed regression |
| b05/h11 | program: loop_end_excluded | [[4],{"status":"ok","value":3}] | accepted_unverified | supported_local | single local intervention fixes observed failures without observed regression |
| b05/h12 | program: accumulator_overwrite | [[4],{"status":"ok","value":3}] | accepted_unverified | inconclusive | intervention is masked, unnecessary, or regresses tested behavior |
| b06/h13 | program: init_zero | [[[-9,-2]],{"status":"ok","value":0}] | inconclusive | refuted | real program behavior contradicts the hypothesis prediction |
| b07/h14 | program: loop_end_excluded | [[4],{"status":"ok","value":6}] | inconclusive | refuted | real program behavior contradicts the hypothesis prediction |
| b08/h15 | program: index_off_by_one | [[[2]],{"status":"runtime_error","error_type":"IndexError"}] | invalid_reference | invalid_reference | citation or version check |
| b09/h16 | program: init_zero | [[[-2,-1]],{"status":"ok","value":0}] | inconclusive | invalid_probe | negative input eligibility not specified |
| b10/h17 | program: init_zero | [[[-4,-1]],{"status":"ok","value":0}] | accepted_unverified | inconclusive | matching symptoms without a supported local mechanism |
| b11/h18 | program: init_zero | [[[4,9]],{"status":"ok","value":0}] | accepted_unverified | supported_local | single local intervention fixes observed failures without observed regression |
| b11/h19 | program: init_zero | [[[]],{"status":"runtime_error","error_type":"IndexError"}] | accepted_unverified | invalid_probe | nonempty list required |
| b12/h20 | program: accumulator_overwrite | [[[-2,4]],{"status":"ok","value":4}] | accepted_unverified | supported_local | single local intervention fixes observed failures without observed regression |
| b13/h21 | program: loop_end_excluded | [[4],{"status":"ok","value":6}] | accepted_unverified | supported_local | single local intervention fixes observed failures without observed regression |
| b14/h22 | program: index_off_by_one | [[[3]],{"status":"runtime_error","error_type":"IndexError"}] | accepted_unverified | supported_local | single local intervention fixes observed failures without observed regression |
| b14/h23 | program: empty_input_unsupported | [[[]],{"status":"ok","value":[]}] | accepted_unverified | inconclusive | matching symptoms without a supported local mechanism |
| b15/h24 | program: accumulator_overwrite | [[[1,2]],{"status":"ok","value":2}] | inconclusive | refuted | real program behavior contradicts the hypothesis prediction |

所有 probe 实测、干预前后、源码和失败均见 comparisons.json（仅本机证据：`experiments/results/B_20261008T152444211466Z_482758/comparisons.json`；不随 Git 分发）、failures.json（仅本机证据：`experiments/results/B_20261008T152444211466Z_482758/failures.json`；不随 Git 分发）；固定输出的原文与 provenance 见 [b_claims_v3.json](<../../../../experiments/data/b_claims_v3.json>)。

h02、h17、h23 的行为预测确实符合，但没有对应可核验机制；h12 的真实覆盖缺陷被端点缺陷遮蔽，单独修累加未使当前用例通过，因此保持待定。h11 只修复其中一个观察，不代表多缺陷程序全部恢复。h17 的 `max([0]+xs)` 是真实缺陷，但当前 AST 模板无法支持它；这是覆盖限制。h19 的空输入不符合 min 题前提，不能拿它充当根因反证。

## 5. 事后简单对照改变了创新解释

事后对照定义（仅本机证据：`experiments/B_POSTHOC_SENSITIVITY.md`；不随 Git 分发） 在执行前记录哈希，数据不变。B_syntax 只要求 B1 合格、程序层、合法 probe 和 AST 机制存在，不执行预测或修复。它接受 10 个正确原因、0 个错误原因，覆盖 9/10 程序和 10/11 真实原因；仅增加约 5.941ms 规则处理，追加执行为 0。

该探索不是预注册主比较，不提供与 B2 同等的执行证据。但在当前标签筛选指标上，B2 没有超越它，且多漏掉 h12。四个 B1 错误解释都可由简单模板过滤挡住。额外执行可以产出真实可回放证据，当前样本未证明用户需要这份证据、也未证明它比简单 AST 规则提高自然诊断可靠性。

## 6. 工程验证、复现与决定

运行器事实检查见 runner_checks.json（仅本机证据：`experiments/results/runner_checks.json`；不随 Git 分发）：正常值、IndexError、禁 import、超时、输出限长、真实内存分配受限分别得到 ok/runtime_error/rejected_source/timeout/output_limit/resource_limit。原先 MemoryError 被归为 runtime_error，已保存失败测试后修正，再重跑全部比较。最终回归另发现 B1/B2 可能把混合证据中的资源失败计为可修复错误，已用注入资源状态的失败测试复现，再把初始失败／干预改善限定为合法且实际可判定的程序结果，重跑 B 与 AST 对照后计数未变。Windows 设置进程数 1、128MiB 提交内存；每批 1.5s 超时、值输出 8192 字节，使用可信启动器和仅已审阅的固定函数／AST 变体。Job Object 设置依据 [Microsoft 扩展限制结构](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)。没有攻击审计，不能开放执行任意模型代码。

核验器不读 gold 标签或 case ID 查表；评分模块另读标签。支持的四类有限语法并不构成任意因果推理。没有模型自动提出新区分输入，没有自然语言因果自动证明，也没有真实学习者认知判定。

```powershell
python -m experiments.run_b
python -m experiments.run_b --data-version v1
python -m experiments.run_b_sensitivity
python -m unittest discover -s experiments/tests -v
```

**B：CONDITIONAL GO。** 可作为独立、受限的证据回放组件继续验证，尚不作为已证明创新的高可信诊断产品。下一轮必须加入 AST 存在却解释错误、补偿性干预、组合缺陷和模板外写法，并与 B_syntax 同模型、同事实对照；若追加执行仍无诊断或用户信任收益，应采用更简单规则。

主要结果：summary.json（仅本机证据：`experiments/results/B_20261008T152444211466Z_482758/summary.json`；不随 Git 分发）；事后结果：summary.json（仅本机证据：`experiments/results/B_sensitivity_20261008T152447176719Z_a4bf0c/summary.json`；不随 Git 分发）。成熟机制出处沿用第二轮固定源码证据：[SmartCode 的执行事实覆盖](https://github.com/mohddarwix/SmartCode/blob/8b7a3e56bb64067ded83bf7ebd0a1e93ba65d70d/backend/app/llm/submission_evaluator.py)、[Iris 的快照锚点检查](https://github.com/ls1intum/edutelligence/blob/4065add4b76b2edd283f35e31d5ac620f477077e/iris/src/iris/pipeline/struggle_intervention_pipeline.py)。
