import os

filepath = 'frontend/app/(protected)/dashboard/page.tsx'
with open(filepath, 'rb') as f:
    content = f.read()
    if b'G' in content:
        idx = content.find(b'G')
        print(content[idx:idx+20])
