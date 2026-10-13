> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# 工程与调用核验

| 检查 | 结果 |
| --- | --- |
| 正式S1首份输出 | 12/12 |
| 输出结构/原话/引用通过 | 36/36 |
| 合法执行请求 | N/A：无新执行请求 |
| 结构化数值预测正确 | N/A：未给结构化预测，不记成零分 |
| 数值预测错误 | 0 |
| 原程序事实网格 | 18 |
| 额外模型调用 | 1独立出题 + 4预选辅助审查 |
| 请求模型/思考 | gpt-6.1-sol/high |
| OS读取隔离 | 未建立 |
| 同模型独立人类认证 | 否 |

每次全新ephemeral exec、不resume；只给prompt/schema，不提供规则、私有参考、旧评分或主对话。工具关闭，已知Skills显式禁用，本地渲染无Skills目录，但启动扫描仍可能有YAML警告；真实服务器上下文未被独立证明。事件流及原始最后消息逐字节保存。禁止模型代码执行；合法建议仅执行冻结原源码和独立oracle。

另对作者选取的自然语言数值前提核验：5/5；-5<-2关系单独正确；bool标量、bool元素、空列表三个不合法输入检查正确拒绝且未执行。不涵盖全部自然语言，也不能核对未提交源码的新版本。

GEN沿用通用运输器，原metadata的data_origin默认辅助审查不准确；metadata_corrected.json与purpose.json明确其实际为独立会话创作模拟输入，保留原metadata及原字节未覆盖。

匿名视图仅删除S0+显式版本前缀；仍可能从固定话术/规则措辞猜实现，匿名不等于完全盲。私有映射没有提供给评审，但OS拒读未建立。

最终文件/会话校验（仅本机证据：`experiments/feature_validation/F01_response_adaptation/final_acceptance/results/package_verification.json`；不随 Git 分发），完整实际输出核验（仅本机证据：`experiments/feature_validation/F01_response_adaptation/final_acceptance/results/actual_output_checks.json`；不随 Git 分发），正式教师延迟与token（仅本机证据：`experiments/feature_validation/F01_response_adaptation/final_acceptance/results/runtime_summary.json`；不随 Git 分发）。

总调用用量（1出题+12教师+4辅助，不含本研究主对话）：{'input_tokens': 156804, 'cached_input_tokens': 27648, 'cache_write_input_tokens': 0, 'output_tokens': 23544, 'reasoning_output_tokens': 9009}；调用耗时之和2730.13秒，不等于并行墙钟时间。缓存/推理token是官方usage中的子字段，不重复相加。货币成本无法分摊。独立线程17，与扫描到的66个历史线程ID无交集；历史文件1706个摘要不变。
