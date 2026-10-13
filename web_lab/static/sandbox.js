import { $, esc, time, withOrigin, api, toast } from "./ui.js";
import {
  runLabels,
  needsReview,
  currentJob,
  versionName,
  outputsDiffer,
} from "./learning-state.js";

export function mountSandbox({
  eid,
  version,
  dirty,
  state,
  refresh,
  showTab,
  viewVersion,
  locateLine,
  onStateChange,
}) {
  let sending = false,
    fingerprint = "",
    pending = null,
    reviewFingerprint = "";
  $("#run-controls").innerHTML =
    `<label for="sandbox-input">输入 n</label><input id="sandbox-input" aria-label="输入 n，0 到 8 的整数" type="number" min="0" max="8" step="1" value="3" required><button id="run-code" class="primary" type="button">运行一次</button><button id="submit-tests" type="button">提交测试</button>`;
  function resultHTML(job) {
    const mismatch = job.status === "completed" && needsReview(job),
      bad = needsReview(job);
    const label = mismatch
      ? "运行完成 · 输出与参考不一致"
      : runLabels[job.status] || job.status;
    const versionLabel = versionName(
      state().code_versions,
      state().code_versions.find((v) => v.version_id === job.version_id),
    );
    const waiting = ["queued", "running"].includes(job.status);
    return `<article class="sandbox-record ${bad ? "result-fail" : ""}"><div class="result-heading"><strong>${esc(label)}</strong><span class="small muted">${esc(versionLabel)} · ${job.mode === "run" ? "单次运行" : "提交测试"}${waiting ? "" : ` · ${Number(job.elapsed_seconds || 0).toFixed(2)} 秒`}</span></div>
      ${waiting ? '<p class="notice">任务已保存，正在等待结果。刷新后可以继续查看。</p>' : ""}
      ${job.error ? `<p class="notice error">${esc(job.error)}</p>` : ""}
      ${job.status === "timeout" ? '<p class="notice error">超过运行时间限制。先检查循环是否能结束，再修改代码重新运行。</p>' : ""}
      ${(job.results || [])
        .map((r, i) => {
          const different = outputsDiffer(r);
          const line = [
            ...(r.stderr || "").matchAll(
              /File "\/tmp\/student\.py", line (\d+)/g,
            ),
          ].at(-1)?.[1];
          return `<div class="sandbox-case"><div class="case-result-heading"><strong>输入 n = ${esc(r.input)}</strong><span class="${different || r.stderr ? "fail-text" : "muted"} small">${r.status === "passed" ? "通过" : different ? "输出不同" : runLabels[r.status] || r.status}${r.output_truncated ? " · 输出已截断" : ""}</span></div><div class="output-pair"><div><span class="small muted">实际输出（含返回值）</span><pre>${esc(r.stdout || "（空）")}</pre></div>${r.expected_output != null ? `<div><span class="small muted">参考输出</span><pre>${esc(r.expected_output)}</pre></div>` : '<p class="small muted">这个输入没有已审核参考输出，仅记录实际行为。</p>'}</div>
        ${r.stderr ? `<div class="traceback"><div class="case-result-heading"><strong class="small fail-text">Python 错误信息</strong>${line ? `<button class="link" data-error-line="${line}" data-error-version="${job.version_id}">定位第 ${line} 行 →</button>` : ""}</div><pre>${esc(r.stderr)}</pre></div>` : ""}</div>`;
        })
        .join("")}
      ${job.hidden_summary?.total ? `<p class="small">隐藏测试通过 ${job.hidden_summary.passed} / ${job.hidden_summary.total}；具体输入与输出不展示。</p>` : ""}
      ${!waiting ? `<p class="evidence-footnote">${job.executed ? "本次实际执行只对应这个版本与这些输入。" : "本次没有取得实际执行证据。"}有限测试不证明整体正确。</p><details class="result-source"><summary>运行时间与来源</summary><p class="small muted">${esc(time(job.created_at))} · 版本指纹 ${esc(job.source_sha256.slice(0, 12))} · 任务 ${esc(job.task_id.slice(0, 8))}</p></details>` : ""}</article>`;
  }
  function bindResults(container) {
    container.querySelectorAll("[data-error-line]").forEach(
      (b) =>
        (b.onclick = () => {
          if (viewVersion(b.dataset.errorVersion)) {
            showTab("code");
            locateLine(Number(b.dataset.errorLine));
          }
        }),
    );
    container.querySelectorAll("[data-review-version]").forEach(
      (b) =>
        (b.onclick = () => {
          if (viewVersion(b.dataset.reviewVersion)) showTab("code");
        }),
    );
  }
  function render() {
    const s = state().sandbox || {
        ready: false,
        reason: "未取得沙箱状态",
        jobs: [],
      },
      v = version(),
      changed = dirty();
    const busy =
      sending || s.jobs.some((j) => ["queued", "running"].includes(j.status));
    $("#run-code").disabled = busy || changed || !s.ready;
    $("#submit-tests").disabled = busy || changed || !s.ready;
    $("#run-code").textContent = busy ? "运行中…" : "运行一次";
    $("#review-state").className =
      "review-state " + (changed || !s.ready ? "warning" : "muted");
    $("#review-state").textContent = changed
      ? "草稿已保留在当前浏览器。先保存，才能运行和发送辅导。"
      : !s.ready
        ? s.reason
        : busy
          ? "运行任务已保存，等待结果；这时可以继续编辑。"
          : v.version_id !== state().current_code_version_id
            ? "运行只检查这个历史版本；辅导仍需要回到当前保存版本。"
            : "已保存，可以运行一次，或提交 3 个已审核测试。";
    const mark = JSON.stringify([
      s.jobs,
      v.version_id,
      v.source_sha256,
      changed,
    ]);
    if (mark !== fingerprint) {
      fingerprint = mark;
      const latest = currentJob(s.jobs, v);
      $("#sandbox-current").innerHTML = changed
        ? '<p class="notice">这份草稿尚未运行。原保存版本的结果保留在回顾与版本记录中。</p>'
        : latest
          ? resultHTML(latest)
          : '<p class="empty compact">这个版本还没有运行记录。试一个小输入，观察实际输出。</p>';
      $("#sandbox-history").innerHTML =
        [...s.jobs]
          .reverse()
          .map(
            (j) =>
              `<details><summary>${esc(time(j.created_at))} · ${esc(runLabels[j.status])} · ${esc(
                versionName(
                  state().code_versions,
                  state().code_versions.find(
                    (v) => v.version_id === j.version_id,
                  ),
                ),
              )}</summary>${resultHTML(j)}</details>`,
          )
          .join("") || '<p class="empty compact">尚未运行。</p>';
      bindResults($("#sandbox-current"));
      bindResults($("#sandbox-history"));
    }
    const reviewMark = JSON.stringify(s.jobs);
    if (reviewMark !== reviewFingerprint) {
      reviewFingerprint = reviewMark;
      const failures = s.jobs.filter(needsReview);
      $("#review-count").textContent = failures.length || "";
      $("#review-list").innerHTML =
        [...failures]
          .reverse()
          .map((j) => {
            const after = s.jobs.find(
              (x) =>
                x.created_at > j.created_at &&
                x.version_id !== j.version_id &&
                x.status === "passed",
            );
            return `<details class="review-item"><summary><span>${esc(
              versionName(
                state().code_versions,
                state().code_versions.find(
                  (v) => v.version_id === j.version_id,
                ),
              ),
            )} · ${esc(j.status === "completed" ? "输出与参考不一致" : runLabels[j.status])}</span><small>${esc(time(j.created_at))}${after ? " · 后续版本已有指定测试通过" : ""}</small></summary>${resultHTML(j)}<button data-review-version="${j.version_id}">查看当时的代码 →</button></details>`;
          })
          .join("") ||
        '<p class="empty compact">尚无失败运行。后续报错、超时和输出差异会保留在这里。</p>';
      bindResults($("#review-list"));
    }
  }
  async function send(mode) {
    if (
      sending ||
      dirty() ||
      !state().sandbox?.ready ||
      state().sandbox.jobs.some((j) => ["queued", "running"].includes(j.status))
    )
      return;
    const input = $("#sandbox-input");
    if (
      mode === "run" &&
      (!input.reportValidity() || !Number.isInteger(Number(input.value)))
    )
      return;
    const v = version(),
      data = withOrigin({
        version_id: v.version_id,
        source_sha256: v.source_sha256,
        ...(mode === "run" ? { input: Number(input.value) } : {}),
      });
    const signature = JSON.stringify([mode, data]);
    if (!pending || pending.signature !== signature)
      pending = { signature, request_id: crypto.randomUUID() };
    sending = true;
    showTab("code");
    render();
    onStateChange();
    try {
      await api(
        `/api/experiments/${eid}/sandbox/${mode === "run" ? "run" : "submit"}`,
        { ...data, request_id: pending.request_id },
      );
      pending = null;
      await refresh();
      toast("运行任务已保存，结果会自动更新。");
    } catch (error) {
      toast("执行请求未成功：" + error.message, true);
      try {
        await refresh();
      } catch {}
    } finally {
      sending = false;
      render();
      onStateChange();
    }
  }
  $("#run-code").onclick = () => send("run");
  $("#submit-tests").onclick = () => send("submit");
  return {
    render,
    busy: () =>
      sending ||
      (state().sandbox?.jobs || []).some((j) =>
        ["queued", "running"].includes(j.status),
      ),
  };
}
