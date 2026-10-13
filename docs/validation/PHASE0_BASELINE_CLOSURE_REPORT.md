# Phase 0：仓库基线收口报告

日期：2026-10-14，Asia/Shanghai。范围：审核 cleanup、收口 main、复验与交接；没有功能或 UI 开发。

## 1. 最终结论

**PASS WITH NOTES — 可以继续，但有非阻断注意事项。**

cleanup 已 fast-forward 合入本地及远程 main，整理的两次提交完整保留。main 可作为后续唯一稳定工程基线；两个 V3 UI 分支保持独立，未合入、未重写、未删除。合并前和合并后各执行既有 78 项轻量回归，均为 78 passed / 0 failed / 0 skipped。

注意事项仅涉及历史提交笔误、Git 重命名显示和本机联网方式，详见第 5 节。没有发现需要停止收口的风险。本报告不将轻量测试通过扩大为整个项目完全正确、Docker 重新通过真实验收或真人教学有效。

## 2. 当前 Git 状态

以下是工程收口及远程推送后、本报告提交前的实际 Git 快照：

| 引用 | 实际 commit | 结果 |
| --- | --- | --- |
| main / origin/main | `abdba7394647d246847c9d65a3aa813d7847253a` | 已包含全部 cleanup 历史 |
| chore/project-cleanup / origin/chore/project-cleanup | `abdba7394647d246847c9d65a3aa813d7847253a` | 保留原分支及原提交 |
| ui/codehelper-reference / origin/ui/codehelper-reference | `b194e0b37031545f2eb51c3c8349f6c93d3463f6` | 独立保留，未合入 main |
| ui/agent-exploration / origin/ui/agent-exploration | `f1200ca5bf2f3fd8712643bd2dac0e4d75cbcb96` | 通过 Git 确认，未合入 main |

收口前 main 为 `c40029ce2bb00581917cb5e45f9c0b4ad0c83745`，也是两个 UI 分支共同基线。cleanup 在该基线上依次包含检查点 `12971c0683e466541e6b6b9d24af87fb323c5356` 和最终整理提交 `abdba739…`。`git merge-base --is-ancestor main chore/project-cleanup` 在合并前通过，因此使用 `git merge --ff-only chore/project-cleanup`，无冲突、无 squash/rebase、无历史改写。

本报告和下述状态修正另作纯文档提交，因此交付时 main HEAD 会高于表中工程收口提交。最终当前值用 `git rev-parse main` 获取，报告提交用 `git log -1 --format=%H -- docs/validation/PHASE0_BASELINE_CLOSURE_REPORT.md` 定位；聊天交付同时给出最终 HEAD。合并前、fast-forward 后的工作树均干净；本机忽略文件仍保留。

## 3. cleanup 变化摘要

按 Git 树和 [逐文件迁移清单](CLEANUP_INVENTORY.md) 重新核对，main 原有 222 个跟踪文件，cleanup 为 332 个；两者完整 diff 显示 119 项路径变化，不能把这个数理解为 119 项功能修改。

| 类别 | 当前核对结果 |
| --- | --- |
| 文件迁移 | 29 份文档：6 份原 main 文档、23 份先纳入检查点的历史文档，迁至 setup / architecture / validation / archive |
| 历史归档 | `docs/archive/` 有 99 份材料，加 1 份索引；104 份整理文档整体由 29 MOVE、73 COPY、2 个 UI 报告只读导出组成 |
| 新增文档 | AGENT_HANDOFF、PROJECT_STATUS、ARCHITECTURE、KNOWN_LIMITATIONS、AGENTS、CHANGELOG，以及本地设置、归档索引与整理验收/留存清单；README 更新导航和启动说明 |
| .gitignore / 配置 | 重组文档逐文件允许清单、补充本机产物保护；169 条 experiments 允许项完整不变；依赖、`.env.example`、`.gitattributes` 原字节未变 |
| 核心源码、教学、Provider | 无变化；session、version/hash、run/submit、sandbox jobs、execution context 和 F01～F05 所属保留文件均与原 main 相同 |
| 测试 | 测试源码、原路径未变；新增 `scripts/check_repository.py` 是只读仓库检查脚本，不是功能或测试体系重写 |
| Docker | 合同、调度、运行、设置与镜像文件原字节未变；未绕过既有验收或 F03/F04 白名单 |
| Web / 前端 | `web_lab` 服务入口、Python、JS/CSS/HTML 原字节未变；UI 分支仅导出报告，没有导入 UI 源码 |
| 数据 / 冻结工件 | 允许清单内静态合成工件、案例、登记、原提示及摘要保持原路径和原字节；未重算冻结摘要 |
| 其他 | 没有运行入口或重要工程文件丢失；无异常核心逻辑修改需要单独拆出 |

