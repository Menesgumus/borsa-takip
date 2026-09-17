import os, glob

for f in glob.glob('frontend/app/(auth)/*/page.tsx'):
    content = open(f, encoding='utf-8').read()
    content = content.replace('<main className="min-h-screen bg-slate-50 flex">', '<main role="main" id="main-content" className="min-h-screen bg-slate-50 flex">')
    
    # left panel
    content = content.replace('<div className="hidden lg:flex lg:w-1/2 bg-navy-900', '<aside aria-label="Branding" className="hidden lg:flex lg:w-1/2 bg-navy-900')
    content = content.replace('</div>\n      </div>\n\n      {/* Right panel - Form */}', '</div>\n      </aside>\n\n      {/* Right panel - Form */}')
    
    # right panel
    content = content.replace('<div className="w-full lg:w-1/2 flex items-center justify-center p-8">', '<section aria-label="Auth Form" className="w-full lg:w-1/2 flex items-center justify-center p-8">')
    content = content.replace('      </div>\n    </main>', '      </section>\n    </main>')
    
    open(f, 'w', encoding='utf-8', newline='\n').write(content)
