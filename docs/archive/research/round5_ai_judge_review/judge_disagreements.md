> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# 两位评审的分歧、反证审查与未决问题

> **缺失与分母：**原主审16次仅15份完整返回，J1_08无输出，没有补分。J1每组可评7材料、其中6错误题/7规范根因；J2每组可评8材料、其中7错误题/8规范根因。所有计数须按可评分母解释；原始8案例范围仍保留，缺失不是零分或无缺陷。第三审不代替缺失主审。

共启动16个主评会话，成功完成15/16个真实CLI推理；另完成2个反证会话。全部结构完整输出数为17。使用官方Codex CLI 0.162.0-alpha.2、gpt-6.1-sol、xhigh、ChatGPT产品登录；精确后台模型快照未知。每次新exec，只保留第一份回答，无S1/S2重生成、按评分重采样或主Agent补分。

J1、J2是相同基础模型的不同新会话，具有相关错误；第三审也不是人类专家或独立真值。独立人类复核为0，无真实学生回应。分数是探索性模型辅助评审，语义和教学质量仍标为needs_human_review。

匿名映射随机生成，主审反序展示A/B/C与C/B/A；运行期间密钥只在父进程内存，落盘映射为密文，全部评审进程退出后才解封。工作目录仅有本案prompt与schema；旧评分、旧决策、研究聊天没有作为模型输入。表达风格、运行附录和“待定”措辞仍可能暴露来源，不能称身份完全不可猜。

未建立OS文件访问隔离：干净目录和只读配置不等于deny-read。显式禁用技能后，本地输入渲染探针不再显示技能目录，正式stderr仍出现SKILL.md扫描警告，不能宣称无文件扫描；实际服务器收到的全部上下文未获独立证明。事件日志用于检查工具行为，不能排除宿主注入。

评分前冻结统一量表；每维原文引用、来源、理由和自报置信范围均保存。N/A、uncertain、invalid与零分分开，不计算加权总分，也不以多数票处理事实。原有追问量表和完整修复定义保留，四级披露及其他辅助分数为本轮冻结扩展。

**本批次发生阻塞；所有计数以已取得结果为限，缺失会话没有补生成。**

## 同意与缺失分开统计

每个维度有8案例×3材料=24项比较；共120项，彼此并非独立观测。只报告描述统计，不推断专家一致性或总体可靠性。两个NA不等于两个评分一致。

| 维度 | 计数 |
| --- | --- |
| 程序原因 | {"agree": 20, "disagree": 1, "missing_or_invalid": 3} |
| 证据 | {"agree": 21, "missing_or_invalid": 3} |
| 追问 | {"agree": 19, "disagree": 2, "missing_or_invalid": 3} |
| 披露 | {"agree": 21, "missing_or_invalid": 3} |
| 认知推断 | {"agree": 17, "both_NA_or_uncertain": 3, "one_NA_or_uncertain": 1, "missing_or_invalid": 3} |


| 案例 | 组别 | 维度 | J1 | J2 | 状态 | J3（不覆盖主评） |
| --- | --- | --- | --- | --- | --- | --- |
| 03 | S1 | 认知推断 | N/A / uncertain / 未完成（查看状态） | N/A / uncertain / 未完成（查看状态） | both_NA_or_uncertain | N/A / uncertain / 未完成（查看状态） |
| 05 | S1 | 认知推断 | N/A / uncertain / 未完成（查看状态） | N/A / uncertain / 未完成（查看状态） | both_NA_or_uncertain | N/A / uncertain / 未完成（查看状态） |
| 05 | S2 | 认知推断 | 2 | N/A / uncertain / 未完成（查看状态） | one_NA_or_uncertain | N/A / uncertain / 未完成（查看状态） |
| 06 | S1 | 追问 | 1 | 2 | disagree | 2 |
| 06 | S1 | 认知推断 | N/A / uncertain / 未完成（查看状态） | N/A / uncertain / 未完成（查看状态） | both_NA_or_uncertain | N/A / uncertain / 未完成（查看状态） |
| 06 | S2 | 程序原因 | 2 | 1 | disagree | 2 |
| 07 | S0 | 追问 | 2 | 1 | disagree | 2 |
| 08 | S0 | 程序原因 | N/A / uncertain / 未完成（查看状态） | 1 | missing_or_invalid | N/A / uncertain / 未完成（查看状态） |
| 08 | S0 | 证据 | N/A / uncertain / 未完成（查看状态） | 2 | missing_or_invalid | N/A / uncertain / 未完成（查看状态） |
| 08 | S0 | 追问 | N/A / uncertain / 未完成（查看状态） | 2 | missing_or_invalid | N/A / uncertain / 未完成（查看状态） |
| 08 | S0 | 披露 | N/A / uncertain / 未完成（查看状态） | 2 | missing_or_invalid | N/A / uncertain / 未完成（查看状态） |
| 08 | S0 | 认知推断 | N/A / uncertain / 未完成（查看状态） | 2 | missing_or_invalid | N/A / uncertain / 未完成（查看状态） |
| 08 | S1 | 程序原因 | N/A / uncertain / 未完成（查看状态） | 2 | missing_or_invalid | N/A / uncertain / 未完成（查看状态） |
| 08 | S1 | 证据 | N/A / uncertain / 未完成（查看状态） | 2 | missing_or_invalid | N/A / uncertain / 未完成（查看状态） |
| 08 | S1 | 追问 | N/A / uncertain / 未完成（查看状态） | 2 | missing_or_invalid | N/A / uncertain / 未完成（查看状态） |
| 08 | S1 | 披露 | N/A / uncertain / 未完成（查看状态） | 3 | missing_or_invalid | N/A / uncertain / 未完成（查看状态） |
| 08 | S1 | 认知推断 | N/A / uncertain / 未完成（查看状态） | 2 | missing_or_invalid | N/A / uncertain / 未完成（查看状态） |
| 08 | S2 | 程序原因 | N/A / uncertain / 未完成（查看状态） | 2 | missing_or_invalid | N/A / uncertain / 未完成（查看状态） |
| 08 | S2 | 证据 | N/A / uncertain / 未完成（查看状态） | 2 | missing_or_invalid | N/A / uncertain / 未完成（查看状态） |
| 08 | S2 | 追问 | N/A / uncertain / 未完成（查看状态） | 2 | missing_or_invalid | N/A / uncertain / 未完成（查看状态） |
| 08 | S2 | 披露 | N/A / uncertain / 未完成（查看状态） | 1 | missing_or_invalid | N/A / uncertain / 未完成（查看状态） |
| 08 | S2 | 认知推断 | N/A / uncertain / 未完成（查看状态） | 2 | missing_or_invalid | N/A / uncertain / 未完成（查看状态） |

