"""Run original prompts via official authenticated CLI. No API/credential extraction or retries."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from experiments.common import digest, dump
from experiments.round5_ui_model.storage import ROOT, WORKSPACE, read, verify_freeze, verify_history
from experiments.round5_ui_model.collection import archive_response
from experiments.round5_ui_model.collect import primary_records, update_index

HERE=Path(__file__).resolve().parent
ORDER=[f'S{arm}_{n:02d}' for n in range(1,9) for arm in ((1,2) if n%2 else (2,1))]
DISABLED=['shell_tool','unified_exec','shell_snapshot','apps','plugins','remote_plugin','hooks','memories',
          'multi_agent','multi_agent_v2','skill_mcp_dependency_install','skill_search','browser_use',
          'browser_use_external','browser_use_full_cdp_access','computer_use','in_app_browser',
          'image_generation','view_image','code_mode','code_mode_host']


def utc():
    return datetime.now(timezone.utc).isoformat()


def child_environment():
    # Names only are examined. Credentials are never read or printed.
    removed=[key for key in os.environ if (key.startswith('CODEX_') and key!='CODEX_HOME') or
             key in {'OPENAI_API_KEY','REPLICATE_API_TOKEN','REPLICATE_API_KEY'}]
    return {key:value for key,value in os.environ.items() if key not in removed},removed


def command(executable,work,last_message,model,effort):
    args=[executable,'exec','--ignore-user-config','--ignore-rules','--strict-config','--ephemeral',
          '--skip-git-repo-check','--json','--color','never','--sandbox','read-only',
          '--model',model,'--cd',str(work),'--output-last-message',str(last_message)]
    values={'model_reasoning_effort':effort,'model_provider':'openai','forced_login_method':'chatgpt',
            'approval_policy':'never','web_search':'disabled','project_doc_max_bytes':0,
            'personality':'none'}
    values.update({'features.'+name:False for name in DISABLED})
    values['features.skip_host_skill_discovery']=True
    for key,value in values.items():
        args+=['-c',key+'='+json.dumps(value,ensure_ascii=False)]
    return args+['-']


def prepare_work(source,work):
    work=Path(work);work.mkdir(parents=True,exist_ok=False)
    target=work/'prompt.md';target.write_bytes(Path(source).read_bytes())
    return target


def ensure_unused(attempt,response):
    if Path(attempt).exists() or Path(response).exists():
        raise FileExistsError('Existing attempt/response must be preserved; no regeneration')


def audit_events(raw):
    threads=[];messages=[];tools={};usage=None;completed=0;errors=[];parse_errors=[];types=[]
    for n,line in enumerate(raw.splitlines(),1):
        if not line.strip():
            continue
        try:
            event=json.loads(line)
        except (json.JSONDecodeError,UnicodeDecodeError):
            parse_errors.append(n);continue
        kind=event.get('type');types.append(kind)
        if kind=='thread.started':
            threads.append(event.get('thread_id'))
        if kind=='turn.completed':
            completed+=1;usage=event.get('usage')
        if kind in {'error','turn.failed'}:
            errors.append(event)
        item=event.get('item',{})
        if item.get('type')=='agent_message' and kind=='item.completed':
            messages.append(item.get('text',''))
        if item and item.get('type') not in {'agent_message','reasoning','plan'}:
            key=item.get('id',str(n));tools[key]={'event':kind,'item':item}
    return {'thread_ids':threads,'completed_turns':completed,'final_messages':messages,
            'tool_activity':list(tools.values()),'usage':usage,'errors':errors,
            'parse_errors':parse_errors,'event_types':types}


def verify_runner():
    frozen=read(HERE/'runner_manifest_v2.json')
    for name,sha in frozen['sha256'].items():
        if digest(HERE/name)!=sha:
            raise ValueError('Automation implementation changed: '+name)
    verify_freeze();verify_history()


def preflight(executable,run):
    output={}
    for name,args in [('version',['--version']),('exec_help',['exec','--help']),('login',['login','status'])]:
        result=subprocess.run([executable,*args],capture_output=True,timeout=30)
        (run/(name+'_stdout.txt')).write_bytes(result.stdout)
        (run/(name+'_stderr.txt')).write_bytes(result.stderr)
        output[name]={'exit_code':result.returncode,'text':(result.stdout+result.stderr).decode('utf-8',errors='replace').strip()}
    if output['login']['exit_code']!=0 or 'Logged in using ChatGPT' not in output['login']['text']:
        raise RuntimeError('CLI ChatGPT authorization unavailable; run codex login normally')
    if output['version']['exit_code'] or output['exec_help']['exit_code']:
        raise RuntimeError('CLI unavailable')
    expected=['--json','--output-last-message','--ignore-user-config','--ephemeral','--strict-config']
    if any(flag not in output['exec_help']['text'] for flag in expected):
        raise RuntimeError('Installed CLI lacks required output/isolation features')
    output['executable']=str(Path(executable).resolve());output['executable_sha256']=digest(executable)
    output['model_requested']='gpt-6.1-sol';output['reasoning_effort']='xhigh'
    output['native_windows_boundary']='not_verified; sandbox windows reported helper_unknown_error/setup refresh errors'
    output['credentials_extracted']=False;output['os_level_blind_test']=False
    dump(run/'preflight.json',output)
    return output


def run_one(executable,run,clean_root,slot,model,effort):
    attempt=run/slot
    response_root=ROOT/'responses'/run.name;response_root.mkdir(exist_ok=True)
    response=response_root/(slot+'.md')
    ensure_unused(attempt,response)
    attempt.mkdir()
    source=ROOT/'prompts'/(slot+'.md')
    work=clean_root/slot/'work';local_prompt=prepare_work(source,work)
    last=clean_root/slot/'last_message.md'
    args=command(executable,work,last,model,effort)
    env,removed=child_environment()
    start=utc();clock=time.perf_counter();timed_out=False
    dump(attempt/'invocation.json',{'slot':slot,'argv':args,'stdin_prompt_sha256':digest(source),
                                 'work':str(work),'work_files_before':['prompt.md'],
                                 'removed_environment_variable_names':removed,'start_utc':start})
    (attempt/'prompt.md').write_bytes(source.read_bytes())
    exit_code=None
    with (attempt/'events.jsonl').open('xb') as out,(attempt/'stderr.log').open('xb') as err:
        process=subprocess.Popen(args,cwd=work,env=env,stdin=subprocess.PIPE,stdout=out,stderr=err)
        try:
            process.communicate(input=source.read_bytes(),timeout=360)
        except subprocess.TimeoutExpired:
            timed_out=True;process.kill();process.communicate()
        exit_code=process.returncode
    end=utc();elapsed=time.perf_counter()-clock
    audit=audit_events((attempt/'events.jsonl').read_bytes());dump(attempt/'event_audit.json',audit)
    raw=last.read_bytes() if last.exists() else b''
    (attempt/'last_message.md').write_bytes(raw)
    message=audit['final_messages'][-1] if audit['final_messages'] else None
    try:
        byte_match=message is not None and raw.decode('utf-8-sig').rstrip('\r\n')==message.rstrip('\r\n')
    except UnicodeDecodeError:
        byte_match=False
    failed=exit_code!=0 or not raw or audit['completed_turns']!=1 or bool(audit['errors']) or bool(audit['parse_errors']) or not byte_match
    files_after=sorted(p.relative_to(work).as_posix() for p in work.rglob('*') if p.is_file())
    config={'product':'Codex CLI','model_label':model,'thinking_setting':effort,
            'model_selection_basis':'explicit --model + authenticated CLI catalog; exact backend snapshot unknown',
            'backend_version':None,'tools':'disabled_by_CLI_config; observed_activity_recorded_separately',
            'fresh_context':len(audit['thread_ids'])==1,'memory_isolated':True,'custom_instructions_isolated':True,
            'prompt_hash_matches':digest(source)==digest(local_prompt)==digest(attempt/'prompt.md'),
            'contamination_risk':True,'file_isolation':'not_OS_verified; empty workdir and no reference material supplied',
            'isolation_basis':'new exec/ephemeral; memory off; AGENTS budget zero; no parent research transcript',
            'managed_prompt_context_attested':False,
            'failed':failed,'truncated':timed_out or (bool(raw) and audit['completed_turns']!=1),
            'elapsed_seconds':round(elapsed,4),'start_utc':start,'end_utc':end,'exit_code':exit_code,
            'token_usage':audit['usage'],'subscription_allocated_cost':None,
            'thread_id':audit['thread_ids'][0] if len(audit['thread_ids'])==1 else None,
            'observed_tool_activity_count':len(audit['tool_activity']),'work_files_after':files_after,
            'prompt_copy_verification_basis':'exact bytes fed to stdin by subprocess; archived SHA equality',
            'expected_prompt_sha256':digest(source),'CLI_output_event_text_matches':byte_match,
            'provenance':'real_official_codex_exec_with_ChatGPT_login; not a mock',
            'original_cli_last_message_sha256':hashlib.sha256(raw).hexdigest(),
            'execution_artifacts':str(attempt.resolve()),'notes':'OS boundary unverified: exploratory comparison only'}
    # Empty output is a preserved failure, never replaced by an invented answer.
    response.write_bytes(raw);dump(response_root/(slot+'.meta.json'),config)
    archived=archive_response(response,ROOT/'responses/archive',slot,config)
    dump(attempt/'metadata.json',config);dump(attempt/'import_record.json',archived)
    result={'slot':slot,'success':not failed,'response_bytes':len(raw),'thread_id':config['thread_id'],
            'elapsed_seconds':config['elapsed_seconds'],'exit_code':exit_code,
            'tool_activity':len(audit['tool_activity']),'work_files_after':files_after,
            'raw_sha256':digest(response),'archived_sha256':archived['raw_sha256'],
            'independent_context':config['fresh_context'],'isolation_limit':True,
            'event_output_match':byte_match,'artifact':str(attempt)}
    dump(attempt/'result.json',result)
    print(json.dumps(result,ensure_ascii=False),flush=True)
    update_index()
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--pilot',action='store_true');mode.add_argument('--remaining',action='store_true')
    parser.add_argument('--run-dir',type=Path)
    args=parser.parse_args();verify_runner()
    executable=shutil.which('codex')
    if not executable:
        raise RuntimeError('Codex CLI unavailable')
    if args.pilot:
        old_records=list(primary_records(ROOT/'responses/archive').values())
        if any(record['raw_bytes'] or record['metadata'].get('thread_id') or not record['metadata'].get('failed') for record in old_records):
            raise RuntimeError('Actual prior model attempt already present; do not regenerate')
        if any(path.stat().st_size for path in (ROOT/'responses').glob('S[12]_0[1-8].md')):
            raise RuntimeError('Actual prior raw output present; do not regenerate')
        stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        run=ROOT/'results'/('cli_automation_'+stamp);run.mkdir()
        clean=Path(tempfile.mkdtemp(prefix='aic_round5_codex_'))
        pre=preflight(executable,run)
        dump(run/'batch.json',{'created_utc':utc(),'order':ORDER,'model':'gpt-6.1-sol','effort':'xhigh',
                              'clean_root':str(clean),'runner_manifest_sha256':digest(HERE/'runner_manifest_v2.json'),
                              'old_freeze_sha256':digest(ROOT/'freeze_manifest.json'),'preflight':pre,
                              'response_collection_root':str(ROOT/'responses'/run.name),
                              'preserved_pre_inference_records':old_records,
                              'parent_research_context_transferred':False,'full_OS_isolation':False})
        selected=ORDER[:2]
        print(json.dumps({'run_dir':str(run),'mode':'pilot','planned':selected},ensure_ascii=False),flush=True)
    else:
        if not args.run_dir:
            raise ValueError('--remaining requires existing --run-dir')
        run=args.run_dir.resolve();batch=read(run/'batch.json');clean=Path(batch['clean_root'])
        if batch['runner_manifest_sha256']!=digest(HERE/'runner_manifest_v2.json'):
            raise ValueError('Runner changed after pilot')
        pilot=[read(run/slot/'result.json') for slot in ORDER[:2]]
        if not all(p['success'] and p['event_output_match'] and p['tool_activity']==0 and p['work_files_after']==['prompt.md'] for p in pilot):
            raise RuntimeError('Pilot not clean/successful; preserve failures and stop')
        if len({p['thread_id'] for p in pilot})!=2:
            raise RuntimeError('Pilot reused a thread; stop')
        selected=ORDER[2:]
    complete=[]
    for slot in selected:
        result=run_one(executable,run,clean,slot,'gpt-6.1-sol','xhigh');complete.append(result)
        prior=[read(path) for path in run.glob('S[12]_0[1-8]/result.json')]
        ids=[p['thread_id'] for p in prior if p['thread_id']]
        if not result['success'] or result['tool_activity'] or result['work_files_after']!=['prompt.md'] or len(ids)!=len(set(ids)):
            dump(run/('stop_'+slot+'.json'),{'reason':'generation/output/isolation/tool/session failure; no automatic retry','result':result})
            print(json.dumps({'stopped_at':slot,'retry_performed':False},ensure_ascii=False),flush=True)
            break
    records=[read(path) for path in run.glob('S[12]_0[1-8]/result.json')]
    snapshot={'results':records,'planned':16,'attempted':len(records),'successful':sum(r['success'] for r in records),
              'independent_thread_ids':len({r['thread_id'] for r in records if r['thread_id']}),
              'phase':'pilot' if args.pilot else 'remaining','history':verify_history(),'freeze':verify_freeze()['version']}
    dump(run/('pilot_summary.json' if args.pilot else 'batch_summary.json'),snapshot)
    print(json.dumps({'run_dir':str(run),'attempted':snapshot['attempted'],'successful':snapshot['successful']},ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
