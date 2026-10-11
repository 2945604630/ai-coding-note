"""First-response-only official CLI generation; no API tokens, mock inference or retries."""
import json
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
from experiments.common import digest,dump
from experiments.round5_ui_model.automation.run_batch_v2 import command,child_environment
from experiments.round5_ui_model.automation.continue_batch import audit_events
from . import core


def utc(): return datetime.now(timezone.utc).isoformat()


def configured_command(work,last):
    executable=shutil.which('codex')
    if not executable: raise RuntimeError('Official Codex CLI unavailable')
    args=command(executable,work,last,core.MODEL,core.EFFORT)
    disabled=(core.WORKSPACE/'experiments/round5_ai_judge_review/preflight/disabled_skills_override.txt').read_text(encoding='utf-8')
    return args[:-1]+['-c',disabled,'--output-schema',str(work/'schema.json'),'-']


def preflight():
    root=core.ROOT/'preflight';executable=shutil.which('codex')
    if not executable: raise RuntimeError('CLI missing')
    for name,argv in [('version',['--version']),('help',['exec','--help']),('login',['login','status'])]:
        result=subprocess.run([executable,*argv],capture_output=True,timeout=30)
        (root/(name+'_stdout.txt')).write_bytes(result.stdout);(root/(name+'_stderr.txt')).write_bytes(result.stderr)
        if result.returncode or (name=='login' and b'Logged in using ChatGPT' not in result.stdout+result.stderr):
            raise RuntimeError('CLI authorization/capability unavailable: '+name)
    work=Path(tempfile.mkdtemp(prefix='aic_f01_probe_'))
    public=core.read(core.ROOT/'inputs/R01.json')
    (work/'prompt.md').write_text(core.prompt(public,'S1'),encoding='utf-8')
    (work/'schema.json').write_bytes((core.ROOT/'schema.json').read_bytes())
    full=configured_command(work,work.parent/'unused.json')
    config=[]
    for i,arg in enumerate(full):
        if arg=='-c': config+=['-c',full[i+1]]
    config+=['-c','model='+json.dumps(core.MODEL)]
    argv=[executable,*config,'debug','prompt-input',core.prompt(public,'S1')]
    env,removed=child_environment()
    result=subprocess.run(argv,cwd=work,env=env,capture_output=True,timeout=60)
    (root/'rendered_prompt_input.json').write_bytes(result.stdout)
    (root/'render_stderr.log').write_bytes(result.stderr)
    text=result.stdout.decode('utf-8',errors='replace')
    probe={'exit_code':result.returncode,'skills_catalog_header_count':text.count('### Available skills'),
        'SKILL_md_mentions':text.count('SKILL.md'),'full_OS_isolation':False,
        'exact_server_context_attested':False,'work':str(work),'removed_environment_names':removed,
        'argv':argv,'known_local_skills_explicitly_disabled':True}
    dump(root/'render_audit.json',probe)
    if result.returncode or probe['skills_catalog_header_count'] or probe['SKILL_md_mentions']:
        raise RuntimeError('Local prompt rendering has unisolated skills or failed')
    return probe


