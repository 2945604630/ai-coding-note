import { $, esc, time, status, origin, withOrigin, api, toast, sourceTag } from './ui.js';
import { failureStatuses, collectMistakes, isPracticeRecord } from './learning-records.js';

const path=location.pathname;
const labels={queued:'排队中',running:'执行中',completed:'运行完成',passed:'测试通过',failed:'测试失败',timeout:'已超时',exception:'运行异常',resource_limit:'资源受限',output_limit:'输出过长',service_error:'执行服务异常',unavailable:'沙箱未就绪'};
const names={C01:'整数求和：循环边界',C03:'整数求和：返回结果'};
const blurbs={C01:'练习循环、边界和返回值。先观察一次运行，再解释你的判断。',C03:'从执行结果出发，检查局部修改是否真的改变了结果。'};
const titleOf=e=>names[e?.case_id]||e?.case_id||'编程练习';
const isUser=e=>isPracticeRecord(e);
const demos=rows=>rows.filter(isUser);

document.querySelector('#nav-home').classList.toggle('active',path==='/'||path.startsWith('/study/'));
document.querySelector('#nav-mistakes').classList.toggle('active',path.startsWith('/mistakes'));
document.querySelector('#nav-history').classList.toggle('active',path==='/learning-history');

async function details(rows){
  return (await Promise.allSettled(rows.map(row=>api('/api/experiments/'+row.experiment_id)))).flatMap((x,i)=>x.status==='fulfilled'?[{summary:rows[i],detail:x.value}]:[]);
}
function kind(job){
  if(job.status==='timeout')return '超时';
  if(job.status==='exception')return '运行异常';
  if(job.status==='output_limit')return '输出过长';
  if(job.status==='resource_limit')return '资源受限';
  if(job.status==='service_error')return '执行服务异常';
  return job.status==='failed'?(job.mode==='submit'?'测试未通过':'运行失败'):(labels[job.status]||job.status);
}
function badge(text,tone='neutral'){return `<span class="status-badge ${tone}">${esc(text)}</span>`;}
function empty(title,copy,action=''){return `<div class="empty-state"><div class="empty-mark">□</div><h3>${esc(title)}</h3><p>${esc(copy)}</p>${action}</div>`;}
function mistakeCard(m){
  const j=m.job,r=j?.results?.find(x=>failureStatuses.has(x.status))||j?.results?.at(-1);
  return `<article class="mistake-card"><div class="mistake-card-top"><span class="mistake-icon">!</span><div><span class="kicker">${esc(titleOf(m.detail))}</span><h3>${esc(m.kind)}</h3></div><time>${esc(time(m.date))}</time></div><p>${j?.mode==='submit'?'这次提交没有通过已审核的测试合同。':j?.status==='timeout'?'程序没有在限定时间内结束。':'这次运行没有得到可用的正常结果。'}${r?.input!==undefined?` 输入 n = ${esc(r.input)}。`:''}</p><div class="mistake-card-foot"><span class="hash-chip">版本 ${esc((m.version?.source_sha256||'').slice(0,10))}</span><a class="text-link" href="/mistakes/${encodeURIComponent(m.sessionId)}">查看过程 →</a></div></article>`;
}
function historyRows(rows){
  if(!rows.length)return empty('还没有学习记录','从一道题开始。保存的代码、AI 对话和运行结果会自动留在这里。','<a class="button primary" href="/">开始第一道题</a>');
  return `<div class="history-list">${rows.map(e=>`<a class="history-row" href="/study/${e.experiment_id}"><span class="history-dot ${e.status}"></span><span class="history-main"><strong>${esc(titleOf(e))}</strong><small>${esc(e.name||'未命名练习')} · ${esc(time(e.created_at))}</small></span><span class="history-right">${badge(status[e.status]||e.status,e.status==='active'?'accent':'neutral')}<span aria-hidden="true">→</span></span></a>`).join('')}</div>`;
}
function practiceCard(c,i){return `<article class="practice-card"><div class="practice-index">0${i+1}</div><div class="practice-copy"><span class="kicker">Python · 基础练习</span><h3>${esc(names[c.case_id]||c.label||c.case_id)}</h3><p>${esc(blurbs[c.case_id]||'从题目、代码和运行证据开始，一步一步完成练习。')}</p><div class="practice-meta"><span>真实运行</span><span>AI 辅导</span></div></div><button class="primary start-case" data-case="${esc(c.case_id)}">开始练习 <span aria-hidden="true">→</span></button></article>`;}