既有检查脚本重新确认 **214/214 保留基线文件逐字节、逐路径一致**；另用 Git blob ID / 文件模式比较复核一致。73 个 COPY 原件均在本机旧路径且 SHA-256 与清单匹配，两个 UI 报告原分支 SHA-256 也匹配。

检查点中移除的 29 个旧路径全部对应 MOVE 项，新位置全部存在，旧内容均可用 `git show 12971c0:<旧路径>` 恢复；原 main 消失的 6 个路径也全部在该映射中。没有发现无对应归档位置或不可由 Git 恢复的受审删除。本轮未删除任何本机留存文件。

## 4. 实际验证结果

使用已有 Python 3.12.10 和已安装依赖，没有新增依赖或重新设计测试。实际执行的两组 README 命令如下，合并前在原工作区执行，合并后在 `git archive main` 导出的干净目录执行：

```powershell
python -X utf8 -m unittest web_lab.tests.test_ai_provider web_lab.tests.test_api web_lab.tests.test_demo web_lab.tests.test_learning_v2 web_lab.tests.test_sandbox
python -X utf8 -m unittest experiments.feature_validation.F01_response_adaptation.test_core experiments.feature_validation.F02_dynamic_questioning.test_core experiments.feature_validation.F03_evidence_verification.test_verifier experiments.feature_validation.F04_self_modification.test_core experiments.feature_validation.F05_independent_assessment.test_core
```

| 实际检查 / 命令 | pass / fail / skip | 证据与边界 |
| --- | --- | --- |
| 合并前 README Web 组 | 38 / 0 / 0 | 84.802 秒；Provider/Docker 替身及临时数据 |
| 合并前 README F01～F05 组 | 40 / 0 / 0 | 7.825 秒；仅固定审核案例允许的执行 |
| 合并后干净导出 Web 组 | 38 / 0 / 0 | 82.713 秒；不借用原工作区忽略的历史工件 |
| 合并后干净导出 F01～F05 组 | 40 / 0 / 0 | 9.669 秒；无新增失败 |
| `python -X utf8 scripts/check_repository.py --cleanup-baseline` | PASS | 原工作区合并前后：332 文件、335 本地链接、24 私人忽略样例、214 原字节基线文件 |
| `python -X utf8 scripts/check_repository.py` | PASS | 合并后的干净目录：332 文件、335 本地链接、24 忽略样例；真实远程链接不联网测试 |
| 加入本报告及状态修正后的 `git diff --cached --check`、`python -X utf8 scripts/check_repository.py --cleanup-baseline` | PASS | 333 文件、340 本地链接、24 忽略样例、214 原字节基线文件；报告进入显式文档允许清单 |
| `teaching.verify_engines()`、`verifier.load_registry()`、`f04.load()`、`f05.load()` | PASS | 在干净导出内调用既有加载函数，未重算摘要 |
| `python -X utf8 output/phase0_baseline_20261014/audit_cleanup.py` | PASS | 本机只读辅助核对：29/73/2 来源、214 blob、169 允许项、359 个 cleanup 历史独立 blob；不打印凭据值 |
| `python -X utf8 output/phase0_baseline_20261014/smoke_startup.py --label pre` | PASS | 调用现有 `python -X utf8 -m web_lab --port <临时端口> --data-dir <新目录> --no-browser`，Provider disabled |
| 上述 smoke 脚本指定 `--repo output/phase0_baseline_20261014/main_clean --label post` | PASS | 合并后干净目录同样启动；health、首页、learning.js/css、demo cases 均 HTTP 200；随后退出本轮进程 |
| `git status --porcelain=v1 --untracked-files=all`、`git branch -avv`、`git log --oneline --graph --decorate --all` | PASS | 初始/合并后无未提交或非忽略未追踪文件；四分支结构正常 |
| `git merge-base main chore/project-cleanup`、`git merge-base ui/codehelper-reference ui/agent-exploration` | PASS | 合并前共同基线均为 c40029c；两个 UI tip 不在 cleanup/main 历史中 |
| `git diff --name-status --find-renames=50% main chore/project-cleanup`、`git diff --name-status --find-renames=50% 12971c0 chore/project-cleanup`、`git diff --check main chore/project-cleanup` | PASS | 只读分类及迁移审查，空白检查通过；重命名显示注意事项见下节 |
| `git -c http.proxy=http://127.0.0.1:7897 fetch origin`、同代理 `ls-remote --heads origin main chore/project-cleanup ui/codehelper-reference ui/agent-exploration` | PASS | 实时远程四个 tip 与本地一致，非仅依靠缓存引用 |
| `git switch main`、`git merge --ff-only chore/project-cleanup`、同代理 `push origin main` 及 `ls-remote` | PASS | 本地和远程 main 均从 c40029c 正常前进到 abdba73；其他三个分支未变 |
| 初次 `git fetch origin` 直连 | FAIL，已恢复 | GitHub 443 连接失败；采用仓库已记载的现有 loopback 代理后成功，未改全局配置或 TLS 校验 |
| 真实 Docker 任务 / build / accept、live 测试、真实 AI API、真人试用 | SKIP（按范围） | 未执行；两次 smoke 新数据目录的 sandbox 均 ready=false，无模型请求、无 sandbox job、无宿主学生代码回退 |

