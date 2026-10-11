"""One abnormal persistence regression; never a simulated successful AI answer."""
import tempfile
import time
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from web_lab.app import create_app


class FailureRunner:
    provenance = 'deterministic_transport_failure_fixture'

    def __call__(self, feature, public, artifact):
        artifact.mkdir(parents=True)
        (artifact / 'raw_response.json').write_bytes(b'')
        (artifact / 'stderr.log').write_text('deterministic_connection_error', encoding='utf8')
        raise RuntimeError('deterministic_connection_error')


class DemoRegression(unittest.TestCase):
    def test_unknown_code_first_submission_cross_session_and_failed_call_persist(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = create_app(Path(tmp), model_runner=FailureRunner())
            with TestClient(app) as client:
                r = client.post('/api/experiments', json={'feature': 'DEMO', 'case_id': 'C01',
                    'mode': 'S1', 'source_type': 'automated_test'})
                self.assertEqual(r.status_code, 201, r.text)
                eid = r.json()['session_id']
                self.assertEqual(r.json()['turns'], [])
                unknown = 'import os\ndef solve(n):\n    return 123\n'
                code = client.post(f'/api/experiments/{eid}/code', json={'source': unknown}).json()
                verified = client.post(f'/api/demo/{eid}/verify', json={'version_id': code['version_id']})
                self.assertEqual(verified.status_code, 201, verified.text)
                self.assertEqual(verified.json()['status'], 'pending_review')
                self.assertFalse(verified.json()['executed'])
                client.post(f'/api/demo/{eid}/assessment', json={'external_help': 'unknown'})
                first = client.post(f'/api/demo/{eid}/first', json={'source': unknown})
                self.assertEqual(first.status_code, 201, first.text)
                self.assertEqual(first.json()['execution_state'], 'pending_review')
                before = first.json()['source_hash']
                duplicate = client.post(f'/api/demo/{eid}/first', json={'source': 'def solve(xs):\n    return max(xs)\n'})
                self.assertEqual(duplicate.status_code, 409)
                client.post(f'/api/demo/{eid}/assessment-code', json={'source': 'def solve(xs):\n    return 7\n'})
                other = client.post('/api/experiments', json={'feature': 'DEMO', 'case_id': 'C03', 'mode': 'S0'}).json()
                self.assertEqual(client.post(f'/api/demo/{other["session_id"]}/verify',
                    json={'version_id': code['version_id']}).status_code, 422)
                self.assertEqual(client.post(f'/api/experiments/{other["session_id"]}/code',
                    json={'source': unknown, 'parent_version_id': code['version_id']}).status_code, 422)
                client.post(f'/api/experiments/{eid}/turns', json={'answer': '我的新版本还没有经过验证。',
                    'request_id': 'failure-1', 'parent_turn_id': None})
                for _ in range(100):
                    data = client.get(f'/api/experiments/{eid}').json()
                    if data['turns'][-1]['status'] == 'failed':
                        break
                    time.sleep(.02)
                self.assertEqual(data['turns'][-1]['status'], 'failed')
                self.assertIn('deterministic_connection_error', data['turns'][-1]['error'])
                self.assertEqual(data['demo']['assessment']['first']['source_hash'], before)
                self.assertEqual(data['demo']['assessment']['current_eligibility']['status'], 'unknown')
                self.assertEqual(data['session_id'], eid)
                self.assertTrue(all(e['session_id'] == eid for e in data['events']))
            # Reopen the service/database: refresh and restart must preserve the frozen first result.
            with TestClient(create_app(Path(tmp), model_runner=FailureRunner())) as again:
                data = again.get(f'/api/experiments/{eid}').json()
                self.assertEqual(data['demo']['assessment']['first']['source_hash'], before)
                self.assertEqual(data['turns'][-1]['status'], 'failed')
                self.assertEqual(data['turns'][-1]['answer_raw'], '我的新版本还没有经过验证。')
