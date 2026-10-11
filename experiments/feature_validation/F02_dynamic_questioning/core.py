"""Public conversation protocol; reuse F01 actions and controlled fact checks."""
import json
from pathlib import Path
from experiments.common import dump, digest
from ..F01_response_adaptation import core as f01

ROOT=Path(__file__).resolve().parent
MODEL,EFFORT,TIMEOUT=f01.MODEL,f01.EFFORT,f01.TIMEOUT
read=f01.read
ACTIONS=f01.ACTIONS
ACTION_ZH=f01.ACTION_ZH


def schema():
    value=f01.schema()
    value['properties']['execution_requests']['items']['properties']['source_version']={'type':'string'}
    value['properties']['execution_requests']['items']['required'].append('source_version')
    value['properties'].update(question_intent={'type':'string'}, stop_questioning={'type':'boolean'},
        stop_reason={'type':'string','enum':['not_stopping','understanding_sufficient','await_new_evidence','user_choice']})
    value['required']=list(value['properties'])
    return value


def public(case,history,origin):
    students=[x['text'] for x in history if x['role']=='student']
    teachers=[x['output']['student_message'] for x in history if x['role']=='teacher']
    return {'case':case,'history':history,'student_answer':students[-1] if students else '',
        'previous_question':teachers[-1] if teachers else '', 'teacher_turn':len(teachers)+1,
        'data_origin':origin}


def prompt(value):
    return '''你是编程导师。根据下面题目、代码、可信执行事实及当前真实对话，选择下一句具体教学追问、反例、有限提示或让学生自主修改。第一次没有学生回应时先提出有价值的问题。
共同边界：不提供完整正确代码或足以完成全部修复的精确编辑。不根据缺陷断言学生长期不懂某概念。不捏造执行事实。不重复已回答清楚的问题。理解当前问题充分时可停止追问，让学生自行修改；未知新版需收集新版材料。学生的自述不等于执行事实。
使用提供的JSON结构。answer_quotes仅引用最新学生原文；首问用空数组。evidence_refs可用SOURCE、CONTRACT、QUESTION、ANSWER及E编号。question_intent写具体问题意图；stop_questioning与stop_reason保持一致。execution_requests可为空；需要真实反例时只指定已提供source_version和合法整数输入args，预测不确定可null。系统独立核验，不能自行声明已验证。只处理当前问题，不评价学习效果。
公开输入：
''' +json.dumps(value,ensure_ascii=False,indent=2)


def check_request(case,request):
    version=request.get('source_version')
    if version=='original':selected=case
    elif version in case.get('versions',{}):
        selected=dict(case,**case['versions'][version])
    else:return {'request':request,'input_legal':False,'input_reason':'unknown_source_version',
        'execution':None,'actual_prediction_correct':None,'expected_prediction_correct':None}
    checked=f01.check_request(selected,{k:v for k,v in request.items() if k!='source_version'})
    checked['request']=request
    return checked


def validate(output,value):
    issues=[]
    if not isinstance(output,dict):return {'structural_valid':False,'display_safe':False,'issues':['not_object'],'requests':[]}
    if set(output)!=set(schema()['required']):issues.append('field_set')
    if output.get('next_action') not in ACTIONS:issues.append('invalid_action')
    if output.get('evidence_sufficiency') not in ['sufficient','partial','insufficient']:issues.append('invalid_sufficiency')
    for k in ['interpretation','student_message','decision_basis','question_intent']:
        if not isinstance(output.get(k),str) or not output[k].strip():issues.append('invalid_'+k)
    for k in ['answer_quotes','uncertainties','evidence_refs','execution_requests']:
        if not isinstance(output.get(k),list):issues.append('invalid_'+k)
    if type(output.get('stop_questioning')) is not bool:issues.append('invalid_stop')
    if output.get('stop_reason') not in schema()['properties']['stop_reason']['enum']:issues.append('invalid_stop_reason')
    if bool(output.get('stop_questioning'))==(output.get('stop_reason')=='not_stopping'):issues.append('inconsistent_stop')
    structural=not issues
    quotes=output.get('answer_quotes',[])
    answer=value['student_answer']
    if answer and (not quotes or any(not isinstance(q,str) or not q or q not in answer for q in quotes)):issues.append('invalid_quote')
    if not answer and quotes:issues.append('quote_without_student')
    refs={'SOURCE','CONTRACT','QUESTION','ANSWER'}|{x['evidence_id'] for x in value['case']['evidence']}
    if any(r not in refs for r in output.get('evidence_refs',[])):issues.append('unknown_ref')
    checked=[]
    for r in output.get('execution_requests',[]):
        if not isinstance(r,dict) or set(r)!={'args','source_version','predicted_actual','predicted_expected'}:
            issues.append('request_shape');continue
        c=check_request(value['case'],r);checked.append(c)
        if not c['input_legal']:issues.append('illegal_request')
        if c['execution'] and c['execution']['status']!='ok':issues.append('execution_failed')
        if any(c[k] is False for k in ['actual_prediction_correct','expected_prediction_correct']):issues.append('false_prediction')
    if output.get('next_action')=='show_counterexample' and not checked:issues.append('missing_counterexample')
    return {'structural_valid':structural,'display_safe':not issues,'issues':issues,'requests':checked,
        'needs_human_review':True,'semantic_truth_certified':False}


def termination(output,turn):
    if output.get('stop_questioning'):return output.get('stop_reason','invalid_stop')
    return 'budget_limited' if turn>=3 else 'continue'


def verify():
    m=read(ROOT/'freeze_manifest.json')
    amended=read(ROOT/'transport_amendment.json') if (ROOT/'transport_amendment.json').exists() else None
    if amended:
        if digest(ROOT/'freeze_manifest.json')!=amended['original_freeze_sha256']:raise ValueError('Original freeze changed')
        for original,backup in amended['preserved_originals'].items():
            if digest(ROOT/backup)!=m['sha256'][original]:raise ValueError('Original code not preserved')
    for rel,sha in m['sha256'].items():
        if amended:sha=amended['sha256'].get(rel,sha)
        if digest(ROOT/rel)!=sha:raise ValueError('F02 frozen file changed: '+rel)
    return len(m['sha256'])
