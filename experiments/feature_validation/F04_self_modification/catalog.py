"""Fixed F04 catalog: hashed historical reviewed fixtures only, not caller-provided source."""
import json
from pathlib import Path

from experiments.common import digest

ROOT = Path(__file__).resolve().parent


def load():
    freeze = json.loads((ROOT / 'freeze.json').read_text(encoding='utf-8'))
    for relative, expected in freeze['sha256'].items():
        if digest(ROOT / relative) != expected:
            raise ValueError('Frozen F04 input changed: ' + relative)
    historical = json.loads((ROOT / 'historical_manifest.json').read_text(encoding='utf-8'))
    for path, expected in historical['sha256'].items():
        if digest(path) != expected:
            raise ValueError('Reviewed historical dependency changed: ' + path)
    return json.loads((ROOT / 'data/registry.json').read_text(encoding='utf-8'))