def generate(public,arm,artifact,prompt_path=None):
    artifact=Path(artifact)
    artifact.mkdir(parents=True,exist_ok=False)
    work=Path(tempfile.mkdtemp(prefix='aic_f01_'+arm+'_'))
    raw_prompt=Path(prompt_path).read_bytes() if prompt_path else core.prompt(public,arm).encode('utf-8')
    (work/'prompt.md').write_bytes(raw_prompt);(artifact/'prompt.md').write_bytes(raw_prompt)
    (work/'schema.json').write_bytes((core.ROOT/'schema.json').read_bytes())
    last=work.parent/(work.name+'_last.json')
    args=configured_command(work,last);env,removed=child_environment()
    start=utc();timer=time.perf_counter();timeout=False
    dump(artifact/'invocation.json',{'argv':args,'work':str(work),'start_utc':start,
        'prompt_sha256':digest(artifact/'prompt.md'),'work_files_before':['prompt.md','schema.json'],
        'removed_environment_names':removed,'parent_context_supplied':False,'gold_supplied':False,
        'prior_model_answers_supplied':False,'OS_deny_read_established':False})
    with (artifact/'events.jsonl').open('xb') as out,(artifact/'stderr.log').open('xb') as err:
        process=subprocess.Popen(args,cwd=work,env=env,stdin=subprocess.PIPE,stdout=out,stderr=err)
        try: process.communicate(raw_prompt,timeout=core.TIMEOUT)
        except subprocess.TimeoutExpired: timeout=True;process.kill();process.communicate()
    raw=last.read_bytes() if last.exists() else b''
    (artifact/'raw_response.json').write_bytes(raw)
    audit=audit_events((artifact/'events.jsonl').read_bytes());dump(artifact/'events_audit.json',audit)
    decoded=raw.decode('utf-8-sig',errors='replace')
    match=bool(audit['final_messages']) and decoded.rstrip('\r\n')==audit['final_messages'][-1].rstrip('\r\n')
    files=sorted(p.name for p in work.iterdir() if p.is_file())
    success=(process.returncode==0 and bool(raw) and audit['completed_turns']==1 and not audit['errors'] and
        not audit['parse_errors'] and not audit['tool_activity'] and match and files==['prompt.md','schema.json'])
    parsed=None;parse_error=None
    if raw:
        try: parsed=json.loads(decoded)
        except json.JSONDecodeError as exc: parse_error=str(exc)
    checked=core.validate_output(parsed,public) if parsed else {'structural_valid':False,'display_safe':False,
        'issues':['unparsed_or_empty_output'],'requests':[],'needs_human_review':True}
    dump(artifact/'validation.json',checked)
    metadata={'arm':arm,'model_requested':core.MODEL,'thinking':core.EFFORT,'backend_snapshot':None,
        'start_utc':start,'end_utc':utc(),'elapsed_seconds':round(time.perf_counter()-timer,4),
        'exit_code':process.returncode,'timeout':timeout,'raw_bytes':len(raw),
        'raw_sha256':digest(artifact/'raw_response.json'),'prompt_sha256':digest(artifact/'prompt.md'),
        'thread_ids':audit['thread_ids'],'completed_turns':audit['completed_turns'],'event_output_match':match,
        'observed_tool_calls':len(audit['tool_activity']),'warnings':len(audit.get('warnings',[])),
        'usage':audit['usage'],'CLI_success':bool(success),'parse_error':parse_error,
        'structural_valid':checked['structural_valid'],'work_files_after':files,
        'normal_product_login':True,'first_response_only':True,'full_OS_isolation':False,
        'exact_server_context_attested':False,'cost_currency':None,'allocated_subscription_cost':None,
        'provenance':'real_official_Codex_CLI; no_model_self_score',
        'data_origin':public['data_origin']}
    dump(artifact/'metadata.json',metadata)
    print(json.dumps({'artifact':artifact.name,'success':metadata['CLI_success'],'structured':metadata['structural_valid'],
        'elapsed_seconds':metadata['elapsed_seconds'],'raw_bytes':len(raw)},ensure_ascii=True),flush=True)
    return metadata,parsed,checked


def batch():
    core.verify_freeze();preflight()
    results=[]
    for n in range(1,9):
        sid=f'R{n:02d}';arms=['S1','S2'] if n%2 else ['S2','S1']
        public=core.read(core.ROOT/'inputs'/(sid+'.json'))
        artifacts=[core.ROOT/'responses'/(arm+'_'+sid) for arm in arms]
        if any(p.exists() for p in artifacts): raise FileExistsError('First attempts already exist; do not rerun batch')
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(generate,public,arm,path,core.ROOT/'prompts'/(arm+'_'+sid+'.md')) for arm,path in zip(arms,artifacts)]
            pair=[f.result()[0] for f in futures]
        results.extend(pair)
        thread_ids=[t for r in results for t in r['thread_ids']]
        blocked=any(not r['CLI_success'] for r in pair) or len(thread_ids)!=len(set(thread_ids))
        dump(core.ROOT/'results/batch_progress.json',{'attempted':len(results),'planned':16,'blocked':blocked,
            'results':results,'not_attempted':16-len(results),'no_retry':True})
        if blocked: break
    dump(core.ROOT/'results/batch_summary.json',{'planned':16,'attempted':len(results),
        'CLI_successful':sum(r['CLI_success'] for r in results),'structured':sum(r['structural_valid'] for r in results),
        'results':results,'not_attempted':16-len(results),'no_retry':True})


if __name__=='__main__': batch()
