"""Back up SQLite through its online API and copy only this lab's artifacts."""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sqlite3

from .app import ROOT
from .store import Store


def backup(root, destination):
    store = Store(root)
    destination = Path(destination).resolve()
    if destination.exists():
        raise FileExistsError('备份目标已存在，请选新目录')
    if destination.is_relative_to(store.root):
        raise ValueError('备份目标不能位于正在备份的数据目录内')
    # Hold the write reservation until copying finishes, so no new submissions can
    # enter during the snapshot. Active calls must first finish (or be recovered).
    with store.connection(write=True) as db:
        running = db.execute("SELECT COUNT(*) FROM attempts WHERE status IN ('queued','connecting','generating')").fetchone()[0]
        if running:
            raise ValueError('尚有调用未完成，请等待完成后备份')
        destination.mkdir(parents=True, exist_ok=False)
        with closing(sqlite3.connect(store.path)) as source, closing(sqlite3.connect(destination / store.path.name)) as target:
            source.backup(target)
        for name in ['artifacts', 'server_logs']:
            folder = store.root / name
            if folder.exists():
                shutil.copytree(folder, destination / name)
        (destination / 'backup_manifest.json').write_text(json.dumps({'source': str(store.root),
            'created_at': datetime.now(timezone.utc).isoformat(), 'schema_version': 1,
            'active_calls_at_backup': 0, 'credentials_included': False}, ensure_ascii=False, indent=2), encoding='utf-8')
    return destination


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'data' / 'aic_web')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    target = args.output or ROOT / 'backups' / datetime.now(timezone.utc).strftime('aic_web_%Y%m%dT%H%M%S%fZ')
    print(backup(args.data_dir, target))


if __name__ == '__main__':
    main()
