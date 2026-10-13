"""V3 read-only summaries: real failures, current evidence and source separation."""
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from web_lab.app import create_app
from web_lab.store import uid, utc
from web_lab.tests.test_demo import FailureRunner


class LearningV3(unittest.TestCase):
    def test_crlf_passed_by_existing_judge_is_not_review_failure(self):
        from web_lab.learning_records import review_kind
        self.assertIsNone(review_kind({'status': 'passed', 'results': [
            {'status': 'passed', 'stdout': '6\r\n', 'expected_output': '6\n'}]}))

    def test_summary_preserves_failed_run_after_new_version_without_evidence(self):
        with tempfile.TemporaryDirectory() as tmp, TestClient(create_app(Path(tmp), FailureRunner())) as c:
            e = c.post('/api/experiments', json={'feature': 'DEMO', 'case_id': 'C01',
                'mode': 'S0', 'source_type': 'automated_test', 'input_origin': 'automated_test'}).json()
            eid, vid = e['session_id'], e['current_code_version_id']
            with c.app.state.service.store.connection(write=True) as db:
                c.app.state.service.store.insert(db, 'sandbox_jobs', {'task_id': uid(), 'session_id': eid,
                    'version_id': vid, 'source_sha256': e['code_versions'][0]['source_sha256'],
                    'request_id': uid(), 'mode': 'run', 'inputs': [3], 'contract_id': 'test-only',
                    'contract_sha256': '0'*64, 'created_at': utc(), 'completed_at': utc(),
                    'status': 'completed', 'executed': True, 'results': [
                        {'visible': True, 'status': 'completed', 'stdout': '3\n', 'expected_output': '6\n'},
                        {'visible': False, 'status': 'failed', 'stdout': 'secret', 'expected_output': 'private'}],
                    'elapsed_seconds': 1, 'error': None})
            v = c.post(f'/api/experiments/{eid}/code', json={'source': 'def solve(n):\n    return n\n',
                'parent_version_id': vid, 'input_origin': 'automated_test'}).json()
            response = c.get('/api/learning/records')
            self.assertEqual(response.status_code, 200, response.text)
            record = response.json()[0]
            self.assertEqual(record['current_code_version_id'], v['version_id'])
            self.assertIsNone(record['current_job'])
            self.assertEqual(record['review_count'], 1)
            self.assertEqual(record['last_review']['version_id'], vid)
            self.assertEqual(record['last_review']['kind'], 'output_mismatch')
            self.assertEqual(record['source_type'], 'automated_test')
            self.assertNotIn('secret', response.text)
            self.assertNotIn('private', response.text)
            self.assertNotIn('source_sha256', response.text)
            self.assertEqual(c.get('/learning-review').status_code, 200)

    def test_legacy_empty_session_has_no_invented_progress(self):
        with tempfile.TemporaryDirectory() as tmp, TestClient(create_app(Path(tmp), FailureRunner())) as c:
            e = c.post('/api/experiments', json={'feature': 'DEMO', 'case_id': 'C03', 'mode': 'S0'}).json()
            response = c.get('/api/learning/records')
            self.assertEqual(response.status_code, 200, response.text)
            record = response.json()[0]
            self.assertEqual(record['experiment_id'], e['session_id'])
            self.assertEqual(record['review_count'], 0)
            self.assertEqual(record['run_count'], 0)
            self.assertIsNone(record['current_job'])
            self.assertNotIn('mastery', record)
