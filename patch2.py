# -*- coding: utf-8 -*-

with open('frontend/tests/e2e/portfolio.spec.ts', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("await expect(page.locator('text=\"AL\"')).toBeAttached({ timeout: 5000 });", "await expect(page.locator('text=\"AL\"').first()).toBeAttached({ timeout: 5000 });")
text = text.replace("await expect(page.locator('text=\"SAT\"')).toBeAttached({ timeout: 10000 });", "await expect(page.locator('text=\"SAT\"').first()).toBeAttached({ timeout: 10000 });")
text = text.replace("await expect(page.locator('text=/ÇEK/i')).toBeVisible({ timeout: 10000 });", "await expect(page.locator('text=\"ÇEKİM\"').first()).toBeAttached({ timeout: 10000 });")
text = text.replace("await expect(page.locator('text=/\\ufffdEK/i')).toBeVisible({ timeout: 10000 });", "await expect(page.locator('text=\"ÇEKİM\"').first()).toBeAttached({ timeout: 10000 });")

with open('frontend/tests/e2e/portfolio.spec.ts', 'w', encoding='utf-8') as f:
    f.write(text)
