> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# P2-B：帮助暴露感知迁移选题快速可行性检查

日期：2026-10-11。判定：**NO-GO，停在材料门槛，不启动模型比较和扩样。**

本轮确认了一个记录层面的实际问题：帮助指向原题还是测验题，不能代替“该帮助是否直接覆盖候选题解法”的判断。但现有材料不能配置两个合格的“原题—近迁移—适用条件变化”场景，因而没有进入 B/B0/B1 的选题准确率比较。**这不是 B 已被模型实验证伪，也不是教师规则已经被证明优于 B；它是当前选题未取得继续试验资格。**

本轮只做既有源码、题目和帮助原文的工程及探索性检查。没有独立人工教学审题、真实学习者、新模型请求、新学生代码执行或双 AI 评分。写入范围仅为本报告和 `P2_B_next_decision.md`。

## 1. 问题是否存在，以及实际能证明什么

### 1.1 F05 的资格记录与暴露内容是不同问题

[F05 records.py](<../../../experiments/feature_validation/F05_independent_assessment/records.py>) 的 `eligibility` 读取首答前帮助的 `target`：

- 指向 `assessment` 的已记录帮助会影响资格，判断不读取帮助正文。
- 只有 `original` 的帮助不会因此直接排除测验资格。
- 帮助关系、外部帮助声明或历史覆盖不确定时保留 `unknown`。
- 这些标签的范围是当前可见记录，不能证明外部无帮助。

因此，原题完整解法若能直接套入同一合同的候选题，单靠 `original` 标签无法说明候选题还有多少新增测量价值；一般概念教学也不能仅因被标为 `assessment` 就在内容层面称为“完整答案泄露”。**这不是本轮要修复的 F05 缺陷：F05 处理独立作答记录，P2-B 要处理题目的新增测量价值，两种判定应并存。**

有实际保存的来源支持上述区别：

| 既有材料 | 可核对的事实 | 不能推出的结论 |
|---|---|---|
| F05 T02 完整帮助事件（仅本机证据：`experiments/feature_validation/F05_independent_assessment/results/formal_v1/T02/events/000004.json`；不随 Git 分发）＋T02 首答结果（仅本机证据：`experiments/feature_validation/F05_independent_assessment/results/formal_v1/T02/first/result.json`；不随 Git 分发） | 首答前保存完整 MAX 实现，随后冻结提交通过 2/2 已指定测试 | 不能把通过说成独立推导算法；也不能说真实学生发生了照抄 |
| F05 T02 局部提示事件（仅本机证据：`experiments/feature_validation/F05_independent_assessment/results/formal_v1/T02/events/000003.json`；不随 Git 分发） | 提示原文为“先核对返回值是否来自输入列表。” | 不足以单独构成完整 MAX 解法 |
| F05 T01 原题帮助事件（仅本机证据：`experiments/feature_validation/F05_independent_assessment/results/formal_v1/T01/events/000002.json`；不随 Git 分发） | 原文为“原题的循环边界教学记录，非本题提示。” | 这是概要占位文本，没有实际讲解内容，不能据此精确恢复解法暴露 |
| F05 T03 session.json（仅本机证据：`experiments/feature_validation/F05_independent_assessment/results/formal_v1/T03/session.json`；不随 Git 分发） | `external_help_declaration=unknown` | 不能补造外部帮助原文，不能认证帮助历史完整无外援 |

T02 同时还有提前见题事件，完整帮助与见题的影响不能在该记录中分离。见过题干本身也不等于见过答案。以上 F05 场景明确为冻结的**模拟记录**；提示及完整代码事件注明 `frozen_simulated_teacher_action_not_real_AI`。本轮验证了记录与规则确有内容粒度缺口，没有验证现实学生中的发生频率或测量损失大小。

### 1.2 事前限定的内容判读规则

本轮先固定以下规则，再决定是否启动模型测试：

