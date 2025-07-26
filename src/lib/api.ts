// API client configuration
const API_BASE = '/api';

export interface Task {
    id: number;
    title: string;
    description: string;
    completed: boolean;
    created_at: string;
    updated_at: string;
}

export interface Project {
    id: number;
    name: string;
    description: string;
    created_at: string;
    updated_at: string;
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
