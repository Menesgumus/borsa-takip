import { test, expect } from '@playwright/test';

async function registerAndOnboard(page: any) {
  const ts = Date.now();
  const email = `qa.p29.${ts}@example.com`;
  
  await page.goto('/register');
  await page.fill('#email', email);
  await page.fill('#password', 'qa_password123!');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/.*\/onboarding/, { timeout: 20000 });
  
  await page.fill('#firstName', 'QA');
  await page.fill('#lastName', 'Phase29');
  
  const submitBtn = page.locator('button[type="submit"]');
  await expect(async () => {
    await page.getByText('YÜKSEK', { exact: true }).click();
    await expect(submitBtn).toBeEnabled({ timeout: 2000 });
  }).toPass({ timeout: 20000 });
  
  await submitBtn.click();
  await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 20000 });
}

// Utility to create portfolio (PAPER or REAL) and deposit initial cash
async function setupPortfolio(page: any, isPaper: boolean = true) {
  await page.goto('/');
  const uniqueId = Date.now();
  const portfolioId = await page.evaluate(async ({ isPaper, uniqueId }: { isPaper: boolean, uniqueId: number }) => {
    // We already have auth cookie from setup project, but since we're using page.evaluate fetch, it will include credentials.
    const type = isPaper ? 'PAPER' : 'REAL';
    const pRes = await fetch('/api/v1/portfolios', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: `Phase29 ${type} ${uniqueId}`,
        description: '',
        portfolio_type: type,
        base_currency: 'TRY'
      })
    });
    const pData = await pRes.json();
    
    await fetch(`/api/v1/portfolios/${pData.id}/transactions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        transaction_type: 'DEPOSIT',
        quantity: 100000,
        price: 1.0,
        fee: 0,
        date: new Date().toISOString()
      })
    });
    return pData.id;
  }, { isPaper, uniqueId });

  // Add the user profile PUT here because otherwise Next.js layout intercepts
  // and redirects fresh users to /onboarding, which blocks locator checks.
  await page.evaluate(async () => {
    await fetch('/api/v1/users/profile', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ onboarding_completed: true })
    });
  });

  return { portfolioId };
}

// Utility to buy an instrument
async function buyInstrument(page: any, portfolioId: number, symbol: string, quantity: number, price: number, isPaper: boolean = true) {
  await page.evaluate(async ({ portfolioId, symbol, quantity, price, isPaper }: { portfolioId: number, symbol: string, quantity: number, price: number, isPaper: boolean }) => {
    const iRes = await fetch(`/api/v1/instruments?search=${symbol}`);
    const iData = await iRes.json();
    const instrumentId = iData.items[0].id;

    if (isPaper) {
      await fetch(`/api/v1/portfolios/${portfolioId}/trade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          side: 'BUY',
          instrument_id: instrumentId,
          quantity
        })
      });
    } else {
      await fetch(`/api/v1/portfolios/${portfolioId}/manual-trade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          side: 'BUY',
          instrument_id: instrumentId,
          quantity,
          native_execution_price: price,
          fee: 0,
          executed_at: new Date().toISOString()
        })
      });
    }
  }, { portfolioId, symbol, quantity, price, isPaper });
}

// Utility to override lifecycle state
async function overrideLifecycle(page: any, portfolioId: number, symbol: string, overrideData: any) {
  await page.evaluate(async ({ portfolioId, symbol, overrideData }: { portfolioId: number, symbol: string, overrideData: any }) => {
    const iRes = await fetch(`/api/v1/instruments?search=${symbol}`);
    const iData = await iRes.json();
    const instrumentId = iData.items[0].id;
    
    const response = await fetch(`/api/v1/test-fixtures/lifecycle-override`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        portfolio_id: portfolioId,
        instrument_id: instrumentId,
        ...overrideData
      })
    });
    
    if (!response.ok) {
      throw new Error(`overrideLifecycle failed: ${response.status} ${await response.text()}`);
    }
  }, { portfolioId, symbol, overrideData });
}

test.describe('Phase 29 Position Lifecycle', () => {
  
  test('Flow A & B - STABLE and WATCH Rendering', async ({ page }) => {
    await registerAndOnboard(page);
    const { portfolioId } = await setupPortfolio(page, true);
    await buyInstrument(page, portfolioId, 'QAHOLD', 10, 15.0, true);
    
    await page.goto(`/portfolios/${portfolioId}?tab=pozisyonlar`);
    await expect(page.getByRole('row', { name: /QAHOLD/ })).toBeVisible();

    // Explicit Evaluation (INITIALIZE ENGINE)
    const evalPromise = page.waitForResponse(res => res.url().includes('/lifecycle/evaluate') && res.request().method() === 'POST');
    await page.getByRole('button', { name: /Ya.am D.ng.s.n. G.ncelle/i }).click();
    await evalPromise;

    await overrideLifecycle(page, portfolioId, 'QAHOLD', {
      health_state: 'STABLE',
      recommended_action: 'HOLD',
      reason_codes: []
    });
    
    const getPromise0 = page.waitForResponse(res => res.url().includes('/lifecycle') && res.request().method() === 'GET');
    await page.reload();
    await getPromise0;

    // Verify STABLE / HOLD
    await expect(page.getByTestId('lifecycle-health-QAHOLD')).toContainText('Stabil');
    await expect(page.getByTestId('lifecycle-action-QAHOLD')).toContainText('Bekle');
    
    // Override to WATCH
    await overrideLifecycle(page, portfolioId, 'QAHOLD', {
      health_state: 'WATCH',
      recommended_action: 'HOLD',
      negative_confirmation_count: 1
    });

    const getPromise = page.waitForResponse(res => res.url().includes('/lifecycle') && res.request().method() === 'GET');
    await page.reload();
    await getPromise;

    // Verify WATCH / HOLD
    await expect(page.getByTestId('lifecycle-health-QAHOLD')).toContainText('İzle');
    await expect(page.getByTestId('lifecycle-action-QAHOLD')).toContainText('Bekle');

    // Expand details
    await page.getByTestId('lifecycle-row-QAHOLD').click();
    await expect(page.getByTestId('lifecycle-details-QAHOLD')).toContainText('İlk olumsuz gözlem kaydedildi');
  });

  test('Flow C & F - CONFIRMED REDUCE and DATA UNCERTAINTY', async ({ page }) => {
    await registerAndOnboard(page);
    const { portfolioId } = await setupPortfolio(page, true);
    await buyInstrument(page, portfolioId, 'QABUY', 10, 10.0, true);

    await page.goto(`/portfolios/${portfolioId}?tab=pozisyonlar`);
    await expect(page.getByRole('row', { name: /QABUY/ })).toBeVisible();

    const evalPromise = page.waitForResponse(res => res.url().includes('/lifecycle/evaluate') && res.request().method() === 'POST');
    await page.getByRole('button', { name: /Ya.am D.ng.s.n. G.ncelle/i }).click();
    await evalPromise;

    await overrideLifecycle(page, portfolioId, 'QABUY', {
      health_state: 'CONFIRMED_DETERIORATION',
      recommended_action: 'CONSIDER_REDUCE',
      negative_confirmation_count: 3,
      suggested_reduce_quantity: '5',
      suggested_remaining_quantity: '5',
      estimated_released_cash_base: '50.0',
      reason_codes: ['CONFIRMED_DETERIORATION']
    });

    const getPromise = page.waitForResponse(res => res.url().includes('/lifecycle') && res.request().method() === 'GET');
    await page.reload();
    await getPromise;

    await expect(page.getByTestId('lifecycle-health-QABUY')).toContainText('Bozulma doğrulandı');
    await expect(page.getByTestId('lifecycle-action-QABUY')).toContainText('Azaltmayı değerlendir');

    await page.getByTestId('lifecycle-row-QABUY').click();
    await expect(page.getByTestId('lifecycle-details-QABUY')).toContainText('TAHMİN / ÖNİZLEME');
    await expect(page.getByTestId('lifecycle-sell-QABUY')).toBeVisible();

    // ONE-SHARE REDUCE UI CHECK — use a new portfolio with exactly 1 share so reduce_qty = floor(1*0.5) = 0
    const { portfolioId: portfolioId1Share } = await setupPortfolio(page, true);
    await buyInstrument(page, portfolioId1Share, 'QABUY', 1, 10.0, true);

    await page.goto(`/portfolios/${portfolioId1Share}?tab=pozisyonlar`);
    await expect(page.getByRole('row', { name: /QABUY/ })).toBeVisible();

    const evalPromise2 = page.waitForResponse(res => res.url().includes('/lifecycle/evaluate') && res.request().method() === 'POST');
    await page.getByRole('button', { name: /Ya.am D.ng.s.n. G.ncelle/i }).click();
    await evalPromise2;

    await overrideLifecycle(page, portfolioId1Share, 'QABUY', {
      health_state: 'CONFIRMED_DETERIORATION',
      recommended_action: 'CONSIDER_REDUCE',
      reason_codes: ['PARTIAL_REDUCTION_NOT_EXECUTABLE']
    });

    const getPromise2 = page.waitForResponse(res => res.url().includes('/lifecycle') && res.request().method() === 'GET');
    await page.reload();
    await getPromise2;

    await page.getByTestId('lifecycle-row-QABUY').click();
    await expect(page.getByText(/Pozisyon 1 adet/i)).toBeVisible();
    await expect(page.getByTestId('lifecycle-sell-QABUY')).not.toBeVisible(); // No full-exit substituted

    // Data Uncertainty — reuse the 1-share portfolio
    await overrideLifecycle(page, portfolioId1Share, 'QABUY', {
      health_state: 'STABLE',
      recommended_action: 'NO_ACTION_DATA',
      data_state: 'MISSING_DATA'
    });

    const getPromise3 = page.waitForResponse(res => res.url().includes('/lifecycle') && res.request().method() === 'GET');
    await page.reload();
    await getPromise3;
    
    await expect(page.getByTestId('lifecycle-action-QABUY')).toContainText('Veri yetersiz');
    await page.getByTestId('lifecycle-row-QABUY').click();
    await expect(page.getByTestId('lifecycle-details-QABUY')).toContainText('yeterli veri sağlanamadı');
  });


  test('Flow D - EXIT MUST BE EXPLICIT', async ({ page }) => {
    await registerAndOnboard(page);
    const { portfolioId } = await setupPortfolio(page, true); // PAPER
    await buyInstrument(page, portfolioId, 'QAHOLD', 10, 20.0, true);

    await page.goto(`/portfolios/${portfolioId}?tab=pozisyonlar`);
    await expect(page.getByRole('row', { name: /QAHOLD/ })).toBeVisible();

    const evalPromise = page.waitForResponse(res => res.url().includes('/lifecycle/evaluate') && res.request().method() === 'POST');
    await page.getByRole('button', { name: /Ya.am D.ng.s.n. G.ncelle/i }).click();
    await evalPromise;

    await overrideLifecycle(page, portfolioId, 'QAHOLD', {
      health_state: 'CONFIRMED_DETERIORATION',
      recommended_action: 'CONSIDER_EXIT',
      suggested_reduce_quantity: '10',
      suggested_remaining_quantity: '0',
      estimated_released_cash_base: '200.0',
      reason_codes: ['EXIT_DETERIORATION']
    });

    const getPromise = page.waitForResponse(res => res.url().includes('/lifecycle') && res.request().method() === 'GET');
    await page.reload();
    await getPromise;

    await expect(page.getByTestId('lifecycle-health-QAHOLD')).toContainText('Bozulma doğrulandı');
    await expect(page.getByTestId('lifecycle-action-QAHOLD')).toContainText('Çıkışı değerlendir');
    
    await page.getByTestId('lifecycle-row-QAHOLD').click();
    await expect(page.getByTestId('lifecycle-details-QAHOLD')).toContainText('Önerilen Satış Adedi:10'); // full quantity

    // Ensure NO auto-trade occurred
    const sRes = await page.evaluate(async (pid) => {
        const res = await fetch(`/api/v1/portfolios/${pid}/summary`);
        return await res.json();
    }, portfolioId);
    expect(parseFloat(sRes.positions.find((p:any) => p.symbol === 'QAHOLD').quantity)).toBe(10.0);
  });

  test('Flow E - RECOVERY + RELAPSE', async ({ page }) => {
    await registerAndOnboard(page);
    const { portfolioId } = await setupPortfolio(page, true);
    await buyInstrument(page, portfolioId, 'QAHOLD', 10, 20.0, true);

    await page.goto(`/portfolios/${portfolioId}?tab=pozisyonlar`);
    await expect(page.getByRole('row', { name: /QAHOLD/ })).toBeVisible();

    const evalPromise = page.waitForResponse(res => res.url().includes('/lifecycle/evaluate') && res.request().method() === 'POST');
    await page.getByRole('button', { name: /Ya.am D.ng.s.n. G.ncelle/i }).click();
    await evalPromise;

    // RECOVERING
    await overrideLifecycle(page, portfolioId, 'QAHOLD', {
      health_state: 'RECOVERING',
      recommended_action: 'HOLD',
      recovery_confirmation_count: 1
    });

    let getPromise = page.waitForResponse(res => res.url().includes('/lifecycle') && res.request().method() === 'GET');
    await page.reload();
    await getPromise;

    await expect(page.getByTestId('lifecycle-health-QAHOLD')).toContainText('Toparlanıyor');
    await expect(page.getByTestId('lifecycle-action-QAHOLD')).toContainText('Bekle');

    await page.getByTestId('lifecycle-row-QAHOLD').click();
    await expect(page.getByTestId('lifecycle-details-QAHOLD')).toContainText('ilk olumlu doğrulama alındı');

    // STABLE
    await overrideLifecycle(page, portfolioId, 'QAHOLD', {
      health_state: 'STABLE',
      recommended_action: 'HOLD'
    });

    getPromise = page.waitForResponse(res => res.url().includes('/lifecycle') && res.request().method() === 'GET');
    await page.reload();
    await getPromise;

    await expect(page.getByTestId('lifecycle-health-QAHOLD')).toContainText('Stabil');

    // RELAPSE (CONFIRMED_DETERIORATION)
    await overrideLifecycle(page, portfolioId, 'QAHOLD', {
      health_state: 'CONFIRMED_DETERIORATION',
      recommended_action: 'CONSIDER_REDUCE'
    });

    getPromise = page.waitForResponse(res => res.url().includes('/lifecycle') && res.request().method() === 'GET');
    await page.reload();
    await getPromise;

    await expect(page.getByTestId('lifecycle-health-QAHOLD')).toContainText('Bozulma doğrulandı');
  });

  test('Flow H - ADD', async ({ page }) => {
    await registerAndOnboard(page);
    const { portfolioId } = await setupPortfolio(page, true);
    await buyInstrument(page, portfolioId, 'QABUY', 10, 20.0, true);

    await page.goto(`/portfolios/${portfolioId}?tab=pozisyonlar`);
    await expect(page.getByRole('row', { name: /QABUY/ })).toBeVisible();

    const evalPromise = page.waitForResponse(res => res.url().includes('/lifecycle/evaluate') && res.request().method() === 'POST');
    await page.getByRole('button', { name: /Ya.am D.ng.s.n. G.ncelle/i }).click();
    await evalPromise;

    await overrideLifecycle(page, portfolioId, 'QABUY', {
      health_state: 'STABLE',
      recommended_action: 'CONSIDER_ADD'
    });

    const getPromise = page.waitForResponse(res => res.url().includes('/lifecycle') && res.request().method() === 'GET');
    await page.reload();
    await getPromise;

    await expect(page.getByTestId('lifecycle-health-QABUY')).toContainText('Stabil');
    await expect(page.getByTestId('lifecycle-action-QABUY')).toContainText('Artırmayı değerlendir');

    await page.getByTestId('lifecycle-row-QABUY').click();
    await expect(page.getByTestId('lifecycle-buy-QABUY')).toBeVisible();

    await page.getByTestId('lifecycle-buy-QABUY').click();
    
    const searchResult = page.getByTestId('search-result-QABUY');
    await expect(searchResult).toBeVisible({ timeout: 8000 });
    await searchResult.click();

    await expect(page.getByRole('button', { name: 'İşlemi Onayla' })).toBeVisible();
    await page.getByRole('button', { name: 'Kapat' }).click();
  });

  test('Flow G - ACTUAL SELL -> REAL CASH -> ROTATION', async ({ page }) => {
    await registerAndOnboard(page);
    // REAL portfolio
    const { portfolioId } = await setupPortfolio(page, false);
    await buyInstrument(page, portfolioId, 'QAHOLD', 10, 20.0, false);

    // Record baseline transaction count and cash
    const baseline = await page.evaluate(async (pid) => {
        const sRes = await fetch(`/api/v1/portfolios/${pid}/summary`);
        const sData = await sRes.json();
        const tRes = await fetch(`/api/v1/portfolios/${pid}/transactions`);
        const tData = await tRes.json();
        return { cash: sData.cash_balance, txCount: tData.length };
    }, portfolioId);

    await page.goto(`/portfolios/${portfolioId}?tab=pozisyonlar`);
    await expect(page.getByRole('row', { name: /QAHOLD/ })).toBeVisible();

    const evalPromise = page.waitForResponse(res => res.url().includes('/lifecycle/evaluate') && res.request().method() === 'POST');
    await page.getByRole('button', { name: /Ya.am D.ng.s.n. G.ncelle/i }).click();
    await evalPromise;

    await overrideLifecycle(page, portfolioId, 'QAHOLD', {
      health_state: 'CONFIRMED_DETERIORATION',
      recommended_action: 'CONSIDER_EXIT',
      suggested_reduce_quantity: '10',
      suggested_remaining_quantity: '0',
      estimated_released_cash_base: '200.0',
      reason_codes: ['EXIT_DETERIORATION']
    });

    const getPromise = page.waitForResponse(res => res.url().includes('/lifecycle') && res.request().method() === 'GET');
    await page.reload();
    await getPromise;
    
    // Verify pre-sell cash/tx unchanged
    const preSell = await page.evaluate(async (pid) => {
        const sRes = await fetch(`/api/v1/portfolios/${pid}/summary`);
        const sData = await sRes.json();
        const tRes = await fetch(`/api/v1/portfolios/${pid}/transactions`);
        const tData = await tRes.json();
        return { cash: sData.cash_balance, txCount: tData.length };
    }, portfolioId);
    expect(preSell.cash).toBe(baseline.cash);
    expect(preSell.txCount).toBe(baseline.txCount);

    await page.getByTestId('lifecycle-row-QAHOLD').click();
    
    // Verify REAL UI wording
    await expect(page.getByTestId('lifecycle-details-QAHOLD')).toContainText('Satışı dışarıda yaptıktan sonra kaydedin');
    
    await page.getByTestId('lifecycle-sell-QAHOLD').click();
    
    const searchResult = page.getByTestId('search-result-QAHOLD');
    await expect(searchResult).toBeVisible({ timeout: 8000 });
    await searchResult.click();
    
    await expect(page.locator('input[type="number"]').first()).toHaveValue('10');
    await page.locator('input[type="number"]').nth(1).fill('25.0');
    
    const tradePromise = page.waitForResponse(res => res.url().includes('/manual-trade') && res.request().method() === 'POST');
    await page.getByRole('button', { name: 'İşlemi Onayla' }).click();
    await tradePromise;

    await expect(page.getByText(/lem Ba.ar.l./i)).toBeVisible();


    // Verify post-sell cash and tx increased
    const postSell = await page.evaluate(async (pid) => {
        const sRes = await fetch(`/api/v1/portfolios/${pid}/summary`);
        const sData = await sRes.json();
        const tRes = await fetch(`/api/v1/portfolios/${pid}/transactions`);
        const tData = await tRes.json();
        return { cash: sData.cash_balance, txCount: tData.length };
    }, portfolioId);
    
    expect(postSell.txCount).toBe(baseline.txCount + 1);
    expect(Number(postSell.cash)).toBeGreaterThan(Number(baseline.cash));

    // Rotation
    await page.getByTestId('lifecycle-rotation').click();
    await expect(page).toHaveURL(/tab=sepet/);
    await expect(page.getByRole('heading', { name: 'Sepet Oluştur (Basket Builder)' })).toBeVisible();
  });
});
