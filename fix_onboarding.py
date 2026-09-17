import os

f = 'frontend/app/(protected)/onboarding/page.tsx'
content = open(f, encoding='utf-8').read()

content = content.replace('<div className="max-w-2xl mx-auto py-12 animate-in fade-in duration-500">', '<main className="max-w-2xl mx-auto py-12 animate-in fade-in duration-500">')
# the file ends with </div>\n    </div>\n  );\n} ... wait, let's just replace the outermost div.
parts = content.rsplit('</div>\n  );\n}', 1)
if len(parts) == 2:
    content = '</main>\n  );\n}'.join(parts)

open(f, 'w', encoding='utf-8', newline='\n').write(content)
print("Onboarding landmarks fixed.")
