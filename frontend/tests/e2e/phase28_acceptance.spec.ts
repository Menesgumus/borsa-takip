import { test, expect, Page } from '@playwright/test';

// ============================================================================
// SHARED HELPER FUNCTIONS
// ============================================================================

async function registerAndOnboard(page: Page) {
  const ts = Date.now();
  const email = `qa.p28.${ts}@example.com`;
  
  await page.goto('/register');
  await page.fill('#email', email);
  await page.fill('#password', 'qa_password123!');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/.*\/onboarding/, { timeout: 20000 });
  
  await page.fill('#firstName', 'QA');
  await page.fill('#lastName', 'Phase28');
  
  const submitBtn = page.locator('button[type="submit"]');
  await expect(async () => {
    await page.getByText('YÜKSEK', { exact: true }).click();
    await expect(submitBtn).toBeEnabled({ timeout: 2000 });
  }).toPass({ timeout: 20000 });
  
  await submitBtn.click();
  await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 20000 });
  
  return email;
}

async function createPortfolio(page: Page, type: 'REAL' | 'PAPER' = 'REAL') {
  await page.goto('/portfolios');
  const createPortfolioButton = page.getByRole('button', { name: 'İlk Portföyü Oluştur' });
  if (await createPortfolioButton.isVisible()) {
    await createPortfolioButton.click();
  } else {
    await page.getByRole('button', { name: 'Yeni Ekle' }).click();
  }
  
  const createModal = page.locator('.fixed.inset-0.z-50');
  await expect(createModal.getByRole('heading', { name: 'Yeni Portföy Ekle' })).toBeVisible({ timeout: 10000 });
  
  const ts = Date.now();
  await createModal.getByRole('textbox').fill(`P28 ${type} ${ts}`);
  await createModal.getByRole('combobox').selectOption(type);
  
  const [response] = await Promise.all([
    page.waitForResponse(res => res.url().includes('/api/v1/portfolios') && res.request().method() === 'POST'),
    createModal.getByRole('button', { name: 'Oluştur' }).click(),
  ]);
  const portfolioData = await response.json();
  return portfolioData.id;
}

async function fundPortfolio(page: Page, portfolioId: number, amount: string) {
  await page.goto(`/portfolios/${portfolioId}`);
  await page.waitForURL(`**/portfolios/${portfolioId}`);
  
  await page.getByRole('button').filter({ hasText: /Yeni İşlem/i }).first().click();
  
  const actionModal = page.locator('.fixed.inset-0.z-50');
  await expect(actionModal.getByRole('heading', { name: /Yeni İşlem/ })).toBeVisible({ timeout: 10000 });
  
  await actionModal.locator('input[type="number"]').fill(amount);
  const confirmBtnDeposit = actionModal.getByRole('button', { name: 'Onayla', exact: true });
  await expect(confirmBtnDeposit).toBeEnabled({ timeout: 5000 });
  
  const [depositResponse] = await Promise.all([
    page.waitForResponse(res => res.url().includes('/transactions') && res.request().method() === 'POST'),
    confirmBtnDeposit.click(),
  ]);
  
  try {
    const closeBtn = page.getByRole('button', { name: 'Kapat' });
    await expect(closeBtn).toBeVisible({ timeout: 5000 });
    await closeBtn.click();
  } catch(e) {}
  await expect(actionModal).not.toBeVisible({ timeout: 15000 });
  return depositResponse.json();
}

// ============================================================================
// PHASE 28 ACCEPTANCE TESTS
// ============================================================================

