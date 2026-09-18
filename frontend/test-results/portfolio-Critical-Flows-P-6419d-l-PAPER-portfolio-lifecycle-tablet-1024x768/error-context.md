# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: portfolio.spec.ts >> Critical Flows: Portfolio & Trade >> Full PAPER portfolio lifecycle
- Location: tests\e2e\portfolio.spec.ts:81:7

# Error details

```
Error: expect(locator).toBeEnabled() failed

Locator:  locator('button[type="submit"]')
Expected: enabled
Received: disabled
Timeout:  20000ms

Call log:
  - Expect "toBeEnabled" locator('button[type="submit"]') with timeout 20000ms
  - waiting for locator('button[type="submit"]')
    42 × locator resolved to <button disabled type="submit" class="w-full py-4 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-bold text-lg transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed">Başla</button>
       - unexpected value "disabled"

```

```yaml
- button "Başla" [disabled]
```

# Test source

```ts
  1   | /**
  2   |  * portfolio.spec.ts
  3   |  *
  4   |  * Full critical-flow E2E for the portfolio feature:
  5   |  *   A. Create PAPER portfolio
  6   |  *   B. DEPOSIT 10,000 TRY  → assert cash & transaction history
  7   |  *   C. BUY by QUANTITY (AEFES, 1 share) → assert position & cash
  8   |  *   D. BUY by BUDGET  (THYAO, 500 TRY)  → assert quantity & cash
  9   |  *   E. SELL (AEFES all) → assert cash increases
  10  |  *   F. WITHDRAW        → assert cash decreases
  11  |  *   G. Risk page       → no errors, percentages visible
  12  |  *   H. Education page  → lesson page loads, image naturalWidth > 0
  13  |  *   I. Chart smoke     → GARAN detail page, chart container visible
  14  |  *
  15  |  * Prerequisites (handled by backend seed + QA env):
  16  |  *   - borsa_takip_test DB with seeded AEFES/THYAO/GARAN instruments
  17  |  *   - QA backend at 127.0.0.1:8002 with ENABLE_MOCK_MARKET_DATA=true
  18  |  */
  19  | import { test, expect, Page } from '@playwright/test';
  20  | 
  21  | // ─── Helpers ──────────────────────────────────────────────────────────────────
  22  | 
  23  | /** Register a fresh QA user, complete onboarding, and land on /dashboard. */
  24  | async function registerAndOnboard(page: Page, email: string, password: string) {
  25  |   await page.goto('/register');
  26  |   await page.waitForLoadState('networkidle');
  27  |   await page.waitForTimeout(500);
  28  |   await page.fill('#email', email);
  29  |   await page.fill('#password', password);
  30  |   await page.click('button[type="submit"]');
  31  |   await expect(page).toHaveURL(/.*\/onboarding/, { timeout: 20000 });
  32  |   
  33  |   const firstNameInput = page.locator('#firstName');
  34  |   await firstNameInput.waitFor({ state: 'visible' });
  35  |   await firstNameInput.fill('QA');
  36  |   await page.locator('#lastName').fill('Portfolio');
  37  |   await page.locator('label:has(input[value="MEDIUM"])').click();
  38  |   
  39  |   // On mobile, React may take longer to hydrate; re-click the risk label to
  40  |   // ensure the onChange fires and the form becomes valid before waiting
  41  |   await page.waitForTimeout(500);
  42  |   await page.locator('label:has(input[value="MEDIUM"])').click();
  43  |   
  44  |   const submitBtn = page.locator('button[type="submit"]');
> 45  |   await expect(submitBtn).toBeEnabled({ timeout: 20000 });
      |                           ^ Error: expect(locator).toBeEnabled() failed
  46  |   await submitBtn.click();
  47  |   await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 20000 });
  48  | }
  49  | 
  50  | /** Open the "Yeni İşlem" (trade) modal from the portfolio detail page. */
  51  | async function openTradeModal(page: Page) {
  52  |   // Make sure modal is not already open
  53  |   const modalOverlay = page.locator('.fixed.inset-0.z-50');
  54  |   if (await modalOverlay.isVisible()) {
  55  |     await page.keyboard.press('Escape');
  56  |     await expect(modalOverlay).not.toBeVisible({ timeout: 5000 });
  57  |   }
  58  |   // Click the "Yeni İşlem" button in the page (not inside modal)
  59  |   await page.getByRole('button', { name: /Yeni İşlem/ }).first().click();
  60  |   // Wait for modal header to appear
  61  |   await expect(page.locator('.fixed.inset-0.z-50 h2').filter({ hasText: /Yeni/ })).toBeVisible({ timeout: 8000 });
  62  | }
  63  | 
  64  | /** Select an action tab inside the already-open modal. */
  65  | async function selectAction(page: Page, label: string) {
  66  |   const modal = page.locator('.fixed.inset-0.z-50');
  67  |   await modal.getByRole('button', { name: label, exact: true }).click();
  68  |   await page.waitForTimeout(200);
  69  | }
  70  | 
  71  | /** Wait for the modal overlay to disappear after a successful transaction. */
  72  | async function waitForModalClose(page: Page) {
  73  |   const modalOverlay = page.locator('.fixed.inset-0.z-50');
  74  |   await expect(modalOverlay).not.toBeVisible({ timeout: 15000 });
  75  | }
  76  | 
  77  | // ─── Main test ────────────────────────────────────────────────────────────────
  78  | 
  79  | test.describe('Critical Flows: Portfolio & Trade', () => {
  80  | 
  81  |   test('Full PAPER portfolio lifecycle', async ({ page }, testInfo) => {
  82  |     // Allow extra time for full flow (7 sub-steps)
  83  |     test.setTimeout(180000);
  84  | 
  85  |     const email = `pf_${Date.now()}_${testInfo.workerIndex}@example.com`;
  86  |     const password = 'TestPassword123!';
  87  | 
  88  |     // ── Setup: register fresh user ──────────────────────────────────────────
  89  |     await registerAndOnboard(page, email, password);
  90  | 
  91  |     // ── A. Create PAPER portfolio ───────────────────────────────────────────
  92  |     await page.goto('/portfolios');
  93  |     await page.waitForLoadState('networkidle');
  94  | 
  95  |     // Empty state shows a create button
  96  |     const createBtn = page.getByRole('button', { name: /Oluştur/ }).first();
  97  |     await expect(createBtn).toBeVisible({ timeout: 10000 });
  98  |     await createBtn.click();
  99  | 
  100 |     // Fill the create-portfolio modal
  101 |     await page.fill('input[type="text"]', 'QA Portfolio');
  102 |     // Select PAPER type if select exists
  103 |     const hasPaperSelect = await page.locator('select').count() > 0;
  104 |     if (hasPaperSelect) {
  105 |       await page.selectOption('select', 'PAPER').catch(() => null);
  106 |     }
  107 |     // Submit the modal (the primary blue button inside the overlay)
  108 |     await page.locator('.fixed button.bg-primary-600, dialog button.bg-primary-600, [role="dialog"] button.bg-primary-600').first().click();
  109 | 
  110 |     // Should land on portfolio detail page
  111 |     await expect(page).toHaveURL(/.*\/portfolios\/\d+/, { timeout: 15000 });
  112 |     const portfolioUrl = page.url();
  113 |     const portfolioId = portfolioUrl.match(/portfolios\/(\d+)/)?.[1];
  114 |     expect(portfolioId).toBeTruthy();
  115 | 
  116 |     // ── B. DEPOSIT 10,000 TRY ──────────────────────────────────────────────
  117 |     await openTradeModal(page);
  118 |     let modal = page.locator('.fixed.inset-0.z-50');
  119 | 
  120 |     // Default tab is "Para Yatır" — just fill the amount
  121 |     const depositAmtInput = modal.locator('input[type="number"]').first();
  122 |     await depositAmtInput.fill('10000');
  123 |     await page.waitForTimeout(300);
  124 | 
  125 |     // Click the Onayla button inside the modal
  126 |     const confirmBtnDeposit = modal.getByRole('button', { name: 'Onayla', exact: true });
  127 |     await expect(confirmBtnDeposit).toBeEnabled({ timeout: 5000 });
  128 |     await confirmBtnDeposit.click();
  129 | 
  130 |     // Modal closes on success
  131 |     await waitForModalClose(page);
  132 | 
  133 |     // Cash balance should now show ≈10,000
  134 |     await expect(page.locator('text="Nakit"').first()).toBeVisible();
  135 |     // Verify deposit appears in transaction history
  136 |     await expect(page.locator('text="YATIRMA"').first()).toBeAttached({ timeout: 10000 });
  137 | 
  138 |     // ── C. BUY by QUANTITY — AEFES, 1 share ────────────────────────────────
  139 |     await openTradeModal(page);
  140 |     await selectAction(page, 'Al');
  141 |     modal = page.locator('.fixed.inset-0.z-50');
  142 | 
  143 |     // Search for AEFES
  144 |     const symbolInput = modal.locator('input[aria-label="Hisse Arama"]');
  145 |     await symbolInput.fill('AEFES');
```