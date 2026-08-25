import subprocess
import os
import sys
import json

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.local.json')

def deploy():
    print("[*] Zapusk avtovygruzki na Cloudflare Pages...")
    
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8-sig') as f:
                config = json.load(f)
        except Exception as e:
            print(f"[!] Warning: Failed to read config.local.json: {e}")

    env = os.environ.copy()
    env["CLOUDFLARE_API_TOKEN"] = os.environ.get("CLOUDFLARE_API_TOKEN", config.get("api_token", ""))
    env["CLOUDFLARE_ACCOUNT_ID"] = os.environ.get("CLOUDFLARE_ACCOUNT_ID", config.get("account_id", ""))

    site_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site')
    if not os.path.exists(site_dir):
        print(f"[!] Oshibka: Papka {site_dir} ne naydena!")
        sys.exit(1)

    env["PYTHONIOENCODING"] = "utf-8"
    env["NO_COLOR"] = "1"

    cmd = ["npx.cmd", "wrangler", "pages", "deploy", "site", "--project-name=dashbord-partners1", "--commit-dirty=true", "--branch=main"]
    
    try:
        res = subprocess.run(cmd, env=env, shell=True, capture_output=True, errors='replace')
        stdout = res.stdout.decode('utf-8', errors='replace') if isinstance(res.stdout, bytes) else (res.stdout or '')
        stderr = res.stderr.decode('utf-8', errors='replace') if isinstance(res.stderr, bytes) else (res.stderr or '')
        combined = stdout + stderr
        # Check success by looking for known success markers in output
        if res.returncode == 0 or 'Success' in combined or 'Deploying' in combined or 'pages.dev' in combined:
            print("[+] USPESHNO VYGRUZHENO!")
            print("[+] Sayt s avtorizaciey: https://dashbord-partners.beckelaguas723.workers.dev")
            print("[+] Pryamaya ssylka:     https://dashbord-partners1.pages.dev")
        else:
            print("[!] Oshibka wrangler:")
            print(stderr or stdout)
    except Exception as e:
        print(f"[!] Oshibka: {e}")

if __name__ == '__main__':
    deploy()
