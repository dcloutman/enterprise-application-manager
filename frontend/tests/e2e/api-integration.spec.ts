import { test, expect } from '@playwright/test';

test.describe('API Integration', () => {
    test('should handle successful API responses', async ({ page }) => {
        // Mock all API endpoints with realistic data
        await page.route('/api/applications/dashboard_stats/', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    total_applications: 15,
                    active_applications: 12,
                    by_lifecycle_stage: [
                        { lifecycle_stage: 'production', count: 8 },
                        { lifecycle_stage: 'development', count: 4 },
                        { lifecycle_stage: 'testing', count: 3 }
                    ],
                    by_criticality: [
                        { criticality: 'high', count: 3 },
                        { criticality: 'medium', count: 8 },
                        { criticality: 'low', count: 4 }
                    ]
                })
            });
        });

        await page.route('/api/applications/*', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    results: [
                        {
                            id: 'app-1',
                            name: 'Customer Portal',
                            description: 'Web portal for customer self-service',
                            lifecycle_stage: 'production',
                            criticality: 'high',
                            business_owner: 'Customer Success Team',
                            technical_owner: 'Platform Team',
                            primary_server_hostname: 'web-prod-01'
                        }
                    ]
                })
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
                            ip_address: '10.0.1.100',
                            operating_system: 'Ubuntu 22.04',
                            os_version: '22.04.3',
                            cpu_cores: 4,
                            memory_gb: 16,
                            storage_gb: 100
                        }
                    ]
                })
            });
        });

        await page.route('/api/languages/', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    results: [
                        { id: 1, name: 'Python', is_active: true },
                        { id: 2, name: 'JavaScript', is_active: true }
                    ]
                })
            });
        });

        await page.route('/api/datastores/', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    results: [
                        { id: 1, name: 'PostgreSQL', datastore_type: 'relational' },
                        { id: 2, name: 'Redis', datastore_type: 'cache' }
                    ]
                })
            });
        });

        await page.goto('/');
        
        // Verify all data is displayed correctly
        await expect(page.locator('text=15')).toBeVisible(); // total applications
        await expect(page.locator('text=12')).toBeVisible(); // active applications
        await expect(page.locator('text=Customer Portal')).toBeVisible();
        await expect(page.locator('text=web-prod-01')).toBeVisible();
        await expect(page.locator('text=Python')).toBeVisible();
        await expect(page.locator('text=PostgreSQL (relational)')).toBeVisible();
    });

    test('should handle API timeout gracefully', async ({ page }) => {
        // Simulate slow API responses
        await page.route('/api/**', async route => {
            await page.waitForTimeout(5000); // 5 second delay
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ results: [] })
            });
        });

        await page.goto('/');
        
        // Should show loading state for extended period
        await expect(page.locator('.loading')).toBeVisible();
        
        // Wait a bit to ensure loading persists
        await page.waitForTimeout(2000);
        await expect(page.locator('.loading')).toBeVisible();
    });

    test('should handle mixed API success/failure responses', async ({ page }) => {
        // Some APIs succeed, others fail
        await page.route('/api/applications/dashboard_stats/', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    total_applications: 10,
                    active_applications: 8
                })
            });
        });

        await page.route('/api/applications/*', async route => {
            await route.fulfill({
                status: 500,
                contentType: 'application/json',
                body: JSON.stringify({ error: 'Internal Server Error' })
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
                            hostname: 'test-server',
                            name: 'Test Server',
                            environment_type: 'development'
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

        await page.goto('/');
        
        // Should handle partial failures gracefully
        // Statistics should load
        await expect(page.locator('text=10')).toBeVisible();
        
        // Applications section should show error handling
        // But servers should load successfully
        await expect(page.locator('text=test-server')).toBeVisible();
    });

    test('should handle malformed JSON responses', async ({ page }) => {
        await page.route('/api/**', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: 'invalid json{'
            });
        });

        await page.goto('/');
        
        // Should handle JSON parse errors gracefully
        await expect(page.locator('.error')).toBeVisible();
    });

    test('should make correct API requests', async ({ page }) => {
        const apiRequests: string[] = [];
        
        await page.route('/api/**', async route => {
            apiRequests.push(route.request().url());
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ results: [] })
            });
        });

        await page.goto('/');
        
        // Wait for all API calls to complete
        await page.waitForTimeout(2000);
        
        // Verify expected API endpoints were called
        const expectedEndpoints = [
            '/api/applications/dashboard_stats/',
            '/api/applications/?limit=10',
            '/api/servers/?limit=10',
            '/api/languages/',
            '/api/datastores/'
        ];

        for (const endpoint of expectedEndpoints) {
            const wasRequested = apiRequests.some(url => url.includes(endpoint));
            expect(wasRequested).toBe(true);
        }
    });

    test('should handle authentication errors', async ({ page }) => {
        await page.route('/api/**', async route => {
            await route.fulfill({
                status: 401,
                contentType: 'application/json',
                body: JSON.stringify({ error: 'Authentication required' })
            });
        });

        await page.goto('/');
        
        // Should handle 401 errors appropriately
        await expect(page.locator('.error')).toBeVisible();
        await expect(page.locator('text=Authentication required')).toBeVisible();
    });

    test('should handle rate limiting', async ({ page }) => {
        await page.route('/api/**', async route => {
            await route.fulfill({
                status: 429,
                contentType: 'application/json',
                body: JSON.stringify({ error: 'Too Many Requests' }),
                headers: {
                    'Retry-After': '60'
                }
            });
        });

        await page.goto('/');
        
        // Should handle rate limiting gracefully
        await expect(page.locator('.error')).toBeVisible();
    });

    test('should handle network connectivity issues', async ({ page }) => {
        // Simulate network failure
        await page.route('/api/**', async route => {
            await route.abort('failed');
        });

        await page.goto('/');
        
        // Should show appropriate error for network issues
        await expect(page.locator('.error')).toBeVisible();
    });
});
