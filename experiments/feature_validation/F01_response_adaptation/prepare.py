"""One-time preparation, private labels never supplied to model sessions."""
import json
from datetime import datetime, timezone
from pathlib import Path
from experiments.common import digest,dump,oracle,valid_args
from experiments.runner import execute
from . import core

ANSWERS = [
 ('01','n=3时i只取1、2，s先1再3；题目还要加3。我能自己改，请别再让我列同一遍。'),
 ('01','我认为range(1,3)会取1、2、3。现在得3应该只是s最后被覆盖了。'),
 ('01','应该是3吧，循环那里可能要动一下。'),
 ('01','我没把右端点当作会进入循环的值；本来打算循环结束后再补最后那项，后来漏写了。先别把它当成我不懂range，我想自己试。'),
 ('07','题目要的是输入里最大的那个数，所以[-5,-2]应是-2。0不在这次输入里，额外参加了比较；我愿意自己改。'),
 ('07','最大值不能是负数，0作保底才安全，所以这题规范答案就该是0。'),
 ('07','0没问题吧？我有点说不清。'),
 ('07','我说的0是这段代码会打印的值，不是在说题目允许把0当最大值。为了专门检验这个区别，我想先用只含一个负数的输入走一遍，再自己改。')]
GOLD = [
 ('clear_understanding',['request_self_modification','suspend_for_choice'],'明确列出实际循环并区分题意；请求自己改，不再列同一遍。'),
 ('explicit_wrong_claim',['show_counterexample','continue_asking','tiered_hint'],'明说错误range序列；覆盖假说不符s+=，用追踪核对，不确诊持久误解。'),
 ('ambiguous',['clarify_meaning','continue_asking','suspend_for_choice'],'3可能是实际或规范；可能动循环不能证明理解，不得确定认知缺陷。'),
 ('self_reported_alternative_plan',['request_self_modification','suspend_for_choice'],'不认为端点进入循环；自述补末项计划未核验，但当前句子反对不懂range归因。'),
 ('clear_understanding',['request_self_modification','suspend_for_choice'],'正确-2、输入候选区别，愿意改；不能推长期掌握。'),
 ('explicit_wrong_claim',['show_counterexample','continue_asking','tiered_hint'],'明确把规范最大值限定非负；纠正当前陈述或合法负数反例，不确诊长期缺陷。'),
 ('ambiguous',['clarify_meaning','continue_asking','suspend_for_choice'],'0的对象和是否认可均不明；吧和说不清不是明确规范错误。'),
 ('prediction_specification_distinction',['show_counterexample','continue_asking'],'0是正确原程序预测，不是规范断言；请求先单负数核验，动作应尊重该请求。')]


def main():
    root=core.ROOT
    if (root/'freeze_manifest.json').exists(): raise FileExistsError('Preparation already frozen; preserve history')
    for folder in ['cases','inputs','gold','prompts','results','responses','user_runs','preflight','test_logs']:
        (root/folder).mkdir(exist_ok=True)
    old=core.WORKSPACE/'experiments/round5_ui_model'
    calls=[]
    questions={'01':'当n=3时，你原本预期循环变量i依次取哪些值？','07':'你在列表前添加0，原本是想解决什么问题？'}
    for cid in questions:
        case=core.read(old/'cases'/(cid+'.json'))
        for e in case['evidence']:
            if not valid_args(case['task'],e['args'],case['domain'])[0]: raise ValueError('Invalid reviewed evidence')
        actual=execute(case['source'],[e['args'] for e in case['evidence']])
        for e,row in zip(case['evidence'],actual):
            if row['status']!='ok' or row['value']!=e['value'] or oracle(case['task'],e['args'])!=e['expected']: raise ValueError('Old fact mismatch')
            calls.append(row)
        case['teaching_question']=questions[cid]
        case['question_provenance']='previous real S1 question only; prior explanation and repair not supplied'
        dump(root/'cases'/(cid+'.json'),case)
    for n,((cid,answer),(label,allowed,rationale)) in enumerate(zip(ANSWERS,GOLD),1):
        sid=f'R{n:02d}';case=core.read(root/'cases'/(cid+'.json'))
        public={'input_version':'F01_v1','data_origin':'simulated_student_reply','case':case,
            'previous_question':case['teaching_question'],'student_answer':answer}
        dump(root/'inputs'/(sid+'.json'),public)
        dump(root/'gold'/(sid+'.json'),{'scenario_id':sid,'case_id':cid,'private_marker':'F01_PRIVATE_'+sid,
            'expected_interpretation':label,'allowed_actions':allowed,'supported_facts':rationale,
            'not_supported':['long_term_mastery','persistent_misconception','independent_repair_success'],
            'repeated_question_forbidden':n in [1,4,5],
            'reference_origin':'author_review_of_simulated_reply; no independent human','needs_human_review':True})
        output=core.baseline(cid,answer)
        dump(root/'results'/('S0_'+sid+'.json'),{'output':output,'validation':core.validate_output(output,public),
            'elapsed_scope':'deterministic baseline includes controlled verification; not model latency'})
        for arm in ['S1','S2']:
            (root/'prompts'/(arm+'_'+sid+'.md')).write_text(core.prompt(public,arm),encoding='utf-8')
    dump(root/'schema.json',core.schema())
    dump(root/'results/ground_truth_execution.json',{'actual_original_calls':calls,'simulated_students':8,'real_learners':0})
    # Snapshot old files read-only, including all previous result artifacts, before any new inference.
    manifests=[core.WORKSPACE/'experiments/round5_ai_judge_review/completion_manifest.json',
        old/'results/cli_automation_20261009T094819533718Z/completed_artifacts_manifest.json',old/'results/prior_files_sha256.json']
    previous={}
    for manifest in manifests:
        data=core.read(manifest)
        for name,sha in data.get('sha256',data).items():
            p=Path(name)
            if not p.is_absolute():
                candidates=[core.WORKSPACE/name,old/name]
                p=next((x for x in candidates if x.exists()),p)
            if digest(p)!=sha: raise ValueError('Historical file changed: '+str(p))
            previous[str(p.resolve())]=sha
    dump(root/'historical_manifest.json',{'sha256':previous,'source_manifests':[str(p) for p in manifests]})
    (root/'BASELINE_RULES.md').write_text('S0仅使用回应文本和案例ID：优先程序/规范否定区别与单负数核验请求；明确右端点或补项遗漏自述则自行修改；明确错误端点序列或非负规范则反例；含糊数值/语气优先澄清。无情景ID、完整句查表或gold读取。源代码见core.baseline。固定模板覆盖有限，不代表所有规则。\n',encoding='utf-8')
    files=[*root.glob('*.py'),root/'F01_test_plan.md',root/'BASELINE_RULES.md',root/'schema.json',root/'historical_manifest.json']
    files += [p for folder in ['cases','inputs','gold','prompts'] for p in (root/folder).glob('*')]
    dump(root/'freeze_manifest.json',{'version':'F01_v1','created_utc':datetime.now(timezone.utc).isoformat(),
        'model':core.MODEL,'effort':core.EFFORT,'timeout_seconds':core.TIMEOUT,'simulated_scenarios':8,
        'sha256':{p.relative_to(root).as_posix():digest(p) for p in files}})
    print(json.dumps({'frozen_files':len(files),'historical_files':len(previous),'original_facts_verified':len(calls)},ensure_ascii=True))


if __name__=='__main__':main()
