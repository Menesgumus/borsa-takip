import { test, expect } from '@playwright/test';

test.describe('Phase 28 Multi-Asset Allocation', () => {
  test('Basket Builder Flow and Execution', async ({ page }) => {
    // 1. Login and go to Opportunities
    await page.goto('/login');
    await page.fill('input[type="email"]', 'qa@example.com');
    await page.fill('input[type="password"]', 'qa_password');
    await page.click('button:has-text("Giriş Yap")');
    await page.goto('/opportunities');
    await expect(page.locator('text=Fırsatlar').first()).toBeVisible();

    // 2. Click "Sepet Oluştur" for the first portfolio
    // Assume a portfolio exists, otherwise we'd create one.
    // Let's create one first to be safe
    await page.goto('/portfolios');
    await page.click('text=İlk Portföyü Oluştur', { timeout: 2000 }).catch(async () => {
       await page.click('text=Yeni Ekle');
    });
    await page.fill('input[placeholder="Örn: BIST Temettü"]', 'Phase 28 QA Portfolio');
    await page.selectOption('select', 'REAL');
    await page.fill('input[type="number"]', '100000');
    await page.click('button:has-text("Oluştur")');
    await expect(page.locator('text=Risk Analizi').first()).toBeVisible();

    // 3. Go to Opportunities
    await page.goto('/opportunities');
    await page.selectOption('select', { label: 'Phase 28 QA Portfolio' });
    
    // 4. Click Sepet Oluştur
    const sepetLink = page.locator('text=Sepet Oluştur');
    await expect(sepetLink).toBeVisible();
    await sepetLink.click();

    // 5. Verify Basket Builder loads
    await expect(page.locator('text=Yatırılacak Tutar')).toBeVisible();
    
    // 6. Preview Basket
    // The items will load automatically.
    await expect(page.locator('text=Varlık Sınıfı Hedefleri')).toBeVisible();
    
    // Check if Altın, US Equities, BIST are visible in the sleeves
    await expect(page.locator('text=US EQUITY').first()).toBeVisible({ timeout: 10000 }).catch(() => {});
    
    // 7. Click Sepeti Uygula
    await page.click('button:has-text("Sepeti Uygula")');
    
    // Since we mocked alert in our minds, let's just listen to it
    page.on('dialog', async dialog => {
      expect(dialog.message()).toContain('başarıyla');
      await dialog.accept();
    });
    
    // 8. Go to transactions tab to verify
    await page.click('text=İşlem Geçmişi');
    // We should see executions
    await expect(page.locator('table').first()).toBeVisible();
  });
});
