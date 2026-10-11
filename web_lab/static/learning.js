import { $,esc,time,status,origin,withOrigin,api,toast,sourceTag } from './ui.js';
const path=location.pathname;
$('#nav-history').classList.toggle('active',path==='/learning-history');
$('#nav-home').classList.toggle('active',path!=='/learning-history');
function recordRows(rows){return rows.map(e=>`<a class="record-row" href="${e.feature==='DEMO'?'/study/':'/experiments/'}${e.experiment_id}"><span><strong>${esc(e.name)}</strong><small>${esc(time(e.created_at))}</small></span><span class="record-meta">${esc(status[e.status]||e.status)} <span aria-hidden="true">→</span></span></a>`).join('') || '<p class="empty">还没有学习记录。从一道题开始，回答和修改会自动保存。</p>';}
async function home(history=false){
  const [all,cases]=await Promise.all([api('/api/experiments'),api('/api/demo/cases')]);
  const rows=all.filter(e=>e.feature==='DEMO' && e.source_type!=='automated_test' &&
    !['automated_test','simulated_student','historical_replay'].includes(e.creation_input_origin?.kind));
  const last=localStorage.getItem('aic-v2:last-session');
  const candidate=rows.find(e=>e.experiment_id===last && ['active','paused','failed'].includes(e.status)) || rows.find(e=>['active','paused','failed'].includes(e.status));
  if(history){$('#main').innerHTML=`<div class="home-shell"><div class="page-title"><div><p class="eyebrow">每一次回答与修改，都留在这里</p><h1>学习记录</h1></div><a class="button" href="/">开始一道题</a></div><div class="records">${recordRows(rows)}</div><p class="muted">完整实验、自动测试、来源声明和导出在<a href="/history">实验历史</a>中查看。历史未记录来源的输入不视为已验证真人数据。</p></div>`;return;}
  $('#main').innerHTML=`<div class="home-shell"><div class="page-title"><div><p class="eyebrow">从代码里的一个问题开始</p><h1>今天，练习解决一个问题。</h1><p class="subtitle">看运行证据，说说你的想法，再自己动手修改。</p></div><span class="local-status">回答与代码保存在本机</span></div><div class="home-grid"><section class="start-area"><h2>开始一道题</h2><p class="muted">选择一份代码，和 AI 一起检查它的行为。</p><div class="case-list">${cases.map((c,i)=>`<article class="case-card"><div class="case-number">0${i+1}</div><div class="case-copy"><span class="tag">Python · 基础练习</span><h3>${i===0?'整数求和':'求和与返回结果'}</h3><p>${i===0?'比较循环过程与题目要求，解释测试中的差异。':'结合不同代码版本与测试结果，判断修改的影响。'}</p></div><button class="primary start-case" data-case="${esc(c.case_id)}">开始练习 <span aria-hidden="true">→</span></button></article>`).join('')}</div><details class="advanced"><summary>高级设置</summary><div class="advanced-fields"><label>这次学习的名称（可选）<input id="session-name" maxlength="120" placeholder="例如：周末求和练习"></label><label>辅导方式<select id="mode"><option value="S1">真实 AI（Codex CLI）</option><option value="S0">固定问题，不调用模型</option></select></label><p class="muted">AI 使用已有模型配置，新学习记录保存完整配置；首次引导是固定问题。</p></div></details></section><aside class="continue-area"><h2>继续上次学习</h2>${candidate?`<h3>${esc(candidate.name)}</h3><p class="muted">${esc(status[candidate.status])} · ${esc(time(candidate.created_at))}</p><a class="button primary" href="/study/${candidate.experiment_id}">继续学习 →</a>`:'<p class="muted">开始练习后，可以随时回来继续。刷新页面不会丢失已保存的回答。</p>'}<div class="activity-summary"><span><strong>${rows.length}</strong>次记录</span><span><strong>${rows.filter(e=>e.status==='completed').length}</strong>次结束</span></div><p class="small muted">结束次数是活动记录，不代表掌握程度。</p></aside></div><section class="recent"><div class="section-heading"><h2>最近学习</h2><a href="/learning-history">查看全部 →</a></div><div class="records">${recordRows(rows.slice(0,5))}</div></section></div>`;
  const health=await api('/api/health'),provider=health.ai_provider?.provider;
  const aiOption=$('#mode option[value="S1"]');
  if(provider==='api')aiOption.textContent='真实 AI（外部 API）';
  if(provider==='disabled'){aiOption.textContent='AI 已禁用';aiOption.disabled=true;$('#mode').value='S0';}
  let creating=false,pending=null;
  document.querySelectorAll('.start-case').forEach(btn=>btn.onclick=async()=>{
    if(creating)return;creating=true;document.querySelectorAll('.start-case').forEach(b=>b.disabled=true);
    const data=withOrigin({feature:'DEMO',case_id:btn.dataset.case,mode:$('#mode').value,
      source_type:origin()==='automated_test'?'automated_test':'real_user',name:$('#session-name').value,entry_point:'learning'});
    if(!pending || JSON.stringify(pending.data)!==JSON.stringify(data))pending={data,id:crypto.randomUUID()};
    try{const e=await api('/api/experiments',{...data,request_id:pending.id});localStorage.setItem('aic-v2:last-session',e.session_id);location.href='/study/'+e.session_id;}
    catch(e){toast(e.message,true);creating=false;document.querySelectorAll('.start-case').forEach(b=>b.disabled=false);}
  });
}
try{
  if(path.startsWith('/study/')){
    const eid=path.split('/')[2];
    if(path.endsWith('/assessment'))await (await import('./assessment.js')).assessment(eid);
    else await (await import('./study.js')).study(eid);
  }else await home(path==='/learning-history');
}catch(e){$('#main').innerHTML=`<div class="home-shell"><h1>暂时无法打开</h1><p class="notice error">${esc(e.message)}</p><a class="button" href="/">返回学习首页</a></div>`;}