| 类别 | 判断依据 | 允许的处理 |
|---|---|---|
| G：一般概念 | 解释通用语义或性质，没有替学生完成候选题特定操作 | 不因“学过相同概念”排除题；仍核对具体作答要求 |
| P：不完整提示 | 指向追踪、核查或局部关系，仍有实质步骤未给出 | 保留剩余测量要求，不能自动升为完整解法 |
| K：关键步骤 | 给出与候选题要求对应的具体边界、初始化、分支或更新方式 | 标出已覆盖的要求；关键步骤不等于整题一律无价值 |
| F：完整/直接可套用解法 | 帮助已覆盖相同合同下完成题目的步骤，或给出可直接提交的代码 | 限定为练习或帮助后表现；不能据此证明未借用解法的独立推导 |
| U：无关/未知分别记录 | 已知无关要求与关系、来源、历史缺失是两个维度 | 已知无关内容不排除；缺失关系保留 unknown，不能假定未暴露 |

代码只需改变量名就能满足相同合同，是直接复用的强依据；一般教学是否使学生理解、自然语言解法是否等价、不同题是否同难度，都不能由这份规则或 AI 自评认证。完整解法被学过并不意味着后续作答完全没有价值，只意味着不能把同一实现再次通过当成“已排除机械套用”的证据。

题目先经过目标概念、额外前置知识、题型和难度审核。没有合格候选时允许“无可选题”，不强行选择最难题。任一概念场景缺少合格题对，停止模型比较；不能靠模型生成题补齐后称已验证迁移。

## 2. 两个概念场景的材料审核

现有“审核”多为源码、输入范围、固定样例及作者材料审核，**不是独立教师对迁移题对的教学审核**。本轮的判断也由 Codex 作出，不能改称教师已认可。

### 场景 S：Python 循环端点与目标闭区间的对应

原题取 [F02 C01](<../../../experiments/feature_validation/F02_dynamic_questioning/cases/C01.json>)：`solve(n)` 返回 1 到 n（含 n）的整数和，n=0 返回 0；整数 n 在 0..8，排除 bool。历史失败源码使用 `range(1,n)`；已有事实为 n=0 返回 0、n=1 返回 0（应为 1）、n=3 返回 3（应为 6）。本轮未重跑这些程序。

| 槽位 | 既有候选及出处 | 共享要求与新增要求 | 本轮审定 |
|---|---|---|---|
| 原题 S-O | F02 C01 的闭区间求和 | range 取值、累加、零边界 | 可作程序行为材料；没有独立迁移题对审定 |
| 近迁移 S-N | round4 a_study.json（仅本机证据：`experiments/round4/data/a_study.json`；不随 Git 分发） 的 `loop_end_assessment`：返回 [1,2,…,n]，n=0 返回空列表 | 端点仍须包含 n；新增列表构造及 `append`，原文件题型是从两段完整代码中选择 | **待审，不能直接当独立实现题**。列表前置知识未确认；读代码选择与 F02 的自行修改形式不同 |
| 条件变化 S-C | **未找到合格的既有题** | 合格题应改变端点规则的适用条件，而非再测同一边界或换容器 | **配置失败，停止** |

已有 n=0、n=1 边界样例是原题已公开事实，不能改称新迁移题。列表生成仍要求同一个“包含 n”的循环端点，也没有改变该规则的适用条件。SUM→MAX 是 F05 的既有换题流程，[question.json](<../../../experiments/feature_validation/F05_independent_assessment/data/question.json>) 已明确注明它不是经过验证的等值迁移题；改换目标算法不能补足 S-C。

round4 两道 `loop_end` 题都标为 `author_review_fixture`、`expert_review=pending`。如果把代码选择题重写成实现题，那会产生新的材料与难度问题；本轮没有这样做，也没有新增半开区间题后宣称审核通过。

### 场景 M：最大值候选集合、初始化与输入条件

原题取 round5 case 03（仅本机证据：`experiments/round5_ui_model/cases/03.json`；不随 Git 分发）：返回非空整数列表最大值，允许全负数；长度 1..8，元素 -20..20，排除 bool。零初始化的失败示例与该合同已有历史审核。关注要求是结果来自合法候选、正确比较及全负情形，不能把一个执行失败等同于学生不懂负数。

