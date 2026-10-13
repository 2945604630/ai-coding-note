> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# 恢复匿名身份后的S0/S1/S2重新比较

> **缺失与分母：**原主审16次仅15份完整返回，J1_08无输出，没有补分。J1每组可评7材料、其中6错误题/7规范根因；J2每组可评8材料、其中7错误题/8规范根因。所有计数须按可评分母解释；原始8案例范围仍保留，缺失不是零分或无缺陷。第三审不代替缺失主审。

共启动16个主评会话，成功完成15/16个真实CLI推理；另完成2个反证会话。全部结构完整输出数为17。使用官方Codex CLI 0.162.0-alpha.2、gpt-6.1-sol、xhigh、ChatGPT产品登录；精确后台模型快照未知。每次新exec，只保留第一份回答，无S1/S2重生成、按评分重采样或主Agent补分。

J1、J2是相同基础模型的不同新会话，具有相关错误；第三审也不是人类专家或独立真值。独立人类复核为0，无真实学生回应。分数是探索性模型辅助评审，语义和教学质量仍标为needs_human_review。

匿名映射随机生成，主审反序展示A/B/C与C/B/A；运行期间密钥只在父进程内存，落盘映射为密文，全部评审进程退出后才解封。工作目录仅有本案prompt与schema；旧评分、旧决策、研究聊天没有作为模型输入。表达风格、运行附录和“待定”措辞仍可能暴露来源，不能称身份完全不可猜。

未建立OS文件访问隔离：干净目录和只读配置不等于deny-read。显式禁用技能后，本地输入渲染探针不再显示技能目录，正式stderr仍出现SKILL.md扫描警告，不能宣称无文件扫描；实际服务器收到的全部上下文未获独立证明。事件日志用于检查工具行为，不能排除宿主注入。

评分前冻结统一量表；每维原文引用、来源、理由和自报置信范围均保存。N/A、uncertain、invalid与零分分开，不计算加权总分，也不以多数票处理事实。原有追问量表和完整修复定义保留，四级披露及其他辅助分数为本轮冻结扩展。

**本批次发生阻塞；所有计数以已取得结果为限，缺失会话没有补生成。**

8案例中有7个错误程序、1个正确程序（05），规范根因共8个（04有两个）。分母、原因集合与回答级分数分别报告。J3只涉及争议子集，不与完整J1/J2组直接比较。

| 评审 | 组别 | 案例数 | 正确根因数（见可评分母） | 错误候选 | 遗漏根因 | 错误确定归因 | 正确程序误报 | 完整修复数（见可评分母） | 正确题替代答案 | 有用追问 | 区分性追问 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J1 | S0 | 7 | 6 | 0 | 1 | 0 | 0 | 4 | 0 | 7 | 6 |
| J1 | S1 | 7 | 7 | 0 | 0 | 0 | 0 | 6 | 1 | 7 | 6 |
| J1 | S2 | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 7 |
| J2 | S0 | 8 | 6 | 1 | 2 | 0 | 0 | 4 | 0 | 8 | 6 |
| J2 | S1 | 8 | 8 | 0 | 0 | 0 | 0 | 7 | 1 | 8 | 8 |
| J2 | S2 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 8 |

计数是评审从原文映射到冻结原因，不等于原文语义已经由程序认证。候选与确定性断言分开；S0有执行拒绝机制，静态发现不能直接当作有效归因。

## 四级披露、有效分数与N/A

