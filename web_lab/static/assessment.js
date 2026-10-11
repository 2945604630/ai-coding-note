import { $,esc,time,withOrigin,api,toast,loadDraft,draft,clearDraft,codeKeys } from './ui.js';
const eligibility={eligible_by_records:'按当前记录符合首次独立作答条件',assisted_or_exposed:'有帮助或提前暴露记录，不能计为独立首次作答',unknown:'帮助或来源信息不足，独立作答条件未知'};
export async function assessment(eid){
  let e=await api('/api/experiments/'+eid),busy=false;
  if(e.feature!=='DEMO'){location.replace('/experiments/'+eid);return;}
  const base='/api/demo/'+eid;
  $('#main').innerHTML=`<div class="assessment-shell"><div class="page-title"><div><a href="/study/${eid}">← 返回本题</a><h1>尝试一道新题</h1><p class="muted">首次提交会单独保留。后续修改和帮助记录不会覆盖它。</p></div></div><div id="assessment-content"></div></div>`;
  async function refresh(){e=await api('/api/experiments/'+eid);render();}
  function render(){
    const d=e.demo,a=d.assessment;
    if(d.assessment_error){$('#assessment-content').innerHTML=`<p class="notice error">记录完整性检查失败：${esc(d.assessment_error)}。首次提交仍锁定，不会重置。请在<a href="/experiments/${eid}">实验管理</a>查看详情。</p>`;return;}
    if(!a){
      $('#assessment-content').innerHTML=`<section class="assessment-panel"><h2>开始前，确认帮助情况</h2><p class="muted">进入后会展示新题。请按真实情况填写；不确定可以保留，不影响保存代码。</p><form id="begin-assessment"><label for="external-help">此前是否得到过这道新题的外部帮助？<select id="external-help"><option value="unknown">不确定</option><option value="none">我声明没有得到帮助</option><option value="used">得到过帮助或答案</option></select></label><details><summary>可以确认的记录范围（可选）</summary><label class="check"><input type="checkbox" id="check-history">本次相关帮助均已记录</label><label class="check"><input type="checkbox" id="check-exposure">已检查是否提前见过这道新题或答案</label><label class="check"><input type="checkbox" id="check-source">提交来源已完整记录</label></details><button class="primary" type="submit">查看新题 →</button></form><p class="small muted">这些是声明与记录，不能客观证明没有使用外部帮助。</p></section>`;
      $('#begin-assessment').onsubmit=async ev=>{ev.preventDefault();if(busy)return;busy=true;ev.target.querySelector('button').disabled=true;
        try{await api(base+'/assessment',withOrigin({external_help:$('#external-help').value,history_complete:$('#check-history').checked,prior_exposure_checked:$('#check-exposure').checked,source_record_complete:$('#check-source').checked}));await refresh();}
        catch(err){toast(err.message,true);ev.target.querySelector('button').disabled=false;}finally{busy=false;}};return;
    }
    const q=a.session.question,first=a.first;
    $('#assessment-content').innerHTML=`<div class="assessment-grid"><section class="assessment-panel"><h2>新题</h2><p>${esc(q.statement)}</p><p class="contract">${esc(q.input_contract)}</p><label for="assessment-code">${first?'后续修改（首次提交不会被覆盖）':'首次提交代码'}</label><textarea class="code-editor" id="assessment-code" spellcheck="false" maxlength="100000"></textarea><p class="editor-tip">未经审核代码仅保存待审，不会执行。Tab 缩进；Esc 后 Tab 离开。</p><button class="primary" id="submit-assessment">${first?'保存后续修改':'保存并冻结首次提交'}</button><p id="assessment-save-state" class="small muted"></p><details><summary>补记帮助或答案暴露</summary><form id="declare-help"><label>帮助类型<select id="help-kind"><option value="hint">提示</option><option value="full_answer">完整答案</option><option value="ai_help">AI 辅助</option><option value="external_help">外部帮助</option><option value="question_seen">提前见过题目</option></select></label><label>关联范围<select id="help-target"><option value="assessment">这道新题</option><option value="unknown">不确定</option><option value="original">上一道题</option></select></label><label class="check"><input type="checkbox" id="help-before">发生在首次提交之前（补记）</label><label for="help-content">帮助原文或来源说明<textarea id="help-content" required maxlength="30000"></textarea></label><button type="submit">保存帮助记录</button></form></details></section><aside class="assessment-panel"><h2>提交与测试记录</h2><p class="notice">${eligibility[a.current_eligibility.status]||'记录状态未知'}</p><p class="small muted">${a.help_records.length} 条相关帮助已保存；资格和程序成绩分别记录。</p>${first?`<h3>首次提交 · 已冻结</h3><p>${first.execution_state==='pending_review'?'待审核，暂不能运行':`指定测试通过 ${first.score.passed} / ${first.score.tested}`}</p><details><summary>查看不可覆盖的首次代码</summary><pre>${esc(first.source_text)}</pre></details><p class="small muted">首次保存时间与版本在完整记录中保留。</p><h3>后续修改 ${a.revisions.length} 次</h3>${a.revisions.map(r=>`<p class="small">${esc(r.revision_id)} · ${r.comparison.status==='pending_review'?'保存待审':`指定测试通过 ${r.comparison.summary.after_passed??'未核验'} / ${r.comparison.summary.test_count??0}`}</p>`).join('')}`:'<p class="muted">尚未提交。第一份代码即使不能执行，也会保留为首次提交。</p>'}<p class="small muted">指定测试通过不代表整体正确，也不证明知识掌握或学习迁移。</p><a class="button" href="/study/${eid}">返回本题</a> <a class="button" href="/">继续学习</a></aside></div>`;
    const old=loadDraft(eid,'assessment');$('#assessment-code').value=old?.text||'';codeKeys($('#assessment-code'));
    $('#assessment-code').oninput=()=>draft(eid,'assessment',{text:$('#assessment-code').value});
    $('#submit-assessment').onclick=async()=>{if(busy)return;const text=$('#assessment-code').value;if(!text.trim())return toast('请输入完整代码。',true);
      busy=true;$('#submit-assessment').disabled=true;$('#assessment-save-state').textContent='正在保存…';
      try{await api(base+(first?'/assessment-code':'/first'),withOrigin({source:text}));clearDraft(eid,'assessment');await refresh();toast(first?'后续修改已单独保存。':'首次提交已冻结。');}
      catch(err){toast(err.message,true);$('#assessment-save-state').textContent='保存失败，输入仍保留。';$('#submit-assessment').disabled=false;}finally{busy=false;}};
    $('#declare-help').onsubmit=async ev=>{ev.preventDefault();if(busy)return;busy=true;ev.target.querySelector('button').disabled=true;
      try{await api(base+'/help',withOrigin({kind:$('#help-kind').value,target:$('#help-target').value,content:$('#help-content').value,applies_before_first:$('#help-before').checked?true:null}));await refresh();toast('帮助记录已追加。');}
      catch(err){toast(err.message,true);ev.target.querySelector('button').disabled=false;}finally{busy=false;}};
  }
  render();
}
