import { expect, test } from '@playwright/test';

test('dashboard connects through the proxy to the live API and PostgreSQL', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  const status = page.getByRole('region', { name: 'Application connection' });
  await expect(status.getByRole('status')).toContainText('API connected — FlowDesk · sprint-0');
  const response = await page.request.get('/actuator/health');
  expect(response.ok()).toBeTruthy();
  expect(await response.json()).toMatchObject({ status: 'UP' });
  expect(errors).toEqual([]);
});

test('failed requests show safe errors and retry recovers against the live backend', async ({ page }) => {
  await page.route('**/api/v1/info', route => route.fulfill({ status: 500, body: 'private stack trace' }));
  await page.goto('/');
  await expect(page.getByRole('alert')).toContainText('Unable to connect');
  await expect(page.getByText('private stack trace')).toHaveCount(0);
  await page.unroute('**/api/v1/info');
  await page.getByRole('button', { name: 'Retry connection' }).click();
  await expect(page.getByRole('status')).toContainText('API connected — FlowDesk · sprint-0');
});

test('HTTP 200 with a malformed payload cannot appear connected', async ({ page }) => {
  await page.route('**/api/v1/info', route => route.fulfill({ json: {} }));
  await page.goto('/');
  await expect(page.getByRole('alert')).toBeVisible();
  await expect(page.getByText('API connected')).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Retry connection' })).toBeEnabled();
});

test('connection controls remain visible and usable at a mobile viewport', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await expect(page.getByRole('status')).toContainText('API connected');
  await expect(page.getByRole('button', { name: 'Check connection' })).toBeInViewport();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
  await page.getByRole('button', { name: 'Check connection' }).click();
  await expect(page.getByRole('status')).toContainText('API connected');
  await page.screenshot({ path: 'test-results/connectivity-mobile.png', fullPage: true });
});
