"""Loopback-only web API. No credential files or arbitrary file access endpoints."""
from contextlib import asynccontextmanager
import json
import os
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import reporting, teaching
from .service import Conflict, Service

ROOT = Path(__file__).resolve().parent.parent
STATIC = Path(__file__).resolve().parent / 'static'


class Input(BaseModel):
    model_config = ConfigDict(extra='forbid')


class OriginInput(Input):
    input_origin: Literal['manual_browser', 'automated_test', 'simulated_student', 'historical_replay', 'unknown'] = 'unknown'


class Create(OriginInput):
    feature: Literal['F01', 'F02', 'DEMO']
    case_id: str = Field(min_length=1, max_length=10)
    mode: Literal['S0', 'S1']
    source_type: Literal['real_user', 'automated_test'] = 'real_user'
    name: str = Field(default='', max_length=120)
    request_id: str | None = Field(default=None, min_length=1, max_length=100)
    entry_point: Literal['learning', 'experiment'] = 'experiment'


class Reply(OriginInput):
    answer: str = Field(min_length=1, max_length=30000)
    request_id: str = Field(min_length=1, max_length=100)
    parent_turn_id: str | None = None

    @field_validator('answer')
    @classmethod
    def nonempty(cls, value):
        if not value.strip():
            raise ValueError('请输入非空回答')
        return value


class Retry(Input):
    reason: str = Field(min_length=1, max_length=1000)
    request_id: str = Field(min_length=1, max_length=100)


class Control(OriginInput):
    action: Literal['pause', 'resume', 'end', 'complete']


class Code(OriginInput):
    source: str = Field(min_length=1, max_length=100000)


class ModifiedCode(Code):
    parent_version_id: str | None = Field(default=None, max_length=100)


class Note(OriginInput):
    text: str = Field(min_length=1, max_length=5000)


class Verification(OriginInput):
    version_id: str = Field(min_length=1, max_length=100)


class SandboxSubmission(Verification):
    source_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    request_id: str = Field(min_length=1, max_length=100)


class SandboxRun(SandboxSubmission):
    input: StrictInt = Field(ge=0, le=8)


class Assessment(OriginInput):
    external_help: Literal['none', 'used', 'unknown'] = 'unknown'
    history_complete: bool = False
    prior_exposure_checked: bool = False
    source_record_complete: bool = False


class Help(OriginInput):
    kind: Literal['hint', 'full_answer', 'ai_help', 'external_help', 'question_seen']
    target: Literal['original', 'assessment', 'unknown']
    content: str = Field(min_length=1, max_length=30000)
    applies_before_first: bool | None = None


class Feedback(OriginInput):
    evaluation_source: Literal['user_subjective', 'ai_auxiliary', 'independent_human'] = 'user_subjective'
    on_topic: Literal['yes', 'no', 'uncertain'] | None = None
    repetitive: Literal['yes', 'no', 'uncertain'] | None = None
    fact_error: Literal['yes', 'no', 'uncertain'] | None = None
    full_repair: Literal['yes', 'no', 'uncertain'] | None = None
    used_previous: Literal['yes', 'no', 'uncertain'] | None = None
    satisfaction: StrictInt | None = Field(default=None, ge=1, le=5)
    notes: str | None = Field(default=None, max_length=5000)


class UIAction(OriginInput):
    action: Literal['edit_code', 'view_evidence', 'view_diff', 'open_assessment']


