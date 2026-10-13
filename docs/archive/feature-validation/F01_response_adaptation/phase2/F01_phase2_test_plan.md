> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# F01 第二阶段冻结计划与复现索引

调用前冻结协议（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/PROTOCOL.md`；不随 Git 分发）；调用前冻结哈希（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/freeze_manifest.json`；不随 Git 分发）。本索引在实验后生成，正式预设标准以这两个不可变文件为准。

| 情景 | 输入 | 私有参考 |
| --- | --- | --- |
| H01 | H01.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/inputs/H01.json`；不随 Git 分发） | H01.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/gold/H01.json`；不随 Git 分发） |
| H02 | H02.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/inputs/H02.json`；不随 Git 分发） | H02.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/gold/H02.json`；不随 Git 分发） |
| H03 | H03.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/inputs/H03.json`；不随 Git 分发） | H03.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/gold/H03.json`；不随 Git 分发） |
| H04 | H04.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/inputs/H04.json`；不随 Git 分发） | H04.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/gold/H04.json`；不随 Git 分发） |
| H05 | H05.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/inputs/H05.json`；不随 Git 分发） | H05.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/gold/H05.json`；不随 Git 分发） |
| H06 | H06.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/inputs/H06.json`；不随 Git 分发） | H06.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/gold/H06.json`；不随 Git 分发） |
| H07 | H07.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/inputs/H07.json`；不随 Git 分发） | H07.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/gold/H07.json`；不随 Git 分发） |
| H08 | H08.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/inputs/H08.json`；不随 Git 分发） | H08.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/gold/H08.json`；不随 Git 分发） |
| H09 | H09.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/inputs/H09.json`；不随 Git 分发） | H09.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/gold/H09.json`；不随 Git 分发） |
| H10 | H10.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/inputs/H10.json`；不随 Git 分发） | H10.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/gold/H10.json`；不随 Git 分发） |
| H11 | H11.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/inputs/H11.json`；不随 Git 分发） | H11.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/gold/H11.json`；不随 Git 分发） |
| H12 | H12.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/inputs/H12.json`；不随 Git 分发） | H12.json（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/gold/H12.json`；不随 Git 分发） |

12条模拟困难回应、原版S0、24次同模型教师推理；预选6个匿名辅助审查。gold允许动作与语义义务不传给教师或辅助评审，辅助评审只有公开事实/通用量表。新版本未提供不补造执行。工作目录隔离有OS限制。源码与原始错误全保留。

复现及CLI体验说明（仅本机证据：`experiments/feature_validation/F01_response_adaptation/phase2/README.md`；不随 Git 分发）
