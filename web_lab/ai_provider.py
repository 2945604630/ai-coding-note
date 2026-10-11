"""Server-side providers reuse the frozen protocol and the web evidence adapter."""
from dataclasses import dataclass, field
import json
import math
import os
from pathlib import Path
from typing import Protocol
from urllib.parse import urlsplit
import urllib.error
import urllib.request

from . import teaching


class AIUnavailable(RuntimeError):
    pass


class AIProvider(Protocol):
    provenance: str
    def __call__(self, feature: str, public: dict, artifact: Path) -> dict: ...
    def public_config(self) -> dict: ...


@dataclass(frozen=True)
class AIConfig:
    provider: str = 'codex_cli'
    base_url: str = ''
    model: str = ''
    api_key: str = field(default='',repr=False)
    timeout: float = 60
    parameters: dict = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, env):
        provider=env.get('AIC_AI_PROVIDER','codex_cli').strip()
        if provider not in {'codex_cli','api','disabled'}:
            raise ValueError('AIC_AI_PROVIDER 必须为 codex_cli、api 或 disabled')
        base=env.get('AIC_AI_BASE_URL','').strip().rstrip('/')
        model=env.get('AIC_AI_MODEL','').strip()
        key=env.get('AIC_AI_API_KEY','')
        try:
            timeout=float(env.get('AIC_AI_TIMEOUT_SECONDS','60'))
            parameters=json.loads(env.get('AIC_AI_GENERATION_PARAMS','{}'))
            if not math.isfinite(timeout) or not 1<=timeout<=1200 or not isinstance(parameters,dict):raise ValueError()
            ranges={'temperature':(0,2),'top_p':(0,1),'max_tokens':(1,8192)}
            for name,value in parameters.items():
                if name not in ranges or type(value) not in (int,float) or not math.isfinite(value) or not ranges[name][0]<=value<=ranges[name][1]:raise ValueError()
                if name=='max_tokens' and type(value) is not int:raise ValueError()
        except (ValueError,TypeError):
            raise ValueError('AI 超时或生成参数无效；允许 temperature、top_p、max_tokens') from None
        if provider=='api':
            parsed=urlsplit(base)
            local=parsed.hostname in {'localhost','127.0.0.1','::1'}
            if not model or not key or not parsed.hostname or parsed.scheme not in {'http','https'} or (parsed.scheme=='http' and not local) or parsed.username or parsed.password or parsed.query or parsed.fragment:
                raise ValueError('api 需要 Model、服务器 API Key 和 HTTPS Base URL；仅本机允许 HTTP，URL 不得携带凭据/查询参数')
            if any(ch in key for ch in '\r\n') or len(key)>4096 or len(model)>200:
                raise ValueError('AI 密钥或 Model 格式无效')
        return cls(provider,base,model,key,timeout,parameters)

    @classmethod
    def from_env(cls, env_file=None):
        values={}
        if env_file and Path(env_file).exists():
            for line in Path(env_file).read_text(encoding='utf-8-sig').splitlines():
                line=line.strip()
                if not line or line.startswith('#'):continue
                if '=' not in line:raise ValueError('.env 需要 KEY=VALUE 格式')
                name,value=line.split('=',1);value=value.strip()
                if value[:1] in {'"',"'"} and value[-1:]==value[:1]:value=value[1:-1]
                values[name.strip()]=value
        values.update({k:v for k,v in os.environ.items() if k.startswith('AIC_AI_')})
        return cls.from_mapping(values)

    def public(self):
        # Endpoint/key remain entirely server-side; no HTTP credentials in exports.
        return {'provider':self.provider,'model':self.model if self.provider=='api' else
                teaching.f01.MODEL if self.provider=='codex_cli' else None,
                'timeout_seconds':self.timeout if self.provider=='api' else teaching.f01.TIMEOUT,
                'generation_parameters':self.parameters if self.provider=='api' else {},
                'key_configured':bool(self.api_key) if self.provider=='api' else False}