| 评审 | 组别 | 披露0/1/2/3/None计数 | 追问0/1/2/None计数 | 各维状态 |
| --- | --- | --- | --- | --- |
| J1 | S0 | {"3": 4, "0": 2, "2": 1} | {"2": 6, "1": 1} | {"program": {"scored": 7}, "evidence": {"scored": 7}, "question": {"scored": 7}, "leakage": {"scored": 7}, "cognition": {"scored": 7}} |
| J1 | S1 | {"3": 7} | {"2": 6, "1": 1} | {"program": {"scored": 7}, "evidence": {"scored": 7}, "question": {"scored": 7}, "leakage": {"scored": 7}, "cognition": {"scored": 4, "not_applicable": 3}} |
| J1 | S2 | {"1": 7} | {"2": 7} | {"program": {"scored": 7}, "evidence": {"scored": 7}, "question": {"scored": 7}, "leakage": {"scored": 7}, "cognition": {"scored": 7}} |
| J2 | S0 | {"3": 4, "0": 2, "2": 2} | {"2": 6, "1": 2} | {"program": {"scored": 8}, "evidence": {"scored": 8}, "question": {"scored": 8}, "leakage": {"scored": 8}, "cognition": {"scored": 8}} |
| J2 | S1 | {"3": 8} | {"2": 8} | {"program": {"scored": 8}, "evidence": {"scored": 8}, "question": {"scored": 8}, "leakage": {"scored": 8}, "cognition": {"scored": 5, "not_applicable": 3}} |
| J2 | S2 | {"1": 8} | {"2": 8} | {"program": {"scored": 8}, "evidence": {"scored": 8}, "question": {"scored": 8}, "leakage": {"scored": 8}, "cognition": {"scored": 7, "not_applicable": 1}} |

0无关键修复，1重要思路，2可实施但不完整的操作，3完整修复或完整替代算法。S0附录包含部分完整干预源码，其披露与导师正文不同；缺少真实学生可见性信息，不能据此构造学生暴露率。S1的完整替代答案在05单列，不是误报。S2不直接给完整答案的提示要求本身可解释差异，不能归因于复杂证据核验独有机制。

## 每案例追问得分与配对判断

| 案例 | 组别 | J1 | J2 | J3 |
| --- | --- | --- | --- | --- |
| 01 | S0 | 2 | 2 | 未完成 |
| 01 | S1 | 2 | 2 | 未完成 |
| 01 | S2 | 2 | 2 | 未完成 |
| 02 | S0 | 2 | 2 | 未完成 |
| 02 | S1 | 2 | 2 | 未完成 |
| 02 | S2 | 2 | 2 | 未完成 |
| 03 | S0 | 2 | 2 | 未完成 |
| 03 | S1 | 2 | 2 | 未完成 |
| 03 | S2 | 2 | 2 | 未完成 |
| 04 | S0 | 2 | 2 | 未完成 |
| 04 | S1 | 2 | 2 | 未完成 |
| 04 | S2 | 2 | 2 | 未完成 |
| 05 | S0 | 1 | 1 | 未完成 |
| 05 | S1 | 2 | 2 | 未完成 |
| 05 | S2 | 2 | 2 | 未完成 |
| 06 | S0 | 2 | 2 | 2 |
| 06 | S1 | 1 | 2 | 2 |
| 06 | S2 | 2 | 2 | 2 |
| 07 | S0 | 2 | 1 | 2 |
| 07 | S1 | 2 | 2 | 2 |
| 07 | S2 | 2 | 2 | 2 |
| 08 | S0 | 未完成 | 2 | 未完成 |
| 08 | S1 | 未完成 | 2 | 未完成 |
| 08 | S2 | 未完成 | 2 | 未完成 |


