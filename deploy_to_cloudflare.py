import subprocess
import os
import sys
import json
import shutil

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
    token = os.environ.get("CLOUDFLARE_API_TOKEN", config.get("api_token", ""))
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", config.get("account_id", ""))
    project_name = config.get("project_name", "dashbord-partners1")
    
    env["CLOUDFLARE_API_TOKEN"] = token
    env["CLOUDFLARE_ACCOUNT_ID"] = account_id

    # Auto-add local node tools if present
    local_node_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scratch', 'tools', 'node-v20.18.0-darwin-arm64', 'bin')
    if os.path.exists(local_node_bin):
        env["PATH"] = local_node_bin + os.pathsep + env.get("PATH", "")

    site_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site')
    if not os.path.exists(site_dir):
        print(f"[!] Oshibka: Papka {site_dir} ne naydena!")
        sys.exit(1)

    env["PYTHONIOENCODING"] = "utf-8"
    env["NO_COLOR"] = "1"

    # Determine npx executable
    npx_bin = "npx.cmd" if sys.platform.startswith("win") else "npx"
    if not shutil.which(npx_bin, path=env.get("PATH")):
        if os.path.exists(os.path.join(local_node_bin, 'npx')):
            npx_bin = os.path.join(local_node_bin, 'npx')

    cmd = [npx_bin, "wrangler", "pages", "deploy", site_dir, f"--project-name={project_name}", "--commit-dirty=true", "--branch=main"]
    
    try:
        res = subprocess.run(cmd, env=env, capture_output=True, errors='replace')
        stdout = res.stdout.decode('utf-8', errors='replace') if isinstance(res.stdout, bytes) else (res.stdout or '')
        stderr = res.stderr.decode('utf-8', errors='replace') if isinstance(res.stderr, bytes) else (res.stderr or '')
        combined = stdout + stderr
        if res.returncode == 0 or 'Success' in combined or 'Deploying' in combined or 'pages.dev' in combined:
            print("[+] USPESHNO VYGRUZHENO NA CLOUDFLARE PAGES!")
            print("[+] Sayt s avtorizaciey: https://dashbord-partners.beckelaguas723.workers.dev")
            print("[+] Pryamaya ssylka:     https://dashbord-partners1.pages.dev")
        else:
            print("[!] Oshibka wrangler:")
            print(stderr or stdout)
    except Exception as e:
        print(f"[!] Oshibka: {e}")

if __name__ == '__main__':
    deploy()

