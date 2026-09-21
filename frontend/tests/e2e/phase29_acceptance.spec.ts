import { test, expect } from '@playwright/test';

// Utility to create a portfolio and return its ID
async function setupPortfolio(page: any, isPaper: boolean = true) {
  const uniqueId = Date.now();
  const email = `phase29_${uniqueId}@example.com`;
  const password = 'Password123!';

  // Register via API (no auth needed)
  await page.request.post('/api/v1/auth/register', {
    data: { email, password, full_name: 'Phase29 Tester' }
  });
  
  // Login via UI so browser gets the cookie
  await page.goto('/login');
  await page.fill('#email', email);
  await page.fill('#password', password);
  await page.click('button[type="submit"]');
  await page.waitForURL(url => url.pathname.includes('/dashboard') || url.pathname.includes('/onboarding'));

  // Complete onboarding to avoid being stuck
  await page.evaluate(async () => {
    await fetch('/api/v1/users/profile', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ onboarding_completed: true })
    });
  });

  // Create Portfolio and deposit cash via page.evaluate
  const portfolioId = await page.evaluate(async ({ isPaper, uniqueId }) => {
    const pRes = await fetch('/api/v1/portfolios', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: `Phase29 Portfolio ${uniqueId}`,
        description: 'E2E Testing',
        portfolio_type: isPaper ? 'PAPER' : 'REAL',
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

  return { portfolioId };
}

// Utility to buy an instrument
async function buyInstrument(page: any, portfolioId: number, symbol: string, quantity: number, price: number, isPaper: boolean = true) {
  await page.evaluate(async ({ portfolioId, symbol, quantity, price, isPaper }) => {
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
  await page.evaluate(async ({ portfolioId, symbol, overrideData }) => {
    const iRes = await fetch(`/api/v1/instruments?search=${symbol}`);
    const iData = await iRes.json();
    const instrumentId = iData.items[0].id;
    
    await fetch(`/api/v1/test-fixtures/lifecycle-override`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        portfolio_id: portfolioId,
        instrument_id: instrumentId,
        ...overrideData
      })
    });
  }, { portfolioId, symbol, overrideData });
}

test.describe('Phase 29 Position Lifecycle', () => {
  
  test('Flow A & B - STABLE and WATCH Rendering', async ({ page }) => {
    const { portfolioId } = await setupPortfolio(page, true);
    
    // Buy QAHOLD (PAPER)
    await buyInstrument(page, portfolioId, 'QAHOLD', 10, 15.0, true);
    
    // Go to portfolio
    await page.goto(`/portfolios/${portfolioId}?tab=pozisyonlar`);
    await page.waitForTimeout(1000); // Wait for data to load

    // Explicit Evaluation (INITIALIZE ENGINE)
    await page.getByRole('button', { name: /Yaşam Döngüsünü Güncelle/i }).click();
    await page.waitForTimeout(1000);

    // Verify STABLE / HOLD
    await expect(page.getByTestId('lifecycle-health-QAHOLD')).toContainText('Stabil');
    await expect(page.getByTestId('lifecycle-action-QAHOLD')).toContainText('Bekle');
    
    // Override to WATCH
    await overrideLifecycle(page, portfolioId, 'QAHOLD', {
      health_state: 'WATCH',
      recommended_action: 'HOLD',
      negative_confirmation_count: 1
    });

    await page.reload();
    await page.waitForTimeout(1000);
    // DO NOT click evaluate again, or we will overwrite the override!

    // Verify WATCH / HOLD
    await expect(page.getByTestId('lifecycle-health-QAHOLD')).toContainText('İzle');
    await expect(page.getByTestId('lifecycle-action-QAHOLD')).toContainText('Bekle');

    // Expand details
    await page.getByTestId('lifecycle-row-QAHOLD').click();
    await expect(page.getByTestId('lifecycle-details-QAHOLD')).toContainText('İlk olumsuz gözlem kaydedildi');
  });

  test('Flow C & F - CONFIRMED REDUCE and DATA UNCERTAINTY', async ({ page }) => {
    const { portfolioId } = await setupPortfolio(page, true);
    await buyInstrument(page, portfolioId, 'QABUY', 10, 10.0, true);

    await page.goto(`/portfolios/${portfolioId}?tab=pozisyonlar`);
    await page.waitForTimeout(1000);

    // Explicit Evaluation (INITIALIZE ENGINE)
    await page.getByRole('button', { name: /Yaşam Döngüsünü Güncelle/i }).click();
    await page.waitForTimeout(1000);

    // Override to CONFIRMED REDUCE
    await overrideLifecycle(page, portfolioId, 'QABUY', {
      health_state: 'CONFIRMED_DETERIORATION',
      recommended_action: 'CONSIDER_REDUCE',
      negative_confirmation_count: 3,
      suggested_reduce_quantity: '5',
      suggested_remaining_quantity: '5',
      estimated_released_cash_base: '50.0',
      reason_codes: ['CONFIRMED_DETERIORATION']
    });

    await page.reload();
    await page.waitForTimeout(1000);
    // DO NOT click evaluate again!

    await expect(page.getByTestId('lifecycle-health-QABUY')).toContainText('Bozulma doğrulandı');
    await expect(page.getByTestId('lifecycle-action-QABUY')).toContainText('Azaltmayı değerlendir');

    await page.getByTestId('lifecycle-row-QABUY').click();
    await expect(page.getByTestId('lifecycle-details-QABUY')).toContainText('TAHMİN / ÖNİZLEME');
    await expect(page.getByTestId('lifecycle-sell-QABUY')).toBeVisible();

    // Data Uncertainty
    await overrideLifecycle(page, portfolioId, 'QABUY', {
      health_state: 'STABLE',
      recommended_action: 'NO_ACTION_DATA',
      data_state: 'MISSING_DATA'
    });

    await page.reload();
    await page.waitForTimeout(1000);
    // DO NOT click evaluate again!
    
    await expect(page.getByTestId('lifecycle-action-QABUY')).toContainText('Veri yetersiz');
    await page.getByTestId('lifecycle-row-QABUY').click();
    await expect(page.getByTestId('lifecycle-details-QABUY')).toContainText('yeterli veri sağlanamadı');
  });

  test('Flow G - ACTUAL SELL -> REAL CASH -> ROTATION', async ({ page }) => {
    // PAPER portfolio for simulation execution
    const { portfolioId } = await setupPortfolio(page, true);
    await buyInstrument(page, portfolioId, 'QAHOLD', 10, 20.0, true);

    await page.goto(`/portfolios/${portfolioId}?tab=pozisyonlar`);
    await page.waitForTimeout(1000);

    // Explicit Evaluation (INITIALIZE ENGINE)
    await page.getByRole('button', { name: /Yaşam Döngüsünü Güncelle/i }).click();
    await page.waitForTimeout(1000);

    // Override to CONSIDER_EXIT
    await overrideLifecycle(page, portfolioId, 'QAHOLD', {
      health_state: 'CONFIRMED_DETERIORATION',
      recommended_action: 'CONSIDER_EXIT',
      suggested_reduce_quantity: '10',
      suggested_remaining_quantity: '0',
      estimated_released_cash_base: '200.0',
      reason_codes: ['EXIT_DETERIORATION']
    });

    await page.reload();
    await page.waitForTimeout(1000);
    // DO NOT click evaluate again!

    await expect(page.getByTestId('lifecycle-action-QAHOLD')).toContainText('Çıkışı değerlendir');
    
    // Do the sell
    await page.getByTestId('lifecycle-row-QAHOLD').click();
    await page.getByTestId('lifecycle-sell-QAHOLD').click(); // Opens modal
    
    // Auto-search happens from initialSymbol, wait for result and click it
    const searchResult = page.getByTestId('search-result-QAHOLD');
    await expect(searchResult).toBeVisible({ timeout: 8000 });
    await searchResult.click();
    
    // Modal Should prefill quantity 10 for Exit
    await expect(page.locator('input[type="number"]').first()).toHaveValue('10');
    await page.getByRole('button', { name: 'İşlemi Onayla' }).click();

    // Verify success modal and Rotation
    await expect(page.getByText('İşlem Başarılı')).toBeVisible();
    await page.getByTestId('lifecycle-rotation').click();

    // Verify it redirects to sepet (Basket Builder)
    await expect(page).toHaveURL(/tab=sepet/);
    await expect(page.getByRole('heading', { name: 'Sepet Oluştur (Basket Builder)' })).toBeVisible();
  });
});