| 槽位 | 既有候选及出处 | 共享要求与新增要求 | 本轮审定 |
|---|---|---|---|
| 原题 M-O | round5 case 03 的 MAX | 非空、允许全负、最大值候选及初始化 | 可作程序行为材料 |
| 近迁移 M-N | F05 `F05_MAX_01`，见 [question.json](<../../../experiments/feature_validation/F05_independent_assessment/data/question.json>) 和 [registry.json](<../../../experiments/feature_validation/F05_independent_assessment/data/registry.json>) | 合同与 M-O 相同，只复用另一历史实现/任务记录 | **不接受为区分机械套用与条件理解的新题**；可作相同算法练习，不能以换 ID 证明迁移 |
| 条件变化 M-C | [P2 候选报告 §4.3](<P2_innovation_candidates.md>) 的既有说明性示例：求严格小于 cap 的最大元素，无合格元素返回 None | 共享极值候选思想；新增筛选谓词、二参数接口、无候选处理、None 及可能的状态初始化 | **未审定**。只是既有原型说明，没有合格题记录、学生前置知识或难度证据 |

筛选后最大值的确有潜在条件变化，但即使原 MAX 帮助没暴露筛选与空候选分支，也不能据此把 M-C 判成公平可测的迁移题。失败可能由未学过 None、筛选或新接口导致。既有 common.py 的 MAX 合同只接受一个非空列表，不能把旧 MAX 的 oracle/执行白名单说成已验证 M-C；本轮不改执行器。

另一个既有陷阱是 [b_cases_v3.json 的 b09](<../../../experiments/data/b_cases_v3.json>)：负数是否合法尚未说明，`domain=unknown_sign`。它不能被改称“原题仅允许非负、迁移题允许全负”的已审核题对；未说明前提不等于已经确认的非负合同。

**材料门槛结果：0/2 个场景完成合格配置。** 这是本轮停止的直接原因。没有用生成题、额外前置知识或旧题重命名填补缺口。

## 3. 四种典型暴露历史 × 两个场景

下表固定的是**来源可追溯的重组条件**，不是八名学生的实际历史。历史真实模型输出与 F05 模拟事件明确区分。H1 含两类提示，H4 把已知无关内容与未知覆盖分开，因而四种历史仍覆盖用户要求的五类内容。组合历史在本轮为研究材料，不导入 F05。

| 场景/历史 | 来源及暴露内容 | 按明确规则能做的判断 | 仍需保留的范围 |
|---|---|---|---|
| S-H1 概念＋不完整追问 | general_range＋partial_range，原文见下 | 通用 range 停止边界与具体追踪问题；未给出 n+1 的修复 | 不能称污染；也不能用复述刚给出的 range 规则证明独立发现该规则 |
| S-H2 关键操作 | key_range：历史 S1_04 明确给 `range(1,n+1)`、`s += i` | 同为“包含 n”的端点要求已经直接覆盖 | 列表生成还需列表操作；不能推导整道 S-N 已完全被代做 |
| S-H3 完整实现 | sum_pair 中 `loop_end_train.reference`，下列完整代码 | 同合同 SUM 的实现可直接套用；n=0、1 重测不成为新算法证据 | **构造的暴露条件**，来源是历史冻结参考代码，未声称原学生实际收到此帮助 |
| S-H4 无关内容＋历史未知 | key_max 的 MAX 初始化建议；unknown_coverage 的外部帮助未知声明 | MAX 初值操作未覆盖 SUM 端点；该已知事件不应排除 SUM | 未知外部帮助没有原文，不可被“已知事件无关”覆盖为无帮助 |
| M-H1 概念＋不完整提示 | general_max＋partial_max，原文见下 | 最大值的性质/核查提示；没有明确初始化及完整算法 | 不把概念学习排除；性质提示覆盖程度需要按目标要求看，不能一律认定为 F |
| M-H2 关键操作 | key_max：历史 S1_03 明确用 `best=xs[0]`，保留原循环 | 非空 MAX 的初始化步骤已直接覆盖 | 没有暴露 cap 筛选和无候选分支；M-C 是否适用仍待审 |
| M-H3 完整实现 | full_max：F05 T02 首答前完整代码，见下 | M-N 同合同 MAX 的可直接套用解法已经暴露 | 这是冻结模拟帮助事件，不是真实学习者收到 AI 答案的观察 |
| M-H4 无关内容＋历史未知 | general_range 的 range 概念讲解；unknown_coverage | 该讲解没有提供 MAX 的初始化/比较解法，不因“都是 Python”判污染 | 外部帮助未知依旧未知，不能认证独立或补造其内容 |

### 3.1 原句与完整材料

G/P 级帮助摘录如下；链接文件是完整来源，不能只给某个方法摘录而给另一个方法全文。本轮没有模型方法消费这些材料。

