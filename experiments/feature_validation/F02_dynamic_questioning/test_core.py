import unittest
from . import core, baseline, simulator


class Contracts(unittest.TestCase):
    def case(self):
        return {'case_id':'unseen','task':'inclusive_sum','source':'def solve(n):\n    s = 0\n    for i in range(1, n):\n        s += i\n    return s\n', 'source_sha256':'x', 'evidence':[{'evidence_id':'E1','args':[3],'actual':3,'expected':6}], 'versions':{}}

    def test_no_invented_reply(self):
        bank={'replies':[{'n':3,'text':'固定原文'}], 'allowed_topics':['boundary']}
        out={'student_message':'请解释你的操作系统与安装目录', 'execution_requests':[]}
        self.assertFalse(simulator.choose(bank,out)['compatible'])

    def test_input_outside_frozen_bank(self):
        bank={'replies':[{'n':3,'text':'固定原文'}], 'allowed_topics':['boundary']}
        out={'student_message':'n=9时range取哪些值？', 'execution_requests':[]}
        self.assertFalse(simulator.choose(bank,out)['compatible'])

    def test_literal_reply_selected(self):
        bank={'replies':[{'n':3,'text':'  冻结原文  '}], 'allowed_topics':['boundary']}
        out={'student_message':'n=3时range取哪些值？', 'execution_requests':[]}
        self.assertEqual(simulator.choose(bank,out)['text'],'  冻结原文  ')

    def test_latest_contradiction_revokes_known(self):
        history=[{'role':'student','text':'range不包含右端点；题目要包含n。'}, {'role':'student','text':'我现在认为range包含右端点。'}]
        self.assertNotIn('boundary',baseline.known(history))

    def test_budget_is_not_pedagogical_stop(self):
        self.assertEqual(core.termination({'stop_questioning':False},3),'budget_limited')
        self.assertEqual(core.termination({'stop_questioning':True,'stop_reason':'understanding_sufficient'},2),'understanding_sufficient')

    def test_public_history_no_private_labels(self):
        public=core.public(self.case(),[{'role':'student','text':'我不确定'}],'simulated')
        prompt=core.prompt(public)
        self.assertNotIn('allowed_actions',prompt)
        self.assertNotIn('gold_causes',prompt)
        self.assertIn('我不确定',prompt)

    def test_known_version_only(self):
        result=core.check_request(self.case(),{'source_version':'invented','args':[3],'predicted_actual':None,'predicted_expected':None})
        self.assertFalse(result['input_legal'])

    def test_baseline_not_case_id_dependent(self):
        a=core.public(self.case(),[],'simulated')
        b=core.public(dict(self.case(),case_id='another'),[],'simulated')
        self.assertEqual(baseline.decide(a),baseline.decide(b))


if __name__=='__main__':unittest.main()
