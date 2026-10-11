# V1 数据字段与统计口径

SQLite schema 版本为 1；新增的观察时间 / 初始快照字段采用只追加的列迁移，不接触历史 F01/F02 文件。所有机器时间保存为带 UTC 偏移的 ISO 8601。网页日期与日期筛选使用 Asia/Shanghai（UTC+08:00）。ID 为随机 UUID 的 32 位十六进制字符串，不包含用户身份。

## experiments：一次实验

| 字段 | 含义 |
| --- | --- |
| experiment_id / create_request_id | 实验唯一 ID / 可选的新建幂等键 |
| name / feature / case_id / mode | 名称、F01/F02、既有案例、S0/S1 |
| source_type | real_user / automated_test；real_user 不认证身份或初学者角色 |
| model_provenance | real_official_Codex_CLI / frozen_S0_rules / simulated_model |
| created_at / ended_at | 起止时间；暂停时 ended_at 为空 |
| status / end_reason | active / paused / completed / failed；结束或暂停原因独立保存 |
| current_code_version_id | 当前记录的版本；新版本并不意味着已经核验 |
| case_snapshot | 开始时的完整公开案例、源码、证据和冻结首问 |
| initial_input_snapshot | 开始时的公开输入快照；早期验收实验在追加字段前创建，值为空，其案例和首次轮次快照仍完整保留 |
| model_config | 请求模型、推理档位、原传输、超时、轮次上限、守卫及模块 SHA-256；后台精确快照未知 |
| version_snapshot | 原案例文件、案例快照、源码、证据 SHA-256 和版本边界 |

completed 仅表示会话结束，含单轮结束、理解足够、预算上限、手动结束 / 提前完成，不等于程序修好或教学验收。await_new_evidence 为 paused，不认证用户修改。

## turns：一次教师输出及触发它的学生回答

| 字段 | 含义 |
| --- | --- |
| turn_id / experiment_id / number | 轮次 ID、所属实验、教师输出序号 |
| request_id | 实验内幂等键；同一键不同原文拒绝 |
| question_shown | 触发本轮时展示给用户的原问题；F02 首次没有前问，留空 |
| answer_raw | 未 trim 的用户原文；F02 首问时为空，不虚构学生回答 |
| public_input | 已冻结的本轮公开输入、同路径历史和未核验新代码文本；不随未来历史改变 |
| code_version_id | 提交时的当前版本 ID，与后续版本分开 |
| submitted_at / started_at / generation_started_at / completed_at | 保存、后台开始、首次观察到 CLI turn.started、结束时间 |
| status | queued / connecting / generating / succeeded / failed / blocked |
| output | 当前选用尝试的完整结构化回复；student_message、next_action、interpretation、answer_quotes、decision_basis、evidence_refs、uncertainties 等原协议字段 |
| checks | 原守卫结构 / 引用 / 受控执行结果；不证明整段自然语言语义正确 |
| selected_attempt_id | 最近这次尝试 ID；旧尝试始终在 attempts 中 |
| elapsed_seconds / error | 当前尝试耗时与原错误原因 |

F01 一轮；F02 最多三次教师输出，包括首问。因此默认最多两次学生回答。`generation_started_at` 为客户端事件的观察时间，非模型服务器精确开始时间；旧验收轮次和模拟 / 规则服务可能为空。

## attempts：每次实际运行，含重试

| 字段 | 含义 |
| --- | --- |
| attempt_id / turn_id / number | 尝试 ID、轮次 ID、尝试序号（A01、A02…） |
| request_id / retry_reason | 重试幂等键 / 人工原文原因；首次原因为空 |
| requested_at / started_at / generation_started_at / completed_at | 排队、开始、观察生成、结束时间 |
| status / error / elapsed_seconds | 运行状态、错误、耗时 |
| artifact_dir | 相对网页数据目录的原始工件路径 |
| output / checks / metadata | 本次结构化原回复、守卫、官方元数据；不覆盖旧尝试 |
| raw_output | UTF-8 解码文本，允许为空；精确原字节保存在 raw_response.json |

metadata 保留存在的 `CLI_success`、exit_code、timeout、warnings、usage（输入 / 输出 / 推理 token 等）、thread_ids、模型 / 推理档位、哈希、原 CLI 与事件匹配结果。用量缺失为 null，不能当作 0 token；S0 的 actual_model_call=false。异常时保留 traceback、stderr 和部分原输出；重启恢复不自动重新生成。

## feedback：评价修订（只追加）

每次保存产生新的 feedback_id、turn_id、created_at（本次修改时间）。字段为 evaluation_source、on_topic、repetitive、fact_error、full_repair、used_previous、satisfaction、notes。

- on_topic 等五项：yes / no / uncertain / null；事实与完整修复项目中 uncertain 显示为“待核验”。
- satisfaction：1～5 或 null；notes 可为空。null 表示未评分，不解释为正确。
- evaluation_source：user_subjective、ai_auxiliary、independent_human。网页控件保存 user_subjective；另外两类可通过 API 明确标注写入，不自动生成，不参与用户反馈计数。
- 客观执行来源为 turns / attempts 的 checks 与已审核案例 evidence，统计单独展示；未评价是用户评分空值，不是模型自动评分。
- 修改评价只追加修订，不改用户原文、模型原输出和旧评价。JSON 全部保留，CSV 和主观统计使用同轮最新 user_subjective 修订。

## code_versions、notes、events

code_versions 保存 version_id、所属实验、label、source、source_sha256、verification_status、execution_allowed、created_at。verified_fixture 只用于冻结原版 / 已审核 local_patch；unverified 仅文本，execution_allowed=false。新版本始终具有独立 ID、时间和哈希，不继承旧证据。

notes 保存 note_id、所属实验、时间、text；追加后旧备注保留。events 保存生命周期、排队 / 完成、人工控制、评价修订和源码记录事件；payload 是对应 ID 与动作，不包含认证秘密。

## 导出与统计

JSON schema_version=1，包含上述全部实验、轮次、尝试、反馈、版本、备注和事件。每个白名单工件包含相对路径、字节数、SHA-256 和 base64 内容，便于精确追溯原文；普通页面工件链接以纯文本显示。没有任意本地文件导出接口。

CSV 分 experiments / turns / attempts，带 UTF-8 BOM。可能触发 Excel 公式的文本前加单引号；JSON 和数据库保留原文。全部 / 单次实验导出都包含明确数据来源。

实验计数分母为所选来源的实验数。反馈计数分母为该范围内全部教师轮次（含未完成 / 失败），并分别保留 yes、no、uncertain、unrated。已评价轮次指最新主观修订至少有一个评分或非空备注，不等于评价过所有维度。

真实 AI 调用只统计 model_provenance=real_official_Codex_CLI 且 mode=S1 的尝试；成功为官方 CLI_success，失败为已结束但 CLI_success 不为 true，正在等待单列。守卫阻断可能仍是传输成功。S0 和模拟调用分开计数。耗时平均值分母为有耗时的已结束真实尝试（含失败），不包括规则或模拟耗时。

源类型默认筛选真实用户；自动测试数据可显式查看。评价来源修订次数不是已评价轮次数；不把模型自评、作者初评或守卫放行显示为认证功能准确率。
