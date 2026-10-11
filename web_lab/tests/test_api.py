import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from web_lab.app import create_app
from web_lab.teaching import rule_result


class SimulatedModel:
    """Explicit integration simulator, never advertised as a real model."""
    provenance = 'simulated_model'

    def __init__(self):
        self.calls = []
        self.gate = threading.Event()
        self.gate.set()
        self.fail = False
        self.block = False
        self.emit_start = False

    def __call__(self, feature, public, artifact):
        self.calls.append(public)
        artifact.mkdir(parents=True, exist_ok=False)
        if self.emit_start:
            (artifact / 'events.jsonl').write_text('{"type":"turn.started"}\n', encoding='utf-8')
        self.gate.wait(5)
        if self.fail:
            (artifact / 'stderr.log').write_text('模拟：网络重连失败', encoding='utf-8')
            raise RuntimeError('模拟网络失败')
        result = rule_result(feature, public)
        result['metadata'] = {'CLI_success': True, 'actual_model_call': False,
                              'provenance': self.provenance, 'usage': None}
        if self.block:
            result['checks']['display_safe'] = False
            result['checks']['issues'] = ['simulated_guard_block']
        (artifact / 'raw_response.json').write_text(json.dumps(result['output'], ensure_ascii=False), encoding='utf-8')
        return result


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.model = SimulatedModel()
        self.app = create_app(self.root, model_runner=self.model)
        self.client_context = TestClient(self.app)
        self.client = self.client_context.__enter__()

    def tearDown(self):
        self.model.gate.set()
        self.client_context.__exit__(None, None, None)
        self.temp.cleanup()

    def create(self, feature='F01', mode='S0', **extra):
        data = {'feature': feature, 'case_id': '01' if feature == 'F01' else 'C02',
                'mode': mode, 'source_type': 'automated_test', **extra}
        r = self.client.post('/api/experiments', json=data)
        self.assertEqual(r.status_code, 201, r.text)
        return r.json()['experiment_id']

    def detail(self, eid):
        response = self.client.get('/api/experiments/' + eid)
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def settled(self, eid):
        deadline = time.monotonic() + 6
        while time.monotonic() < deadline:
            data = self.detail(eid)
            if data['turns'] and data['turns'][-1]['status'] not in ['queued', 'connecting', 'generating']:
                return data
            time.sleep(.02)
        self.fail('worker did not finish')

    def reply(self, eid, text, key='answer-1'):
        detail = self.detail(eid)
        return self.client.post('/api/experiments/' + eid + '/turns', json={
            'answer': text, 'request_id': key,
            'parent_turn_id': detail['turns'][-1]['turn_id'] if detail['turns'] else None})

    def test_home_and_catalog(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        cases = self.client.get('/api/cases').json()
        self.assertEqual({c['feature'] for c in cases}, {'F01', 'F02'})
        self.assertEqual(len(cases), 5)

    def test_f01_s0_one_reply_persisted_verbatim(self):
        eid = self.create()
        self.assertEqual(self.reply(eid, '  range不包含3，只取1和2。  ').status_code, 202)
        data = self.settled(eid)
        self.assertEqual(data['status'], 'completed')
        self.assertEqual(data['turns'][0]['answer_raw'], '  range不包含3，只取1和2。  ')
        self.assertTrue(data['turns'][0]['checks']['display_safe'])
        self.assertEqual(len(self.model.calls), 0)
        self.assertEqual(self.reply(eid, '继续', 'later').status_code, 409)

    def test_f02_stops_early(self):
        eid = self.create('F02')
        self.settled(eid)
        self.assertEqual(self.reply(eid, 'range不包含右端点n；题目要求包含n；s=i赋值覆盖以前的值。').status_code, 202)
        data = self.settled(eid)
        self.assertEqual(data['status'], 'completed')
        self.assertEqual(data['end_reason'], 'understanding_sufficient')
        self.assertEqual(len(data['turns']), 2)
        self.assertEqual(len(data['turns'][0]['public_input']['history']), 0)
        self.assertEqual(len(data['turns'][1]['public_input']['history']), 2)

    def test_f02_three_teacher_outputs_maximum(self):
        eid = self.create('F02')
        self.settled(eid)
        for n in range(2):
            self.assertEqual(self.reply(eid, '我还不确定', 'r' + str(n)).status_code, 202)
            self.settled(eid)
        data = self.detail(eid)
        self.assertEqual(len(data['turns']), 3)
        self.assertEqual(data['end_reason'], 'budget_limited')

    def test_async_and_idempotency(self):
        self.model.gate.clear()
        eid = self.create(mode='S1')
        started = time.monotonic()
        response = self.reply(eid, ' 我的回答 ', 'same')
        self.assertEqual(response.status_code, 202)
        self.assertLess(time.monotonic() - started, 1)
        self.assertEqual(self.detail(eid)['turns'][0]['answer_raw'], ' 我的回答 ')
        self.assertEqual(self.client.get('/api/stats').status_code, 200)
        duplicate = self.client.post('/api/experiments/' + eid + '/turns', json={
            'answer': ' 我的回答 ', 'request_id': 'same', 'parent_turn_id': None})
        self.assertEqual(duplicate.status_code, 202)
        self.assertEqual(self.reply(eid, '第二份', 'different').status_code, 409)
        self.model.gate.set()
        self.settled(eid)
        self.assertEqual(len(self.model.calls), 1)
        self.assertEqual(self.detail(eid)['source_type'], 'automated_test')

    def test_failed_attempt_retry_preserves_first(self):
        self.model.fail = True
        eid = self.create(mode='S1')
        self.reply(eid, '原始回答')
        failed = self.settled(eid)
        tid = failed['turns'][0]['turn_id']
        self.assertEqual(failed['status'], 'failed')
        self.assertIn('模拟网络失败', failed['turns'][0]['attempts'][0]['error'])
        self.model.fail = False
        retry = self.client.post('/api/turns/' + tid + '/retry', json={'reason': '人工检查网络后重试', 'request_id': 'retry-1'})
        self.assertEqual(retry.status_code, 202, retry.text)
        result = self.settled(eid)
        attempts = result['turns'][0]['attempts']
        self.assertEqual(len(attempts), 2)
        self.assertEqual(attempts[0]['status'], 'failed')
        self.assertEqual(attempts[1]['retry_reason'], '人工检查网络后重试')
        export = self.client.get('/api/export/json', params={'experiment_id': eid}).json()
        self.assertTrue(export['experiments'][0]['turns'][0]['attempts'][0]['artifacts'])

    def test_feedback_is_append_only_and_unrated_is_not_correct(self):
        eid = self.create()
        self.reply(eid, '不确定')
        tid = self.settled(eid)['turns'][0]['turn_id']
        endpoint = '/api/turns/' + tid + '/feedback'
        self.assertEqual(self.client.post(endpoint, json={'on_topic': 'no', 'notes': '第一版'}).status_code, 201)
        self.assertEqual(self.client.post(endpoint, json={'on_topic': 'uncertain', 'satisfaction': 3}).status_code, 201)
        feedback = self.detail(eid)['turns'][0]['feedback']
        self.assertEqual(len(feedback), 2)
        self.assertEqual(feedback[0]['on_topic'], 'no')
        stats = self.client.get('/api/stats').json()
        self.assertEqual(stats['feedback']['on_topic']['yes'], 0)
        self.assertEqual(stats['feedback']['on_topic']['uncertain'], 1)
        self.assertEqual(stats['feedback']['fact_error']['unrated'], 1)
        self.assertEqual(self.client.post(endpoint, json={'satisfaction': 6}).status_code, 422)

    def test_unverified_code_never_replaces_frozen_source(self):
        eid = self.create('F02', 'S1')
        initial = self.settled(eid)
        source = 'raise RuntimeError("THIS MUST NEVER EXECUTE")'
        r = self.client.post('/api/experiments/' + eid + '/code', json={'source': source})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()['verification_status'], 'unverified')
        self.reply(eid, '新版代码已提交')
        data = self.settled(eid)
        value = data['turns'][1]['public_input']
        self.assertEqual(value['case']['source'], initial['case_snapshot']['source'])
        self.assertEqual(value['unverified_code_records'][-1]['source'], source)
        self.assertFalse(data['code_versions'][-1]['execution_allowed'])

    def test_pause_and_end_during_call_preserve_result(self):
        self.model.gate.clear()
        eid = self.create(mode='S1')
        self.reply(eid, '不确定')
        self.assertEqual(self.client.post('/api/experiments/' + eid + '/control', json={'action': 'end'}).status_code, 200)
        self.model.gate.set()
        data = self.settled(eid)
        self.assertEqual(data['status'], 'completed')
        self.assertEqual(data['end_reason'], 'manual_end')
        self.assertIsNotNone(data['turns'][0]['output'])

    def test_history_export_and_notes(self):
        eid = self.create(name='中文实验')
        self.reply(eid, '不确定')
        self.settled(eid)
        self.assertEqual(self.client.post('/api/experiments/' + eid + '/notes', json={'text': '补充备注'}).status_code, 201)
        history = self.client.get('/api/experiments', params={'feature': 'F01', 'mode': 'S0'}).json()
        self.assertEqual(history[0]['experiment_id'], eid)
        data = self.client.get('/api/export/json').json()
        self.assertEqual(data['experiments'][0]['notes'][0]['text'], '补充备注')
        for kind in ['experiments', 'turns', 'attempts']:
            csv = self.client.get('/api/export/csv', params={'kind': kind, 'experiment_id': eid})
            self.assertEqual(csv.status_code, 200)
            self.assertTrue(csv.content.startswith(b'\xef\xbb\xbf'))
        self.assertEqual(self.client.get('/api/export/json', params={'experiment_id': 'absent'}).status_code, 404)

    def test_refresh_and_restart_keep_data(self):
        eid = self.create()
        self.reply(eid, '原样')
        self.settled(eid)
        second = create_app(self.root, model_runner=SimulatedModel())
        with TestClient(second) as client:
            self.assertEqual(client.get('/api/experiments/' + eid).json()['turns'][0]['answer_raw'], '原样')

    def test_bad_host_origin_and_paths(self):
        self.assertEqual(self.client.get('/api/cases', headers={'Host': 'evil.example'}).status_code, 400)
        self.assertEqual(self.client.post('/api/experiments', headers={'Origin': 'https://evil.example'}, json={}).status_code, 403)
        self.assertEqual(self.client.get('/api/artifacts/unknown/../../auth.json').status_code, 404)
        self.assertEqual(self.client.post('/api/experiments', json={'feature': 'F03', 'case_id': '01', 'mode': 'S0'}).status_code, 422)

    def test_s0_is_not_queued_behind_slow_models(self):
        self.model.gate.clear()
        for n in range(2):
            eid = self.create(mode='S1')
            self.reply(eid, '等待模型', str(n))
        eid = self.create()
        self.reply(eid, '不确定')
        self.assertEqual(self.settled(eid)['status'], 'completed')
        self.assertFalse(self.model.gate.is_set())

    def test_new_experiment_duplicate_request_is_idempotent(self):
        a = self.create(request_id='create-id')
        b = self.create(request_id='create-id')
        self.assertEqual(a, b)
        self.assertEqual(len(self.client.get('/api/experiments').json()), 1)

    def test_other_evaluation_sources_do_not_become_user_feedback(self):
        eid = self.create()
        self.reply(eid, '不确定')
        tid = self.settled(eid)['turns'][0]['turn_id']
        self.client.post('/api/turns/' + tid + '/feedback', json={'evaluation_source': 'ai_auxiliary', 'on_topic': 'yes'})
        stats = self.client.get('/api/stats').json()
        self.assertEqual(stats['feedback']['on_topic']['yes'], 0)
        self.assertEqual(stats['feedback']['on_topic']['unrated'], 1)
        self.assertEqual(stats['evaluation_sources']['ai_auxiliary'], 1)

    def test_recover_pending_call_does_not_resample(self):
        eid = self.create(mode='S1')
        service = self.app.state.service
        with service.store.connection(write=True) as db:
            e = service.store.experiment(db, eid)
            service.new_turn(db, e, '崩溃前原文', 'crash-request')
        second = create_app(self.root, model_runner=SimulatedModel())
        with TestClient(second) as client:
            e = client.get('/api/experiments/' + eid).json()
            self.assertEqual(e['turns'][0]['answer_raw'], '崩溃前原文')
            self.assertEqual(e['status'], 'failed')
            self.assertEqual(e['end_reason'], 'server_restarted')
            self.assertEqual(e['turns'][0]['attempts'][0]['status'], 'failed')
        self.assertEqual(len(self.model.calls), 0)

    def test_guard_block_keeps_raw_response(self):
        self.model.block = True
        eid = self.create(mode='S1')
        self.reply(eid, '不确定')
        data = self.settled(eid)
        self.assertEqual(data['turns'][0]['status'], 'blocked')
        self.assertIsNotNone(data['turns'][0]['attempts'][0]['raw_output'])
        self.assertFalse(data['turns'][0]['checks']['display_safe'])
        self.assertIn('web_validation.json', data['turns'][0]['attempts'][0]['artifact_names'])
        exported = self.client.get('/api/export/json', params={'experiment_id': eid}).json()
        names = [a['name'] for a in exported['experiments'][0]['turns'][0]['attempts'][0]['artifacts']]
        self.assertIn('web_validation.json', names)

    def test_paused_finished_f01_can_resume_to_completion(self):
        self.model.gate.clear()
        eid = self.create(mode='S1')
        self.reply(eid, '不确定')
        self.client.post('/api/experiments/' + eid + '/control', json={'action': 'pause'})
        self.model.gate.set()
        self.assertEqual(self.settled(eid)['status'], 'paused')
        resumed = self.client.post('/api/experiments/' + eid + '/control', json={'action': 'resume'})
        self.assertEqual(resumed.status_code, 200)
        self.assertEqual(resumed.json()['status'], 'completed')

    def test_backup_restores_dialogue_and_artifacts(self):
        from web_lab.backup import backup
        from web_lab.store import Store
        eid = self.create()
        self.reply(eid, '备份中文数据')
        self.settled(eid)
        with tempfile.TemporaryDirectory() as destination:
            target = backup(self.root, Path(destination) / 'snapshot')
            restored = Store(target).get(eid)
            self.assertEqual(restored['turns'][0]['answer_raw'], '备份中文数据')
            self.assertTrue((target / restored['turns'][0]['attempts'][0]['artifact_dir'] / 'raw_response.json').exists())

    def test_generation_event_observation_is_persisted(self):
        self.model.emit_start = True
        self.model.gate.clear()
        eid = self.create(mode='S1')
        self.reply(eid, '事件观察')
        deadline = time.monotonic() + 3
        data = self.detail(eid)
        while not data['turns'][0]['generation_started_at'] and time.monotonic() < deadline:
            time.sleep(.05)
            data = self.detail(eid)
        self.assertEqual(data['turns'][0]['status'], 'generating')
        self.assertIsNotNone(data['turns'][0]['attempts'][0]['generation_started_at'])
        self.model.gate.set()
        self.settled(eid)

    def test_initial_snapshot_and_csv_formula_escape(self):
        eid = self.create(name='=SUM(1,2)')
        self.assertEqual(self.detail(eid)['initial_input_snapshot']['previous_question'],
                         self.detail(eid)['case_snapshot']['teaching_question'])
        self.reply(eid, '@原始文本')
        self.settled(eid)
        raw = self.client.get('/api/export/csv', params={'kind': 'turns', 'experiment_id': eid}).content.decode('utf-8-sig')
        self.assertIn("'@原始文本", raw)
        self.assertIn("'=SUM", raw)
        self.assertEqual(self.detail(eid)['turns'][0]['answer_raw'], '@原始文本')

    def test_date_filter_uses_shanghai_calendar(self):
        eid = self.create()
        with self.app.state.service.store.connection(write=True) as db:
            self.app.state.service.store.update(db, 'experiments', 'experiment_id', eid,
                                               {'created_at': '2026-10-10T18:00:00+00:00'})
        self.assertEqual(len(self.client.get('/api/experiments', params={'date': '2026-10-11'}).json()), 1)
        self.assertEqual(len(self.client.get('/api/experiments', params={'date': '2026-10-10'}).json()), 0)

    def test_simulated_model_cannot_label_itself_real_user_or_real_ai(self):
        eid = self.create(mode='S1', source_type='real_user')
        self.reply(eid, '自动数据')
        e = self.settled(eid)
        self.assertEqual(e['source_type'], 'automated_test')
        self.assertEqual(e['model_provenance'], 'simulated_model')
        self.assertEqual(self.client.get('/api/stats').json()['ai_calls']['denominator'], 0)


if __name__ == '__main__':
    unittest.main()
