# P2-R1 第一轮技术门槛验证

日期：2026-10-11。只做两项构造任务的离线门槛检查；不开发网页、不接入 V2、不扩展执行合同。本报告与 [下一步决策](<P2_R1_next_decision.md>) 是本轮仅有的交付文件。

<!-- R1_RESULT_SUMMARY_START -->
**结论：当前 R1 独立机制 NO-GO，停止扩样和开发。** 在两项作者构造任务的离线检查中，确认后条件层与显式规则基线 28/28 同判；没有找到需要 AI 才能补上的语义差异，也没有审核减负证据。真实实验模型调用 0，候选程序执行 0；B0 未运行。

这不是普通 LLM 已实测胜出，也不是对所有需求理解工具的否定。本轮只支持：当前增加的结构化解释层没有显示超出明确规则的增量，未达到继续投资门槛。
<!-- R1_RESULT_SUMMARY_END -->

## 1. 创新最小单位与本轮实际测到什么

拟议 R1 的最小单位是：**把需求转换为允许变化区域、必须满足的保留性质和未知事项；确认后用这些条件解释双版本行为差异。** “允许变化”只允许指定目标改变，并不豁免同一输入上的其他性质。

已有能力与拟新增部分分开：

| 部分 | 归属 | 本轮状态 |
|---|---|---|
| 双版本行为比较、参数副作用、符号输入探索 | CrossHair 等已有差分工具 | 未安装、未运行；不认领创新 |
| 属性输入生成、反例缩减 | Hypothesis 等已有工具 | 未安装、未运行；本轮输入固定 |
| 来源哈希、版本关联、真实执行/未知记录 | 本地 F03/F04/P1 已有能力 | 只参照结构与边界；未扩展 |
| 自由表述需求 → 有原句支持的条件 → 用户确认 | 拟议 R1 的语义与审核阶段 | 本轮未调用模型；无真实用户确认 |
| 确认后的条件 → 允许/保留/回归/未知判断 | 拟议 R1 的条件解释层 | 用预冻结条件进行实际离线规则运行 |
| 需求 ID、JSON、日志、哈希 | 普通工程记录 | 用于复核，不计入创新 |

本轮实际比较的是 **R1-post-confirm（作者填写条件后的解释层）** 与 **B1-rule（预写显式业务规则）**。不能把结果称为完整 AI R1 的成绩。作者是本轮研究助手；这些“确认后条件”是模拟输入，不是独立教师编写或用户实际批准。

