import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 90000,
  retries: 0,
  use: {
    baseURL: 'http://127.0.0.1:3000',
    trace: 'on',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'mobile-360x800',
      use: { browserName: 'chromium', viewport: { width: 360, height: 800 } },
    },
    {
      name: 'mobile-390x844',
      use: { browserName: 'chromium', viewport: { width: 390, height: 844 } },
    },
    {
      name: 'mobile-430x932',
      use: { browserName: 'chromium', viewport: { width: 430, height: 932 } },
    },
    {
      name: 'tablet-768x1024',
      use: { browserName: 'chromium', viewport: { width: 768, height: 1024 } },
    },
    {
      name: 'tablet-1024x768',
      use: { browserName: 'chromium', viewport: { width: 1024, height: 768 } },
    },
    {
      name: 'desktop-1280x800',
      use: { browserName: 'chromium', viewport: { width: 1280, height: 800 } },
    },
    {
      name: 'desktop-1920x1080',
      use: { browserName: 'chromium', viewport: { width: 1920, height: 1080 } },
    },
  ],
  webServer: {
    command: 'pnpm run start',
    url: 'http://127.0.0.1:3000',
    reuseExistingServer: true,
    timeout: 120000,
    env: {
      INTERNAL_API_URL: 'http://127.0.0.1:8002',
      NEXT_PUBLIC_API_URL: 'http://127.0.0.1:8002',
      DISABLE_PWA: 'true',
      HOSTNAME: '127.0.0.1',
    },
  },
});
