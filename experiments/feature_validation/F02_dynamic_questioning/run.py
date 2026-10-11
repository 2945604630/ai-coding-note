"""Frozen, first-attempt finite dialogues with same-history shadow baseline."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from threading import Event,Lock
from experiments.common import dump,digest
from . import core,baseline,simulator,native

BLOCKED=Event()
LOCK=Lock()


def teacher_entry(output,checks):
    return {'role':'teacher','output':output,'independent_execution':checks.get('requests',[])}


def dialogue(path,arm,initial=None):
    case=core.read(core.ROOT/'cases'/(path['case_id']+'.json'))
    history=[];turns=[];student_turn=0;sid=path['scenario_id']
    end='uncompleted';problem=None
    for turn in range(1,4):
        value=core.public(case,history,'frozen_simulated_student')
        if arm=='S1':
            if turn==1:item=initial
            else:
                if BLOCKED.is_set():end='blocked_not_attempted';break
                item=native.generate(value,core.ROOT/'responses'/f'S1_{sid}_T{turn}')
            shadow=baseline.decide(value);shadow_check=core.validate(shadow,value)
        else:
            output=baseline.decide(value)
            item={'output':output,'checks':core.validate(output,value),'metadata':None,'artifact':None}
            shadow=shadow_check=None
        output=item['output']
        entry={'turn':turn,'public_input':value,'input_sha256':None,**item,
            'S0_same_history':shadow,'S0_checks':shadow_check}
        turns.append(entry)
        if arm=='S1' and not item['metadata']['CLI_success']:
            BLOCKED.set();end='CLI_failure';break
        if not item['checks']['display_safe']:
            end='invalid_output';problem=item['checks']['issues'];break
        history.append(teacher_entry(output,item['checks']))
        end=core.termination(output,turn)
        if end!='continue':break
        selected=simulator.choose(path['banks'][student_turn],output)
        entry['frozen_response_selection']=selected
        if not selected['compatible']:end='path_incompatible';problem=selected['reason'];break
        history.append({'role':'student','text':selected['text'],'data_origin':'frozen_simulated_student',
            'frozen_bank_slot':student_turn,'frozen_reply_index':selected['reply_index']})
        student_turn+=1
    result={'scenario_id':sid,'arm':arm,'data_origin':'frozen_simulated_student','turns':turns,'history':history,
        'termination':end,'problem':problem,'student_replies_used':student_turn,'max_teacher_turns':3,
        'needs_human_review':True}
    filename=core.ROOT/'results'/f'{arm}_{sid}.json'
    with LOCK:
        if filename.exists():raise FileExistsError('No rerun of formal paths')
        dump(filename,result)
    print(arm,sid,end,flush=True)
    return result


def batch():
    core.verify();native.preflight();native.install_command()
    paths=core.read(core.ROOT/'gold/response_bank.json')
    for p in paths:dialogue(p,'S0')
    initials={}
    for cid in ['C01','C02','C03']:
        value=core.public(core.read(core.ROOT/'cases'/(cid+'.json')),[],'frozen_simulated_student')
        initials[cid]=native.generate(value,core.ROOT/'responses'/('S1_'+cid+'_FIRST'))
        if not initials[cid]['metadata']['CLI_success']:
            BLOCKED.set();break
    results=[]
    if not BLOCKED.is_set():
        with ThreadPoolExecutor(max_workers=2) as pool:
            for result in pool.map(lambda p:dialogue(p,'S1',initials[p['case_id']]),paths):results.append(result)
    dump(core.ROOT/'results/batch_summary.json',{'initials':initials,'completed_paths':len(results),
        'blocked':BLOCKED.is_set(),'no_retries':True,'first_question_unique_count':len(initials),
        'max_planned_calls':27,'paths':[{k:r[k] for k in ['scenario_id','termination','student_replies_used']} for r in results]})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['batch','preflight'])
    mode=parser.parse_args().mode
    batch() if mode=='batch' else native.preflight()
