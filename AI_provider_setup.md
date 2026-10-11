# AI Provider 配置

统一接口位于 `web_lab/ai_provider.py`：`AIProvider.__call__(feature, public, artifact)` 返回 output/checks/metadata，`public_config()` 只返回可公开信息。Service 统一检查 `provider_success`，兼容旧运行器的 `CLI_success`；继续使用原 F01/F02 提示、输出结构、引用/执行事实守卫和停止条件。没有改教学算法。

| Provider | 行为 |
|---|---|
| `codex_cli`（默认） | 委托原 `teaching.OfficialModel`；原官方传输、产品登录、冻结模型 gpt-6.1-sol、effort 与 1200 秒超时保持原样 |
| `api` | 外部兼容 Chat Completions 的可替换适配器；服务器向 Base URL 后追加 `/chat/completions`，发送原提示和 JSON schema，并要求 json_object 输出 |
| `disabled` | 不进行 AI 调用；首页默认选择固定规则 S0；旧 S1 会话若继续请求则明确失败，回答保留，不伪造回复 |

将根目录 `.env.example` 复制为 `.env`，或设置进程环境变量。环境变量优先。没有真实密钥的示例：

```dotenv
AIC_AI_PROVIDER=codex_cli
AIC_AI_BASE_URL=
AIC_AI_MODEL=
AIC_AI_API_KEY=
AIC_AI_TIMEOUT_SECONDS=60
AIC_AI_GENERATION_PARAMS={}
```

未来接入时，改 `AIC_AI_PROVIDER=api`，由用户自己填写 Base URL（例如服务商提供的 `https://…/v1`）、Model 和 API Key。URL 必须 HTTPS，仅 `localhost` / `127.0.0.1` / `::1` 允许 HTTP；拒绝 URL 中的用户名、密码、查询参数和 fragment；拒绝重定向，避免 Authorization 被转发。需要服务商支持 `/chat/completions`、JSON 输出和所选模型，不保证兼容所有厂商私有协议。

`AIC_AI_TIMEOUT_SECONDS` 接受 1～1200 的有限数值。`AIC_AI_GENERATION_PARAMS` 是 JSON 对象，允许 temperature（0～2）、top_p（0～1）、max_tokens（整数 1～8192）。未知 Provider、缺密钥/API Model、非法 URL 或参数会在服务器启动时明确失败。配置校验不请求远端，不检查余额。上述 API 配置项只作用于 `api`；`codex_cli` 保留冻结教学模型配置。改配置后须停止旧服务并重启。

密钥仅在服务器配置与内存中；`.env`、`.env.local` 已忽略。配置快照、`/api/health`、网页、SQLite 导出不包含 Key/Base URL。API HTTP 错误只保留状态与通用失败原因，不写请求 headers、原响应错误 body 或含凭据异常；输出中回显的精确密钥会被替换为 `[REDACTED]`。响应上限 1 MiB，TLS 使用系统默认验证。不要把 `.env` 纳入手工备份、截图或共享目录。

API 不成功、输出格式错误或守卫阻断时，沿用原失败/阻断流程，不自动重试、不切换到模拟成功。用户仍可保存回答和源码，并明确重试。

无需提供密钥的可替换性验证：

```powershell
python -X utf8 -m unittest web_lab.tests.test_ai_provider -v
```

2026-10-11 实测 4 项 Provider 测试通过，使用确定性替身传输、临时数据库和假密钥：验证默认 CLI 委托、disabled、配置错误、UTF-8（含 BOM）文件加载、环境变量覆盖 `.env`、超时/生成参数边界、原提示/守卫、API 失败不伪造回复、密钥不进入工件或导出。修复了旧代码的 `.env` 编码名称错误，Windows 本地配置文件现可正常加载。没有外部 API 或付费调用；未要求用户提供 Key。

实测 Codex CLI 0.162.0-alpha.17.2 已登录 ChatGPT；运行服务 `/api/health` 显示 `codex_cli`、冻结模型 `gpt-6.1-sol` 与原 1200 秒超时。CLI 委托与冻结工件回归通过，保留原调用链；本轮未重新生成模型教学回复，不能把模拟测试称为外部 API 联通或模型质量验收。V2 首页及学习设置可显示当前 Provider。
