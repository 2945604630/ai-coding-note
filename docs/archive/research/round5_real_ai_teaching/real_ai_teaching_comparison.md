> 历史归档；结论和停止指令仅适用于原报告阶段。当前状态以根目录 PROJECT_STATUS.md 为准。
> 本版仅调整路径、私人标识和归档说明；原字节与冻结路径保留在本机。仅本机证据不随 Git 分发。

# 第五轮真实 AI 教学比较：前置检查 blocked

日期：2026-10-09（Asia/Shanghai）。**真实模型实验未启动，S0/S1/S2 均未运行。** 本轮依用户的停止条件，在实际推理不可用时停止，没有扩充静态案例或使用 mock 替代模型。

## 实际 Provider 检查

当前进程和用户环境存在 REPLICATE_API_TOKEN；只记录变量名及是否配置，密钥值没有进入文件、终端输出或对话。工作区未发现 Provider 配置文件，Codex 配置仍是产品登录，没有标准 OpenAI API 凭据；没有使用产品登录令牌。

| 检查 | 实际响应 | 结论 |
| --- | --- | --- |
| 初始 urllib 账户检查 | HTTP 403，error code: 1010 | 未据此认定密钥失效 |
| 明确标识实验客户端后的账户检查 | HTTP 200 | Replicate 凭据可认证 |
| 模型元数据 | HTTP 200 | 模型端点及参数可查询 |
| 最小真实生成请求 | HTTP 402，Insufficient credit | 额度不足，推理前置条件不满足 |

本轮探测模型为 `meta/llama-4-maverick-instruct`；查询到的 Replicate 版本标识为 `d79a9e4383bf0533d313b30c0e5e7f313a61b4f0d0b928983f59028e959bf53e`。这是元数据版本，**没有成功生成响应可证明实际推理使用的版本**。接口形态依据 [Replicate 官方模型 API](https://replicate.com/meta/llama-4-maverick-instruct/api) 和 [官方 HTTP 文档](https://replicate.com/docs/reference/http/)。

为确认实际可推理性，只发送一次独立的就绪探测：要求返回 READY，输出上限 8 token，temperature=0、top_p=1、top_k=0。该请求不含任何教学案例，不是 S1 或 S2 的正式样本。服务返回 402 后没有换模型、重试生成或继续编写教学比较。

## 计数与原始证据

| 项目 | 实际值 |
| --- | --- |
| 就绪生成 POST 请求 | 1 |
| 成功生成 | 0 |
| S1 / S2 教学调用 | 0 / 0 |
| 可评分模型输出 | 0 |
| 模型 token、推理延迟、账单费用 | 未返回，unknown；不伪造为测量值 0 |
| 教学正确性、问题区分力、错误确认、修复泄露 | not_run |

密钥已经存在不等于推理可用。本轮阻塞原因从“未确认 Provider”进一步定位为“已认证 Replicate 的模型推理额度不足”，不能沿用第四轮的缺配置解释，也不能将额度错误解释为模型教学能力不足。

完整请求正文、公开模型元数据、HTTP 状态及错误体见 readiness.json（仅本机证据：`experiments/round5/results/readiness_20261009T051602159537Z_be90a9/readiness.json`；不随 Git 分发）。没有模型原文响应；raw_generation 为 null。复现源码和命令见 README（仅本机证据：`experiments/round5/README.md`；不随 Git 分发）。

## 停止位置与恢复条件

S0/S1/S2 教学评价协议尚未冻结，案例和人工标注未新增。Provider 失败发生在推理前置探测阶段，没有开展任何可据此计算教学质量的实验。未来恢复时仍须先冻结同模型、同事实、同参数与调用预算的正式协议，不能把本次 READY 请求计入教学优势。

所需能力是：Replicate 账户具有可用推理额度，或另一个已授权且能实际完成文本推理的 Provider。可以参照服务错误指向的 [账户计费页面](https://replicate.com/account/billing#billing) 检查额度；也可在本机配置替代服务。对话仅需 Provider 名称、模型标识和非秘密配置位置，不需要明文 API Key。

本轮到此暂停，等待用户处理 Provider 可用性及审核，不继续静态推演。
