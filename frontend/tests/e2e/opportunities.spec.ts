import { test, expect, Page } from '@playwright/test';

test.describe('Phase 26.1 Opportunities E2E', () => {
  test.describe.configure({ mode: 'serial' });

  let page: Page;

  test.beforeAll(async ({ browser }) => {
    page = await browser.newPage();
  });

  test.afterAll(async () => {
    await page.close();
  });

  async function registerAndOnboard(page: Page, email: string, password: string) {
    await page.goto('/register');
    await page.fill('#email', email);
    await page.fill('#password', password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*\/onboarding/, { timeout: 20000 });
    
    await page.waitForTimeout(1000); // Wait for React to settle
    
    await page.fill('#firstName', 'QA');
    await page.fill('#lastName', 'Opportunity');
    
    const submitBtn = page.locator('button[type="submit"]');
    await expect(async () => {
      await page.getByText('ORTA', { exact: true }).click();
      await expect(submitBtn).toBeEnabled({ timeout: 2000 });
    }).toPass({ timeout: 20000 });
    
    // Check if firstName is really filled, if not fill again
    const fname = await page.inputValue('#firstName');
    if (!fname) {
        await page.fill('#firstName', 'QA');
        await page.fill('#lastName', 'Opportunity');
    }

    await submitBtn.click();
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 20000 });
  }

  test('Opportunities Workflow & Monotonicity', async () => {
    test.setTimeout(180000);
    const ts = Date.now();
    const randomSuffix = Math.random().toString(36).substring(7);
    const email = `oppqa_${ts}_${randomSuffix}@example.com`;
    const pwd = 'TestPassword123!';
    
    await registerAndOnboard(page, email, pwd);

    await page.goto('/portfolios');
    const createInitialBtn = page.getByRole('button', { name: /Oluştur/i }).first();
    await expect(createInitialBtn).toBeVisible({ timeout: 10000 });
    await createInitialBtn.click();
    await page.fill('input[type="text"]', 'Empty Portfolio');
    const hasPaperSelect = await page.locator('select').count() > 0;
    if (hasPaperSelect) {
      await page.selectOption('select', 'PAPER').catch(() => null);
    }
    await page.locator('.fixed button.bg-primary-600, dialog button.bg-primary-600, [role="dialog"] button.bg-primary-600').first().click();
    await expect(page.locator('text="Empty Portfolio"').first()).toBeVisible({ timeout: 30000 });
    
    await page.goto('/opportunities');
    await page.waitForLoadState('networkidle');

    const portfolioSelect = page.locator('select');
    await portfolioSelect.selectOption({ label: 'Genel Piyasa Görünümü' });
    await expect(page.locator('span.px-2.py-1.text-xs.font-bold', { hasText: /AL/ }).first()).toBeVisible({ timeout: 60000 });

    await portfolioSelect.selectOption({ label: 'Empty Portfolio' });
    await page.waitForLoadState('networkidle');
    await expect(page.locator('.opacity-90').first()).toBeVisible({ timeout: 60000 });
    
    let buyLocator = page.locator('span.px-2.py-1.text-xs.font-bold', { hasText: /AL/ });
    await expect(buyLocator).toHaveCount(0, { timeout: 60000 });

    await portfolioSelect.selectOption({ label: 'Genel Piyasa Görünümü' });
    await expect(buyLocator).not.toHaveCount(0, { timeout: 60000 });
    
    const firstOpportunity = page.locator('a[href^="/opportunities/"]').first();
    await expect(firstOpportunity).toBeVisible({ timeout: 120000 });
    await firstOpportunity.click();
    await expect(page).toHaveURL(/.*\/opportunities\/[A-Z0-9.]+/, { timeout: 30000 });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const statsContainer = page.locator('text="Piyasa Görünümü"');
    await expect(statsContainer).toBeVisible({ timeout: 15000 });
    
    const futureWorkspaceMarker = page.locator('text="Gelecek çalışma alanı"');
    await expect(futureWorkspaceMarker).toBeVisible({ timeout: 15000 });
    await expect(page.locator('text="Veri Kalitesi"')).toBeVisible();
  });
});
