/**
 * auth.spec.ts
 *
 * Critical auth lifecycle E2E:
 *   Register → Onboarding → Dashboard → Logout → Protected route redirect → Login
 *
 * Also runs Axe accessibility checks on login, register, onboarding pages.
 * Uses 127.0.0.1:8002 QA backend (mock market data, borsa_takip_test DB).
 */
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Auth Lifecycle', () => {

  test('Register, Onboarding, Logout, Protected Route, Login', async ({ page }, testInfo) => {
    // Unique email per worker/run to avoid conflicts in the shared test DB
    const randomEmail = `auth_${Date.now()}_${testInfo.workerIndex}@example.com`;
    const password = 'TestPassword123!';

    // 1. Unauthenticated access to protected route → redirect to login
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/.*\/login/);

    // Accessibility: login page
    const loginAxeResults = await new AxeBuilder({ page }).analyze();
    expect(loginAxeResults.violations, 'Login page has axe violations').toEqual([]);

    // 2. Navigate to register
    await page.goto('/register');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500); // allow React hydration

    // Accessibility: register page
    const registerAxeResults = await new AxeBuilder({ page }).analyze();
    expect(registerAxeResults.violations, 'Register page has axe violations').toEqual([]);

    await page.fill('#email', randomEmail);
    await page.fill('#password', password);
    await page.click('button[type="submit"]');

    // 3. Redirect to onboarding after registration
    await expect(page).toHaveURL(/.*\/onboarding/, { timeout: 15000 });

    // Accessibility: onboarding page
    const onboardingAxeResults = await new AxeBuilder({ page }).analyze();
    expect(onboardingAxeResults.violations, 'Onboarding page has axe violations').toEqual([]);

    // 4. Complete onboarding
    await page.fill('#firstName', 'QA');
    await page.fill('#lastName', 'Tester');
    await page.click('label:has(input[value="MEDIUM"])');
    await page.click('button[type="submit"]');

    // 5. Redirect to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });

    // 6. Logout — find the button by aria-label
    // On mobile, open the sidebar first
    await page.waitForTimeout(500); // allow responsive layout to settle
    const menuBtn = page.locator('button[aria-label="Menüyü Aç"]');
    if (await menuBtn.isVisible()) {
      await menuBtn.click();
      await page.waitForTimeout(500); // Wait for sidebar to slide in
    }
    const logoutBtn = page.locator('button[aria-label="Çıkış Yap"]').first();
    await logoutBtn.click();
    await expect(page).toHaveURL(/.*\/login/, { timeout: 15000 });

    // 7. Protected route is blocked again after logout
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/.*\/login/);

    // 8. Login with same credentials
    await page.fill('#email', randomEmail);
    await page.fill('#password', password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 15000 });
  });
});
