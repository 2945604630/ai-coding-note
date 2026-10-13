> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# F02 守卫失败与修复

三次原阻断均由程序守卫错误地要求新增execution_requests导致。它们不是非法测试、学生代码异常或模型预测被执行器证伪。原学生代码的缺陷属于案例事实；阻断根因另属验证协议。

| 原始阻断 | 可信版本/输入 | 真实核对结果 | 根因与分类 |
| --- | --- | --- | --- |
| S1_C01_wrong_T2 | original n=1 | 实际0 / 预期1 | 唯一阻断missing_counterexample；已引用事实但新请求为空，协议误拦截 |
| S1_C02_wrong_T3 | original n=3 | 实际2 / 预期6 | 唯一阻断missing_counterexample；已引用事实但新请求为空，协议误拦截 |
| S1_C03_wrong_T2 | local_patch n=1；local_patch n=3 | 实际1 / 预期1；实际8 / 预期6 | 唯一阻断missing_counterexample；已引用事实但新请求为空，协议误拦截 |

逐项首次原文：

- S1_C01_wrong_T2：“看一个更小的边界：n=1 时，s 初始为0。如果右端点1会进入循环，最终应返回多少？但 E2 记录的实际返回值是0。根据这个反例，你会怎样调整对 range 右端点的判断？”
- S1_C02_wrong_T3：“已有执行事实显示：原版代码在 n=3 时返回 2，不是 3。循环中 i 依次为 1、2，第一轮后 s=1。请把第二轮 `s=i` 右边的 `i` 换成当轮数值，写出这次赋值：上一轮的 `s=1` 有没有参与右边的计算？这能否解释实际返回的 2？”
- S1_C03_wrong_T2：“已有执行记录显示：local_patch 在 n=1 时通过，但在 n=3 时返回 8，题目要求 6。请比较这两个输入：return 中的 + n - 1 分别是多少？为什么 n=1 的通过不能排除返回部分有问题？”

旧冻结v1在show_counterexample且请求列表为空时必然阻断，即使引用了已经审核过的反例。此前v2运行守卫确实能独立重放三份原回答引用的事实，本轮重新核对3/3通过。因此早先修复解决了这三项具体误拦截，但没有补齐原先被截断的学生路径，也没有解决评审历史污染或所有输入形态。

本轮在归档v2中另复现两项工程缺陷：evidence_refs包含非字符串字典会触发TypeError；一句同时提n=1/n=8但只引用n=1事实会被v2放行。v3在调用冻结验证器前检查数组元素与请求类型，并要求所有显式n值均由引用事实的实际重放覆盖。非法输入、布尔值、未知代码版本、错误预测、虚构引用、非最新学生原文引用仍然阻断。具体复现记录：summary.json（仅本机证据：`experiments/feature_validation/F02_dynamic_questioning/validation_repair/checks/20261010T144116541394Z/summary.json`；不随 Git 分发）；三份原回答的v3核验：guard_replay_v3.json（仅本机证据：`experiments/feature_validation/F02_dynamic_questioning/validation_repair/checks/20261010T144116541394Z/guard_replay_v3.json`；不随 Git 分发）。

v3的public_evidence_replays注明runtime_replay_of_public_ref_not_new_model_request。只重放已审核原版/local_patch，不执行模型新代码，也不执行用户尚未审核的新代码。程序原码哈希、输入合法性、实际输出与独立oracle都校验后才展示相应执行事实。

自然语言中的因果、意图、数值绑定与跨版本措辞没有可靠的全自动证明，semantic_truth_certified始终false。display_safe仅表示通过结构、引用和受控执行检查；可能出现模型把真实证据解释错，不能用放行当作教学评分。新CLI把每个证据的source_version、代码与证据哈希一并记录、展示；未经提供/核验的新代码不自动继承旧版事实。

输入层另有两个问题：C03_partial的回应与local_patch前问版本不匹配；C02_wrong没有回答s=5/i=2的假设状态。C03_wrong若放行，其双输入问题仍不适配冻结模拟器。上述问题不修改gold、不补答、不重采样。原invalid_output仍保留3条，修复后3/3可展示是单步离线工程结果，不是3条路径重新成功。

空回答、截断、超时或连接失败保留原字节/日志并记model_call_failed；可解析但不通过守卫的回答记guard_blocked。运行异常与教学判断异常不再合并为同一成功/失败百分比。
