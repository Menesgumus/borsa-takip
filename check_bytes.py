import os

filepath = 'frontend/app/(protected)/dashboard/page.tsx'
with open(filepath, 'rb') as f:
    content = f.read()
    if b'0,00' in content:
        idx = content.find(b'0,00')
        print(content[idx:idx+20])
