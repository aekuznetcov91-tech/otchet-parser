"""Validate, publish the checked commit to Git, then deploy its site/ snapshot."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

from scripts.sync_frontend import sync_frontend

ROOT = Path(__file__).resolve().parent
CONFIG_FILE = ROOT / 'config.local.json'
MAX_FILE_BYTES = 25 * 1024 * 1024


def redact(text):
    text = re.sub(r'https://[^/\s@]+@', 'https://[redacted]@', text or '')
    return re.sub(r'(?:cfut_|ghp_)[A-Za-z0-9_-]+', '[redacted]', text)


def run(args, *, env=None, cwd=ROOT, timeout=300):
    result = subprocess.run(args, cwd=cwd, env=env, capture_output=True,
                            text=True, errors='replace', timeout=timeout)
    if result.returncode:
        raise RuntimeError(f'{Path(args[0]).name} failed ({result.returncode}): '
                           + redact(result.stderr or result.stdout))
    return result.stdout.strip()


def deployment_environment():
    config = {}
    if CONFIG_FILE.exists():
        config = json.loads(CONFIG_FILE.read_text(encoding='utf-8-sig'))
    env = os.environ.copy()
    for key, field in [('CLOUDFLARE_API_TOKEN', 'api_token'), ('CLOUDFLARE_ACCOUNT_ID', 'account_id')]:
        env.setdefault(key, config.get(field, ''))
    node_bin = ROOT / 'scratch/tools/node-v20.18.0-darwin-arm64/bin'
    if node_bin.exists():
        env['PATH'] = str(node_bin) + os.pathsep + env.get('PATH', '')
    if sys.platform == 'win32':
        env['PATH'] = str(Path(env.get('APPDATA', '')) / 'npm') + os.pathsep + env.get('PATH', '')
    env.update(PYTHONIOENCODING='utf-8', NO_COLOR='1')
    return env, config.get('project_name', 'dashbord-partners1')


def validate_site(site):
    if not (site / 'index.html').is_file():
        raise RuntimeError('site/index.html missing')
    for path in site.rglob('*'):
        if path.is_symlink():
            raise RuntimeError(f'Symlinks are not deployable: {path.name}')
        if path.is_file() and path.stat().st_size >= MAX_FILE_BYTES:
            raise RuntimeError(f'Cloudflare file size limit exceeded: {path.name}')


def validate_staged_changes():
    names = run(['git', 'diff', '--cached', '--name-only']).splitlines()
    if any(Path(name).name in ('config.local.json', '.env') for name in names):
        raise RuntimeError('Local secrets must not be committed')
    diff = run(['git', 'diff', '--cached', '--no-ext-diff', '--unified=0'])
    added = '\n'.join(line[1:] for line in diff.splitlines() if line.startswith('+') and not line.startswith('+++'))
    if re.search(r'(?:cfut_|ghp_)[A-Za-z0-9_-]{20,}', added):
        raise RuntimeError('A token was detected in staged changes; remove it before publishing')


def sync_and_push_git(commit_message=None):
    """Fail closed on divergence or any Git error; return the published commit."""
    if run(['git', 'branch', '--show-current']) != 'main':
        raise RuntimeError('Publishing requires the main branch')
    run(['git', 'fetch', 'origin', 'main'])
    run(['git', 'merge-base', '--is-ancestor', 'origin/main', 'HEAD'])
    run(['git', 'add', '-A'])
    validate_staged_changes()
    if run(['git', 'diff', '--cached', '--name-only']):
        run(['git', 'commit', '-m', commit_message or 'refactor: validate and synchronize dashboard release'])
    revision = run(['git', 'rev-parse', 'HEAD'])
    run(['git', 'push', 'origin', 'HEAD:refs/heads/main'])
    remote = run(['git', 'ls-remote', 'origin', 'refs/heads/main']).split()
    if not remote or remote[0] != revision:
        raise RuntimeError('Remote main does not match the release commit')
    print(f'Git origin/main verified: {revision}')
    return revision


def deploy(*, git_only=False, commit_message=None):
    env, project = deployment_environment()
    if not shutil.which('node', path=env.get('PATH')):
        raise RuntimeError('Node.js is required for dashboard regression tests')
    # Configuration errors are caught before committing or pushing.
    if not git_only and not (env['CLOUDFLARE_API_TOKEN'] and env['CLOUDFLARE_ACCOUNT_ID']):
        raise RuntimeError('Cloudflare credentials are missing')
    sync_frontend()
    validate_site(ROOT / 'site')
    print(run([sys.executable, '-m', 'unittest', 'discover', 'tests'], env=env))
    sync_frontend(check=True)
    revision = sync_and_push_git(commit_message)
    if git_only:
        return revision
    # Only tracked files from the exact pushed commit reach Cloudflare.
    with tempfile.TemporaryDirectory(prefix='dashboard-release-') as temp:
        archive = Path(temp) / 'site.tar'
        run(['git', 'archive', '--format=tar', '--output=' + str(archive), revision, 'site'])
        with tarfile.open(archive) as tar:
            for member in tar.getmembers():
                if member.issym() or member.islnk() or '..' in Path(member.name).parts or Path(member.name).is_absolute():
                    raise RuntimeError('Unsafe path in release archive')
            tar.extractall(temp)
        site = Path(temp) / 'site'
        validate_site(site)
        wrangler = shutil.which('wrangler.cmd' if sys.platform == 'win32' else 'wrangler', path=env.get('PATH'))
        command = [wrangler] if wrangler else ['npx.cmd' if sys.platform == 'win32' else 'npx', '--yes', 'wrangler']
        command += ['pages', 'deploy', str(site), '--project-name=' + project,
                    '--branch=main', '--commit-hash=' + revision]
        print(redact(run(command, env=env, cwd=temp)))
    print(f'Cloudflare deployment completed for {revision}')
    return revision


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--git-only', action='store_true', help='Publish the checked commit to origin/main without Cloudflare')
    parser.add_argument('--message', help='Git commit message')
    args = parser.parse_args()
    try:
        deploy(git_only=args.git_only, commit_message=args.message)
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as error:
        print('Release stopped: ' + redact(str(error)), file=sys.stderr)
        sys.exit(1)
