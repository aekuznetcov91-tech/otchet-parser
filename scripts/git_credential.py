"""Repository-local Git credential helper. Git calls this; do not run to display secrets."""
import json,sys
from pathlib import Path
if sys.argv[1:] == ['get']:
    fields=dict(line.rstrip('\n').split('=',1) for line in sys.stdin if '=' in line)
    if fields.get('protocol')=='https' and fields.get('host')=='github.com' and fields.get('path')=='beckelaguas723-gif/otchet-parser.git':
        token=json.loads((Path(__file__).resolve().parents[1]/'config.local.json').read_text()).get('github_token')
        if token:sys.stdout.write('username=x-access-token\npassword='+token+'\n')
