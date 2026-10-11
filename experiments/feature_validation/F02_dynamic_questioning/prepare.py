"""Write reviewed public cases and private frozen persona branches, once."""
from datetime import datetime, timezone
from experiments.common import dump,digest,oracle
from experiments.runner import execute,source_hash
from .core import ROOT,read,schema


def reply(cid,kind,slot,n):
    vals=list(range(1,n));s=sum(vals);target=n*(n+1)//2
    trace='、'.join(map(str,vals)) if vals else '没有任何i'
    original={'C01':s,'C02':max(n-1,0),'C03':target-1}[cid]
    patch=target+n-1
    if cid=='C01':
        texts={
        ('correct',0):f'n={n}时range实际取{trace}，不包含右端点n，当前返回{original}。题目要求包含n，目标是{target}。我之前是实现时疏漏，并非故意改变题意；现在能说明少了哪一项。',
        ('correct',1):f'换成n={n}也一样，实际{original}与要求{target}的差来自端点n未进入循环。我想自己修改，不用再重复问同一范围。',
        ('wrong',0):f'我认为range包含右端点n，所以n={n}应把1到{n}都加进去，得到{target}；已记录的实际输出我还解释不了。',
        ('wrong',1):f'我现在看到range不包含右端点；但我以为题目也只要求小于n的数，不包含n，所以输出{original}就应该对。',
        ('partial',0):f'实际输出{original}，题目应为{target}；我还分不清是范围、题意，还是算的时候少了一步。',
        ('partial',1):f'我能列出实际i为{trace}，目标应包含n，但我还不会解释代码里的右端点为什么没取到。',
        ('unexpected',0):f'先补充我的意图：我想把n也算进去，不是有意排除它，请不要只从错误代码推测我的想法。range实际没取右端点，n={n}的结果是{original}而要求是{target}。',
        ('unexpected',1):'我已经说明想包含n，也理解实际范围；我想先自己改。还没改代码，不能把这个愿望当作修改已成功。'}
    elif cid=='C02':
        texts={
        ('correct',0):f'我先解释范围这一部分：n={n}取{trace}，range不包含右端点；题目要包含n。s如何变化我还没检查，不能说已经把全部原因找完。',
        ('correct',1):f'再看赋值：s=i覆盖前值，只保留本轮i，不累加，n={n}最终是{original}。范围还漏n，题目目标为{target}。现在两处关系都能解释，我准备自己修改。',
        ('wrong',0):f'n={n}应该包含n；我认为s=i就是累加，和s+=i一样，所以最后应是{target}。实际{original}我解释不了。',
        ('wrong',1):f'范围不包含右端点我接受了；但s=i仍然是累加，我觉得当前循环会留下{ s }，这和真实输出是否一致还不清楚。',
        ('partial',0):f'n={n}实际是{original}，目标{target}；范围可能不含n，但变量每次怎么变我还不确定。',
        ('partial',1):'s=i会覆盖前值，这一点我理解了；范围是否还少了题目要求的项我暂时不确定，不要当成全部理解。',
        ('unexpected',0):'我刚才修改了代码，现在同样n=3看到3，旧记录是2。新版没有贴出来，也没保存完整记录；请别用旧源码认定新输出。',
        ('unexpected',1):'我找不到新版完整代码，只能确认你看到的旧版；现在先暂停新版原因判断。'}
    else:
        texts={
        ('correct',0):f'原版循环不含右端点，但返回里的+n补回n，所以不是单独的范围问题；还额外减1，n={n}原版{original}，目标{target}。局部改动版会再加一次n后减1，得到{patch}，单例通过不能说明全修好。',
        ('correct',1):f'n={n}同样体现补偿与偏移：原版{original}，局部改动版{patch}，要求{target}。我能解释它们的关系，想自己调整代码，不需要给全部修改。',
        ('wrong',0):'只要把范围补齐就行；局部改动版在n=1通过，说明它已经修好了，其它返回部分不用看。',
        ('wrong',1):f'局部改动版n={n}的返回{patch}不一定等于{target}。我看到不一致，但还不懂为什么，多出来的返回部分我没解释清楚。',
        ('partial',0):f'n={n}原版返回{original}、要求{target}。我还没理清循环的和与返回式中n之间的关系；局部通过不够确认。',
        ('partial',1):'我现在知道+n补回了循环没取到的n，但那个减1到底怎么影响结果我还不会解释，请不要当成我全部懂了。',
        ('unexpected',0):'我撤回“一个测试通过就修好了”的想法：已记录局部改动版n=3得到8，要求6；n=1虽通过仍不能忽略它。我想比较循环与返回补偿。',
        ('unexpected',1):'但是我又想，n=1通过就算改好了，n=3的8和6可以不用管。这和我前一句矛盾；先别认定我已经理解全部问题。'}
    return texts[kind,slot]


