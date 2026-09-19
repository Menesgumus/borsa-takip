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
    
    const fname = await page.inputValue('#firstName');
    if (!fname) {
        await page.fill('#firstName', 'QA');
        await page.fill('#lastName', 'Opportunity');
    }

    await submitBtn.click();
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 20000 });
  }

  test('Decision Monotonicity: Personal Action <= Market Action', async () => {
    test.setTimeout(180000);
    const ts = Date.now();
    const randomSuffix = Math.random().toString(36).substring(7);
    const email = `oppqa_mono_${ts}_${randomSuffix}@example.com`;
    
    await registerAndOnboard(page, email, 'TestPassword123!');

    // Create empty portfolio
    await page.goto('/portfolios');
    const createInitialBtn = page.getByRole('button', { name: /Olu.tur/i }).first();
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

    // Select General Market
    const portfolioSelect = page.locator('select');
    await portfolioSelect.selectOption('');
    await page.waitForTimeout(2000);

    // Get the first symbol and its market action
    const firstCard = page.locator('a[href^="/opportunities/"]').first();
    await expect(firstCard).toBeVisible({ timeout: 60000 });
    
    const symbolText = await firstCard.locator('h3').textContent();
    const symbol = symbolText?.trim() || '';
    expect(symbol).not.toBe('');

    const marketActionText = await firstCard.locator('span.px-2.py-1.text-xs.font-bold').first().textContent();
    const marketAction = marketActionText?.trim() || 'BEKLE';

    // Switch to Empty Portfolio
    await portfolioSelect.selectOption('Empty Portfolio');
    await page.waitForTimeout(2000);
    
    // Find the exact same card in the portfolio view
    const portCard = page.locator(`a[href^="/opportunities/"]:has(h3:has-text("${symbol}"))`).first();
    // It might not be visible if filtered out, but if it is, we check it
    if (await portCard.isVisible()) {
      const personalActionText = await portCard.locator('span.px-2.py-1.text-xs.font-bold').first().textContent();
      const personalAction = personalActionText?.trim() || 'BEKLE';

      const rankMap: Record<string, number> = {
        'GÜÇLÜ SAT': 1,
        'SAT': 2,
        'BEKLE': 3,
        'AL': 4,
        'GÜÇLÜ AL': 5
      };

      const mRank = rankMap[marketAction] || 3;
      const pRank = rankMap[personalAction] || 3;

      expect(pRank).toBeLessThanOrEqual(mRank);
    }


  });

  test('Executable Position Sizing & Future Workspace', async () => {
    test.setTimeout(180000);
    const ts = Date.now();
    const randomSuffix = Math.random().toString(36).substring(7);
    const email = `oppqa_size_${ts}_${randomSuffix}@example.com`;
    
    // We can reuse the page session if we logout, or just use a new context. But since mode: serial, let's just clear cookies or use a new page.
    // To be safe, just logout and register again, OR use a fresh context!
    // Actually, mode: serial means we can just logout.
    await page.context().clearCookies();
    await page.goto('/login');
    await expect(page).toHaveURL(/.*\/login/, { timeout: 10000 });

    await registerAndOnboard(page, email, 'TestPassword123!');

    // Create a funded portfolio
    await page.goto('/portfolios');
    await page.getByRole('button', { name: /Yeni Portf.y/i }).first().click();
    await page.fill('input[name="name"]', 'Funded Portfolio');
    const responsePromise = page.waitForResponse(response => response.url().includes('/api/v1/portfolios') && response.request().method() === 'POST');
    await page.getByRole('button', { name: 'Kaydet' }).click();
    
    const response = await responsePromise;
    const data = await response.json();
    const portfolioId = data.id;
    
    await expect(page.locator('h1').filter({ hasText: 'Portföylerim' })).toBeVisible();
    expect(portfolioId).not.toBe('');
    
    // Deposit cash
    await page.goto(`/portfolios/${portfolioId}`);
    
    // Deposit cash
    await page.getByRole('button').filter({ hasText: /Yeni .şlem/i }).first().click();
    await page.waitForTimeout(1000);
    await page.fill('input[type="number"]', '1000000');
    const modal = page.locator('.fixed.inset-0.z-50');
    await modal.locator('button.bg-primary-600').filter({ hasText: 'Onayla' }).click();
    
    await expect(page.locator('.fixed.inset-0.z-50')).not.toBeVisible({ timeout: 15000 });

    // Go to opportunities
    await page.goto('/opportunities');
    const portfolioSelect = page.locator('select');
    await portfolioSelect.selectOption(portfolioId);
    await page.waitForTimeout(2000);

    // Click the first card
    const firstCard = page.locator('a[href^="/opportunities/"]').first();
    await expect(firstCard).toBeVisible({ timeout: 60000 });
    const cardHref = await firstCard.getAttribute('href');
    const symbol = cardHref?.split('/').pop() || '';
    
    await firstCard.click();
    
    // We can just query the API directly using page.request to get the JSON payload safely
    const detailResponse = await page.request.get(`/api/v1/opportunities/${symbol}?portfolio_id=${portfolioId}`);
    const detail = await detailResponse.json();

    // Check sizes
    if (detail.recommended_quantity && detail.recommended_quantity > 0) {
      expect(Number.isInteger(detail.recommended_quantity)).toBeTruthy();
      
      const price = parseFloat(detail.quote_price);
      const budget = parseFloat(detail.max_executable_budget);
      const qty = parseFloat(detail.max_executable_quantity);
      
      // max_executable_budget == max_executable_quantity * current_price
      expect(Math.abs(budget - (qty * price))).toBeLessThan(0.01);
      
      const theoretical = parseFloat(detail.theoretical_max_additional_budget);
      expect(budget).toBeLessThanOrEqual(theoretical + 0.01); // +0.01 for floating point margin
    }

    // Check future workspace marker
    const futureWorkspaceMarker = page.locator('text=/Gelecek/');
    await expect(futureWorkspaceMarker).toBeVisible({ timeout: 15000 });
  });
});
