# AIC 交互实验台 V1 功能测试报告

验收日期：2026-10-10（Asia/Shanghai）。实现：Python 3.12、FastAPI 0.118.3、Uvicorn 0.49.0、SQLite、原生 HTML / CSS / JavaScript。服务真实地址：**http://127.0.0.1:8000**，仅监听 127.0.0.1。根目录 `start_web.bat` 已实际执行，后台服务启动并打开默认浏览器；重复启动复用原服务。

## 自动测试：63 / 63 通过

完整命令：

```powershell
python -X utf8 -m unittest web_lab.tests.test_api experiments.feature_validation.F01_response_adaptation.test_core experiments.feature_validation.F02_dynamic_questioning.test_core experiments.feature_validation.F02_dynamic_questioning.validation_repair.test_runtime -v
```

其中网页接口 / 数据 / 恢复测试 23 项，既有 F01 / F02 核心和最新运行守卫回归 40 项。最后一次完整运行 63 项通过，约 5.9 秒；原始日志在 [final_tests.log](../output/web_lab/final_tests.log)。`node --check web_lab/static/app.js` 与 `python -m compileall -q web_lab` 通过。

网页测试采用临时库和明确标记的模拟模型服务。覆盖：先保存原文再异步执行、幂等与重复提交保护、三次教师上限、提前结束、暂停 / 结束期间保留模型结果、重试独立尝试、守卫阻断保留原文、未完成调用重启记失败、不自动重采样、评价追加与空值、不同评价来源隔离、日期时区、新版本不替换冻结执行源码、生成事件观察时间、中文 JSON / CSV、CSV 公式文本转义、白名单工件、同源 / 主机边界、真实数据备份恢复。S0 在两个模拟慢模型占满队列时仍能独立完成。

## 有限真实 Codex 验收：4 / 4 调用返回有效首次输出

通过既有正常产品登录使用官方 `codex-cli 0.162.0-alpha.2`，模型请求 `gpt-6.1-sol`、推理档位 high，复用原 F01 phase2 传输及 F02 runtime / v3 守卫。未改传输配置，未读取认证文件，未使用模拟回复代替。模型过程经历原 CLI 的网络重连和 HTTP 回退，日志完整保留；不是网页人工重试。

| 功能 / 实验 | 教师序号 | 官方 CLI_success | 守卫 display_safe | 总耗时 | 输入历史长度 |
| --- | --- | --- | --- | --- | --- |
| F01 / bf5024cbc21f496ca00b4b9a32ae09fe | 1 | true | true | 131.8122 秒 | F01 无连续历史 |
| F02 / d2108bc0e9f34eeeb9e87e214c64a554 | 1 | true | true | 130.5688 秒 | 0 |
| 同一 F02 实验 | 2 | true | true | 138.3757 秒 | 2 |
| 同一 F02 实验 | 3 | true | true | 132.3857 秒 | 4 |

F01 结束原因为 `f01_single_reply`。F02 最后模型选择 `understanding_sufficient` 并结束，不再强制问答。第二、三次输入仅包含各自此前同路径对话，没有未来回答混入早期快照。

F02 首问询问 n=3 时 range 的变量及赋值后 s。第二次学生回答明确承认边界，但把赋值当累加；模型下一句询问右侧是否用到旧值，原文可追溯。第三次学生说明赋值和累加的区别、以及端点遗漏，模型转入自主修改。这里仅描述保存的对话，不为切题、理解、泄题或学习效果自动评分。

这两个真实模型实验的输入均由工程验收提供，**source_type=automated_test**，不是实际学习者体验。模型 token 用量、thread_id、首次原字节哈希、原事件 / stderr / 提示 / schema / 校验全部保存。汇总见 [real_smoke_summary.json](../output/web_lab/real_smoke_summary.json)，完整原文可直接在网页历史打开对应 ID 并导出。

## 浏览器实际检查

用 Playwright CLI 操作真实 Chromium，不向产品引入 Node 运行依赖。已检查：

