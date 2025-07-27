import { test, expect } from '@playwright/test';

test.describe('Dashboard Page', () => {
    test('should load dashboard and display basic structure', async ({ page }) => {
        await page.goto('/');
        
        // Check page title
        await expect(page).toHaveTitle(/Enterprise Application Tracker/);
        
        // Check main heading
        await expect(page.locator('h1')).toContainText('Enterprise Application Tracker');
        
        // Check main sections are present
        await expect(page.locator('header')).toBeVisible();
        
        // Wait for loading to complete (either show content or error)
        await page.waitForFunction(() => {
            const loadingElement = document.querySelector('.loading');
            return !loadingElement || loadingElement.style.display === 'none';
        }, { timeout: 10000 });
    });

    test('should handle loading state correctly', async ({ page }) => {
        // Intercept API calls to delay them
        await page.route('/api/**', async route => {
            await page.waitForTimeout(2000); // Delay for 2 seconds
            await route.continue();
        });

        await page.goto('/');
        
        // Should show loading state
        await expect(page.locator('.loading')).toBeVisible();
        await expect(page.locator('text=Loading dashboard data...')).toBeVisible();
        
        // Should show spinner
        await expect(page.locator('.spinner')).toBeVisible();
    });

    test('should handle API error gracefully', async ({ page }) => {
        // Intercept API calls and return errors
        await page.route('/api/**', async route => {
            await route.fulfill({
                status: 500,
                contentType: 'application/json',
                body: JSON.stringify({ error: 'Internal Server Error' })
            });
        });

        await page.goto('/');
        
        // Should show error state
        await expect(page.locator('.error')).toBeVisible();
        await expect(page.locator('text=Error Loading Data')).toBeVisible();
        
        // Should have retry button
        await expect(page.locator('button:has-text("Retry")')).toBeVisible();
    });

    test('should retry data loading when retry button is clicked', async ({ page }) => {
        let requestCount = 0;
        
        // First request fails, second succeeds
        await page.route('/api/**', async route => {
            requestCount++;
            if (requestCount <= 4) { // Fail first few requests (4 API endpoints)
                await route.fulfill({
                    status: 500,
                    body: JSON.stringify({ error: 'Server Error' })
                });
            } else {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({ results: [] })
                });
            }
        });

        await page.goto('/');
        
        // Wait for error state
        await expect(page.locator('.error')).toBeVisible();
        
        // Click retry button
        await page.locator('button:has-text("Retry")').click();
        
        // Should attempt to load again and potentially succeed
        await page.waitForTimeout(1000);
    });

    test('should display dashboard statistics when data loads', async ({ page }) => {
        // Mock successful API responses
        await page.route('/api/applications/dashboard_stats/', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    total_applications: 42,
                    active_applications: 38,
                    by_lifecycle_stage: [
                        { lifecycle_stage: 'production', count: 20 },
                        { lifecycle_stage: 'development', count: 12 },
                        { lifecycle_stage: 'testing', count: 6 }
                    ]
                })
            });
        });

        await page.route('/api/applications/*', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ results: [] })
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
        
        // Wait for statistics to load
        await expect(page.locator('text=Dashboard Overview')).toBeVisible();
        
        // Check statistics display
        await expect(page.locator('text=42')).toBeVisible(); // total applications
        await expect(page.locator('text=38')).toBeVisible(); // active applications
        
        // Check lifecycle stage chart
        await expect(page.locator('text=Applications by Lifecycle Stage')).toBeVisible();
        await expect(page.locator('text=production')).toBeVisible();
        await expect(page.locator('text=20')).toBeVisible();
    });

    test('should display applications section correctly', async ({ page }) => {
        await page.route('/api/applications/*', async route => {
            if (route.request().url().includes('dashboard_stats')) {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({
                        total_applications: 10,
                        active_applications: 8
                    })
                });
            } else {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({
                        results: [
                            {
                                id: '1',
                                name: 'Test Application',
                                description: 'A test application for demo purposes',
                                lifecycle_stage: 'production',
                                criticality: 'high',
                                business_owner: 'Test Owner',
                                primary_server_hostname: 'prod-server-01'
                            },
                            {
                                id: '2',
                                name: 'Dev Application',
                                description: 'Development application',
                                lifecycle_stage: 'development',
                                criticality: 'low',
                                business_owner: 'Dev Team'
                            }
                        ]
                    })
                });
            }
        });

        await page.route('/api/**', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ results: [] })
            });
        });

        await page.goto('/');
        
        // Wait for applications section
        await expect(page.locator('text=Recent Applications')).toBeVisible();
        
        // Check application cards
        await expect(page.locator('text=Test Application')).toBeVisible();
        await expect(page.locator('text=A test application for demo purposes')).toBeVisible();
        await expect(page.locator('text=Dev Application')).toBeVisible();
        
        // Check badges
        await expect(page.locator('.badge-production')).toBeVisible();
        await expect(page.locator('.badge-high')).toBeVisible();
        await expect(page.locator('.badge-development')).toBeVisible();
        await expect(page.locator('.badge-low')).toBeVisible();
        
        // Check "View All Applications" link
        await expect(page.locator('text=View All Applications →')).toBeVisible();
    });

    test('should display servers section correctly', async ({ page }) => {
        await page.route('/api/servers/*', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    results: [
                        {
                            id: 1,
                            hostname: 'web-server-01',
                            name: 'Production Web Server',
                            environment_type: 'production',
                            ip_address: '10.0.1.100',
                            operating_system: 'Ubuntu 22.04',
                            os_version: '22.04.3',
                            cpu_cores: 8,
                            memory_gb: 32
                        },
                        {
                            id: 2,
                            hostname: 'db-server-01',
                            name: 'Database Server',
                            environment_type: 'production',
                            ip_address: '10.0.1.101',
                            operating_system: 'Ubuntu 22.04'
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
        
        // Wait for servers section
        await expect(page.locator('text=Server Environments')).toBeVisible();
        
        // Check server cards
        await expect(page.locator('text=web-server-01')).toBeVisible();
        await expect(page.locator('text=Production Web Server')).toBeVisible();
        await expect(page.locator('text=db-server-01')).toBeVisible();
        await expect(page.locator('text=Database Server')).toBeVisible();
        
        // Check IP addresses
        await expect(page.locator('text=10.0.1.100')).toBeVisible();
        await expect(page.locator('text=10.0.1.101')).toBeVisible();
        
        // Check system specs
        await expect(page.locator('text=8 cores, 32GB RAM')).toBeVisible();
        
        // Check "View All Servers" link
        await expect(page.locator('text=View All Servers →')).toBeVisible();
    });

    test('should display technology stack correctly', async ({ page }) => {
        await page.route('/api/languages/', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    results: [
                        { id: 1, name: 'Python' },
                        { id: 2, name: 'JavaScript' },
                        { id: 3, name: 'Java' }
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
                        { id: 1, name: 'MySQL', datastore_type: 'relational' }
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
        
        // Check programming languages section
        await expect(page.locator('text=Programming Languages')).toBeVisible();
        await expect(page.locator('.tech-badge:has-text("Python")')).toBeVisible();
        await expect(page.locator('.tech-badge:has-text("JavaScript")')).toBeVisible();
        await expect(page.locator('.tech-badge:has-text("Java")')).toBeVisible();
        
        // Check datastores section
        await expect(page.locator('text=Data Stores')).toBeVisible();
        await expect(page.locator('.tech-badge:has-text("MySQL (relational)")')).toBeVisible();
    });

    test('should display quick links section', async ({ page }) => {
        await page.route('/api/**', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ results: [] })
            });
        });

        await page.goto('/');
        
        // Check quick links section
        await expect(page.locator('text=Quick Links')).toBeVisible();
        
        // Check individual quick links
        await expect(page.locator('text=Admin Panel')).toBeVisible();
        await expect(page.locator('text=API Browser')).toBeVisible();
        await expect(page.locator('text=Development Server')).toBeVisible();
        
        // Check link descriptions
        await expect(page.locator('text=Manage applications, servers, and infrastructure')).toBeVisible();
        await expect(page.locator('text=Explore REST API endpoints and data')).toBeVisible();
        await expect(page.locator('text=Frontend development with hot-reload')).toBeVisible();
    });

    test('should handle empty states correctly', async ({ page }) => {
        await page.route('/api/**', async route => {
            if (route.request().url().includes('dashboard_stats')) {
                await route.fulfill({
                    status: 404,
                    contentType: 'application/json',
                    body: JSON.stringify({ error: 'Not found' })
                });
            } else {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({ results: [] })
                });
            }
        });

        await page.goto('/');
        
        // Should show empty states
        await expect(page.locator('text=No applications found.')).toBeVisible();
        await expect(page.locator('text=No servers found.')).toBeVisible();
        await expect(page.locator('text=No languages configured.')).toBeVisible();
        await expect(page.locator('text=No datastores configured.')).toBeVisible();
        
        // Should show helpful links
        await expect(page.locator('text=Add some applications')).toBeVisible();
    });

    test('should be responsive on mobile devices', async ({ page }) => {
        await page.route('/api/**', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ results: [] })
            });
        });

        // Set mobile viewport
        await page.setViewportSize({ width: 375, height: 667 });
        await page.goto('/');
        
        // Check that main content is visible and properly laid out
        await expect(page.locator('h1')).toBeVisible();
        
        // Check that sections stack vertically on mobile
        const mainElement = page.locator('main');
        await expect(mainElement).toBeVisible();
        
        // Test horizontal scrolling is not needed
        const bodyScrollWidth = await page.evaluate(() => document.body.scrollWidth);
        const viewportWidth = 375;
        expect(bodyScrollWidth).toBeLessThanOrEqual(viewportWidth + 10); // Allow small margin
    });
});
