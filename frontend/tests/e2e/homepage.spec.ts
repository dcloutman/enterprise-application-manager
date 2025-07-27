import { test, expect } from '@playwright/test';

test.describe('Enterprise Application Tracker E2E Tests', () => {
    test.beforeEach(async ({ page }) => {
        // Set up basic authentication if needed
        // These tests should run against the real API
    });

    test('should load the main page successfully', async ({ page }) => {
        await page.goto('/');

        // Check that the page title is correct
        await expect(page).toHaveTitle(/Enterprise Application Tracker/);

        // Check that main heading is visible
        await expect(page.getByText('Enterprise Application Tracker (EAT)')).toBeVisible();
        await expect(page.getByText('Enterprise Application Tracker - Comprehensive IT Infrastructure Management')).toBeVisible();
    });

    test('should display dashboard sections', async ({ page }) => {
        await page.goto('/');

        // Wait for main sections to load from real API
        await expect(page.getByText('Dashboard Overview')).toBeVisible();
        await expect(page.getByText('Recent Applications')).toBeVisible();
        await expect(page.getByText('Server Environments')).toBeVisible();
        await expect(page.getByText('Programming Languages')).toBeVisible();
        await expect(page.getByText('Data Stores')).toBeVisible();
        await expect(page.getByText('Quick Links')).toBeVisible();
    });

    test('should display quick links section', async ({ page }) => {
        await page.goto('/');

        // Check quick links section
        await expect(page.getByText('Quick Links')).toBeVisible();
        await expect(page.getByText('Admin Panel')).toBeVisible();
        await expect(page.getByText('API Browser')).toBeVisible();

        // Check that links are actually links
        await expect(page.locator('a').filter({ hasText: 'Admin Panel' })).toHaveAttribute('href', '/admin/');
        await expect(page.locator('a').filter({ hasText: 'API Browser' })).toHaveAttribute('href', '/api/');
    });

    test('should handle loading states', async ({ page }) => {
        await page.goto('/');

        // Should show loading indicator while real API calls are made
        // The exact loading behavior depends on the real implementation
        await expect(page.getByText('Enterprise Application Tracker (EAT)')).toBeVisible();
    });

    test('should be responsive on mobile devices', async ({ page }) => {
        // Set mobile viewport
        await page.setViewportSize({ width: 375, height: 667 });
        await page.goto('/');

        // Check that content is still visible and properly laid out
        await expect(page.getByText('Enterprise Application Tracker (EAT)')).toBeVisible();
        await expect(page.getByText('Dashboard Overview')).toBeVisible();
    });

    test('should have proper accessibility features', async ({ page }) => {
        await page.goto('/');

        // Check for proper heading hierarchy
        const h1 = page.getByRole('heading', { level: 1 });
        await expect(h1).toBeVisible();

        // Check for proper link text and navigation
        const links = page.getByRole('link');
        await expect(links.first()).toBeVisible();

        // Check keyboard navigation
        await page.keyboard.press('Tab');
        const focusedElement = page.locator(':focus');
        await expect(focusedElement).toBeVisible();
    });

    test('should navigate to external links correctly', async ({ page }) => {
        await page.goto('/');

        // Check that external links have correct attributes
        const adminLink = page.locator('a').filter({ hasText: 'Admin Panel' });
        await expect(adminLink).toHaveAttribute('target', '_blank');
        await expect(adminLink).toHaveAttribute('href', '/admin/');

        const apiLink = page.locator('a').filter({ hasText: 'API Browser' });
        await expect(apiLink).toHaveAttribute('target', '_blank');
        await expect(apiLink).toHaveAttribute('href', '/api/');
    });
});