general_range，历史真实模型回复 F01 最终验收 S1_T01（仅本机证据：`experiments/feature_validation/F01_response_adaptation/final_acceptance/responses/S1_T01/raw_response.json`；不随 Git 分发）：

> 你对E01的解释是对的。提示：range的第二个参数表示“第一个不取的数”，不是“最后一个取的数”。那么，最后一个参与相加的数与这个边界有什么关系？

partial_range，历史真实模型回复 [F02 S1_C01_FIRST](<../../../experiments/feature_validation/F02_dynamic_questioning/responses/S1_C01_FIRST/raw_response.json>)：

> 当 n=3 时，range(1, n) 会依次产生哪些 i？题目要求相加哪些整数？对比这两组数，差在哪里？

general_max，历史真实模型回复 F01 最终验收 S1_T12（仅本机证据：`experiments/feature_validation/F01_response_adaptation/final_acceptance/responses/S1_T12/raw_response.json`；不随 Git 分发）：

> 如果返回 -5，它虽然在原列表里，却比 -2 小。这说明返回值与列表中每个元素之间还应满足什么关系？

partial_max，冻结模拟帮助事件 F05 T02 提示（仅本机证据：`experiments/feature_validation/F05_independent_assessment/results/formal_v1/T02/events/000003.json`；不随 Git 分发）：

> 先核对返回值是否来自输入列表。

K 级原文所在的历史真实输出：

- S1_04 event_audit.json（仅本机证据：`experiments/round5_ui_model/results/cli_automation_20261009T094819533718Z/generation_v4/S1_04/event_audit.json`；不随 Git 分发） 的 `final_messages[0]` 给出“再将循环上界改为`n + 1`，更新语句改为`s += i`”。它还含原因、解释和追问；判读不能忽略这些上下文。
- S1_03 event_audit.json（仅本机证据：`experiments/round5_ui_model/results/cli_automation_20261009T094819533718Z/generation_v4/S1_03/event_audit.json`；不随 Git 分发） 的 `final_messages[0]` 给出“将初始化改为 `best = xs[0]`，原循环可以保留，因为列表保证非空”。这是具体操作，不只是通用最大值概念。

S-H3 完整暴露条件取自旧冻结题的参考实现，并非新生成题目：

```python
def solve(n):
    s = 0
    for i in range(1, n + 1):
        s += i
    return s
```

M-H3 为 F05 中实际保存的模拟帮助正文：

```python
def solve(xs):
    best = 0
    for x in xs:
        if x > best:
            best = x
    if max(xs) < 0:
        return max(xs)
    return best
```

这里存在一个不利于 B 的简单情形：对只差循环端点的 SUM 修复题，直接给出 n+1 已经完成关键修复。把 K 与 F 分成两个漂亮的标签，不一定产生两种不同选题动作。对同合同 MAX，给出初始化建议和完整实现也可能同样覆盖候选题的主要差异。**分类更细不自动等于选题更好。**

## 4. B、B0、B1 的检查状态

本轮按用户当前命名：B 是“帮助内容语义映射＋暴露感知选题”；B0 是普通 LLM 在相同材料和约束下直接选择；B1 是教师标签式明确规则。没有沿用 P2 初稿不同的基线编号。

| 方法 | 本轮完成的部分 | 没有完成的部分 |
|---|---|---|
| B | 固定所需字段：帮助原文/来源/时间、题目作答要求、已覆盖要求、剩余要求、前置知识与未知 | 没有调用语义映射模型，没有运行选题器 |
| B0 | 固定公平约束：相同候选、完整帮助原文、相同“不具备可选题可拒选”权利 | 没有真实模型输出，不能评价准确率 |
| B1 | 对原文作规则可处理范围的静态审核，列出上述八个重组条件的已覆盖/待定要求 | 标签是 Codex 的探索性建议，没有独立教师标签；没有合格题库上的选题实测 |

强 B1 不能被降格为关键词匹配。它可以使用教师对题目要求、帮助级别、直接解法覆盖和前置知识的标注，也必须允许未知与拒选。所有方法若有后续正式比较，都要面对同样的完整原文与候选，不给 B 额外执行事实或教学审定。

