"""Keep root compatibility assets in sync with canonical site/ sources.

KAM source files are concatenated in explicit dependency order. No transpilation,
minification, npm dependencies or runtime loader is involved.
"""
import argparse
import hashlib
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
KAM_MODULES = ('defaults', 'normalization', 'access', 'plans', 'filters', 'aggregation', 'render', 'reports')


def expected_assets(root=ROOT):
    site = root / 'site'
    bundle = ''.join((site / 'js/kam' / (name + '.js')).read_text(encoding='utf-8') for name in KAM_MODULES).encode('utf-8')
    assets = {site / 'js/kam-dashboard.js': bundle}
    for folder in ('js', 'css'):
        for source in sorted((site / folder).glob('*.' + folder)):
            content = assets.get(source, source.read_bytes())
            assets[root / folder / source.name] = content
    for source in sorted((site / 'vendor').glob('*')):
        if source.is_file():
            assets[root / 'vendor' / source.name] = source.read_bytes()
    html = (site / 'index.html').read_text(encoding='utf-8')

    def version(match):
        path = site / match.group(2)
        content = assets.get(path, path.read_bytes())
        digest = hashlib.sha256(content).hexdigest()[:12]
        return match.group(1) + match.group(2) + '?v=' + digest + match.group(3)

    html = re.sub(r'((?:src|href)=")((?:js|css)/[^"?]+)(?:\?[^" ]*)?(")', version, html)
    assets[site / 'index.html'] = html.encode('utf-8')
    assets[root / 'index.html'] = html.encode('utf-8')
    return assets


def sync_frontend(root=ROOT, check=False):
    changed = []
    for path, content in expected_assets(root).items():
        if not path.exists() or path.read_bytes() != content:
            changed.append(str(path.relative_to(root)))
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
    if check and changed:
        raise RuntimeError('Frontend assets out of sync: ' + ', '.join(changed))
    return changed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print('Frontend:', sync_frontend(check=args.check) or 'up to date')
