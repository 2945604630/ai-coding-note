import { $,esc,time,status,withOrigin,api,toast,loadDraft,draft,clearDraft,codeKeys,evidenceTable,sourceTag } from './ui.js';
import { mountSandbox } from './sandbox.js';
const running=new Set(['queued','connecting','generating']);
const actions={continue_asking:'继续追问',show_counterexample:'查看新反例',layered_hint:'分层提示',request_self_modification:'自行修改代码',clarify_meaning:'澄清意思',pause_for_choice:'暂停，由你选择'};
export async function study(eid){
  let e=await api('/api/experiments/'+eid);
  if(e.feature!=='DEMO'){location.replace('/experiments/'+eid);return;}
  localStorage.setItem('aic-v2:last-session',eid);
  let selected=e.current_code_version_id,submitting=false,saving=false,verifying=false,chatFingerprint='',versionFingerprint='',stopFingerprint='',failureFingerprint='',pending=loadDraft(eid,'pending-answer');
  const saved=loadDraft(eid,'code');
  if(saved && e.code_versions.some(v=>v.version_id===saved.base))selected=saved.base;
  const endpoint='/api/experiments/'+eid;
  const realAI=e.mode==='S1' && ['real_official_Codex_CLI','real_external_AI_API'].includes(e.model_provenance);
  const aiLabel=e.model_provenance==='real_external_AI_API'?'外部 AI API':e.model_provenance==='AI_disabled'?'AI 已禁用':'Codex CLI';
  const version=()=>e.code_versions.find(v=>v.version_id===selected);
  const dirty=()=>$('#code-editor').value!==version().source;
  const record=action=>api(endpoint+'/ui-actions',withOrigin({action})).catch(err=>toast('操作已显示，但记录失败：'+err.message,true));
  $('#main').innerHTML=`<div class="study-shell"><div class="study-heading"><div><a class="back" href="/">← 学习首页</a><h1>${esc(e.case_id==='C01'?'整数求和':'求和与返回结果')}</h1></div><div class="heading-actions"><span id="session-status"></span><details class="advanced"><summary>学习设置与记录</summary><div class="advanced-fields"><strong>${esc(e.name)}</strong><span>${esc(sourceTag(e))}</span><span>${e.mode==='S1'?'真实 AI · '+esc(aiLabel):'固定问题 · 不调用 AI'}</span><span class="small">${esc(e.model_config.model_requested||'固定规则')} ${esc(e.model_config.reasoning_effort||'')}<br>首次引导 + 最多两次后续回复；充分理解时提前停止。</span><a href="/experiments/${eid}">查看完整实验记录 ↗</a></div></details><button id="end-question">结束本题</button></div></div><div class="workspace"><section class="code-pane" aria-label="题目与代码工作区"><div class="problem"><h2>题目</h2><p>${esc(e.case_snapshot.statement)}</p><p class="contract"><strong>输入：</strong>${esc(e.case_snapshot.input_contract)}<br><strong>输出：</strong>solve 函数返回计算结果。</p></div><div class="workspace-tabs" role="tablist" aria-label="代码工作区视图"><button role="tab" id="tab-code" aria-controls="panel-code" class="active" aria-selected="true" data-tab="code">代码</button><button role="tab" id="tab-evidence" aria-controls="panel-evidence" aria-selected="false" data-tab="evidence">运行证据</button><button role="tab" id="tab-changes" aria-controls="panel-changes" aria-selected="false" data-tab="changes">修改记录</button></div><div class="code-toolbar"><label for="version-select">查看版本</label><select id="version-select"></select></div><div id="panel-code" role="tabpanel" aria-labelledby="tab-code"><label class="small" for="code-editor">Python 代码 · 可以直接编辑</label><textarea id="code-editor" class="code-editor" spellcheck="false" autocapitalize="off" maxlength="100000" aria-describedby="editor-help"></textarea><p class="editor-tip" id="editor-help">Tab 缩进，Shift+Tab 取消缩进；Esc 后按 Tab 离开编辑区。</p><div class="code-actions"><button class="primary" id="save-code">保存修改</button><button id="verify-code">核验登记版本</button><span id="save-state" class="saved-state"></span></div><p id="review-state" class="review-state"></p><div class="evidence-summary"><h2>当前查看版本的测试</h2><div id="code-evidence"></div></div></div><div id="panel-evidence" role="tabpanel" aria-labelledby="tab-evidence" hidden><h2>当前查看版本的运行证据</h2><div id="full-evidence"></div></div><div id="panel-changes" role="tabpanel" aria-labelledby="tab-changes" hidden><h2>修改前后对比</h2><div id="diff-view"></div><h2>保存的版本</h2><div class="version-list" id="version-list"></div></div></section><section class="chat-pane" aria-label="AI 辅导对话"><div class="chat-heading"><h2>${e.mode==='S1'?'AI 辅导':'固定问题辅导'}</h2><small id="round-count"></small></div><div class="chat-messages" id="messages" aria-label="对话历史"><div id="conversation"></div><div id="call-status" role="status" aria-live="polite"></div></div><div id="stop-area" class="stop-area" hidden></div><form id="answer-form" class="composer"><div class="quick-actions"><button type="button" data-reply="我没理解，请换一种方式解释刚才的问题。">我没理解</button><button type="button" data-reply="能不能先给我一点提示？不要直接给出完整修复。">给一点提示</button><button type="button" id="edit-shortcut">我想修改代码</button><button type="button" id="evidence-shortcut">查看运行证据</button></div><label class="small" for="answer">说说你的想法或疑问</label><textarea id="answer" maxlength="30000" placeholder="可以回答追问，也可以说“为什么这里有问题？”" required></textarea><div class="composer-bottom"><p id="composer-note">Enter 换行，Ctrl+Enter 发送</p><button type="submit" class="primary" id="send-answer">发送回答 →</button></div></form><details class="feedback-mini"><summary>这次辅导切题吗？留下反馈</summary><form id="feedback-form"><label for="feedback-topic">是否切题</label><select id="feedback-topic"><option value="uncertain">不确定</option><option value="yes">切题</option><option value="no">不切题</option></select><label for="feedback-notes" class="small">你的意见（可选）</label><textarea id="feedback-notes" maxlength="5000" placeholder="例如：这个问题我已经回答过了"></textarea><button type="submit">保存反馈</button></form></details></section></div></div>`;
  $('#code-editor').value=saved?.base===selected?saved.text:version().source;
  $('#answer').value=loadDraft(eid,'answer')?.text||'';
  codeKeys($('#code-editor'));
  const sandboxUI=mountSandbox({eid,version,dirty,state:()=>e,refresh});
  if(e.mode==='S1')$('.advanced-fields span:nth-of-type(2)').textContent=aiLabel;
  function showTab(tab){document.querySelectorAll('[data-tab]').forEach(b=>{const active=b.dataset.tab===tab;b.classList.toggle('active',active);b.setAttribute('aria-selected',active);$('#panel-'+b.dataset.tab).hidden=!active;});}
  const number=v=>e.code_versions.indexOf(v)+1;
  const name=v=>v.label==='original'?'原始代码':v.label==='用户提交版本'?`修改版 ${number(v)-1}`:'登记版 · '+v.label;
  function rows(){
    const v=version(),op=[...e.demo.operations].reverse().find(o=>o.version_id===selected && o.payload.source_hash===v.source_sha256 && o.payload.result?.tests?.length);
    if(op)return {rows:op.payload.result.tests.map(t=>({args:t.args,before:t.before.actual_output,actual:t.after.actual_output,expected:t.after.reference_output,success:t.after.execution_success})),comparison:true,label:'本会话实际执行 · '+time(op.completed_at)};
    const sourceVersion=v.label==='original'?'original':v.label;
    const frozen=e.case_snapshot.evidence.filter(r=>r.source_version===sourceVersion && (v.label==='original'?e.case_snapshot.source_sha256:e.case_snapshot.versions[v.label]?.source_sha256)===v.source_sha256);
    return {rows:frozen.map(r=>({args:r.args,actual:r.actual,expected:r.expected})),comparison:false,label:frozen.length?'已审核案例的历史运行证据':'尚未执行'};
  }
  function renderCode(){
    const v=version(),ready=e.demo.version_readiness.find(r=>r.version_id===selected),changed=dirty();
    const versions=JSON.stringify([e.code_versions.map(v=>v.version_id),e.current_code_version_id]);
    if(versions!==versionFingerprint){versionFingerprint=versions;$('#version-select').innerHTML=e.code_versions.map(v=>`<option value="${v.version_id}">${esc(name(v))}${v.version_id===e.current_code_version_id?' · 当前保存版本':''}</option>`).join('');}
    $('#version-select').value=selected;
    $('#save-code').disabled=!changed||saving;$('#verify-code').disabled=changed||verifying||!ready?.can_verify;
    $('#save-state').textContent=saving?'正在保存…':changed?'有未保存的编辑':'已保存';
    $('#review-state').className='review-state '+(!ready?.source_registered?'warning':'muted');
    $('#review-state').textContent=changed?'编辑内容尚未保存，也未执行。保存后会建立单独版本。':!ready?.source_registered?(e.sandbox?.ready?'旧 F03/F04 核验仍待审核；这个保存版本可使用下方独立沙箱。':'待审核，暂不能运行。可以保存、继续编辑和比较文本。'):!ready.can_verify?'源码已登记，但旧核验所需的对比来源版本未审核。':'此源码与审核登记版本一致，可以核验指定输入；通过不代表整体正确。';
    const facts=rows(),html=evidenceTable(facts.rows,facts.comparison)+`<p class="evidence-footnote">${esc(facts.label)} · 仅对应上方选中版本。有限测试不证明整体正确或知识掌握。</p>`;
    $('#code-evidence').innerHTML=changed?'<p class="notice">编辑草稿尚未运行。原保存版本的结果可在“运行证据”中查看，不能用于确认这个草稿。</p>':html;
    $('#full-evidence').innerHTML=(changed?`<p class="notice">下列证据对应已保存的「${esc(name(v))}」，不适用于编辑草稿。</p>`:'')+html;
    const event=[...e.events].reverse().find(r=>r.type==='unverified_code_recorded' && r.payload.version_id===selected);
    $('#diff-view').innerHTML=event?`<p class="small muted">与保存修改时的来源版本比较。</p><pre class="diff">${esc(event.payload.modification.unified_diff||'未改变源码文本')}</pre>`:'<p class="muted">这是预先登记的代码版本，没有本会话的修改差异。</p>';
    $('#version-list').innerHTML=e.code_versions.map(v=>`<div class="version-item"><strong>${esc(name(v))}</strong><small>${esc(time(v.created_at))} · ${v.verification_status==='unverified'?'保存待审':'有登记或核验记录'}</small></div>`).join('');
    sandboxUI.render();
  }
  function message(text,role,label,date,extra=''){return `<article class="message ${role}"><div class="message-meta">${esc(label)}${date?' · '+esc(time(date)):''}</div><div class="bubble">${esc(text)}</div>${extra}</article>`;}
  function renderChat(){
    const mark=JSON.stringify([e.turns.map(t=>[t.status,t.output,t.error,t.answer_raw]),e.status,e.current_code_version_id]);
    if(mark!==chatFingerprint){
      chatFingerprint=mark;const box=$('#messages'),bottom=box.scrollHeight-box.scrollTop-box.clientHeight<90;
      let html=message(e.case_snapshot.demo_initial_output.student_message,'teacher','题目引导 · 固定首次问题',e.created_at);
      for(const t of e.turns){
        if(t.answer_raw)html+=message(t.answer_raw,'student','你的回答',t.submitted_at,`<span class="small muted">回答时使用已保存版本 ${esc(name(e.code_versions.find(v=>v.version_id===t.code_version_id)))}</span>`);
        if(t.status==='succeeded'){
          const o=t.output;
          const ctx=t.public_input?.execution_context,stale=t.code_version_id!==e.current_code_version_id;
          const evidence=ctx?`<p class="evidence-footnote">依据保存版本 ${esc(name(e.code_versions.find(v=>v.version_id===ctx.version_id)))} · SHA-256 ${esc(ctx.source_sha256.slice(0,12))} · ${ctx.task_id?'执行任务 '+esc(ctx.task_id.slice(0,12))+' · '+esc(ctx.status):'没有该版本 Docker 执行证据'}${stale?' · 已是历史版本，不能用于确认当前代码':''}。教学主张尚未核验。</p>`:'';
          const extra=evidence+`<span class="action-tag">下一步：${esc(e.action_labels[o.next_action]||actions[o.next_action]||'查看建议')}</span><details><summary>为什么这样建议</summary><p>${esc(o.decision_basis)}</p>${o.uncertainties?.length?`<p>还不能确认：${esc(o.uncertainties.join('；'))}</p>`:''}</details>`;
          html+=message(o.student_message,'teacher',realAI?'AI · 真实模型回复':e.mode==='S0'?'固定规则回复':'测试工件 · 不是正式模型回复',t.completed_at,extra);
        }
      }
      $('#conversation').innerHTML=html;if(bottom||!e.turns.length)box.scrollTop=box.scrollHeight;
    }
    const last=e.turns.at(-1),waiting=last && running.has(last.status),limit=e.turns.length>=2;
    $('#session-status').textContent=status[e.status]||e.status;$('#round-count').textContent=`后续回复 ${e.turns.filter(t=>t.status==='succeeded').length} / 最多 2 次`;
    const disabled=submitting||waiting||e.status!=='active'||limit||last&&last.status!=='succeeded';
    $('#send-answer').disabled=!!disabled;$('#answer').disabled=!!disabled;
    document.querySelectorAll('[data-reply]').forEach(b=>b.disabled=!!disabled);
    $('#end-question').disabled=e.status==='completed';
    const reasonText={understanding_sufficient:'可以停止追问，先自己修改代码。保存后再查看可核验范围。',budget_limited:'本题已达到原型的三次教学输出上限，可继续编辑和保存代码。',manual_end:'你已结束本题。对话、代码和证据都已保留。',await_new_evidence:'需要新版本或更清楚的证据，当前先暂停追问。',user_choice:'当前判断暂停，由你选择下一步。',manual_pause:'本题已暂停。'};
    const stopped=e.status==='completed'||e.status==='paused';$('#stop-area').hidden=!stopped;
    $('#answer-form').hidden=stopped;
    const stopMark=JSON.stringify([e.status,e.end_reason,limit]);
    if(stopped&&stopMark!==stopFingerprint){stopFingerprint=stopMark;$('#stop-area').innerHTML=`<strong>${e.status==='completed'?'本次追问已结束':'追问已暂停'}</strong><div>${esc(reasonText[e.end_reason]||'可继续保存修改；结束不代表已经掌握知识。')}</div><div class="stop-actions"><button id="stop-edit">自行修改代码</button>${e.status==='paused'&&!limit?'<button id="resume-study">准备好后继续</button>':''}<a class="button" id="new-assessment" href="/study/${eid}/assessment">尝试新题验收</a><a class="button" href="/">继续学习 →</a></div>`;
      $('#stop-edit').onclick=()=>{showTab('code');$('#code-editor').focus();record('edit_code');};
      $('#new-assessment').onclick=()=>record('open_assessment');
      if($('#resume-study'))$('#resume-study').onclick=async()=>{try{await api(endpoint+'/control',withOrigin({action:'resume'}));await refresh();}catch(err){toast(err.message,true);}};
    }
    $('#composer-note').textContent=waiting?'回答与执行证据快照已保存；等待期间保存新版会阻断本轮建议。':disabled?'本轮暂不能再发送；仍可编辑代码、查看证据和结束本题。':dirty()?'编辑尚未保存，发送时使用最近保存版本。':selected!==e.current_code_version_id?'当前查看历史版本；发送时使用最近保存版本。':'运行结束后发送想法，辅导将使用当前保存版本的执行记录。Ctrl+Enter 发送；最多两次后续回复。';
    const state=$('#call-status');
    if(waiting){const start=last.attempts.at(-1)?.requested_at||last.submitted_at,elapsed=Math.max(0,Math.floor((Date.now()-Date.parse(start))/1000));
    const phase=e.mode==='S0'?'固定规则处理中':{queued:'后台排队中',connecting:'正在连接 '+aiLabel,generating:'模型正在生成回复'}[last.runtime_phase||last.status];
      state.innerHTML=`<div class="notice call-status"><strong><span class="state-dot"></span>${phase} · 已等待 ${elapsed} 秒</strong>${realAI?'你的回答已保存，可能需要约两分钟或更久。':e.mode==='S0'?'使用固定规则，不调用模型。':'这是测试调用链路，不是真实模型推理。'}可以编辑代码，刷新后会恢复状态。${last.connection_notice?`<p>${esc(last.connection_notice)}</p>`:''}</div>`;
    }else if(last && ['failed','blocked'].includes(last.status)){
      const failureMark=JSON.stringify([last.turn_id,last.error,last.status,e.status]);
      if(failureMark===failureFingerprint)return;failureFingerprint=failureMark;
      state.innerHTML=`<div class="notice error call-status"><strong>${last.status==='blocked'?'回复未通过核验，未作为教学建议展示':'这次回复没有成功'}</strong><p>${esc(last.error||'未取得可用回复。')}</p><p class="small">回答及原始结果已保留，不会自动重新生成。</p><button id="retry-model">明确重试这次调用</button> <a href="/experiments/${eid}">查看失败记录</a></div>`;
      $('#retry-model').disabled=e.status==='completed';$('#retry-model').onclick=async()=>{
        const reason=prompt('请说明重试原因。会新增一次调用，原失败保留。');if(!reason?.trim())return;
        $('#retry-model').disabled=true;try{await api('/api/turns/'+last.turn_id+'/retry',{reason,request_id:crypto.randomUUID()});await refresh();}catch(err){toast(err.message,true);}
      };
    }else {state.innerHTML='';failureFingerprint='';}
  }
  async function refresh(){
    const data=await api(endpoint);e=data;
    if(pending && e.turns.some(t=>t.request_id===pending.request_id)){
      if($('#answer').value===pending.answer){$('#answer').value='';clearDraft(eid,'answer');}
      pending=null;clearDraft(eid,'pending-answer');
    }
    renderCode();renderChat();
  }
  $('#code-editor').oninput=()=>{draft(eid,'code',{base:selected,text:$('#code-editor').value});renderCode();};
  $('#answer').oninput=()=>draft(eid,'answer',{text:$('#answer').value});
  $('#answer').onkeydown=ev=>{if(ev.key==='Enter'&&(ev.ctrlKey||ev.metaKey)){ev.preventDefault();if(!$('#send-answer').disabled)$('#answer-form').requestSubmit();}};
  $('#version-select').onchange=ev=>{
    const next=ev.target.value;
    if(dirty() && !confirm('当前有未保存编辑。切换版本会替换编辑区内容，是否继续？')){ev.target.value=selected;return;}
    selected=next;$('#code-editor').value=version().source;clearDraft(eid,'code');renderCode();
  };
  document.querySelectorAll('[data-tab]').forEach((b,i)=>{b.onclick=()=>{showTab(b.dataset.tab);if(b.dataset.tab!=='code')record(b.dataset.tab==='changes'?'view_diff':'view_evidence');};b.onkeydown=ev=>{if(['ArrowLeft','ArrowRight'].includes(ev.key)){ev.preventDefault();const tabs=[...document.querySelectorAll('[data-tab]')],next=tabs[(i+(ev.key==='ArrowRight'?1:tabs.length-1))%tabs.length];next.focus();next.click();}};});
  $('#save-code').onclick=async()=>{
    if(saving||!dirty())return;const source=$('#code-editor').value;if(!source.trim())return toast('请输入完整代码。',true);
    saving=true;renderCode();try{const v=await api(endpoint+'/code',withOrigin({source,parent_version_id:selected}));selected=v.version_id;if($('#code-editor').value===source)clearDraft(eid,'code');else draft(eid,'code',{base:selected,text:$('#code-editor').value});await refresh();toast('修改已保存为新版本。运行可用性见下方沙箱状态。');}catch(err){toast(err.message,true);}finally{saving=false;renderCode();}
  };
  $('#verify-code').onclick=async()=>{
    if(verifying||dirty())return;verifying=true;renderCode();try{const r=await api('/api/demo/'+eid+'/verify',withOrigin({version_id:selected}));await refresh();toast(r.executed?'已保存实际核验结果，仅适用于指定输入。':'没有执行代码，请查看审核状态。');}catch(err){toast(err.message,true);}finally{verifying=false;renderCode();}
  };
  $('#edit-shortcut').onclick=()=>{showTab('code');$('#code-editor').focus();record('edit_code');};
  $('#evidence-shortcut').onclick=()=>{showTab('evidence');$('#full-evidence').scrollIntoView({block:'nearest'});record('view_evidence');};
  document.querySelectorAll('[data-reply]').forEach(b=>b.onclick=()=>{$('#answer').value=b.dataset.reply;draft(eid,'answer',{text:$('#answer').value});$('#answer-form').requestSubmit();});
  $('#end-question').onclick=async()=>{try{await api(endpoint+'/control',withOrigin({action:'end'}));await refresh();toast('本题已结束；正在进行的调用仍会保留结果。');}catch(err){toast(err.message,true);}};
  $('#answer-form').onsubmit=async ev=>{
    ev.preventDefault();if(submitting||$('#send-answer').disabled)return;const answer=$('#answer').value;if(!answer.trim())return;
    if(!pending||pending.answer!==answer)pending=withOrigin({answer,request_id:crypto.randomUUID(),parent_turn_id:e.turns.at(-1)?.turn_id||null});
    draft(eid,'pending-answer',pending);submitting=true;renderChat();
    try{await api(endpoint+'/turns',pending);await refresh();toast('回答已保存，正在后台处理。');}
    catch(err){toast(err.message,true);try{await refresh();}catch{}}
    finally{submitting=false;renderChat();}
  };
  $('#feedback-form').onsubmit=async ev=>{
    ev.preventDefault();const t=e.turns.filter(t=>t.status==='succeeded').at(-1),text=$('#feedback-notes').value;
    try{if(t)await api('/api/turns/'+t.turn_id+'/feedback',withOrigin({evaluation_source:'user_subjective',on_topic:$('#feedback-topic').value,notes:text}));
      else await api(endpoint+'/notes',withOrigin({text:`首次引导反馈：切题=${$('#feedback-topic').value}；${text}`}));
      toast('反馈已保存。');$('#feedback-notes').value='';await refresh();
    }catch(err){toast(err.message,true);}
  };
  if(e.mode==='S1'&&!realAI){$('.chat-heading h2').textContent='调用链路测试 · 无真实模型';$('.advanced-fields').insertAdjacentHTML('beforeend','<span class="warning">此记录使用测试运行器，不是正式 AI 推理。</span>');}
  renderCode();renderChat();$('#messages').scrollTop=$('#messages').scrollHeight;
  let polling=false;const interval=setInterval(async()=>{if(polling||document.hidden)return;polling=true;try{await refresh();}catch(err){$('#call-status').innerHTML=`<p class="notice error">无法刷新状态：${esc(err.message)}。已提交记录不会因页面断开而删除。</p>`;}finally{polling=false;}},2000);
  window.addEventListener('pagehide',()=>clearInterval(interval),{once:true});
}
