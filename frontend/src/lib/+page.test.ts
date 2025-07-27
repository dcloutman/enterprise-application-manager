import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/svelte';
import Page from './+page.svelte';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('Main Page Component', () => {
    beforeEach(() => {
        mockFetch.mockClear();
    });

    it('should render page title and description', () => {
        // Mock all API calls to return empty data
        mockFetch.mockResolvedValue({
            ok: false,
            status: 404
        });

        render(Page);

        expect(screen.getByText('Enterprise Application Tracker (EAT)')).toBeInTheDocument();
        expect(screen.getByText('Enterprise Application Tracker - Comprehensive IT Infrastructure Management')).toBeInTheDocument();
    });

    it('should show loading spinner initially', () => {
        mockFetch.mockImplementation(() => new Promise(() => {})); // Never resolves

        render(Page);

        expect(screen.getByText('Loading dashboard data...')).toBeInTheDocument();
        expect(screen.getByRole('generic', { name: /spinner/i })).toBeInTheDocument();
    });

    it('should display error message when API calls fail', async () => {
        mockFetch.mockRejectedValue(new Error('Network error'));

        render(Page);

        await waitFor(() => {
            expect(screen.getByText('Error Loading Data')).toBeInTheDocument();
            expect(screen.getByText('Network error')).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument();
        });
    });

    it('should display dashboard statistics when available', async () => {
        const mockStats = {
            total_applications: 25,
            active_applications: 20,
            by_lifecycle_stage: [
                { lifecycle_stage: 'production', count: 10 },
                { lifecycle_stage: 'development', count: 8 },
                { lifecycle_stage: 'testing', count: 2 }
            ]
        };

        mockFetch.mockImplementation((url) => {
            if (url.includes('dashboard_stats')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockStats)
                });
            }
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ results: [] })
            });
        });

        render(Page);

        await waitFor(() => {
            expect(screen.getByText('Dashboard Overview')).toBeInTheDocument();
            expect(screen.getByText('25')).toBeInTheDocument(); // total_applications
            expect(screen.getByText('20')).toBeInTheDocument(); // active_applications
            expect(screen.getByText('Total Applications')).toBeInTheDocument();
            expect(screen.getByText('Active Applications')).toBeInTheDocument();
        });
    });

    it('should display lifecycle stage chart when data is available', async () => {
        const mockStats = {
            total_applications: 20,
            active_applications: 18,
            by_lifecycle_stage: [
                { lifecycle_stage: 'production', count: 10 },
                { lifecycle_stage: 'development', count: 5 },
                { lifecycle_stage: 'testing', count: 3 }
            ]
        };

        mockFetch.mockImplementation((url) => {
            if (url.includes('dashboard_stats')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockStats)
                });
            }
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ results: [] })
            });
        });

        render(Page);

        await waitFor(() => {
            expect(screen.getByText('Applications by Lifecycle Stage')).toBeInTheDocument();
            expect(screen.getByText('production')).toBeInTheDocument();
            expect(screen.getByText('development')).toBeInTheDocument();
            expect(screen.getByText('testing')).toBeInTheDocument();
            expect(screen.getByText('10')).toBeInTheDocument(); // production count
            expect(screen.getByText('5')).toBeInTheDocument(); // development count
            expect(screen.getByText('3')).toBeInTheDocument(); // testing count
        });
    });

    it('should display applications when available', async () => {
        const mockApplications = {
            results: [
                {
                    id: '1',
                    name: 'Test Application',
                    description: 'A test application',
                    lifecycle_stage: 'production',
                    criticality: 'high',
                    business_owner: 'John Doe',
                    primary_server_hostname: 'prod-server-01'
                },
                {
                    id: '2',
                    name: 'Dev App',
                    description: 'Development application',
                    lifecycle_stage: 'development',
                    criticality: 'low',
                    business_owner: 'Jane Smith',
                    primary_server_hostname: 'dev-server-01'
                }
            ]
        };

        mockFetch.mockImplementation((url) => {
            if (url.includes('applications')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockApplications)
                });
            }
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ results: [] })
            });
        });

        render(Page);

        await waitFor(() => {
            expect(screen.getByText('Recent Applications')).toBeInTheDocument();
            expect(screen.getByText('Test Application')).toBeInTheDocument();
            expect(screen.getByText('Dev App')).toBeInTheDocument();
            expect(screen.getByText('A test application')).toBeInTheDocument();
            expect(screen.getByText('John Doe')).toBeInTheDocument();
            expect(screen.getByText('Jane Smith')).toBeInTheDocument();
        });
    });

    it('should display servers when available', async () => {
        const mockServers = {
            results: [
                {
                    id: 1,
                    hostname: 'web-server-01',
                    name: 'Production Web Server',
                    ip_address: '10.0.1.100',
                    environment_type: 'production',
                    operating_system: 'Ubuntu',
                    os_version: '22.04',
                    cpu_cores: 8,
                    memory_gb: 32
                },
                {
                    id: 2,
                    hostname: 'db-server-01',
                    name: 'Database Server',
                    ip_address: '10.0.1.101',
                    environment_type: 'production',
                    operating_system: 'CentOS',
                    os_version: '8',
                    cpu_cores: 16,
                    memory_gb: 64
                }
            ]
        };

        mockFetch.mockImplementation((url) => {
            if (url.includes('servers')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockServers)
                });
            }
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ results: [] })
            });
        });

        render(Page);

        await waitFor(() => {
            expect(screen.getByText('Server Environments')).toBeInTheDocument();
            expect(screen.getByText('web-server-01')).toBeInTheDocument();
            expect(screen.getByText('db-server-01')).toBeInTheDocument();
            expect(screen.getByText('Production Web Server')).toBeInTheDocument();
            expect(screen.getByText('Database Server')).toBeInTheDocument();
            expect(screen.getByText('10.0.1.100')).toBeInTheDocument();
            expect(screen.getByText('10.0.1.101')).toBeInTheDocument();
        });
    });

    it('should display technology stack when available', async () => {
        const mockLanguages = {
            results: [
                { id: 1, name: 'Python' },
                { id: 2, name: 'JavaScript' },
                { id: 3, name: 'Java' }
            ]
        };

        const mockDatastores = {
            results: [
                { id: 1, name: 'PostgreSQL', datastore_type: 'relational' },
                { id: 2, name: 'Redis', datastore_type: 'cache' },
                { id: 3, name: 'Elasticsearch', datastore_type: 'search' }
            ]
        };

        mockFetch.mockImplementation((url) => {
            if (url.includes('languages')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockLanguages)
                });
            }
            if (url.includes('datastores')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockDatastores)
                });
            }
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ results: [] })
            });
        });

        render(Page);

        await waitFor(() => {
            expect(screen.getByText('Programming Languages')).toBeInTheDocument();
            expect(screen.getByText('Data Stores')).toBeInTheDocument();
            expect(screen.getByText('Python')).toBeInTheDocument();
            expect(screen.getByText('JavaScript')).toBeInTheDocument();
            expect(screen.getByText('Java')).toBeInTheDocument();
            expect(screen.getByText('PostgreSQL (relational)')).toBeInTheDocument();
            expect(screen.getByText('Redis (cache)')).toBeInTheDocument();
            expect(screen.getByText('Elasticsearch (search)')).toBeInTheDocument();
        });
    });

    it('should display quick links section', async () => {
        mockFetch.mockResolvedValue({
            ok: true,
            json: () => Promise.resolve({ results: [] })
        });

        render(Page);

        await waitFor(() => {
            expect(screen.getByText('Quick Links')).toBeInTheDocument();
            expect(screen.getByText('Admin Panel')).toBeInTheDocument();
            expect(screen.getByText('API Browser')).toBeInTheDocument();
            expect(screen.getByText('Development Server')).toBeInTheDocument();
        });
    });

    it('should show appropriate messages for empty data', async () => {
        mockFetch.mockResolvedValue({
            ok: true,
            json: () => Promise.resolve({ results: [] })
        });

        render(Page);

        await waitFor(() => {
            expect(screen.getByText(/No applications found/)).toBeInTheDocument();
            expect(screen.getByText(/No servers found/)).toBeInTheDocument();
            expect(screen.getByText(/No languages configured/)).toBeInTheDocument();
            expect(screen.getByText(/No datastores configured/)).toBeInTheDocument();
        });
    });

    it('should handle retry functionality', async () => {
        let callCount = 0;
        mockFetch.mockImplementation(() => {
            callCount++;
            if (callCount === 1) {
                return Promise.reject(new Error('Network error'));
            }
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ results: [] })
            });
        });

        render(Page);

        // Wait for error to appear
        await waitFor(() => {
            expect(screen.getByText('Network error')).toBeInTheDocument();
        });

        // Click retry button
        const retryButton = screen.getByRole('button', { name: 'Retry' });
        await retryButton.click();

        // Should show loading again and then success
        await waitFor(() => {
            expect(screen.getByText('Recent Applications')).toBeInTheDocument();
        });

        expect(callCount).toBe(6); // Initial 5 calls + 5 retry calls
    });

    it('should apply correct CSS classes for badges', async () => {
        const mockApplications = {
            results: [
                {
                    id: '1',
                    name: 'Prod App',
                    lifecycle_stage: 'production',
                    criticality: 'high'
                }
            ]
        };

        mockFetch.mockImplementation((url) => {
            if (url.includes('applications')) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockApplications)
                });
            }
            return Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ results: [] })
            });
        });

        render(Page);

        await waitFor(() => {
            const productionBadge = screen.getByText('production');
            const criticalityBadge = screen.getByText('high');
            
            expect(productionBadge).toHaveClass('badge', 'badge-production');
            expect(criticalityBadge).toHaveClass('badge', 'badge-high');
        });
    });
});
