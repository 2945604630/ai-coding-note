"""Read-only publication checks; never invoke models, Docker or a real learner DB."""
from pathlib import Path
from urllib.parse import unquote
import hashlib
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r'!?\[[^\]\n]*\]\((<[^>\n]+>|[^\s)]+)(?:\s+"[^"\n]*")?\)')
SECRET = re.compile(
    r'(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{25,}|'
    r'github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|'
    r'https?://[^\s/@:]+:[^\s/@]+@)'
)
HOST_PATH = re.compile(r'[A-Za-z]:[/\\]Users[/\\]')
PRIVATE_DIRS = {'data', 'backups', 'output', 'tmp', 'temp', '.planning', '.playwright-cli',
                'screenshots', 'browser-recordings', '.venv', 'venv', 'node_modules'}
PRIVATE_PARTS = {'__pycache__', '.pytest_cache', 'user_runs', 'server_logs', '.cache'}
PRIVATE_NAMES = {'auth.json', 'acceptance.json', 'runtime.json', 'service.lock'}
PRIVATE_SUFFIXES = {'.log', '.jsonl', '.sqlite', '.sqlite3', '.db', '.pyc', '.pem', '.key', '.p12', '.pfx', '.iid'}
IGNORE_SAMPLES = [
    '.env', '.env.local', 'data/aic_demo/aic_web.sqlite3',
    'data/aic_demo/aic_web.sqlite3-wal', 'data/aic_demo/aic_web.sqlite3-shm',
    'data/aic_demo/artifacts/learner/session.json',
    'data/aic_demo/sandbox/acceptance.json', 'backups/example/session.json',
    'output/playwright/private.png', '.playwright-cli/browser.json',
    'screenshots/private.png', 'browser-recordings/private.webm',
    '.venv/pyvenv.cfg', 'node_modules/example/index.js',
    'web_lab/__pycache__/app.pyc', '.pytest_cache/v/cache/nodeids',
    '.planning/example/task_plan.md', 'experiments/feature_validation/F02_dynamic_questioning/user_runs/private/session.json',
    'docs/research/private_report.md', 'docs/archive/private_raw_response.json',
    'local.stdout.log', 'execution_receipt_local.json', 'acceptance.json', 'runtime.json',
]


def git(*args, data=None):
    return subprocess.check_output(['git', *args], cwd=ROOT, input=data)


def check_links(paths, errors):
    count = 0
    for name in paths:
        if not name.endswith('.md'):
            continue
        text = (ROOT / name).read_text(encoding='utf-8-sig')
        # Examples in fenced code blocks are not rendered Markdown links.
        text = re.sub(r'^```.*?^```[^\n]*$', '', text, flags=re.M | re.S)
        for match in LINK.finditer(text):
            target = unquote(match.group(1).strip('<>'))
            if re.match(r'^(?:https?://|mailto:|app://|codex://)', target):
                continue
            count += 1
            file_target = target.split('#', 1)[0]
            if not file_target:
                continue
            if re.match(r'^(?:[A-Za-z]:[/\\]|/|file://)', file_target):
                errors.append(name + ': non-portable local Markdown target')
                continue
            resolved = ((ROOT / name).parent / file_target).resolve()
            if not resolved.is_relative_to(ROOT):
                errors.append(name + ': Markdown target escapes repository')
                continue
            relative = resolved.relative_to(ROOT).as_posix()
            present = relative in paths or any(p.startswith(relative.rstrip('/') + '/') for p in paths)
            if not present or not resolved.exists():
                errors.append(name + ': target not in publication: ' + file_target)
    return count


def check_publication(paths, errors):
    for name in paths:
        path = Path(name)
        if (path.parts[0] in PRIVATE_DIRS or PRIVATE_PARTS.intersection(path.parts)
                or path.name in PRIVATE_NAMES or path.suffix in PRIVATE_SUFFIXES
                or (path.name.startswith('.env') and path.name != '.env.example')
                or re.search(r'\.(?:db|sqlite3?)-(?:wal|shm|journal)$', path.name)):
            errors.append(name + ': private/local artifact is tracked')
        # No credential values are printed, including on failure.
        text = (ROOT / name).read_bytes().decode('utf-8-sig', errors='ignore')
        if SECRET.search(text):
            errors.append(name + ': possible credential')
        if HOST_PATH.search(text):
            errors.append(name + ': personal machine path')
    ignored = set(git('check-ignore', '--no-index', '--stdin', data=('\n'.join(IGNORE_SAMPLES) + '\n').encode()).decode('utf8').splitlines())
    for name in sorted(set(IGNORE_SAMPLES) - ignored):
        errors.append(name + ': private sample is not ignored')


def check_cleanup_baseline(errors):
    baseline = 'c40029ce2bb00581917cb5e45f9c0b4ad0c83745'
    changed_docs = {'README.md', '.gitignore', 'AI_provider_setup.md', 'GITHUB_SETUP.md',
                    'sandbox_architecture_decision.md', 'sandbox_test_results.md',
                    'teaching_execution_integration.md', 'web_lab/TEST_REPORT.md'}
    rows = git('ls-tree', '-r', baseline).decode('utf8').splitlines()
    checked = 0
    for row in rows:
        info, name = row.split('\t', 1)
        if name in changed_docs:
            continue
        file = ROOT / name
        if not file.is_file():
            errors.append(name + ': baseline file missing')
            continue
        content = file.read_bytes()
        digest = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
        if digest != info.split()[2]:
            errors.append(name + ': baseline bytes changed')
        checked += 1
    return checked


def main():
    paths = set(git('ls-files', '-z').decode('utf8').rstrip('\0').split('\0'))
    errors = []
    links = check_links(paths, errors)
    check_publication(paths, errors)
    baseline = '--cleanup-baseline' in sys.argv
    checked = check_cleanup_baseline(errors) if baseline else 0
    if errors:
        for error in errors:
            print('FAIL:', error)
        raise SystemExit(1)
    print(f'PASS: {len(paths)} tracked files; {links} local Markdown links; credential/path scan; {len(IGNORE_SAMPLES)} private ignore samples.')
    if baseline:
        print(f'PASS: {checked} baseline files retain exact bytes and paths.')
    print('No remote links, models, Docker jobs or learner databases were accessed.')


if __name__ == '__main__':
    main()
