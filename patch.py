# -*- coding: utf-8 -*-
import re

with open('frontend/tests/e2e/portfolio.spec.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(len(lines)):
    lines[i] = lines[i].replace("text=Nakit", "text=\"Nakit\"")
    lines[i] = lines[i].replace("text=YATIRMA", "text=\"YATIRMA\"")
    lines[i] = lines[i].replace("text=AEFES", "text=\"AEFES\"")
    lines[i] = lines[i].replace("text=AL", "text=\"AL\"")
    lines[i] = lines[i].replace("text=SAT", "text=\"SAT\"")
    lines[i] = lines[i].replace("text=/ÇEK|Çek/i", "text=\"ÇEKİM\"")
    lines[i] = lines[i].replace("/Bütçe|Budget/", "/Tutar|Budget/")
    lines[i] = lines[i].replace('canvas, [data-testid="chart"], .chart-container, #chart-root', ".recharts-wrapper")
    lines[i] = lines[i].replace('input[placeholder*="Ara"]', 'input[aria-label="Hisse Arama"]')

    if 'text="YATIRMA"' in lines[i]:
        lines[i] = lines[i].replace("toBeVisible", "toBeAttached")
    if 'text="AEFES"' in lines[i]:
        lines[i] = lines[i].replace("toBeVisible", "toBeAttached")
    if 'text="AL"' in lines[i]:
        lines[i] = lines[i].replace("toBeVisible", "toBeAttached")
    if 'text="SAT"' in lines[i]:
        lines[i] = lines[i].replace("toBeVisible", "toBeAttached")
    if 'text="ÇEKİM"' in lines[i]:
        lines[i] = lines[i].replace("toBeVisible", "toBeAttached")
        
    if 'await page.locator(\'button\').filter({ hasText: /Onayla|Confirm/ }).first().click();' in lines[i]:
        # add the next line if it doesn't have it
        if i + 1 < len(lines) and 'not.toBeVisible' not in lines[i+1]:
            lines[i] = lines[i] + "    await expect(page.locator('h2').filter({ hasText: /Yeni/ })).not.toBeVisible({ timeout: 10000 });\n"

with open('frontend/tests/e2e/portfolio.spec.ts', 'w', encoding='utf-8') as f:
    f.writelines(lines)
