# -*- coding: utf-8 -*-

with open('frontend/tests/e2e/portfolio.spec.ts', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("await expect(page.locator('td').filter({ hasText: 'AEFES' })).toBeVisible({ timeout: 10000 });", "await expect(page.locator('td').filter({ hasText: 'AEFES' }).first()).toBeVisible({ timeout: 10000 });")

text = text.replace("await selectAction(page, 'YATIR/ÇEK');", "await selectAction(page, 'Para Çek');")

with open('frontend/tests/e2e/portfolio.spec.ts', 'w', encoding='utf-8') as f:
    f.write(text)
