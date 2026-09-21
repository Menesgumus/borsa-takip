import { test, expect, Page } from '@playwright/test';

async function registerAndOnboard(page: Page, email: string, password: string) {
  await page.goto('/register');
  await page.fill('#email', email);
  await page.fill('#password', password);
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/.*\/onboarding/, { timeout: 20000 });
  
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

async function createPortfolioViaUi(page: Page, portfolioName: string) {
  await page.goto('/portfolios');
  
  const yeniIslemBtn = page.getByRole('button', { name: /Yeni İşlem/i }).first();
  if (await yeniIslemBtn.isVisible()) {
    await yeniIslemBtn.click();
  }
  
  const createPortfolioButton = page.getByRole('button', {
    name: 'İlk Portföyü Oluştur',
  });
  if (await createPortfolioButton.isVisible()) {
    await createPortfolioButton.click();
  } else {
    await page.getByRole('button', { name: 'Yeni Ekle' }).click().catch(() => null);
  }

  const createModal = page.locator('.fixed.inset-0.z-50');
  await expect(
    createModal.getByRole('heading', { name: 'Yeni Portföy Ekle' })
  ).toBeVisible({ timeout: 10000 });

  await createModal.locator('input[type="text"]').fill(portfolioName);

  const responsePromise = page.waitForResponse(
    response =>
      response.url().includes('/api/v1/portfolios') &&
      response.request().method() === 'POST'
  );

  await createModal.getByRole('button', { name: 'Oluştur' }).click();

  const response = await responsePromise;
  expect(response.ok()).toBeTruthy();

  const data = await response.json();
  const portfolioId = data.id;
  expect(portfolioId).toBeTruthy();

  await expect(page).toHaveURL(
    new RegExp(`/portfolios/${portfolioId}(?:\\?.*)?$`),
    { timeout: 20000 }
  );

  await expect(
    page.getByRole('heading', { name: portfolioName })
  ).toBeVisible({ timeout: 20000 });

  return portfolioId;
}

async function depositCashViaUi(page: Page, portfolioId: string | number, amount: string) {
  await page.goto(`/portfolios/${portfolioId}`);
  await page.getByRole('button').filter({ hasText: /Yeni İşlem/i }).first().click();
  
  const modal = page.locator('.fixed.inset-0.z-50');
  await expect(modal.getByRole('heading', { name: /Yeni İşlem/ })).toBeVisible({ timeout: 10000 });
  await modal.locator('input[type="number"]').fill(amount);
  const confirmBtnDeposit = modal.getByRole('button', { name: 'Onayla', exact: true });
  await expect(confirmBtnDeposit).toBeEnabled({ timeout: 5000 });
  await confirmBtnDeposit.click();
  await expect(modal).not.toBeVisible({ timeout: 15000 });
}

