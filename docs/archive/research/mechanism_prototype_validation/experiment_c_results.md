> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# 实验 C：独立题包质量检查与强基线消融

日期：2026-10-08。Python 3.12.10／Windows，本轮仅实现机制实验。真实模型实验 `not_run`，未检测到当前进程的 Provider 环境配置；实际 API 调用、token 和费用均为 0。没有访问私有凭据，也没有生成参赛产品、UI、Fork 或部署。

**结论：质量闸门真实运行，但目标错误检查未体现超越通用变异测试的增量。** C2 相对 C1 额外挡住 c09/c12/c13，分别依赖独立参考、概念审核、缺失审核；目标检查拦下的四个弱测试题，C1 已全部拦下。保留一个合格题误拒。

程序错误标签、固定诊断、学习事件及题包均由本助手按源码和自拟题意编写，**不是外部人类独立标注、真实学生数据或真实模型输出**。独立参考指预先固定、不取自候选答案的函数规范 oracle；尚未经过第二名专家复核。

## 1. 独立候选与公平对照

C 不读取 A 的状态、学习者历史或 B 的诊断；独立入口接收 14 个冻结题包，覆盖 4 个语义合格题、4 个弱测试、2 个参考和测试共错、2 个偏题、1 个缺审核、1 个坏参考。“不应放行”10 个中有 9 个已知缺陷、1 个待审核；缺审核本身不证明内容错误。

C0 检查结构、合法输入、参考通过当前测试、starter 所有用例失败。C1 在此基础上执行通用 AST 常数、比较、二元运算、range 端点、累加→覆盖和下标替换，未人为删掉目标变异。先在有限 witness 与候选参考比较，非等价者全部被当前测试检出才接受；合法输入上参考异常也拒绝。这是严格有限基线，非完整 EvalPlus 或 mutmut 复现。

C2 在 C0 后检查独立 oracle、测试期望、预置概念审核和指定目标变体；没有暗中再加 C1。C2_without_target 去除目标检查，其他相同。每组预算单列，另行执行的全题包测量 audit 不反馈给 C0/C1。

参考实现使用 max/min、整数求和公式、sum 或 list 的预设规范；C 本次只有 max/inclusive_sum/sum_items/copy_items 四类任务。不能自动把任意自然生成题映射到可信 oracle，题意、输入约束与参考的建立仍有人工成本。

## 2. 全部题包结果

| 题包 | 预设性质 | C0 | C1 | C2 | 去目标消融 | 当前测试检出目标 | 独立参考冲突 | C2 判定理由 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| c01 | good | 拒绝 | 拒绝 | 拒绝 | 拒绝 | True | False | starter_already_passes |
| c02 | good | 接受 | 接受 | 接受 | 接受 | True | False | target_killed |
| c03 | good | 接受 | 接受 | 接受 | 接受 | True | False | target_killed |
| c04 | good | 接受 | 接受 | 接受 | 接受 | True | False | target_killed |
| c05 | weak_tests | 接受 | 拒绝 | 拒绝 | 接受 | False | False | target_survives |
| c06 | weak_tests | 接受 | 拒绝 | 拒绝 | 接受 | False | False | target_survives |
| c07 | weak_tests | 接受 | 拒绝 | 拒绝 | 接受 | False | False | target_survives |
| c08 | weak_tests | 接受 | 拒绝 | 拒绝 | 接受 | False | False | target_survives |
| c09 | shared_wrong | 接受 | 接受 | 拒绝 | 拒绝 | False | True | independent_reference_conflict |
| c10 | shared_wrong | 接受 | 拒绝 | 拒绝 | 拒绝 | False | True | independent_reference_conflict |
| c11 | off_concept | 拒绝 | 拒绝 | 拒绝 | 拒绝 | True | False | starter_already_passes |
| c12 | off_concept | 接受 | 接受 | 拒绝 | 拒绝 | True | False | off_concept |
| c13 | review_missing | 接受 | 接受 | 拒绝 | 拒绝 | True | False | missing_review |
| c14 | bad_reference | 拒绝 | 拒绝 | 拒绝 | 拒绝 | True | True | basic_reference_mismatch |

