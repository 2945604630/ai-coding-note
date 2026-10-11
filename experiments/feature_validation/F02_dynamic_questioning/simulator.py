"""Only select frozen literal responses; incompatible questions are retained."""
import re


def scope(output):
    text=output.get('student_message','')
    topics=[]
    for topic,pattern in {'boundary':r'range|端点|边界|哪些i|取哪些|最后.*i|循环',
        'state':r'逐|累加|覆盖|s\s*=|s的|s是多少|变量|追踪',
        'contract':r'题目|要求|加数|求和|题意', 'compensation':r'返回|return|\+\s*n|补偿|最终|少1|偏移',
        'version':r'新版|修改后|当前完整代码|报错|版本|局部|改动',
        'intent':r'意图|想法|疏漏|为什么|怎么理解|原因|含义|能解释'}.items():
        if re.search(pattern,text,re.I):topics.append(topic)
    nums=[int(x) for x in re.findall(r'n\s*=\s*(\d+)',text)]
    for r in output.get('execution_requests',[]):
        if len(r.get('args',[]))==1 and type(r['args'][0]) is int:nums.append(r['args'][0])
    return sorted(set(topics)),sorted(set(nums))


def choose(bank,output):
    topics,nums=scope(output)
    result={'compatible':False,'topics':topics,'requested_inputs':nums,'basis':'frozen_scope_router',
        'needs_human_review':True,'text':None}
    if not topics or not set(topics)&set(bank['allowed_topics']):
        result['reason']='unsupported_question_topic';return result
    if len(nums)>1:
        result['reason']='multiple_inputs_not_in_frozen_single_input_bank';return result
    n=nums[0] if nums else 3
    choices=[x for x in bank['replies'] if x['n']==n]
    if not choices:result['reason']='input_not_in_frozen_bank';return result
    result.update(compatible=True,text=choices[0]['text'],reply_index=bank['replies'].index(choices[0]),
        reason='intentional_interrupt' if bank.get('interrupt') else 'covered_topic_and_input')
    return result
