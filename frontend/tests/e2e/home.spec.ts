/**
 * home.spec.ts
 *
 * Root routing and login page accessibility tests.
 * Uses Axe against the real rendered login page.
 */
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Root Routing and Accessibility', () => {

  test('root redirects to login when unauthenticated', async ({ page }) => {
    await page.goto('/');
    // Should redirect to login
    await expect(page).toHaveURL(/.*\/login.*/);

    // Assert login page h1 is present
    const loginH1 = page.locator('h1').first();
    await expect(loginH1).toBeVisible({ timeout: 10000 });
  });

  test('login page should not have any automatically detectable accessibility issues', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500); // allow hydration

    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations, 'Login page Axe violations').toEqual([]);
  });

});
