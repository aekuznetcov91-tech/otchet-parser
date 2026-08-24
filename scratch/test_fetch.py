import urllib.request
try:
    req = urllib.request.Request('https://dashbord-partners1.pages.dev', headers={'User-Agent': 'Mozilla/5.0'})
    res = urllib.request.urlopen(req)
    print("SUCCESS", res.status)
except Exception as e:
    print("ERROR BODY:")
    print(e.read().decode('utf-8', errors='ignore'))