| 案例 | 评审 | 配对 | 关系 | 偏好 | 引用有效 |
| --- | --- | --- | --- | --- | --- |
| 01 | J1 | S1/S2 | near_equivalent | tie | true |
| 01 | J1 | S0/S2 | different | tie | true |
| 01 | J1 | S0/S1 | different | tie | true |
| 01 | J2 | S1/S2 | near_equivalent | tie | true |
| 01 | J2 | S0/S2 | different | uncertain | true |
| 01 | J2 | S0/S1 | different | uncertain | true |
| 02 | J1 | S0/S2 | different | tie | true |
| 02 | J1 | S1/S2 | different | S2 | true |
| 02 | J1 | S0/S1 | near_equivalent | S0 | true |
| 02 | J2 | S0/S2 | different | tie | true |
| 02 | J2 | S1/S2 | different | S2 | true |
| 02 | J2 | S0/S1 | different | S0 | true |
| 03 | J1 | S0/S2 | different | tie | true |
| 03 | J1 | S0/S1 | near_equivalent | tie | true |
| 03 | J1 | S1/S2 | different | tie | true |
| 03 | J2 | S0/S2 | different | S2 | true |
| 03 | J2 | S0/S1 | near_equivalent | tie | true |
| 03 | J2 | S1/S2 | different | S2 | true |
| 04 | J1 | S0/S1 | different | S0 | true |
| 04 | J1 | S1/S2 | different | S2 | true |
| 04 | J1 | S0/S2 | different | uncertain | true |
| 04 | J2 | S0/S1 | different | S0 | true |
| 04 | J2 | S1/S2 | different | tie | true |
| 04 | J2 | S0/S2 | different | S0 | true |
| 05 | J1 | S0/S1 | different | S1 | true |
| 05 | J1 | S0/S2 | different | S2 | true |
| 05 | J1 | S1/S2 | different | tie | true |
| 05 | J2 | S0/S1 | different | S1 | true |
| 05 | J2 | S0/S2 | different | S2 | true |
| 05 | J2 | S1/S2 | different | tie | true |
| 06 | J1 | S0/S2 | different | tie | true |
| 06 | J1 | S0/S1 | different | S0 | true |
| 06 | J1 | S1/S2 | different | S2 | true |
| 06 | J2 | S0/S2 | different | tie | true |
| 06 | J2 | S0/S1 | near_equivalent | tie | true |
| 06 | J2 | S1/S2 | different | tie | true |
| 06 | J3 | S0/S2 | different | tie | true |
| 06 | J3 | S0/S1 | near_equivalent | S0 | true |
| 06 | J3 | S1/S2 | different | tie | true |
| 07 | J1 | S0/S2 | different | tie | true |
| 07 | J1 | S0/S1 | different | tie | true |
| 07 | J1 | S1/S2 | near_equivalent | tie | true |
| 07 | J2 | S0/S2 | different | S2 | true |
| 07 | J2 | S0/S1 | different | S1 | true |
| 07 | J2 | S1/S2 | near_equivalent | tie | true |
| 07 | J3 | S0/S2 | different | tie | true |
| 07 | J3 | S0/S1 | different | tie | true |
| 07 | J3 | S1/S2 | near_equivalent | tie | true |
| 08 | J2 | S1/S2 | near_equivalent | tie | true |
| 08 | J2 | S0/S1 | different | tie | true |
| 08 | J2 | S0/S2 | different | tie | true |

配对偏好与单份等级可能冲突，原样保留，不为形成排名强行修正。先解释后追问可能诱发复述；解释正确、能推演两条路径与实际动态教学成功是不同证据。

## 特别复查07与08

### 案例07

冻结根因：[{"id": "init_zero", "definition": "额外的零候选/初值改变规范极值"}]。

**S0**

J1：

判定：**1**；主观置信范围：[0.76, 0.9]；依据：SOURCE, ROOTS, E01, RUBRIC。

只报告失败，未识别源码已可确定的额外0候选；原因分析不完整，但没有错误归因。

> 候选原因（未确认）：[]


> 当前方法暂不定位原因。


J2：

判定：**1**；主观置信范围：[0.7, 0.85]；依据：SOURCE, ROOTS, RUBRIC。

分析停留在未定位状态，未识别额外零候选这一根因；没有确定性错误归因。按不完整分析计1，不表示覆盖了任何根因；源码已有可诊断依据，继续搁置偏保守。

> 候选原因（未确认）：[]


> 当前方法暂不定位原因。


**S1**

J1：

判定：**2**；主观置信范围：[0.96, 0.99]；依据：SOURCE, ROOTS, CONTRACT, RUBRIC。