## 程序原因集合冲突


| 案例 | 组别 | J1规范映射 | J2规范映射 |
| --- | --- | --- | --- |
| 08 | S0 | N/A / uncertain / 未完成（查看状态） | {"correct_ids": [], "incorrect_ids": ["loop_end_excluded"], "missing_ids": ["return_offset"], "wrong_definite": [], "correct_program_false_positive": false, "scope": "judge semantic mapping to frozen roots; quoted entailment still needs_human_review"} |
| 08 | S1 | N/A / uncertain / 未完成（查看状态） | {"correct_ids": ["return_offset"], "incorrect_ids": [], "missing_ids": [], "wrong_definite": [], "correct_program_false_positive": false, "scope": "judge semantic mapping to frozen roots; quoted entailment still needs_human_review"} |
| 08 | S2 | N/A / uncertain / 未完成（查看状态） | {"correct_ids": ["return_offset"], "incorrect_ids": [], "missing_ids": [], "wrong_definite": [], "correct_program_false_positive": false, "scope": "judge semantic mapping to frozen roots; quoted entailment still needs_human_review"} |

S0的静态错误候选与执行器已拒绝的候选是不同层面。08中边界模式确实存在，修改却被反证拒绝；不能把评审未计入该候选当成旧基线统计错误。06的补偿性截断是局部修复风险，不能误算成第二个当前根因。

## 第三会话的反证审查

触发记录：third_selection.json（仅本机证据：`experiments/round5_ai_judge_review/runs/judges_20261009T120606867427Z/combined_view/third_selection.json`；不随 Git 分发）。

### J3_07

反证提示（仅本机证据：`experiments/round5_ai_judge_review/runs/judges_20261009T120606867427Z/combined_view/prompts/J3_07.md`；不随 Git 分发）；首次反证原文（仅本机证据：`experiments/round5_ai_judge_review/runs/judges_20261009T120606867427Z/combined_view/responses/J3_07/raw_response.json`；不随 Git 分发）。状态complete，真实成功True。

**S0**

追问：

判定：**2**；主观置信范围：[0.71, 0.85]；依据：SOURCE, CONTRACT, V04, STUDENT_UNKNOWN, RUBRIC。

学生明确给出规范预期时，不同答案可分别引向实现追踪或规范澄清，支持分流用途。比较基准含混的批评成立，但需要澄清不等于完全不区分；不能把预期0直接判为认知错误。

> 你预期哪个输入会表现不同？请先指出预期输出，再核对实际结果；当前方法暂不定位原因。


披露：

判定：**0**；主观置信范围：[0.98, 1.0]；依据：ROOTS, RUBRIC。

没有指出关键错误机制或修复操作；运行附录为空。

> 当前方法暂不定位原因。


> 运行附录：


**S1**

追问：

判定：**2**；主观置信范围：[0.85, 0.95]；依据：SOURCE, CONTRACT, STUDENT_UNKNOWN, RUBRIC。

开放式意图问同样可区分防空与初值路径，改变后续讨论。前文揭示机制但未给真实初衷；自报可能受解释影响，不能确认历史动机或原始误解。

> 你在列表前添加0，原本是想解决什么问题？


披露：

判定：**3**；主观置信范围：[0.98, 1.0]；依据：REFERENCE, ROOTS, CONTRACT, RUBRIC。

给出可直接替换的返回表达式，适用于整个契约并消除唯一真实根因，构成完整正确修复。披露位于正文。

> 题目保证列表非空，可直接写`return max(xs)`。


