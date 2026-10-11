"use strict";
const app = document.getElementById("app");
const statusLabels = {
  active: "进行中",
  paused: "已暂停",
  completed: "已结束",
  failed: "失败",
  blocked: "守卫阻断",
  succeeded: "已完成",
  queued: "排队中",
  connecting: "正在连接",
  generating: "正在生成",
};
const reasons = {
  f01_single_reply: "F01 单轮完成",
  understanding_sufficient: "当前理解足够，转入自行修改",
  await_new_evidence: "等待新版本证据",
  user_choice: "暂停判断，交给用户选择",
  budget_limited: "达到三次教师输出上限",
  manual_end: "手动结束",
  manual_early_complete: "人工提前完成",
  manual_pause: "手动暂停",
  model_call_failed: "模型调用失败",
  guard_blocked: "输出被守卫阻断",
  server_restarted: "上次服务中断",
};
const dimensions = [
  ["on_topic", "是否切题"],
  ["repetitive", "是否重复无意义追问"],
  ["fact_error", "是否存在程序事实错误"],
  ["full_repair", "是否直接给出完整修复"],
  ["used_previous", "是否利用上一轮回答"],
];
const $ = (s) => document.querySelector(s);
const esc = (v) =>
  String(v ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const date = (v) =>
  v
    ? new Date(v).toLocaleString("zh-CN", {
        timeZone: "Asia/Shanghai",
        hour12: false,
      })
    : "—";
const seconds = (v) => (v == null ? "—" : Number(v).toFixed(1) + " 秒");
const sourceLabel = (value) => {
  if(typeof value === 'object') {
    const kind=value.creation_input_origin?.kind;
    if(kind==='automated_test' || value.source_type==='automated_test')return '自动测试（含来源更正）';
    if(kind==='manual_browser')return '浏览器手动声明（未认证真人）';
    return '来源未确认（保留创建设定）';
  }
  return value==='automated_test'?'自动测试创建设定':'用户创建设定（不认证真人）';
};
const badge = (v) =>
  `<span class="badge ${esc(v)}">${esc(statusLabels[v] || v)}</span>`;
const option = (v, t) => `<option value="${esc(v)}">${esc(t)}</option>`;
let toastTimer;
let uiVersion = null;
const inputOrigin = () => {
  const flag=new URLSearchParams(location.search).get('source_type');
  if(flag==='automated_test')sessionStorage.setItem('aic-input-origin','automated_test');
  if(flag==='real_user')sessionStorage.removeItem('aic-input-origin');
  return navigator.webdriver || sessionStorage.getItem('aic-input-origin')==='automated_test' ? 'automated_test' : 'manual_browser';
};
function toast(message, error = false) {
  const el = $("#toast");
  el.textContent = message;
  el.dataset.error = error;
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (el.hidden = true), 5500);
}
async function api(url, data) {
  if (data !== undefined && uiVersion === 'V2' && (/\/turns$|\/code$|\/notes$|\/feedback$|\/control$|\/help$|\/first$|\/assessment-code$|\/assessment$|\/verify$|^\/api\/experiments$/.test(url))) {
    data = {...data, input_origin: inputOrigin()};
  }
  const response = await fetch(
    url,
    data === undefined
      ? {}
      : {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        },
  );
  if (!response.ok) {
    let detail;
    try {
      detail = (await response.json()).detail;
    } catch {
      detail = response.statusText;
    }
    throw new Error(
      typeof detail === "string" ? detail : "输入无效，请检查必填项",
    );
  }
  return response.json();
}
function exports(eid) {
  const query = eid ? "&experiment_id=" + encodeURIComponent(eid) : "";
  return `<div class="export-links"><a class="button subtle" href="/api/export/json?${query.slice(1)}">导出 JSON</a><a class="button subtle" href="/api/export/csv?kind=experiments${query}">实验 CSV</a><a class="button subtle" href="/api/export/csv?kind=turns${query}">轮次 CSV</a><a class="button subtle" href="/api/export/csv?kind=attempts${query}">调用 CSV</a></div>`;
}
function metrics(s) {
  return `<div class="metrics">${[
    ["实验总数", s.total, "当前筛选范围"],
    ["已结束", s.completed, "含手动结束和预算结束"],
    ["失败", s.failed, "原文与日志已保留"],
    ["未完成", s.unfinished, "进行中或已暂停"],
  ]
    .map(
      ([label, value, note]) =>
        `<div class="metric"><span>${label}</span><strong>${value}</strong><span>${note}</span></div>`,
    )
    .join("")}</div>`;
}
function records(rows) {
  if (!rows.length)
    return '<div class="empty">还没有实验记录。开始一次实验后，数据会自动保存在本地。</div>';
  return `<div class="table-wrap"><table><thead><tr><th>实验名称</th><th>功能 / 案例</th><th>模式</th><th>状态</th><th>开始时间</th><th>数据来源</th><th></th></tr></thead><tbody>${rows.map((e) => `<tr><td><a href="/experiments/${e.experiment_id}">${esc(e.name)}</a><span class="small muted mono">${e.experiment_id.slice(0, 12)}</span></td><td>${e.feature} / ${e.case_id}</td><td>${e.mode}</td><td>${badge(e.status)}</td><td>${date(e.created_at)}</td><td class="small">${sourceLabel(e)}</td><td><a href="/experiments/${e.experiment_id}">打开记录 →</a></td></tr>`).join("")}</tbody></table></div>`;
}
async function home() {
  const testOrigin =
    new URLSearchParams(location.search).get("source_type") ===
    "automated_test";
  const [cases, rows, s] = await Promise.all([
    Promise.all([api("/api/cases"), api("/api/demo/cases").catch(()=>[])]).then(([a,b])=>a.concat(b)),
    api("/api/experiments"),
    api("/api/stats"),
  ]);
  const previous = rows.find(
    (e) =>
      ["active", "paused", "failed"].includes(e.status) &&
      e.source_type === "real_user",
  );
  app.innerHTML = `<div class="page"><div class="page-heading"><div><div class="eyebrow">本地实验 / 逐轮记录</div><h1>从一次真实对话开始</h1><p>选择已核验案例，观察 AI 的下一步教学动作，留下可追溯的实验记录。</p></div><span class="badge">${testOrigin ? "自动测试入口 · 数据单独标记" : (cases.some(c => c.feature === "DEMO") ? "F01～F05 Demo · 真实 CLI 后端" : "F01 · F02 原服务")}</span></div><div class="home-grid"><section class="panel"><div class="section-head"><h2>新建实验</h2><span class="small muted">回答和调用记录自动保存</span></div><form id="create-form"><div class="form-grid"><div class="field"><label for="feature">验证功能</label><select id="feature" name="feature"><option value="DEMO">F01～F05 · 最小可用 Demo</option><option value="F01">F01 · 单次回应与动作选择</option><option value="F02">F02 · 动态追问与连续教学</option></select></div><div class="field"><label for="mode">实验模式</label><select id="mode" name="mode"><option value="S1">S1 · 真实 Codex AI</option><option value="S0">S0 · 固定规则，无模型</option></select></div></div><div class="field"><label for="case-id">编程案例</label><select id="case-id" name="case_id"></select></div><div class="field"><label for="experiment-name">实验名称 <span class="muted small">可选</span></label><input id="experiment-name" name="name" maxlength="120" placeholder="例如：循环边界 · 第一次体验"></div><p class="small muted" id="mode-note">S1 使用当前已登录的官方 Codex CLI，单轮可能等待数分钟。</p><button class="primary block-button" type="submit" id="start-experiment">开始实验 →</button></form></section><section class="panel"><h2 class="section-head">当前可以验证什么</h2><div class="feature-list"><div class="feature-row"><span class="feature-code">F01</span><div><h3>理解这一次回答</h3><p>对一个自然语言回应选择追问、反例、提示或自行修改。只完成一轮。</p></div></div><div class="feature-row"><span class="feature-code">F02</span><div><h3>让追问接着回答走</h3><p>基于同一对话继续教学，最多三次教师输出；理解足够时提前结束。</p></div></div></div><p class="small muted">程序事实有受控核验；切题、重复和帮助程度由你评价。未评分保持“未评价”。</p>${previous ? `<div class="resume-box"><p class="small">上次未完成：<strong>${esc(previous.name)}</strong> ${badge(previous.status)}</p><a class="button subtle" href="/experiments/${previous.experiment_id}">继续上次实验 →</a></div>` : '<div class="resume-box small muted">还没有需要继续的用户实验。</div>'}</section></div>${metrics(s)}<section class="panel"><div class="section-head"><h2>最近的实验</h2><a href="/history">全部记录 →</a></div>${records(rows.slice(0, 6))}</section></div>`;
  const update = () => {
    $("#case-id").innerHTML = cases
      .filter((c) => c.feature === $("#feature").value)
      .map((c) => option(c.case_id, c.case_id + " · " + c.label))
      .join("");
  };
  if (!cases.some(c => c.feature === "DEMO")) {
    $("#feature option[value=DEMO]").remove();
    $("#feature").value = "F01";
  }
  update();
  $("#feature").addEventListener("change", update);
  $("#mode").addEventListener(
    "change",
    () =>
      ($("#mode-note").textContent =
        $("#mode").value === "S1"
          ? "S1 使用当前已登录的官方 Codex CLI，单轮可能等待数分钟。"
          : "S0 复用冻结规则，不调用模型；规则回复不代表真实 AI。"),
  );
  let busy = false,
    requestId = crypto.randomUUID();
  $("#create-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (busy) return;
    busy = true;
    $("#start-experiment").disabled = true;
    try {
      const data = Object.fromEntries(new FormData(event.target));
      const e = await api("/api/experiments", {
        ...data,
        source_type: testOrigin ? "automated_test" : "real_user",
        request_id: requestId,
      });
      location.href = "/experiments/" + e.experiment_id;
    } catch (error) {
      toast(error.message, true);
      busy = false;
      $("#start-experiment").disabled = false;
    }
  });
}
async function history() {
  const cases = (await api("/api/cases")).concat(await api("/api/demo/cases").catch(()=>[]));
  app.innerHTML = `<div class="page"><div class="page-heading"><div><div class="eyebrow">实验归档</div><h1>历史记录</h1><p>查看原始对话、人工反馈、程序版本与每次调用。此处保留网页历史记录，包含 V2 学习会话。</p></div>${exports()}</div><section class="panel"><form id="filters" class="filters"><div><label for="filter-date">日期（北京时间）</label><input id="filter-date" type="date" name="date"></div><div><label for="filter-feature">功能</label><select id="filter-feature" name="feature"><option value="">全部</option><option>DEMO</option><option>F01</option><option>F02</option></select></div><div><label for="filter-case">案例</label><select id="filter-case" name="case_id"><option value="">全部</option>${cases.map((c) => option(c.case_id, c.feature + " / " + c.case_id)).join("")}</select></div><div><label for="filter-mode">模式</label><select id="filter-mode" name="mode"><option value="">全部</option><option>S0</option><option>S1</option></select></div><div><label for="filter-status">状态</label><select id="filter-status" name="status"><option value="">全部</option>${["active", "paused", "completed", "failed"].map((v) => option(v, statusLabels[v])).join("")}</select></div><div><label for="filter-source">来源</label><select id="filter-source" name="source_type"><option value="">全部</option><option value="real_user">用户创建设定</option><option value="automated_test">自动测试</option></select></div></form><div id="history-count" class="small muted"></div><div id="history-records"></div></section></div>`;
  const update = async () => {
    try {
      const params = new URLSearchParams(
        [...new FormData($("#filters"))].filter(([, v]) => v),
      );
      const rows = await api("/api/experiments?" + params);
      $("#history-count").textContent = `当前筛选 ${rows.length} 次实验`;
      $("#history-records").innerHTML = records(rows);
    } catch (e) {
      toast(e.message, true);
    }
  };
  $("#filters").addEventListener("change", update);
  $("#filters").addEventListener("submit", (e) => e.preventDefault());
  await update();
}
async function statistics() {
  app.innerHTML = `<div class="page"><div class="page-heading"><div><div class="eyebrow">数据统计 / 保留分母</div><h1>数据统计</h1><p>保留未评价数量，按来源观察。用户反馈与客观执行检查分别计数。</p></div>${exports()}</div><div class="field"><label for="stats-source">统计范围</label><select id="stats-source"><option value="real_user">用户创建设定（非真人证明）</option><option value="automated_test">自动测试实验</option><option value="">全部来源</option></select></div><div id="statistics-body"></div></div>`;
  const update = async () => {
    try {
      const s = await api("/api/stats" + ($("#stats-source").value ? "?source_type=" + $("#stats-source").value : ""));
      const grouped = (title, counts) =>
        `<section class="panel"><h2>${title}</h2><table><thead><tr><th>分类</th><th>次数</th></tr></thead><tbody>${
          Object.entries(counts)
            .map(([k, v]) => `<tr><td>${esc(k)}</td><td>${v}</td></tr>`)
            .join("") || '<tr><td colspan="2">暂无记录</td></tr>'
        }</tbody></table></section>`;
      $("#statistics-body").innerHTML =
        `${metrics(s)}<p class="stat-explanation">已评价 ${s.evaluated_turns} / ${s.turns} 轮；未评价 ${s.unrated_turns} 轮。下表使用每轮最新一份用户主观评价；“不确定 / 待核验”不计作“是”。</p><section class="panel"><h2>用户逐轮反馈</h2><div class="table-wrap"><table><thead><tr><th>评价维度</th><th>是</th><th>否</th><th>不确定 / 待核验</th><th>未评价</th><th>分母</th></tr></thead><tbody>${dimensions
          .map(([k, t]) => {
            const v = s.feedback[k];
            return `<tr><td>${t}</td><td>${v.yes}</td><td>${v.no}</td><td>${v.uncertain}</td><td>${v.unrated}</td><td>${v.denominator}</td></tr>`;
          })
          .join(
            "",
          )}</tbody></table></div><p class="small muted">数据来源：用户主观反馈。以上不是经认证的功能准确率；筛选按原创建设定，每次输入来源单独记录，更正保留原文。</p></section><div class="stat-grid">${s.answer_origins ? grouped("每次回答的实际来源声明",s.answer_origins) : ""}${grouped("按功能", s.by_feature)}${grouped("按案例", s.by_case)}<section class="panel"><h2>真实 Codex 调用</h2><dl class="status-list"><dt>成功 / 全部尝试</dt><dd>${s.ai_calls.success} / ${s.ai_calls.denominator}</dd><dt>失败 / 等待中</dt><dd>${s.ai_calls.failed} / ${s.ai_calls.pending}</dd><dt>平均耗时</dt><dd>${seconds(s.latency.average_seconds)}</dd><dt>最短 / 最长</dt><dd>${seconds(s.latency.min_seconds)} / ${seconds(s.latency.max_seconds)}</dd><dt>耗时分母</dt><dd>${s.latency.denominator} 次已结束真实调用</dd><dt>S0 规则尝试</dt><dd>${s.s0_attempts}</dd><dt>模拟服务尝试</dt><dd>${s.simulated_calls.denominator}</dd></dl><p class="small muted">传输成功包含守卫阻断的情况，不等于教学正确。</p></section><section class="panel"><h2>核验与数据来源</h2><dl class="status-list"><dt>结构 / 引用 / 受控执行放行</dt><dd>${s.objective_checks.passed} / ${s.objective_checks.denominator} 轮</dd><dt>用户创建设定（非真人证明）</dt><dd>${s.by_source.real_user || 0}</dd><dt>自动测试实验</dt><dd>${s.by_source.automated_test || 0}</dd><dt>用户反馈修订</dt><dd>${s.evaluation_sources.user_subjective || 0}</dd><dt>AI 辅助评价记录</dt><dd>${s.evaluation_sources.ai_auxiliary || 0}</dd><dt>独立人工复核记录</dt><dd>${s.evaluation_sources.independent_human || 0}</dd></dl><p class="small muted">“已核验案例”指源码与输入输出事实已核对，程序仍可能有错误。教学语义仍需人工复核。</p></section></div>`;
    } catch (e) {
      toast(e.message, true);
    }
  };
  $("#stats-source").addEventListener("change", update);
  await update();
}

