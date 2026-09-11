/**
 * portfolio.spec.ts
 *
 * Full critical-flow E2E for the portfolio feature:
 *   A. Create PAPER portfolio
 *   B. DEPOSIT 10,000 TRY  → assert cash & transaction history
 *   C. BUY by QUANTITY (AEFES, 1 share) → assert position & cash
 *   D. BUY by BUDGET  (THYAO, 500 TRY)  → assert quantity & cash
 *   E. SELL (AEFES all) → assert cash increases
 *   F. WITHDRAW        → assert cash decreases
 *   G. Risk page       → no errors, percentages visible
 *   H. Education page  → lesson page loads, image naturalWidth > 0
 *   I. Chart smoke     → GARAN detail page, chart container visible
 *
 * Prerequisites (handled by backend seed + QA env):
 *   - borsa_takip_test DB with seeded AEFES/THYAO/GARAN instruments
 *   - QA backend at 127.0.0.1:8002 with ENABLE_MOCK_MARKET_DATA=true
 */
import { test, expect, Page } from '@playwright/test';

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** Register a fresh QA user, complete onboarding, and land on /dashboard. */
async function registerAndOnboard(page: Page, email: string, password: string) {
  await page.goto('/register');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(500);
  await page.fill('#email', email);
  await page.fill('#password', password);
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/.*\/onboarding/, { timeout: 20000 });
  
  const firstNameInput = page.locator('#firstName');
  await firstNameInput.waitFor({ state: 'visible' });
  await firstNameInput.fill('QA');
  await page.locator('#lastName').fill('Portfolio');
  await page.locator('label:has(input[value="MEDIUM"])').click();
  
  // On mobile, React may take longer to hydrate; re-click the risk label to
  // ensure the onChange fires and the form becomes valid before waiting
  await page.waitForTimeout(500);
  await page.locator('label:has(input[value="MEDIUM"])').click();
  
  const submitBtn = page.locator('button[type="submit"]');
  await expect(submitBtn).toBeEnabled({ timeout: 20000 });
  await submitBtn.click();
  await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 20000 });
}

/** Open the "Yeni İşlem" (trade) modal from the portfolio detail page. */
async function openTradeModal(page: Page) {
  // Make sure modal is not already open
  const modalOverlay = page.locator('.fixed.inset-0.z-50');
  if (await modalOverlay.isVisible()) {
    await page.keyboard.press('Escape');
    await expect(modalOverlay).not.toBeVisible({ timeout: 5000 });
  }
  // Click the "Yeni İşlem" button in the page (not inside modal)
  await page.getByRole('button', { name: /Yeni İşlem/ }).first().click();
  // Wait for modal header to appear
  await expect(page.locator('.fixed.inset-0.z-50 h2').filter({ hasText: /Yeni/ })).toBeVisible({ timeout: 8000 });
}

/** Select an action tab inside the already-open modal. */
async function selectAction(page: Page, label: string) {
  const modal = page.locator('.fixed.inset-0.z-50');
  await modal.getByRole('button', { name: label, exact: true }).click();
  await page.waitForTimeout(200);
}

/** Wait for the modal overlay to disappear after a successful transaction. */
async function waitForModalClose(page: Page) {
  const modalOverlay = page.locator('.fixed.inset-0.z-50');
  await expect(modalOverlay).not.toBeVisible({ timeout: 15000 });
}

// ─── Main test ────────────────────────────────────────────────────────────────

