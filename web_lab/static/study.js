import {
  $,
  esc,
  time,
  status,
  withOrigin,
  api,
  toast,
  loadDraft,
  draft,
  clearDraft,
  codeKeys,
  evidenceTable,
} from "./ui.js";
import { mountSandbox } from "./sandbox.js";
import { studyLayout } from "./study-layout.js";
import {
  currentJob,
  coachGate,
  versionName,
  runLabels,
  retryGate,
} from "./learning-state.js";
const running = new Set(["queued", "connecting", "generating"]);
const actions = {
  continue_asking: "继续追问",
  show_counterexample: "查看新反例",
  layered_hint: "分层提示",
  request_self_modification: "自行修改代码",
  clarify_meaning: "澄清意思",
  pause_for_choice: "暂停，由你选择",
};
export async function study(eid) {
  let e = await api("/api/experiments/" + eid);
  if (e.feature !== "DEMO") {
    location.replace("/experiments/" + eid);
    return;
  }
  localStorage.setItem("aic-v2:last-session", eid);
  let selected = e.current_code_version_id,
    submitting = false,
    saving = false,
    verifying = false,
    chatFingerprint = "",
    versionFingerprint = "",
    versionPanelFingerprint = "",
    stopFingerprint = "",
    failureFingerprint = "",
    pending = loadDraft(eid, "pending-answer");
  const saved = loadDraft(eid, "code");
  if (saved && e.code_versions.some((v) => v.version_id === saved.base))
    selected = saved.base;
  const endpoint = "/api/experiments/" + eid;
  const realAI =
    e.mode === "S1" &&
    ["real_official_Codex_CLI", "real_external_AI_API"].includes(
      e.model_provenance,
    );
  const aiLabel =
    e.model_provenance === "real_external_AI_API"
      ? "外部 AI API"
      : e.model_provenance === "AI_disabled"
        ? "AI 已禁用"
        : "Codex CLI";
  const version = () => e.code_versions.find((v) => v.version_id === selected);
  const dirty = () => $("#code-editor").value !== version().source;
  const record = (action) =>
    api(endpoint + "/ui-actions", withOrigin({ action })).catch((err) =>
      toast("操作已显示，但记录失败：" + err.message, true),
    );
  $("#main").innerHTML = studyLayout(e, eid, aiLabel);
  $("#code-editor").value =
    saved?.base === selected ? saved.text : version().source;
  $("#answer").value = loadDraft(eid, "answer")?.text || "";
  codeKeys($("#code-editor"));
  const sandboxUI = mountSandbox({
    eid,
    version,
    dirty,
    state: () => e,
    refresh,
    showTab,
    viewVersion: (next) => viewVersion(next, true),
    locateLine,
    onStateChange: renderChat,
  });
  if (e.mode === "S1")
    $(".advanced-fields span:nth-of-type(2)").textContent = aiLabel;
  function showTab(tab) {
    document.querySelectorAll("[data-tab]").forEach((b) => {
      const active = b.dataset.tab === tab;
      b.classList.toggle("active", active);
      b.setAttribute("aria-selected", active);
      b.tabIndex = active ? 0 : -1;
      $("#panel-" + b.dataset.tab).hidden = !active;
    });
  }
  function showPane(pane) {
    $(".workspace").dataset.mobilePane = pane;
    ["code", "coach"].forEach((k) => {
      const b = $("#mobile-" + k);
      b.classList.toggle("active", k === pane);
      b.setAttribute("aria-pressed", k === pane);
    });
  }
  function viewVersion(next, savedSource = false) {
    if (next === selected && (!savedSource || !dirty())) return true;
    if (!e.code_versions.some((v) => v.version_id === next)) return false;
    if (
      dirty() &&
      !confirm("当前有未保存编辑。查看已保存版本会替换编辑内容，是否继续？")
    )
      return false;
    selected = next;
    $("#code-editor").value = version().source;
    clearDraft(eid, "code");
    renderCode();
    renderChat();
    showPane("code");
    return true;
  }
  function locateLine(line) {
    const el = $("#code-editor"),
      start =
        el.value
          .split("\n")
          .slice(0, line - 1)
          .join("\n").length + (line > 1 ? 1 : 0);
    showPane("code");
    el.focus();
    el.setSelectionRange(
      start,
      el.value.indexOf("\n", start) < 0
        ? el.value.length
        : el.value.indexOf("\n", start),
    );
    el.scrollTop = Math.max(0, (line - 3) * 26);
  }
  const name = (v) => versionName(e.code_versions, v);
  function rows() {
    const v = version(),
      op = [...e.demo.operations]
        .reverse()
        .find(
          (o) =>
            o.version_id === selected &&
            o.payload.source_hash === v.source_sha256 &&
            o.payload.result?.tests?.length,
        );
    if (op)
      return {
        rows: op.payload.result.tests.map((t) => ({
          args: t.args,
          before: t.before.actual_output,
          actual: t.after.actual_output,
          expected: t.after.reference_output,
          success: t.after.execution_success,
        })),
        comparison: true,
        label: "本会话实际执行 · " + time(op.completed_at),
      };
    const sourceVersion = v.label === "original" ? "original" : v.label;
    const frozen = e.case_snapshot.evidence.filter(
      (r) =>
        r.source_version === sourceVersion &&
        (v.label === "original"
          ? e.case_snapshot.source_sha256
          : e.case_snapshot.versions[v.label]?.source_sha256) ===
          v.source_sha256,
    );
    return {
      rows: frozen.map((r) => ({
        args: r.args,
        actual: r.actual,
        expected: r.expected,
      })),
      comparison: false,
      label: frozen.length ? "已审核案例的历史运行证据" : "尚未执行",
    };
  }
  function renderCode() {
    const v = version(),
      ready = e.demo.version_readiness.find((r) => r.version_id === selected),
      changed = dirty();
    const versions = JSON.stringify([
      e.code_versions.map((v) => v.version_id),
      e.current_code_version_id,
    ]);
    if (versions !== versionFingerprint) {
      versionFingerprint = versions;
      $("#version-select").innerHTML = e.code_versions
        .map(
          (v) =>
            `<option value="${v.version_id}">${esc(name(v))}${v.version_id === e.current_code_version_id ? " · 当前保存版本" : ""}</option>`,
        )
        .join("");
    }
    $("#version-select").value = selected;
    $("#save-code").disabled = !changed || saving;
    $("#verify-code").disabled = changed || verifying || !ready?.can_verify;
    $("#save-state").textContent = saving
      ? "正在保存…"
      : changed
        ? "未保存 · 本机草稿已保留"
        : `${name(v)} · 已保存`;
    $("#save-code").classList.toggle("primary", changed);
    $("#historical-version").hidden = selected === e.current_code_version_id;
    $("#line-numbers").textContent = $("#code-editor")
      .value.split("\n")
      .map((_, i) => i + 1)
      .join("\n");
    $("#legacy-readiness").textContent = changed
      ? "先保存编辑再核验。"
      : !ready?.source_registered
        ? "自由保存版本可使用 Docker；旧审核核验不支持此版本。"
        : ready.can_verify
          ? "此案例版本可核验指定输入。"
          : "对比来源版本尚未审核。";
    const job = currentJob(e.sandbox?.jobs || [], v),
      flow = changed
        ? "edit"
        : !job || ["queued", "running"].includes(job.status)
          ? "run"
          : "coach";
    ["edit", "run", "coach"].forEach((k) => {
      $("#flow-" + k).classList.toggle("active", k === flow);
      $("#flow-" + k).setAttribute(
        "aria-current",
        k === flow ? "step" : "false",
      );
    });
    const facts = rows(),
      html =
        evidenceTable(facts.rows, facts.comparison) +
        `<p class="evidence-footnote">${esc(facts.label)} · 仅对应上方选中版本。有限测试不证明整体正确或知识掌握。</p>`;

    $("#full-evidence").innerHTML =
      (changed
        ? `<p class="notice">下列证据对应已保存的「${esc(name(v))}」，不适用于编辑草稿。</p>`
        : "") + html;
    const panelMark = JSON.stringify([
      selected,
      e.current_code_version_id,
      e.code_versions.map((v) => v.version_id),
      (e.sandbox?.jobs || []).map((j) => [j.task_id, j.status]),
    ]);
    if (panelMark !== versionPanelFingerprint) {
      versionPanelFingerprint = panelMark;
      const event = [...e.events]
        .reverse()
        .find(
          (r) =>
            r.type === "unverified_code_recorded" &&
            r.payload.version_id === selected,
        );
      $("#diff-view").innerHTML = event
        ? `<p class="small muted">与保存修改时的来源版本比较。</p><pre class="diff">${esc(event.payload.modification.unified_diff || "未改变源码文本")}</pre>`
        : '<p class="muted">这是预先登记的代码版本，没有本会话的修改差异。</p>';
      $("#version-list").innerHTML = [...e.code_versions]
        .reverse()
        .map(
          (v) =>
            `<button class="version-item ${v.version_id === selected ? "selected" : ""}" data-version="${v.version_id}"><span><strong>${esc(name(v))}${v.version_id === e.current_code_version_id ? " · 当前保存版本" : ""}</strong><small>${esc(time(v.created_at))} · ${(e.sandbox?.jobs || []).filter((j) => j.version_id === v.version_id).length} 次运行</small></span><span aria-hidden="true">→</span></button>`,
        )
        .join("");
      document.querySelectorAll("[data-version]").forEach(
        (b) =>
          (b.onclick = () => {
            viewVersion(b.dataset.version);
          }),
      );
    }
    sandboxUI.render();
  }
  function message(text, role, label, date, extra = "") {
    return `<article class="message ${role}"><div class="message-meta">${esc(label)}${date ? " · " + esc(time(date)) : ""}</div><div class="bubble">${esc(text)}</div>${extra}</article>`;
  }
  function renderChat() {
    const mark = JSON.stringify([
      e.turns.map((t) => [t.status, t.output, t.error, t.answer_raw]),
      e.status,
      e.current_code_version_id,
    ]);
    if (mark !== chatFingerprint) {
      chatFingerprint = mark;
      const box = $("#messages"),
        bottom = box.scrollHeight - box.scrollTop - box.clientHeight < 90;
      let html = message(
        e.case_snapshot.demo_initial_output.student_message,
        "teacher",
        "题目引导 · 固定首次问题",
        e.created_at,
      );
      for (const t of e.turns) {
        if (t.answer_raw)
          html += message(
            t.answer_raw,
            "student",
            "你的回答",
            t.submitted_at,
            `<span class="small muted">回答时使用已保存版本 ${esc(name(e.code_versions.find((v) => v.version_id === t.code_version_id)))}</span>`,
          );
        if (t.status === "succeeded") {
          const o = t.output;
          const ctx = t.public_input?.execution_context,
            stale = t.code_version_id !== e.current_code_version_id;
          const evidence = ctx
            ? `<p class="evidence-footnote ${stale ? "stale-evidence" : ""}">依据 ${esc(name(e.code_versions.find((v) => v.version_id === ctx.version_id)))} · ${ctx.task_id ? "已保存的运行记录" : "当时没有此版本的 Docker 运行结果"}${stale ? " · 已是历史版本，请重新运行当前代码" : ""}。教学解释仍需你判断。</p>`
            : "";
          const extra =
            evidence +
            `<span class="action-tag">下一步：${esc(e.action_labels[o.next_action] || actions[o.next_action] || "查看建议")}</span><details><summary>为什么这样建议</summary><p>${esc(o.decision_basis)}</p>${o.uncertainties?.length ? `<p>还不能确认：${esc(o.uncertainties.join("；"))}</p>` : ""}</details>`;
          html += message(
            o.student_message,
            "teacher",
            realAI
              ? "AI · 真实模型回复"
              : e.mode === "S0"
                ? "固定规则回复"
                : "测试工件 · 不是正式模型回复",
            t.completed_at,
            extra,
          );
        }
      }
      $("#conversation").innerHTML = html;
      if (bottom || !e.turns.length) box.scrollTop = box.scrollHeight;
    }
    const last = e.turns.at(-1),
      waiting = last && running.has(last.status),
      limit = e.turns.length >= 2;
    $("#session-status").textContent = status[e.status] || e.status;
    $("#round-count").textContent =
      `后续回复 ${e.turns.filter((t) => t.status === "succeeded").length} / 最多 2 次`;
    const gate = coachGate({
      dirty: dirty(),
      historical: selected !== e.current_code_version_id,
      busy: sandboxUI.busy(),
    });
    const disabled =
      submitting ||
      waiting ||
      e.status !== "active" ||
      limit ||
      (last && last.status !== "succeeded");
    $("#send-answer").disabled = !!disabled || !!gate;
    $("#answer").disabled = !!disabled;
    document
      .querySelectorAll("[data-reply]")
      .forEach((b) => (b.disabled = !!disabled));
    $("#end-question").disabled = e.status === "completed";
    const reasonText = {
      understanding_sufficient:
        "可以停止追问，先自己修改代码。保存后再查看可核验范围。",
      budget_limited:
        "本题已达到原型的三次教学输出上限，可继续编辑和保存代码。",
      manual_end: "你已结束本题。对话、代码和证据都已保留。",
      await_new_evidence: "需要新版本或更清楚的证据，当前先暂停追问。",
      user_choice: "当前判断暂停，由你选择下一步。",
      manual_pause: "本题已暂停。",
    };
    const stopped = e.status === "completed" || e.status === "paused";
    $("#stop-area").hidden = !stopped;
    $("#answer-form").hidden = stopped;
    const stopMark = JSON.stringify([e.status, e.end_reason, limit]);
    if (stopped && stopMark !== stopFingerprint) {
      stopFingerprint = stopMark;
      $("#stop-area").innerHTML =
        `<strong>${e.status === "completed" ? "本次追问已结束" : "追问已暂停"}</strong><div>${esc(reasonText[e.end_reason] || "可继续保存修改；结束不代表已经掌握知识。")}</div><div class="stop-actions"><button id="stop-edit">自行修改代码</button>${e.status === "paused" && !limit ? '<button id="resume-study">准备好后继续</button>' : ""}<a class="button" id="new-assessment" href="/study/${eid}/assessment">尝试新题验收</a><a class="button" href="/">继续学习 →</a></div>`;
      $("#stop-edit").onclick = () => {
        showTab("code");
        showPane("code");
        $("#code-editor").focus();
        record("edit_code");
      };
      $("#new-assessment").onclick = () => record("open_assessment");
      if ($("#resume-study"))
        $("#resume-study").onclick = async () => {
          try {
            await api(endpoint + "/control", withOrigin({ action: "resume" }));
            await refresh();
          } catch (err) {
            toast(err.message, true);
          }
        };
    }
    $("#composer-note").textContent = waiting
      ? "回答已保存。此时保存新版会阻断本轮建议。"
      : disabled
        ? "本轮暂不能发送，仍可修改、保存和运行。"
        : gate || "Ctrl+Enter 发送 · 快捷提示可编辑后再发送";
    const latest = currentJob(
      e.sandbox?.jobs || [],
      e.code_versions.find((v) => v.version_id === e.current_code_version_id),
    );
    $("#coach-context").textContent =
      e.mode === "S0"
        ? "离线固定规则，使用既有案例提示，不会分析任意新代码。"
        : `${name(e.code_versions.find((v) => v.version_id === e.current_code_version_id))} · ${latest ? runLabels[latest.status] : "尚无本版本运行结果"}`;
    const state = $("#call-status");
    if (waiting) {
      const start = last.attempts.at(-1)?.requested_at || last.submitted_at,
        elapsed = Math.max(
          0,
          Math.floor((Date.now() - Date.parse(start)) / 1000),
        );
      const phase =
        e.mode === "S0"
          ? "固定规则处理中"
          : {
              queued: "后台排队中",
              connecting: "正在连接 " + aiLabel,
              generating: "模型正在生成回复",
            }[last.runtime_phase || last.status];
      state.innerHTML = `<div class="notice call-status"><strong><span class="state-dot"></span>${phase} · 已等待 ${elapsed} 秒</strong>${realAI ? "你的回答已保存，可能需要约两分钟或更久。" : e.mode === "S0" ? "使用固定规则，不调用模型。" : "这是测试调用链路，不是真实模型推理。"}可以编辑代码，刷新后会恢复状态。${last.connection_notice ? `<p>${esc(last.connection_notice)}</p>` : ""}</div>`;
    } else if (last && ["failed", "blocked"].includes(last.status)) {
      const retryReason = () =>
        retryGate({
          dirty: dirty(),
          historical: selected !== e.current_code_version_id,
          busy: sandboxUI.busy(),
          turnVersion: last.code_version_id,
          currentVersion: e.current_code_version_id,
        });
      if ($("#retry-model"))
        $("#retry-model").disabled =
          e.status === "completed" || !!retryReason();
      if ($("#retry-note"))
        $("#retry-note").textContent =
          retryReason() || "重试沿用这次调用的原回答与运行快照。";
      const failureMark = JSON.stringify([
        last.turn_id,
        last.error,
        last.status,
        e.status,
      ]);
      if (failureMark === failureFingerprint) return;
      failureFingerprint = failureMark;
      state.innerHTML = `<div class="notice error call-status"><strong>${last.status === "blocked" ? "回复未通过核验，未作为教学建议展示" : "这次回复没有成功"}</strong><p>${esc(last.error || "未取得可用回复。")}</p><p class="small">回答及原始结果已保留，不会自动重新生成。</p><p class="small" id="retry-note"></p><button id="retry-model">重试原回答与快照</button> <a href="/experiments/${eid}">查看失败记录</a> · <a href="/">开始新练习</a></div>`;
      $("#retry-model").disabled = e.status === "completed" || !!retryReason();
      $("#retry-note").textContent =
        retryReason() || "重试沿用这次调用的原回答与运行快照。";
      $("#retry-model").onclick = async () => {
        if (e.status === "completed" || retryReason()) return;
        const reason = prompt("请说明重试原因。会新增一次调用，原失败保留。");
        if (!reason?.trim()) return;
        $("#retry-model").disabled = true;
        try {
          await api("/api/turns/" + last.turn_id + "/retry", {
            reason,
            request_id: crypto.randomUUID(),
          });
          await refresh();
        } catch (err) {
          toast(err.message, true);
        }
      };
    } else {
      state.innerHTML = "";
      failureFingerprint = "";
    }
  }
  async function refresh() {
    const data = await api(endpoint);
    e = data;
    if (pending && e.turns.some((t) => t.request_id === pending.request_id)) {
      if ($("#answer").value === pending.answer) {
        $("#answer").value = "";
        clearDraft(eid, "answer");
      }
      pending = null;
      clearDraft(eid, "pending-answer");
    }
    renderCode();
    renderChat();
  }
  $("#code-editor").oninput = () => {
    if (dirty())
      draft(eid, "code", { base: selected, text: $("#code-editor").value });
    else clearDraft(eid, "code");
    renderCode();
    renderChat();
  };
  $("#code-editor").onscroll = () =>
    ($("#line-numbers").scrollTop = $("#code-editor").scrollTop);
  $("#code-editor").addEventListener("keydown", (ev) => {
    if ((ev.ctrlKey || ev.metaKey) && ["s", "Enter"].includes(ev.key)) {
      ev.preventDefault();
      if (ev.key === "s") $("#save-code").click();
      else if (!$("#run-code").disabled) $("#run-code").click();
    }
  });
  $("#answer").oninput = () =>
    draft(eid, "answer", { text: $("#answer").value });
  $("#answer").onkeydown = (ev) => {
    if (ev.key === "Enter" && (ev.ctrlKey || ev.metaKey)) {
      ev.preventDefault();
      if (!$("#send-answer").disabled) $("#answer-form").requestSubmit();
    }
  };
  $("#version-select").onchange = (ev) => {
    if (!viewVersion(ev.target.value)) ev.target.value = selected;
  };
  document.querySelectorAll("[data-tab]").forEach((b, i) => {
    b.onclick = () => {
      showTab(b.dataset.tab);
      if (b.dataset.tab !== "code")
        record(b.dataset.tab === "changes" ? "view_diff" : "view_evidence");
    };
    b.onkeydown = (ev) => {
      if (["ArrowLeft", "ArrowRight"].includes(ev.key)) {
        ev.preventDefault();
        const tabs = [...document.querySelectorAll("[data-tab]")],
          next =
            tabs[
              (i + (ev.key === "ArrowRight" ? 1 : tabs.length - 1)) %
                tabs.length
            ];
        next.focus();
        next.click();
      }
    };
  });
  $("#save-code").onclick = async () => {
    if (saving || !dirty()) return;
    const source = $("#code-editor").value;
    if (!source.trim()) return toast("请输入完整代码。", true);
    saving = true;
    renderCode();
    try {
      const v = await api(
        endpoint + "/code",
        withOrigin({ source, parent_version_id: selected }),
      );
      e = await api(endpoint);
      selected = v.version_id;
      if ($("#code-editor").value === source) clearDraft(eid, "code");
      else
        draft(eid, "code", { base: selected, text: $("#code-editor").value });
      await refresh();
      toast("新版本已保存。现在可以运行它。");
    } catch (err) {
      toast(err.message, true);
    } finally {
      saving = false;
      renderCode();
      renderChat();
    }
  };
  $("#verify-code").onclick = async () => {
    if (verifying || dirty()) return;
    verifying = true;
    renderCode();
    try {
      const r = await api(
        "/api/demo/" + eid + "/verify",
        withOrigin({ version_id: selected }),
      );
      await refresh();
      toast(
        r.executed
          ? "已保存实际核验结果，仅适用于指定输入。"
          : "没有执行代码，请查看审核状态。",
      );
    } catch (err) {
      toast(err.message, true);
    } finally {
      verifying = false;
      renderCode();
    }
  };
  $("#edit-shortcut").onclick = () => {
    showPane("code");
    $("#code-editor").focus();
    record("edit_code");
  };
  $("#evidence-shortcut").onclick = () => {
    showTab("evidence");
    showPane("code");
    $("#review-list").scrollIntoView({ block: "nearest" });
    record("view_evidence");
  };
  document.querySelectorAll("[data-reply]").forEach(
    (b) =>
      (b.onclick = () => {
        $("#answer").value = b.dataset.reply;
        draft(eid, "answer", { text: $("#answer").value });
        $("#answer").focus();
      }),
  );
  $("#back-current").onclick = () => viewVersion(e.current_code_version_id);
  $("#restore-version").onclick = () => {
    const source = $("#code-editor").value;
    if (!viewVersion(e.current_code_version_id)) return;
    $("#code-editor").value = source;
    $("#code-editor").dispatchEvent(new Event("input"));
    toast("历史代码已放入编辑区。保存后会建立新版本。");
  };
  $("#mobile-code").onclick = () => showPane("code");
  $("#mobile-coach").onclick = () => showPane("coach");
  $("#assessment-link").onclick = () => record("open_assessment");
  $("#end-question").onclick = async () => {
    try {
      await api(endpoint + "/control", withOrigin({ action: "end" }));
      await refresh();
      toast("本题已结束；正在进行的调用仍会保留结果。");
    } catch (err) {
      toast(err.message, true);
    }
  };
  $("#answer-form").onsubmit = async (ev) => {
    ev.preventDefault();
    if (submitting || $("#send-answer").disabled) return;
    const answer = $("#answer").value;
    if (!answer.trim()) return;
    if (!pending || pending.answer !== answer)
      pending = withOrigin({
        answer,
        request_id: crypto.randomUUID(),
        parent_turn_id: e.turns.at(-1)?.turn_id || null,
      });
    draft(eid, "pending-answer", pending);
    submitting = true;
    renderChat();
    try {
      await api(endpoint + "/turns", pending);
      await refresh();
      toast("回答已保存，正在后台处理。");
    } catch (err) {
      toast(err.message, true);
      try {
        await refresh();
      } catch {}
    } finally {
      submitting = false;
      renderChat();
    }
  };
  $("#feedback-form").onsubmit = async (ev) => {
    ev.preventDefault();
    const t = e.turns.filter((t) => t.status === "succeeded").at(-1),
      text = $("#feedback-notes").value;
    try {
      if (t)
        await api(
          "/api/turns/" + t.turn_id + "/feedback",
          withOrigin({
            evaluation_source: "user_subjective",
            on_topic: $("#feedback-topic").value,
            notes: text,
          }),
        );
      else
        await api(
          endpoint + "/notes",
          withOrigin({
            text: `首次引导反馈：切题=${$("#feedback-topic").value}；${text}`,
          }),
        );
      toast("反馈已保存。");
      $("#feedback-notes").value = "";
      await refresh();
    } catch (err) {
      toast(err.message, true);
    }
  };
  if (e.mode === "S1" && !realAI) {
    $(".chat-heading h2").textContent =
      e.model_provenance === "AI_disabled"
        ? "AI 当前已关闭"
        : "调用链路测试 · 无真实模型";
    $(".advanced-fields").insertAdjacentHTML(
      "beforeend",
      '<span class="warning">此记录使用测试运行器，不是正式 AI 推理。</span>',
    );
  }
  showPane("code");
  showTab(
    new URLSearchParams(location.search).get("view") === "review"
      ? "evidence"
      : "code",
  );
  renderCode();
  renderChat();
  $("#messages").scrollTop = $("#messages").scrollHeight;
  let polling = false;
  const interval = setInterval(async () => {
    if (polling || document.hidden) return;
    polling = true;
    try {
      await refresh();
    } catch (err) {
      failureFingerprint = '';
      $("#call-status").innerHTML =
        `<p class="notice error">无法刷新状态：${esc(err.message)}。已提交记录不会因页面断开而删除。</p>`;
    } finally {
      polling = false;
    }
  }, 2000);
  window.addEventListener("pagehide", () => clearInterval(interval), {
    once: true,
  });
}
