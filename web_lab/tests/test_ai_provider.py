import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class Providers(unittest.TestCase):
    def test_api_failure_does_not_log_key_or_fabricate_reply(self):
        from web_lab.ai_provider import AIConfig, APIProvider, AIUnavailable
        from web_lab import teaching
        from web_lab.service import Service
        config=AIConfig.from_mapping({'AIC_AI_PROVIDER':'api','AIC_AI_BASE_URL':'https://example.com/v1','AIC_AI_MODEL':'fake','AIC_AI_API_KEY':'secret-for-guard'})
        def failing(*args):raise RuntimeError('secret-for-guard')
        with tempfile.TemporaryDirectory() as tmp:
            s=Service(Path(tmp),model_runner=APIProvider(config,transport=failing))
            try:
                e=s.create({'feature':'DEMO','case_id':'C01','mode':'S1'})
                s.submit(e['session_id'],'我还不确定。','failure-test',None)
                import time
                for _ in range(100):
                    detail=s.detail(e['session_id'])
                    if detail['turns'][0]['status']=='failed':break
                    time.sleep(.01)
                self.assertEqual(detail['turns'][0]['status'],'failed')
                self.assertIsNone(detail['turns'][0]['output'])
                self.assertNotIn('secret-for-guard',json.dumps(detail,ensure_ascii=False))
                logs=''.join(p.read_text(encoding='utf8',errors='ignore') for p in (Path(tmp)/'artifacts').rglob('*') if p.is_file())
                self.assertNotIn('secret-for-guard',logs)
            finally:s.close()

    def test_config_secret_validation_and_disabled(self):
        from web_lab.ai_provider import AIConfig, make_provider, AIUnavailable
        c=AIConfig.from_mapping({'AIC_AI_PROVIDER':'disabled'})
        provider=make_provider(c)
        self.assertEqual(provider.provenance,'AI_disabled')
        with self.assertRaises(AIUnavailable): provider('DEMO',{},Path('unused'))
        with self.assertRaises(ValueError): AIConfig.from_mapping({'AIC_AI_PROVIDER':'api','AIC_AI_BASE_URL':'https://example.com/v1','AIC_AI_MODEL':'test'})
        with self.assertRaises(ValueError): AIConfig.from_mapping({'AIC_AI_PROVIDER':'api','AIC_AI_BASE_URL':'https://secret@example.com/v1','AIC_AI_MODEL':'test','AIC_AI_API_KEY':'do-not-export'})
        c=AIConfig.from_mapping({'AIC_AI_PROVIDER':'api','AIC_AI_BASE_URL':'https://example.com/v1','AIC_AI_MODEL':'test','AIC_AI_API_KEY':'do-not-export'})
        self.assertNotIn('do-not-export',repr(c))
        self.assertNotIn('do-not-export',json.dumps(c.public()))
        with self.assertRaises(ValueError): AIConfig.from_mapping({'AIC_AI_PROVIDER':'typo'})
        for invalid in [{'AIC_AI_TIMEOUT_SECONDS':'NaN'}, {'AIC_AI_TIMEOUT_SECONDS':'0'},
                        {'AIC_AI_GENERATION_PARAMS':'{"max_tokens":1.5}'},
                        {'AIC_AI_GENERATION_PARAMS':'{"temperature":3}'},
                        {'AIC_AI_GENERATION_PARAMS':'{"unknown":1}'}]:
            with self.assertRaises(ValueError): AIConfig.from_mapping(invalid)
        with tempfile.TemporaryDirectory() as tmp:
            env_file=Path(tmp)/'.env'
            env_file.write_text('AIC_AI_PROVIDER=api\nAIC_AI_BASE_URL=https://example.com/v1\nAIC_AI_MODEL=fake\nAIC_AI_API_KEY=only-a-fake-key\n',encoding='utf-8-sig')
            with patch.dict('os.environ',{},clear=True):
                self.assertEqual(AIConfig.from_env(env_file).provider,'api')
                with patch.dict('os.environ',{'AIC_AI_PROVIDER':'disabled'}):
                    self.assertEqual(AIConfig.from_env(env_file).provider,'disabled')

    def test_codex_delegates_without_changing_teaching(self):
        from web_lab.ai_provider import AIConfig, make_provider
        with patch('web_lab.teaching.OfficialModel.__call__',return_value={'output':{},'checks':{},'metadata':{'CLI_success':True}}) as called:
            provider=make_provider(AIConfig.from_mapping({}))
            result=provider('DEMO',{'saved':'input'},Path('artifact'))
            called.assert_called_once()
            self.assertEqual(provider.provenance,'real_official_Codex_CLI')
            self.assertTrue(result['metadata']['provider_success'])

    def test_api_fake_transport_uses_existing_prompt_and_guard_no_paid_call(self):
        from web_lab.ai_provider import AIConfig, APIProvider
        from web_lab import teaching
        from web_lab.service import Service
        config=AIConfig.from_mapping({'AIC_AI_PROVIDER':'api','AIC_AI_BASE_URL':'https://example.com/v1','AIC_AI_MODEL':'fake','AIC_AI_API_KEY':'server-secret'})
        seen={}
        def fake(url,headers,body,timeout):
            seen.update(url=url,headers=headers,body=body)
            public=seen['public']
            output=teaching.rule_result('DEMO',public)['output']
            return {'choices':[{'message':{'content':json.dumps(output,ensure_ascii=False)}}]}
        with tempfile.TemporaryDirectory() as tmp:
            provider=APIProvider(config,transport=fake)
            s=Service(Path(tmp),model_runner=provider)
            try:
                e=s.create({'feature':'DEMO','case_id':'C01','mode':'S0'})
                public=teaching.make_public(e,[],'我还不确定。')
                seen['public']=public
                result=provider('DEMO',public,Path(tmp)/'api-artifact')
                self.assertTrue(result['metadata']['provider_success'])
                self.assertTrue(result['checks']['display_safe'])
                self.assertEqual(seen['headers']['Authorization'],'Bearer server-secret')
                self.assertNotIn('server-secret',json.dumps(result))
                self.assertEqual(seen['body']['model'],'fake')
                self.assertTrue(seen['url'].endswith('/chat/completions'))
                self.assertNotIn('server-secret',''.join(p.read_text(encoding='utf8',errors='ignore') for p in (Path(tmp)/'api-artifact').glob('*') if p.is_file()))
            finally:s.close()


if __name__=='__main__':unittest.main()
