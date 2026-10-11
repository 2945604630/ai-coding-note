"""Official first-response-only CLI calls, with all artifacts in phase2."""
import argparse
import json
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from experiments.common import dump,digest
from .. import native
from . import engine as e


def preflight():
    root=e.ROOT/'preflight';root.mkdir(exist_ok=True)
    executable=shutil.which('codex')
    if not executable:raise RuntimeError('Official Codex CLI missing')
    for name,argv in [('version',['--version']),('help',['exec','--help']),('login',['login','status'])]:
        r=subprocess.run([executable,*argv],capture_output=True,timeout=30)
        (root/(name+'_stdout.txt')).write_bytes(r.stdout)
        (root/(name+'_stderr.txt')).write_bytes(r.stderr)
        if r.returncode or (name=='login' and b'Logged in using ChatGPT' not in r.stdout+r.stderr):
            raise RuntimeError('CLI unavailable or unauthorized: '+name)
    work=Path(tempfile.mkdtemp(prefix='aic_f01_p2_probe_'))
    raw=(e.ROOT/'prompts/S1_H01.md').read_bytes()
    (work/'prompt.md').write_bytes(raw)
    (work/'schema.json').write_bytes((e.PARENT/'schema.json').read_bytes())
    full=native.configured_command(work,work.parent/'unused.json')
    configs=[]
    for i,arg in enumerate(full):
        if arg=='-c':configs+=['-c',full[i+1]]
    configs+=['-c','model='+json.dumps(e.v1.MODEL)]
    argv=[executable,*configs,'debug','prompt-input',raw.decode('utf-8')]
    env,removed=native.child_environment()
    r=subprocess.run(argv,cwd=work,env=env,capture_output=True,timeout=60)
    (root/'rendered_prompt_input.json').write_bytes(r.stdout)
    (root/'render_stderr.log').write_bytes(r.stderr)
    text=r.stdout.decode('utf-8',errors='replace')
    probe={'exit_code':r.returncode,'skills_catalog_header_count':text.count('### Available skills'),
        'SKILL_md_mentions':text.count('SKILL.md'),'full_OS_isolation':False,
        'exact_server_context_attested':False,'removed_environment_names':removed,'argv':argv,
        'work':str(work),'known_local_skills_explicitly_disabled':True}
    dump(root/'render_audit.json',probe)
    if r.returncode or probe['skills_catalog_header_count'] or probe['SKILL_md_mentions']:
        raise RuntimeError('Local prompt rendering failed isolation audit')
    return probe