现有明确例子中，教师可以通过具体编辑、完整代码、合同相同、知识前置缺失等可核对标签描述问题，无须复杂选择算法。留下的争议是“概念/关键步骤覆盖到何种程度”“帮助缺失”“题对是否公平”。前两者没有独立标签真值，后一者不能靠 LLM 完成认证。**没有建立一个经过审核、B1 实际处理失败且 AI 映射可能改进的选题单元。** 这不是宣称规则已解决所有自由表述，只是本轮不具备启动模型测试的依据。

材料审核已经触发停止条件，因此不再用八个重组条件跑模型、追加题目或搜索新的开源项目。也不报告“B=B0=B1 选择相同”：三者未完成选题对照。

## 5. 按评价重点记录结果与失败

| 用户评价项 | 本轮结果 | 证据边界 |
|---|---|---|
| 可直接迁移的答案/解法暴露 | 完整 MAX 代码与同合同 M-N 有明确复用关系；n+1 具体步骤覆盖 SUM 端点要求 | 原文及源码可核对；没有人工教学标签，不报识别准确率 |
| 是否误伤概念学习 | 冻结规则不因 G/P 或共享概念自动排除 | 只是规则约束；没有模型测试，不能报误伤率 0 |
| 是否保留未知 | 外部帮助未知、占位原文、未说明负数前提均保留 | 没有将未知映射为“无帮助”或“已泄露完整答案” |
| 候选题前置知识/难度 | 两个场景均未完成合格配置 | 列表/append、筛选/None、题型差异以及条件题缺失 |
| 是否优于普通 LLM/教师规则 | **未验证，不能声称优于或相当** | B/B0 没有运行；B1 没有独立标签及合格题库 |
| 人工审核成本 | 独立人工审阅者 0；实际教学审核时间未知 | 未来必须审题、审要求覆盖及分歧；不能以 0 次模型调用冒充已节省教师成本 |
| 学习/迁移测量效果 | **未验证** | 真实学习者 0；没有有效迁移测验或学习效果数据 |

已发现的失败/否定案例：

1. **同合同 MAX＋完整 MAX 代码**：候选换 ID 或变量名不能排除机械套用；若 B 仍认证“独立推导”，机制直接失败。
2. **筛选 MAX 在 None/筛选未教时被选择**：这是前置知识失配，不能用低分证明识别了理解边界。当前材料已触发这一阻断。
3. **SUM→列表生成被当端点条件变化**：端点规则没有变化；列表生成与题型差异可能解释成绩差异。
4. **range 通用讲解或最大值性质提示一律判污染**：误伤正常学习；本轮只冻结此失败标准，未测系统犯错率。
5. **只因已知事件无关就清除 unknown 外部帮助**：把可见性不足改成独立认证；原记录不支持。
6. **K/F 标签不同但覆盖同一目标操作**：细分类可能没有新增决策价值；不能用多几个分类标签证明 B 胜过 B1。
7. **强规则同样识别暴露而成本更低**：将来若经公平对照成立，独立 AI 选题机制 NO-GO；本轮未实际证明这一结果。

## 6. 实际工作量与停止位置

| 项目 | 本轮记录 |
|---|---:|
| 源材料冻结 | 18 个既有文件的 SHA-256 快照 |
| 概念场景 | 2 |
| 暴露历史 | 8 个来源可追溯的重组条件 |
| 合格的完整场景配置 | 0/2 |
| 新模型调用、模型 token/请求费用 | 0；没有发送模型请求 |
| 新学生程序执行、Docker 操作 | 0 |
| 独立人工教学审查、真实学习者 | 0 |
| 新题生成、新网页/Provider/沙箱修改 | 0 |

“历史真实模型输出”只表示重用已有回复，没有重新调用。读取帮助日志、核对源码及文件哈希属于本轮审查；不是训练数据、学生实验或 B/B0/B1 的准确率试验。模型的正式收费数据不存在，因为没有新请求；也不把本对话撰写报告的开销算成比较实验费用。

停止位置是**材料门槛**。NO-GO 的范围是当前 P2-B 方案进入扩样、正式机制测试或产品开发；并非证明所有帮助暴露研究无用。完整解法复用的问题可以保留为教学审核要求，但本轮没有证明 AI 的必要性、成本优势或有效迁移测验。

## 7. 冻结依据与复核方式