async function home(){
  const [all,cases,health]=await Promise.all([api('/api/experiments'),api('/api/demo/cases'),api('/api/health')]);
  const rows=demos(all),items=await details(rows.slice(0,8)),mistakes=collectMistakes(items),last=localStorage.getItem('aic-v2:last-session');
  const candidate=rows.find(e=>e.experiment_id===last&&['active','paused','failed'].includes(e.status))||rows.find(e=>['active','paused','failed'].includes(e.status));
  const provider=health.ai_provider?.provider;
  $('#main').innerHTML=`<div class="home-shell"><section class="hero-grid"><div class="hero-copy"><p class="kicker">AIC / 今天的练习</p><h1>把一个错误，<em>弄清楚。</em></h1><p class="hero-lede">写下你的判断，运行它，看见证据，再决定下一步。AI 会跟着当前代码版本一起阅读。</p><div class="hero-actions"><a class="button primary" href="#practice">开始练习 <span aria-hidden="true">→</span></a>${candidate?`<a class="text-link" href="/study/${candidate.experiment_id}">继续 ${esc(titleOf(candidate))} ↗</a>`:''}</div></div><div class="hero-note"><span class="note-label">学习方式</span><strong>先自己想，再问一句</strong><p>运行结果、代码版本和对话会绑定保存。旧版本的成功，不会替新版本背书。</p><div class="note-line"><span class="signal-dot"></span>${health.sandbox?.ready?'本机沙箱已就绪':'沙箱待本机验收'}<span class="note-sep">·</span>${provider==='disabled'?'AI 已关闭':provider==='api'?'API Provider':'Codex CLI'}</div></div></section><section class="quick-strip"><div><span class="strip-label">进行中的练习</span><strong>${rows.filter(e=>e.status==='active').length}</strong></div><div><span class="strip-label">最近错题</span><strong>${mistakes.length}</strong></div><div><span class="strip-label">已保存记录</span><strong>${rows.length}</strong></div><p>这些是记录数量，不代表掌握程度。</p></section><section class="home-section" id="practice"><div class="section-heading"><div><p class="kicker">Practice</p><h2>选一道题开始</h2></div><span class="section-note">${cases.length} 道可用练习 · 先从一题做起</span></div><div class="practice-list">${cases.map(practiceCard).join('')}</div><details class="advanced settings-fold"><summary>学习设置</summary><div class="advanced-fields"><label>这次学习的名称（可选）<input id="session-name" maxlength="120" placeholder="例如：周末求和练习"></label><label>辅导方式<select id="mode"><option value="S1">AI 辅导（Codex CLI）</option><option value="S0">固定提示，不调用模型</option></select></label><p class="muted">${provider==='disabled'?'当前 AI 已关闭，将使用固定提示。':'AI 只读取当前题目、代码版本和已保存的执行证据。'}</p></div></details></section><section class="home-columns"><div class="home-section compact-section"><div class="section-heading"><div><p class="kicker">Mistakes</p><h2>最近的错题</h2></div><a class="text-link" href="/mistakes">打开错题本 →</a></div>${mistakes.length?`<div class="mistake-mini-list">${mistakes.slice(0,3).map(mistakeCard).join('')}</div>`:empty('还没有错题','当一次真实运行失败时，它会出现在这里，带着对应版本和错误证据。')}</div><div class="home-section compact-section"><div class="section-heading"><div><p class="kicker">History</p><h2>最近学习</h2></div><a class="text-link" href="/learning-history">查看全部 →</a></div>${historyRows(rows.slice(0,4))}</div></section></div>`;
  const mode=$('#mode'),option=mode?.querySelector('option[value="S1"]');
  if(provider==='api'&&option)option.textContent='AI 辅导（外部 API）';
  if(provider==='disabled'&&option){option.textContent='AI 已关闭';option.disabled=true;mode.value='S0';}
  let creating=false;
  document.querySelectorAll('.start-case').forEach(btn=>btn.onclick=async()=>{if(creating)return;creating=true;document.querySelectorAll('.start-case').forEach(b=>b.disabled=true);const data=withOrigin({feature:'DEMO',case_id:btn.dataset.case,mode:mode.value,source_type:origin()==='automated_test'?'automated_test':'real_user',name:$('#session-name')?.value||'',entry_point:'learning'});try{const e=await api('/api/experiments',{...data,request_id:crypto.randomUUID()});localStorage.setItem('aic-v2:last-session',e.session_id);location.href='/study/'+e.session_id;}catch(err){toast(err.message,true);creating=false;document.querySelectorAll('.start-case').forEach(b=>b.disabled=false);}});
}
async function mistakesPage(){
  const rows=demos(await api('/api/experiments')),mistakes=collectMistakes(await details(rows));
  $('#main').innerHTML=`<div class="page-shell"><div class="page-title"><div><p class="kicker">Review / 错题本</p><h1>把错题留下，<em>下次从这里开始。</em></h1><p class="page-lede">这里只显示真实保存过的失败运行和提交。错误记录帮助你复盘，不自动说明你已经掌握或还没掌握。</p></div><a class="button primary" href="/">继续做题 <span aria-hidden="true">→</span></a></div><div class="filter-bar"><label>按结果筛选<select id="mistake-filter"><option value="">全部错误</option><option value="超时">超时</option><option value="测试未通过">测试未通过</option><option value="运行异常">运行异常</option><option value="输出过长">输出过长</option></select></label><span class="filter-count" id="mistake-count"></span></div><div id="mistake-list"></div></div>`;
  const render=()=>{const value=$('#mistake-filter').value,shown=value?mistakes.filter(m=>m.kind===value):mistakes;$('#mistake-count').textContent=`${shown.length} 条真实记录`;$('#mistake-list').innerHTML=shown.length?`<div class="mistake-list">${shown.map(mistakeCard).join('')}</div>`:empty(value?'没有符合条件的记录':'错题本还没有内容',value?'换一个筛选条件，或回到练习继续运行。':'运行一次失败后，这里会自动出现题目、版本和错误证据。','<a class="button" href="/">回到学习首页</a>');};
  $('#mistake-filter').onchange=render;render();
}
async function mistakeDetail(eid){
  const e=await api('/api/experiments/'+decodeURIComponent(eid)),items=collectMistakes([{detail:e}]);
  if(!items.length){$('#main').innerHTML=`<div class="page-shell">${empty('这道题还没有错误记录','没有找到对应的失败运行。旧版本的结果不会被当作当前版本证据。','<a class="button" href="/mistakes">返回错题本</a>')}</div>`;return;}
  const m=items[0],j=m.job,r=j?.results?.find(x=>failureStatuses.has(x.status))||j?.results?.at(-1),turns=e.turns?.filter(t=>t.status==='succeeded')||[],diffs=(e.events||[]).filter(x=>x.type==='unverified_code_recorded');
  $('#main').innerHTML=`<div class="page-shell mistake-detail"><a class="back-link" href="/mistakes">← 错题本</a><div class="page-title detail-title"><div><p class="kicker">${esc(titleOf(e))} · 错误记录</p><h1>${esc(j?.mode==='submit'?'测试未通过':m.kind)}</h1><p class="page-lede">${esc(time(m.date))} · 这次结果只对应保存版本 <code>${esc((m.version?.source_sha256||'').slice(0,12))}</code></p></div><a class="button primary" href="/study/${encodeURIComponent(eid)}">再做一次 <span aria-hidden="true">→</span></a></div><div class="review-flow"><section class="flow-block"><span class="flow-number">01</span><div><p class="kicker">题目</p><h2>${esc(e.case_snapshot.statement)}</h2><p>${esc(e.case_snapshot.input_contract)}</p></div></section><section class="flow-block error-block"><span class="flow-number">02</span><div><p class="kicker">实际错误</p><h2>${esc(m.kind)}</h2>${j?.error?`<p class="notice error">${esc(j.error)}</p>`:''}${r?`<div class="output-grid"><div><span>标准输出</span><pre>${esc(r.stdout||'（空）')}</pre></div><div><span>标准错误</span><pre>${esc(r.stderr||'（空）')}</pre></div>${r.expected_output!=null?`<div><span>参考输出</span><pre>${esc(r.expected_output)}</pre></div>`:''}</div>`:'<p class="muted">没有保存可展示的输出。执行服务没有报告成功，不会补写结果。</p>'}</div></section><section class="flow-block"><span class="flow-number">03</span><div><p class="kicker">当时的代码</p><h2>${esc(m.version?.label==='original'?'原始代码':'保存版本')}</h2><pre class="code-snapshot">${esc(m.version?.source||'该版本源码不可用')}</pre></div></section><section class="flow-block"><span class="flow-number">04</span><div><p class="kicker">AI 辅导</p><h2>${turns.length?'你们讨论过这些线索':'还没有 AI 复盘记录'}</h2>${turns.length?turns.map(t=>`<article class="review-message"><span>AI 辅导 · ${esc(time(t.completed_at))}</span><p>${esc(t.output?.student_message||'已保存一条辅导回复。')}</p></article>`).join(''):'<p class="muted">回到练习工作台，先运行当前版本，再用右侧 AI 询问这次错误。AI 的解释是辅导建议，不是认知诊断。</p>'}</div></section><section class="flow-block"><span class="flow-number">05</span><div><p class="kicker">后续修改</p><h2>${diffs.length?'你保存过后续版本':'等待你的下一次修改'}</h2>${diffs.length?diffs.map(d=>`<pre class="diff">${esc(d.payload?.modification?.unified_diff||'已保存版本，暂无文本差异')}</pre>`).join(''):'<p class="muted">修改代码、保存并重新运行后，这里会继续显示版本之间的差异。</p>'}</div></section></div><p class="technical-note">技术详情：session ${esc(e.experiment_id)} · task ${esc(j?.task_id||'无')} · SHA-256 ${esc(m.version?.source_sha256||'')}</p></div>`;
}
async function historyPage(){
  const all=demos(await api('/api/experiments'));$('#main').innerHTML=`<div class="page-shell"><div class="page-title"><div><p class="kicker">History / 学习历史</p><h1>每一次修改，<em>都有来处。</em></h1><p class="page-lede">按练习查看代码版本、运行记录与 AI 对话。技术 ID 默认藏在详情里，必要时再打开。</p></div><a class="button primary" href="/">开始练习 <span aria-hidden="true">→</span></a></div><div class="history-overview"><div><strong>${all.length}</strong><span>次练习</span></div><div><strong>${all.filter(e=>e.status==='completed').length}</strong><span>已结束</span></div><div><strong>${all.filter(e=>e.status==='active').length}</strong><span>进行中</span></div></div>${historyRows(all)}</div>`;
}
try{if(path.startsWith('/study/')){const eid=path.split('/')[2];if(path.endsWith('/assessment'))await (await import('./assessment.js')).assessment(eid);else await (await import('./study.js')).study(eid);}else if(path.startsWith('/mistakes/'))await mistakeDetail(path.split('/')[2]);else if(path==='/mistakes')await mistakesPage();else if(path==='/learning-history')await historyPage();else await home();}catch(e){$('#main').innerHTML=`<div class="page-shell"><h1>页面暂时打不开</h1><p class="notice error">${esc(e.message)}</p><a class="button" href="/">返回学习首页</a></div>`;}
