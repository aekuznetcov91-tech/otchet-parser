import urllib.request
import json
import os
import mimetypes
import hashlib
import sys

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8-sig')
    except AttributeError:
        pass

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.local.json')
config = {}
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8-sig') as f:
            config = json.load(f)
    except Exception as e:
        print(f"[!] Warning: Failed to read config.local.json: {e}")

ACCOUNT_ID = os.environ.get('CLOUDFLARE_ACCOUNT_ID', config.get('account_id', '8847a4c47c5dbe34f3887ce61182873a'))
API_TOKEN = os.environ.get('CLOUDFLARE_API_TOKEN', config.get('api_token', ''))
PROJECT_NAME = config.get('project_name', 'dashbord-partners1')
SITE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site')

def deploy():
    print(f"[*] Podgotovka k vygruzke v Cloudflare Pages ({PROJECT_NAME})...")
    
    if not API_TOKEN:
        print("[!] Oshibka: API Token ne ukazan v config.local.json ili CLOUDFLARE_API_TOKEN!")
        sys.exit(1)

    if not os.path.exists(SITE_DIR):
        print(f"[!] Oshibka: Papka {SITE_DIR} ne naydena!")
        sys.exit(1)

    url = f'https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT_NAME}/deployments'
    boundary = '----WebKitFormBoundaryAutoDeploy7MA4YWxkTrZu0gW'
    body = bytearray()

    manifest = {}
    files_to_upload = {}

    total_size = 0
    file_count = 0

    for root, dirs, files in os.walk(SITE_DIR):
        for f in files:
            file_path = os.path.join(root, f)
            rel_path = '/' + os.path.relpath(file_path, SITE_DIR).replace('\\', '/')
            with open(file_path, 'rb') as fp:
                content = fp.read()
            sha256_hash = hashlib.sha256(content).hexdigest()
            manifest[rel_path] = sha256_hash
            files_to_upload[sha256_hash] = (rel_path, content)
            total_size += len(content)
            file_count += 1

    print(f"[*] Naydeno faylov: {file_count} (ob'em: {total_size / (1024*1024):.2f} MB)")

    # 1. Manifest
    body.extend(f'--{boundary}\r\n'.encode('utf-8'))
    body.extend(f'Content-Disposition: form-data; name="manifest"\r\n\r\n'.encode('utf-8'))
    body.extend(json.dumps(manifest).encode('utf-8'))
    body.extend(b'\r\n')

    # 2. Files
    for sha256_hash, (rel_path, content) in files_to_upload.items():
        mime_type = mimetypes.guess_type(rel_path)[0] or 'application/octet-stream'
        body.extend(f'--{boundary}\r\n'.encode('utf-8'))
        body.extend(f'Content-Disposition: form-data; name="{sha256_hash}"; filename="{sha256_hash}"\r\n'.encode('utf-8'))
        body.extend(f'Content-Type: {mime_type}\r\n\r\n'.encode('utf-8'))
        body.extend(content)
        body.extend(b'\r\n')

    body.extend(f'--{boundary}--\r\n'.encode('utf-8'))

    req = urllib.request.Request(url, data=bytes(body), method='POST')
    req.add_header('Authorization', f'Bearer {API_TOKEN}')
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')

    print("[*] Otpravka faylov na Cloudflare...")
    try:
        with urllib.request.urlopen(req) as res:
            resp_data = json.loads(res.read().decode('utf-8'))
            if resp_data.get('success'):
                deploy_url = resp_data['result']['url']
                print("[+] USPESHNO VYGRUZHENO!")
                print(f"[+] Ssylka na deploy: {deploy_url}")
                print(f"[+] Osnovnoy sayt: https://dashbord-partners1.pages.dev")
            else:
                print("[!] Otvet Cloudflare:", resp_data)
    except urllib.error.HTTPError as e:
        print(f"[!] Oshibka HTTP {e.code}: {e.read().decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Oshibka: {e}")
        sys.exit(1)

if __name__ == '__main__':
    deploy()

