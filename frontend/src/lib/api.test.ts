import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api } from '../lib/api';
import type { Task, Project } from '../lib/api';

// Mock fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('API Client', () => {
    beforeEach(() => {
        mockFetch.mockClear();
    });

    describe('Tasks API', () => {
        it('should fetch tasks successfully', async () => {
            const mockTasks: Task[] = [
                {
                    id: 1,
                    title: 'Test Task',
                    description: 'Test Description',
                    completed: false,
                    created_at: '2025-01-01T00:00:00Z',
                    updated_at: '2025-01-01T00:00:00Z'
                }
            ];

            mockFetch.mockResolvedValue({
                ok: true,
                json: () => Promise.resolve(mockTasks)
            });

            const tasks = await api.getTasks();

            expect(mockFetch).toHaveBeenCalledWith('/api/tasks/', {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            expect(tasks).toEqual(mockTasks);
        });

        it('should create a task successfully', async () => {
            const newTask: Partial<Task> = {
                title: 'New Task',
                description: 'New Description',
                completed: false
            };

            const createdTask: Task = {
                id: 2,
                ...newTask as Task,
                created_at: '2025-01-01T00:00:00Z',
                updated_at: '2025-01-01T00:00:00Z'
            };

            mockFetch.mockResolvedValue({
                ok: true,
                json: () => Promise.resolve(createdTask)
            });

            const result = await api.createTask(newTask);

            expect(mockFetch).toHaveBeenCalledWith('/api/tasks/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newTask)
            });
            expect(result).toEqual(createdTask);
        });

        it('should update a task successfully', async () => {
            const taskId = 1;
            const updates: Partial<Task> = {
                title: 'Updated Task',
                completed: true
            };

            const updatedTask: Task = {
                id: taskId,
                title: 'Updated Task',
                description: 'Test Description',
                completed: true,
                created_at: '2025-01-01T00:00:00Z',
                updated_at: '2025-01-01T01:00:00Z'
            };

            mockFetch.mockResolvedValue({
                ok: true,
                json: () => Promise.resolve(updatedTask)
            });

            const result = await api.updateTask(taskId, updates);

            expect(mockFetch).toHaveBeenCalledWith('/api/tasks/1/', {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updates)
            });
            expect(result).toEqual(updatedTask);
        });

        it('should delete a task successfully', async () => {
            const taskId = 1;

            mockFetch.mockResolvedValue({
                ok: true,
                json: () => Promise.resolve()
            });

            await api.deleteTask(taskId);

            expect(mockFetch).toHaveBeenCalledWith('/api/tasks/1/', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        });

        it('should handle API errors for tasks', async () => {
            mockFetch.mockResolvedValue({
                ok: false,
                status: 404
            });

            await expect(api.getTasks()).rejects.toThrow('API request failed: 404');
        });
    });

    describe('Projects API', () => {
        it('should fetch projects successfully', async () => {
            const mockProjects: Project[] = [
                {
                    id: 1,
                    name: 'Test Project',
                    description: 'Test Description',
                    created_at: '2025-01-01T00:00:00Z',
                    updated_at: '2025-01-01T00:00:00Z'
                }
            ];

            mockFetch.mockResolvedValue({
                ok: true,
                json: () => Promise.resolve(mockProjects)
            });

            const projects = await api.getProjects();

            expect(mockFetch).toHaveBeenCalledWith('/api/projects/', {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            expect(projects).toEqual(mockProjects);
        });

        it('should create a project successfully', async () => {
            const newProject: Partial<Project> = {
                name: 'New Project',
                description: 'New Description'
            };

            const createdProject: Project = {
                id: 2,
                ...newProject as Project,
                created_at: '2025-01-01T00:00:00Z',
                updated_at: '2025-01-01T00:00:00Z'
            };

            mockFetch.mockResolvedValue({
                ok: true,
                json: () => Promise.resolve(createdProject)
            });

            const result = await api.createProject(newProject);

            expect(mockFetch).toHaveBeenCalledWith('/api/projects/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newProject)
            });
            expect(result).toEqual(createdProject);
        });

        it('should update a project successfully', async () => {
            const projectId = 1;
            const updates: Partial<Project> = {
                name: 'Updated Project'
            };

            const updatedProject: Project = {
                id: projectId,
                name: 'Updated Project',
                description: 'Test Description',
                created_at: '2025-01-01T00:00:00Z',
                updated_at: '2025-01-01T01:00:00Z'
            };

            mockFetch.mockResolvedValue({
                ok: true,
                json: () => Promise.resolve(updatedProject)
            });

            const result = await api.updateProject(projectId, updates);

            expect(mockFetch).toHaveBeenCalledWith('/api/projects/1/', {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updates)
            });
            expect(result).toEqual(updatedProject);
        });

        it('should delete a project successfully', async () => {
            const projectId = 1;

            mockFetch.mockResolvedValue({
                ok: true,
                json: () => Promise.resolve()
            });

            await api.deleteProject(projectId);

            expect(mockFetch).toHaveBeenCalledWith('/api/projects/1/', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        });

        it('should handle API errors for projects', async () => {
            mockFetch.mockResolvedValue({
                ok: false,
                status: 500
            });

            await expect(api.getProjects()).rejects.toThrow('API request failed: 500');
        });
    });

    describe('Error handling', () => {
        it('should handle network errors', async () => {
            mockFetch.mockRejectedValue(new Error('Network error'));

            await expect(api.getTasks()).rejects.toThrow('Network error');
        });

        it('should handle invalid JSON responses', async () => {
            mockFetch.mockResolvedValue({
                ok: true,
                json: () => Promise.reject(new Error('Invalid JSON'))
            });

            await expect(api.getTasks()).rejects.toThrow('Invalid JSON');
        });
    });

    describe('Request configuration', () => {
        it('should include correct headers', async () => {
            mockFetch.mockResolvedValue({
                ok: true,
                json: () => Promise.resolve([])
            });

            await api.getTasks();

            expect(mockFetch).toHaveBeenCalledWith(
                expect.any(String),
                expect.objectContaining({
                    headers: expect.objectContaining({
                        'Content-Type': 'application/json'
                    })
                })
            );
        });

        it('should use correct base URL', async () => {
            mockFetch.mockResolvedValue({
                ok: true,
                json: () => Promise.resolve([])
            });

            await api.getTasks();

            expect(mockFetch).toHaveBeenCalledWith(
                '/api/tasks/',
                expect.any(Object)
            );
        });
    });
});
