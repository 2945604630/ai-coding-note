"""Double-click launcher: start a hidden local Python server, then open browser."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parent.parent
URL = 'http://127.0.0.1:8000'


def healthy(url=URL):
    try:
        with urllib.request.urlopen(url + '/api/health', timeout=1) as response:
            return json.load(response).get('service') == 'aic_web_v1'
    except (OSError, ValueError):
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--data-dir', type=Path)
    args = parser.parse_args()
    url=f'http://127.0.0.1:{args.port}'
    root = (args.data_dir or Path(os.environ.get('AIC_WEB_DATA_DIR', ROOT / 'data' / 'aic_web'))).resolve()
    if not healthy(url):
        check = subprocess.run([sys.executable, '-c', 'import fastapi, uvicorn'], capture_output=True)
        if check.returncode:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(ROOT / 'requirements-web.txt')], check=True)
        logs = root / 'server_logs'
        logs.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        stdout_path, stderr_path = logs / (stamp + '.stdout.log'), logs / (stamp + '.stderr.log')
        with stdout_path.open('xb') as out, stderr_path.open('xb') as err:
            process = subprocess.Popen([sys.executable, '-X', 'utf8', '-m', 'web_lab', '--no-browser',
                '--port',str(args.port),'--data-dir',str(root)],
                cwd=ROOT, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        for _ in range(120):
            if healthy(url):
                print(f'AIC started: {url}\nData: {root}\nPID: {process.pid}', flush=True)
                break
            if process.poll() is not None:
                raise SystemExit('Server failed. Log: ' + str(stderr_path))
            time.sleep(.25)
        else:
            raise SystemExit('Server not ready. Log: ' + str(stderr_path))
    else:
        print('AIC already running: ' + url)
    if not args.no_browser:
        webbrowser.open(url)


if __name__ == '__main__':
    main()
