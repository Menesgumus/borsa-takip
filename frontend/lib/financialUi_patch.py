from pathlib import Path

path = Path('lib/financialUi.ts')
content = path.read_text(encoding='utf-8')

# Find formatTry and add formatMoney
format_money = '''export function formatMoney(value: number | string | null | undefined, currency: string = "TRY"): string {
  if (value === null || value === undefined) return "-";
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return "-";
  
  const formatter = new Intl.NumberFormat("tr-TR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  
  const formatted = formatter.format(num);
  
  if (currency === "USD") return "$" + formatted;
  if (currency === "TRY") return formatted + " ₺";
  return formatted + " " + currency;
}'''

content = content.replace("export function formatTry", format_money + "\n\nexport function formatTry")

path.write_text(content, encoding='utf-8')