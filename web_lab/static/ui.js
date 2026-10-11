export const $ = s => document.querySelector(s);
export const esc = v => String(v ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const time = v => v ? new Date(v).toLocaleString('zh-CN',{hour12:false}) : '';
export const status = {active:'学习中',paused:'已暂停',completed:'已结束',failed:'回复失败'};
export const origin = () => {
  const flag=new URLSearchParams(location.search).get('source_type');
  if(flag==='automated_test')sessionStorage.setItem('aic-input-origin','automated_test');
  if(flag==='real_user')sessionStorage.removeItem('aic-input-origin');
  return navigator.webdriver || sessionStorage.getItem('aic-input-origin')==='automated_test' ? 'automated_test' : 'manual_browser';
};
export const withOrigin = data => ({...data,input_origin:origin()});
export async function api(url,data) {
  const r=await fetch(url,data===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  if(!r.ok){let e;try{e=(await r.json()).detail;}catch{e=`请求失败 (${r.status})`;}throw new Error(typeof e==='string'?e:JSON.stringify(e));}
  return r.json();
}
let timer;
export function toast(message,error=false){const t=$('#toast');t.textContent=message;t.dataset.error=error;t.hidden=false;clearTimeout(timer);timer=setTimeout(()=>t.hidden=true,6500);}
export function sourceTag(e){return e.source_type==='automated_test'||e.creation_input_origin?.kind==='automated_test'?'自动测试记录':'学习记录 · 输入来源见记录';}
export function key(eid,type){return `aic-v2:${eid}:${type}`;}
export function loadDraft(eid,type){try{return JSON.parse(localStorage.getItem(key(eid,type)));}catch{return null;}}
export function draft(eid,type,value){localStorage.setItem(key(eid,type),JSON.stringify(value));}
export function clearDraft(eid,type){localStorage.removeItem(key(eid,type));}
export function codeKeys(el){
  let escapeTab=false;
  el.addEventListener('keydown',e=>{
    if(e.key==='Escape'){escapeTab=true;return;}
    if(e.key==='Tab' && !escapeTab){e.preventDefault();const s=el.selectionStart,end=el.selectionEnd;
      if(e.shiftKey){const line=el.value.lastIndexOf('\n',s-1)+1;const spaces=(el.value.slice(line).match(/^ {1,4}/)||[''])[0].length;
        if(spaces){el.setRangeText('',line,line+spaces,'end');el.selectionStart=el.selectionEnd=Math.max(line,s-spaces);}}
      else el.setRangeText('    ',s,end,'end');
      el.dispatchEvent(new Event('input',{bubbles:true}));
    }
    escapeTab=false;
  });
}
export function evidenceTable(rows,comparison=false){
  if(!rows.length)return '<p class="muted">这个版本还没有运行证据。旧版本的结果不会用于确认本版本。</p>';
  return `<table class="evidence-table"><thead><tr><th>输入</th>${comparison?'<th>修改前</th>':''}<th>实际输出</th><th>预期输出</th><th>结果</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${esc(JSON.stringify(r.args))}</td>${comparison?`<td>${esc(JSON.stringify(r.before))}</td>`:''}<td>${esc(r.success===false?'执行异常':JSON.stringify(r.actual))}</td><td>${esc(JSON.stringify(r.expected))}</td><td class="${r.success===false||r.actual!==r.expected?'fail-text':'pass-text'}">${r.success===false?'无法核验':r.actual===r.expected?'通过':'未通过'}</td></tr>`).join('')}</tbody></table>`;
}