已有技术依据沿用 [P2 重新选题报告](<P2_project_reselection.md>) 中已检查的 [CrossHair 差分源码](https://github.com/pschanely/CrossHair/blob/35e504cc5b09846242e9ac67d10219b67d587a65/crosshair/diff_behavior.py)、[Hypothesis](https://github.com/HypothesisWorks/hypothesis/blob/82fa40ada6bc83480a746890a40bb3d708ba8f03/README.md) 与 [需求到测试判定研究](https://arxiv.org/html/2607.10277v1)。本轮没有重新检索或运行这些项目。需求转断言与差分测试本身已有先行工作；必须有强基线无法同成本完成的实际增量，才能支持本项目继续。

## 2. 执行边界与证据等级

当前 [sandbox_contract.py](<web_lab/sandbox_contract.py>) 仅接受 V2 已审核的 C01/C03、SUM `solve(n)`、整数 n=0..8。下面的字符串列表函数和双参数运费函数均不满足合同。

**未在宿主执行任何旧代码、正确补丁或错误补丁。** 未调用 Docker、未修改白名单、未将业务任务编码成 SUM 输入绕过合同。对六份候选源码只计算哈希并做 `ast.parse` 语法解析；解析不执行函数。

使用用户允许的替代路径：作者逐句审查明确需求、逐行推演这六个短函数，事前冻结返回值与输入前后快照；随后宿主只执行可信的离线分析脚本，读取数据并验证规则。原始记录统一注明 `author_manual_trace_NOT_program_execution`。

因此：

- 程序“观察”是**人工式静态推演材料**，不是容器输出，不是独立执行事实。
- 离线脚本实际运行结果可复核；它证明规则怎样处理给定快照，不能证明快照等同真实运行。
- 反例只有需求条款＋源码推演支持，**没有相应隔离执行证据**。未来若获准继续，新的受限执行合同是独立工程前提。
- 未支持输入的既有代码表现不生成业务规范；保留 UNKNOWN。没有反例也不宣称正确。

## 3. 材料来源、需求审查与冻结顺序

两个任务都是本轮**作者构造样例**，不是生产 Bug、AI 真实补丁历史或既有教学数据。任务 D 沿用重新选题报告中的演示设想，再补齐明确合同；任务 F 是新的运费规则小场景。独立人工需求审查人数为 0。

这里的需求审查是作者逐条自查：每个已知性质绑定原文，检查输入范围、合法变化、未说明事项与旧实现；不能替代用户的业务审定。独立参考的含义是**从需求推导，不从待评补丁输出反推答案**，不是“由另一位独立人员编写”。

冻结步骤：先写定原文、六个源码、14 个输入、42 份手工推演快照、金标、条件对象、B1 规则、B0 Prompt 和失败控制；写入本文附录；单独记录冻结 SHA-256；之后运行检查器。运行后仅填结果区，附录材料与检查器不调整。没有对失败样例事后改需求。

<!-- R1_FREEZE_RECORD_START -->
冻结时间：2026-10-11T15:23:36.831517+00:00（UTC，离线分类运行之前）。
- 材料 SHA-256：`e40c8b9ab820ca76db6f94e2377bdd805b0e6c859c861db1327a5024192c9a0c`（12118 字节）。
- 检查器 SHA-256：`755134cda7b70b902eba10fa9dc0efc21e5a2a8cf8a0c3caeb2074b3bd50da78`（8045 字节，不含最后换行）。
- 此时尚未运行分类器、调用测试模型或执行候选代码。后续结果不得修改上述两个冻结代码块。
<!-- R1_FREEZE_RECORD_END -->

### 3.1 任务 D：通讯录标签忽略大小写去重

**原始合同**

- D-O1：输入为长度 0～6 的列表，每项为长度 1～4 的 ASCII 英文字母串。
- D-O2：按字符串原文完全相等去重，仅保留第一次出现的元素。
- D-O3：保留留下元素的原文和原先相对顺序。
- D-O4：不得修改输入列表。

**新要求**

- D-C1：重复判断改为忽略 ASCII 字母大小写。
- D-C2：仍保留第一次出现的原文、相对顺序；不得修改输入列表；输入范围不变。

旧代码：

```python
def solve(xs):
    out = []
    for x in xs:
        if x not in out:
            out.append(x)
    return out
```

正确补丁：

```python
def solve(xs):
    seen = set()
    out = []
    for x in xs:
        key = x.lower()
        if key not in seen:
            seen.add(key)
            out.append(x)
    return out
```

需求外回归补丁：

```python
def solve(xs):
    return sorted({x.lower() for x in xs})
```

**允许变化区域：**存在原文不同、ASCII 忽略大小写后相同的两个元素。仅完全相同的重复项不是新增变化区域。该区域允许合并重复，不允许把保留原文改为小写或排序。

**独立需求参考：**对每个 ASCII 大小写等价组，取原列表中下标最小的元素；按下标递增输出这些元素的原文；输入列表保持原状。这个下标定义从 D-O2/O3/O4/C1/C2 推导，先冻结参考表，再用于核对给定快照，未调用待评补丁生成 expected。

| 输入 ID | 输入 xs | 旧返回 | 正确补丁返回 | 回归补丁返回 | 事前判定 |
|---|---|---|---|---|---|
| D0 | `[]` | `[]` | `[]` | `[]` | 两者在该观察上保留 |
| D1 | `["B","b","A"]` | `["B","b","A"]` | `["B","A"]` | `["a","b"]` | 正确补丁合法变化；错误补丁破坏原文和顺序 |
| D2 | `["b","a"]` | `["b","a"]` | `["b","a"]` | `["a","b"]` | 排序产生非目标回归，大小写比较根本不需要变化 |
| D3 | `["B"]` | `["B"]` | `["B"]` | `["b"]` | 单项原文被改，小写结果看似合理但不合法 |
| D4 | `["b","b","a"]` | `["b","a"]` | `["b","a"]` | `["a","b"]` | 完全相同重复项不能授权重排 |
| D5 | `["a","A"]` | `["a","A"]` | `["a"]` | `["a"]` | 两个补丁在该输入均为合法变化；不能据此放行整个错误补丁 |
| DU | `["ß","SS"]` | `["ß","SS"]` | `["ß","SS"]` | `["ss","ß"]` | 超出 ASCII 范围，两者 UNKNOWN，不设正确输出 |

所有快照的输入前后相同，来自手工源码推演；只记录值变化，没有对象身份、额外 I/O 或运行时资源证据。原始合同也未要求“必须返回新对象”，不能自行加入。

旧实现自查：在冻结的 6 个范围内输入上符合旧需求；循环按原文比较并保留首次出现，未见旧合同违规。它区分大小写是旧需求，不能称为旧 Bug。未执行，不宣称完成全域程序证明。

### 3.2 任务 F：小店降低非会员免运费门槛

**原始合同**

- F-O1：`amount_cents` 是 0～20000 的整数分；`is_member` 严格为 True 或 False；返回整数分。
- F-O2：会员一律免运费。
- F-O3：非会员订单金额满 10000 分（含）免运费，不满收 1000 分运费。

**新要求**

- F-C1：非会员免运费门槛改为 8000 分（含）。
- F-C2：会员免运费和 1000 分基础运费不变，其余合同不变。

旧代码：

```python
def solve(amount_cents, is_member):
    if is_member or amount_cents >= 10000:
        return 0
    return 1000
```

正确补丁：

```python
def solve(amount_cents, is_member):
    if is_member or amount_cents >= 8000:
        return 0
    return 1000
```

需求外回归补丁：

```python
def solve(amount_cents, is_member):
    if amount_cents >= 8000:
        return 0
    return 1000
```

**允许变化区域：**非会员且 `8000 <= amount_cents < 10000`。会员在这个金额区间仍属于必须免运费的保留性质；目标门槛调整不能删除会员优惠。

**独立需求参考：**会员为 0；非会员金额 ≥8000 为 0，否则为 1000，单位为整数分。旧参考只将非会员门槛换回 10000。两张分段表从文字推导，与待评代码的返回值来源分离；但作者相同，参考没有独立业务人员复核。

| 输入 ID | (金额分, 会员) | 旧返回 | 正确补丁返回 | 回归补丁返回 | 事前判定 |
|---|---|---|---|---|---|
| F0 | `(0, False)` | 1000 | 1000 | 1000 | 两者在该观察上保留 |
| F1 | `(7900, False)` | 1000 | 1000 | 1000 | 两者在该观察上保留 |
| F2 | `(8000, False)` | 1000 | 0 | 0 | 两者在该输入均为合法变化，包括门槛边界 |
| F3 | `(9000, False)` | 1000 | 0 | 0 | 合法降门槛，不能将与旧版不同误报为回归 |
| F4 | `(3000, True)` | 0 | 0 | 1000 | 回归补丁漏掉会员免运费；1000 是正常运费值，但用于该用户违反保留要求 |
| F5 | `(12000, False)` | 0 | 0 | 0 | 两者在该观察上保留 |
| FU | `(-100, False)` | 1000 | 1000 | 1000 | 超出金额范围；即使新旧相同也 UNKNOWN，不认证退款处理 |

不加入优惠券、计税、币种转换等业务条件。金额是券前还是券后未定义，这个函数不能回答；不据此增加新的确定性断言。F 函数输入为不可变标量，原文没有额外的可变对象副作用合同，本轮不把参数快照相等计为新的业务性质。

旧实现自查：冻结的 6 个范围内输入符合旧需求；未见旧合同违规。非会员 9000 分收运费是原规范，不能认作旧实现错误。没有实际执行验证。

## 4. 事前冻结的对照与评价

| 方法 | 原始材料 / 工具 | 实际运行范围 | 不得推断的内容 |
|---|---|---|---|
| R1-post-confirm | 同样原文、源码、14 个固定输入快照；作者填写且原句绑定的条件对象 | 解释层按条件分类；不读取 evaluator-only 金标 | AI 提取可靠性、真实用户确认、审核减负 |
| B0 | 同样原文、源码和离线快照工具；附录冻结优化 Prompt | 只有在出现具体语义转换差异时才启动真实模型 | 未调用就不能给正确率，不能称“B0 已胜出/等效” |
| B1-rule | 同样输入快照；预写明确业务规则，不读取金标 | 直接规则分类，作为人工规则能力的离线替身 | 本轮规则由助手预写，不是教师实际作业；不能报人工耗时优势 |

所有已运行方法只读取相同的 7 输入/任务，不进行自动生成、额外搜索或自适应加题。候选版本源码和需求信息完全相同。金标及需求参考位于 `evaluator_only`，只在方法输出后做核对，不传给分类函数。R1 的条件对象不是额外业务事实，而是要评估的作者填写中间表示；使用它恰恰意味着**跳过了尚未证明的 AI 语义提取阶段**。

账本的 `good/bad` 是作者角色标签，分类函数不读取候选角色名称或金标；作者仍知道材料，所以不是独立盲测。B0 本轮未接收任何材料；若未来另行测试，须先匿名为补丁 P/Q，不能把正确/错误标签交给模型。

B1-rule 使用独立直接表达式：D 用原文列表＋已出现小写键构造参考；F 用会员/金额分段规则。R1 逐条解释条件对象。两者都需要正确的需求到规则转换；不同写法不会自动成为不同创新机制。

冻结标签与停止规则：

- `ALLOWED_CHANGE`：范围内，满足全部新合同与保留性质，变化属于明确授权目标。
- `PRESERVED`：范围内，给定观察符合新合同且与旧观察相同；仅表示该观察。
- `REGRESSION`：给定观察破坏明确保留要求或出现未授权改变。
- `CHANGE_NOT_IMPLEMENTED`：保持旧结果却漏做明确要求的新变化。另设两个“旧代码作为新补丁”控制，避免把无差异当正确。
- `UNKNOWN`：范围外输入或未说明性质；没有正确输出参考，不凭旧代码补规范。
- 对未知条件类型必须报未支持/UNKNOWN，不允许静默放行；脚本只支持本轮列出的业务规则，**不是自由条件编译器**。
- 事前审定的负例漏报、合法改变误报、UNKNOWN 被伪造确定结论，均不扩样。
- 若显式规则已完整覆盖，并且 R1 解释层没有额外处理能力或审核减负证据，停止；不为了补齐模型表格强行调用 AI。
- 若要以完整 AI R1 声称增量，必须有同输入、同工具、同预算的 B0 真实输出以及真实审核成本；本轮没有就不声称。

逐条指标不合成创新分数：需求外回归、合法变化误报、来源支持、保留遗漏、UNKNOWN、反例证据、人工审查与模型/执行成本。附录源 ID 检查只能验证“引用存在”；语义是否准确由上面的作者逐句审查支持，**不是 AI 自评认证或自动语义证明**。

## 5. 实际离线运行与对照结果

<!-- R1_ACTUAL_RESULTS_START -->
首次且唯一一次离线分类运行完成；记录时间：2026-10-11 15:23:45 UTC。进程退出码 0，进程工具墙钟约 0.2550144 秒，脚本计时 0.001103 秒。两者仅为同一次合并分析运行，**不是 R1/B1 的独立性能比较**。

| 指标（快照级） | R1-post-confirm 实际 | B1-rule 实际 | B0 |
|---|---:|---:|---|
| 明确需求外回归检出 | 5/5 | 5/5 | 未运行 |
| 合法变化误报 | 0/7 | 0/7 | 未运行 |
| 范围内保留观察 | 12/12 | 12/12 | 未运行 |
| 范围外保留 UNKNOWN | 4/4 | 4/4 | 未运行 |
| 全部冻结分类匹配 | 28/28 | 28/28 | 未运行 |
| 旧代码作为补丁：目标变更遗漏控制 | 2/2 判为未实现变更 | 2/2 判为未实现变更 | 未运行 |
| 真正 AI 条件提取准确性 | 未测试 | 不适用 | 未测试 |
| 独立人工审查/审核耗时 | 无实际样本 | 无实际样本 | 无实际样本 |
| 隔离程序执行支持的反例 | 0 | 0 | 0 |

快照来自 **2 个错误补丁**，不能将 5 个错误输入说成 5 个独立任务；28 个判定也不是 28 个真实用户实验。正确补丁的 4 个合法变化与错误补丁在局部输入上的 3 个合法变化共同构成 7 个观察。错误补丁的局部合法不代表整份补丁获批。

逐行实际输出：

| 输入 ID | R1 正确补丁 | B1 正确补丁 | R1 回归补丁 | B1 回归补丁 |
|---|---|---|---|---|
| D0 | 保留 | 保留 | 保留 | 保留 |
| D1 | 合法变化 | 合法变化 | 回归 | 回归 |
| D2 | 保留 | 保留 | 回归 | 回归 |
| D3 | 保留 | 保留 | 回归 | 回归 |
| D4 | 保留 | 保留 | 回归 | 回归 |
| D5 | 合法变化 | 合法变化 | 合法变化 | 合法变化 |
| DU | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| F0 | 保留 | 保留 | 保留 | 保留 |
| F1 | 保留 | 保留 | 保留 | 保留 |
| F2 | 合法变化 | 合法变化 | 合法变化 | 合法变化 |
| F3 | 合法变化 | 合法变化 | 合法变化 | 合法变化 |
| F4 | 保留 | 保留 | 回归 | 回归 |
| F5 | 保留 | 保留 | 保留 | 保留 |
| FU | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

两项错误补丁分别在 D1/D2/D3/D4 和 F4 被阻断；正确补丁在已定义快照上没有发现违规，但保留 DU/FU 未知，不能颁发“全域正确”。D1 尤其重要：输入位于允许合并区，系统仍检查首条原文/顺序；它没有把整个输入区域所有变化都当合法。F3 的 1000→0 被接受，F4 的 0→1000 被阻断。

两个冻结控制直接把旧版观察当候选：
- D1 保留三项而不做大小写合并 → 两方法均 `CHANGE_NOT_IMPLEMENTED`。
- F2 仍收 1000 分而不执行新门槛 → 两方法均 `CHANGE_NOT_IMPLEMENTED`。
这只检查“无差异不能自动通过”；不是新增业务任务或运行旧函数。

**来源与保留检查。** 条件对象中的 11 个规则对象、20 个原文引用均指向冻结原句。作者逐句核对后，D 的首条原文/顺序/输入不变及 F 的会员免运费/非会员基础费/返回类型都有对应规则。自动检查只是引用存在性；没有测试“模型会不会遗漏这些规则”。输入不变在所有快照均为真，本轮没有变异输入的负例，因此不能声称验证了该性质的检出能力。

首次运行 stdout 摘要如下；逐行结果与控制结果已完整列在上表和说明中，六个源码摘要另列，未复制重复数组：

```json
{
  "material_sha256": "e40c8b9ab820ca76db6f94e2377bdd805b0e6c859c861db1327a5024192c9a0c",
  "tasks": 2,
  "source_syntax_parses": 6,
  "manual_version_snapshots": 42,
  "old_requirement_consistency_checks": 12,
  "decisions_per_method": 28,
  "R1_B1_equal": 28,
  "frozen_label_matches_per_method": 28,
  "label_counts": {
    "PRESERVED": 12,
    "ALLOWED_CHANGE": 7,
    "REGRESSION": 5,
    "UNKNOWN": 4
  },
  "target_missed_control_decisions_per_method": 2,
  "actual_candidate_program_executions": 0,
  "actual_test_model_calls": 0,
  "B0_actual_model_status": "NOT_RUN",
  "independent_human_reviews": 0,
  "elapsed_seconds": 0.001103
}
```

源码身份（UTF-8，包括源码末尾换行；仅解析未执行）：

| 版本 | SHA-256 |
|---|---|
| D/old | `a61dc47d318639dce3df0d927d489fde397f0c30ac4f5622c9292ac5129b99b0` |
| D/good | `d2c207ab8cddfd0cca8ebeaf88e3dad612938cbaac6d60b8c94b1d22526a4031` |
| D/bad | `588fc4aa528ff627e155dfd4d5b727fc847fd4327b458a2da933209e52d58924` |
| F/old | `be3b7c4418ea06af22f216e88723cfa2fb2b64e033f3c624aa2819ec8a80b69a` |
| F/good | `1163d74e5e20b87cded789984171e0fbd8b2a7618c35163b8c04fd0b9a6bc0fa` |
| F/bad | `8ac71e6684718fe27257fa2d43789362f8278e362091a65b0503c78c14fce9e4` |

**模型阶段停止原因。** 两个显式合同不需要补猜业务语义；两种规则实现覆盖所有冻结已知标签和 UNKNOWN。R1 正确性依赖已经写对的条件，B1 直接写同样业务规则即可。没有剩余的、可事前指明的语义转换差异，按用户“先规则、必要时才模型”的门槛结束。不能据此给 B0 赋 100% 正确率，不能声称普通 Prompt 比 R1 更快，也不申请四任务扩样。
<!-- R1_ACTUAL_RESULTS_END -->

## 6. 失败、局限与成本

<!-- R1_FAILURE_COST_START -->
**实际未通过的是创新增量门槛，而不是已确认条件的分类正确率。** 28/28 同判说明在这两项材料与正确条件下，结构层没有改变结论；它不是 AI 提取有效或审核成本更低的证据。附录代码采用固定业务分派和属性断言，当前可实现部分属于普通规则工程；若再加自然语言入口，尚能具体指出的部分只是优化 Prompt＋现成验证，没有已证实的新算法或决策增量。

保留以下失败与局限，不把推测伪装成观察：

| 情形 | 本轮证据 / 状态 | 对 R1 的限制 |
|---|---|---|
| 解释层没有额外判断能力 | 实际：与 B1-rule 28/28 一致，两个目标遗漏控制也一致 | 当前独立机制没有显示增量 |
| 合法变更误报风险 | 实际：D1/D5、F2/F3 等变化被两者正确接受 | 说明要按需求判定，但无法独占为 R1 的收益；“所有 diff 都是 Bug”不是 B0 |
| 合理输出损害非目标性质 | 实际：D3 小写、D2 排序、F4 标准运费都违反原文并被两者抓到 | 用户问题具体，但普通显式规则同样解决 |
| AI 遗漏会员豁免或原文保留 | 未测试；条件由作者填写，遗漏可能把错误放行 | 本轮不能宣称条件提取可靠、没有遗漏 |
| 条件源 ID 正确但语义错误 | 只检查引用存在，作者做语义自查；没有独立审查 | 贴出处不会自动证明条件解释正确 |
| 旧实现本来就错 | 作者自查未见旧合同违规；没有这样的真实负例 | 旧结果不普遍可当规范；只验证了两份构造旧码 |
| DU 新旧不同、FU 新旧相同 | 实际均保留 UNKNOWN | 未说明边界不能靠新旧一致或不一致补成业务意图 |
| 执行与解释分离 | 机制层明确分开；事实层只有人工式推演 | 当前没有隔离运行支持的回归反例，不能宣称端到端可信 |
| 参数副作用、异常、超时、状态 | 这些未获得负例/真实执行覆盖 | 不借 CrossHair/P1 已有能力替本轮补成绩 |
| 跨业务自由规则翻译与编译 | 未实现，解释器只识别本轮固定种类 | 不是通用需求约束编译器，也没有算法新颖性依据 |
| 减少人工审核 | 未测量；独立人类参与为 0 | 不得把零人工参与写成零人工审核需求 |

**实际资源记录**

| 项目 | 数量 / 实际状态 |
|---|---|
| 作者构造任务、源码版本 | 2、6 |
| 冻结输入、手工推演版本快照 | 14、42 |
| 需求原句 | 11 条 |
| R1 中间规则对象与出处引用 | 11 个、20 处；它们需要语义审查，不当成收益 |
| 各方法快照判定 | R1 28、B1 28；另各 2 个目标遗漏控制 |
| 旧合同/参考一致性核对 | 12 个范围内旧观察；属于数据检查，不是旧代码运行 |
| 实际机制分类脚本运行 | 1 次；进程墙钟约 0.2550144 秒；另有只读哈希与文档核对，不计候选执行 |
| 真正实验模型调用 / 双 AI 评分 | 0 / 0 |
| 候选程序执行 / 新合同部署 / 新网页 | 0 / 0 / 0 |
| 独立人类审查、真实开发者样本 | 0、0 |
| 人工编写、确认、复核分钟数 | 未测量，不能用脚本毫秒数替代 |
| 模型实验费用 | 无额外实验调用；不估算本对话生成成本，也不报虚构 token/金额 |

R1 比直接规则多了条件对象、出处核对和确认流程，这是可见的额外工序；本轮没有证明这些工序减少审核。不能据此量化“R1 比 B0 更贵”，也不能用 JSON 长度、日志丰富或微秒差声称可靠性提高。

**本轮裁决：NO-GO（当前额外机制）。** 支持依据是规则已完整处理构造材料，R1 确认后层没有实际增量，AI 的额外作用与审核减负没有证据；按用户停止门槛 4 和“先规则”的规则结束。没有触发“已运行 B0 更好”的门槛 3，因为 B0 没运行；也没有把真实执行不足说成已观察到的需求解释混淆。此结论不证明自由需求翻译永远无价值，只决定当前方案不获得自动扩样或开发资格。

<!-- R1_ARTIFACT_CHECK_START -->
交付前只读核对（2026-10-11 15:29:45 UTC）：冻结材料与检查器 SHA-256 均未改变；六个展示源码块与冻结字符串一致；14 个实际输入行及本地链接核对通过；抽查的 13 个 V2/沙箱/Provider/F03/F04/验收文件 SHA-256 与本轮开始时一致。本轮写入仅两份交付文档。没有重跑分类器、运行候选代码或追加模型调用。
<!-- R1_ARTIFACT_CHECK_END -->
<!-- R1_FAILURE_COST_END -->

## 附录 A：实验前冻结材料

以下 JSON 是全部材料与判定标准的冻结对象。源码是字符串；快照是作者推演数据。前文可读表与本对象对应。冻结摘要针对代码块内容的 UTF-8 字节，不包含围栏、前后换行或运行结果区。

<!-- R1_FROZEN_MATERIALS -->
```json
{
  "schema": "P2-R1-offline-freeze-v1",
  "origin": "assistant-authored synthetic tasks; not real project history; no independent human approval",
  "evidence_contract": {
    "program_execution": false,
    "code_handling": "SHA-256 and ast.parse only; never exec/eval/import candidate code",
    "ledger": "manual symbolic/source trace; not container output",
    "model_calls": 0,
    "tool_budget": "7 fixed observations per task per method; no extra input search",
    "unknown": "outside explicit domain: no normative output; UNKNOWN even when old/new equal"
  },
  "public_tasks": [
    {
      "id": "D",
      "title": "通讯录标签去重",
      "clauses": [
        {"id":"D-O1","text":"输入为长度 0～6 的列表，每项为长度 1～4 的 ASCII 英文字母串。"},
        {"id":"D-O2","text":"按字符串原文完全相等去重，仅保留第一次出现的元素。"},
        {"id":"D-O3","text":"保留留下元素的原文和原先相对顺序。"},
        {"id":"D-O4","text":"不得修改输入列表。"},
        {"id":"D-C1","text":"重复判断改为忽略 ASCII 字母大小写。"},
        {"id":"D-C2","text":"仍保留第一次出现的原文、相对顺序；不得修改输入列表；输入范围不变。"}
      ],
      "code": {
        "old": "def solve(xs):\n    out = []\n    for x in xs:\n        if x not in out:\n            out.append(x)\n    return out\n",
        "good": "def solve(xs):\n    seen = set()\n    out = []\n    for x in xs:\n        key = x.lower()\n        if key not in seen:\n            seen.add(key)\n            out.append(x)\n    return out\n",
        "bad": "def solve(xs):\n    return sorted({x.lower() for x in xs})\n"
      },
      "rows": [
        {"id":"D0","args":[[]],"origin":"author_manual_trace_NOT_program_execution","versions":{"old":{"return":[],"args_after":[[]]},"good":{"return":[],"args_after":[[]]},"bad":{"return":[],"args_after":[[]]}}},
        {"id":"D1","args":[["B","b","A"]],"origin":"author_manual_trace_NOT_program_execution","versions":{"old":{"return":["B","b","A"],"args_after":[["B","b","A"]]},"good":{"return":["B","A"],"args_after":[["B","b","A"]]},"bad":{"return":["a","b"],"args_after":[["B","b","A"]]}}},
        {"id":"D2","args":[["b","a"]],"origin":"author_manual_trace_NOT_program_execution","versions":{"old":{"return":["b","a"],"args_after":[["b","a"]]},"good":{"return":["b","a"],"args_after":[["b","a"]]},"bad":{"return":["a","b"],"args_after":[["b","a"]]}}},
        {"id":"D3","args":[["B"]],"origin":"author_manual_trace_NOT_program_execution","versions":{"old":{"return":["B"],"args_after":[["B"]]},"good":{"return":["B"],"args_after":[["B"]]},"bad":{"return":["b"],"args_after":[["B"]]}}},
        {"id":"D4","args":[["b","b","a"]],"origin":"author_manual_trace_NOT_program_execution","versions":{"old":{"return":["b","a"],"args_after":[["b","b","a"]]},"good":{"return":["b","a"],"args_after":[["b","b","a"]]},"bad":{"return":["a","b"],"args_after":[["b","b","a"]]}}},
        {"id":"D5","args":[["a","A"]],"origin":"author_manual_trace_NOT_program_execution","versions":{"old":{"return":["a","A"],"args_after":[["a","A"]]},"good":{"return":["a"],"args_after":[["a","A"]]},"bad":{"return":["a"],"args_after":[["a","A"]]}}},
        {"id":"DU","args":[["ß","SS"]],"origin":"author_manual_trace_NOT_program_execution","versions":{"old":{"return":["ß","SS"],"args_after":[["ß","SS"]]},"good":{"return":["ß","SS"],"args_after":[["ß","SS"]]},"bad":{"return":["ss","ß"],"args_after":[["ß","SS"]]}}}
      ]
    },
    {
      "id": "F",
      "title": "小店订单运费",
      "clauses": [
        {"id":"F-O1","text":"amount_cents 是 0～20000 的整数分；is_member 严格为 True 或 False；返回整数分。"},
        {"id":"F-O2","text":"会员一律免运费。"},
        {"id":"F-O3","text":"非会员订单金额满 10000 分（含）免运费，不满收 1000 分运费。"},
        {"id":"F-C1","text":"非会员免运费门槛改为 8000 分（含）。"},
        {"id":"F-C2","text":"会员免运费和 1000 分基础运费不变，其余合同不变。"}
      ],
      "code": {
        "old": "def solve(amount_cents, is_member):\n    if is_member or amount_cents >= 10000:\n        return 0\n    return 1000\n",
        "good": "def solve(amount_cents, is_member):\n    if is_member or amount_cents >= 8000:\n        return 0\n    return 1000\n",
        "bad": "def solve(amount_cents, is_member):\n    if amount_cents >= 8000:\n        return 0\n    return 1000\n"
      },
      "rows": [
        {"id":"F0","args":[0,false],"origin":"author_manual_trace_NOT_program_execution","versions":{"old":{"return":1000,"args_after":[0,false]},"good":{"return":1000,"args_after":[0,false]},"bad":{"return":1000,"args_after":[0,false]}}},
        {"id":"F1","args":[7900,false],"origin":"author_manual_trace_NOT_program_execution","versions":{"old":{"return":1000,"args_after":[7900,false]},"good":{"return":1000,"args_after":[7900,false]},"bad":{"return":1000,"args_after":[7900,false]}}},
        {"id":"F2","args":[8000,false],"origin":"author_manual_trace_NOT_program_execution","versions":{"old":{"return":1000,"args_after":[8000,false]},"good":{"return":0,"args_after":[8000,false]},"bad":{"return":0,"args_after":[8000,false]}}},
        {"id":"F3","args":[9000,false],"origin":"author_manual_trace_NOT_program_execution","versions":{"old":{"return":1000,"args_after":[9000,false]},"good":{"return":0,"args_after":[9000,false]},"bad":{"return":0,"args_after":[9000,false]}}},
        {"id":"F4","args":[3000,true],"origin":"author_manual_trace_NOT_program_execution","versions":{"old":{"return":0,"args_after":[3000,true]},"good":{"return":0,"args_after":[3000,true]},"bad":{"return":1000,"args_after":[3000,true]}}},
        {"id":"F5","args":[12000,false],"origin":"author_manual_trace_NOT_program_execution","versions":{"old":{"return":0,"args_after":[12000,false]},"good":{"return":0,"args_after":[12000,false]},"bad":{"return":0,"args_after":[12000,false]}}},
        {"id":"FU","args":[-100,false],"origin":"author_manual_trace_NOT_program_execution","versions":{"old":{"return":1000,"args_after":[-100,false]},"good":{"return":1000,"args_after":[-100,false]},"bad":{"return":1000,"args_after":[-100,false]}}}
      ]
    }
  ],
  "confirmed_layer_fixture": {
    "status": "author-filled post-confirmation fixture, not model extraction and not human confirmation",
    "D": {
      "domain": {
        "kind": "ascii_words",
        "sources": ["D-O1","D-C2"]
      },
      "allow": {
        "kind": "new_ascii_case_collision",
        "sources": ["D-C1"]
      },
      "checks": [
        {
          "kind": "first_original_order",
          "sources": ["D-O2","D-O3","D-C1","D-C2"]
        },
        {
          "kind": "input_unchanged",
          "sources": ["D-O4","D-C2"]
        }
      ],
      "unknown": {
        "kind": "outside_domain",
        "sources": ["D-O1"],
        "note": "Unicode、非字符串及范围外输入的处理未规定；返回对象身份也未规定。"
      }
    },
    "F": {
      "domain": {
        "kind": "cents_member",
        "sources": ["F-O1","F-C2"]
      },
      "allow": {
        "kind": "nonmember_8000_to_9999",
        "sources": ["F-O3","F-C1"]
      },
      "checks": [
        {
          "kind": "member_free",
          "sources": ["F-O2","F-C2"]
        },
        {
          "kind": "nonmember_threshold_8000",
          "sources": ["F-C1","F-C2"]
        },
        {
          "kind": "integer_return",
          "sources": ["F-O1"]
        }
      ],
      "unknown": {
        "kind": "outside_domain",
        "sources": ["F-O1"],
        "note": "负额、浮点、非布尔会员标记的处理未规定；优惠券前后金额语义未规定。"
      }
    }
  },
  "evaluator_only": {
    "independence": "normative tables derived from frozen clauses, not taken from candidate return values; same author is not independent reviewer",
    "old_expected": {
      "D0": [],
      "D1": ["B","b","A"],
      "D2": ["b","a"],
      "D3": ["B"],
      "D4": ["b","a"],
      "D5": ["a","A"],
      "F0": 1000,
      "F1": 1000,
      "F2": 1000,
      "F3": 1000,
      "F4": 0,
      "F5": 0
    },
    "new_expected": {
      "D0": [],
      "D1": ["B","A"],
      "D2": ["b","a"],
      "D3": ["B"],
      "D4": ["b","a"],
      "D5": ["a"],
      "F0": 1000,
      "F1": 1000,
      "F2": 0,
      "F3": 0,
      "F4": 0,
      "F5": 0
    },
    "labels": {
      "D0": {
        "good": "PRESERVED",
        "bad": "PRESERVED"
      },
      "D1": {
        "good": "ALLOWED_CHANGE",
        "bad": "REGRESSION"
      },
      "D2": {
        "good": "PRESERVED",
        "bad": "REGRESSION"
      },
      "D3": {
        "good": "PRESERVED",
        "bad": "REGRESSION"
      },
      "D4": {
        "good": "PRESERVED",
        "bad": "REGRESSION"
      },
      "D5": {
        "good": "ALLOWED_CHANGE",
        "bad": "ALLOWED_CHANGE"
      },
      "DU": {
        "good": "UNKNOWN",
        "bad": "UNKNOWN"
      },
      "F0": {
        "good": "PRESERVED",
        "bad": "PRESERVED"
      },
      "F1": {
        "good": "PRESERVED",
        "bad": "PRESERVED"
      },
      "F2": {
        "good": "ALLOWED_CHANGE",
        "bad": "ALLOWED_CHANGE"
      },
      "F3": {
        "good": "ALLOWED_CHANGE",
        "bad": "ALLOWED_CHANGE"
      },
      "F4": {
        "good": "PRESERVED",
        "bad": "REGRESSION"
      },
      "F5": {
        "good": "PRESERVED",
        "bad": "PRESERVED"
      },
      "FU": {
        "good": "UNKNOWN",
        "bad": "UNKNOWN"
      }
    },
    "source_audit": {
      "allowed": "D-C1 permits case-based merging; F-C1 permits lower nonmember threshold, not all changes on affected inputs",
      "preserved": "D-O2/O3/O4 plus D-C2: first original/order/no mutation; F-O2/O3/O1 plus F-C2: member waiver/base fee/types",
      "no_known_old_bug": "manual source review and 12 defined ledger entries match original requirements; not executed proof",
      "unknown": "no oracle supplied for DU/FU; no behavior invented for out-of-domain input or unsupported business context"
    }
  },
  "frozen_failure_controls": [
    {"id":"old_as_patch_D1","task":"D","row":"D1","candidate":"old","expected":"CHANGE_NOT_IMPLEMENTED"},
    {"id":"old_as_patch_F2","task":"F","row":"F2","candidate":"old","expected":"CHANGE_NOT_IMPLEMENTED"}
  ],
  "decision_gate": {
    "model_stage": "Only if a concrete semantic translation gap remains after rule sufficiency check. No repeated samples or AI judge.",
    "stop": "If R1 post-confirmation layer and explicit rules give the same supported decisions with no new handling, do not claim novelty or proceed to model calls merely to fill a table.",
    "b0_status_if_stop": "NOT_RUN; optimized prompt frozen below; no inferred B0 correctness or cost advantage",
    "extension": "Only actual reproducible increment permits proposal for up to four tasks; no automatic product development"
  },
  "b0_prompt": "你在审查一个 Python 变更。只使用原始需求、新变更、旧代码、补丁和同一份冻结观察工具；工具结果可能只是人工离线推演，不能说成真实执行。区分需求允许变化、必须保留的性质及没有原文依据的未知要求。允许变化区不免除其他保留要求。旧代码可作兼容性参考，但不能自动当作正确规范；合法变化区依据需求判断。检查每个候选补丁是否漏实现目标或产生需求外回归；每项结论注明原句、输入、旧/新观察及证据等级。范围外输入保留 UNKNOWN，即使结果相同。未见反例不等于正确。最多读取每任务7个已给输入，不增加搜索、改代码、调用外部工具或猜测参考。只输出简短判定及未决事项。",
  "planned_observations": {
    "task_count": 2,
    "source_versions": 6,
    "frozen_input_rows": 14,
    "manual_version_snapshots": 42,
    "candidate_method_decisions": 28,
    "old_compatibility_checks": 12,
    "old_as_patch_controls_per_method": 2
  }
}
```

## 附录 B：可复核离线检查器

本脚本只读取本文冻结数据、解析源码语法并执行可信规则；不运行候选程序，也不调用模型。可以在工作目录用 Python 运行此段审查过的分析脚本；不要把附录 A 的源码拿到宿主执行。运行数字只用于核对工程处理，不证明学习、业务审核或程序真实执行效果。

源 ID 校验是引用存在性检查；支持的条件语义写在固定函数里，未实现通用自然语言形式化。范围内标签核对后还检查“旧代码作为新补丁”两个失败控制。

<!-- R1_OFFLINE_CHECKER -->
```python
import ast
import hashlib
import json
import re
import time
from collections import Counter
from pathlib import Path

REPORT = Path("P2_R1_feasibility.md")
MARKER = r"<!-- R1_FROZEN_MATERIALS -->\s*\x60\x60\x60json\n(.*?)\n\x60\x60\x60"
raw = re.search(MARKER, REPORT.read_text(encoding="utf-8"), re.S).group(1)
fixture = json.loads(raw)
started = time.perf_counter()
material_sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()

# This checker executes trusted analysis only. Candidate programs remain strings.
# No eval, exec, dynamic import, compile-and-run, Docker, or provider calls.
def ascii_key(word):
    return "".join(chr(ord(c) + 32) if "A" <= c <= "Z" else c for c in word)

def domain_D(args):
    if len(args) != 1 or type(args[0]) is not list:
        return False
    xs = args[0]
    return len(xs) <= 6 and all(
        type(x) is str and 1 <= len(x) <= 4 and
        all("A" <= c <= "Z" or "a" <= c <= "z" for c in x)
        for x in xs
    )

def domain_F(args):
    return (len(args) == 2 and type(args[0]) is int and
            0 <= args[0] <= 20000 and type(args[1]) is bool)

def r1_allow(task_id, args):
    if task_id == "D":
        xs = args[0]
        return any(xs[i] != xs[j] and ascii_key(xs[i]) == ascii_key(xs[j])
                   for i in range(len(xs)) for j in range(i))
    amount, member = args
    return not member and 8000 <= amount < 10000

def r1_property(kind, args, observation):
    output = observation["return"]
    if kind == "first_original_order":
        xs = args[0]
        positions = [i for i in range(len(xs))
                     if all(ascii_key(xs[i]) != ascii_key(xs[j]) for j in range(i))]
        return type(output) is list and output == [xs[i] for i in positions]
    if kind == "input_unchanged":
        return observation["args_after"] == args
    if kind == "member_free":
        return not args[1] or output == 0
    if kind == "nonmember_threshold_8000":
        return args[1] or output == (0 if args[0] >= 8000 else 1000)
    if kind == "integer_return":
        return type(output) is int
    raise ValueError("Unsupported property is not silently accepted")

def r1(task_id, row, observation, constraints):
    expected_domain = {"D": "ascii_words", "F": "cents_member"}[task_id]
    expected_allow = {"D": "new_ascii_case_collision", "F": "nonmember_8000_to_9999"}[task_id]
    if (constraints["domain"]["kind"] != expected_domain or
        constraints["allow"]["kind"] != expected_allow or
        constraints["unknown"]["kind"] != "outside_domain"):
        return "UNKNOWN"
    valid = domain_D(row["args"]) if task_id == "D" else domain_F(row["args"])
    if not valid:
        return "UNKNOWN"
    if any(not r1_property(rule["kind"], row["args"], observation)
           for rule in constraints["checks"]):
        unchanged = observation == row["versions"]["old"]
        return "CHANGE_NOT_IMPLEMENTED" if unchanged and r1_allow(task_id, row["args"]) else "REGRESSION"
    if observation == row["versions"]["old"]:
        return "PRESERVED"
    return "ALLOWED_CHANGE" if r1_allow(task_id, row["args"]) else "REGRESSION"

# Explicit rule baseline: independent expression, no structured constraint object,
# no evaluator-only labels/references, and no candidate source execution.
def b1(task_id, row, observation):
    args = row["args"]
    if task_id == "D":
        if not domain_D(args):
            return "UNKNOWN"
        seen, expected = set(), []
        for word in args[0]:
            key = word.lower()  # Domain already excludes non-ASCII.
            if key not in seen:
                seen.add(key)
                expected.append(word)
        conforms = type(observation["return"]) is list and observation["return"] == expected and observation["args_after"] == args
        changed_region = any(a != b and a.lower() == b.lower()
                             for i, a in enumerate(args[0]) for b in args[0][:i])
    else:
        if not domain_F(args):
            return "UNKNOWN"
        amount, member = args
        expected = 0 if member or amount >= 8000 else 1000
        conforms = type(observation["return"]) is int and observation["return"] == expected
        changed_region = not member and 8000 <= amount < 10000
    if not conforms:
        return "CHANGE_NOT_IMPLEMENTED" if observation == row["versions"]["old"] and changed_region else "REGRESSION"
    if observation == row["versions"]["old"]:
        return "PRESERVED"
    return "ALLOWED_CHANGE" if changed_region else "REGRESSION"

def old_requirement_reference(task_id, args):
    if task_id == "D":
        return [word for i, word in enumerate(args[0]) if word not in args[0][:i]]
    return 0 if args[1] or args[0] >= 10000 else 1000

# Public task material and confirmed-layer fixture only go to method functions.
# Evaluator-only tables are used below, after predictions.
records, source_hashes, old_checks = [], {}, 0
for task in fixture["public_tasks"]:
    task_id = task["id"]
    for version, source in task["code"].items():
        ast.parse(source)  # Syntax parse only; no candidate code execution.
        source_hashes[task_id + "/" + version] = hashlib.sha256(source.encode("utf-8")).hexdigest()
    sources = {clause["id"] for clause in task["clauses"]}
    rules = fixture["confirmed_layer_fixture"][task_id]
    for rule in [rules["domain"], rules["allow"], rules["unknown"]] + rules["checks"]:
        assert rule["sources"] and set(rule["sources"]) <= sources
        # Existence of a source ID is not proof that its semantic mapping is right.
    for row in task["rows"]:
        if row["id"] in fixture["evaluator_only"]["old_expected"]:
            old_output = row["versions"]["old"]["return"]
            assert old_output == old_requirement_reference(task_id, row["args"])
            assert old_output == fixture["evaluator_only"]["old_expected"][row["id"]]
            assert row["versions"]["good"]["return"] == fixture["evaluator_only"]["new_expected"][row["id"]]
            old_checks += 1
        for version in ("good", "bad"):
            observation = row["versions"][version]
            prediction_r1 = r1(task_id, row, observation, rules)
            prediction_b1 = b1(task_id, row, observation)
            gold = fixture["evaluator_only"]["labels"][row["id"]][version]
            records.append({"row": row["id"], "patch": version, "gold": gold,
                            "R1_post_confirm": prediction_r1, "B1_rule": prediction_b1})
            assert prediction_r1 == gold, records[-1]
            assert prediction_b1 == gold, records[-1]

controls = []
for control in fixture["frozen_failure_controls"]:
    task = next(t for t in fixture["public_tasks"] if t["id"] == control["task"])
    row = next(r for r in task["rows"] if r["id"] == control["row"])
    observation = row["versions"][control["candidate"]]
    a = r1(task["id"], row, observation, fixture["confirmed_layer_fixture"][task["id"]])
    b = b1(task["id"], row, observation)
    assert a == b == control["expected"]
    controls.append({"id": control["id"], "R1_post_confirm": a, "B1_rule": b})

summary = {
    "material_sha256": material_sha,
    "source_sha256": source_hashes,
    "tasks": len(fixture["public_tasks"]),
    "source_syntax_parses": len(source_hashes),
    "manual_version_snapshots": sum(len(t["rows"]) * 3 for t in fixture["public_tasks"]),
    "old_requirement_consistency_checks": old_checks,
    "decisions_per_method": len(records),
    "R1_B1_equal": sum(r["R1_post_confirm"] == r["B1_rule"] for r in records),
    "frozen_label_matches_per_method": len(records),
    "label_counts": dict(Counter(r["gold"] for r in records)),
    "target_missed_control_decisions_per_method": len(controls),
    "actual_candidate_program_executions": 0,
    "actual_test_model_calls": 0,
    "B0_actual_model_status": "NOT_RUN",
    "independent_human_reviews": 0,
    "elapsed_seconds": round(time.perf_counter() - started, 6),
    "records": records,
    "controls": controls
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
```
