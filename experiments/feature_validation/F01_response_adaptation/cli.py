"""One reply interaction; user/smoke traces never enter simulated formal batch."""
import argparse
import json
from datetime import datetime,timezone
from . import core,native
from experiments.common import dump


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',choices=['01','07'],default='01')
    parser.add_argument('--arm',choices=['S0','S1','S2'],default='S2')
    parser.add_argument('--scripted-smoke',action='store_true',help='Label piped developer smoke input, never a real student')
    args=parser.parse_args();core.verify_freeze()
    case=core.read(core.ROOT/'cases'/(args.case+'.json'))
    print(case['statement']);print(case['input_contract']);print(case['source'])
    for e in case['evidence']:
        print('可信运行证据:',json.dumps({'args':e['args'],'actual':e['value'],'expected':e['expected']},ensure_ascii=False))
    print('第一次追问:',case['teaching_question'])
    answer=input('你的回答> ').strip()
    if not answer: print('空回答：未调用模型。');return
    origin='scripted_smoke_not_real_student' if args.scripted_smoke else 'user_entered_reply_identity_unverified'
    public={'input_version':'F01_v1','data_origin':origin,'case':case,'previous_question':case['teaching_question'],'student_answer':answer}
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    path=core.ROOT/'user_runs'/stamp;path.mkdir()
    dump(path/'input.json',public)
    if args.arm=='S0':
        output=core.baseline(args.case,answer);checked=core.validate_output(output,public)
        dump(path/'S0_output.json',output);meta={'arm':'S0','CLI_success':True}
    else:
        print('正在通过官方Codex新会话取得首次回答，请等待。',flush=True)
        meta,output,checked=native.generate(public,args.arm,path/'model_call')
    dump(path/'interaction.json',{'input':public,'metadata':meta,'output':output,'checks':checked,
        'formal_simulated_batch':False,'real_learning_outcome_measured':False})
    if not meta['CLI_success'] or not checked['display_safe']:
        print('暂停判断，交给用户选择：输出未通过完整性或可执行事实检查。')
        print('保留的检查问题:',checked['issues'])
    else:
        print('下一步动作:',core.ACTION_ZH[output['next_action']])
        print('对回应的有限理解:',output['interpretation'])
        print('对学生展示:',output['student_message'])
        print('依据:',output['decision_basis'])
        print('尚未知:',json.dumps(output['uncertainties'],ensure_ascii=False))
        for r in checked['requests']:
            print('独立执行核验:',json.dumps(r,ensure_ascii=False))
        print('语义和教学适当性仍需人工复核。')
    print('交互记录:',str(path))


if __name__=='__main__':main()
