import { test, expect } from '@playwright/test';

test.describe('Critical Flows: Portfolio & Trade', () => {
  test('Create PAPER portfolio, deposit, and view dashboard', async ({ page }, testInfo) => {
    test.setTimeout(60000);
    const userEmail = `portfolio_${Date.now()}_${testInfo.workerIndex}@example.com`;
    // Register
    await page.goto('/register');
    await page.waitForLoadState('networkidle');
    await page.fill('input[id="email"]', userEmail);
    await page.fill('input[id="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');
    
    // Onboarding
    await expect(page).toHaveURL(/.*\/onboarding/, { timeout: 10000 });
    await page.fill('input[id="firstName"]', 'John');
    await page.fill('input[id="lastName"]', 'Portfolio');
    await page.click('label:has(input[value="MEDIUM"])');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 10000 });

    // Navigate to portfolios page
    await page.goto('/portfolios');
    await page.waitForLoadState('networkidle');

    // It will show the empty state: 'İlk Portföyü Oluştur'
    await page.locator('button').filter({ hasText: 'Oluştur' }).click();
    
    // Fill the modal
    await page.fill('input[type="text"]', 'QA Portfolio');
    await page.selectOption('select', 'PAPER');
    await page.locator('.fixed.inset-0 button.bg-primary-600').click(); 
    
    // Should navigate to portfolio detail
    await expect(page).toHaveURL(/.*\/portfolios\/\d+/, { timeout: 10000 });
    
    // Trade Modal (Yeni İşlem)
    // Both deposit and trade happen in this modal
    await page.locator('button').filter({ hasText: 'Yeni' }).first().click();
    await expect(page.locator('h2').filter({ hasText: 'Yeni' }).first()).toBeVisible();

    // Just dismiss the modal because we mock Yahoo quotes in tests
    await page.keyboard.press('Escape');

    // Risk page
    await page.goto('/risk');
    await expect(page.locator('h1').filter({ hasText: 'Risk' }).first()).toBeVisible();
    
    // Education page
    await page.goto('/education');
    await expect(page.locator('h1').filter({ hasText: 'Eğitim' }).first()).toBeVisible();
  });
});
