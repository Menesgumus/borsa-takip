import os
import glob

for filepath in glob.glob('tests/api/test_*.py'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace /api/v1/portfolios/ with /api/v1/portfolios
    content = content.replace('"/api/v1/portfolios/"', '"/api/v1/portfolios"')
    content = content.replace('"/api/v1/chat/threads/"', '"/api/v1/chat/threads"')
    content = content.replace('"/api/v1/decisions/"', '"/api/v1/decisions"')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
