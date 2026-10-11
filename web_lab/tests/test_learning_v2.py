"""Small V2 contract regression: provenance, reviewed boundary and durable errors."""
import tempfile
import time
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from web_lab.app import create_app
from web_lab.tests.test_demo import FailureRunner


class LearningV2(unittest.TestCase):
    def test_learning_routes_and_per_input_origin_do_not_infer_human_from_session_label(self):
        with tempfile.TemporaryDirectory() as tmp, TestClient(create_app(Path(tmp), FailureRunner())) as c:
            self.assertIn('learning.js', c.get('/').text)
            self.assertIn('app.js', c.get('/manage').text)
            e = c.post('/api/experiments', json={'feature':'DEMO', 'case_id':'C01', 'mode':'S0',
                'source_type':'real_user', 'input_origin':'automated_test', 'entry_point':'learning'}).json()
            eid = e['session_id']
            self.assertTrue(c.get(f'/api/experiments/{eid}').json()['demo']['version_readiness'][0]['can_verify'])
            v = c.post(f'/api/experiments/{eid}/code', json={'source':'import os\ndef solve(n):\n    return 7\n',
                'input_origin':'automated_test'}).json()
            d = c.get(f'/api/experiments/{eid}').json()
            self.assertFalse(next(x for x in d['demo']['version_readiness'] if x['version_id']==v['version_id'])['can_verify'])
            blocked = c.post(f'/api/demo/{eid}/verify',json={'version_id':v['version_id'],'input_origin':'automated_test'}).json()
            self.assertFalse(blocked['executed'])
            self.assertEqual(blocked['input_origin']['kind'],'automated_test')
            c.post(f'/api/experiments/{eid}/ui-actions',json={'action':'view_evidence','input_origin':'automated_test'})
            body={'answer':'我还不确定。','request_id':'same-input','parent_turn_id':None,'input_origin':'automated_test'}
            self.assertEqual(c.post(f'/api/experiments/{eid}/turns',json=body).status_code,202)
            self.assertEqual(c.post(f'/api/experiments/{eid}/turns',json=body).status_code,202)
            d=c.get(f'/api/experiments/{eid}').json()
            self.assertEqual(len(d['turns']),1)
            self.assertEqual(d['turns'][0]['public_input']['answer_input_origin']['kind'],'automated_test')
            self.assertEqual(c.get('/api/stats').json()['answer_origins']['automated_test'],1)
            self.assertEqual(c.get('/api/stats').json()['answer_origins'].get('manual_browser',0),0)
            # A correction is appended, never rewrites the saved model input.
            with c.app.state.service.store.connection(write=True) as db:
                c.app.state.service.store.event(db,eid,'input_origin_corrected',{
                    'turn_id':d['turns'][0]['turn_id'],'kind':'simulated_student','reason':'declared test correction'})
            self.assertEqual(c.get('/api/stats').json()['answer_origins']['simulated_student'],1)
            after=c.get(f'/api/experiments/{eid}').json()
            self.assertEqual(after['turns'][0]['public_input']['answer_input_origin']['kind'],'automated_test')
            self.assertEqual(c.get('/api/export/json',params={'experiment_id':eid}).status_code,200)
            self.assertIn('input_origin',c.get('/api/export/csv',params={'experiment_id':eid}).text)

    def test_failed_reply_and_first_submission_keep_actual_origin_on_reopen(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestClient(create_app(Path(tmp),FailureRunner())) as c:
                e=c.post('/api/experiments',json={'feature':'DEMO','case_id':'C01','mode':'S1','source_type':'real_user'}).json()
                eid=e['session_id']
                sent=c.post(f'/api/experiments/{eid}/turns',json={'answer':'模拟学生不确定。','request_id':'fail',
                    'parent_turn_id':None,'input_origin':'simulated_student'})
                self.assertEqual(sent.status_code,202,sent.text)
                for _ in range(100):
                    d=c.get(f'/api/experiments/{eid}').json()
                    if d['turns'][0]['status']=='failed': break
                    time.sleep(.02)
                self.assertEqual(d['turns'][0]['status'],'failed')
                c.post(f'/api/demo/{eid}/assessment',json={'external_help':'unknown'})
                first=c.post(f'/api/demo/{eid}/first',json={'source':'def solve(xs):\n    return 0\n','input_origin':'automated_test'}).json()
                self.assertEqual(first['submission_origin'],'frozen_simulated_submission')
                self.assertEqual(c.post(f'/api/demo/{eid}/first',json={'source':'def solve(xs):\n    return 1\n'}).status_code,409)
            with TestClient(create_app(Path(tmp),FailureRunner())) as c:
                d=c.get(f'/api/experiments/{eid}').json()
                self.assertEqual(d['turns'][0]['answer_raw'],'模拟学生不确定。')
                self.assertEqual(d['turns'][0]['public_input']['answer_input_origin']['kind'],'simulated_student')
                self.assertEqual(d['demo']['assessment']['first']['source_hash'],first['source_hash'])
                self.assertTrue(d['turns'][0]['attempts'][0]['raw_output'] is not None)
