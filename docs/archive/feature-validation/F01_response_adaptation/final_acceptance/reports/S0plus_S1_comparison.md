> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# S0 / S0+ / S1 最终比较

全部学生回应为独立模型会话创作的模拟输入，不是真实学生。语义成绩是作者模型辅助初审；预选4例匿名同模型新会话辅助审查用于揭示分歧，独立人类复核0，真实学生效果0。全部needs_human_review。动作集合成员、JSON通过、程序数值正确均不能代替教学真值。

作者首次动作初审：

| 组 | 合理 | 错误 | 待定 | 无法评分 | 分母 |
| --- | --- | --- | --- | --- | --- |
| S0 | 0 | 12 | 0 | 0 | 12 |
| S0+ | 1 | 7 | 4 | 0 | 12 |
| S1 | 10 | 0 | 2 | 0 | 12 |

把辅助审查分歧保留待定的视图（未更改原分数）：

| 组 | 合理 | 错误 | 待定 | 无法评分 | 分母 |
| --- | --- | --- | --- | --- | --- |
| S0 | 0 | 12 | 0 | 0 | 12 |
| S0+ | 1 | 6 | 5 | 0 | 12 |
| S1 | 10 | 0 | 2 | 0 | 12 |

逐例（理解/动作来自作者初审）：

| 案例 | S0 理解/动作 | S0+ 理解/动作 | S1 理解/动作 | 冻结动作成员S0+/S1 |
| --- | --- | --- | --- | --- |
| T01 | error/error | correct/uncertain | correct/reasonable | True/True |
| T02 | error/error | error/error | correct/reasonable | False/True |
| T03 | error/error | error/error | correct/reasonable | False/True |
| T04 | error/error | error/error | correct/uncertain | False/False |
| T05 | error/error | correct/uncertain | correct/reasonable | True/True |
| T06 | error/error | uncertain/uncertain | correct/reasonable | True/True |
| T07 | error/error | correct/error | correct/reasonable | True/True |
| T08 | error/error | error/error | correct/reasonable | True/True |
| T09 | error/error | error/error | correct/reasonable | True/True |
| T10 | error/error | correct/reasonable | correct/uncertain | True/False |
| T11 | error/error | correct/uncertain | correct/reasonable | True/True |
| T12 | error/error | error/error | correct/reasonable | False/True |

各维度分别统计，分母每组12，不求综合百分比：

| 维度 | S0 首次标签计数 | S0+ 首次标签计数 | S1 首次标签计数 |
| --- | --- | --- | --- |
| understanding | {'error': 12} | {'correct': 5, 'error': 6, 'uncertain': 1} | {'correct': 12} |
| action | {'error': 12} | {'uncertain': 4, 'error': 7, 'reasonable': 1} | {'reasonable': 10, 'uncertain': 2} |
| omissions | {'present': 12} | {'present': 10, 'absent': 1, 'uncertain': 1} | {'absent': 10, 'uncertain': 1, 'present': 1} |
| knowledge_overreach | {'absent': 12} | {'absent': 12} | {'absent': 12} |
| program_contradiction | {'absent': 12} | {'absent': 12} | {'absent': 12} |
| repair_leak | {'0': 12} | {'0': 12} | {'1': 5, '0': 7} |
| version_match | {'matched': 10, 'uncertain': 2} | {'matched': 11, 'uncertain': 1} | {'matched': 12} |

相对本版本S0+从错误到合理、S1动作未被辅助评审提出不同标签的初审候选：T02, T03, T07, T08, T09, T12。这不是独立人类确认。包含S0+待定的较宽候选：T01, T02, T03, T05, T06, T07, T08, T09, T11, T12。

T04：原参考允许clarify_meaning/suspend_for_choice，但处理义务也允许明确暂缓新版判断。S1选择continue_asking并限定给定源码；可能合理却不在冻结集合。保留参考与输出原样，作者标待定；不能把成员失败直接宣布模型教学错误，也不能事后修改gold刷通过。

S0+不是全部可能规则的最优实现。词形覆盖不足如“动过”可用简单规则改善，但本次禁止事后改动；类型/契约澄清与版本收集设计单元例可由规则完成。对复杂否定、先前问题的语境、省略与比喻，有限规则经常继续泛化或重复追问。不能把未覆盖写成规则技术不可能实现。

S0保留历史函数，只消费case_id和回应。控制器引用同一public_input，S0+和S1实际接收完整公开对象；主要公平对照为后两组，旧S0只作参考。

开销：

| 组 | 模型调用 | 延迟 | token |
| --- | --- | --- | --- |
| S0 | 0 | 0.013 ms平均路由 | 0 |
| S0+ | 0 | 0.262 ms平均路由 | 0 |
| S1 | 12 | 127.90–138.85 s/次，中位134.12s | {'input_tokens': 107022, 'cached_input_tokens': 27648, 'cache_write_input_tokens': 0, 'output_tokens': 6605, 'reasoning_output_tokens': 3302} |

规则计时只含路由；S1计时含CLI启动、联网重连、服务推理与落盘，执行校验另计。所有S1调用保留传输回退，延迟不是纯模型生成时间。订阅货币分摊未知，没有虚构API价格。
