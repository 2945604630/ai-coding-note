> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# F02 实际执行结果

正式教师推理21/21成功、首份原文完整，3个共享首问+18个后续决策；不是每条路径各自重新生成首问。独立辅助审查3次，CLI工程冒烟真实调用2次，总计26个不同会话。未观察到工具调用。请求模型gpt-6.1-sol、high，CLI 0.162.0-alpha.2，ChatGPT正常产品登录；后台精确模型快照未知。没有Replicate、密钥读取、主Agent模拟模型输出或质量重采样。

正式输出JSON结构通过21/21；冻结守卫可展示18/21。三份“已有反例、无新请求”被错误阻断，不能用模型语义合理替代实际路径成功。

| 路径 | S0自身结束 | S1结束 | S1教师输出 | 实际学生回应 |
| --- | --- | --- | --- | --- |
| C01_correct | understanding_sufficient | understanding_sufficient | 2 | 1 |
| C01_wrong | budget_limited | invalid_output | 2 | 1 |
| C01_partial | budget_limited | budget_limited | 3 | 2 |
| C01_unexpected | budget_limited | understanding_sufficient | 2 | 1 |
| C02_correct | understanding_sufficient | understanding_sufficient | 3 | 2 |
| C02_wrong | budget_limited | invalid_output | 3 | 2 |
| C02_partial | budget_limited | budget_limited | 3 | 2 |
| C02_unexpected | await_new_evidence | await_new_evidence | 2 | 1 |
| C03_correct | budget_limited | understanding_sufficient | 2 | 1 |
| C03_wrong | budget_limited | invalid_output | 2 | 1 |
| C03_partial | budget_limited | budget_limited | 3 | 2 |
| C03_unexpected | budget_limited | budget_limited | 3 | 2 |

全部12条学生路径是冻结模拟输入，不是真实学生。作者评分是带原文依据的模型辅助初审，未经独立人类认证。三次辅助AI审查都受到评审包未来历史污染，不能作为有效独立评分；原文和失败检查全部保留，未重新采样。相同基础模型的新会话也具有相关错误。不得把表格称为学习效果或总体准确率。

cases/与gold/、S0规则和正式模型原字节未改；历史F01家族969个文件hash相同。新的会话只提供公开代码、事实和该路径截至当时的真实历史，没有参考原因或其它路径回答。禁用工具/联网/技能，本地渲染没有技能目录；未建立OS文件读隔离，也未证明服务端全部隐藏上下文，因此不能称完全盲测。

记录层曾将history列表共享引用：原results逐轮索引64项中61项含当前或未来追加内容。原推理prompt与f02_input保存于追加前，未受影响。results/reconstruction_v2/从真实输入和实际前缀重建64/64项，并用冻结S0重新计算对照，结果一致；原索引不覆盖。辅助评审包已混入未来历史，3份评分均不采纳。部分material_id带前缀而旧解析器只认A/B，属于组织/解析器设计问题，不用程序补分或把它指责为模型不能输出JSON。

正式单次教师调用129.15～149.30秒，中位134.99秒。系统经历WebSocket超时重试再转HTTPS；CLI默认产品运输器的重连不是按评分重采样。两次教师输出通常约270秒，三次约405秒，未含真实学生思考/键入。当前等待对普通教学偏长，接受度未知，不能宣称适合真实学习。

全批已报告token：input=270730，output=38282；cached input=21120、reasoning output=11899为上述子项，不再相加。教师/审查/工程调用分项在results/run_accounting.json。CLI事件只给已报告用量，失败连接的额外用量未知；货币成本和订阅分摊未知。

固定规则自身25个去重决策，AI和同历史S0各21个去重决策。路径表的首问各出现4次，分项评分只计3个唯一首问。S0自身轨迹与S1轨迹的历史不同，不能直接计算公平教学效率优势；失败阻断、预算停止也不能算省步骤的收益。

S1实际4/12路径在理解充分后转自主修改，1/12等待新版，4/12预算耗尽，3/12接口失败。S0自身2/12理解充分、1/12等待新版、9/12预算耗尽。C03_partial另有版本不适配，不能把budget_limited称完整有效学习路径。

真实模型CLI工程冒烟退出0，记录见user_runs/20261010T134314_7398a46b/；S0脚本冒烟退出0。两者origin=scripted_engineering_smoke，反馈留空。真实用户/初学者记录0。当前CLI支持自由输入、最多3次教师输出、动作/依据/事实展示和反馈保存；达到预算即停止不代表问题解决。
