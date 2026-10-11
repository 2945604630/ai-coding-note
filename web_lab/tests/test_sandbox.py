"""Control-plane tests only. Never execute student source on host Python."""
import hashlib
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from web_lab.app import create_app
from web_lab.tests.test_demo import FailureRunner


class SandboxAPI(unittest.TestCase):
    def test_custom_run_preserves_optional_reference_without_judging(self):
        # Fake transport only; even a reviewed mismatch remains a run, not a verdict.
        with tempfile.TemporaryDirectory() as tmp, TestClient(create_app(Path(tmp), FailureRunner())) as c:
            e=c.post('/api/experiments',json={'feature':'DEMO','case_id':'C01','mode':'S0'}).json()
            eid=e['session_id'];v=e['code_versions'][0];runtime=c.app.state.service.sandbox.runtime
            body={'version_id':v['version_id'],'source_sha256':v['source_sha256']}
            with patch.object(runtime,'status',return_value={'ready':True}), patch.object(runtime,'execute',return_value={'status':'completed','executed':True,'cleaned':True,'stdout':'3\n','stderr':'','error':None}):
                for n,expected in [(3,'6\n'),(8,None)]:
                    job=c.post(f'/api/experiments/{eid}/sandbox/run',json={**body,'input':n,'request_id':'reference-'+str(n)}).json()
                    for _ in range(100):
                        job=c.get(f'/api/experiments/{eid}/sandbox/jobs/{job["task_id"]}').json()
                        if job['status'] not in {'queued','running'}:break
                        time.sleep(.01)
                    self.assertEqual(job['status'],'completed')
                    self.assertEqual(job['results'][0]['expected_output'],expected)

    def test_service_exception_and_unconfirmed_execution_cannot_pass(self):
        # Deterministic control-plane fault injection, not real program execution.
        with tempfile.TemporaryDirectory() as tmp, TestClient(create_app(Path(tmp), FailureRunner())) as c:
            e=c.post('/api/experiments',json={'feature':'DEMO','case_id':'C01','mode':'S0'}).json()
            eid=e['session_id'];v=e['code_versions'][0];runtime=c.app.state.service.sandbox.runtime
            body={'version_id':v['version_id'],'source_sha256':v['source_sha256'],'request_id':'failure'}
            with patch.object(runtime,'status',return_value={'ready':True}), patch.object(runtime,'execute',side_effect=RuntimeError('deterministic broker failure')):
                job=c.post(f'/api/experiments/{eid}/sandbox/submit',json=body).json()
                for _ in range(100):
                    job=c.get(f'/api/experiments/{eid}/sandbox/jobs/{job["task_id"]}').json()
                    if job['status'] not in {'queued','running'}:break
                    time.sleep(.01)
                self.assertEqual(job['status'],'service_error');self.assertFalse(job['executed'])
            with patch.object(runtime,'status',return_value={'ready':True}), patch.object(runtime,'execute',return_value={'status':'completed','executed':False,'cleaned':True,'stdout':'0\n','stderr':'','error':None}):
                job=c.post(f'/api/experiments/{eid}/sandbox/submit',json={**body,'request_id':'unconfirmed'}).json()
                for _ in range(100):
                    job=c.get(f'/api/experiments/{eid}/sandbox/jobs/{job["task_id"]}').json()
                    if job['status'] not in {'queued','running'}:break
                    time.sleep(.01)
                self.assertEqual(job['status'],'service_error');self.assertFalse(job['executed'])

    def test_unavailable_is_persisted_and_does_not_unlock_f03(self):
        with tempfile.TemporaryDirectory() as tmp, TestClient(create_app(Path(tmp), FailureRunner())) as c:
            e = c.post('/api/experiments', json={'feature':'DEMO','case_id':'C01','mode':'S0'}).json()
            eid = e['session_id']
            source = 'def solve(n):\n    return n*(n+1)//2\n'
            v = c.post(f'/api/experiments/{eid}/code', json={'source':source}).json()
            body = {'version_id':v['version_id'],'source_sha256':v['source_sha256'],
                    'request_id':'run-one','input':3}
            r = c.post(f'/api/experiments/{eid}/sandbox/run', json=body)
            self.assertEqual(r.status_code, 202, r.text)
            job = r.json()
            self.assertEqual(job['status'], 'unavailable')
            self.assertFalse(job['executed'])
            self.assertEqual(job['source_sha256'], hashlib.sha256(source.encode()).hexdigest())
            self.assertEqual(c.post(f'/api/experiments/{eid}/sandbox/run', json=body).json()['task_id'],job['task_id'])
            self.assertEqual(len(c.get(f'/api/experiments/{eid}/sandbox/jobs').json()),1)
            old = c.post(f'/api/demo/{eid}/verify', json={'version_id':v['version_id']}).json()
            self.assertFalse(old['executed'])
            detail = c.get(f'/api/experiments/{eid}').json()
            self.assertFalse(detail['code_versions'][-1]['execution_allowed'])
            self.assertEqual(detail['sandbox']['jobs'][0]['task_id'],job['task_id'])
            export = c.get('/api/export/json',params={'experiment_id':eid}).json()
            self.assertEqual(export['experiments'][0]['sandbox_jobs'][0]['task_id'],job['task_id'])

    def test_version_hash_cross_session_and_old_request_guards(self):
        with tempfile.TemporaryDirectory() as tmp, TestClient(create_app(Path(tmp), FailureRunner())) as c:
            e = c.post('/api/experiments',json={'feature':'DEMO','case_id':'C01','mode':'S0'}).json()
            eid=e['session_id']; v=e['code_versions'][0]
            url=f'/api/experiments/{eid}/sandbox/run'
            body={'version_id':v['version_id'],'source_sha256':v['source_sha256'],'request_id':'same','input':3}
            self.assertEqual(c.post(url,json={**body,'source_sha256':'0'*64}).status_code,409)
            self.assertEqual(c.post(url,json={**body,'input':True}).status_code,422)
            self.assertEqual(c.post(url,json={**body,'input':9}).status_code,422)
            self.assertEqual(c.post(url,json={**body,'image':'attacker'}).status_code,422)
            first=c.post(url,json=body).json()
            v2=c.post(f'/api/experiments/{eid}/code',json={'source':'def solve(n):\n    return 7\n'}).json()
            self.assertEqual(c.post(url,json={**body,'version_id':v2['version_id'],'source_sha256':v2['source_sha256']}).status_code,409)
            second=c.post(url,json={**body,'request_id':'fresh'}).json()
            self.assertNotEqual(first['task_id'],second['task_id'])
            other=c.post('/api/experiments',json={'feature':'DEMO','case_id':'C03','mode':'S0'}).json()['session_id']
            self.assertEqual(c.post(f'/api/experiments/{other}/sandbox/run',json=body).status_code,422)
            self.assertEqual(c.get(f'/api/experiments/{other}/sandbox/jobs/{first["task_id"]}').status_code,404)

    def test_hidden_details_are_redacted(self):
        from web_lab.sandbox_service import public_job
        job={'mode':'submit','inputs':[0,8],'results':[
            {'visible':True,'input':0,'stdout':'0\n','expected_output':'0\n','status':'passed'},
            {'visible':False,'input':8,'stdout':'hidden','stderr':'hidden','expected_output':'36\n','status':'failed'}]}
        public=public_job(job)
        self.assertNotIn('inputs',public)
        self.assertEqual(public['hidden_summary'],{'total':1,'passed':0})
        self.assertNotIn('hidden',str(public['results']))


