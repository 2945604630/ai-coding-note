"""Generic AST + fixed question bank; never imports private paths or labels."""
import ast
import re


def known(history):
    topics=set()
    for x in history:
        if x['role']!='student':continue
        text=x['text']
        if re.search(r'range.{0,10}(不包含|不含|取不到|排除).*?(右|n)|右端点.{0,6}(不取|排除)',text):topics.add('boundary')
        if re.search(r'(现在认为|其实|还是).*?range.{0,6}(包含|取到)右',text):topics.discard('boundary')
        if re.search(r'(题目|目标|要求).{0,12}(含n|包含n|算到n|包括n)',text):topics.add('contract')
        if re.search(r'(题目|目标).{0,12}(不含n|不包含n|小于n)',text):topics.discard('contract')
        if re.search(r'(s\s*=\s*i|赋值).{0,16}(覆盖|替换|只保留)|覆盖前',text):topics.add('state')
        if re.search(r'(不覆盖|不会覆盖|就是累加|和累加一样)',text):topics.discard('state')
        if re.search(r'(补回|补偿|抵消).{0,14}n|\+n.{0,10}(补回|补偿)',text):topics.add('compensation')
        if re.search(r'(减1|减一|少1|少一|偏移)',text):topics.add('offset')
        if re.search(r'(只有|只要).{0,10}(一个|n=1).{0,12}(通过|对).{0,12}(修好|没问题)|不用管.*n=3',text):topics.discard('offset')
    return topics


def required(case):
    tree=ast.parse(case['source'])
    assigns=[x for x in ast.walk(tree) if isinstance(x,ast.Assign) and isinstance(x.value,ast.Name) and x.value.id=='i']
    returns=[x.value for x in ast.walk(tree) if isinstance(x,ast.Return)]
    result=['boundary','contract']
    if assigns:result.append('state')
    if any(isinstance(x,ast.BinOp) for x in returns):result+=['compensation','offset']
    return result


QUESTIONS={
 'boundary':'先只核对当前循环：n={n}时range实际会取哪些i？这与题目包含n的要求有什么差别？',
 'contract':'先分开代码行为与题目要求：题目规定1到n求和时，端点n应不应该作为加数？',
 'state':'范围这一点先保留。n={n}时逐次经过s=i，s还保留以前的值吗？请写出最后两次的s。',
 'compensation':'你已核对部分循环。原版返回式中的+n对循环漏掉的项有什么作用？请区分循环部分与最终返回。',
 'offset':'比较原版和局部改动版的最终返回，而不只看循环：单个输入通过能否解释其它输入仍失败？请说明尚未解释的项。'}


def decide(value):
    answer=value['student_answer'];case=value['case'];history=value['history']
    unresolved=[t for t in required(case) if t not in known(history)]
    n=max((x['args'][0] for x in case['evidence'] if x.get('source_version','original')=='original'),default=3)
    action='continue_asking';stop=False;reason='not_stopping';requests=[];state='partial'
    if not history:
        message=f'n={n}时，当前循环实际取哪些i，s逐次是多少，最后返回多少？再说题目是否要求包含n；哪些差异是你仍不能解释的？'
        interpretation='尚无学生回答；先区分运行轨迹、题目范围与意图。';state='insufficient'
    elif re.search(r'(改过|修改了|动过|新版|新错误|另一个版本|还没保存)',answer):
        message='请提供当前完整代码、同一次执行的输入和原始报错或输出；没有新版材料前暂停判断。'
        action='clarify_meaning';stop=True;reason='await_new_evidence';interpretation='回应提及版本变化，原版证据不能确认新版。'
    elif re.search(r'(直接给|给我).{0,8}(完整|答案|代码)',answer):
        message='可以选择有限提示或自行修改；我不会替你完成整个修复。你希望先检查哪一步？'
        action='suspend_for_choice';stop=True;reason='user_choice';interpretation='学生请求更直接的帮助，先让其选择有限支持。'
    elif not unresolved:
        action='request_self_modification';stop=True;reason='understanding_sufficient';state='sufficient'
        message='你已说明当前问题的关键关系。请自行修改并测试；这不代表代码已通过或长期掌握。'
        interpretation='当前回应和历史解释覆盖了本题相关主题。'
    else:
        message=QUESTIONS[unresolved[0]].format(n=4 if '包含右' in answer else n)
        interpretation='保留已明确表达的主题，只询问尚未识别的关系。'
    return {'interpretation':interpretation,'answer_quotes':[answer] if answer else [],'evidence_sufficiency':state,
        'next_action':action,'student_message':message,'decision_basis':'冻结的AST主题与历史表达路由；不是知识确诊。',
        'uncertainties':['尚未观察独立修改或新题表现。'],'evidence_refs':['SOURCE','CONTRACT']+(['ANSWER'] if answer else []),
        'execution_requests':requests,'question_intent':','.join(unresolved) if unresolved else 'independent_edit',
        'stop_questioning':stop,'stop_reason':reason}
