"""Original-byte archives. Does not create, call, or impersonate a model."""
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from experiments.common import digest, dump


def archive_response(source, archive_root, slot, metadata):
    if not re.fullmatch(r'S[12]_0[1-8]', slot):
        raise ValueError('Unknown response slot')
    source = Path(source)
    raw = source.read_bytes()
    if len(raw) > 2 * 1024 * 1024:
        raise ValueError('Response exceeds archive budget; preserve source and review manually')
    root = Path(archive_root) / slot
    existing = list(root.glob('attempt_*/record.json'))
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    target = root / ('attempt_' + stamp + '_' + uuid.uuid4().hex[:6])
    target.mkdir(parents=True, exist_ok=False)
    path = target / 'raw_response.md'
    path.write_bytes(raw)
    record = {'slot': slot, 'utc': stamp, 'raw_path': str(path.resolve()), 'raw_sha256': digest(path),
              'raw_bytes': len(raw), 'primary': not existing, 'metadata': metadata,
              'source_file': str(source.resolve()), 'original_preserved': True}
    dump(target / 'record.json', record)
    return record