完整题面、源码、声明测试、witness、目标变体和审核夹具见 [c_packs.json](<../../../../experiments/data/c_packs.json>)；实际每个参考／starter／通用变体／目标执行见 comparisons.json（仅本机证据：`experiments/results/C_20261008T150856779211Z_96198f/comparisons.json`；不随 Git 分发）；独立测量见 independent_audit.json（仅本机证据：`experiments/results/C_20261008T150856779211Z_96198f/independent_audit.json`；不随 Git 分发）。所有失败和未执行检查也保留，没有仅展示成功题。

## 3. 计数与成本

| 指标 | C0 | C1 | C2 | C2_without_target |
| --- | --- | --- | --- | --- |
| 接受题包 | 11 | 6 | 3 | 7 |
| 合格题接受／4 | 3 | 3 | 3 | 3 |
| 合格题误拒／4 | 1 | 1 | 1 | 1 |
| 不应放行却漏放／10 | 8 | 3 | 0 | 4 |
| 其中已知缺陷漏放／9 | 7 | 2 | 0 | 4 |
| 其中缺审核仍放行／1 | 1 | 1 | 0 | 0 |
| 偏题漏放／2 | 1 | 1 | 0 | 0 |
| 共同错误漏放／2 | 2 | 1 | 0 | 0 |
| 放行包中目标错误仍存活 | 6 | 1 | 0 | 4 |
| 实际函数求值次数 | 84 | 343 | 158 | 128 |
| 实际进程批次 | 28 | 89 | 46 | 39 |
| 本机总毫秒 | 1498.721 | 4702.877 | 2433.232 | 2086.79 |
| 基础设施／限制失败 | 0 | 0 | 0 | 0 |

离线独立测量发现 3/14 个参考冲突（c09/c10/c14）、2/14 个测试期望冲突（c09/c10）。14 个指定目标变体在 witness 上都是真错误；现有测试仅检出 8/14（57.1%），其余 6 个存活。这个检出率属于原始题包测试集，不是 C2 自动改良后的质量。C2 实际执行目标检查 7 个：3 检出、4 存活；其余 7 个因先前闸门拒绝而 not_checked，不计为检出。

C2 放行 3 个题的目标均被检出；按仅放行题计算的 3/3 不能冒充全题包 100% 检出率。没有自动修复或补测试。离线 audit 另耗 122 次求值／28 批，未包含在四组门控成本中。各成本包含子进程开销，顺序运行且未做统计重复；不据约两倍延迟差宣称普遍性能优势。

## 4. 通用变异结果与消融解释

| 题包 | C1 通用变异计数 | 指定目标在通用变异中 | C1 原因 |
| --- | --- | --- | --- |
| c01 | 未进入变异阶段 | not_checked | starter_already_passes |
| c02 | {"killed":7,"survived":0,"witness_equivalent":1,"not_checked":0} | False | all_finite_non_equivalent_mutants_killed |
| c03 | {"killed":3,"survived":0,"witness_equivalent":0,"not_checked":0} | True | all_finite_non_equivalent_mutants_killed |
| c04 | {"killed":4,"survived":0,"witness_equivalent":0,"not_checked":0} | True | all_finite_non_equivalent_mutants_killed |
| c05 | {"killed":2,"survived":2,"witness_equivalent":2,"not_checked":0} | True | generic_mutant_survives |
| c06 | {"killed":2,"survived":5,"witness_equivalent":1,"not_checked":0} | False | generic_mutant_survives |
| c07 | {"killed":2,"survived":1,"witness_equivalent":0,"not_checked":0} | True | generic_mutant_survives |
| c08 | {"killed":2,"survived":2,"witness_equivalent":0,"not_checked":0} | True | generic_mutant_survives |
| c09 | {"killed":3,"survived":0,"witness_equivalent":0,"not_checked":0} | False | all_finite_non_equivalent_mutants_killed |
| c10 | 未进入变异阶段 | not_checked | reference_runtime_failure_on_valid_witness |
| c11 | 未进入变异阶段 | not_checked | starter_already_passes |
| c12 | {"killed":7,"survived":0,"witness_equivalent":1,"not_checked":0} | False | all_finite_non_equivalent_mutants_killed |
| c13 | {"killed":3,"survived":0,"witness_equivalent":0,"not_checked":0} | True | all_finite_non_equivalent_mutants_killed |
| c14 | 未进入变异阶段 | not_checked | basic_reference_mismatch |

