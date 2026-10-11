/* Small panels for the existing web lab; no second teaching UI. */
let demoFingerprint = "";
function renderDemo() {
  if (experiment.feature !== "DEMO") return;
  if (!$("#demo-verification")) {
    $(".lab-heading .export-links").insertAdjacentHTML("afterbegin", '<a class="button subtle" href="#demo-verification">修改核验</a><a class="button subtle" href="#assessment-state">新题验收</a>');
    $(".lab-side").insertAdjacentHTML("beforeend", `<section><h3>F04 / F03 · 修改与核验</h3><p class="small muted">保存不执行。核验只接受与登记源码完全相同的哈希，使用输入 0、1、3。</p><button class="subtle" id="verify-version">核验当前查看版本</button><div id="demo-verification"></div></section>`);
    $(".right-side").insertAdjacentHTML("beforeend", `<section><h3>F05 · 新题首次提交</h3><p class="small muted">资格与测试成绩分别记录。首次提交永久保留；未审核代码只保存待审。</p><form id="assessment-begin"><label for="external-help">新题的外部帮助声明</label><select id="external-help"><option value="unknown">不确定 / 未知</option><option value="none">声明没有外部帮助</option><option value="used">声明使用过帮助</option></select><p class="small">仅在你能确认时勾选：</p><label><input type="checkbox" id="coverage-history"> 本次帮助历史已完整记录</label><br><label><input type="checkbox" id="coverage-exposure"> 已检查新题提前暴露情况</label><br><label><input type="checkbox" id="coverage-source"> 提交来源记录完整</label><br><button class="subtle" type="submit">建立新题验收记录</button></form><div id="assessment-state"></div><div id="assessment-input" hidden><form id="assessment-submit"><label for="assessment-source">你的新题代码（完整 solve 函数）</label><textarea class="new-code" id="assessment-source" required maxlength="100000"></textarea><button class="subtle" type="submit" id="freeze-first">冻结首次提交</button><button class="subtle" type="button" id="save-assessment-revision">记录后续修改</button></form><details><summary>补记提示、答案暴露或帮助</summary><form id="help-form"><label for="help-kind">帮助类型</label><select id="help-kind"><option value="hint">提示</option><option value="full_answer">完整答案</option><option value="ai_help">AI 帮助</option><option value="external_help">外部帮助</option><option value="question_seen">提前见过题目</option></select><label for="help-target">关联对象</label><select id="help-target"><option value="assessment">新题</option><option value="unknown">关联未知</option><option value="original">原题</option></select><label><input type="checkbox" id="help-before"> 发生在首次提交之前（补记）</label><label for="help-content">原文或来源说明</label><textarea id="help-content" required maxlength="30000"></textarea><button class="subtle" type="submit">追加帮助记录</button></form></details></div></section><section><h3>统一会话事件</h3><p class="small muted">完整 JSON 导出包含模型原始字节、版本、F03 证据和 F05 密封记录。</p><details><summary>查看事件与版本关联</summary><pre class="code-block" id="demo-events"></pre></details></section>`);
    const path = "/api/demo/" + experiment.session_id;
    const submit = async (button, url, data, message) => {
      button.disabled = true;
      try { await api(url, data); await refreshExperiment(); toast(message); }
      catch (e) { toast(e.message, true); }
      finally { button.disabled = false; renderDemo(); }
    };
    $("#verify-version").onclick = () => submit($("#verify-version"), path + "/verify",
      {version_id: $("#code-version").value}, "核验记录已保存；请查看实际范围和状态");
    $("#assessment-begin").onsubmit = (event) => {
      event.preventDefault();
      submit(event.target.querySelector("button"), path + "/assessment", {
        external_help: $("#external-help").value, history_complete: $("#coverage-history").checked,
        prior_exposure_checked: $("#coverage-exposure").checked, source_record_complete: $("#coverage-source").checked,
      }, "新题记录已建立，原题帮助已关联");
    };
    $("#assessment-submit").onsubmit = (event) => {
      event.preventDefault();
      if (experiment.demo.first_submission_locked) return;
      submit($("#freeze-first"), path + "/first", {source: $("#assessment-source").value}, "首次提交已冻结，之后不能覆盖");
    };
    $("#save-assessment-revision").onclick = () => {
      if (!$("#assessment-source").value.trim()) return toast("请输入完整代码", true);
      submit($("#save-assessment-revision"), path + "/assessment-code", {source: $("#assessment-source").value}, "后续修改单独保存，首次成绩保持原样");
    };
    $("#help-form").onsubmit = (event) => {
      event.preventDefault();
      submit(event.target.querySelector("button"), path + "/help", {kind: $("#help-kind").value,
        target: $("#help-target").value, content: $("#help-content").value,
        applies_before_first: $("#help-before").checked ? true : null}, "帮助记录已追加；资格将重新核对");
    };
    // Drafts are local convenience only; submitted records live in SQLite/F05 seals.
    ["answer", "new-code", "assessment-source"].forEach((id) => {
      const key = "aic-draft:" + experiment.session_id + ":" + id;
      const el = $("#" + id);
      el.value = sessionStorage.getItem(key) || "";
      el.addEventListener("input", () => sessionStorage.setItem(key, el.value));
    });
  }
  const d = experiment.demo;
  $("#freeze-first").disabled = d.first_submission_locked;
  $("#save-assessment-revision").disabled = !d.first_submission_locked || !!d.assessment_error;
  $("#assessment-begin").hidden = !!d.assessment || !!d.assessment_error;
  $("#assessment-input").hidden = !d.assessment;
  const fingerprint = JSON.stringify([d, experiment.events]);
  if (fingerprint === demoFingerprint) return;
  demoFingerprint = fingerprint;
  $("#demo-verification").innerHTML = d.operations.map((op) => {
    const r = op.payload.result;
    return `<details open><summary>${esc(op.status)} · ${op.version_id.slice(0,8)}</summary><p class="small">会话 ${esc(op.session_id)}<br>旧版 ${esc(op.parent_version_id)} → 新版 ${esc(op.version_id)}<br>源码哈希 ${esc(op.payload.source_hash)}</p>${op.error ? `<p class="notice">${esc(op.error)}</p>` : ""}${r ? `<pre class="code-block">${esc(r.modification.unified_diff || "无源码差异")}</pre><table><thead><tr><th>输入</th><th>旧 / 新 / 参考</th><th>判定</th></tr></thead><tbody>${r.tests.map(t=>`<tr><td>${esc(JSON.stringify(t.args))}</td><td>${esc(t.before.actual_output)} / ${esc(t.after.actual_output)} / ${esc(t.after.reference_output)}</td><td>${esc(t.classification)}</td></tr>`).join("")}</tbody></table><p class="small">${esc(r.feedback.student_message)}</p>` : ""}<p class="small muted">仅确认这些输入和源码版本，不确认整体正确或学生掌握。</p></details>`;
  }).join("") || '<p class="small muted">尚无本会话的新执行记录。保存代码后可核验选中的版本。</p>';
  if (d.assessment_error) $("#assessment-state").innerHTML = `<p class="error">验收记录不完整或完整性检查失败：${esc(d.assessment_error)}。${d.first_submission_locked ? "首次槽位仍锁定，不会覆盖。" : "记录不能重置，请保留失败并检查。"}</p>`;
  else if (d.assessment) {
    const a = d.assessment, q = a.session.question;
    const eligibility = {eligible_by_records: "按当前记录符合独立验收条件", assisted_or_exposed: "受辅助或暴露影响", unknown: "资格未知"};
    $("#assessment-state").innerHTML = `<p><strong>${esc(q.question_id)} / ${esc(q.question_version)}</strong><br>${esc(q.statement)}<br><span class="small muted">${esc(q.input_contract)}</span></p><p>${eligibility[a.current_eligibility.status]}<br><span class="small muted">${esc(a.current_eligibility.reasons.join("；"))}</span></p><p class="small">原题帮助 ${a.help_records.filter(r=>r.payload.target === "original").length} 条；全部帮助 ${a.help_records.length} 条</p>${a.first ? `<p>首次提交已冻结 · ${esc(a.first.execution_state)}<br>指定输入通过 ${a.first.score.passed} / ${a.first.score.tested}<br><span class="mono small">${esc(a.first.source_hash)}</span></p><details><summary>不可覆盖的首次源码与核验</summary><pre class="code-block">${esc(a.first.source_text)}</pre><pre class="code-block">${esc(JSON.stringify(a.first.tests,null,2))}</pre></details><p class="small">后续修改 ${a.revisions.length} 次，均不替换首次成绩。</p>${a.revisions.map(r=>`<details><summary>后续修改 ${esc(r.revision_id)} · ${esc(r.comparison.status)}</summary><p class="small">新版哈希 ${esc(r.source_hash)}<br>父版哈希 ${esc(r.parent_source_hash)}<br>指定输入通过 ${r.comparison.summary.after_passed ?? "未核验"} / ${r.comparison.summary.test_count ?? 0}</p><pre class="code-block">${esc(r.comparison.modification.unified_diff || "无可核验差异")}</pre></details>`).join("")}` : '<p class="small">尚未提交。首次保存即冻结，包括未审核源码。</p>'}<p class="small muted">记录资格不是无外部帮助的客观证明；测试通过不代表知识掌握。</p>`;
  } else $("#assessment-state").innerHTML = '<p class="small muted">新题尚未展示。建立记录后显示题目。</p>';
  $("#demo-events").textContent = JSON.stringify(experiment.events, null, 2);
}
