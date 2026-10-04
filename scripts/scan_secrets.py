"""Fail a release on credential patterns in tracked text or added commit content."""
import argparse,re,subprocess,sys
from pathlib import Path
PATTERNS=[rb'(?:cfut_|ghp_|github_pat_)[A-Za-z0-9_-]{20,}',rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'https://[^\s/@]+:[^\s/@]+@github\.com']
def hits(data):return any(re.search(pattern,data) for pattern in PATTERNS)
def main():
    p=argparse.ArgumentParser();p.add_argument('--range');args=p.parse_args();bad=[]
    if args.range:
        # Check additions, including intermediate commits; never print matching values.
        patch=subprocess.check_output(['git','log','-p','--format=','--no-ext-diff',args.range])
        if hits(b'\n'.join(line[1:] for line in patch.splitlines() if line.startswith(b'+') and not line.startswith(b'+++'))):bad.append('commit additions')
    for name in subprocess.check_output(['git','ls-files','-z']).decode().split('\0'):
        if not name:continue
        path=Path(name)
        if path.is_file() and path.suffix.lower() not in {'.xls','.xlsx','.png','.jpg','.pdf','.zip'} and hits(path.read_bytes()):bad.append(name)
    if bad:print('Secret pattern detected in: '+', '.join(bad),file=sys.stderr);return 1
    print('Tracked files and requested changes: no credential patterns detected');return 0
if __name__=='__main__':sys.exit(main())
