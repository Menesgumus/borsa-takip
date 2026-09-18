import { test, expect } from '@playwright/test';

test('Dump Card HTML', async ({ page }) => {
  await page.goto('/register');
  const ts = Date.now();
  const email = `debug_${ts}@example.com`;
  await page.fill('#email', email);
  await page.fill('#password', 'TestPassword123!');
  await page.click('button[type="submit"]');
  await page.locator('#firstName').waitFor({ state: 'visible' });
  await page.locator('#firstName').fill('Debug');
  await page.locator('#lastName').fill('User');
  await page.getByText('ORTA', { exact: true }).click();
  await page.locator('button[type="submit"]').click();
  
  await page.waitForURL('**/dashboard');
  
  // Create empty portfolio
  await page.goto('/portfolios');
  await page.getByRole('button', { name: /Oluştur/i }).first().click();
  await page.fill('input[type="text"]', 'Empty Portfolio');
  await page.locator('.fixed button.bg-primary-600, dialog button.bg-primary-600, [role="dialog"] button.bg-primary-600').first().click();
  await page.waitForTimeout(2000);

  await page.goto('/opportunities');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);
  
  const cards = page.locator('a[href^="/opportunities/"]');
  const count = await cards.count();
  console.log(`FOUND CARDS: ${count}`);
  if (count > 0) {
    const html = await cards.nth(0).evaluate(el => el.outerHTML);
    console.log(`CARD 0 HTML:\n${html}`);
  }
});
