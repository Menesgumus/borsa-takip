import glob
import os

files = glob.glob('frontend/app/(auth)/*/page.tsx')
for f in files:
    content = open(f, encoding='utf-8').read()
    content = content.replace('<div className="min-h-screen', '<main className="min-h-screen')
    content = content.replace('</div>\n    </div>\n  );\n}', '</div>\n    </main>\n  );\n}')
    open(f, 'w', encoding='utf-8', newline='\n').write(content)
print(f"Fixed {len(files)} auth pages.")