完整识别额外0候选及其全负数后果，符合冻结根因；没有错误归因或唯一性过推。

> `[0] + xs` 把额外的0加入比较。


> 全负数时，0大于所有原元素，结果便错误地变成0。


J2：

判定：**2**；主观置信范围：[0.97, 0.99]；依据：SOURCE, ROOTS, CONTRACT。

完整指出额外零候选改变全负列表最大值，符合唯一冻结根因init_zero，没有错误归因。

> `[0] + xs` 把额外的0加入比较。全负数时，0大于所有原元素，结果便错误地变成0。


**S2**

J1：

判定：**2**；主观置信范围：[0.95, 0.99]；依据：SOURCE, ROOTS, CONTRACT, RUBRIC。

完整指出额外0改变全负列表最大值，符合唯一冻结根因。防空和通用初值是待定学生动机，不是新增程序根因。

> 源码额外加入了0。


> 0比两个原元素都大，却不属于原列表。


J2：

判定：**2**；主观置信范围：[0.96, 0.99]；依据：SOURCE, ROOTS, CONTRACT。

明确指出额外0参与比较并压过合法负数，识别init_zero。防空和通用初值被保留为动机候选，不计作新增程序根因。

> `max`会比较加入0后的所有元素。对于`[-5,-2]`，0比两个原元素都大，却不属于原列表。


> 候选原因是想防空列表，或把0当作通用初值；缺少你的解题思路，动机待定，不能据此判断你不懂最大值。


### 案例08

冻结根因：[{"id": "return_offset", "definition": "返回表达式相对规范存在固定偏移"}]。

**S0**

J1：

未完成；没有补填分数。

J2：

判定：**1**；主观置信范围：[0.94, 0.99]；依据：SOURCE, ROOTS, V09, V11, V12。

提出的是未确认错误线索：遗漏的n已有+n补偿。未识别return_offset；附录源码及局部成功不等于明确归因。

> 候选原因（未确认）：["loop_end_excluded"]


> accepted：false


**S1**

J1：

未完成；没有补填分数。

J2：

判定：**2**；主观置信范围：[0.97, 1.0]；依据：SOURCE, ROOTS, REFERENCE。

完整识别固定偏移及已有补偿，未把循环终点排除误列为独立根因。

> 错误在返回式多减了1。


> `range(1, n)`不包含n，但`+n`已经补上末项。


**S2**

J1：

未完成；没有补填分数。

J2：

判定：**2**；主观置信范围：[0.94, 0.99]；依据：SOURCE, ROOTS, STUDENT_UNKNOWN。

已解释真实固定偏移及+n补偿；待定的是书写动机，而非另增循环遗漏根因。

> 循环累加到n−1，再加n就覆盖了目标各项，额外减1会使结果偏小。


> 缺少你的推导过程，暂不能确定，也不能据此判断你不懂循环。


07额外0被纳入max；08循环遗漏已由+n补偿，剩余-1才使结果偏小。固定AST基线不能定位这两题的有效原因，模型原文是否清楚表达则需引用复核。任何成立的增量仅相对当前有限S0，不证明所有扩展规则或符号方法都无法实现。

## 程序事实、成本与范围

新评审提取的预测：{"scope_excluded": 18, "verified": 25}。其中多份评审可重复提取同一句，不计独立模型能力样本。旧13条和S0附录独立校验见机器日志；违法参数或范围不明不运行新代码。

单次生成、单次评分不能验证用户回应后的动作更新，也没有完成耗时、理解程度、依赖或独立新题数据。两审成本见[blind_judge_results.md](<blind_judge_results.md>)。运行器只完成本轮复核；后续产品和学生实验均未开始。

## 实际问题与逐条分流路径

逐案例原追问、假设回应路径及配对理由（仅本机证据：`experiments/round5_ai_judge_review/runs/judges_20261009T120606867427Z/combined_view/teaching_question_paths.md`；不随 Git 分发）。其中路径均为评审假设，没有学生学习数据。
