import subprocess
import os
import sys
import json
import shutil

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

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

    # Auto-add npm global path on Windows
    if sys.platform.startswith("win"):
        appdata_npm = os.path.join(os.environ.get("APPDATA", ""), "npm")
        if os.path.exists(appdata_npm) and appdata_npm not in env.get("PATH", ""):
            env["PATH"] = appdata_npm + os.pathsep + env.get("PATH", "")

    site_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site')
    if not os.path.exists(site_dir):
        print(f"[!] Oshibka: Papka {site_dir} ne naydena!")
        sys.exit(1)

    env["PYTHONIOENCODING"] = "utf-8"
    env["NO_COLOR"] = "1"

    # Determine wrangler / npx executable
    wrangler_bin = "wrangler.cmd" if sys.platform.startswith("win") else "wrangler"
    wrangler_path = shutil.which(wrangler_bin, path=env.get("PATH"))
    
    if wrangler_path:
        cmd = [wrangler_path, "pages", "deploy", site_dir, f"--project-name={project_name}", "--commit-dirty=true", "--branch=main"]
    else:
        npx_bin = "npx.cmd" if sys.platform.startswith("win") else "npx"
        if not shutil.which(npx_bin, path=env.get("PATH")):
            if os.path.exists(os.path.join(local_node_bin, 'npx')):
                npx_bin = os.path.join(local_node_bin, 'npx')
        cmd = [npx_bin, "--yes", "wrangler", "pages", "deploy", site_dir, f"--project-name={project_name}", "--commit-dirty=true", "--branch=main"]

    try:
        print(f"[*] Komanda: {' '.join(cmd)}")
        res = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300
        )
        combined = (res.stdout or "") + "\n" + (res.stderr or "")
        print(combined)
        
        if res.returncode == 0 or 'Success' in combined or 'Deployment complete' in combined or 'pages.dev' in combined:
            print("\n[+] USPESHNO VYGRUZHENO NA CLOUDFLARE PAGES!")
            print("[+] Sayt s avtorizaciey: https://dashbord-partners.beckelaguas723.workers.dev")
            print("[+] Pryamaya ssylka:     https://dashbord-partners1.pages.dev")
        else:
            print("\n[!] Oshibka wrangler pri vygruzke:")
            if not combined.strip():
                print(f"Protsess zavershilsya s kodom {res.returncode}")
    except subprocess.TimeoutExpired:
        print("\n[!] Warning: Wrangler process timed out, continuing...")
    except Exception as e:
        print(f"[!] Oshibka: {e}")

    # Synchronize and push all changes to Git (origin main)
    sync_and_push_git()

def sync_and_push_git(commit_message=None):
    """Auto-syncs and pushes all tracked and modified files to Git origin main."""
    print("\n[*] Sinkhronizatsiya i otpravka v Git (origin main)...")
    try:
        status_res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, errors='replace')
        if status_res.returncode == 0:
            changes = status_res.stdout.strip()
            if changes:
                print("[*] Obnaruzheny izmeneniya dlya Git:")
                for l in changes.splitlines()[:10]:
                    print(f"    {l}")
                if len(changes.splitlines()) > 10:
                    print(f"    ... i esche {len(changes.splitlines()) - 10} faylov")
                
                # Always rebase latest remote commits before committing to prevent push rejects
                subprocess.run(["git", "pull", "--rebase", "origin", "main"], capture_output=True)
                
                subprocess.run(["git", "add", "raw_data/", "data.json", "site/", "scripts/", "js/", "css/", "docs/", "README.md", "deploy_to_cloudflare.py", "partners_registry.json", "russia_dealer_benchmarks.json", "data/", ".geminirules", ".cursorrules", ".windsurfrules", "AGENTS.md"], capture_output=True)
                
                msg = commit_message or "data(deploy): auto-sync data and assets with Cloudflare deployment"
                subprocess.run(["git", "commit", "-m", msg], capture_output=True)
                
                push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, errors='replace')
                if push_res.returncode == 0:
                    print("[+] Uspeshno zapusheno v Git (origin main)!")
                else:
                    print(f"[!] Warning Git push: {push_res.stderr.strip() or push_res.stdout.strip()}")
            else:
                print("[+] Git derevo chistoe, vse izmeneniya uzhe v Git.")
    except Exception as e:
        print(f"[!] Warning Git sync: {e}")

if __name__ == '__main__':
    deploy()



