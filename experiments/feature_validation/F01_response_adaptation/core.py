"""F01 public input, transparent S0, and controlled original-program verification."""
import json
import re
from pathlib import Path
from experiments.common import digest, dump, oracle, valid_args
from experiments.runner import execute, source_hash

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[2]
ACTIONS = ['continue_asking','show_counterexample','tiered_hint','request_self_modification','clarify_meaning','suspend_for_choice']
ACTION_ZH = dict(zip(ACTIONS,['继续追问','展示新的执行反例','给出分层提示','请学生自行修改代码','澄清学生意思','暂停判断，交给用户选择']))
MODEL, EFFORT, TIMEOUT = 'gpt-6.1-sol','high',1200


def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))


def schema():
    text = {'type':'string'}
    request = {'type':'object','additionalProperties':False,'properties':{
        'args':{'type':'array','items':{'anyOf':[{'type':'integer'},{'type':'array','items':{'type':'integer'}}]}},
        'predicted_actual':{'type':['integer','null']},'predicted_expected':{'type':['integer','null']}},
        'required':['args','predicted_actual','predicted_expected']}
    props = {'interpretation':text,'answer_quotes':{'type':'array','items':text},
        'evidence_sufficiency':{'type':'string','enum':['sufficient','partial','insufficient']},
        'next_action':{'type':'string','enum':ACTIONS},'student_message':text,'decision_basis':text,
        'uncertainties':{'type':'array','items':text},'evidence_refs':{'type':'array','items':text},
        'execution_requests':{'type':'array','items':request}}
    return {'type':'object','additionalProperties':False,'properties':props,'required':list(props)}


def prompt(public, arm):
    shared = '''你是编程导师。现在只处理学生对一次教学追问的回应，选择一个下一步动作，给出对学生展示的下一句话。不要评估长期掌握。
两项共同要求：不直接给完整正确代码，也不提供足以完成全部修复的精确编辑；只选择一个动作，简短完整回答。
请按所提供JSON格式回答。interpretation是对当前回应的有限理解；answer_quotes引用学生原话；evidence_sufficiency只指这句回应是否足以支持你的理解；decision_basis说明选择；uncertainties列出无法知道的部分。evidence_refs只能引用SOURCE、CONTRACT、QUESTION、ANSWER或给定E编号。
动作：continue_asking继续追问、show_counterexample展示新执行反例、tiered_hint分层提示、request_self_modification请学生自行修改、clarify_meaning澄清意思、suspend_for_choice暂停由用户选择。
如建议执行，execution_requests仅填写原学生代码的合法solve实参（数组包含一个实参）、预测实际输出与题目预期输出；不确定预测填null，无执行建议填空数组。不要生成其他待执行源码。此处不能调用工具，运行建议将由独立程序检查，不是你自称已运行。
'''
    constraint = ('按普通编程辅导方式分析学生回答，给出你的理解、解释与下一步建议。\n' if arm=='S1' else
        '额外要求：区分观察事实、解释以及尚未确认的学生意图；不要把程序缺陷或一句含糊回应确诊为学生不懂概念。最多考虑两个解释，证据不足时澄清或用合法反例区分；明确回应已有内容时不要重复同一追问。不把自述意图当作经过验证的事实，不把你自己的解释当作核验结果。\n')
    return shared+constraint+'\n<public_input>\n'+json.dumps(public,ensure_ascii=False,indent=2)+'\n</public_input>\n'


def public_from_prompt(value): return json.loads(value.split('<public_input>\n',1)[1].split('\n</public_input>',1)[0])


def baseline(case_id, answer):
    """No scenario IDs/gold access. Ordered linguistic rules are intentionally inspectable."""
    t = answer.replace('−','-').replace('，','、').replace(' ','')
    state, action = 'insufficient','clarify_meaning'
    interpretation = '这句回应尚不能确定你说的是程序行为、题意还是原先计划。'
    message = '你说的是这段代码实际会输出什么，还是题目要求它输出什么？请说明你指的是哪一种。'
    requests = []
    hedged = any(x in t for x in ['说不清','不确定','可能','大概','吧'])
    if case_id=='01':
        plan = ('补' in t and ('漏写' in t or '忘' in t) and ('range' in t or '右端点' in t))
        clear = ('只取1、2' in t or '只取1和2' in t or '不包含3' in t or '不含3' in t)
        wrong = not hedged and ('会取1、2、3' in t or '包括1、2、3' in t)
        if plan or clear:
            state,action = 'sufficient','request_self_modification'
            interpretation = '你明确说明循环不包含右端点；补末项的计划若提到，仅是你的自述。'
            message = '请按你现在的想法自行修改；完成后先手算一个不同的合法输入，再检查修改后的结果。'
        elif wrong:
            state,action = 'sufficient','show_counterexample'
            interpretation = '你明确预测range包含右端点，并提出覆盖变量的解释；需要用逐轮记录核对这两项。'
            message = '用n=4追踪当前循环中的i与s，再比较实际返回值和题意要求；先检验你刚才的两个说法。'
            requests = [{'args':[4],'predicted_actual':6,'predicted_expected':10}]
        else:
            message = '你说的3是当前代码的实际结果，还是题目应有的结果？请先澄清这个区别。'
    elif case_id=='07':
        contrast = '代码' in t and any(x in t for x in ['不是','不在说','并非']) and any(x in t for x in ['题目','规范'])
        probe = ('一个负数' in t or '单个负数' in t) and any(x in t for x in ['检验','走一遍','先用','想先'])
        correct = '-2' in t and any(x in t for x in ['0不在','不属于','额外'])
        wrong = not hedged and (bool(re.search('最大值不能.*负',t)) or bool(re.search('规范答案.*0',t)))
        if contrast and probe:
            state,action = 'partial','show_counterexample'
            interpretation = '你区分代码输出与题目答案，并希望先检查单个负数；尚未看到独立修改。'
            message = '按你的提议，用[-8]检查原代码：先分开预测实际输出和题目要求，再核对这两个值。'
            requests = [{'args':[[-8]],'predicted_actual':0,'predicted_expected':-8}]
        elif correct:
            state,action = 'sufficient','request_self_modification'
            interpretation = '你指出本次规范最大值是-2，并说明额外零与输入的区别。'
            message = '请自行修改代码，再用一个未出现过的合法输入检查；先手算题目要求的结果。'
        elif wrong:
            state,action = 'sufficient','show_counterexample'
            interpretation = '这句话明确声称规范最大值不能为负；这不是对你的长期知识状态的诊断。'
            message = '试着只给一个元素[-8]：题目要求的最大值来自哪些元素？再对照原代码实际结果。'
            requests = [{'args':[[-8]],'predicted_actual':0,'predicted_expected':-8}]
    return {'interpretation':interpretation,'answer_quotes':[answer] if answer else [],
        'evidence_sufficiency':state,'next_action':action,'student_message':message,
        'decision_basis':'按冻结的明确数值/右端点/否定/程序与规范区分规则分流；无法识别则澄清。',
        'uncertainties':['未观察实际修改或独立新题；不能推出长期掌握。'],
        'evidence_refs':['ANSWER','SOURCE','CONTRACT'],'execution_requests':requests}