class CodexCLIProvider:
    provenance='real_official_Codex_CLI'
    def __init__(self, config):
        self.config=config;self.delegate=teaching.OfficialModel()
    def public_config(self):return self.config.public()
    def __call__(self,feature,public,artifact):
        result=self.delegate(feature,public,artifact)
        result['metadata']={**(result.get('metadata') or {}),'provider':'codex_cli',
                            'provider_success':bool((result.get('metadata') or {}).get('CLI_success'))}
        return result


class DisabledProvider:
    provenance='AI_disabled'
    def __init__(self, config):self.config=config
    def public_config(self):return self.config.public()
    def __call__(self,feature,public,artifact):
        raise AIUnavailable('AI Provider 已禁用；请选择固定问题模式')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise AIUnavailable('AI API 重定向被拒绝')


def http_transport(url,headers,body,timeout):
    request=urllib.request.Request(url,data=json.dumps(body,ensure_ascii=False).encode('utf8'),headers=headers,method='POST')
    try:
        with urllib.request.build_opener(NoRedirect).open(request,timeout=timeout) as response:
            raw=response.read(1048577)
            if len(raw)>1048576:raise AIUnavailable('AI API 响应超出 1 MiB 限制')
        return json.loads(raw)
    except urllib.error.HTTPError as exc:
        raise AIUnavailable('AI API HTTP '+str(exc.code)) from None
    except (urllib.error.URLError,TimeoutError,OSError,ValueError):
        raise AIUnavailable('AI API 网络、超时或响应格式错误') from None


class APIProvider:
    provenance='real_external_AI_API'
    def __init__(self,config,transport=None):
        self.config=config;self.transport=transport or http_transport
    def public_config(self):return self.config.public()
    def redact(self,value):
        # Even an upstream response that echoes the exact key cannot export it.
        if isinstance(value,str):return value.replace(self.config.api_key,'[REDACTED]')
        if isinstance(value,list):return [self.redact(v) for v in value]
        if isinstance(value,dict):return {self.redact(k):self.redact(v) for k,v in value.items()}
        return value
    def __call__(self,feature,public,artifact):
        artifact=Path(artifact);artifact.mkdir(parents=True,exist_ok=False)
        public=self.redact(public)
        engine=teaching.f01 if feature=='F01' else teaching.f02
        prompt=teaching.model_prompt(feature,public)
        schema=json.loads((engine.ROOT/'schema.json').read_text(encoding='utf8'))
        messages=[]
        if public.get('execution_context') is not None:
            messages.append({'role':'system','content':teaching.EXECUTION_BOUNDARY})
        messages.append({'role':'user','content':prompt+'\nReturn only JSON matching this schema:\n'+json.dumps(schema,ensure_ascii=False)})
        body={'model':self.config.model,'messages':messages,
              'response_format':{'type':'json_object'},**self.config.parameters}
        try:
            response=self.transport(self.config.base_url+'/chat/completions',
                {'Content-Type':'application/json','Authorization':'Bearer '+self.config.api_key},body,self.config.timeout)
            content=self.redact(response['choices'][0]['message']['content'])
            output=json.loads(content)
        except AIUnavailable:
            # No exception text, body or request headers is logged by this boundary.
            raise AIUnavailable('AI API 未成功；未生成教学建议') from None
        except Exception:
            raise AIUnavailable('AI API 响应无效；未生成教学建议') from None
        checks=teaching.validate_reply(feature,output,public)
        metadata={'provider':'api','provider_success':True,'actual_model_call':True,
                  'model_requested':self.config.model,'usage':self.redact(response.get('usage')),
                  'provenance':self.provenance,'CLI_success':False}
        for name,value in [('raw_response.json',output),('validation.json',checks),('metadata.json',metadata)]:
            (artifact/name).write_text(json.dumps(self.redact(value),ensure_ascii=False,indent=2),encoding='utf8')
        return {'output':output,'checks':checks,'metadata':metadata}


def make_provider(config=None):
    config=config or AIConfig.from_env(Path(__file__).resolve().parent.parent/'.env')
    return {'codex_cli':CodexCLIProvider,'api':APIProvider,'disabled':DisabledProvider}[config.provider](config)