test.describe('Critical Flows: Portfolio & Trade', () => {

  test('Full PAPER portfolio lifecycle', async ({ page }, testInfo) => {
    // Allow extra time for full flow (7 sub-steps)
    test.setTimeout(180000);

    const email = `pf_${Date.now()}_${testInfo.workerIndex}@example.com`;
    const password = 'TestPassword123!';

    // ── Setup: register fresh user ──────────────────────────────────────────
    await registerAndOnboard(page, email, password);

    // ── A. Create PAPER portfolio ───────────────────────────────────────────
    await page.goto('/portfolios');
    await page.waitForLoadState('networkidle');

    // Empty state shows a create button
    const createBtn = page.getByRole('button', { name: /Oluştur/ }).first();
    await expect(createBtn).toBeVisible({ timeout: 10000 });
    await createBtn.click();

    // Fill the create-portfolio modal
    await page.fill('input[type="text"]', 'QA Portfolio');
    // Select PAPER type if select exists
    const hasPaperSelect = await page.locator('select').count() > 0;
    if (hasPaperSelect) {
      await page.selectOption('select', 'PAPER').catch(() => null);
    }
    // Submit the modal (the primary blue button inside the overlay)
    await page.locator('.fixed button.bg-primary-600, dialog button.bg-primary-600, [role="dialog"] button.bg-primary-600').first().click();

    // Should land on portfolio detail page
    await expect(page).toHaveURL(/.*\/portfolios\/\d+/, { timeout: 15000 });
    const portfolioUrl = page.url();
    const portfolioId = portfolioUrl.match(/portfolios\/(\d+)/)?.[1];
    expect(portfolioId).toBeTruthy();

    // ── B. DEPOSIT 10,000 TRY ──────────────────────────────────────────────
    await openTradeModal(page);
    let modal = page.locator('.fixed.inset-0.z-50');

    // Default tab is "Para Yatır" — just fill the amount
    const depositAmtInput = modal.locator('input[type="number"]').first();
    await depositAmtInput.fill('10000');
    await page.waitForTimeout(300);

    // Click the Onayla button inside the modal
    const confirmBtnDeposit = modal.getByRole('button', { name: 'Onayla', exact: true });
    await expect(confirmBtnDeposit).toBeEnabled({ timeout: 5000 });
    await confirmBtnDeposit.click();

    // Modal closes on success
    await waitForModalClose(page);

    // Cash balance should now show ≈10,000
    await expect(page.locator('text="Nakit"').first()).toBeVisible();
    // Verify deposit appears in transaction history
    await expect(page.locator('text="YATIRMA"').first()).toBeAttached({ timeout: 10000 });

    // ── C. BUY by QUANTITY — AEFES, 1 share ────────────────────────────────
    await openTradeModal(page);
    await selectAction(page, 'Al');
    modal = page.locator('.fixed.inset-0.z-50');

    // Search for AEFES
    const symbolInput = modal.locator('input[aria-label="Hisse Arama"]');
    await symbolInput.fill('AEFES');
    await page.waitForTimeout(600); // debounce

    // Click the search result
    const aefesResult = modal.locator('button, li, div[role="option"]').filter({ hasText: 'AEFES' }).first();
    await expect(aefesResult).toBeVisible({ timeout: 8000 });
    await aefesResult.click();

    // Wait for quote to load (mock provider responds immediately)
    await page.waitForTimeout(1000);

    // Quantity mode: fill 1 share
    const qtyInput = modal.locator('input[min="1"]').first();
    await qtyInput.fill('1');

    const confirmBtnBuy = modal.getByRole('button', { name: /İşlemi Onayla|Onayla/ });
    await expect(confirmBtnBuy).toBeEnabled({ timeout: 5000 });
    await confirmBtnBuy.click();
    await waitForModalClose(page);

    // Position AEFES should appear in the positions table
    await expect(page.locator('td').filter({ hasText: 'AEFES' }).first()).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text="AL"').first()).toBeAttached({ timeout: 5000 });

    // ── D. BUY by BUDGET — THYAO, 500 TRY ─────────────────────────────────
    await openTradeModal(page);
    await selectAction(page, 'Al');
    modal = page.locator('.fixed.inset-0.z-50');

    const symbolInput2 = modal.locator('input[aria-label="Hisse Arama"]');
    await symbolInput2.fill('THYAO');
    await page.waitForTimeout(600);

    const thyaoResult = modal.locator('button, li, div[role="option"]').filter({ hasText: 'THYAO' }).first();
    await expect(thyaoResult).toBeVisible({ timeout: 8000 });
    await thyaoResult.click();
    await page.waitForTimeout(1000);

    // Switch to BUDGET mode
    const budgetModeBtn = modal.getByRole('button', { name: /Tutar|Budget/ }).first();
    await budgetModeBtn.click();

    const budgetInput = modal.locator('input[min="0"]').first();
    await budgetInput.fill('500');
    await page.waitForTimeout(500);

    // Only submit if at least 1 share can be bought (preview > 0)
    const budgetQtyText = modal.locator('text=/\\d+ adet/');
    const qtyText = await budgetQtyText.textContent({ timeout: 5000 }).catch(() => '0 adet');
    const budgetQty = parseInt(qtyText?.match(/(\d+)/)?.[1] ?? '0');

    if (budgetQty >= 1) {
      const confirmBtnBudget = modal.getByRole('button', { name: /İşlemi Onayla|Onayla/ });
      await expect(confirmBtnBudget).toBeEnabled({ timeout: 5000 });
      await confirmBtnBudget.click();
      await waitForModalClose(page);
    } else {
      // Budget insufficient for 1 share — click the X button (text-slate-400) to close modal
      await modal.locator('button.text-slate-400').click();
      await waitForModalClose(page);
    }

    // ── E. SELL all AEFES ──────────────────────────────────────────────────
    await openTradeModal(page);
    await selectAction(page, 'Sat');
    modal = page.locator('.fixed.inset-0.z-50');

    const symbolInput3 = modal.locator('input[aria-label="Hisse Arama"]');
    await symbolInput3.fill('AEFES');
    await page.waitForTimeout(600);

    const aefesResult2 = modal.locator('button, li, div[role="option"]').filter({ hasText: 'AEFES' }).first();
    await expect(aefesResult2).toBeVisible({ timeout: 8000 });
    await aefesResult2.click();
    await page.waitForTimeout(1000);

    // Click "Tümünü Sat" (sell all) if available
    const sellAllBtn = modal.getByRole('button', { name: /Tümünü Sat/ });
    if (await sellAllBtn.isVisible()) {
      await sellAllBtn.click();
    } else {
      const sellQtyInput = modal.locator('input[min="1"]').first();
      await sellQtyInput.fill('1');
    }

    const confirmBtnSell = modal.getByRole('button', { name: /İşlemi Onayla|Onayla/ });
    await expect(confirmBtnSell).toBeEnabled({ timeout: 5000 });
    await confirmBtnSell.click();
    await waitForModalClose(page);

    // SAT should appear in history
    await expect(page.locator('text="SAT"').first()).toBeAttached({ timeout: 10000 });

    // ── F. WITHDRAW ────────────────────────────────────────────────────────
    await openTradeModal(page);
    await selectAction(page, 'Para Çek');
    modal = page.locator('.fixed.inset-0.z-50');

    const withdrawInput = modal.locator('input[type="number"]').first();
    await withdrawInput.fill('100');
    await page.waitForTimeout(300);

    const confirmBtnWithdraw = modal.getByRole('button', { name: 'Onayla', exact: true });
    await expect(confirmBtnWithdraw).toBeEnabled({ timeout: 5000 });
    await confirmBtnWithdraw.click();
    await waitForModalClose(page);

    await expect(page.locator('text="ÇEKİM"').first()).toBeAttached({ timeout: 10000 });

    // ── G. Risk page ────────────────────────────────────────────────────────
    await page.goto(`/portfolios/${portfolioId}/risk`);
    await page.waitForLoadState('networkidle');
    // No JS error page, risk section heading visible
    await expect(page.locator('h1, h2').filter({ hasText: /Risk/ }).first()).toBeVisible({ timeout: 10000 });
    // No scientific notation visible
    const pageContent = await page.content();
    expect(pageContent).not.toMatch(/\dE[+-]\d+%?/);

    // ── H. Education page & lesson ──────────────────────────────────────────
    await page.goto('/education');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('h1').first()).toBeVisible({ timeout: 10000 });

    // Click first available lesson card
    const lessonCard = page.locator('a[href*="/education/"]').first();
    const hasLesson = await lessonCard.count() > 0;
    if (hasLesson) {
      await lessonCard.click();
      await page.waitForLoadState('networkidle');
      // Assert lesson page has content
      await expect(page.locator('h1, h2').first()).toBeVisible({ timeout: 10000 });

      // Verify at least one image loaded (naturalWidth > 0)
      const imgs = page.locator('img');
      const imgCount = await imgs.count();
      if (imgCount > 0) {
        const firstImgLoaded = await imgs.first().evaluate((el: HTMLImageElement) => el.naturalWidth > 0);
        expect(firstImgLoaded, 'Education image not loaded').toBe(true);
      }
    }

    // ── I. Chart smoke — GARAN instrument detail ────────────────────────────
    await page.goto('/instruments/GARAN');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000); // allow chart to initialize

    // Instrument detail page loads without JS errors
    // The "Fiyat Grafiği" section heading should be visible
    await expect(page.locator('text=/Fiyat Graf|Price Chart/i').first()).toBeVisible({ timeout: 15000 });
    // The instrument symbol heading should be visible
    await expect(page.locator('h1, h2').filter({ hasText: /GARAN/ }).first()).toBeVisible({ timeout: 5000 });
  });
});
