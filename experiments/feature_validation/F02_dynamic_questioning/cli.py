"""One-command genuine interaction; real-user records separate from simulations."""
import argparse
from datetime import datetime,timezone
import time
import uuid
from experiments.common import dump
from . import core,baseline,native
from .run import teacher_entry


def main():
    p=argparse.ArgumentParser();p.add_argument('--case',choices=['C01','C02','C03'])
    p.add_argument('--arm',choices=['S0','S1'],default='S1');p.add_argument('--scripted-smoke',action='store_true')
    args=p.parse_args();core.verify()
    cid=args.case or input('选择案例 C01/C02/C03 [C01]：').strip() or 'C01'
    if cid not in ['C01','C02','C03']:raise ValueError('Unknown case')
    case=core.read(core.ROOT/'cases'/(cid+'.json'))
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'_'+uuid.uuid4().hex[:8]
    folder=core.ROOT/'user_runs'/stamp;folder.mkdir(parents=True,exist_ok=False)
    origin='scripted_engineering_smoke' if args.scripted_smoke else 'interactive_user_unverified_role'
    record={'data_origin':origin,'not_formal_simulation_sample':True,'case_id':cid,'arm':args.arm,
        'history':[],'turns':[],'feedback':{'on_topic':None,'understood_intent':None,'want_to_continue':None},
        'elapsed_seconds':None,'termination':None,'exception':None}
    print(case['statement']);print(case['input_contract']);print(case['source'])
    for version,data in case['versions'].items():print(version+'：\n'+data['source'])
    for row in case['evidence']:print(row)
    start=time.perf_counter()
    try:
        if args.arm=='S1':native.install_command()
        for turn in range(1,4):
            value=core.public(case,record['history'],origin);timer=time.perf_counter()
            if args.arm=='S1':item=native.generate(value,folder/('U'+stamp+'_T'+str(turn)))
            else:
                output=baseline.decide(value)
                item={'output':output,'checks':core.validate(output,value),'metadata':None}
            record['turns'].append({'turn':turn,**item,'elapsed_seconds':time.perf_counter()-timer})
            dump(folder/'interaction.json',record)
            if not item['checks']['display_safe'] or args.arm=='S1' and not item['metadata']['CLI_success']:
                record['termination']='invalid_or_failed_output';print('原始失败已保存，停止展示教学内容。');break
            output=item['output'];record['history'].append(teacher_entry(output,item['checks']))
            print('\n动作：'+core.ACTION_ZH[output['next_action']]);print(output['student_message'])
            print('依据：'+output['decision_basis']);print('尚不确定：'+'；'.join(output['uncertainties']))
            for checked in item['checks']['requests']:print('独立执行：',checked)
            end=core.termination(output,turn)
            if end!='continue':record['termination']=end;break
            answer=input('你的回答（/quit退出）：')
            if answer.strip()=='/quit':record['termination']='user_quit';break
            record['history'].append({'role':'student','text':answer,'data_origin':origin})
        if record['termination'] is None:record['termination']='budget_limited'
        for key,label in [('on_topic','回复是否切题'),('understood_intent','是否理解系统意图'),('want_to_continue','是否希望继续使用')]:
            text=input(label+'（是/否/留空）：')
            record['feedback'][key]={'是':True,'否':False}.get(text.strip())
    except (EOFError,KeyboardInterrupt) as exc:record['exception']=type(exc).__name__
    except Exception as exc:
        record['exception']=type(exc).__name__+': '+str(exc);raise
    finally:
        record['elapsed_seconds']=round(time.perf_counter()-start,4)
        dump(folder/'interaction.json',record);print('记录：'+str(folder))


if __name__=='__main__':main()