def create_app(data_dir=None, model_runner=None):
    data_dir = Path(data_dir or os.environ.get('AIC_WEB_DATA_DIR', ROOT / 'data' / 'aic_web'))

    @asynccontextmanager
    async def lifespan(app):
        app.state.service = Service(data_dir, model_runner)
        yield
        app.state.service.close()

    app = FastAPI(title='AIC 编程学习台 V2', lifespan=lifespan, docs_url=None, redoc_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1', 'localhost', *(['testserver'] if model_runner else [])])

    @app.middleware('http')
    async def local_origin(request: Request, call_next):
        if request.method in {'POST', 'PUT', 'PATCH', 'DELETE'}:
            origin = request.headers.get('origin')
            if (origin and urlsplit(origin).netloc != request.headers.get('host')) or request.headers.get('sec-fetch-site') == 'cross-site':
                return JSONResponse({'detail': '本地接口仅接受同源操作'}, status_code=403)
            if request.headers.get('content-type', '').split(';')[0] != 'application/json':
                return JSONResponse({'detail': '接口需要 application/json'}, status_code=415)
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"
        return response

    @app.exception_handler(Conflict)
    async def conflict(request, exc):
        return JSONResponse({'detail': str(exc)}, status_code=409)

    @app.exception_handler(KeyError)
    async def missing(request, exc):
        return JSONResponse({'detail': str(exc.args[0])}, status_code=404)

    @app.exception_handler(ValueError)
    async def invalid(request, exc):
        return JSONResponse({'detail': str(exc)}, status_code=422)

    def service():
        return app.state.service

    @app.get('/api/health')
    def health():
        return {'service': 'aic_web_v1', 'ui_version': 'V2', 'status': 'ok', 'model_provider': service().runner.provenance,
                'sandbox':service().sandbox.status(), 'ai_provider':service().runner.public_config() if hasattr(service().runner,'public_config') else {'provider':'test_fixture'}}

    @app.post('/api/experiments/{eid}/sandbox/run', status_code=202)
    def sandbox_run(eid: str, payload: SandboxRun):
        return service().sandbox.submit(eid,payload.version_id,payload.source_sha256,
            payload.request_id,'run',payload.input,payload.input_origin)

    @app.post('/api/experiments/{eid}/sandbox/submit', status_code=202)
    def sandbox_submit(eid: str, payload: SandboxSubmission):
        return service().sandbox.submit(eid,payload.version_id,payload.source_sha256,
            payload.request_id,'submit',input_origin=payload.input_origin)

    @app.get('/api/experiments/{eid}/sandbox/jobs')
    def sandbox_jobs(eid: str):
        return service().sandbox.jobs(eid)

    @app.get('/api/experiments/{eid}/sandbox/jobs/{task_id}')
    def sandbox_job(eid: str, task_id: str):
        return service().sandbox.get(eid,task_id)

    @app.get('/api/cases')
    def cases():
        return teaching.catalog()

    @app.get('/api/demo/cases')
    def demo_cases():
        return teaching.catalog(demo=True)

    @app.post('/api/demo/{eid}/verify', status_code=201)
    def verify(eid: str, payload: Verification):
        return service().demo.verify(eid, payload.version_id, payload.input_origin)

    @app.post('/api/demo/{eid}/assessment', status_code=201)
    def assessment(eid: str, payload: Assessment):
        values = payload.model_dump()
        origin = values.pop('input_origin')
        return service().demo.begin(eid, values.pop('external_help'), values, origin)

    @app.post('/api/demo/{eid}/help', status_code=201)
    def help_record(eid: str, payload: Help):
        return service().demo.help(eid, payload.kind, payload.target, payload.content, payload.applies_before_first, payload.input_origin)

    @app.post('/api/demo/{eid}/first', status_code=201)
    def first(eid: str, payload: Code):
        return service().demo.submit(eid, payload.source, input_origin=payload.input_origin)

    @app.post('/api/demo/{eid}/assessment-code', status_code=201)
    def assessment_code(eid: str, payload: Code):
        return service().demo.submit(eid, payload.source, first=False, input_origin=payload.input_origin)

    @app.get('/api/experiments')
    def experiments(date: str | None = None, feature: str | None = None, case_id: str | None = None,
                    mode: str | None = None, status: str | None = None, source_type: str | None = None):
        return service().store.list(locals())

    @app.post('/api/experiments', status_code=201)
    def create(payload: Create):
        return service().create(payload.model_dump())

    @app.get('/api/experiments/{eid}')
    def detail(eid: str):
        result = service().detail(eid)
        for t in result['turns']:
            for a in t['attempts']:
                a['artifact_names'] = sorted(reporting.artifact_files(service().store.root, a))
        return result

    @app.post('/api/experiments/{eid}/turns', status_code=202)
    def reply(eid: str, payload: Reply):
        return service().submit(eid, payload.answer, payload.request_id, payload.parent_turn_id, payload.input_origin)

    @app.post('/api/turns/{tid}/retry', status_code=202)
    def retry(tid: str, payload: Retry):
        return service().retry(tid, payload.reason, payload.request_id)

    @app.post('/api/experiments/{eid}/control')
    def control(eid: str, payload: Control):
        return service().control(eid, payload.action, payload.input_origin)

    @app.post('/api/experiments/{eid}/code', status_code=201)
    def code(eid: str, payload: ModifiedCode):
        return service().add_code(eid, payload.source, payload.parent_version_id, payload.input_origin)

    @app.post('/api/experiments/{eid}/notes', status_code=201)
    def note(eid: str, payload: Note):
        return service().note(eid, payload.text, payload.input_origin)

    @app.post('/api/experiments/{eid}/ui-actions', status_code=201)
    def ui_action(eid: str, payload: UIAction):
        return service().ui_action(eid, payload.action, payload.input_origin)

    @app.post('/api/turns/{tid}/feedback', status_code=201)
    def feedback(tid: str, payload: Feedback):
        return service().feedback(tid, payload.model_dump())

    @app.get('/api/stats')
    def stats(source_type: Literal['real_user', 'automated_test'] | None = None):
        return reporting.stats(service().store.list({'source_type': source_type}, full=True))

    @app.get('/api/export/json')
    def json_export(experiment_id: str | None = None):
        export = reporting.export_json(service().store, experiment_id)
        for e in export['experiments']:
            e['sandbox_jobs'] = service().sandbox.jobs(e['experiment_id'])
            if e['feature'] == 'DEMO':
                e['demo'] = service().demo.detail(e['experiment_id'])
                e['events'] = service().store.get(e['experiment_id'])['events']
                e['demo_artifacts'] = service().demo.export_files(e['experiment_id'])
        export['data_scope'] = 'web_lab_sessions; historical_experiments_preserved_not_migrated'
        export['canonical_identity'] = 'session_id equals experiment_id UUID; explicit FK and ledger links'
        body = json.dumps(export, ensure_ascii=False, indent=2)
        return Response(body, media_type='application/json', headers={
            'Content-Disposition': f'attachment; filename="aic_{experiment_id or "all"}.json"'})

    @app.get('/api/export/csv')
    def csv_export(kind: Literal['experiments', 'turns', 'attempts'] = 'turns', experiment_id: str | None = None):
        return Response(reporting.export_csv(service().store, kind, experiment_id), media_type='text/csv; charset=utf-8',
                        headers={'Content-Disposition': f'attachment; filename="aic_{kind}.csv"'})

    @app.get('/api/artifacts/{aid}/{name}')
    def artifact(aid: str, name: str):
        with service().store.connection() as db:
            row = db.execute('SELECT * FROM attempts WHERE attempt_id=?', (aid,)).fetchone()
        files = reporting.artifact_files(service().store.root, dict(row)) if row else {}
        if name not in files:
            raise KeyError('工件不存在')
        raw = files[name].read_bytes()
        return Response(raw, media_type='text/plain; charset=utf-8')

    app.mount('/static', StaticFiles(directory=STATIC), name='static')

    @app.get('/manage')
    @app.get('/history')
    @app.get('/stats')
    @app.get('/experiments/{eid}')
    def page():
        return FileResponse(STATIC / 'index.html')

    @app.get('/')
    @app.get('/learning-history')
    @app.get('/mistakes')
    @app.get('/mistakes/{eid}')
    @app.get('/study/{eid}')
    @app.get('/study/{eid}/assessment')
    def learning_page():
        return FileResponse(STATIC / 'learning.html')

    return app
