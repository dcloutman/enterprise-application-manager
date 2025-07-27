// API client configuration
const API_BASE = '/api';

export interface Application {
    id: string;
    name: string;
    description?: string;
    lifecycle_stage: string;
    criticality: string;
    business_owner?: string;
    technical_owner?: string;
    primary_server_hostname?: string;
}

export interface Server {
    id: number;
    hostname: string;
    name: string;
    environment_type: string;
    ip_address?: string;
    operating_system?: string;
    os_version?: string;
    cpu_cores?: number;
    memory_gb?: number;
    storage_gb?: number;
}

export interface Language {
    id: number;
    name: string;
    is_active?: boolean;
}

export interface Datastore {
    id: number;
    name: string;
    datastore_type: string;
}

export interface DashboardStats {
    total_applications: number;
    active_applications: number;
    by_lifecycle_stage?: Array<{
        lifecycle_stage: string;
        count: number;
    }>;
    by_criticality?: Array<{
        criticality: string;
        count: number;
    }>;
}

export interface ApiResponse<T> {
    results: T[];
    count?: number;
    next?: string;
    previous?: string;
}

class ApiClient {
    private async request(endpoint: string, options: RequestInit = {}) {
        const url = `${API_BASE}${endpoint}`;
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }

        return response.json();
    }

    // Tasks
    async getTasks(): Promise<Task[]> {
        return this.request('/tasks/');
    }

    async createTask(task: Partial<Task>): Promise<Task> {
        return this.request('/tasks/', {
            method: 'POST',
            body: JSON.stringify(task),
        });
    }

    async updateTask(id: number, task: Partial<Task>): Promise<Task> {
        return this.request(`/tasks/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify(task),
        });
    }

    async deleteTask(id: number): Promise<void> {
        return this.request(`/tasks/${id}/`, {
            method: 'DELETE',
        });
    }

    // Projects
    async getProjects(): Promise<Project[]> {
        return this.request('/projects/');
    }

    async createProject(project: Partial<Project>): Promise<Project> {
        return this.request('/projects/', {
            method: 'POST',
            body: JSON.stringify(project),
        });
    }

    async updateProject(id: number, project: Partial<Project>): Promise<Project> {
        return this.request(`/projects/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify(project),
        });
    }

    async deleteProject(id: number): Promise<void> {
        return this.request(`/projects/${id}/`, {
            method: 'DELETE',
        });
    }
}

export const api = new ApiClient();
