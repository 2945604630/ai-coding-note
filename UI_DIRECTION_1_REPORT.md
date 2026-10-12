# V3 方向一：CodeHelper 参考型学习界面

## 设计与范围

参考对象已核对为 [CodeHelper Studio](https://github.com/SuLiverse/CodeHelper-Studio) 及其[错题指南](https://github.com/SuLiverse/CodeHelper-Studio/blob/master/docs/user-guide/mistakes-guide.md)。借鉴题目、代码、错误输出、AI 侧栏与重做入口的组织方式，采用独立的浅色视觉设计；不复制第三方实现或品牌素材。

四个入口：学习首页、编程工作台、错题本、学习历史。首页如实显示两道现有练习，优先继续练习；工作台给编辑器约六成宽度，结果在下方展开，右侧持续阅读辅导；错题回顾串联失败版本、实际输出、对应辅导、后续修改与重新测试。

## 实施结果

1. 复用现有会话、版本、任务及教学 API，前端投影按 session/version/SHA 绑定；新增 `/mistakes` 和 `/mistakes/{session_id}` 只读错题路由。
2. 完成学习首页、练习工作台、结果面板、错题列表、错题详情及学习历史；草稿恢复、快捷提问、真实等待和失败状态保留。
3. 使用 `8007` 与独立 `data/aic_ui_codehelper` 目录。Docker 固定镜像重新 build/accept 成功，真实提交产生了一条失败任务，详情展示 stdout、参考输出、源码 SHA 和 task ID。
4. 浏览器检查 1440px 桌面与 390px 窄屏；控制台 0 errors / 0 warnings。未调用真实付费 AI。

## 截图

本地截图位于 `output/playwright/`：

- `v3-home-1440.png`：学习首页
- `v3-workbench-ready-1440.png`：沙箱已验收的编程工作台
- `v3-mistakes-real-1440.png`：含真实失败任务的错题本
- `v3-mistake-detail-1440.png`：题目 → 错误输出 → 代码 → AI 辅导 → 后续修改
- `v3-history-390.png`：390px 窄屏学习历史

## 验证与边界

Node 记录投影守卫 4/4 通过；Python 既有学习/Provider/API 回归 29/29 通过；F01～F05 旧教学协议没有改动。沙箱验收使用固定镜像 `sha256:9f94accc36180132e48aed10e6ca7ac9d4151ff4230768019aaf92267581f842` 与策略摘要 `842b011ed3b81e9fc1cd4410625daad6485bbeb40fdb35de67ca8f167a6c0b39`，正确、错误和超时场景均真实执行并清理。

错题收藏、复习计划、掌握率和跨题知识点聚合仍没有后端字段，本轮显示真实失败记录与时间线，不生成这些数据。错题详情中的 AI 区域只引用已有会话回复；没有回复时明确显示空状态。实验管理保留原入口，学生页面默认不展示研究参数。
