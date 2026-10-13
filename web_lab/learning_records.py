"""Read-only learner summaries over the existing V2 database, without migration."""
from datetime import datetime
from .store import decode

FAILURES = {'failed', 'timeout', 'exception', 'resource_limit', 'output_limit', 'service_error', 'unavailable'}


def review_kind(job):
    if job['status'] in FAILURES:
        return job['status']
    if any(r.get('visible', True) and r.get('expected_output') is not None
           and r.get('stdout', '').replace('\r\n', '\n') != r['expected_output'] for r in job['results']):
        return 'output_mismatch'
    return None


def brief(job):
    if not job:
        return None
    return {k: job[k] for k in ('task_id', 'version_id', 'status', 'mode', 'created_at')}


def records(store):
    result = []
    for e in store.list({'feature': 'DEMO'}):
        eid = e['experiment_id']
        with store.connection() as db:
            jobs = [decode(r) for r in db.execute(
                'SELECT * FROM sandbox_jobs WHERE session_id=? ORDER BY created_at,rowid', (eid,))]
            turns = [dict(r) for r in db.execute(
                'SELECT status,submitted_at FROM turns WHERE experiment_id=?', (eid,))]
            versions = [dict(r) for r in db.execute(
                'SELECT version_id,created_at FROM code_versions WHERE experiment_id=?', (eid,))]
            latest_event = db.execute('SELECT created_at FROM events WHERE experiment_id=? ORDER BY rowid DESC LIMIT 1', (eid,)).fetchone()
        reviews = [(j, review_kind(j)) for j in jobs if review_kind(j)]
        current = [j for j in jobs if j['version_id'] == e['current_code_version_id']]
        times = [e['created_at'], *[v['created_at'] for v in versions],
                 *[j['created_at'] for j in jobs], *[t['submitted_at'] for t in turns]]
        if latest_event:
            times.append(latest_event['created_at'])
        result.append({**{k: e[k] for k in ('experiment_id', 'name', 'case_id', 'mode', 'status',
            'source_type', 'creation_input_origin', 'current_code_version_id', 'created_at')},
            'updated_at': max(times, key=lambda x: datetime.fromisoformat(x).timestamp()),
            'version_count': len(versions), 'run_count': len(jobs), 'current_job': brief(current[-1]) if current else None,
            'review_count': len(reviews), 'coach_failure_count': sum(t['status'] in {'failed', 'blocked'} for t in turns),
            'last_review': {**brief(reviews[-1][0]), 'kind': reviews[-1][1]} if reviews else None})
    return sorted(result, key=lambda r: datetime.fromisoformat(r['updated_at']).timestamp(), reverse=True)
