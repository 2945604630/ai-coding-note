"""Frozen package checks and append-only local results; no network or credentials."""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from experiments.common import digest, dump

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent.parent


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def verify_history():
    old = read(ROOT / 'results/prior_files_sha256.json')
    changed = [name for name, sha in old.items() if not (WORKSPACE / name).is_file() or digest(WORKSPACE / name) != sha]
    if changed:
        raise ValueError('Historical files changed: ' + repr(changed))
    return {'checked': len(old), 'changed': changed}


def verify_freeze():
    manifest = read(ROOT / 'freeze_manifest.json')
    changed = [name for name, sha in manifest['sha256'].items() if digest(ROOT / name) != sha]
    if changed:
        raise ValueError('Frozen package changed: ' + repr(changed))
    for path in sorted(ROOT.glob('freeze_addendum_*.json')):
        addon = read(path)
        if addon['base_manifest_sha256'] != digest(ROOT / 'freeze_manifest.json'):
            raise ValueError('Base freeze changed')
        for name, sha in addon['sha256'].items():
            if digest(ROOT / name) != sha:
                raise ValueError('Frozen addendum changed: ' + name)
    return manifest


def load_case(case_id):
    verify_freeze()
    return read(ROOT / 'cases' / f'{int(case_id):02d}.json')


def new_result(kind):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    path = ROOT / 'results' / f'{kind}_{stamp}_{uuid.uuid4().hex[:6]}'
    path.mkdir(parents=True, exist_ok=False)
    dump(path / 'environment.json', {'utc': stamp, 'history': verify_history(),
                                    'implementation_sha256': {p.name: digest(p) for p in ROOT.glob('*.py')},
                                    'inference_calls': 0, 'kind': kind})
    return path
