import os

filepath = 'frontend/app/(protected)/portfolios/page.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()
    if 'â‚º' in content:
        print('FAIL')
    if '₺' in content:
        pass # success