function highlight(source) {
  const pattern =
    /(#[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b(?:def|return|for|in|if|else|elif|while|import|from|as|and|or|not|True|False|None|raise|class|with|try|except|pass)\b|\b\d+\b)/g;
  let result = "",
    last = 0;
  for (const match of source.matchAll(pattern)) {
    result += esc(source.slice(last, match.index));
    const token = match[0],
      type = token.startsWith("#")
        ? "comment"
        : /^["']/.test(token)
          ? "string"
          : /^\d/.test(token)
            ? "number"
            : "keyword";
    result += `<span class="tok-${type}">${esc(token)}</span>`;
    last = match.index + token.length;
  }
  return result + esc(source.slice(last));
}
let experiment,
  selectedTurn,
  chatFingerprint = "",
  codeFingerprint = "",
  noteFingerprint = "",
  pollTimer;
function latestFeedback(t) {
  return (
    t.feedback
      .filter((f) => f.evaluation_source === "user_subjective")
      .at(-1) || {}
  );
}
function showFeedback() {
  const turns = experiment.turns;
  const valid = turns.find((t) => t.turn_id === selectedTurn);
  const t = valid || turns.at(-1);
  selectedTurn = t?.turn_id;
  if (!t) {
    $("#feedback-area").innerHTML =
      '<p class="small muted">产生教师回复后可以逐轮评价。</p>';
    return;
  }
  const f = latestFeedback(t);
  $("#feedback-area").innerHTML =
    `<label for="feedback-turn">评价轮次</label><select id="feedback-turn">${turns.map((x) => option(x.turn_id, `第 ${x.number} 轮 · ${statusLabels[x.status]}`)).join("")}</select><form id="feedback-form">${dimensions.map(([key, label]) => `<div class="feedback-field"><label for="feedback-${key}">${label}</label><select id="feedback-${key}" name="${key}"><option value="">跳过</option><option value="yes">是</option><option value="no">否</option><option value="uncertain">${["fact_error", "full_repair"].includes(key) ? "待核验" : "不确定"}</option></select></div>`).join("")}<div class="feedback-field"><label for="feedback-satisfaction">帮助满意度</label><select name="satisfaction" id="feedback-satisfaction"><option value="">跳过</option>${[1, 2, 3, 4, 5].map((v) => option(v, v + " 分")).join("")}</select></div><div class="field"><label for="feedback-notes">评价备注</label><textarea name="notes" id="feedback-notes" class="feedback-note" placeholder="可留空"></textarea></div><button type="submit" class="feedback-save">保存本轮评价</button><p id="feedback-saved" class="small muted">${f.created_at ? "最近修改：" + date(f.created_at) : "未评价 · 所有项目均可跳过"}</p></form><details class="revision-list"><summary>评价修订记录（${t.feedback.length}）</summary>${t.feedback.map((x) => `<p>${date(x.created_at)} · ${esc(x.evaluation_source)}<br>${dimensions.map(([k, l]) => l + "：" + ({ yes: "是", no: "否", uncertain: "不确定 / 待核验" }[x[k]] || "未评价")).join("；")}<br>${esc(x.notes || "")}</p>`).join("")}</details>`;
  $("#feedback-turn").value = t.turn_id;
  for (const [k, v] of Object.entries(f)) {
    const field = $("#feedback-form").elements.namedItem(k);
    if (field) field.value = v ?? "";
  }
  $("#feedback-turn").addEventListener("change", () => {
    selectedTurn = $("#feedback-turn").value;
    showFeedback();
  });
  $("#feedback-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = event.target.querySelector("button");
    button.disabled = true;
    const data = Object.fromEntries(new FormData(event.target));
    for (const k of dimensions.map((x) => x[0])) data[k] = data[k] || null;
    data.satisfaction = data.satisfaction ? Number(data.satisfaction) : null;
    data.notes = data.notes || null;
    data.evaluation_source = "user_subjective";
    try {
      await api("/api/turns/" + selectedTurn + "/feedback", data);
      experiment = await api("/api/experiments/" + experiment.experiment_id);
      showFeedback();
      toast("评价已保存，旧版评价仍可追溯");
    } catch (e) {
      toast(e.message, true);
      button.disabled = false;
    }
  });
}
function renderCode() {
  const current = experiment.code_versions.find(
    (v) => v.version_id === experiment.current_code_version_id,
  );
  const key = JSON.stringify(experiment.code_versions);
  if (key === codeFingerprint) return;
  codeFingerprint = key;
  const caseData = experiment.case_snapshot;
  $("#question").textContent = caseData.statement;
  $("#contract").textContent = caseData.input_contract;
  $("#code-version").innerHTML = experiment.code_versions
    .map((v) =>
      option(
        v.version_id,
        v.label +
          (v.verification_status === "unverified"
            ? " · 未验证"
            : " · 已核验案例"),
      ),
    )
    .join("");
  $("#code-version").value = current.version_id;
  const update = () => {
    const v = experiment.code_versions.find(
      (v) => v.version_id === $("#code-version").value,
    );
    $("#source-code").innerHTML = highlight(v.source);
    $("#code-verification").innerHTML =
      v.verification_status === "unverified"
        ? '<span class="badge unverified">新版本未验证 · 仅文本记录</span>'
        : '<span class="badge">源码与运行事实已核验</span>';
  };
  update();
  $("#code-version").onchange = update;
  $("#original-code").innerHTML = highlight(caseData.source);
  $("#evidence").innerHTML =
    `${current.verification_status === "unverified" ? '<p class="notice">当前新版本未验证。以下事实属于冻结版本，不能用于证明新版输出。</p>' : ""}<table class="evidence-table"><thead><tr><th>证据 / 版本</th><th>输入</th><th>实际</th><th>预期</th></tr></thead><tbody>${caseData.evidence.map((e) => `<tr><td>${e.evidence_id}<br><span class="muted">${e.source_version || "original"}</span></td><td class="mono">${esc(JSON.stringify(e.args))}</td><td>${e.actual ?? e.value}</td><td>${e.expected}</td></tr>`).join("")}</tbody></table>`;
  $("#known-facts").textContent =
    "仅上述版本、合法输入和输出已经核验。是否理解题意、独立修改结果和教学帮助程度尚待观察。";
}
function message(t) {
  const out = t.output,
    successful = t.status === "succeeded";
  const model =
    experiment.mode === "S0"
      ? "S0 固定规则"
      : experiment.model_provenance === "simulated_model"
        ? "模拟模型（自动测试）"
        : "Codex 实际回复";
  return `${t.answer_raw ? `<article class="message student"><div class="meta">你的回答 · ${date(t.submitted_at)}</div><div class="message-body">${esc(t.answer_raw)}</div></article>` : ""}<article class="message teacher"><div class="meta"><span class="teacher-label">${model}</span><span>第 ${t.number} 次后续回复 · 源码 ${t.code_version_id.slice(0,8)}</span>${badge(t.status)}<span>${seconds(t.elapsed_seconds)}</span></div>${successful ? `${t.code_version_id !== experiment.current_code_version_id ? '<p class="notice">此回复基于上方标注的旧源码版本；不能当作当前修改版的执行结果。</p>' : ""}<div class="message-body">${esc(out.student_message)}</div><div class="turn-footer"><span class="badge">${esc(experiment.action_labels[out.next_action])}</span><button class="subtle evaluate-turn" data-turn="${t.turn_id}">评价这一轮</button></div><details><summary>查看回应解释、证据与未知项</summary><p>有限理解（未认证）：${esc(out.interpretation)}</p><p>选择依据（未认证）：${esc(out.decision_basis)}</p><p>引用：${esc(out.evidence_refs.join("、"))}</p><p>待定部分：${esc(out.uncertainties.join("；"))}</p><p>客观核验：${esc(JSON.stringify(t.checks.requests || []))}</p></details>` : t.status === "failed" || t.status === "blocked" ? `<div class="error">${esc(t.error)}<br>用户原文、首次输出及日志保留。本次没有生成替代回答。</div><details><summary>查看被阻断的原始回复（未作教学展示）</summary><pre class="code-block">${esc(JSON.stringify(out, null, 2) || "无可解析回复")}</pre></details><form class="retry-form" data-turn="${t.turn_id}"><label>人工重试原因</label><input name="reason" required maxlength="1000" placeholder="例如：网络已恢复，保留首次失败后重试"><button class="subtle" type="submit" ${experiment.status === "completed" ? "disabled" : ""}>记录原因并重试</button></form>` : `<div class="waiting">${t.connection_notice ? `<p class="notice">${esc(t.connection_notice)}</p>` : ""}<strong>${statusLabels[t.runtime_phase || t.status]}${experiment.mode === "S1" ? " · 真实模型可能需要数分钟" : ""}</strong><p class="small muted">已等待 <span data-wait-start="${t.attempts.at(-1)?.requested_at || t.submitted_at}">0</span> 秒。可以刷新页面或查看历史，已提交的回答不会丢失。</p></div>`}<details><summary>执行工件与历次尝试（${t.attempts.length}）</summary>${t.attempts.map((a) => `<p>尝试 ${a.number} · ${statusLabels[a.status]} · ${seconds(a.elapsed_seconds)}${a.retry_reason ? " · 重试原因：" + esc(a.retry_reason) : ""}<br>${esc(a.error || "")}</p><div class="artifact-links">${(a.artifact_names || []).map((n) => `<a target="_blank" rel="noopener" href="/api/artifacts/${a.attempt_id}/${encodeURIComponent(n)}">${esc(n)}</a>`).join("")}</div>`).join("")}</details></article>`;
}
function renderExperiment() {
  const e = experiment,
    last = e.turns.at(-1),
    running =
      last && ["queued", "connecting", "generating"].includes(last.status);
  $("#experiment-title").textContent = e.name;
  $("#experiment-subtitle").textContent =
    `${e.feature} / ${e.case_id} · ${e.mode === "S1" ? "真实 AI S1" : "固定规则 S0"} · ${sourceLabel(e)}`;
  $("#chat-state").innerHTML = badge(e.status);
  $("#status-area").innerHTML =
    `<dl class="status-list"><dt>实验 ID</dt><dd class="id">${e.experiment_id}</dd><dt>功能 / 案例</dt><dd>${e.feature} / ${e.case_id}</dd><dt>模式</dt><dd>${e.mode} ${e.mode === "S1" ? "· " + esc(e.model_config.model_requested) : "· 无模型"}</dd><dt>轮次</dt><dd>${e.turns.length} / ${e.feature === "F01" ? 1 : e.feature === "DEMO" ? 2 : 3} 次模型/规则后续输出</dd><dt>教学动作</dt><dd>${esc(last?.output ? e.action_labels[last.output.next_action] : "等待输出")}</dd><dt>代码版本</dt><dd class="mono">${esc(e.code_versions.find(v=>v.version_id===e.current_code_version_id)?.label)} · ${e.current_code_version_id.slice(0,8)}</dd><dt>版本状态</dt><dd>${e.code_versions.find((v) => v.version_id === e.current_code_version_id)?.verification_status === "unverified" ? "新版本未验证" : "审核源码有指定输入证据"}</dd><dt>当前核验</dt><dd>${last?.checks ? (last.checks.display_safe ? "结构 / 执行放行，语义待复核" : "守卫阻断") : "尚无输出"}</dd><dt>最近调用耗时</dt><dd>${seconds(last?.elapsed_seconds)}</dd></dl>${e.end_reason ? `<p class="notice">${esc(reasons[e.end_reason] || e.end_reason)}${e.end_reason === "budget_limited" ? "；仍可能有未回答的问题，不表示已理解。" : ""}</p>` : ""}`;
  $("#pause-experiment").disabled = e.status !== "active";
  $("#resume-experiment").hidden = e.status !== "paused";
  $("#end-experiment").disabled = e.status === "completed";
  $("#complete-experiment").disabled = e.status === "completed";
  $("#answer").disabled = running || e.status !== "active";
  $("#send-answer").disabled = running || e.status !== "active";
  $("#composer-note").textContent = running
    ? "回答已保存，正在等待本次调用"
    : e.status === "completed"
      ? "本次实验已结束，仍可评价和导出"
      : e.status === "paused"
        ? "实验已暂停；恢复后继续，原轮次上限保留"
        : e.status === "failed"
          ? "保留失败记录；在上方明确重试"
          : "Ctrl + Enter 提交 · 输入原文完整保存";
  renderCode();
  const fingerprint = JSON.stringify(
    e.turns.map((t) => [
      t.turn_id,
      t.status,
      t.runtime_phase,
      t.connection_notice,
      t.output,
      t.attempts.length,
    ]),
  );
  if (fingerprint !== chatFingerprint) {
    chatFingerprint = fingerprint;
    const scroll = $("#chat-scroll"),
      nearBottom =
        scroll.scrollHeight - scroll.scrollTop - scroll.clientHeight < 100;
    scroll.innerHTML =
      (["F01", "DEMO"].includes(e.feature)
        ? `<article class="message teacher"><div class="meta"><span class="teacher-label">案例首问</span><span>固定首问 · 非模型生成</span></div><div class="message-body">${esc(e.case_snapshot.teaching_question)}</div></article>`
        : "") + e.turns.map(message).join("");
    if (nearBottom || !scroll.scrollTop) scroll.scrollTop = scroll.scrollHeight;
    scroll.querySelectorAll(".evaluate-turn").forEach((b) =>
      b.addEventListener("click", () => {
        selectedTurn = b.dataset.turn;
        showFeedback();
        $("#feedback-area").scrollIntoView({
          block: "nearest",
          behavior: "instant",
        });
      }),
    );
    scroll.querySelectorAll(".retry-form").forEach((form) => {
      let busy = false;
      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (busy) return;
        busy = true;
        form.querySelector("button").disabled = true;
        try {
          await api("/api/turns/" + form.dataset.turn + "/retry", {
            reason: new FormData(form).get("reason"),
            request_id: crypto.randomUUID(),
          });
          toast("重试已排队，首次尝试已保留");
          await refreshExperiment();
        } catch (error) {
          toast(error.message, true);
          busy = false;
          form.querySelector("button").disabled = false;
        }
      });
    });
    if (!selectedTurn || !e.turns.find((t) => t.turn_id === selectedTurn))
      showFeedback();
    else if ($("#feedback-turn")) {
      $("#feedback-turn").innerHTML = e.turns
        .map((t) => option(t.turn_id, `第 ${t.number} 轮 · ${statusLabels[t.status]}`))
        .join("");
      $("#feedback-turn").value = selectedTurn;
    }
  }
  const notesKey = JSON.stringify(e.notes);
  if (notesKey !== noteFingerprint) {
    noteFingerprint = notesKey;
    $("#experiment-notes").innerHTML =
      e.notes
        .map(
          (n) =>
            `<p>${esc(n.text)}<br><span class="muted small">${date(n.created_at)}</span></p>`,
        )
        .join("") || '<p class="small muted">还没有备注。</p>';
  }
  renderDemo();
}
async function refreshExperiment() {
  experiment = await api("/api/experiments/" + experiment.experiment_id);
  renderExperiment();
}
async function lab(eid) {
  experiment = await api("/api/experiments/" + eid);
  app.innerHTML = `<div class="lab-heading"><div><h1 id="experiment-title"></h1><p id="experiment-subtitle" class="small muted"></p></div>${exports(eid)}</div><div class="lab-grid"><aside class="lab-side"><section><h3>题目与输入要求</h3><p id="question"></p><p id="contract" class="small muted"></p></section><section><h3>当前代码版本</h3><label class="small" for="code-version">查看版本</label><select id="code-version"></select><div class="code-head"><span id="code-verification"></span><button class="subtle" id="copy-current">复制</button></div><pre class="code-block"><code id="source-code"></code></pre><details class="small"><summary>原始程序</summary><button class="subtle" id="copy-original">复制原始代码</button><pre class="code-block"><code id="original-code"></code></pre></details><details><summary class="small">记录修改后的新代码</summary><form id="code-form"><p class="small muted">仅保存文本，未验证，不执行。</p><label for="new-code" class="small">新代码</label><textarea id="new-code" name="source" class="new-code" required maxlength="100000"></textarea><button class="subtle" type="submit">保存为未验证版本</button></form></details></section><section><h3>已验证的输入与输出</h3><div id="evidence"></div></section><section><h3>已知证据与未知信息</h3><p id="known-facts" class="small muted"></p></section></aside><section class="chat-panel"><div class="chat-top"><h2>教学对话</h2><span id="chat-state"></span></div><div class="chat-scroll" id="chat-scroll" aria-live="polite"></div><form id="answer-form" class="composer"><label class="small" for="answer">你的回答</label><textarea id="answer" name="answer" maxlength="30000" placeholder="自然地描述你的想法、疑问或运行观察…" required></textarea><div class="composer-bottom"><span id="composer-note"></span><button id="send-answer" type="submit" class="primary">发送回答 →</button></div></form></section><aside class="lab-side right-side"><section><h3>实验状态</h3><div id="status-area"></div><div class="controls"><button id="pause-experiment" data-control="pause">暂停</button><button id="resume-experiment" data-control="resume">恢复实验</button><button id="complete-experiment" data-control="complete">提前完成</button><button id="end-experiment" data-control="end">结束</button></div><p class="small muted">结束 / 暂停期间已提交的调用仍会保存结果。</p></section><section><h3>人工评价 <span class="small muted">均可跳过</span></h3><div id="feedback-area"></div></section><section><h3>实验备注</h3><div class="note-list" id="experiment-notes"></div><form id="note-form"><label for="experiment-note" class="small">补充备注</label><textarea name="text" id="experiment-note" maxlength="5000" required class="feedback-note"></textarea><button class="subtle" type="submit">追加备注</button></form></section></aside></div>`;
  renderExperiment();
  showFeedback();
  let submitting = false,
    pending = null;
  $("#answer-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (submitting) return;
    const answer = $("#answer").value;
    if (!answer.trim()) return;
    submitting = true;
    $("#send-answer").disabled = true;
    if (!pending || pending.answer !== answer)
      pending = {
        answer,
        request_id: crypto.randomUUID(),
        parent_turn_id: experiment.turns.at(-1)?.turn_id || null,
      };
    try {
      await api("/api/experiments/" + eid + "/turns", pending);
      $("#answer").value = "";
      sessionStorage.removeItem("aic-draft:" + eid + ":answer");
      pending = null;
      toast("回答已保存，后台开始处理");
      await refreshExperiment();
    } catch (error) {
      toast(error.message, true);
    } finally {
      submitting = false;
      renderExperiment();
    }
  });
  $("#answer").addEventListener("keydown", (event) => {
    if (event.ctrlKey && event.key === "Enter") {
      event.preventDefault();
      $("#answer-form").requestSubmit();
    }
  });
  document.querySelectorAll("[data-control]").forEach((button) =>
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await api("/api/experiments/" + eid + "/control", {
          action: button.dataset.control,
        });
        await refreshExperiment();
      } catch (error) {
        toast(error.message, true);
        button.disabled = false;
      }
    }),
  );
  $("#copy-original").addEventListener("click", () =>
    copy(experiment.case_snapshot.source),
  );
  $("#copy-current").addEventListener("click", () =>
    copy(
      experiment.code_versions.find(
        (v) => v.version_id === $("#code-version").value,
      ).source,
    ),
  );
  $("#code-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = event.target.querySelector("button");
    button.disabled = true;
    try {
      await api(
        "/api/experiments/" + eid + "/code",
        {...Object.fromEntries(new FormData(event.target)), parent_version_id: $("#code-version").value},
      );
      $("#new-code").value = "";
      sessionStorage.removeItem("aic-draft:" + eid + ":new-code");
      await refreshExperiment();
      toast("新代码文本已保存：新版本未验证");
    } catch (e) {
      toast(e.message, true);
    } finally {
      button.disabled = false;
    }
  });
  $("#note-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = event.target.querySelector("button");
    button.disabled = true;
    try {
      await api(
        "/api/experiments/" + eid + "/notes",
        Object.fromEntries(new FormData(event.target)),
      );
      $("#experiment-note").value = "";
      await refreshExperiment();
      toast("备注已追加");
    } catch (e) {
      toast(e.message, true);
    } finally {
      button.disabled = false;
    }
  });
  pollTimer = setInterval(async () => {
    try {
      await refreshExperiment();
    } catch (error) {
      $("#composer-note").textContent =
        "连接本地服务失败，已保存记录仍在数据库；请检查服务。";
    }
  }, 1500);
  setInterval(() => {
    document
      .querySelectorAll("[data-wait-start]")
      .forEach(
        (el) =>
          (el.textContent = Math.max(
            0,
            Math.floor((Date.now() - new Date(el.dataset.waitStart)) / 1000),
          )),
      );
  }, 1000);
}
async function copy(value) {
  try {
    await navigator.clipboard.writeText(value);
    toast("代码已复制");
  } catch {
    toast("浏览器复制失败，可在代码区手动选择复制", true);
  }
}
async function main() {
  try {
    uiVersion = (await api('/api/health')).ui_version;
    if (uiVersion === 'V2') {
      $('.brand').href='/manage';
      $('[data-nav="home"]').href='/manage';
      $('.topbar nav').insertAdjacentHTML('afterbegin','<a href="/">学生学习模式</a>');
      $('.brand small').textContent='管理';
    }
  } catch {}
  const path = location.pathname;
  const nav =
    path === "/history" ? "history" : path === "/stats" ? "stats" : "home";
  $(`[data-nav="${nav}"]`).classList.add("active");
  try {
    if (path === "/history") await history();
    else if (path === "/stats") await statistics();
    else if (path.startsWith("/experiments/")) await lab(path.split("/")[2]);
    else await home();
  } catch (error) {
    app.innerHTML = `<div class="page"><div class="error">${esc(error.message)}</div><a class="button" href="/">返回首页</a></div>`;
  }
}
main();
