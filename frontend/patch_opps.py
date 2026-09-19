from pathlib import Path
import re
p = Path('frontend/app/(protected)/opportunities/page.tsx')
c = p.read_text('utf-8')

c = c.replace('const [selectedPortfolioId, setSelectedPortfolioId] = useState<number | null>(null);', 'const [selectedPortfolioId, setSelectedPortfolioId] = useState<number | null>(null);\n  const [selectedAssetClass, setSelectedAssetClass] = useState<string>("BIST_EQUITY");')

query_replace = '''queryKey: ["opportunities", selectedPortfolioId, selectedAssetClass],
    queryFn: () => {
      let url = selectedPortfolioId 
        ? /api/v1/opportunities?portfolio_id=&limit=20
        : /api/v1/opportunities?limit=20;
      if (selectedAssetClass !== "ALL") {
        url += &asset_class=;
      }
      return fetchApi(url);
    },'''
c = re.sub(r'queryKey: \["opportunities", selectedPortfolioId\],\n    queryFn: \(\) => {\n.*?(?=enabled:)', query_replace + '\n    ', c, flags=re.DOTALL)

ui_replace = '''<div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-navy-900 tracking-tight">Fırsatlar</h1>
          <p className="text-navy-700 mt-1">Sistem tarafından belirlenen güncel potansiyeller.</p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 items-center">
          <div className="flex flex-col gap-1 min-w-[200px]">
            <label className="text-sm font-medium text-navy-700">Portföy Seçimi</label>
            <select 
              className="w-full bg-surface border border-navy-800/20 rounded-lg px-3 py-2 text-sm text-navy-900 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={selectedPortfolioId || ""}
              onChange={(e) => handlePortfolioChange(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">Genel Piyasa Görünümü</option>
              {!isPortfoliosLoading && Array.isArray(portfolios) && portfolios.map((p: any) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          {selectedPortfolioId && (
            <div className="mt-5 sm:mt-5">
              <Link href={/portfolios/?tab=sepet} className="inline-flex items-center justify-center rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 transition-colors">
                <PieChartIcon className="h-4 w-4 mr-2" />
                Sepet Oluştur
              </Link>
            </div>
          )}
        </div>
      </div>
      
      {/* Tabs */}
      <div className="border-b border-navy-800/10">
        <nav className="-mb-px flex space-x-6 overflow-x-auto" aria-label="Tabs">
          {["BIST_EQUITY", "US_EQUITY", "GOLD", "ALL"].map((tab) => (
            <button
              key={tab}
              onClick={() => setSelectedAssetClass(tab)}
              className={${
                selectedAssetClass === tab
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-navy-600 hover:border-navy-300 hover:text-navy-800'
              } whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors}
            >
              {tab === "BIST_EQUITY" ? "BIST" : tab === "US_EQUITY" ? "US Equities" : tab === "GOLD" ? "Altın" : "Tümü"}
            </button>
          ))}
        </nav>
      </div>'''

c = re.sub(r'<div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">.*?(?=</select>\n          </div>\n        </div>)', ui_replace, c, flags=re.DOTALL)
# Fix the trailing tag issue from regex
c = c.replace('</select>\n          </div>\n        </div>', '')

p.write_text(c, 'utf-8')