def main():
    if (ROOT/'freeze_manifest.json').exists():raise FileExistsError('Package already frozen')
    for name in ['cases','gold','responses','results','prompts','preflight','user_runs','reviews']:(ROOT/name).mkdir(exist_ok=True)
    old=ROOT.parent/'F01_response_adaptation'
    historic={str(p.resolve()):digest(p) for p in old.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    dump(ROOT/'historical_manifest.json',{'sha256':historic})
    rules=read(ROOT/'rule_freeze.json')
    for rel,sha in rules['sha256'].items():
        if digest(ROOT/rel)!=sha:raise ValueError('Rule changed after rule freeze')
    sources=[('C01','r08_loop_only'),('C02','r04_two_masked_bugs'),('C03','r11_compensated_loop_with_wrong_return')]
    prior=read(ROOT.parents[1]/'round4/data/b_cases.json') if (ROOT.parents[1]/'round4/data/b_cases.json').exists() else read(ROOT.parents[2]/'round4/data/b_cases.json')
    if isinstance(prior,dict):prior=prior['cases']
    grid=[];paths=[];private=[]
    for cid,oldid in sources:
        # Lookup by prefix, without putting historical purpose/labels into public material.
        original=next(x for x in prior if x['id']==oldid or x['id']==oldid.split('_')[0] or x['id'].startswith(oldid.split('_')[0]+'_'))
        source=original['source']
        case={'case_id':cid,'task':'inclusive_sum','statement':'实现solve(n)，返回从1到n（含n）的所有整数之和。n=0返回0。',
            'input_contract':'一个整数n，0<=n<=8；布尔值不属于合法整数。',
            'source':source,'source_sha256':source_hash(source),'versions':{},'evidence':[]}
        if cid=='C03':
            patch=source.replace('range(1, n)','range(1, n + 1)')
            case['versions']['local_patch']={'source':patch,'source_sha256':source_hash(patch),'evidence':[]}
        for version in ['original',*case['versions']]:
            code=source if version=='original' else case['versions'][version]['source']
            rows=execute(code,[[n] for n in range(9)])
            for n,row in enumerate(rows):
                if row['status']!='ok':raise RuntimeError('Controlled fixture execution failed')
                record={'case_id':cid,'source_version':version,'args':[n],'execution':row,'expected':oracle('inclusive_sum',[n])}
                grid.append(record)
                if n in [0,1,3]:
                    case['evidence'].append({'evidence_id':f'E{len(case["evidence"])+1}','source_version':version,
                        'args':[n],'actual':row['value'],'expected':record['expected'],'status':'ok'})
        dump(ROOT/'cases'/(cid+'.json'),case)
        causes={'C01':['right_endpoint_excluded'], 'C02':['right_endpoint_excluded','overwrite_instead_of_accumulation'],
            'C03':['uncancelled_minus_one_offset; endpoint exclusion compensated_by_plus_n']}[cid]
        private.append({'case_id':cid,'program_causes':causes,'student_intent_not_inferable_from_source':True,
            'competing_interpretations':['contract misreading','runtime misunderstanding','implementation oversight'],
            'frozen_reference':'n*(n+1)//2; original & local_patch full grid stored separately',
            'repair_leak_boundaries':'精确完成全部修改或完整正确代码；重要思路提示另标，不混为完整泄露。'})
        for kind in ['correct','wrong','partial','unexpected']:
            banks=[]
            for slot in range(2):
                banks.append({'allowed_topics':['boundary','state','contract','compensation','version','intent'],
                    'interrupt':kind=='unexpected','replies':[{'n':n,'text':reply(cid,kind,slot,n)} for n in range(9)]})
            sid=cid+'_'+kind
            paths.append({'scenario_id':sid,'case_id':cid,'data_origin':'frozen_simulated_student','banks':banks})
            reference={'scenario_id':sid,'kind':kind,'supported_after_first':'见冻结原文，区分明确表达与尚未说明；不得据此长期确诊。',
                'supported_after_second':'见冻结原文，最新矛盾撤回旧确定性；新版缺失不假设修复。',
                'allow_early_stop':kind=='correct' and cid!='C02' or kind=='unexpected' and cid in ['C01','C02'],
                'allowed_actions_first':(['request_self_modification','clarify_meaning','suspend_for_choice'] if kind=='correct' and cid!='C02' else ['continue_asking','show_counterexample','tiered_hint','clarify_meaning','suspend_for_choice']),
                'allowed_actions_second':(['request_self_modification','suspend_for_choice'] if kind=='correct' else ['continue_asking','show_counterexample','tiered_hint','clarify_meaning','suspend_for_choice']),
                'expected_resolved':{'C01':['boundary','contract'], 'C02':['boundary','contract','state'], 'C03':['compensation','offset','local_patch_not_general_proof']}[cid],
                'needs_human_review':True,'non_unique_valid_wording':True}
            private.append(reference)
    dump(ROOT/'gold/paths.json',private);dump(ROOT/'gold/response_bank.json',paths)
    dump(ROOT/'results/frozen_execution_grid.json',grid);dump(ROOT/'schema.json',schema())
    files=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.parts[-2] not in ['preflight']]
    dump(ROOT/'freeze_manifest.json',{'utc':datetime.now(timezone.utc).isoformat(),'before_formal_calls':True,
        'simulated_paths':12,'case_count':3,'max_teacher_calls':27,'rule_first':rules,
        'sha256':{str(p.relative_to(ROOT)):digest(p) for p in files}})
    print('Frozen:',len(files),'files; reviewed execution grid:',len(grid),'records; historical files:',len(historic))


if __name__=='__main__':main()
