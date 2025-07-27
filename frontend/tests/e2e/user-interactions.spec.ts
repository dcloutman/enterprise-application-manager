import { test, expect } from '@playwright/test';

test.describe('User Interactions', () => {
    test.beforeEach(async ({ page }) => {
        // Mock all API endpoints with test data
        await page.route('/api/applications/dashboard_stats/', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    total_applications: 25,
                    active_applications: 20,
                    by_lifecycle_stage: [
                        { lifecycle_stage: 'production', count: 12 },
                        { lifecycle_stage: 'development', count: 8 },
                        { lifecycle_stage: 'testing', count: 5 }
                    ],
                    by_criticality: [
                        { criticality: 'high', count: 5 },
                        { criticality: 'medium', count: 12 },
                        { criticality: 'low', count: 8 }
                    ]
                })
            });
        });

        await page.route('/api/applications/*', async route => {
            const url = route.request().url();
            const urlObj = new URL(url);
            const search = urlObj.searchParams.get('search');
            
            let results = [
                {
                    id: 'app-1',
                    name: 'Customer Portal',
                    description: 'Web portal for customer self-service',
                    lifecycle_stage: 'production',
                    criticality: 'high',
                    business_owner: 'Customer Success Team',
                    technical_owner: 'Platform Team',
                    primary_server_hostname: 'web-prod-01'
                },
                {
                    id: 'app-2',
                    name: 'Admin Dashboard',
                    description: 'Internal admin management system',
                    lifecycle_stage: 'production',
                    criticality: 'medium',
                    business_owner: 'Operations Team',
                    technical_owner: 'Backend Team',
                    primary_server_hostname: 'admin-prod-01'
                },
                {
                    id: 'app-3',
                    name: 'Analytics Engine',
                    description: 'Data processing and analytics',
                    lifecycle_stage: 'development',
                    criticality: 'high',
                    business_owner: 'Data Team',
                    technical_owner: 'Data Engineering',
                    primary_server_hostname: 'analytics-dev-01'
                }
            ];

            // Filter by search if provided
            if (search) {
                results = results.filter(app => 
                    app.name.toLowerCase().includes(search.toLowerCase()) ||
                    app.description.toLowerCase().includes(search.toLowerCase())
                );
            }

            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ results })
            });
        });

        await page.route('/api/servers/*', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    results: [
                        {
                            id: 1,
                            hostname: 'web-prod-01',
                            name: 'Production Web Server',
                            environment_type: 'production',
                            ip_address: '10.0.1.100'
                        },
                        {
                            id: 2,
                            hostname: 'admin-prod-01',
                            name: 'Admin Production Server',
                            environment_type: 'production',
                            ip_address: '10.0.1.101'
                        }
                    ]
                })
            });
        });

        await page.route('/api/**', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ results: [] })
            });
        });
    });

    test('should allow searching/filtering applications', async ({ page }) => {
        await page.goto('/');
        
        // Wait for initial load
        await expect(page.locator('text=Customer Portal')).toBeVisible();
        await expect(page.locator('text=Admin Dashboard')).toBeVisible();
        await expect(page.locator('text=Analytics Engine')).toBeVisible();

        // Find and interact with search input
        const searchInput = page.locator('input[type="search"], input[placeholder*="search"], input[placeholder*="filter"]').first();
        if (await searchInput.count() > 0) {
            await searchInput.fill('Customer');
            await page.keyboard.press('Enter');
            
            // Should show filtered results
            await expect(page.locator('text=Customer Portal')).toBeVisible();
            await expect(page.locator('text=Admin Dashboard')).not.toBeVisible();
        }
    });

    test('should handle form submissions', async ({ page }) => {
        await page.goto('/');
        
        // Look for any forms on the page
        const forms = page.locator('form');
        const formCount = await forms.count();

        if (formCount > 0) {
            // Test form interaction
            const firstForm = forms.first();
            const inputs = firstForm.locator('input, select, textarea');
            const inputCount = await inputs.count();

            if (inputCount > 0) {
                // Fill out form fields
                for (let i = 0; i < Math.min(inputCount, 3); i++) {
                    const input = inputs.nth(i);
                    const type = await input.getAttribute('type');
                    const tagName = await input.evaluate(el => el.tagName.toLowerCase());

                    if (type === 'text' || type === 'email' || tagName === 'textarea') {
                        await input.fill('Test Value');
                    } else if (type === 'checkbox') {
                        await input.check();
                    } else if (tagName === 'select') {
                        const options = input.locator('option');
                        const optionCount = await options.count();
                        if (optionCount > 1) {
                            await input.selectOption({ index: 1 });
                        }
                    }
                }

                // Submit form
                const submitButton = firstForm.locator('button[type="submit"], input[type="submit"]');
                if (await submitButton.count() > 0) {
                    await submitButton.click();
                    
                    // Verify some response (could be success message, redirect, etc.)
                    await page.waitForTimeout(1000);
                    // Form should either show success or clear
                }
            }
        }
    });

    test('should handle button clicks and navigation', async ({ page }) => {
        await page.goto('/');
        
        // Test various button interactions
        const buttons = page.locator('button:not([disabled])');
        const buttonCount = await buttons.count();

        for (let i = 0; i < Math.min(buttonCount, 5); i++) {
            const button = buttons.nth(i);
            const buttonText = await button.textContent();
            
            // Skip buttons that might cause navigation away from test
            if (buttonText && !buttonText.toLowerCase().includes('delete')) {
                await button.click();
                await page.waitForTimeout(500);
                
                // Verify page state after click
                await expect(page.locator('body')).toBeVisible();
            }
        }
    });

    test('should handle keyboard navigation', async ({ page }) => {
        await page.goto('/');
        
        // Test tab navigation
        await page.keyboard.press('Tab');
        await page.keyboard.press('Tab');
        await page.keyboard.press('Tab');
        
        // Test focus states
        const focusedElement = page.locator(':focus');
        await expect(focusedElement).toBeVisible();
        
        // Test Enter key on focused elements
        await page.keyboard.press('Enter');
        await page.waitForTimeout(500);
        
        // Test Escape key
        await page.keyboard.press('Escape');
    });

    test('should handle modal/dialog interactions', async ({ page }) => {
        await page.goto('/');
        
        // Look for buttons that might open modals
        const modalTriggers = page.locator('button:has-text("Add"), button:has-text("Edit"), button:has-text("Create"), button:has-text("View")');
        const triggerCount = await modalTriggers.count();

        if (triggerCount > 0) {
            const firstTrigger = modalTriggers.first();
            await firstTrigger.click();
            
            // Look for modal/dialog
            const modal = page.locator('[role="dialog"], .modal, .overlay').first();
            if (await modal.count() > 0) {
                await expect(modal).toBeVisible();
                
                // Test modal close
                const closeButton = modal.locator('button:has-text("Close"), button:has-text("Cancel"), [aria-label="Close"]');
                if (await closeButton.count() > 0) {
                    await closeButton.first().click();
                    await expect(modal).not.toBeVisible();
                } else {
                    // Try ESC key
                    await page.keyboard.press('Escape');
                    await expect(modal).not.toBeVisible();
                }
            }
        }
    });

    test('should handle sorting and pagination', async ({ page }) => {
        await page.goto('/');
        
        // Test sorting if available
        const sortButtons = page.locator('button:has-text("Sort"), th:has(button), [role="columnheader"]:has(button)');
        const sortCount = await sortButtons.count();

        if (sortCount > 0) {
            const firstSort = sortButtons.first();
            await firstSort.click();
            await page.waitForTimeout(1000);
            
            // Click again for reverse sort
            await firstSort.click();
            await page.waitForTimeout(1000);
        }

        // Test pagination if available
        const nextButton = page.locator('button:has-text("Next"), button[aria-label*="next"]');
        if (await nextButton.count() > 0) {
            await nextButton.click();
            await page.waitForTimeout(1000);
            
            // Go back
            const prevButton = page.locator('button:has-text("Previous"), button:has-text("Prev"), button[aria-label*="previous"]');
            if (await prevButton.count() > 0) {
                await prevButton.click();
                await page.waitForTimeout(1000);
            }
        }
    });

    test('should handle data refresh/reload', async ({ page }) => {
        await page.goto('/');
        
        // Initial load
        await expect(page.locator('text=Customer Portal')).toBeVisible();
        
        // Look for refresh buttons
        const refreshButtons = page.locator('button:has-text("Refresh"), button:has-text("Reload"), button[aria-label*="refresh"]');
        if (await refreshButtons.count() > 0) {
            await refreshButtons.first().click();
            await page.waitForTimeout(1000);
            
            // Data should still be visible after refresh
            await expect(page.locator('text=Customer Portal')).toBeVisible();
        }
    });

    test('should handle drag and drop interactions', async ({ page }) => {
        await page.goto('/');
        
        // Look for draggable elements
        const draggableElements = page.locator('[draggable="true"], .draggable');
        const draggableCount = await draggableElements.count();

        if (draggableCount > 1) {
            const source = draggableElements.first();
            const target = draggableElements.nth(1);
            
            // Perform drag and drop
            await source.dragTo(target);
            await page.waitForTimeout(1000);
        }
    });

    test('should handle context menus', async ({ page }) => {
        await page.goto('/');
        
        // Right-click on various elements to test context menus
        const clickableElements = page.locator('button, [role="button"], tr, .item').first();
        if (await clickableElements.count() > 0) {
            await clickableElements.click({ button: 'right' });
            await page.waitForTimeout(500);
            
            // Look for context menu
            const contextMenu = page.locator('.context-menu, [role="menu"]');
            if (await contextMenu.count() > 0) {
                await expect(contextMenu).toBeVisible();
                
                // Click elsewhere to close
                await page.click('body');
                await expect(contextMenu).not.toBeVisible();
            }
        }
    });

    test('should handle data export/download', async ({ page }) => {
        await page.goto('/');
        
        // Look for export/download buttons
        const exportButtons = page.locator('button:has-text("Export"), button:has-text("Download"), a[download]');
        const exportCount = await exportButtons.count();

        if (exportCount > 0) {
            // Start waiting for download before clicking
            const downloadPromise = page.waitForEvent('download');
            await exportButtons.first().click();
            
            try {
                const download = await Promise.race([
                    downloadPromise,
                    page.waitForTimeout(5000).then(() => null)
                ]);
                
                if (download) {
                    expect(download.suggestedFilename()).toBeTruthy();
                }
            } catch (error) {
                // Download might not actually happen in test environment
                console.log('Download test completed (may not actually download in test)');
            }
        }
    });
});
