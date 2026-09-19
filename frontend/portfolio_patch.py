from pathlib import Path
import re

path = Path('frontend/app/(protected)/portfolios/[id]/page.tsx')
content = path.read_text(encoding='utf-8')

# Add formatMoney to import
content = content.replace('formatTry, formatQuantity, getProfitLossColorClass', 'formatTry, formatMoney, formatQuantity, getProfitLossColorClass')

# Update table headers
headers = '''<th className="px-5 py-3">Sembol</th>
                        <th className="px-5 py-3 text-right">Varlık Sınıfı</th>
                        <th className="px-5 py-3 text-right">Adet</th>
                        <th className="px-5 py-3 text-right">Ort. Maliyet (TRY)</th>
                        <th className="px-5 py-3 text-right">Anlık Fiyat (Native)</th>
                        <th className="px-5 py-3 text-right">Anlık Fiyat (TRY)</th>
                        <th className="px-5 py-3 text-right">Piyasa Değeri (TRY)</th>
                        <th className="px-5 py-3 text-right">Durum (K/Z)</th>'''
content = re.sub(r'<th className="px-5 py-3">Sembol</th>.*?<th className="px-5 py-3 text-right">Durum \(K/Z\)</th>', headers, content, flags=re.DOTALL)

# Update table row
row = '''<td className="px-5 py-4 font-semibold text-navy-900">
                            <Link href={/instruments/\} className="hover:text-primary-600 hover:underline">
                              {pos.symbol}
                            </Link>
                          </td>
                          <td className="px-5 py-4 text-right text-slate-600 font-medium text-xs">
                            {pos.asset_class?.replace('_', ' ') || '-'}
                          </td>
                          <td className="px-5 py-4 text-right font-medium">{formatQuantity(pos.quantity)}</td>
                          <td className="px-5 py-4 text-right text-slate-600">{formatTry(pos.average_cost)}</td>
                          <td className="px-5 py-4 text-right text-slate-600">
                            {pos.current_native_price != null ? formatMoney(pos.current_native_price, pos.native_currency || "TRY") : '-'}
                          </td>
                          <td className="px-5 py-4 text-right font-medium">
                            {pos.current_price != null ? formatTry(pos.current_price) : 'Yetersiz Veri'}
                          </td>
                          <td className="px-5 py-4 text-right font-medium">
                            {pos.market_value != null ? formatTry(pos.market_value) : 'Yetersiz Veri'}
                          </td>
                          <td className="px-5 py-4 text-right">'''

content = re.sub(r'<td className="px-5 py-4 font-semibold text-navy-900">.*?<td className="px-5 py-4 text-right">', row, content, flags=re.DOTALL)

# Add Sepet Oluştur tab button logic
tabs = '''{ id: "islemler", label: "İşlem Geçmişi", icon: History },
  ];'''

new_tabs = '''{ id: "islemler", label: "İşlem Geçmişi", icon: History },
    { id: "sepet", label: "Sepet Oluştur", icon: Briefcase },
  ];'''
content = content.replace(tabs, new_tabs)

# Make sure tabs block exists and was replaced. If the exact literal isn't found due to char diff, use regex
content = re.sub(r'\{\s*id:\s*"islemler".*?\},?\s*\n\s*\];', new_tabs, content, flags=re.DOTALL)

path.write_text(content, encoding='utf-8')