class DockerPolicy(unittest.TestCase):
    def test_invalid_utf8_cannot_expand_stored_output_beyond_limit(self):
        from web_lab.sandbox_runtime import bounded_text, OUTPUT_BYTES
        stdout,stderr=bounded_text(b'\xff'*OUTPUT_BYTES,b'error')
        self.assertLessEqual(len((stdout+stderr).encode('utf8')),OUTPUT_BYTES)
        stdout,stderr=bounded_text(b'ok\n',b'error\n')
        self.assertEqual((stdout,stderr),('ok\n','error\n'))

    def test_policy_has_no_mounts_ports_privilege_or_user_commands(self):
        from web_lab.sandbox_runtime import DockerRuntime, IMAGE_ID_RE
        runtime=DockerRuntime(Path('unused'))
        args=runtime.create_args('aic-task-test','sha256:'+'a'*64)
        self.assertIn('--network=none',args)
        self.assertIn('--read-only',args)
        self.assertIn('--user=65534:65534',args)
        self.assertIn('--cap-drop=ALL',args)
        self.assertNotIn('--privileged',args)
        self.assertFalse(any(x in args for x in ['-v','--volume','--mount','-p','--publish']))
        self.assertTrue(IMAGE_ID_RE.fullmatch(args[-1]))

    def test_cleanup_failure_cannot_report_success(self):
        from web_lab.sandbox_runtime import execution_status
        self.assertEqual(execution_status(0,False,False,False,False),'service_error')
        self.assertEqual(execution_status(0,False,False,True,True),'output_limit')
        self.assertEqual(execution_status(0,False,True,False,True),'timeout')
        self.assertEqual(execution_status(1,False,False,False,True),'exception')
        self.assertEqual(execution_status(0,True,False,False,True),'resource_limit')


if __name__=='__main__': unittest.main()