快照时间：2026-10-11T12:30:18.073804+00:00，即北京时间 2026-10-11 20:30:18。这是本轮停止门槛材料快照，**不是尚未开展实验的预注册结果**。来源版本、八个历史组合、规则和审查范围记录在下面；没有模型输出可据以调整规则。18 个文件本轮只读。

```json
{
  "version": "P2_B_material_gate_v1",
  "captured_utc": "2026-10-11T12:30:18.073804+00:00",
  "scope": "source-and-material-audit-only",
  "model_tests_started": false,
  "scenes": [
    {
      "id": "SUM_LOOP_END",
      "original": "sum_original",
      "near": "sum_pair:loop_end_assessment",
      "changed_condition": null,
      "gate": "not_ready",
      "reasons": [
        "near adds list construction and answer-choice reading",
        "no frozen reviewed condition-change item found"
      ]
    },
    {
      "id": "MAX_CANDIDATE_SET",
      "original": "max_original",
      "near": "max_question:F05_MAX_01",
      "changed_condition": "prior_design:section4.3 cap/None illustration",
      "gate": "not_ready",
      "reasons": [
        "near repeats original MAX contract",
        "condition-change illustration adds filtering and None without prerequisite evidence"
      ]
    }
  ],
  "histories": {
    "S-H1": [
      "general_range",
      "partial_range"
    ],
    "S-H2": [
      "key_range"
    ],
    "S-H3": [
      "sum_pair:loop_end_train.reference (constructed exposure condition, not historical help event)"
    ],
    "S-H4": [
      "key_max",
      "unknown_coverage"
    ],
    "M-H1": [
      "general_max",
      "partial_max"
    ],
    "M-H2": [
      "key_max"
    ],
    "M-H3": [
      "full_max"
    ],
    "M-H4": [
      "general_range",
      "unknown_coverage"
    ]
  },
  "rules": [
    "general concept or incomplete hint is not automatically direct-solution exposure",
    "key operation maps to item requirement; preserve residual requirements instead of blanket rejection",
    "full solution under identical contract cannot establish independently derived algorithm",
    "source/history/relevance unknown remains unknown; question_seen alone is not full-answer exposure",
    "item prerequisite and format audit is required before exposure-aware selection",
    "stop model comparison when eligible item pairs are unavailable"
  ],
  "labels_origin": "Codex source audit; not independent human teacher labels",
  "sources": {
    "sum_original": {
      "path": "experiments/feature_validation/F02_dynamic_questioning/cases/C01.json",
      "sha256": "9439ccfd7b5effa8bc94ed1e54b264c965387ffb036fb71e9256282c2538dec3"
    },
    "sum_pair": {
      "path": "experiments/round4/data/a_study.json",
      "sha256": "5b524c45637f0c250669777888fe183dd63b86ffaaef214621b988689f002917"
    },
    "max_original": {
      "path": "experiments/round5_ui_model/cases/03.json",
      "sha256": "2d32b9bbcdd673fd946cbe7cd6c1c897daab4e3d0c95bed3af248df5fa2dbc83"
    },
    "max_question": {
      "path": "experiments/feature_validation/F05_independent_assessment/data/question.json",
      "sha256": "2381326b839c758edf87dc0a583ab2d8850c4038260921bfde4d64f035f3ec76"
    },
    "max_registry": {
      "path": "experiments/feature_validation/F05_independent_assessment/data/registry.json",
      "sha256": "60165cf70a0ba43bf4b162977d7c6fb976e95272750702cf3286a042ac31fcec"
    },
    "general_range": {
      "path": "experiments/feature_validation/F01_response_adaptation/final_acceptance/responses/S1_T01/raw_response.json",
      "sha256": "04476187d057f304931d3440bed255ff5c9928897d30e1cf49eef26cdd314948"
    },
    "partial_range": {
      "path": "experiments/feature_validation/F02_dynamic_questioning/responses/S1_C01_FIRST/raw_response.json",
      "sha256": "234e54ea3fa3703b0b96abd1dccb1191df40e99bae299cd301fc0e0d2d2abedc"
    },
    "key_range": {
      "path": "experiments/round5_ui_model/results/cli_automation_20261009T094819533718Z/generation_v4/S1_04/event_audit.json",
      "sha256": "f42084ad679a0aab869b1866ebbb09e4bd2d1168dbf414caa0701109eea31a5b"
    },
    "general_max": {
      "path": "experiments/feature_validation/F01_response_adaptation/final_acceptance/responses/S1_T12/raw_response.json",
      "sha256": "887c51263e06045a23d7a09199b671fe339655bc64c1bdf71874ff72a0846a7b"
    },
    "key_max": {
      "path": "experiments/round5_ui_model/results/cli_automation_20261009T094819533718Z/generation_v4/S1_03/event_audit.json",
      "sha256": "7ec675f0823a8e48b9599c74712a4a8c67a35d99e4be1455a86283157d045505"
    },
    "partial_max": {
      "path": "experiments/feature_validation/F05_independent_assessment/results/formal_v1/T02/events/000003.json",
      "sha256": "aef26ff421fd04dfb0a53fb1a249463e5a33211e4bff268f923171fb1ccb9baa"
    },
    "full_max": {
      "path": "experiments/feature_validation/F05_independent_assessment/results/formal_v1/T02/events/000004.json",
      "sha256": "fe72d134b1b2a26347a37959fe94b0c67ce206a0965dc5d3bdd4266945e2adb5"
    },
    "placeholder": {
      "path": "experiments/feature_validation/F05_independent_assessment/results/formal_v1/T01/events/000002.json",
      "sha256": "489a191bb1f178e65e18f5ff5677ebaf171d28233ac1f87e2bcdcd2af1e8b201"
    },
    "unknown_coverage": {
      "path": "experiments/feature_validation/F05_independent_assessment/results/formal_v1/T03/session.json",
      "sha256": "7b1279c13861d0187ebe8ec965fcbb1e791567825a9c9ea96f5d9188344f3e82"
    },
    "policy": {
      "path": "experiments/feature_validation/F05_independent_assessment/records.py",
      "sha256": "3d89d1b0d0b4db76a6a80bce959376996f5c9ce4b630397d3868daad4425ec26"
    },
    "prior_design": {
      "path": "P2_innovation_candidates.md",
      "sha256": "d324a39b1c7113a19b6d9f24ac9018cfdef97127d4a660c61e51e50934eb6647"
    },
    "max_result": {
      "path": "experiments/feature_validation/F05_independent_assessment/results/formal_v1/T02/first/result.json",
      "sha256": "e0306d00403821b133f92a7144ebc592f0d50fd8b3e64b73526078ca8816168b"
    },
    "unknown_contract": {
      "path": "experiments/data/b_cases_v3.json",
      "sha256": "a23222bfaf6ec478486a9f5cabe5e1f555c98b6a107a01dc98429988ac1e59c0"
    }
  }
}
```

