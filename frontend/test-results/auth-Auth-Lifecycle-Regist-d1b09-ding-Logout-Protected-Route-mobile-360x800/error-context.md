# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.ts >> Auth Lifecycle >> Register, Login, Onboarding, Logout, Protected Route
- Location: tests\e2e\auth.spec.ts:7:7

# Error details

```
Error: expect(page).toHaveURL(expected) failed

Expected pattern: /.*\/onboarding/
Received string:  "http://localhost:3000/register"
Timeout: 5000ms

Call log:
  - Expect "toHaveURL" with timeout 5000ms
    14 × locator resolved to <html lang="tr">…</html>
       - unexpected value "http://localhost:3000/register"

```

```yaml
- heading "Yeni Hesap Oluşturun" [level=2]
- text: E-posta adresi
- textbox "E-posta adresi": test_77868@example.com
- text: Şifre
- textbox "Şifre":
  - /placeholder: Şifre (En az 8 karakter)
  - text: TestPassword123!
- text: Şifreyi Onayla
- textbox "Şifreyi Onayla": TestPassword123!
- text: Bilinmeyen bir API hatası oluştu
- button "Kayıt Ol"
- text: Zaten hesabınız var mı?
- link "Giriş Yapın":
  - /url: /login
- alert
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Auth Lifecycle', () => {
  4  |   const randomEmail = `test_${Math.floor(Math.random() * 100000)}@example.com`;
  5  |   const password = 'TestPassword123!';
  6  | 
  7  |   test('Register, Login, Onboarding, Logout, Protected Route', async ({ page, context }) => {
  8  |     // 1. Unauthenticated protected route -> login redirect
  9  |     await page.goto('/dashboard');
  10 |     await expect(page).toHaveURL(/.*\/login/);
  11 | 
  12 |     // 2. Register
  13 |     await page.goto('/register');
  14 |     await page.fill('input[name="email"]', randomEmail);
  15 |     await page.fill('input[name="password"]', password);
  16 |     await page.fill('input[name="passwordConfirm"]', password);
  17 |     await page.click('button[type="submit"]');
  18 | 
  19 |     // 3. Should redirect to onboarding
> 20 |     await expect(page).toHaveURL(/.*\/onboarding/);
     |                        ^ Error: expect(page).toHaveURL(expected) failed
  21 |     
  22 |     // 4. Fill onboarding
  23 |     await page.fill('input[name="firstName"]', 'John');
  24 |     await page.fill('input[name="lastName"]', 'Doe');
  25 |     await page.selectOption('select[name="riskTolerance"]', 'MEDIUM');
  26 |     await page.click('button[type="submit"]');
  27 | 
  28 |     // 5. Should redirect to dashboard
  29 |     await expect(page).toHaveURL(/.*\/dashboard/);
  30 |     await expect(page.locator('text=John')).toBeVisible({ timeout: 10000 }).catch(() => null); // Optional check
  31 | 
  32 |     // 6. Logout
  33 |     await page.click('button:has-text("Çıkış Yap")');
  34 |     await expect(page).toHaveURL(/.*\/login/);
  35 | 
  36 |     // 7. Verify session is revoked (Access protected route)
  37 |     await page.goto('/dashboard');
  38 |     await expect(page).toHaveURL(/.*\/login/);
  39 | 
  40 |     // 8. Invalid credentials test
  41 |     await page.fill('input[name="email"]', randomEmail);
  42 |     await page.fill('input[name="password"]', 'WrongPassword!');
  43 |     await page.click('button[type="submit"]');
  44 |     await expect(page.locator('text=E-posta adresi veya şifre hatalı')).toBeVisible();
  45 |   });
  46 | });
  47 | 
```