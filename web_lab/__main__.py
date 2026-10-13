"""python -m web_lab: single-process loopback server."""
import argparse
import os
from pathlib import Path
import threading
import time
import urllib.request
import webbrowser

import uvicorn

from .app import ROOT, create_app


def lock_data(root):
    root.mkdir(parents=True, exist_ok=True)
    handle = (root / 'service.lock').open('a+b')
    handle.seek(0)
    if handle.read(1) == b'':
        handle.write(b'0')
        handle.flush()
    handle.seek(0)
    try:
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        raise SystemExit('This data directory is already in use by AIC. Open the existing service.')
    return handle


def main():
    parser = argparse.ArgumentParser(description='AIC local learning app V3')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--data-dir', type=Path)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    root = (args.data_dir or Path(os.environ.get('AIC_WEB_DATA_DIR', ROOT / 'data' / 'aic_web'))).resolve()
    url = f'http://127.0.0.1:{args.port}'
    try:
        with urllib.request.urlopen(url + '/api/health', timeout=1) as response:
            if b'aic_web_v1' in response.read():
                print('Already running: ' + url)
                if not args.no_browser:
                    webbrowser.open(url)
                return
    except OSError:
        pass
    lock = lock_data(root)
    if not args.no_browser:
        def open_when_ready():
            for _ in range(100):
                try:
                    urllib.request.urlopen(url + '/api/health', timeout=1).close()
                    webbrowser.open(url)
                    return
                except OSError:
                    time.sleep(.2)
        threading.Thread(target=open_when_ready, daemon=True).start()
    print(f'AIC V3: {url}\nData: {root}', flush=True)
    try:
        uvicorn.run(create_app(root), host='127.0.0.1', port=args.port, workers=1, log_level='info')
    finally:
        lock.close()


if __name__ == '__main__':
    main()
