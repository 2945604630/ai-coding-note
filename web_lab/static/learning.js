import {
  $,
  esc,
  time,
  status,
  origin,
  withOrigin,
  api,
  toast,
  loadDraft,
} from "./ui.js";
import { runLabels } from "./learning-state.js";
const path = location.pathname;
$("#nav-history").classList.toggle("active", path === "/learning-history");
$("#nav-review").classList.toggle("active", path === "/learning-review");
$("#nav-home").classList.toggle(
  "active",
  path === "/" || path.startsWith("/study/"),
);
const caseInfo = {
  C01: {
    tag: "循环边界",
    title: "把整数求和跑明白",
    copy: "检查循环是否包含最后一个数，用小输入观察输出。",
  },
  C03: {
    tag: "局部修改与返回值",
    title: "一次修改，真的修好了吗？",
    copy: "对比循环与返回值，检查修改后仍然出错的边界。",
  },
};
const isTest = (e) =>
  e.source_type === "automated_test" ||
  ["automated_test", "simulated_student", "historical_replay"].includes(
    e.creation_input_origin?.kind,
  );
function draftHint(e) {
  return loadDraft(e.experiment_id, "code") ? " · 有本机草稿" : "";
}
function nextStep(e) {
  if (loadDraft(e.experiment_id, "code")) return "继续未保存的编辑";
  if (!e.current_job) return "运行当前保存版本";
  if (["queued", "running"].includes(e.current_job.status))
    return "查看正在进行的运行";
  if (e.current_job.status === "passed") return "复查想法，或继续学习";
  return "打开结果，继续修改";
}
function recordRows(rows) {
  return (
    rows
      .map(
        (e) =>
          `<a class="record-row" href="/study/${e.experiment_id}"><span class="record-main"><span class="record-dot ${esc(e.status)}"></span><span><strong>${esc(e.name)}</strong><small>${esc(time(e.updated_at))} · ${e.version_count} 个版本 · ${e.run_count} 次运行${esc(draftHint(e))}${isTest(e) ? " · 开发测试" : ""}</small></span></span><span class="record-meta">${esc(e.current_job ? runLabels[e.current_job.status] : status[e.status])}<span aria-hidden="true">→</span></span></a>`,
      )
      .join("") ||
    '<p class="empty">选一道练习，保存的代码与每次运行都会留在这里。</p>'
  );
}
function reviewRows(rows) {
  return (
    rows
      .map(
        (e) =>
          `<a class="mistake-link" href="/study/${e.experiment_id}?view=review"><span class="mistake-mark" aria-hidden="true">!</span><span><strong>${esc(e.name)}</strong><small>${e.review_count ? `${e.review_count} 次运行需要回看 · ${esc(runLabels[e.last_review.kind])}` : "辅导未取得有效回复"}${e.current_job?.status === "passed" ? " · 当前版本已有指定测试通过" : ""}${isTest(e) ? " · 开发测试" : ""}</small></span><span aria-hidden="true">→</span></a>`,
      )
      .join("") ||
    '<p class="empty">还没有需要回看的运行。代码报错、超时或输出差异会记录在这里。</p>'
  );
}
async function home() {
  const [all, cases, health] = await Promise.all([
    api("/api/learning/records"),
    api("/api/demo/cases"),
    api("/api/health"),
  ]);
  let showTests = localStorage.getItem("aic-v3:show-tests") === "true";
  let selectedMode = health.ai_provider?.provider === "disabled" ? "S0" : "S1",
    sessionName = "",
    creating = false,
    pending = null;
  const history = path === "/learning-history",
    review = path === "/learning-review";
  function render() {
    if ($("#mode")) selectedMode = $("#mode").value;
    if ($("#session-name")) sessionName = $("#session-name").value;
    const rows = all.filter((e) => showTests || !isTest(e)),
      reviews = rows.filter((e) => e.review_count || e.coach_failure_count);
    const last = localStorage.getItem("aic-v2:last-session");
    const candidate =
      rows.find((e) => e.experiment_id === last) ||
      rows.find((e) => e.status !== "completed") ||
      rows[0];
    const testControl = `<label class="check test-switch"><input id="show-tests" type="checkbox" ${showTests ? "checked" : ""}>显示开发测试记录</label>`;
    if (history || review) {
      $("#main").innerHTML =
        `<div class="home-shell history-shell"><div class="page-title"><div><span class="eyebrow">你的学习现场</span><h1>${review ? "错误回顾" : "学习记录"}</h1><p class="subtitle">${review ? "从真实失败回到对应版本，再看看后来怎么改。" : "按最近活动排列，重新打开即可接着写。"}</p></div><a class="button" href="/">选择练习 →</a></div><div class="section-heading"><span class="muted small">${review ? reviews.length : rows.length} 条练习${showTests ? " · 包含开发测试" : ""}</span>${testControl}</div><section class="record-board ${review ? "review-board" : ""}">${review ? reviewRows(reviews) : recordRows(rows)}</section><p class="history-note small muted">每个记录都保留原版本与结果。${review ? "出现后续通过结果，也不会删除之前的失败。" : ""}完整记录与导出可在<a href="/history">实验管理</a>查看。</p></div>`;
    } else {
      $("#main").innerHTML =
        `<div class="home-shell"><div class="home-hero"><div><span class="eyebrow">AIC / Python 学习空间</span><h1>把一个问题，<em>跑明白。</em></h1><p class="subtitle">写代码，观察结果，把不懂的地方留给教练。</p></div><span class="small muted local-note">记录保存在本机<br>AI 辅导按已配置的服务调用</span></div><div class="home-grid"><section class="start-area"><div class="section-heading"><h2>从一道小练习开始</h2><span class="count-chip">${cases.length} 道现有练习</span></div><div class="case-list">${cases
          .map((c, i) => {
            const info = caseInfo[c.case_id] || {
              tag: "Python 练习",
              title: c.label,
              copy: "修改代码，用运行结果检查你的判断。",
            };
            return `<article class="case-card"><span class="case-index">${String(i + 1).padStart(2, "0")}</span><div class="case-copy"><span class="tag">${esc(info.tag)}</span><h3>${esc(info.title)}</h3><p>${esc(info.copy)}</p></div><button class="primary start-case" data-case="${esc(c.case_id)}">开始练习 →</button></article>`;
          })
          .join(
            "",
          )}</div><details class="advanced"><summary>辅导方式与练习名称</summary><div class="advanced-fields"><label>练习名称（可选）<input id="session-name" maxlength="120" placeholder="例如：今天的循环练习"></label><label>辅导方式<select id="mode"><option value="S1" ${health.ai_provider?.provider === "disabled" ? "disabled" : ""}>${health.ai_provider?.provider === "disabled" ? "AI 当前已关闭" : health.ai_provider?.provider === "api" ? "AI 辅导 · 外部服务" : "AI 辅导 · Codex CLI"}</option><option value="S0" ${health.ai_provider?.provider === "disabled" ? "selected" : ""}>离线固定提示 · 不调用模型</option></select></label><p class="small muted">首次引导是固定问题，后续辅导最多两次。外部 AI 会接收有限代码与运行摘录。</p></div></details></section><aside class="continue-area"><span class="section-kicker">接着上次的思路</span><h2>${candidate ? "继续练习" : "你的第一段代码，从这里开始"}</h2>${candidate ? `<div class="continue-card"><span class="continue-status">${isTest(candidate) ? "开发测试 · " : ""}${esc(status[candidate.status])}</span><h3>${esc(candidate.name)}</h3><p>${esc(nextStep(candidate))}${esc(draftHint(candidate))}</p><a class="button primary" href="/study/${candidate.experiment_id}">回到工作台 →</a></div>` : '<p class="continue-empty">选左边的一道题。先试一次运行，再决定从哪里修改。</p>'}<p class="small muted">编辑草稿自动保留在当前浏览器；点击保存后才会建立可运行的代码版本。</p></aside></div><section class="recent"><div class="section-heading"><h2>最近练习</h2><a href="/learning-history">全部学习记录 →</a></div><div class="recent-grid"><section class="record-board">${recordRows(rows.slice(0, 4))}</section><section class="mistake-board"><div class="board-label"><span>值得再看一遍</span><a href="/learning-review">错误回顾 →</a></div>${reviewRows(reviews.slice(0, 3))}</section></div></section><footer class="home-footer">${testControl}<a href="/manage">实验管理与导出 ↗</a></footer></div>`;
    }
    if ($("#mode")) $("#mode").value = selectedMode;
    if ($("#session-name")) $("#session-name").value = sessionName;
    $("#show-tests").disabled = creating;
    document
      .querySelectorAll(".start-case")
      .forEach((b) => (b.disabled = creating));
    $("#show-tests").onchange = (ev) => {
      showTests = ev.target.checked;
      localStorage.setItem("aic-v3:show-tests", showTests);
      render();
    };
    document.querySelectorAll(".start-case").forEach(
      (btn) =>
        (btn.onclick = async () => {
          if (creating) return;
          creating = true;
          $("#show-tests").disabled = true;
          document
            .querySelectorAll(".start-case")
            .forEach((b) => (b.disabled = true));
          btn.textContent = "打开中…";
          const data = withOrigin({
            feature: "DEMO",
            case_id: btn.dataset.case,
            mode: $("#mode").value,
            source_type:
              origin() === "automated_test" ? "automated_test" : "real_user",
            name: $("#session-name").value,
            entry_point: "learning",
          });
          if (!pending || JSON.stringify(pending.data) !== JSON.stringify(data))
            pending = { data, id: crypto.randomUUID() };
          try {
            const e = await api("/api/experiments", {
              ...data,
              request_id: pending.id,
            });
            localStorage.setItem("aic-v2:last-session", e.session_id);
            location.href = "/study/" + e.session_id;
          } catch (error) {
            toast(error.message, true);
            creating = false;
            $("#show-tests").disabled = false;
            document.querySelectorAll(".start-case").forEach((b) => {
              b.disabled = false;
              b.textContent = "开始练习 →";
            });
          }
        }),
    );
  }
  render();
}
try {
  if (path.startsWith("/study/")) {
    const eid = path.split("/")[2];
    if (path.endsWith("/assessment"))
      await (await import("./assessment.js")).assessment(eid);
    else await (await import("./study.js")).study(eid);
  } else await home();
} catch (error) {
  $("#main").innerHTML =
    `<div class="home-shell error-page"><h1>暂时无法打开</h1><p class="notice error">${esc(error.message)}</p><button id="reload-page">重新加载</button> <a class="button" href="/">返回首页</a></div>`;
  $("#reload-page").onclick = () => location.reload();
}