def generate(prompt_path,schema_path,artifact,role,public=None):
    artifact=Path(artifact);artifact.mkdir(parents=True,exist_ok=False)
    work=Path(tempfile.mkdtemp(prefix='aic_f01_p2_'+role+'_'))
    raw_prompt=Path(prompt_path).read_bytes()
    for base,content in [('prompt.md',raw_prompt),('schema.json',Path(schema_path).read_bytes())]:
        (work/base).write_bytes(content);(artifact/base).write_bytes(content)
    last=work.parent/(work.name+'_last.json')
    args=native.configured_command(work,last);env,removed=native.child_environment()
    start=native.utc();timer=time.perf_counter();timed_out=False
    dump(artifact/'invocation.json',{'argv':args,'work':str(work),'start_utc':start,
        'prompt_sha256':digest(artifact/'prompt.md'),'schema_sha256':digest(artifact/'schema.json'),
        'work_files_before':['prompt.md','schema.json'],'removed_environment_names':removed,
        'parent_context_supplied':False,'gold_supplied':False,'old_reviews_supplied':False,
        'peer_judgments_supplied':False,'OS_deny_read_established':False})
    with (artifact/'events.jsonl').open('xb') as out,(artifact/'stderr.log').open('xb') as err:
        process=subprocess.Popen(args,cwd=work,env=env,stdin=subprocess.PIPE,stdout=out,stderr=err)
        try:process.communicate(raw_prompt,timeout=e.v1.TIMEOUT)
        except subprocess.TimeoutExpired:
            timed_out=True;process.kill();process.communicate()
        except BaseException:
            process.kill();process.communicate();raise
    raw=last.read_bytes() if last.exists() else b''
    (artifact/'raw_response.json').write_bytes(raw)
    audit=native.audit_events((artifact/'events.jsonl').read_bytes());dump(artifact/'events_audit.json',audit)
    decoded=raw.decode('utf-8-sig',errors='replace')
    match=bool(audit['final_messages']) and decoded.rstrip('\r\n')==audit['final_messages'][0].rstrip('\r\n')
    files=sorted(p.name for p in work.iterdir() if p.is_file())
    success=(process.returncode==0 and bool(raw) and audit['completed_turns']==1 and
        len(audit['final_messages'])==1 and len(audit['thread_ids'])==1 and not audit['errors'] and
        not audit['parse_errors'] and not audit['tool_activity'] and match and files==['prompt.md','schema.json'])
    parsed=None;parse_error=None
    if raw:
        try:parsed=json.loads(decoded)
        except json.JSONDecodeError as exc:parse_error=str(exc)
    if public is not None:
        checked=e.v1.validate_output(parsed,public) if isinstance(parsed,dict) else {
            'structural_valid':False,'display_safe':False,'issues':['unparsed_or_empty_output'],
            'requests':[],'needs_human_review':True}
    else:
        checked={'structural_valid':isinstance(parsed,dict),'needs_human_review':True,
            'semantic_score_certified':False}
    dump(artifact/'validation.json',checked)
    metadata={'role':role,'model_requested':e.v1.MODEL,'thinking':e.v1.EFFORT,'backend_snapshot':None,
        'start_utc':start,'end_utc':native.utc(),'elapsed_seconds':round(time.perf_counter()-timer,4),
        'exit_code':process.returncode,'timeout':timed_out,'raw_bytes':len(raw),
        'raw_sha256':digest(artifact/'raw_response.json'),'prompt_sha256':digest(artifact/'prompt.md'),
        'thread_ids':audit['thread_ids'],'completed_turns':audit['completed_turns'],
        'event_output_match':match,'observed_tool_calls':len(audit['tool_activity']),
        'warnings':len(audit.get('warnings',[])),'usage':audit['usage'],'CLI_success':bool(success),
        'parse_error':parse_error,'structural_valid':checked['structural_valid'],'work_files_after':files,
        'normal_product_login':True,'first_response_only':True,'full_OS_isolation':False,
        'exact_server_context_attested':False,'cost_currency':None,'allocated_subscription_cost':None,
        'provenance':'real_official_Codex_CLI; no_model_self_score',
        'data_origin':public['data_origin'] if public is not None else 'independent_AI_auxiliary_review'}
    dump(artifact/'metadata.json',metadata)
    print(json.dumps({'artifact':artifact.name,'success':metadata['CLI_success'],
        'structured':metadata['structural_valid'],'elapsed_seconds':metadata['elapsed_seconds'],
        'raw_bytes':len(raw)},ensure_ascii=True),flush=True)
    return metadata,parsed,checked


def teachers():
    e.verify();preflight();results=[];timer=time.perf_counter()
    for n,sid in enumerate(e.IDS,1):
        arms=['S1','S2'] if n%2 else ['S2','S1']
        public=e.v1.read(e.ROOT/'inputs'/(sid+'.json'))
        artifacts=[e.ROOT/'responses'/(arm+'_'+sid) for arm in arms]
        if any(p.exists() for p in artifacts):raise FileExistsError('First attempts exist; do not rerun')
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(generate,e.ROOT/'prompts'/(arm+'_'+sid+'.md'),
                e.PARENT/'schema.json',path,arm,public) for arm,path in zip(arms,artifacts)]
            pair=[f.result()[0] for f in futures]
        results.extend(pair)
        threads=[t for r in results for t in r['thread_ids']]
        blocked=any(not r['CLI_success'] for r in pair) or len(threads)!=len(set(threads))
        summary={'planned':24,'attempted':len(results),'CLI_successful':sum(r['CLI_success'] for r in results),
            'structured':sum(r['structural_valid'] for r in results),'blocked':blocked,
            'results':results,'not_attempted':24-len(results),'no_retry':True,
            'elapsed_wall_seconds':round(time.perf_counter()-timer,4)}
        dump(e.ROOT/'results/batch_progress.json',summary)
        if blocked:break
    dump(e.ROOT/'results/batch_summary.json',summary)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['teachers','preflight'])
    mode=parser.parse_args().mode
    teachers() if mode=='teachers' else preflight()
