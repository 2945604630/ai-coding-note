import { $,esc,time,withOrigin,api,toast } from './ui.js';

const labels={queued:'排队中',running:'执行中',completed:'正常运行',passed:'测试通过',failed:'测试失败',
  timeout:'超时',exception:'运行异常',resource_limit:'资源超限',output_limit:'输出超限',service_error:'执行服务异常',unavailable:'沙箱未就绪'};

export function mountSandbox({eid,version,dirty,state,refresh}){
  let sending=false,fingerprint='',pending=null;
  $('#review-state').insertAdjacentHTML('afterend',`<section class="sandbox-panel" aria-label="运行与提交测试">
    <h2>运行与提交测试</h2><p class="small muted">运行会调用 solve(n)，展示打印内容和返回值。提交会比较 3 个已审核测试的输出；额外打印也参与比较。</p>
    <label for="sandbox-input" class="small">自定义输入 n（0～8 的整数）</label>
    <div class="sandbox-actions"><input id="sandbox-input" type="number" min="0" max="8" step="1" value="3" required>
      <button id="run-code" type="button">运行代码</button><button id="submit-tests" type="button">提交测试</button></div>
    <p id="sandbox-availability" class="small" role="status"></p>
    <div id="sandbox-current" aria-live="polite"></div>
    <details><summary>每次运行记录（含历史版本）</summary><div id="sandbox-history"></div></details>
  </section>`);
  function resultHTML(job){
    const summary=`<strong>${esc(labels[job.status]||job.status)}</strong> · ${job.mode==='run'?'自定义运行':'审核合同提交'} · ${Number(job.elapsed_seconds||0).toFixed(3)} 秒`;
    return `<article class="sandbox-record"><p>${summary}<br><span class="small muted">${esc(time(job.created_at))} · 源码 ${esc(job.source_sha256.slice(0,12))} · 任务 ${esc(job.task_id.slice(0,8))}</span></p>
      ${job.error?`<p class="notice error">${esc(job.error)}</p>`:''}
      ${(job.results||[]).map(r=>`<div class="sandbox-case"><p class="small">输入 n=${esc(r.input)} · ${esc(labels[r.status]||r.status)}${r.output_truncated?' · 输出已截断':''}</p>
        <span class="small">实际输出 / 标准输出</span><pre>${esc(r.stdout||'（空）')}</pre>
        ${r.expected_output!=null?`<span class="small">参考输出</span><pre>${esc(r.expected_output)}</pre>`:job.mode==='run'?'<p class="small muted">此输入没有已审核参考结果；本次只记录实际行为。</p>':''}
        <details${r.stderr?' open':''}><summary>标准错误</summary><pre>${esc(r.stderr||'（空）')}</pre></details></div>`).join('')}
      ${job.hidden_summary?.total?`<p class="small">隐藏测试：通过 ${job.hidden_summary.passed} / ${job.hidden_summary.total}；输入与输出只在后端保存。</p>`:''}
      <p class="small muted">${job.executed?'本次实际执行仅适用于该源码版本及本次输入。':'本次没有取得代码实际执行证据。'}有限测试不证明整体正确。</p></article>`;
  }
  function render(){
    const sandbox=state().sandbox||{ready:false,reason:'未取得沙箱状态',jobs:[]},v=version(),changed=dirty();
    const busy=sending||sandbox.jobs.some(j=>['queued','running'].includes(j.status));
    $('#run-code').disabled=busy||changed||!sandbox.ready;$('#submit-tests').disabled=busy||changed||!sandbox.ready;
    $('#sandbox-availability').textContent=changed?'请先保存编辑，再运行新版本。':!sandbox.ready?sandbox.reason:busy?'运行已保存，等待执行结果…':'使用当前选中保存版本；运行与提交各保存一条独立记录。';
    const mark=JSON.stringify([sandbox.jobs,selectedIdentity(),changed]);
    if(mark===fingerprint)return;fingerprint=mark;
    const current=sandbox.jobs.filter(j=>j.version_id===v.version_id&&j.source_sha256===v.source_sha256);
    $('#sandbox-current').innerHTML=changed?'<p class="notice">草稿尚未运行。历史记录不能验证这份编辑。</p>':current.length?resultHTML(current.at(-1)):'<p class="small muted">这个源码版本还没有沙箱运行记录。</p>';
    $('#sandbox-history').innerHTML=[...sandbox.jobs].reverse().map(j=>`<details><summary>${esc(time(j.created_at))} · ${esc(labels[j.status]||j.status)} · ${j.version_id===v.version_id?'选中版本':'历史版本'} ${esc(j.source_sha256.slice(0,12))}</summary>${resultHTML(j)}</details>`).join('')||'<p class="small muted">暂无运行记录。</p>';
  }
  function selectedIdentity(){return version().version_id+version().source_sha256;}
  async function send(mode){
    if(sending||dirty()||!state().sandbox?.ready)return;
    const input=$('#sandbox-input');
    if(mode==='run'&&(!input.reportValidity()||!Number.isInteger(Number(input.value))))return;
    const v=version(),data=withOrigin({version_id:v.version_id,source_sha256:v.source_sha256,...(mode==='run'?{input:Number(input.value)}:{})});
    const signature=JSON.stringify([mode,data]);
    if(!pending||pending.signature!==signature)pending={signature,request_id:crypto.randomUUID()};
    sending=true;render();
    try{
      const job=await api(`/api/experiments/${eid}/sandbox/${mode==='run'?'run':'submit'}`,{...data,request_id:pending.request_id});
      pending=null;await refresh();toast(['queued','running'].includes(job.status)?'运行任务已保存。':labels[job.status]||job.status,!['queued','running','completed','passed'].includes(job.status));
    }catch(err){toast('执行请求未成功：'+err.message,true);try{await refresh();}catch{}}
    finally{sending=false;render();}
  }
  $('#run-code').onclick=()=>send('run');$('#submit-tests').onclick=()=>send('submit');
  return {render};
}
