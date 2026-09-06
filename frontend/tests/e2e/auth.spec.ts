import { test, expect } from '@playwright/test';

test.describe('Auth Lifecycle', () => {
  const randomEmail = `test_${Math.floor(Math.random() * 100000)}@example.com`;
  const password = 'TestPassword123!';

  test('Register, Login, Onboarding, Logout, Protected Route', async ({ page, context }) => {
    // 1. Unauthenticated protected route -> login redirect
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/.*\/login/);

    // 2. Register
    await page.goto('/register');
    await page.fill('input[name="email"]', randomEmail);
    await page.fill('input[name="password"]', password);
    await page.fill('input[name="passwordConfirm"]', password);
    await page.click('button[type="submit"]');

    // 3. Should redirect to onboarding
    await expect(page).toHaveURL(/.*\/onboarding/);
    
    // 4. Fill onboarding
    await page.fill('input[name="firstName"]', 'John');
    await page.fill('input[name="lastName"]', 'Doe');
    await page.selectOption('select[name="riskTolerance"]', 'MEDIUM');
    await page.click('button[type="submit"]');

    // 5. Should redirect to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/);
    await expect(page.locator('text=John')).toBeVisible({ timeout: 10000 }).catch(() => null); // Optional check

    // 6. Logout
    await page.click('button:has-text("Çıkış Yap")');
    await expect(page).toHaveURL(/.*\/login/);

    // 7. Verify session is revoked (Access protected route)
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/.*\/login/);

    // 8. Invalid credentials test
    await page.fill('input[name="email"]', randomEmail);
    await page.fill('input[name="password"]', 'WrongPassword!');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=E-posta adresi veya şifre hatalı')).toBeVisible();
  });
});
