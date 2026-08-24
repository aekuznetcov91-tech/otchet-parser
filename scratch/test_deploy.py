import urllib.request
import json
import os
import mimetypes
import hashlib

account_id = '8847a4c47c5dbe34f3887ce61182873a'
api_token = 'cfut_q7HetIQoFb0tMezDfBGRTZZpJi40eG7Ul0MRVRq326b7e897'
project_name = 'dashbord-partners1'
site_dir = './site'

url = f'https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/{project_name}/deployments'
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = bytearray()

manifest = {}
files_to_upload = {}

for root, dirs, files in os.walk(site_dir):
    for f in files:
        file_path = os.path.join(root, f)
        rel_path = '/' + os.path.relpath(file_path, site_dir).replace('\\', '/')
        with open(file_path, 'rb') as fp:
            content = fp.read()
        sha256_hash = hashlib.sha256(content).hexdigest()
        manifest[rel_path] = sha256_hash
        files_to_upload[sha256_hash] = (rel_path, content)

# Add manifest field
body.extend(f'--{boundary}\r\n'.encode('utf-8'))
body.extend(f'Content-Disposition: form-data; name="manifest"\r\n\r\n'.encode('utf-8'))
body.extend(json.dumps(manifest).encode('utf-8'))
body.extend(b'\r\n')

# Add files keyed by sha256
for sha256_hash, (rel_path, content) in files_to_upload.items():
    mime_type = mimetypes.guess_type(rel_path)[0] or 'application/octet-stream'
    body.extend(f'--{boundary}\r\n'.encode('utf-8'))
    body.extend(f'Content-Disposition: form-data; name="{sha256_hash}"; filename="{sha256_hash}"\r\n'.encode('utf-8'))
    body.extend(f'Content-Type: {mime_type}\r\n\r\n'.encode('utf-8'))
    body.extend(content)
    body.extend(b'\r\n')

body.extend(f'--{boundary}--\r\n'.encode('utf-8'))

req = urllib.request.Request(url, data=bytes(body), method='POST')
req.add_header('Authorization', f'Bearer {api_token}')
req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')

try:
    res = urllib.request.urlopen(req)
    print("SUCCESS!")
    print(res.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.code)
    print(e.read().decode('utf-8'))
except Exception as e:
    print("ERROR:", str(e))
