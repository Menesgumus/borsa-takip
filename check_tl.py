import os

filepath = 'frontend/app/(protected)/instruments/[symbol]/page.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()
    if 'â‚º' in content:
        print('Found â‚º')
