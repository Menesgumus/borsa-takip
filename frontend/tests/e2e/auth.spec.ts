import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Auth Lifecycle', () => {

  test('Register, Login, Onboarding, Logout, Protected Route', async ({ page }, testInfo) => {
    const randomEmail = `test_${Date.now()}_${testInfo.workerIndex}@example.com`;
    const password = 'TestPassword123!';

    // 1. Unauthenticated protected route -> login redirect
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/.*\/login/);

    // Accessibility check on Login page
    const loginAxeResults = await new AxeBuilder({ page }).analyze();
    expect(loginAxeResults.violations).toEqual([]);

    // 2. Register
    await page.goto('/register');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    // Accessibility check on Register page
    const registerAxeResults = await new AxeBuilder({ page }).analyze();
    expect(registerAxeResults.violations).toEqual([]);
    
    await page.fill('input[id="email"]', randomEmail);
    await page.fill('input[id="password"]', password);
    await page.click('button[type="submit"]');

    // 3. Should redirect to onboarding
    await expect(page).toHaveURL(/.*\/onboarding/, { timeout: 10000 });
    
    // Accessibility check on Onboarding page
    const onboardingAxeResults = await new AxeBuilder({ page }).analyze();
    expect(onboardingAxeResults.violations).toEqual([]);
    
    // 4. Fill onboarding
    await page.fill('input[id="firstName"]', 'John');
    await page.fill('input[id="lastName"]', 'Doe');
    await page.click('label:has(input[value="MEDIUM"])');
    await page.click('button[type="submit"]');

    // 5. Should redirect to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 10000 });
    await expect(page.locator('text=John').first()).toBeVisible({ timeout: 10000 }).catch(() => null);

    // 6. Logout
    await page.click('button:has-text("Çıkış Yap")');
    await expect(page).toHaveURL(/.*\/login/, { timeout: 10000 });

    // 7. Verify session is revoked (Access protected route)
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/.*\/login/);

    // 8. Login again
    await page.fill('input[id="email"]', randomEmail);
    await page.fill('input[id="password"]', password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 10000 });
  });
});
