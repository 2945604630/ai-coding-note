# AIC V3 · 方向二：自主探索型设计

开发与验收：2026-10-12～13，Asia/Shanghai。分支：`ui/agent-exploration`。

## 基线与范围

原 V2 基线是 `c40029ce2bb00581917cb5e45f9c0b4ad0c83745`。恢复任务时目标分支已经选中，存在未提交的方向二草稿；保留并继续完成，没有丢弃工作区文件。方向一已独立提交为 `b194e0b37031545f2eb51c3c8349f6c93d3463f6`，没有合并、复制或 cherry-pick 其提交。`main` 和 `ui/codehelper-reference` 保持原提交。

阅读了原 V2 的前端、API、README、沙箱报告和执行证据接入报告，并核对实际 C01/C03 案例。V3 改造学生界面，仅增加一个只读摘要接口 `/api/learning/records`，使用既有表，无数据库迁移。Docker 镜像与安全策略、AIProvider、教学协议、代码保存与执行关联、管理端和历史格式保留。

## 调研：看到的事实与设计推断

本轮读取以下官方说明及其公开页面；未登录这些产品进行账户级体验，因此不声称验证了未公开或付费功能。未取用第三方代码、图标或品牌素材。

| 产品 | 官方说明中实际看到的设计 | 对 AIC 的推断 |
| --- | --- | --- |
| [LeetCode](https://support.leetcode.com/hc/en-us/articles/360012016874-Start-your-Coding-Practice) | 题目页标签、代码模板、可编辑测试输入；Run 的输入/实际/预期输出与错误；Submit 和提交历史分开 | 单次观察与提交判题需要不同按钮；结果紧邻代码 |
| [Exercism](https://exercism.org/docs/using/solving-exercises/using-the-online-editor) | 左侧编辑器、右侧说明；运行测试后在右侧展示结果；通过后提交；部分语言可打印调试 | 题目应保持可查看，测试反馈要在当前练习内出现；不需要复制其布局 |
| [CodeHS](https://help.codehs.com/en/articles/3995966-tracking-student-activity) | 同一道作业可查看并恢复历史代码；保存、运行等操作会创建快照 | 回顾应以真实版本和操作为单位，恢复代码要先形成草稿 |
| [VS Code](https://code.visualstudio.com/docs/chat/chat-overview) | Chat view、聊天编辑器和轻量 inline/Quick Chat；上下文、对话导航和修改复查有明确入口 | 辅导应靠近代码，但不能遮挡主任务；需要说明回复依据哪个版本 |

“错误回顾融入练习”“草稿或运行等待期间阻止误发旧证据”是本项目的设计判断，不是上述产品的已验证功能。

## V2 的主要问题与方案取舍

V2 的题目、旧审核证据、Docker 操作和执行反馈都挤在可滚动代码面板里，主操作靠下；对话占比大于代码。学生还需要理解“登记版”“F03/F04”等研究术语。保存状态、历史证据和真实新运行的层级不够明显；直接发送草稿疑问仍会使用最近保存版本。会话 `failed` 表示回复失败，不能据此认定代码错题。

| 方案 | 首页与工作区 | 辅导、结果、历史 | 优点 / 缺点 |
| --- | --- | --- | --- |
| 三栏引导轨道 | 首页给下一步；题目/步骤在左、代码在中、教练在右 | 中栏结果，独立回顾侧栏 | 流程直观；小屏和短代码案例仍被多栏挤占，成本中等 |
| 全宽专注画布 | 首页直接续写；代码全宽 | AI 抽屉、底部结果、历史弹层 | 空间大；教练被隐藏，多次开关打断初学者，成本较高 |
| **代码优先的练习笔记（采用）** | 首页两道真实题 + 继续入口；桌面代码约 65%、辅导约 35% | 结果/错误/版本在编辑器下方切换；窄屏切换代码或辅导 | 当前现场完整、主操作固定且实现符合既有 API；长结果仍需要区域内滚动 |

第三种减少跳转，也不要求学生学习反常规操作；它能在原生 HTML/CSS/JS 中完整实现，避免为布局新增大后端模块。视觉采用深绿导航、浅色内容、低饱和橙色操作强调、系统中文字体和深色代码面板，动画只用于状态反馈。

## 实际完成

- 首页即时选择 C01/C03、续写最近练习、查看真实记录与错误；没有虚构题库、能力统计或掌握率。
- 代码始终留在工作台；显示行号，支持缩进、快捷保存/运行、草稿刷新恢复。执行操作紧邻编辑器。
- 运行和提交各保存独立任务；实际/参考输出并列。正常退出但输出不同也会提示差异；输入无审核参考时只显示实际行为。
- Python traceback 可返回对应版本并定位源码行；同版本草稿也必须经确认才能替换为当时的保存源码。
- 错误回顾记录真实输出差异、报错、超时和服务失败。后续通过不删除失败，支持查看当时版本、真实修改 diff 和全部运行历史。
- 历史恢复先形成草稿，保存才产生新版本；学生查看旧版本不会偷偷切换后端当前版本。
- 普通发送和失败重试都检查草稿、历史查看与运行等待；POST 尚未返回时即锁定发送。原回答重试明确沿用原快照；版本已变化时引导新练习。
- AI 依据版本与执行记录有明确提示，历史回复标示过期。快捷提示先填入可编辑回答，不直接消耗教学轮次。固定 S0 提示与真实 AI 区分展示。
- 保留旧审核核验、F05 新题首次提交/帮助记录、反馈、实验管理和导出。开发测试默认隐藏，显示时明确标记来源。

## 验证与截图

服务运行于 [127.0.0.1:8008](http://127.0.0.1:8008/)，数据为独立 `output/aic-v3-test`，未覆盖原 V2 数据库。Docker Desktop 最初未运行，页面如实禁用沙箱；启动后沿用本机既有收据，由原 runtime 重新核对镜像、Engine 和策略，未修改安全策略、构建新镜像或绕过验收。

轻量回归命令：

```powershell
python -X utf8 -m unittest web_lab.tests.test_ai_provider web_lab.tests.test_api web_lab.tests.test_demo web_lab.tests.test_learning_v2 web_lab.tests.test_sandbox web_lab.tests.test_learning_v3
python -X utf8 -m unittest experiments.feature_validation.F03_evidence_verification.test_verifier experiments.feature_validation.F04_self_modification.test_core experiments.feature_validation.F05_independent_assessment.test_core
node web_lab/tests/test_learning_state.mjs
```

第一组 41 项通过，第二组 25 项通过；V3 前端状态回归通过，全部相关 JS 语法检查通过。摘要接口和状态守卫先观察到测试失败，再实现和回归；CRLF 输出比较与后端判题保持一致。独立代码审查发现的请求窗口、重试边界、草稿定位、首页筛选重置和轮询控件重建问题均已修复。

最终完整 Playwright 流程 32 个断言通过，另有请求等待、超时、失败恢复和 F05 的针对性验证。Playwright 实际操作覆盖：新建、重复提交禁用、离线选择保持、未保存禁用、刷新恢复、S0 真回复、真实 Docker 单次运行/提交、报错行定位、无参考输入 8 返回 36、无限循环超时、历史恢复、差异、错误回顾、Provider 关闭失败恢复、新题冻结提交、管理入口。验证 1440px 桌面、1024px、390px 和 320px，无页面横向溢出。截图后至少一轮实际优化了留白、字号、主按钮位置、结果可见性与窄屏辅导高度。

截图保留在本地 `output/playwright/`，全部来自开发测试。按照仓库排除策略，不上传测试数据库、执行收据或浏览器记录：

- [首页](output/playwright/v3-home.png)、[工作台](output/playwright/v3-workspace-first.png)、[运行结果](output/playwright/v3-submit-results.png)
- [错误回顾](output/playwright/v3-review.png)、[练习内回顾](output/playwright/v3-review-workspace.png)、[Python 报错](output/playwright/v3-python-error.png)
- [辅导对话](output/playwright/v3-conversation.png)、[学习历史](output/playwright/v3-history.png)、[新题验收](output/playwright/v3-assessment.png)
- [窄屏代码](output/playwright/v3-workspace-mobile.png)、[窄屏辅导](output/playwright/v3-coach-mobile.png)、[窄屏首页](output/playwright/v3-home-mobile.png)

本轮真实模型调用和付费 API 调用均为 0。实际对话使用原 S0 固定规则，关闭状态失败使用 `disabled` Provider；不把这两者当成真实 AI 的回复质量验收。交付时已恢复原 `codex_cli` Provider，仍需使用者发起真实辅导来评估语义质量。

## 主要不足

仍是有限本机原型：两道练习、首次引导加最多两次后续回复，没有长期课程和掌握诊断。S0 不分析任意新代码；F05 自由提交仍待审核。代码编辑使用原生 textarea，尚无语法高亮与补全。长 traceback、多例提交和历史需要局部滚动；窄屏无法同时显示代码和辅导。跨浏览器草稿同步、真实学习者试用与真实 AI 语义质量本轮未验收。

相对 V2 最重要的改善是：**从失败结果直接回到准确版本与代码行，再保存新版本重新验证**。学生可以理解现在保存了什么、正在运行什么，以及教练看到了什么，不必在代码、错误和对话之间手工搬运证据。