def check_request(case, request):
    args = request.get('args')
    legal, reason = valid_args(case['task'],args,case.get('domain','default'))
    row = {'request':request,'input_legal':legal,'input_reason':reason,'execution':None,
           'actual_prediction_correct':None,'expected_prediction_correct':None}
    if not legal: return row
    if source_hash(case['source']) != case['source_sha256']: raise ValueError('Original source hash mismatch')
    actual = execute(case['source'],[args])[0]
    expected = oracle(case['task'],args)
    row.update(execution=actual,expected=expected,new_input=args not in [e['args'] for e in case['evidence']])
    for key,value in [('actual',actual.get('value')),('expected',expected)]:
        predicted = request.get('predicted_'+key)
        if predicted is not None: row[key+'_prediction_correct'] = type(predicted) is int and actual['status']=='ok' and predicted==value
    return row


def validate_output(output, public):
    issues=[]
    if not isinstance(output,dict): return {'structural_valid':False,'display_safe':False,'issues':['not_object'],'requests':[]}
    if set(output)!=set(schema()['required']): issues.append('field_set')
    if output.get('next_action') not in ACTIONS: issues.append('invalid_action')
    if output.get('evidence_sufficiency') not in ['sufficient','partial','insufficient']: issues.append('invalid_sufficiency')
    for key in ['interpretation','student_message','decision_basis']:
        if not isinstance(output.get(key),str) or not output[key].strip(): issues.append('invalid_'+key)
    for key in ['answer_quotes','uncertainties','evidence_refs']:
        if not isinstance(output.get(key),list) or any(not isinstance(x,str) for x in output.get(key,[])): issues.append('invalid_'+key)
    structural = not issues
    quotes = output.get('answer_quotes',[])
    quotes_valid = isinstance(quotes,list) and bool(quotes) and all(isinstance(q,str) and bool(q) and q in public['student_answer'] for q in quotes)
    if not quotes_valid: issues.append('invalid_student_quote')
    refs = {'SOURCE','CONTRACT','QUESTION','ANSWER'}|{e['evidence_id'] for e in public['case']['evidence']}
    refs_valid = isinstance(output.get('evidence_refs'),list) and all(r in refs for r in output['evidence_refs'])
    if not refs_valid: issues.append('invalid_evidence_ref')
    requests = output.get('execution_requests')
    checked=[]
    if not isinstance(requests,list): issues.append('invalid_requests')
    else:
        for request in requests:
            if not isinstance(request,dict) or set(request)!= {'args','predicted_actual','predicted_expected'}:
                issues.append('invalid_request_shape');continue
            checked.append(check_request(public['case'],request))
    if any(not r['input_legal'] for r in checked): issues.append('illegal_test')
    if any(r['execution'] and r['execution']['status']!='ok' for r in checked): issues.append('execution_unavailable')
    if any(r[k] is False for r in checked for k in ['actual_prediction_correct','expected_prediction_correct']): issues.append('incorrect_numeric_prediction')
    if output.get('next_action')=='show_counterexample' and not checked: issues.append('counterexample_missing_input')
    return {'structural_valid':structural,'answer_quotes_valid':quotes_valid,'evidence_refs_valid':refs_valid,
        'requests':checked,'issues':issues,'display_safe':not issues,
        'semantic_truth_automatically_verified':False,'needs_human_review':True}


def verify_freeze():
    manifest=read(ROOT/'freeze_manifest.json')
    for relative,sha in manifest['sha256'].items():
        if digest(ROOT/relative)!=sha: raise ValueError('Frozen F01 input changed: '+relative)
    return len(manifest['sha256'])