有限 witness 等价只表示这些输入无法区分；不是证明全域等价。程序自身的 IndexError/TypeError 计为可被测试检出的错误行为，timeout/资源限制/运行设施失败单列，不能利用未能执行变体刷分。

c05–c08 的目标错误行为均被通用变异覆盖，C1 与 C2 均拒绝。c06 的指定变体未以完全相同 AST 出现，但通用 range_minus_one 和终点常数替换产生了在全部 witness 上行为相同的边界错误变体；表中的 False 是语法精确匹配结果，不表示该错误族没有被测试。消融去掉目标检查后漏放这 4 个，说明 C2 内部需要错误检出，但并未证明这一环节比通用变异更新颖或更有效。

C2 对 C1 的额外收益仅 3 个：c09 参考与测试一起少算 n，通用变异把该参考当 oracle 无法指出题意错误；独立公式指出 n=3 应为 6 而该参考为 3。c12 数学正确但目标概念偏离，靠预置审题拒绝；c13 没有审核记录，靠放行资格拒绝。c10 在空列表上参考本身异常，C1 已拒绝，不能将它算作 C2 的独立增量。

由已保存结果作逻辑合取，C1＋C2_without_target 将放行与 C2 相同的 c02/c03/c04；这是离线推导，未另行运行完整组合系统。因此当前目标模块可被成熟变异检查替代。仅查指定目标可减少执行候选数量，但是否漏掉其他坏题、是否降低教师总成本，尚无证据。

## 5. 误拒、审核和修复代价

c01 题意、参考和测试语义合格，却被全部方案拒绝：starter 固定返回 −1，在输入 `[-1]` 上恰好正确；被冻结的“starter 必须所有用例失败”规则过严。c11 同样在基础关被拒，不能把它算作概念审核的增量。数据及规则均未为改善指标修改。这次共有 1/4 合格题误拒（25%），不可隐藏。

C 测试初次曾错误预期 c11 能进入 C1，失败和调试原始结果均保留；查明 starter 偶然通过后，概念独立性测试改用既有 c12，新增 c01 误拒回归测试，没有替换正式样本。未来可选 starter 返回不属于答案域的值或允许 starter 部分通过，但应另注册规则后重测；本轮未修复题包以追求零误拒。

审核状态 approved_fixture 及概念一致布尔值均为作者预设，未安排教师审题，未测量审核或修复分钟数。误判减少有一部分是人工真值作为输入带来的收益，不能记为自动语义核验创新。真实模型生成题、生成成本、教师劳动、难度匹配、目标误解的真实发生率和练习效度均 not_run。

## 6. 复现与独立价值决定

```powershell
python -m experiments.run_c
python -m unittest experiments.tests.test_c -v
```

**C：NO-GO，指当前“创新型独立 AI 题工厂”选题。** 作为独立离线质量检查工具有工程用途，可以不依赖 A/B 运行；独立参考、防共错和审核留痕值得保留，但本次没有自然生成任务、教师需求或超越“通用变异＋独立参考＋审题”的新增机制证据。不因它是后台而降低要求，也不因 A/B 排名而否定其工程用途。

结果：summary.json（仅本机证据：`experiments/results/C_20261008T150856779211Z_96198f/summary.json`；不随 Git 分发）；拒绝日志：failures.json（仅本机证据：`experiments/results/C_20261008T150856779211Z_96198f/failures.json`；不随 Git 分发）。成熟基线来源沿用 [Artemis 的参考／template 校验](https://github.com/ls1intum/Artemis/blob/aafd3924cae763ba168ff3faa2e7681d0b662ef1/src/main/java/de/tum/cit/aet/artemis/hyperion/service/variants/ProgrammingVariantAdapterService.java)及 [EvalPlus 的程序变异流程](https://github.com/evalplus/evalplus/blob/26d6d00bb1fd0fa37f39c99d5290da67891d1c5e/tools/tsr/mutation_init.py)；本实验没有安装或调用它们。
