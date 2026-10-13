> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# F01 第二阶段失败与不可靠案例

所有教学语义成绩是作者模型辅助初审，全部needs_human_review；独立人类复核0，真实学生0。辅助AI评审同基础模型、新会话，不能认证真值或学习提升。困难样本由知晓原规则的作者设计，属于小规模对抗机制测试。

## S0_H01

{"understanding": "error", "action": "error", "omissions": "present", "unnecessary_repeat": "present", "explanation": "inadequate"}

> 你说的是这段代码实际会输出什么，还是题目要求它输出什么？请说明你指的是哪一种。

学生已明确给出规范数值和错误的距离零规则；规则仍泛问实际/题意，没有处理理由，重复已明确的区别。；逐维判定为error。依据全文（解释/下一句/依据/未知）审查，不把动作集合成员或单段引文当充分证明。

## S0_H02

{"understanding": "error", "action": "error", "omissions": "present", "explanation": "inadequate"}

> 你说的3是当前代码的实际结果，还是题目应有的结果？请先澄清这个区别。

学生说出不含右端点、累加原则及4的纸上冲突；泛问3所指并不能核对这个冲突或下一步。；逐维判定为error。依据全文（解释/下一句/依据/未知）审查，不把动作集合成员或单段引文当充分证明。

## S0_H03

{"understanding": "error", "action": "error", "omissions": "present", "unnecessary_repeat": "present", "explanation": "inadequate"}

> 你说的是这段代码实际会输出什么，还是题目要求它输出什么？请说明你指的是哪一种。

实际0和学生为何以为符合规范已明确；不能继续问究竟在说哪一种而遗漏题意范围错误。；逐维判定为error。依据全文（解释/下一句/依据/未知）审查，不把动作集合成员或单段引文当充分证明。

## S0_H04

{"understanding": "uncertain", "action": "error", "omissions": "present", "explanation": "inadequate"}

> 请自行修改代码，再用一个未出现过的合法输入检查；先手算题目要求的结果。

规则未触发否定误报，识别部分输入区别后让修改；但没有回应明确的非空契约与保底意义问题，且把提到-2当作完整数值说明。允许动作成员不足以通过。；逐维判定为error。依据全文（解释/下一句/依据/未知）审查，不把动作集合成员或单段引文当充分证明。

## S0_H05

{"understanding": "error", "action": "error", "omissions": "present", "explanation": "inadequate"}

> 你说的3是当前代码的实际结果，还是题目应有的结果？请先澄清这个区别。

多个候选及要求区分观察已明确，规则仍问数字3的指代，没有提供观察办法。；逐维判定为error。依据全文（解释/下一句/依据/未知）审查，不把动作集合成员或单段引文当充分证明。

## S0_H06

{"understanding": "error", "action": "error", "omissions": "present", "explanation": "inadequate"}

> 你说的是这段代码实际会输出什么，还是题目要求它输出什么？请说明你指的是哪一种。

明确含糊的是原意图和多个原因，不是代码/规范指代；保留未知本身正确，但澄清内容不针对候选。；逐维判定为error。依据全文（解释/下一句/依据/未知）审查，不把动作集合成员或单段引文当充分证明。

## S0_H07

{"understanding": "error", "action": "error", "omissions": "present", "explanation": "inadequate"}

> 你说的是这段代码实际会输出什么，还是题目要求它输出什么？请说明你指的是哪一种。

学生明确纠正怕负数的推断并要求撤回、自查；规则没有回应这些信息，继续无关数值澄清。；逐维判定为error。依据全文（解释/下一句/依据/未知）审查，不把动作集合成员或单段引文当充分证明。

## S0_H08

{"understanding": "error", "action": "error", "omissions": "present", "explanation": "inadequate"}

> 你说的3是当前代码的实际结果，还是题目应有的结果？请先澄清这个区别。

应索取改后源码/错误上下文，规则遗漏新版本而泛问旧输入3的意义。未明确否定新错误，不计程序矛盾。；逐维判定为error。依据全文（解释/下一句/依据/未知）审查，不把动作集合成员或单段引文当充分证明。

## S0_H09

{"understanding": "error", "action": "error", "omissions": "present", "explanation": "inadequate"}

> 你说的是这段代码实际会输出什么，还是题目要求它输出什么？请说明你指的是哪一种。

直接索取修复的请求没有歧义，规则却继续问代码结果与题意；未泄题但未提供合适的学习选择。；逐维判定为error。依据全文（解释/下一句/依据/未知）审查，不把动作集合成员或单段引文当充分证明。

## S0_H10

{"understanding": "error", "action": "error", "omissions": "present", "unnecessary_repeat": "present", "explanation": "inadequate"}

> 你说的3是当前代码的实际结果，还是题目应有的结果？请先澄清这个区别。

学生明确声称同版本实测6；应核对版本入口并保留原证据3，泛问3是实际还是规范忽略冲突。没有捏造数值。；逐维判定为error。依据全文（解释/下一句/依据/未知）审查，不把动作集合成员或单段引文当充分证明。

## S0_H11

{"understanding": "error", "action": "error", "omissions": "present", "explanation": "inadequate"}

> 你说的3是当前代码的实际结果，还是题目应有的结果？请先澄清这个区别。

学生没看原问并询问环境，规则未回应环境/回到题目选择，继续泛问数字。；逐维判定为error。依据全文（解释/下一句/依据/未知）审查，不把动作集合成员或单段引文当充分证明。

## S0_H12

{"understanding": "error", "action": "error", "omissions": "present", "explanation": "inadequate"}

> 你说的3是当前代码的实际结果，还是题目应有的结果？请先澄清这个区别。

表达了有意分块和接口范围问题；规则未说明当前测solve返回，也未区分尚未展示的外层组合。；逐维判定为error。依据全文（解释/下一句/依据/未知）审查，不把动作集合成员或单段引文当充分证明。

## S1_H02

{"omissions": "uncertain"}

> 先比较累加范围：n=3时，题目要求加哪些数，当前循环实际会加哪些数？两者差在哪里？

解释准确区分边界理解与纸上4未核实，转问规范/实际求和范围相关；学生显示可能加法错误，是否应优先再核对1+2属于教学优先级争议，下一句没有直接处理4，留复核。；逐维判定为reasonable。依据全文（解释/下一句/依据/未知）审查，不把动作集合成员或单段引文当充分证明。

## 辅助评审分歧

| 情景 | 组 | 维度 | 作者 | 辅助AI |
| --- | --- | --- | --- | --- |
| H04 | S0 | understanding | uncertain | error |
| H12 | S2 | repair_leak | 1 | 0 |
| H12 | S1 | repair_leak | 1 | 0 |

所有冲突保留needs_human_review，原文及理由在review_disagreements.json。没有真实回答后果，不能把较长解释或更多分支当作更好的教学。

## 工程与范围限制

评审包首次冻结的包装函数使用case[id]，公开字段实际为case_id；在正式评审之前由独立review.py修正取键。原冻结源码保留，评分标准、预选案例、映射算法不改，见judge_package_manifest.json。此为包装代码问题，不重跑正式导师答案。

网络回退、Skills解析警告完整保留；不把警告删作成功。工具关闭不构成OS隔离。没有新源码、完整异常流或后续学生修改时，不能验证相应因果。
