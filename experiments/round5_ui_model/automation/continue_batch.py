"""Append audit correction and continue unattempted prompts; never regenerate existing model replies."""
import argparse
import json
import shutil
from pathlib import Path
from experiments.common import digest,dump
from experiments.round5_ui_model.storage import ROOT,read,verify_freeze,verify_history
from experiments.round5_ui_model.automation import run_batch_v2 as base

_audit=base.audit_events
_command=base.command


def audit_events(raw):
    audit=_audit(raw)
    warnings=[];tools=[];errors=[]
    for entry in audit['tool_activity']:
        if entry['item'].get('type')=='error':
            warnings.append(entry)
        else:
            tools.append(entry)
    for entry in audit['errors']:
        if entry.get('type')=='error' and str(entry.get('message','')).startswith('Reconnecting...'):
            warnings.append(entry)
        else:
            errors.append(entry)
    return {**audit,'tool_activity':tools,'errors':errors,'warnings':warnings}


def command(*args):
    original=_command(*args)
    # Documented provider transport. No new endpoint, API credentials or model parameters.
    extra=[]
    for key,value in [('name','OpenAI'),('requires_openai_auth',True),('wire_api','responses'),('supports_websockets',False)]:
        extra+=['-c','model_providers.openai.'+key+'='+json.dumps(value)]
    return original[:-1]+extra+['-']


def qualified_record(run,slot):
    attempt=run/slot
    record=read(attempt/'import_record.json');old=read(attempt/'result.json')
    audit=audit_events((attempt/'events.jsonl').read_bytes())
    raw=Path(record['raw_path']).read_bytes()
    if digest(Path(record['raw_path']))!=record['raw_sha256'] or digest(attempt/'last_message.md')!=record['raw_sha256']:
        raise ValueError('Original bytes changed')
    text=raw.decode('utf-8-sig')
    match=bool(audit['final_messages']) and text.rstrip('\r\n')==audit['final_messages'][-1].rstrip('\r\n')
    success=old['exit_code']==0 and bool(raw) and audit['completed_turns']==1 and not audit['errors'] and not audit['parse_errors'] and match
    corrected_meta={**record['metadata'],'failed':not success,'truncated':not success and bool(raw),
                    'observed_tool_activity_count':len(audit['tool_activity']),
                    'audit_corrected_from_original':True,'audit_correction_reason':'item.error setup warnings and reconnect notices are not tool calls or fatal completed-turn failures',
                    'local_skill_loading_observed':True,'custom_instructions_isolated':None,
                    'contamination_risk':True,'backend_version':None,
                    'transport':'CLI HTTPS; S1_01 reached HTTPS after recorded WebSocket fallback',
                    'model_selection_basis':'explicit gpt-6.1-sol CLI option; exact backend version not attested'}
    qualified={**record,'metadata':corrected_meta,'archive_primary_flag_unchanged':record['primary'],
               'qualified_first_model_response':True,'original_import_record':str(attempt/'import_record.json')}
    result={**old,'success':success,'tool_activity':len(audit['tool_activity']),'warnings':len(audit['warnings']),
            'event_output_match':match,'qualification':'first real model response, all old records preserved'}
    correction={'result':result,'record':qualified,'event_audit':audit,'history':verify_history()}
    target=attempt/'audit_correction_v3.json'
    if not target.exists():
        dump(target,correction)
    return correction


def verify_implementation():
    manifest=read(base.HERE/'continuation_manifest_v3.json')
    for name,sha in manifest['sha256'].items():
        if digest(base.HERE/name)!=sha:
            raise ValueError('Continuation implementation changed')
    base.verify_runner()


def save_selection(run):
    selected={}
    results=[]
    for slot in base.ORDER:
        if (run/slot/'import_record.json').exists():
            correction=qualified_record(run,slot)
            selected[slot]=correction['record'];results.append(correction['result'])
    snapshot={'selected':selected,'results':results,'attempted':len(results),'successful':sum(r['success'] for r in results),
              'distinct_threads':len({r['thread_id'] for r in results if r['thread_id']}),'expected':16,
              'selection_basis':'first actual model thread per slot; zero-thread configuration failure retained separately',
              'full_OS_isolation':False,'custom_instruction_context_attested':False}
    # This is an explicitly versioned selection snapshot; original archive primary flags stay intact.
    target=run/f'qualified_selection_{len(results):02d}.json'
    if not target.exists():
        dump(target,snapshot)
    return snapshot


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run-dir',type=Path,required=True)
    args=parser.parse_args();verify_implementation()
    run=args.run_dir.resolve();batch=read(run/'batch.json')
    clean=Path(batch['clean_root']);executable=shutil.which('codex')
    if not executable:
        raise RuntimeError('CLI unavailable')
    original=qualified_record(run,'S1_01')
    if not original['result']['success'] or original['result']['tool_activity']:
        raise RuntimeError('S1_01 incomplete or tool use: stop without regenerating')
    base.audit_events=audit_events;base.command=command
    already=[slot for slot in base.ORDER if (run/slot/'result.json').exists()]
    print(json.dumps({'qualified_existing':already,'model':'gpt-6.1-sol','effort':'xhigh','transport':'official CLI HTTPS'},ensure_ascii=False),flush=True)
    for slot in base.ORDER:
        if (run/slot/'result.json').exists():
            continue
        result=base.run_one(executable,run,clean,slot,'gpt-6.1-sol','xhigh')
        snapshot=save_selection(run)
        clean_result=result['success'] and result['tool_activity']==0 and result['work_files_after']==['prompt.md']
        if not clean_result or snapshot['distinct_threads']!=snapshot['attempted']:
            dump(run/('continuation_stop_'+slot+'.json'),{'result':result,'no_retry':True})
            break
        if slot=='S2_01':
            print(json.dumps({'pilot_qualified':True,'two_distinct_threads':snapshot['distinct_threads']==2,
                              'collector_archive_records':2,'remaining_prompts':14},ensure_ascii=False),flush=True)
    snapshot=save_selection(run)
    dump(run/'final_automation_summary.json',{k:v for k,v in snapshot.items() if k!='selected'})
    print(json.dumps({'attempted':snapshot['attempted'],'successful':snapshot['successful'],
                      'distinct_threads':snapshot['distinct_threads'],'all_outputs_preserved':True},ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