test.describe('Phase 26.1 Opportunities E2E', () => {

  test('Decision Monotonicity: Personal Action <= Market Action', async ({ page }) => {
    test.setTimeout(180000);
    const ts = Date.now();
    const randomSuffix = Math.random().toString(36).substring(7);
    const email = `oppqa_mono_${ts}_${randomSuffix}@example.com`;
    
    await registerAndOnboard(page, email, 'TestPassword123!');
    await createPortfolioViaUi(page, 'Empty Portfolio');
    
    await page.goto('/opportunities');
    await page.waitForLoadState('networkidle');

    const portfolioSelect = page.locator('select');
    await portfolioSelect.selectOption('');

    const firstCard = page.locator('a[href^="/opportunities/"]').first();
    await expect(firstCard).toBeVisible({ timeout: 60000 });
    
    const symbolText = await firstCard.locator('h3').textContent();
    const symbol = symbolText?.trim() || '';
    expect(symbol).not.toBe('');

    const marketActionText = await firstCard.locator('span.px-2.py-1.text-xs.font-bold').first().textContent();
    const marketAction = marketActionText?.trim() || 'BEKLE';

    await portfolioSelect.selectOption('Empty Portfolio');
    
    const portCard = page.locator(`a[href^="/opportunities/"]:has(h3:has-text("${symbol}"))`).first();
    await expect(portCard, "Target instrument disappeared").toBeVisible({ timeout: 10000 });
    
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
  });

  test('Executable Position Sizing & Future Workspace', async ({ page }) => {
    test.setTimeout(180000);
    const ts = Date.now();
    const randomSuffix = Math.random().toString(36).substring(7);
    const email = `oppqa_size_${ts}_${randomSuffix}@example.com`;
    
    await registerAndOnboard(page, email, 'TestPassword123!');
    const portfolioId = await createPortfolioViaUi(page, 'Funded Portfolio');
    await depositCashViaUi(page, portfolioId, '1000000');

    // Navigate to the base opportunities page
    await page.goto(`/opportunities`);

    const portfolioSelect = page.locator('select').first();
    
    // Set up the response promise BEFORE selecting the option
    const responsePromise = page.waitForResponse(response => {
        const url = new URL(response.url());
        return (
            url.pathname.includes('/api/v1/opportunities') &&
            !url.pathname.includes('/portfolios') &&
            url.searchParams.get('portfolio_id') === String(portfolioId) &&
            url.searchParams.get('asset_class') === 'BIST_EQUITY' &&
            response.request().method() === 'GET' &&
            (response.request().resourceType() === 'fetch' || response.request().resourceType() === 'xhr')
        );
    }, { timeout: 15000 });

    // Select the portfolio using the UI dropdown
    await portfolioSelect.selectOption(String(portfolioId));
    
    const opportunitiesResponse = await responsePromise;
    expect(opportunitiesResponse.ok(), `Portfolio opportunities request failed: ${opportunitiesResponse.status()}`).toBeTruthy();

    const opportunities = await opportunitiesResponse.json();
    
    const qaBuy = opportunities.find((opp: any) => opp.symbol === 'QABUY');
    expect(qaBuy).toBeDefined();
    expect(qaBuy.sizing_state).toBe('OK');
    expect(qaBuy.recommended_quantity).toBeGreaterThan(0);

    const targetSymbol = 'QABUY';
    const qaCard = page.locator('a[href^="/opportunities/"]').filter({ has: page.getByRole('heading', { name: 'QABUY' }) }).first();
    
    const detailResponsePromise = page.waitForResponse(response => {
        const url = new URL(response.url());
        return (
            url.pathname.includes(`/api/v1/opportunities/${targetSymbol}`) &&
            url.searchParams.get('portfolio_id') === String(portfolioId) &&
            response.request().method() === 'GET' &&
            (response.request().resourceType() === 'fetch' || response.request().resourceType() === 'xhr')
        );
    }, { timeout: 15000 });

    await page.goto(`/opportunities/${targetSymbol}?portfolio_id=${portfolioId}`);
    
    const detailResponse = await detailResponsePromise;
    expect(detailResponse.ok(), `Detail response failed: ${detailResponse.status()}`).toBeTruthy();
    const detail = await detailResponse.json();

    expect(detail.symbol).toBe('QABUY');
    expect(detail.selected_portfolio_id).toBe(Number(portfolioId));
    expect(detail.sizing_state).toBe('OK');
    expect(detail.recommended_quantity).toBeGreaterThan(0);
    expect(Number.isInteger(detail.recommended_quantity)).toBeTruthy();
    expect(detail.max_executable_quantity).toBeGreaterThan(0);
    expect(Number.isInteger(detail.max_executable_quantity)).toBeTruthy();
    
    const price = parseFloat(detail.quote_price);
    expect(price).toBeGreaterThan(0);

    const budget = parseFloat(detail.max_executable_budget);
    const qty = parseFloat(detail.max_executable_quantity);
    
    expect(Math.abs(budget - (qty * price))).toBeLessThan(0.01);
    const theoretical = parseFloat(detail.theoretical_max_additional_budget);
    expect(budget).toBeLessThanOrEqual(theoretical + 0.01); 

    const futureWorkspaceMarker = page.locator('text=/Gelecek/');
    await expect(futureWorkspaceMarker).toBeVisible({ timeout: 15000 });
  });
});