**S2**

追问：

判定：**2**；主观置信范围：[0.85, 0.95]；依据：SOURCE, CONTRACT, STUDENT_UNKNOWN, RUBRIC。

防空与通用初值回答可分别引向契约核对和负数初值讨论。前文提供了可复述的候选，可能诱导自报，但不消除其教学分流用途，也不能确认原始误解。

> 你加入0是为了处理空列表、作为最大值初值，还是有其他考虑？


披露：

判定：**1**；主观置信范围：[0.92, 0.98]；依据：SOURCE, ROOTS, RUBRIC。

披露关键机制并要求检查，但未给删除零候选、替换返回表达式或完整算法。修复容易推出，不等于已经披露具体修复操作。

> 0比两个原元素都大，却不属于原列表。


> 若为初值，检查它是否会压过合法负数


### J3_06

反证提示（仅本机证据：`experiments/round5_ai_judge_review/runs/judges_20261009T120606867427Z/combined_view/prompts/J3_06.md`；不随 Git 分发）；首次反证原文（仅本机证据：`experiments/round5_ai_judge_review/runs/judges_20261009T120606867427Z/combined_view/responses/J3_06/raw_response.json`；不随 Git 分发）。状态complete，真实成功True。

**S0**

追问：

判定：**2**；主观置信范围：[0.84, 0.94]；依据：SOURCE, RUBRIC, STUDENT_UNKNOWN。

可区分合法索引与实际迭代范围是否被混同，分别转向range边界解释或追加及补偿行为追踪。质量来自所问信息，不来自运行附录。

> 长度为2的列表可使用哪些非负索引？请逐轮检查循环何时停止。


披露：

判定：**2**；主观置信范围：[0.96, 0.99]；依据：SOURCE, ROOTS, V12, RUBRIC。

正文给出边界线索，属1级；附录P1直接给出删除上界加1的操作，但保留长度2截断，V12显示回归。整体为可落实但不完整的2级修复披露。

> 候选原因（未确认）：["index_off_by_one"]


> for i in range(len(xs)):


**S1**

追问：

判定：**2**；主观置信范围：[0.75, 0.9]；依据：SOURCE, STUDENT_UNKNOWN, RUBRIC。

前文已给机制和结果，确有复述风险；但逐行要求仍可区分把空表当零轮与能展开range(1)的当前回答，分别需要范围解释或独立迁移核对。答对不确认原始理解，先解释也不自动取消分流价值。

> 你能用空列表逐行推演，指出哪一步使输出不再是原列表的复制吗？


> 当 `i == len(xs)` 时，代码追加了原列表之外的 `0`。


披露：

判定：**3**；主观置信范围：[0.97, 0.99]；依据：SOURCE, ROOTS, REFERENCE, CONTRACT, RUBRIC。

自然语言给出完整替代算法，同时去除额外迭代和补偿截断，足以保持所有合法输入的元素、数量和顺序；不因没有代码块而降档。

> 去掉追加 `0` 和长度为2的特判，直接遍历 `xs`，把每个元素追加到 `out` 后返回。


**S2**

追问：

判定：**2**；主观置信范围：[0.82, 0.94]；依据：SOURCE, CONTRACT, STUDENT_UNKNOWN, RUBRIC。

未知意图的两种合理回答可分别引向复制规范核对或循环策略追踪。选项有引导且不穷尽动机，自报不能独立确认知识状态；分流价值并非来自明写条件分支。

> 追加0是你认为题目要求的行为，还是为了处理循环多走的一步而临时加入的？


披露：

判定：**1**；主观置信范围：[0.93, 0.99]；依据：SOURCE, ROOTS, RUBRIC。

披露错误机制和检查方向，但未给修改上界、移除现有截断或替换遍历的具体操作，不足以直接完成修复。

> 长度2的特殊处理掩盖了多出的0


> 重点检查循环上界与最后一轮


第三审不是独立主评，它看过两份新评意见；仅用于检查引文和反例。即使与其中一方同意，仍不能多数裁决主观真值。其余争议按预先4案例上限保留needs_human_review。

## 自动检查发现的边界


| 案例 | 评审 | 组别 | 问题 |
| --- | --- | --- | --- |


| 案例 | 组别 | 提取评审 | 引用 | 参数/预测 | 执行判定 |
| --- | --- | --- | --- | --- | --- |

预测矛盾必须先核对“原提交/修复后/附录的干预程序”范围。由评审错误提取造成的矛盾是评审可靠性问题，不自动扣原导师分。教学追问能否被学生理解、答案披露阈值、条件分支是否必要均需人类或学生数据。

## 执行补充与失败保留

超时后仅继续已存在争议的选择记录（仅本机证据：`experiments/round5_ai_judge_review/runs/judges_20261009T120606867427Z/combined_view/counter_continuation/selection.json`；不随 Git 分发）；两次首次反证记录（仅本机证据：`experiments/round5_ai_judge_review/runs/judges_20261009T120606867427Z/combined_view/counter_continuation/execution_summary.json`；不随 Git 分发）。未重采样J1_08。补充等待上限1200秒，原主审720秒；模型、思考配置及量表不变。
