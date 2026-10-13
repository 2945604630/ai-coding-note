export const runLabels = {
  queued: "排队中",
  running: "运行中",
  completed: "运行完成",
  passed: "指定测试通过",
  failed: "测试未通过",
  timeout: "运行超时",
  exception: "代码报错",
  resource_limit: "资源超限",
  output_limit: "输出过多",
  service_error: "执行服务异常",
  unavailable: "沙箱未就绪",
  output_mismatch: "输出与参考不一致",
};
export function needsReview(job) {
  return (
    [
      "failed",
      "timeout",
      "exception",
      "resource_limit",
      "output_limit",
      "service_error",
      "unavailable",
    ].includes(job.status) || (job.results || []).some((r) => outputsDiffer(r))
  );
}
export function outputsDiffer(result) {
  return (
    result.expected_output != null &&
    (result.stdout || "").replace(/\r\n/g, "\n") !== result.expected_output
  );
}
export function retryGate({
  dirty,
  historical,
  busy,
  turnVersion,
  currentVersion,
}) {
  return (
    coachGate({ dirty, historical, busy }) ||
    (turnVersion !== currentVersion
      ? "这次调用使用旧版本。请开始新的辅导，原失败记录会保留。"
      : "")
  );
}
export function currentJob(jobs, version) {
  return (
    jobs
      .filter(
        (j) =>
          j.version_id === version.version_id &&
          j.source_sha256 === version.source_sha256,
      )
      .at(-1) || null
  );
}
export function coachGate({ dirty, historical, busy }) {
  if (dirty) return "先保存编辑，再发送给教练。";
  if (historical) return "请回到当前保存版本后再发送。";
  if (busy) return "等待运行结束后再发送，教练才能看到这次结果。";
  return "";
}
export function versionName(versions, v) {
  if (!v) return "未找到的历史版本";
  if (v.label === "original") return "起始代码";
  if (v.label === "用户提交版本")
    return `修改 ${versions.filter((x) => x.label === "用户提交版本").indexOf(v) + 1}`;
  return "案例版本 · " + v.label;
}