| 检查项 | 结果与证据 |
| --- | --- |
| 首页、已有案例和新建 | 页面正常；选择 S0 并创建唯一实验 ID |
| F01 一轮 | 浏览器输入、发送、显示冻结 S0 原回复，正常结束 |
| F02 连续与真实 S1 | 官方链路三次真实输出，同路径历史长度 0 / 2 / 4 |
| 等待时网页可用 | 两个真实调用并行等待时浏览器仍可新建、浏览历史；模型提交 API 约 0.03 秒返回 |
| 刷新恢复 | S0 对话、评价和未验证源码均在 reload 后保留；真实实验在服务重启后仍完整 |
| 评价 | 浏览器保存部分评分和备注成功；其余为空，不计作正确 |
| 历史 | 可筛选 F01 / S0、重新打开对话与工件 |
| 新代码 | 浏览器保存 `def solve(n): return -999` 为文本，刷新后仍显示新版本未验证；旧证据明确标为冻结版本 |
| 统计 | 真实用户默认为 0，自动测试单列；全部来源可切换，保留分母和未评分数量 |
| 导出下载 | 浏览器成功下载 aic_all.json 与 aic_turns.csv；API 同时核验三类 CSV |
| 窗口适配 | 1440×960 三栏；1024×768 右侧移至下方，聊天区保留宽度 |
| 浏览器错误 | console：0 errors / 0 warnings |

浏览器 S0 联调实验 `132d03419eed4b599f1cabaa9e6adecb` 在默认首页创建，提交回答前纠正为 `automated_test`，并追加 `engineering_origin_corrected` 事件保留原始来源及纠正原因。控件评分备注明确写明“自动浏览器保存联调，不是实际学习者满意度”；不计入真实用户统计。

截图见 [首页](../output/web_lab/home.png)、[交互页](../output/web_lab/interaction.png)、[真实等待](../output/web_lab/real_waiting.png)、[未验证源码](../output/web_lab/unverified_code.png)、[历史](../output/web_lab/history.png)、[全部来源统计](../output/web_lab/stats_all.png)、[真实 F02 完成](../output/web_lab/real_f02_completed.png)、[1024 窗口交互](../output/web_lab/interaction_1024.png)。

## 导出、备份与历史保护

最终真实运行数据包含 3 次工程实验、5 轮教师输出 / 5 次运行尝试（4 次真实 Codex，1 次 S0），全部标为自动测试。真实用户实验 0，学习者满意度 / 教学准确率尚未验收。没有为了制造失败而重复消耗真实模型额度。

最终全量 JSON 中 66 份白名单工件的 base64 内容逐一解码，SHA-256 全部匹配。实验 / 轮次 / 调用 CSV 分别为 3 / 5 / 5 行，均带 UTF-8 BOM；原中文正确。SQLite `PRAGMA integrity_check` 返回 ok。导出副本在 `output/web_lab/final_all.json` 和 `final_experiments.csv`、`final_turns.csv`、`final_attempts.csv`。

真实数据备份命令 `python -X utf8 -m web_lab.backup` 已运行，生成 [备份目录](../backups/aic_web_20261010T154548068226Z)。备份库 integrity_check=ok，包含 3 实验、5 轮、5 尝试及 5 份原回复。另有自动测试验证备份恢复后原回答与关联工件可读。没有覆盖现有数据目录。

开发前记录原 `experiments/` 与 `docs/research/` 共 **2,780** 份历史文件 SHA-256（排除 Python 字节码缓存）；完成后 **0 份修改 / 缺失**。核对结果在 [historical_after_check.json](../output/web_lab/historical_after_check.json)。冻结案例、正式首份输出、历史失败与原评分均保留。

## 验收范围与已知限制

功能平台 V1 工程验收通过；实际学习者体验、教学语义和创新性仍等待人工评价。真实额度耗尽 / 长时间离线等外部状态未穷举；失败、超时、中断、部分原文和明确人工重试通过模拟联调 / 原运行回归验证，不称作真实模型失败实验已通过。

S1 仍可能需两分钟或更久；超时沿用 1200 秒。暂停 / 手动结束只控制会话状态，不取消已提交调用。新代码只记文本，未提供核验入口。五个冻结案例、最多三次 F02 教师输出、无长期知识诊断。未增加 F03～F06，未进行更多模型批次。本轮到此停止。