test.describe('Phase 28 Multi-Asset Allocation & Basket Builder', () => {

  test('Flow A - Multi-Asset Portfolio / Filters', async ({ page }) => {
    await registerAndOnboard(page);
    const portfolioId = await createPortfolio(page);

    await page.goto('/opportunities');
    await page.waitForURL('**/opportunities');
    // BIST Tab is active by default. Selecting the portfolio triggers the BIST fetch.
    const bistPromise = page.waitForResponse(res => {
        try {
            const url = new URL(res.url());
            return url.pathname === '/api/v1/opportunities' &&
                   url.searchParams.get('portfolio_id') === String(portfolioId) &&
                   url.searchParams.get('asset_class') === 'BIST_EQUITY' &&
                   res.request().method() === 'GET' &&
                   ['fetch', 'xhr'].includes(res.request().resourceType());
        } catch { return false; }
    });
    
    await page.locator('select').first().selectOption({ value: String(portfolioId) });
    
    const bistRes = await bistPromise;
    expect(bistRes.ok()).toBeTruthy();
    const bistData = await bistRes.json();
    expect(Array.isArray(bistData)).toBe(true);
    expect(bistData.length).toBeGreaterThan(0);
    for (const item of bistData) {
      expect(item.asset_class).toBe('BIST_EQUITY');
    }
    // Require specific QA fixture
    expect(bistData.some((item: any) => item.symbol === 'QABUY' || item.symbol === 'QAHOLD')).toBe(true);

    // US Tab
    const usTab = page.locator('button', { hasText: 'US Equities' });
    const usPromise = page.waitForResponse(res => {
        try {
            const url = new URL(res.url());
            return url.pathname === '/api/v1/opportunities' &&
                   url.searchParams.get('portfolio_id') === String(portfolioId) &&
                   url.searchParams.get('asset_class') === 'US_EQUITY' &&
                   res.request().method() === 'GET' &&
                   ['fetch', 'xhr'].includes(res.request().resourceType());
        } catch { return false; }
    });
    await usTab.click();
    const usRes = await usPromise;
    expect(usRes.ok()).toBeTruthy();
    const usData = await usRes.json();
    expect(Array.isArray(usData)).toBe(true);
    expect(usData.length).toBeGreaterThan(0);
    for (const item of usData) {
      expect(item.asset_class).toBe('US_EQUITY');
    }
    expect(usData.some((item: any) => item.symbol === 'QAUS')).toBe(true);

    // Gold Tab
    const gldTab = page.locator('button').filter({ hasText: /Alt.n/i });
    const gldPromise = page.waitForResponse(res => {
        try {
            const url = new URL(res.url());
            return url.pathname === '/api/v1/opportunities' &&
                   url.searchParams.get('portfolio_id') === String(portfolioId) &&
                   url.searchParams.get('asset_class') === 'GOLD' &&
                   res.request().method() === 'GET' &&
                   ['fetch', 'xhr'].includes(res.request().resourceType());
        } catch { return false; }
    });
    await gldTab.click();
    const gldRes = await gldPromise;
    expect(gldRes.ok()).toBeTruthy();
    const gldData = await gldRes.json();
    expect(Array.isArray(gldData)).toBe(true);
    expect(gldData.length).toBeGreaterThan(0);
    for (const item of gldData) {
      expect(item.asset_class).toBe('GOLD');
    }
    expect(gldData.some((item: any) => item.symbol === 'QAGOLD')).toBe(true);

    // Tümü Tab (All)
    const allTab = page.locator('button').filter({ hasText: /T.m./i });
    const allPromise = page.waitForResponse(res => {
        try {
            const url = new URL(res.url());
            return url.pathname === '/api/v1/opportunities' &&
                   url.searchParams.get('portfolio_id') === String(portfolioId) &&
                   !url.searchParams.has('asset_class') &&
                   res.request().method() === 'GET' &&
                   ['fetch', 'xhr'].includes(res.request().resourceType());
        } catch { return false; }
    });
    await allTab.click();
    const allRes = await allPromise;
    expect(allRes.ok()).toBeTruthy();
    const allData = await allRes.json();
    expect(Array.isArray(allData)).toBe(true);
    expect(allData.length).toBeGreaterThan(0);
    for (const item of allData) {
      expect(item.asset_class).not.toBe('FX_REFERENCE');
    }
    expect(allData.some((item: any) => item.symbol === 'QAUSDTRY')).toBe(false);
  });

  test('Flow B - Basket Conservation', async ({ page }) => {
    await registerAndOnboard(page);
    const portfolioId = await createPortfolio(page);
    await fundPortfolio(page, portfolioId, '100000');

    await page.goto('/opportunities');
    await page.locator('select').first().selectOption({ value: String(portfolioId) });

    const sepetLink = page.locator('text=Sepet Oluştur');
    if (await sepetLink.isVisible()) {
      const previewPromise = page.waitForResponse(res => res.url().includes(`/api/v1/portfolios/${portfolioId}/basket-preview`) && res.request().method() === 'POST');
      await sepetLink.click();
      await previewPromise;
    }
    
    // Set exact deploy amount
    await page.fill('input[type="number"][placeholder="Örn: 10000"]', '50000');
    const recalculatePromise = page.waitForResponse(res => res.url().includes(`/api/v1/portfolios/${portfolioId}/basket-preview`) && res.request().method() === 'POST');
    await page.locator('button', { hasText: 'Sepeti Hesapla' }).click();
    const recalculateRes = await recalculatePromise;
    expect(recalculateRes.ok()).toBeTruthy();
    
    const previewData = await recalculateRes.json();
    expect(Number(previewData.requested_deploy_amount)).toBe(50000);
    expect(Number(previewData.allocated_amount)).toBeGreaterThanOrEqual(0);
    expect(Number(previewData.unallocated_amount)).toBeGreaterThanOrEqual(0);
    expect(Number(previewData.allocated_amount)).toBeLessThanOrEqual(Number(previewData.requested_deploy_amount));
    
    const diff = Math.abs(Number(previewData.allocated_amount) + Number(previewData.unallocated_amount) - Number(previewData.requested_deploy_amount));
    expect(diff).toBeLessThan(0.01);
    
    for (const item of previewData.items) {
      expect(Number.isInteger(Number(item.proposed_quantity))).toBe(true);
      expect(Number(item.proposed_quantity)).toBeGreaterThanOrEqual(0);
    }
    
    // Check side-effects
    const txRes = await page.evaluate(async ({ portfolioId }) => {
      return await fetch(`/api/v1/portfolios/${portfolioId}/transactions`).then(r => r.json());
    }, { portfolioId });
    expect(txRes.length).toBe(1); // Only the initial deposit
  });

  test('Flow B2 - Zero / Blank Deploy Semantics', async ({ page }) => {
    await registerAndOnboard(page);
    const portfolioId = await createPortfolio(page);
    await fundPortfolio(page, portfolioId, '100000');

    // Fetch initial portfolio details
    const pData = await page.evaluate(async ({ portfolioId }) => {
      return await fetch(`/api/v1/portfolios/${portfolioId}`).then(r => r.json());
    }, { portfolioId });
    const initialTotalValue = pData.total_value;

    await page.goto('/opportunities');
    await page.locator('select').first().selectOption({ value: String(portfolioId) });

    const sepetLink = page.locator('text=Sepet Oluştur');
    const previewPromise = page.waitForResponse(res => res.url().includes(`/api/v1/portfolios/${portfolioId}/basket-preview`) && res.request().method() === 'POST');
    await sepetLink.click();
    const previewRes = await previewPromise;
    expect(previewRes.ok()).toBeTruthy();
    
    const previewData = await previewRes.json();
    expect(Number(previewData.requested_deploy_amount)).toBe(100000); // 0 or blank defaults to available cash buffer
    
    // Verify total value didn't change (no virtual deposit)
    const pDataAfter = await page.evaluate(async ({ portfolioId }) => {
      return await fetch(`/api/v1/portfolios/${portfolioId}`).then(r => r.json());
    }, { portfolioId });
    expect(Number(pDataAfter.total_value)).toBe(Number(initialTotalValue));
  });

  test('Flow C - No Forced Buy', async ({ page }) => {
    await registerAndOnboard(page);
    const portfolioId = await createPortfolio(page);
    await fundPortfolio(page, portfolioId, '100000');

    // First fetch the opportunities list to ensure QAHOLD is returned and is HOLD
    const cookieHeader = (await page.context().cookies()).map(c => c.name + '=' + c.value).join('; ');
    const oppRes = await page.request.get(`/api/v1/opportunities/QAHOLD?portfolio_id=${portfolioId}`, { headers: { Cookie: cookieHeader } });
    expect(oppRes.status()).toBe(200);
    const qaholdOpp = await oppRes.json();
    
    // Assert QAHOLD exists in deterministic opportunity data
    expect(qaholdOpp).toBeDefined();
    // Assert market_view == HOLD or personal_action == HOLD
    expect(qaholdOpp.market_view === 'HOLD' || qaholdOpp.personal_action === 'HOLD').toBeTruthy();

    await page.goto('/opportunities');
    await page.locator('select').first().selectOption({ value: String(portfolioId) });

    const sepetLink = page.locator('text=Sepet Oluştur');
    const previewPromise = page.waitForResponse(res => res.url().includes(`/api/v1/portfolios/${portfolioId}/basket-preview`) && res.request().method() === 'POST');
    await sepetLink.click();
    const previewRes = await previewPromise;
    
    const previewData = await previewRes.json();
    
    // Check that QAHOLD does NOT receive a positive basket allocation
    const holdItem = previewData.items?.find((i: any) => i.symbol === 'QAHOLD');
    expect(holdItem ? Number(holdItem.proposed_quantity) : 0).toBe(0);
    
    // Assert unallocated capital is preserved (>= 0)
    expect(Number(previewData.unallocated_amount)).toBeGreaterThanOrEqual(0);
  });

  test('Flow D - Manual Broker Price Invariance', async ({ page }) => {
    await registerAndOnboard(page);
    const portfolioId = await createPortfolio(page);
    await fundPortfolio(page, portfolioId, '100000');

    await page.goto('/opportunities');
    await page.locator('select').first().selectOption({ value: String(portfolioId) });
    
    // Switch to US Equities
    const usTab = page.locator('button', { hasText: 'US Equities' });
    const usPromise = page.waitForResponse(res => res.url().includes('asset_class=US_EQUITY') && res.request().method() === 'GET');
    await usTab.click();
    await usPromise;

    // QAUS will be in the basket builder, proceed to create basket
    const sepetLink = page.locator('text=Sepet Oluştur');
    const previewPromise = page.waitForResponse(res => res.url().includes(`/api/v1/portfolios/${portfolioId}/basket-preview`) && res.request().method() === 'POST');
    await sepetLink.click();
    const previewRes = await previewPromise;
    const previewData = await previewRes.json();
    
    const usItem = previewData.items.find((i: any) => i.symbol === 'QAUS');
    expect(usItem).toBeDefined();
    
    const originalAnalysisPrice = usItem.analysis_native_price;
    const itemRow = page.locator('tr').filter({ hasText: 'QAUS' }).first();
    
    // Preview A
    await itemRow.locator('input[type="number"]').fill(String(originalAnalysisPrice));
    
    const execPreviewPromiseA = page.waitForResponse(res => res.url().includes(`/api/v1/portfolios/${portfolioId}/execution-preview`) && res.request().method() === 'POST');
    await itemRow.locator('button').filter({ hasText: /nizle/i }).click();
    const execPreviewResA = await execPreviewPromiseA;
    const execDataA = await execPreviewResA.json();
    
    // Preview B
    const manualPriceB = (originalAnalysisPrice * 1.5).toFixed(2);
    await itemRow.locator('input[type="number"]').fill(manualPriceB);
    
    const execPreviewPromiseB = page.waitForResponse(res => res.url().includes(`/api/v1/portfolios/${portfolioId}/execution-preview`) && res.request().method() === 'POST');
    await itemRow.locator('button').filter({ hasText: /nizle/i }).click();
    const execPreviewResB = await execPreviewPromiseB;
    const execDataB = await execPreviewResB.json();
    
    // Assert invariant properties for both
    expect(execDataA.market_view).toBe(usItem.market_view);
    expect(execDataA.personal_action).toBe(usItem.personal_action);
    expect(Number(execDataA.market_score)).toBe(Number(usItem.market_score));
    expect(Number(execDataA.analysis_price)).toBe(Number(originalAnalysisPrice));
    expect(execDataA.execution_source).toBe('MANUAL_BROKER');

    expect(execDataB.market_view).toBe(usItem.market_view);
    expect(execDataB.personal_action).toBe(usItem.personal_action);
    expect(Number(execDataB.market_score)).toBe(Number(usItem.market_score));
    expect(Number(execDataB.analysis_price)).toBe(Number(originalAnalysisPrice));
    expect(execDataB.execution_source).toBe('MANUAL_BROKER');
    
    // Assert execution result changed
    const quantityChanged = Number(execDataA.recomputed_quantity) !== Number(execDataB.recomputed_quantity);
    const budgetChanged = Number(execDataA.recomputed_budget) !== Number(execDataB.recomputed_budget);
    const weightChanged = Number(execDataA.projected_weight) !== Number(execDataB.projected_weight);
    expect(quantityChanged || budgetChanged || weightChanged).toBeTruthy();
  });

  test('Flow E - Real External Trade Record', async ({ page }) => {
    await registerAndOnboard(page);
    const portfolioId = await createPortfolio(page, 'REAL');
    await fundPortfolio(page, portfolioId, '1000000'); // Note: Added 1M cash to prevent 400 Bad Request

    const cookies = await page.context().cookies();
    const cookieHeader = cookies.map(c => c.name + '=' + c.value).join('; ');
    
    const instRes = await page.request.get('/api/v1/instruments?search=QAUS', { headers: { Cookie: cookieHeader } });
    const instData = await instRes.json();
    const qausId = instData.items[0].id;
    
    const execTradeRes = await page.request.post(`/api/v1/portfolios/${portfolioId}/manual-trade`, {
      headers: { Cookie: cookieHeader },
      data: {
        instrument_id: qausId,
        side: 'BUY',
        quantity: 1,
        native_execution_price: 150.00,
        fee: 0
      }
    });
    
    const status = execTradeRes.status();
    const txData = await execTradeRes.json();
    if (status !== 200) console.log('Flow E 400 Error:', txData);

    expect(status).toBe(200);
    expect(txData.native_currency).toBe('USD');
    expect(Number(txData.native_price)).toBe(150.00);
    expect(Number(txData.fx_rate_to_base)).toBeGreaterThan(0);
    expect(txData.execution_source).toBe('MANUAL_BROKER');
    
    // Check history in UI
    await page.goto(`/portfolios/${portfolioId}?tab=islemler`);
    
    // Wait for the cell containing QAUS to be visible
    await expect(page.getByRole('cell', { name: 'QAUS' }).first()).toBeVisible({ timeout: 15000 });
  });

  test('Flow F - Paper Execution Regression', async ({ page }) => {
    await registerAndOnboard(page);
    const portfolioId = await createPortfolio(page, 'PAPER');
    await fundPortfolio(page, portfolioId, '1000000'); // Note: Added 1M cash to prevent 400 Bad Request

    const cookies = await page.context().cookies();
    const cookieHeader = cookies.map(c => c.name + '=' + c.value).join('; ');
    
    const instRes = await page.request.get('/api/v1/instruments?search=QABUY', { headers: { Cookie: cookieHeader } });
    const instData = await instRes.json();
    const qabuyId = instData.items[0].id;
    
    const oppRes = await page.request.get('/api/v1/opportunities', { headers: { Cookie: cookieHeader } });
    const oppData = await oppRes.json();
    const qabuyOpp = oppData.find((i: any) => i.symbol === 'QABUY');
    
    const execTradeRes = await page.request.post(`/api/v1/portfolios/${portfolioId}/trade`, {
      headers: { Cookie: cookieHeader },
      data: {
        instrument_id: qabuyId,
        side: 'BUY',
        quantity: 1,
        native_execution_price: 9999.00, // Manual price (should be ignored by PAPER)
        fee: 0
      }
    });
    
    const status = execTradeRes.status();
    const txData = await execTradeRes.json();
    if (status !== 200) console.log('Flow F 400 Error:', txData);
    
    expect(status).toBe(200);
    expect(Number(txData.price)).toBe(Number(qabuyOpp.quote_price)); // Must match the system quote
    expect(txData.execution_source).toBe('SYSTEM_QUOTE');
    expect(txData.execution_source).not.toBe('MANUAL_BROKER');
  });

});
