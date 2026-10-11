# F02 最小连续追问原型

在项目根目录 PowerShell 执行一条命令：

```powershell
python -X utf8 -m experiments.feature_validation.F02_dynamic_questioning.cli
```

选择C01/C02/C03，默认真实Codex S1；显示代码与可信证据，自己输入任意回答，最多3次教师输出。可/quit退出，最后记录是否切题、是否理解意图、是否希望继续使用。需要已安装官方Codex CLI并用产品正常登录；不需要在对话提供密钥。首次调用可能较慢。

固定基线体验：命令末加 `--arm S0`。指定案例加 `--case C02`。规则与AI是可选择的对照，不声称自动混合路由已经验证。

真实键入记录保存在user_runs/独立目录；正式模拟实验在results/，模型原字节与事件在responses/。--scripted-smoke仅供工程测试，会标注模拟冒烟，不能混入真实用户数据。

复现顺序：先运行单元测试，再prepare冻结，再run batch。当前包冻结后禁止重跑首份正式结果；要复核使用已有responses和results，不能覆盖或按结果修改规则。全包复制到新目录时需保留模块导入结构及历史依赖路径。

```powershell
python -X utf8 -m unittest experiments.feature_validation.F02_dynamic_questioning.test_core
python -X utf8 -m experiments.feature_validation.F02_dynamic_questioning.prepare
python -X utf8 -m experiments.feature_validation.F02_dynamic_questioning.run batch
```

只执行审核原版与local_patch，模型新代码不运行。新模型会话显式获得同路径对话历史，没有原研究上下文、参考原因、评价或其它路径回答。禁用工具/技能并检查事件；没有OS级禁止读取其它目录，不称完全盲测。
