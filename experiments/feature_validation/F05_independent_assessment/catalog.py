"""Fixed reviewed assessment catalog; no runtime arbitrary-code registration."""
import json
from pathlib import Path

from experiments.common import digest

ROOT = Path(__file__).resolve().parent


def load():
    frozen = json.loads((ROOT / 'freeze.json').read_text(encoding='utf-8'))
    for relative, expected in frozen['sha256'].items():
        if digest(ROOT / relative) != expected:
            raise ValueError('F05 frozen input changed: ' + relative)
    historical = json.loads((ROOT / 'historical_manifest.json').read_text(encoding='utf-8'))
    for path, expected in historical['sha256'].items():
        if digest(path) != expected:
            raise ValueError('Reviewed historical input changed: ' + path)
    return json.loads((ROOT / 'data/registry.json').read_text(encoding='utf-8'))


def question():
    load()
    return json.loads((ROOT / 'data/question.json').read_text(encoding='utf-8'))
