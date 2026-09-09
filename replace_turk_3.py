import os

filepath = 'frontend/app/(protected)/instruments/[symbol]/page.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("KAYNAÄžI BAÄžLI DEÄžİL", "KAYNAĞI BAĞLI DEĞİL")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
