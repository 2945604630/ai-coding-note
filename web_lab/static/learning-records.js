export const failureStatuses = new Set(['failed','timeout','exception','resource_limit','output_limit','service_error']);

export function failureKind(job) {
  if (job.status === 'timeout') return '超时';
  if (job.status === 'exception') return '运行异常';
  if (job.status === 'output_limit') return '输出过长';
  if (job.status === 'resource_limit') return '资源受限';
  if (job.status === 'service_error') return '执行服务异常';
  return job.status === 'failed' ? (job.mode === 'submit' ? '测试未通过' : '运行失败') : job.status;
}

export function isPracticeRecord(e) {
  return e?.feature === 'DEMO' && e.source_type !== 'automated_test' && !['automated_test','simulated_student','historical_replay'].includes(e.creation_input_origin?.kind);
}

export function jobsForVersion(e, version) {
  return (e?.sandbox?.jobs || []).filter(job => job.session_id === e.experiment_id && job.version_id === version?.version_id && job.source_sha256 === version?.source_sha256);
}

export function executionSummary(e, version) {
  const jobs=jobsForVersion(e,version);
  const latest=jobs.at(-1);
  if(!latest) return {kind:'unrun',jobs:[]};
  if(failureStatuses.has(latest.status)) return {kind:'failed',status:latest.status,jobs};
  if(latest.mode==='run' && latest.status==='completed') return {kind:'completed',status:latest.status,jobs};
  if(latest.mode==='submit' && latest.status==='passed') return {kind:'passed',status:latest.status,jobs};
  return {kind:latest.status,status:latest.status,jobs};
}

export function collectMistakes(items) {
  const records=[];
  for(const item of items){
    const e=item.detail||item;
    if(!isPracticeRecord(e)) continue;
    for(const job of (e.sandbox?.jobs||[])){
      if(job.session_id!==e.experiment_id) continue;
      if(!failureStatuses.has(job.status) && !(job.results||[]).some(r=>failureStatuses.has(r.status))) continue;
      const version=(e.code_versions||[]).find(v=>v.version_id===job.version_id && v.source_sha256===job.source_sha256);
      if(!version) continue;
      records.push({id:`${e.experiment_id}:${job.task_id}`,sessionId:e.experiment_id,detail:e,job,version,kind:failureKind(job),date:job.created_at});
    }
  }
  return records.sort((a,b)=>Date.parse(b.date||0)-Date.parse(a.date||0));
}
