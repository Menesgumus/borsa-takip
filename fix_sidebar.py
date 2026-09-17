import os

f = 'frontend/components/Sidebar.tsx'
content = open(f, encoding='utf-8').read()

# Replace mobile header
content = content.replace('<div className="lg:hidden sticky top-0', '<header className="lg:hidden sticky top-0')
content = content.replace('Borsa Takip\n        </Link>\n      </div>', 'Borsa Takip\n        </Link>\n      </header>')

# Replace desktop sidebar
content = content.replace('<div className="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0', '<aside className="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0')

# For the end of desktop sidebar, we just find the last </div> before </>
parts = content.rsplit('</div>\n    </>', 1)
if len(parts) == 2:
    content = '</aside>\n    </>'.join(parts)

# For the mobile sidebar, we should probably also make the overlay wrapper a dialog or leave it as div.
# But `region` usually triggers if text/content is outside landmarks.

open(f, 'w', encoding='utf-8', newline='\n').write(content)
print("Sidebar landmarks fixed.")
