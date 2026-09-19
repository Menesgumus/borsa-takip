import { test, expect, Page } from '@playwright/test';

async function registerAndOnboard(page: Page, email: string, password: string) {
  await page.goto('/register');
  await page.fill('#email', email);
  await page.fill('#password', password);
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/.*\/onboarding/, { timeout: 20000 });
  
  await page.fill('#firstName', 'QA');
  await page.fill('#lastName', 'MultiAsset');
  
  const submitBtn = page.locator('button[type="submit"]');
  await expect(async () => {
    await page.getByText('YÜKSEK', { exact: true }).click();
    await expect(submitBtn).toBeEnabled({ timeout: 2000 });
  }).toPass({ timeout: 20000 });
  
  const fname = await page.inputValue('#firstName');
  if (!fname) {
      await page.fill('#firstName', 'QA');
      await page.fill('#lastName', 'MultiAsset');
  }

  await submitBtn.click();
  await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 20000 });
}

test.describe('Phase 28 Multi-Asset Allocation & Basket Builder', () => {
  test('Basket Builder Flow and Execution', async ({ page, request }) => {
    // 1. Register and login
    const ts = Date.now();
    const email = `qa.multiasset.${ts}@example.com`;
    await registerAndOnboard(page, email, 'qa_password123!');

    // 2. Create REAL Portfolio
    await page.goto('/portfolios');
    const createPortfolioButton = page.getByRole('button', { name: 'İlk Portföyü Oluştur' });
    if (await createPortfolioButton.isVisible()) {
      await createPortfolioButton.click();
    } else {
      await page.getByRole('button', { name: 'Yeni Ekle' }).click();
    }
    
    const createModal = page.locator('.fixed.inset-0.z-50');
    await expect(createModal.getByRole('heading', { name: 'Yeni Portföy Ekle' })).toBeVisible({ timeout: 10000 });
    
    await createModal.getByRole('textbox').fill(`Phase 28 Multi-Asset Portfolio ${ts}`);
    await createModal.getByRole('combobox').selectOption('REAL');
    
    const fundingModal = page.locator('.fixed.inset-0.z-50');
    await fundingModal.getByRole('spinbutton').fill('100000');
    
    const [response] = await Promise.all([
      page.waitForResponse(res => res.url().includes('/api/v1/portfolios') && res.request().method() === 'POST'),
      fundingModal.getByRole('button', { name: 'Oluştur' }).click(),
    ]);
    const portfolioData = await response.json();
    const portfolioId = portfolioData.id;

    // 3. Navigate to Opportunities
    await page.goto('/opportunities');
    await page.waitForURL('**/opportunities');
    
    // Select the portfolio
    await page.selectOption('select.w-full.bg-slate-50', { value: String(portfolioId) });
    
    // 4. Test Asset Class Filter Tabs
    // Click on US Equities tab
    const usTab = page.locator('button', { hasText: 'ABD Hisse' });
    await expect(usTab).toBeVisible();
    await usTab.click();
    
    // Check if GET /opportunities?asset_class=US_EQUITY was fired
    const usRes = await page.waitForResponse(res => res.url().includes('asset_class=US_EQUITY') && res.request().method() === 'GET');
    expect(usRes.ok()).toBeTruthy();

    const gldTab = page.locator('button', { hasText: 'Altın/Emtia' });
    await expect(gldTab).toBeVisible();
    await gldTab.click();
    const gldRes = await page.waitForResponse(res => res.url().includes('asset_class=GOLD') && res.request().method() === 'GET');
    expect(gldRes.ok()).toBeTruthy();

    // Go back to Tüm Varlıklar
    await page.locator('button', { hasText: 'Tüm Varlıklar' }).click();

    // 5. Open Basket Builder
    const sepetLink = page.locator('text=Sepet Oluştur');
    await expect(sepetLink).toBeVisible();
    await sepetLink.click();

    // Wait for basket preview request
    const previewRes = await page.waitForResponse(res => res.url().includes(`/api/v1/portfolios/${portfolioId}/basket-preview`) && res.request().method() === 'POST');
    expect(previewRes.ok()).toBeTruthy();
    
    await expect(page.locator('text=Varlık Sınıfı Hedefleri')).toBeVisible();

    // 6. Provide a deploy amount and recalculate
    await page.fill('input[type="number"][placeholder="Örn: 10000"]', '50000');
    await page.locator('button', { hasText: 'Sepeti Hesapla' }).click();

    const recalculateRes = await page.waitForResponse(res => res.url().includes(`/api/v1/portfolios/${portfolioId}/basket-preview`) && res.request().method() === 'POST');
    expect(recalculateRes.ok()).toBeTruthy();

    // 7. Manual Price Execution Preview
    // Find the first manual price input
    const manualInputs = page.locator('input.w-24.text-right.border');
    if (await manualInputs.count() > 0) {
      await manualInputs.first().fill('150.00');
      
      const onizleBtn = page.locator('button', { hasText: 'Önizle' }).first();
      
      // Setup dialog handler before clicking
      const dialogPromise = page.waitForEvent('dialog');
      
      await onizleBtn.click();
      
      const execPreviewRes = await page.waitForResponse(res => res.url().includes(`/api/v1/portfolios/${portfolioId}/execution-preview`) && res.request().method() === 'POST');
      expect(execPreviewRes.ok()).toBeTruthy();
      
      const dialog = await dialogPromise;
      expect(dialog.message()).toContain('İşlem Önizlemesi Alındı:');
      await dialog.accept();
    }
  });
});