干净目录的创建命令为 `git archive --format=zip --output=output/phase0_baseline_20261014/main_clean.zip main`，随后 `Expand-Archive`；只为既有检查脚本在该副本 `git init -q` 和 `git add --all` 建索引，未增加工作树或分支。日志、临时数据、辅助脚本和导出副本均留在忽略的 `output/phase0_baseline_20261014/`，不进入交付 Git。

本报告提交还包含小范围状态修正：AGENTS、AGENT_HANDOFF、PROJECT_STATUS、GitHub 设置文档更新 main 已收口的事实和 Phase 1 入口；`.gitignore` 仅增加本报告的单文件允许项。源码、测试、UI、Docker 与冻结文件继续不变。最终暂存内容的空白、交接链接、发布扫描和原字节基线检查均已通过。

## 5. 发现的问题

**P0 阻断：无。** 核心改动、重要文件丢失、secret/私人数据混入、UI 分支被混合等阻断条件均未发现。

**P1 应尽快处理：无。** 交接文档的 main 状态已作必要修正；历史整理报告保留原阶段语境，没有大规模改写。

**P2 可后续处理：**

- 任务提供的 cleanup hash 写成 `adbba7394647d246847c9d65a3aa813d7847253a`；本地及实时远程均为 **`abdba7394647d246847c9d65a3aa813d7847253a`**。方向二实际 tip 为 `f1200ca5bf2f3fd8712643bd2dac0e4d75cbcb96`，没有猜测其提交。
- Git 重命名是内容相似度推断：相对检查点识别出 28 个 R，`GITHUB_SETUP.md` 显示 D + 新增 `docs/setup/GITHUB_SETUP.md`，因为内容已重新整理。29 项清单逐项有旧 blob 和新文件，显示 D 不构成材料永久丢失；相对原 main 的 diff 看不到先新增后迁移的 23 项完整迁移过程，应联合检查点审查。
- 本机直连 GitHub 曾失败，现有代理已完成远程核对和普通推送；代理只作用于本轮 Git 命令，新环境应使用自己的网络配置。
- 本机存在大量有意忽略的数据库、备份、浏览器材料、历史原件与缓存。初次聚合盘点为 5,460 个，后续本轮输出会增加；非忽略未追踪为 0。只核对路径/类型及明确冻结原件，不读取私人数据库、不删除不确定材料、不把它们纳入 main。详见 [本机留存说明](RETAINED_LOCAL_FILES.md)。当前可证明的是受审 Git 材料可恢复，Git 不负责恢复私人本机数据。

交接入口与四份主文档足以定位现有工程、停止路线、运行依赖和测试边界。原“不自动合并 main”适用上轮整理；本轮用户已明确授权通过审核后收口，未把旧禁令误当阻断，也未自动恢复 P2。

## 6. 后续建议

进入 **Phase 1：比较 `ui/codehelper-reference` 与 `ui/agent-exploration`，进行最终 UI 选型。**