以下复核代码只读取本报告和来源文件，不写入旧系统，也不运行学生代码。在项目根目录用 `python -B -X utf8` 运行即可：

```python
import hashlib
import json
from pathlib import Path

report = Path("P2_B_feasibility.md").read_text(encoding="utf-8")
start = report.index("```json\n") + len("```json\n")
frozen = json.loads(report[start:report.index("\n```", start)])
for key, entry in frozen["sources"].items():
    actual = hashlib.sha256(Path(entry["path"]).read_bytes()).hexdigest()
    if actual != entry["sha256"]:
        raise ValueError("Frozen source changed: " + key)

items = json.loads(Path(frozen["sources"]["sum_pair"]["path"]).read_text(encoding="utf-8"))
loop_items = [q for q in items["questions"] if q["concept"] == "loop_end"]
assert len(loop_items) == 2
assert all(q["review"]["expert_review"] == "pending" for q in loop_items)
assert len(frozen["histories"]) == 8
assert frozen["model_tests_started"] is False
assert all(scene["gate"] == "not_ready" for scene in frozen["scenes"])
print(json.dumps({
    "source_hashes_verified": len(frozen["sources"]),
    "loop_pair_expert_review": "pending",
    "history_conditions": len(frozen["histories"]),
    "model_tests_started": False
}, ensure_ascii=False))
```

复核只确认来源未变、材料元数据与本轮范围，不认证教学等价性。交付前实际运行上述读取检查，退出码为 0，输出如下：

```text
{"source_hashes_verified": 18, "loop_pair_expert_review": "pending", "history_conditions": 8, "model_tests_started": false}
```

另行检查两份报告的 UTF-8 内容与 21 个本地文件链接，缺失链接 0。以上不是 B 的选题成功数，也不是教学测量验收。
