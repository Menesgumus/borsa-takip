import os

replacements = {
    'Ã¼': 'ü',
    'Ã§': 'ç',
    'ÅŸ': 'ş',
    'Ä±': 'ı',
    'Ã¶': 'ö',
    'Ã–': 'Ö',
    'Ã‡': 'Ç',
    'Ä°': 'İ',
    'Åž': 'Ş',
    'Ãœ': 'Ü',
    'â‚º': '₺',
    'ÃŸ': 'ß',
    'Ã¢': 'â',
    'Ã®': 'î',
    'Ã»': 'û',
    'ÄŸ': 'ğ',
    'Äž': 'Ğ',
    'Ã¡': 'á',
    'Ã©': 'é',
    'Ã­': 'í',
    'Ã³': 'ó',
    'Ãº': 'ú',
    'Ã±': 'ñ',
    'Ã': 'İ', # Note: 'Ã' might be a partial match, better be careful. Wait, 'Ä°' is 'İ', what is just 'Ã'? It's often followed by another character.
}

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    for bad, good in replacements.items():
        if bad != 'Ã':
            content = content.replace(bad, good)
            
    # Quick fix for any leftover 'Ã' that might be part of an incomplete replacement? Actually better not to do 'Ã' blindly.
    # We missed 'ğ' which is 'ÄŸ', 'Ğ' which is 'Äž'.
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filepath}")

for root, dirs, files in os.walk('frontend'):
    if 'node_modules' in root or '.next' in root:
        continue
    for file in files:
        if file.endswith(('.tsx', '.ts')):
            fix_file(os.path.join(root, file))
