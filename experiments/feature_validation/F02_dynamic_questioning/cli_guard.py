"""Runtime-only fix: independently replay a referenced public counterexample.

Formal run.py/core.py remain frozen and their original failures are not rerun.
This adapter preserves the original strict check alongside its runtime result.
"""
import re
from copy import deepcopy
from . import core

FROZEN_VALIDATE=core.validate
FROZEN_PUBLIC=core.public


def public_snapshot(case,history,origin):
    return deepcopy(FROZEN_PUBLIC(case,history,origin))


def validate(output,value):
    # The frozen validator assumes array item and request field types. Fail closed
    # before calling it; frozen experiment code and old artifacts stay intact.
    shape=[]
    if isinstance(output,dict):
        for key in ['answer_quotes','uncertainties','evidence_refs']:
            rows=output.get(key)
            if not isinstance(rows,list) or any(not isinstance(x,str) for x in rows):shape.append('invalid_'+key)
        requests=output.get('execution_requests')
        if not isinstance(requests,list):shape.append('invalid_execution_requests')
        else:
            for request in requests:
                if not isinstance(request,dict):shape.append('request_shape');continue
                if not isinstance(request.get('source_version'),str):shape.append('invalid_source_version_type')
                for key in ['predicted_actual','predicted_expected']:
                    prediction=request.get(key)
                    if prediction is not None and type(prediction) is not int:shape.append('invalid_'+key)
    if shape:
        return {'structural_valid':False,'display_safe':False,'issues':shape,'requests':[],
            'runtime_guard_version':'public_evidence_replay_v3','public_evidence_replays':[],
            'frozen_guard_issues':None,'semantic_truth_certified':False,'needs_human_review':True}
    result=deepcopy(FROZEN_VALIDATE(output,value))
    result['frozen_guard_issues']=list(result['issues'])
    result['runtime_guard_version']='public_evidence_replay_v3'
    result['public_evidence_replays']=[]
    result['semantic_truth_certified']=False
    result['needs_human_review']=True
    result['program_prose_not_semantically_certified']=True
    if result['issues']!=['missing_counterexample']:return result
    text=output['student_message']
    nums={int(n) for n in re.findall(r'n\s*=\s*(\d+)',text)}
    refs=set(output['evidence_refs'])
    for evidence in value['case']['evidence']:
        if evidence['evidence_id'] not in refs or evidence['args'][0] not in nums:continue
        version=evidence.get('source_version','original')
        request={'source_version':version,'args':evidence['args'],
            'predicted_actual':evidence['actual'],'predicted_expected':evidence['expected']}
        checked=core.check_request(value['case'],request)
        if not checked['input_legal'] or not checked['execution'] or checked['execution']['status']!='ok':continue
        if checked['actual_prediction_correct'] is not True or checked['expected_prediction_correct'] is not True:continue
        checked['origin']='runtime_replay_of_public_ref_not_new_model_request'
        checked['evidence_id']=evidence['evidence_id']
        result['public_evidence_replays'].append(checked)
    covered={r['request']['args'][0] for r in result['public_evidence_replays']}
    if nums and nums<=covered:
        result['issues']=[];result['display_safe']=True
        result['requests']+=result['public_evidence_replays']
    result['program_prose_not_semantically_certified']=True
    return result


def main():
    from .runtime import trial_cli
    trial_cli.main()


if __name__=='__main__':main()
