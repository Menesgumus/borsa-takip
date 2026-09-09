import os

def find_replacement_char(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            content = f.read()
            if '\ufffd' in content:
                print(f"Found U+FFFD in {filepath}")
        except Exception:
            pass

for root, dirs, files in os.walk('frontend'):
    if 'node_modules' in root or '.next' in root:
        continue
    for file in files:
        if file.endswith(('.tsx', '.ts')):
            find_replacement_char(os.path.join(root, file))
