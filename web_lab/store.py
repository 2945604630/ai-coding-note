"""SQLite transactions, immutable inputs and append-only evaluation revisions."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import uuid


def utc():
    return datetime.now(timezone.utc).isoformat()


def uid():
    return uuid.uuid4().hex


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


SCHEMA = '''
PRAGMA user_version=1;
CREATE TABLE IF NOT EXISTS experiments (
 experiment_id TEXT PRIMARY KEY, name TEXT NOT NULL, feature TEXT NOT NULL,
 case_id TEXT NOT NULL, mode TEXT NOT NULL, source_type TEXT NOT NULL,
 model_provenance TEXT NOT NULL, created_at TEXT NOT NULL, ended_at TEXT,
 status TEXT NOT NULL, end_reason TEXT, current_code_version_id TEXT NOT NULL,
 case_snapshot TEXT NOT NULL, model_config TEXT NOT NULL, version_snapshot TEXT NOT NULL, initial_input_snapshot TEXT,
 create_request_id TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS code_versions (
 version_id TEXT PRIMARY KEY, experiment_id TEXT NOT NULL REFERENCES experiments(experiment_id),
 label TEXT NOT NULL, source TEXT NOT NULL, source_sha256 TEXT NOT NULL,
 verification_status TEXT NOT NULL, execution_allowed INTEGER NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS turns (
 turn_id TEXT PRIMARY KEY, experiment_id TEXT NOT NULL REFERENCES experiments(experiment_id),
 number INTEGER NOT NULL, request_id TEXT NOT NULL, question_shown TEXT NOT NULL,
 answer_raw TEXT NOT NULL, public_input TEXT NOT NULL, code_version_id TEXT NOT NULL,
 status TEXT NOT NULL, submitted_at TEXT NOT NULL, started_at TEXT, generation_started_at TEXT, completed_at TEXT,
 output TEXT, checks TEXT, selected_attempt_id TEXT, elapsed_seconds REAL, error TEXT,
 UNIQUE(experiment_id, number), UNIQUE(experiment_id, request_id)
);
CREATE TABLE IF NOT EXISTS attempts (
 attempt_id TEXT PRIMARY KEY, turn_id TEXT NOT NULL REFERENCES turns(turn_id), number INTEGER NOT NULL,
 status TEXT NOT NULL, requested_at TEXT NOT NULL, started_at TEXT, generation_started_at TEXT, completed_at TEXT,
 retry_reason TEXT, request_id TEXT NOT NULL, artifact_dir TEXT NOT NULL,
 output TEXT, checks TEXT, metadata TEXT, raw_output TEXT, elapsed_seconds REAL, error TEXT,
 UNIQUE(turn_id, number), UNIQUE(turn_id, request_id)
);
CREATE TABLE IF NOT EXISTS feedback (
 feedback_id TEXT PRIMARY KEY, turn_id TEXT NOT NULL REFERENCES turns(turn_id), created_at TEXT NOT NULL,
 evaluation_source TEXT NOT NULL, on_topic TEXT, repetitive TEXT, fact_error TEXT,
 full_repair TEXT, used_previous TEXT, satisfaction INTEGER, notes TEXT
);
CREATE TABLE IF NOT EXISTS notes (
 note_id TEXT PRIMARY KEY, experiment_id TEXT NOT NULL REFERENCES experiments(experiment_id),
 created_at TEXT NOT NULL, text TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
 event_id TEXT PRIMARY KEY, experiment_id TEXT NOT NULL REFERENCES experiments(experiment_id),
 created_at TEXT NOT NULL, type TEXT NOT NULL, payload TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS turns_experiment ON turns(experiment_id);
CREATE INDEX IF NOT EXISTS feedback_turn ON feedback(turn_id);
CREATE INDEX IF NOT EXISTS experiments_created ON experiments(created_at);
CREATE TABLE IF NOT EXISTS demo_operations (
 operation_id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES experiments(experiment_id),
 kind TEXT NOT NULL, status TEXT NOT NULL, version_id TEXT, parent_version_id TEXT,
 artifact_dir TEXT NOT NULL, created_at TEXT NOT NULL, completed_at TEXT, error TEXT, payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS demo_assessments (
 session_id TEXT PRIMARY KEY REFERENCES experiments(experiment_id), directory TEXT NOT NULL UNIQUE,
 question_id TEXT NOT NULL, question_version TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sandbox_jobs (
 task_id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES experiments(experiment_id),
 version_id TEXT NOT NULL REFERENCES code_versions(version_id), source_sha256 TEXT NOT NULL,
 request_id TEXT NOT NULL, mode TEXT NOT NULL, inputs TEXT NOT NULL,
 contract_id TEXT NOT NULL, contract_sha256 TEXT NOT NULL, created_at TEXT NOT NULL,
 completed_at TEXT, status TEXT NOT NULL, executed INTEGER NOT NULL,
 results TEXT NOT NULL, elapsed_seconds REAL NOT NULL, error TEXT,
 UNIQUE(session_id, request_id)
);
CREATE INDEX IF NOT EXISTS sandbox_session ON sandbox_jobs(session_id, created_at);
'''

JSON_FIELDS = {'case_snapshot', 'model_config', 'version_snapshot', 'public_input', 'output',
               'checks', 'metadata', 'payload', 'initial_input_snapshot', 'inputs', 'results'}


def decode(row):
    if row is None:
        return None
    result = dict(row)
    for key in JSON_FIELDS & result.keys():
        result[key] = json.loads(result[key]) if result[key] is not None else None
    if 'execution_allowed' in result:
        result['execution_allowed'] = bool(result['execution_allowed'])
    if 'executed' in result:
        result['executed'] = bool(result['executed'])
    return result


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / 'aic_web.sqlite3'
        db = sqlite3.connect(self.path, timeout=15)
        try:
            db.execute('PRAGMA journal_mode=WAL')
            db.executescript(SCHEMA)
            for table in ['turns', 'attempts']:
                columns = {r[1] for r in db.execute('PRAGMA table_info(' + table + ')')}
                if 'generation_started_at' not in columns:
                    db.execute('ALTER TABLE ' + table + ' ADD COLUMN generation_started_at TEXT')
            columns = {r[1] for r in db.execute('PRAGMA table_info(experiments)')}
            if 'initial_input_snapshot' not in columns:
                db.execute('ALTER TABLE experiments ADD COLUMN initial_input_snapshot TEXT')
            db.commit()
        finally:
            db.close()

    @contextmanager
    def connection(self, write=False):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA synchronous=FULL')
        try:
            db.execute('BEGIN IMMEDIATE' if write else 'BEGIN')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def insert(self, db, table, values):
        keys = list(values)
        db.execute(f'INSERT INTO {table} ({",".join(keys)}) VALUES ({",".join("?" for _ in keys)})',
                   [encoded(v) if k in JSON_FIELDS else v for k, v in values.items()])

    def update(self, db, table, key, ident, values):
        db.execute(f'UPDATE {table} SET {",".join(k + "=?" for k in values)} WHERE {key}=?',
                   [encoded(v) if k in JSON_FIELDS and v is not None else v for k, v in values.items()] + [ident])

    def event(self, db, eid, kind, payload):
        self.insert(db, 'events', {'event_id': uid(), 'experiment_id': eid, 'created_at': utc(),
                                  'type': kind, 'payload': {'session_id': eid, **payload}})

    def experiment(self, db, eid):
        result = decode(db.execute('SELECT * FROM experiments WHERE experiment_id=?', (eid,)).fetchone())
        if result is None:
            raise KeyError('实验不存在')
        # The existing UUID is the canonical identity, not a filename-derived link.
        result['session_id'] = eid
        result['code_versions'] = [decode(r) for r in db.execute(
            'SELECT * FROM code_versions WHERE experiment_id=? ORDER BY created_at,rowid', (eid,))]
        result['turns'] = []
        for row in db.execute('SELECT * FROM turns WHERE experiment_id=? ORDER BY number', (eid,)):
            turn = decode(row)
            turn['attempts'] = [decode(r) for r in db.execute(
                'SELECT * FROM attempts WHERE turn_id=? ORDER BY number', (turn['turn_id'],))]
            turn['feedback'] = [decode(r) for r in db.execute(
                'SELECT * FROM feedback WHERE turn_id=? ORDER BY created_at,rowid', (turn['turn_id'],))]
            result['turns'].append(turn)
        result['notes'] = [decode(r) for r in db.execute(
            'SELECT * FROM notes WHERE experiment_id=? ORDER BY created_at,rowid', (eid,))]
        result['events'] = [decode(r) for r in db.execute(
            'SELECT * FROM events WHERE experiment_id=? ORDER BY created_at,rowid', (eid,))]
        result['creation_input_origin'] = self.creation_origin(result['events'])
        for event in result['events']:
            if event['type']=='input_origin_corrected' and event['payload'].get('turn_id'):
                for turn in result['turns']:
                    if turn['turn_id']==event['payload']['turn_id']:
                        turn['input_origin_correction']={**event['payload'],'event_id':event['event_id']}
        for record in result['code_versions'] + result['turns'] + result['notes'] + result['events']:
            record['session_id'] = eid
        for turn in result['turns']:
            for record in turn['attempts'] + turn['feedback']:
                record['session_id'] = eid
        return result

    def get(self, eid):
        with self.connection() as db:
            return self.experiment(db, eid)

    def list(self, filters=None, full=False):
        clauses, values = [], []
        for key, value in (filters or {}).items():
            if not value:
                continue
            if key == 'date':
                # Stored timestamps are UTC. Calendar filters use the user's +08:00 day.
                clauses.append("date(created_at,'+8 hours')=?")
            elif key in {'feature', 'case_id', 'mode', 'status', 'source_type'}:
                clauses.append(key + '=?')
            else:
                continue
            values.append(value)
        where = ' WHERE ' + ' AND '.join(clauses) if clauses else ''
        with self.connection() as db:
            rows = db.execute('SELECT * FROM experiments' + where + ' ORDER BY created_at DESC', values).fetchall()
            out=[]
            for r in rows:
                if full:
                    out.append(self.experiment(db,r['experiment_id']))
                else:
                    value=decode(r)
                    events=[decode(x) for x in db.execute("SELECT * FROM events WHERE experiment_id=? AND type IN ('experiment_created','input_origin_corrected') ORDER BY created_at,rowid",(r['experiment_id'],))]
                    value['creation_input_origin']=self.creation_origin(events)
                    out.append(value)
            return out

    @staticmethod
    def creation_origin(events):
        origin={'kind':'unknown','basis':'legacy_creation_origin_not_recorded','real_student_verified':False}
        for event in events:
            if event['type']=='experiment_created':
                origin=event['payload'].get('input_origin',origin)
            elif event['type']=='input_origin_corrected' and event['payload'].get('scope')=='creation':
                origin={'kind':event['payload']['kind'],'basis':'append_only_source_correction',
                        'correction_event_id':event['event_id'],'real_student_verified':False}
        return origin
