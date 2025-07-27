import { describe, it, expect, vi } from 'vitest';

// Test utilities and helpers for the frontend test suite

/**
 * Mock API response helper
 */
export function mockApiResponse(data: any, status = 200) {
    return Promise.resolve({
        ok: status >= 200 && status < 300,
        status,
        json: () => Promise.resolve(data),
        text: () => Promise.resolve(JSON.stringify(data))
    });
}

/**
 * Mock API error helper
 */
export function mockApiError(status: number, message?: string) {
    return Promise.resolve({
        ok: false,
        status,
        statusText: message || 'Error',
        json: () => Promise.reject(new Error('Invalid JSON')),
        text: () => Promise.resolve('')
    });
}

/**
 * Mock fetch with specific responses for different endpoints
 */
export function setupMockFetch(responses: Record<string, any>) {
    const mockFetch = vi.fn();
    
    mockFetch.mockImplementation((url: string) => {
        for (const [pattern, response] of Object.entries(responses)) {
            if (url.includes(pattern)) {
                if (response instanceof Error) {
                    return Promise.reject(response);
                }
                return mockApiResponse(response);
            }
        }
        
        // Default response
        return mockApiResponse({ results: [] });
    });
    
    global.fetch = mockFetch;
    return mockFetch;
}

/**
 * Sample data for testing
 */
export const sampleData = {
    dashboardStats: {
        total_applications: 25,
        active_applications: 20,
        by_lifecycle_stage: [
            { lifecycle_stage: 'production', count: 10 },
            { lifecycle_stage: 'development', count: 8 },
            { lifecycle_stage: 'testing', count: 2 }
        ]
    },
    
    applications: {
        results: [
            {
                id: '1',
                name: 'Customer Portal',
                description: 'Main customer-facing application',
                lifecycle_stage: 'production',
                criticality: 'high',
                business_owner: 'Marketing Team',
                primary_server_hostname: 'web-prod-01'
            },
            {
                id: '2',
                name: 'Internal Dashboard',
                description: 'Employee dashboard application',
                lifecycle_stage: 'development',
                criticality: 'medium',
                business_owner: 'HR Department',
                primary_server_hostname: 'web-dev-01'
            }
        ]
    },
    
    servers: {
        results: [
            {
                id: 1,
                hostname: 'web-prod-01',
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
                hostname: 'db-prod-01',
                name: 'Production Database',
                ip_address: '10.0.1.101',
                environment_type: 'production',
                operating_system: 'Ubuntu',
                os_version: '22.04',
                cpu_cores: 16,
                memory_gb: 64
            }
        ]
    },
    
    languages: {
        results: [
            { id: 1, name: 'Python' },
            { id: 2, name: 'JavaScript' },
            { id: 3, name: 'TypeScript' }
        ]
    },
    
    datastores: {
        results: [
            { id: 1, name: 'PostgreSQL', datastore_type: 'relational' },
            { id: 2, name: 'Redis', datastore_type: 'cache' },
            { id: 3, name: 'Elasticsearch', datastore_type: 'search' }
        ]
    }
};

/**
 * Wait for async operations to complete
 */
export function waitForAsync(ms = 0) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Test API client error handling
 */
describe('Test Utilities', () => {
    it('should create mock API responses correctly', () => {
        const mockResponse = mockApiResponse({ test: 'data' });
        
        expect(mockResponse).resolves.toEqual({
            ok: true,
            status: 200,
            json: expect.any(Function),
            text: expect.any(Function)
        });
    });
    
    it('should create mock API errors correctly', () => {
        const mockError = mockApiError(404, 'Not Found');
        
        expect(mockError).resolves.toEqual({
            ok: false,
            status: 404,
            statusText: 'Not Found',
            json: expect.any(Function),
            text: expect.any(Function)
        });
    });
    
    it('should setup mock fetch with multiple endpoints', () => {
        const mockFetch = setupMockFetch({
            'applications': sampleData.applications,
            'servers': sampleData.servers
        });
        
        expect(mockFetch).toBeDefined();
        expect(global.fetch).toBe(mockFetch);
    });
});
