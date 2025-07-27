Development Guide
=================

This guide provides information for developers working on the Enterprise Application Tracker.

.. toctree::
   :maxdepth: 2

   testing

Development Environment Setup
-----------------------------

**Prerequisites**

- Docker and Docker Compose
- Git
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- VS Code or similar IDE

**Quick Start**

The Enterprise Application Tracker includes a comprehensive command-line tool called `eatcmd` that simplifies development and deployment operations. This tool replaces manual Docker commands and provides a unified interface for managing the application lifecycle.

.. code-block:: bash

    # Clone the repository
    git clone https://github.com/your-org/app-tracker.git
    cd app-tracker
    
    # Run initial project setup (creates directories, sets permissions, builds images)
    ./bin/eatcmd setup
    
    # Start the development environment
    ./bin/eatcmd start
    
    # Check container status
    ./bin/eatcmd status
    
    # Run database migrations and create superuser
    ./bin/eatcmd shell
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py loaddata sample_data.json
    exit

**Development URLs**

When the application is running, you can access these development interfaces:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/
- **Admin Interface**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/docs/

You can check if all services are running properly by using the `eatcmd status` command, which shows the current state of all application containers.

Architecture Overview
---------------------

**System Architecture**

.. code-block::

    ┌─────────────────────────────────────────────────────────────┐
    │                    Frontend Layer                           │
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
    │  │  SvelteKit  │  │   Vite     │  │     TypeScript      │ │
    │  │   Pages     │  │   Build    │  │    Components      │ │
    │  └─────────────┘  └─────────────┘  └─────────────────────┘ │
    └─────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST API
                                    ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    Backend Layer                            │
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
    │  │   Django    │  │    DRF      │  │   Authentication   │ │
    │  │   Models    │  │ Serializers │  │   & Permissions    │ │
    │  └─────────────┘  └─────────────┘  └─────────────────────┘ │
    └─────────────────────────────────────────────────────────────┘
                                    │
                                    │ ORM/SQL
                                    ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    Data Layer                              │
    │  ┌─────────────┐                  ┌─────────────────────┐ │
    │  │   MySQL     │                  │    File Storage    │ │
    │  │  Database   │                  │      Media         │ │
    │  └─────────────┘                  └─────────────────────┘ │
    └─────────────────────────────────────────────────────────────┘

**Component Relationships**

.. code-block::

    Applications ──┐
                   ├─── Servers ──── DataStores
    Languages ─────┤
                   ├─── CloudPlatforms
    Environments ──┘
    
    Users ──── UserProfiles ──── RecordPermissions
           └── ActivityLogs

**Technology Stack**

**Backend Technologies**
- **Django 4.2+**: Web framework
- **Django REST Framework**: API development
- **MySQL 8.4**: Primary database
- **Gunicorn**: WSGI server

**Frontend Technologies**
- **SvelteKit**: Frontend framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Utility-first CSS
- **Chart.js**: Data visualization

**DevOps Technologies**
- **Docker**: Containerization
- **Docker Compose**: Local development
- **Docker Swarm**: Production deployment
- **Nginx**: Reverse proxy and load balancer

Project Structure
-----------------

.. code-block::

    app-tracker/
    ├── backend/                 # Django backend
    │   ├── config/             # Django settings
    │   ├── apps/
    │   │   ├── inventory/      # Main application logic
    │   │   │   ├── models.py   # Data models
    │   │   │   ├── views.py    # API views
    │   │   │   ├── serializers.py # DRF serializers
    │   │   │   ├── urls.py     # URL routing
    │   │   │   └── permissions.py # Custom permissions
    │   │   └── users/          # User management
    │   ├── requirements.txt    # Python dependencies
    │   └── manage.py          # Django management
    ├── frontend/               # SvelteKit frontend
    │   ├── src/
    │   │   ├── routes/        # SvelteKit pages
    │   │   ├── lib/           # Shared components
    │   │   ├── stores/        # State management
    │   │   └── types/         # TypeScript types
    │   ├── static/            # Static assets
    │   ├── package.json       # Node.js dependencies
    │   └── vite.config.js     # Vite configuration
    ├── docker-compose.yml     # Development setup
    ├── docker-compose.prod.yml # Production setup
    ├── docs/                  # Documentation
    └── README.md             # Project overview

Backend Development
-------------------

**Django Models**

Follow these patterns for model development:

.. code-block:: python

    from django.db import models
    from django.contrib.auth.models import User
    
    class BaseModel(models.Model):
        """Base model with common fields"""
        created_date = models.DateTimeField(auto_now_add=True)
        modified_date = models.DateTimeField(auto_now=True)
        created_by = models.ForeignKey(
            User,
            on_delete=models.SET_NULL,
            null=True,
            related_name='%(app_label)s_%(class)s_created'
        )
        modified_by = models.ForeignKey(
            User,
            on_delete=models.SET_NULL,
            null=True,
            related_name='%(app_label)s_%(class)s_modified'
        )
        is_active = models.BooleanField(default=True)
        
        class Meta:
            abstract = True
    
    class Application(BaseModel):
        name = models.CharField(max_length=100, unique=True)
        description = models.TextField(blank=True)
        url = models.URLField(blank=True)
        business_owner = models.CharField(max_length=100, blank=True)
        technical_owner = models.CharField(max_length=100, blank=True)
        cost_center = models.CharField(max_length=50, blank=True)
        languages = models.ManyToManyField(Language, blank=True)
        
        # System manager protected fields
        system_manager_notes = models.TextField(blank=True)
        
        class Meta:
            ordering = ['name']
        
        def __str__(self):
            return self.name

**API Views**

Use Django REST Framework viewsets:

.. code-block:: python

    from rest_framework import viewsets, permissions
    from rest_framework.decorators import action
    from rest_framework.response import Response
    from .models import Application
    from .serializers import ApplicationSerializer
    from .permissions import CanViewSystemNotes
    
    class ApplicationViewSet(viewsets.ModelViewSet):
        queryset = Application.objects.all()
        serializer_class = ApplicationSerializer
        permission_classes = [permissions.IsAuthenticated]
        filterset_fields = ['is_active', 'languages']
        search_fields = ['name', 'description', 'business_owner']
        ordering_fields = ['name', 'created_date', 'modified_date']
        
        def get_queryset(self):
            """Filter queryset based on user permissions"""
            queryset = super().get_queryset()
            
            if not self.request.user.profile.can_view_system_notes():
                # Hide system_manager_notes for non-privileged users
                queryset = queryset.defer('system_manager_notes')
            
            return queryset
        
        def perform_create(self, serializer):
            """Set created_by when creating objects"""
            serializer.save(created_by=self.request.user)
        
        def perform_update(self, serializer):
            """Set modified_by when updating objects"""
            serializer.save(modified_by=self.request.user)
        
        @action(detail=True, methods=['post'])
        def assign_languages(self, request, pk=None):
            """Custom action to assign languages to application"""
            application = self.get_object()
            language_ids = request.data.get('language_ids', [])
            
            if not isinstance(language_ids, list):
                return Response(
                    {'error': 'language_ids must be a list'}, 
                    status=400
                )
            
            languages = Language.objects.filter(id__in=language_ids)
            application.languages.set(languages)
            
            serializer = self.get_serializer(application)
            return Response(serializer.data)

**Serializers**

Create efficient serializers with proper validation:

.. code-block:: python

    from rest_framework import serializers
    from .models import Application, Language
    
    class ApplicationSerializer(serializers.ModelSerializer):
        languages = serializers.PrimaryKeyRelatedField(
            many=True,
            queryset=Language.objects.all(),
            required=False
        )
        language_names = serializers.SerializerMethodField()
        system_manager_notes = serializers.SerializerMethodField()
        
        class Meta:
            model = Application
            fields = [
                'id', 'name', 'description', 'url',
                'business_owner', 'technical_owner', 'cost_center',
                'languages', 'language_names', 'system_manager_notes',
                'is_active', 'created_date', 'modified_date'
            ]
            read_only_fields = ['created_date', 'modified_date']
        
        def get_language_names(self, obj):
            """Return language names for display"""
            return [lang.name for lang in obj.languages.all()]
        
        def get_system_manager_notes(self, obj):
            """Return system notes only for authorized users"""
            request = self.context.get("request")
            if request and hasattr(request.user, "profile"):
                if request.user.profile.can_view_system_notes():
                    return obj.system_manager_notes
            return None
        
        def validate_name(self, value):
            """Custom validation for application name"""
            if len(value) < 3:
                raise serializers.ValidationError(
                    "Application name must be at least 3 characters long."
                )
            return value.strip()
        
        def validate_url(self, value):
            """Validate URL format"""
            if value and not value.startswith(("http://", "https://")):
                raise serializers.ValidationError(
                    "URL must start with http:// or https://"
                )
            return value

**Custom Permissions**

Implement role-based permissions:

.. code-block:: python

    from rest_framework.permissions import BasePermission
    
    class CanViewSystemNotes(BasePermission):
        """Permission to view system manager notes"""
        
        def has_permission(self, request, view):
            if not request.user.is_authenticated:
                return False
            
            try:
                return request.user.profile.can_view_system_notes()
            except AttributeError:
                return False
    
    class CanEditRecord(BasePermission):
        """Permission to edit specific records"""
        
        def has_object_permission(self, request, view, obj):
            if not request.user.is_authenticated:
                return False
            
            # Read permissions for authenticated users
            if request.method in ["GET", "HEAD", "OPTIONS"]:
                return True
            
            # Write permissions based on role and ownership
            user_profile = request.user.profile
            
            if user_profile.role in ["application_admin", "systems_manager"]:
                return True
            elif user_profile.role == "technician":
                # Technicians can edit records they created or are assigned to
                return (obj.created_by == request.user or 
                       self.user_has_record_permission(request.user, obj))
            
            return False
        
        def user_has_record_permission(self, user, obj):
            """Check if user has specific permission for this record"""
            from .models import RecordPermission
            return RecordPermission.objects.filter(
                user=user,
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
                permission_type="edit",
                is_active=True
            ).exists()

Frontend Development
--------------------

**SvelteKit Project Structure**

.. code-block::

    frontend/src/
    ├── routes/                 # SvelteKit routes (pages)
    │   ├── +layout.svelte     # Root layout
    │   ├── +page.svelte       # Home page
    │   ├── login/             # Login page
    │   ├── dashboard/         # Dashboard pages
    │   ├── applications/      # Application management
    │   ├── servers/           # Server management
    │   └── admin/             # Admin pages
    ├── lib/                   # Shared components and utilities
    │   ├── components/        # Reusable UI components
    │   ├── stores/           # Svelte stores (state management)
    │   ├── api/              # API client functions
    │   ├── types/            # TypeScript type definitions
    │   └── utils/            # Utility functions
    ├── static/               # Static assets
    └── app.html              # HTML template

**TypeScript Types**

Define strong types for API data:

.. code-block:: typescript

    // src/lib/types/api.ts
    export interface User {
        id: number;
        username: string;
        email: string;
        first_name: string;
        last_name: string;
        is_active: boolean;
        profile?: UserProfile;
    }
    
    export interface UserProfile {
        role: "business_user" | "business_manager" | "technician" | 
              "systems_manager" | "application_admin";
        department: string;
        phone_number: string;
        permissions: UserPermissions;
    }
    
    export interface UserPermissions {
        can_create_applications: boolean;
        can_edit_applications: boolean;
        can_delete_applications: boolean;
        can_view_system_notes: boolean;
        can_manage_users: boolean;
    }
    
    export interface Application {
        id: number;
        name: string;
        description: string;
        url: string;
        business_owner: string;
        technical_owner: string;
        cost_center: string;
        languages: number[];
        language_names: string[];
        system_manager_notes?: string;
        is_active: boolean;
        created_date: string;
        modified_date: string;
    }

**API Client**

Create a typed API client:

.. code-block:: typescript

    // src/lib/api/client.ts
    import type { User, Application } from '$lib/types/api';
    
    const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
    
    class APIError extends Error {
        constructor(public status: number, message: string, public data?: any) {
            super(message);
        }
    }
    
    class APIClient {
        private token: string | null = null;
        
        setToken(token: string) {
            this.token = token;
        }
        
        private async request<T>(
            endpoint: string, 
            options: RequestInit = {}
        ): Promise<T> {
            const url = `${API_BASE}${endpoint}`;
            
            const headers: HeadersInit = {
                "Content-Type": "application/json",
                ...options.headers,
            };
            
            if (this.token) {
                headers["Authorization"] = `Bearer ${this.token}`;
            }
            
            const response = await fetch(url, {
                ...options,
                headers,
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new APIError(
                    response.status,
                    errorData?.message || response.statusText,
                    errorData
                );
            }
            
            return response.json();
        }
        
        // Authentication
        async login(username: string, password: string): Promise<{token: string, user: User}> {
            return this.request("/auth/login/", {
                method: "POST",
                body: JSON.stringify({ username, password }),
            });
        }
        
        async getCurrentUser(): Promise<User> {
            return this.request("/auth/user/");
        }
        
        // Applications
        async getApplications(params?: {
            page?: number;
            search?: string;
            is_active?: boolean;
        }): Promise<{results: Application[], count: number}> {
            const query = new URLSearchParams();
            if (params) {
                Object.entries(params).forEach(([key, value]) => {
                    if (value !== undefined) {
                        query.append(key, String(value));
                    }
                });
            }
            
            const endpoint = `/applications/${query.toString() ? `?${query}` : ''}`;
            return this.request(endpoint);
        }
        
        async getApplication(id: number): Promise<Application> {
            return this.request(`/applications/${id}/`);
        }
        
        async createApplication(data: Partial<Application>): Promise<Application> {
            return this.request("/applications/", {
                method: "POST",
                body: JSON.stringify(data),
            });
        }
        
        async updateApplication(id: number, data: Partial<Application>): Promise<Application> {
            return this.request(`/applications/${id}/`, {
                method: "PATCH",
                body: JSON.stringify(data),
            });
        }
        
        async deleteApplication(id: number): Promise<void> {
            return this.request(`/applications/${id}/`, {
                method: "DELETE",
            });
        }
    }
    
    export const apiClient = new APIClient();

**Svelte Stores**

Manage application state with stores:

.. code-block:: typescript

    // src/lib/stores/auth.ts
    import { writable } from 'svelte/store';
    import { browser } from '$app/environment';
    import type { User } from '$lib/types/api';
    import { apiClient } from '$lib/api/client';
    
    interface AuthState {
        isAuthenticated: boolean;
        user: User | null;
        token: string | null;
        loading: boolean;
    }
    
    const initialState: AuthState = {
        isAuthenticated: false,
        user: null,
        token: null,
        loading: true,
    };
    
    function createAuthStore() {
        const { subscribe, set, update } = writable<AuthState>(initialState);
        
        return {
            subscribe,
            
            async init() {
                if (!browser) return;
                
                const token = localStorage.getItem("auth_token");
                if (token) {
                    try {
                        apiClient.setToken(token);
                        const user = await apiClient.getCurrentUser();
                        
                        set({
                            isAuthenticated: true,
                            user,
                            token,
                            loading: false,
                        });
                    } catch (error) {
                        localStorage.removeItem('auth_token');
                        set({ ...initialState, loading: false });
                    }
                } else {
                    set({ ...initialState, loading: false });
                }
            },
            
            async login(username: string, password: string) {
                try {
                    const { token, user } = await apiClient.login(username, password);
                    
                    if (browser) {
                        localStorage.setItem('auth_token', token);
                    }
                    
                    apiClient.setToken(token);
                    
                    set({
                        isAuthenticated: true,
                        user,
                        token,
                        loading: false,
                    });
                    
                    return { success: true };
                } catch (error) {
                    return { 
                        success: false, 
                        error: error instanceof Error ? error.message : 'Login failed' 
                    };
                }
            },
            
            logout() {
                if (browser) {
                    localStorage.removeItem('auth_token');
                }
                
                apiClient.setToken('');
                
                set({
                    isAuthenticated: false,
                    user: null,
                    token: null,
                    loading: false,
                });
            },
        };
    }
    
    export const auth = createAuthStore();

**Reusable Components**

Create consistent UI components:

.. code-block:: html

    <!-- src/lib/components/DataTable.svelte -->
    <script lang="ts">
        import type { ComponentType } from 'svelte';
        
        export let data: any[] = [];
        export let columns: Array<{
            key: string;
            label: string;
            sortable?: boolean;
            component?: ComponentType;
        }> = [];
        export let loading = false;
        export let onSort: ((key: string) => void) | undefined = undefined;
        export let onRowClick: ((item: any) => void) | undefined = undefined;
        
        let sortColumn = '';
        let sortDirection: "asc" | "desc" = "asc";
        
        function handleSort(key: string) {
            if (!onSort) return;
            
            if (sortColumn === key) {
                sortDirection = sortDirection === "asc" ? "desc" : "asc";
            } else {
                sortColumn = key;
                sortDirection = "asc";
            }
            
            onSort(`${sortDirection === "desc" ? "-" : ""}${key}`);
        }
    </script>
    
    <div class="overflow-x-auto">
        <table class="min-w-full bg-white border border-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    {#each columns as column}
                        <th 
                            class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                            class:cursor-pointer={column.sortable}
                            on:click={() => column.sortable && handleSort(column.key)}
                        >
                            <div class="flex items-center space-x-1">
                                <span>{column.label}</span>
                                {#if column.sortable && sortColumn === column.key}
                                    <span class="text-gray-400">
                                        # You can use alternation operator with pipe character
        if sortDirection === "desc" ? "↓" : "↑"
                                    </span>
                                {/if}
                            </div>
                        </th>
                    {/each}
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
                {#if loading}
                    <tr>
                        <td colspan={columns.length} class="px-6 py-4 text-center text-gray-500">
                            Loading...
                        </td>
                    </tr>
                {:else if data.length === 0}
                    <tr>
                        <td colspan={columns.length} class="px-6 py-4 text-center text-gray-500">
                            No data available
                        </td>
                    </tr>
                {:else}
                    {#each data as item, index}
                        <tr 
                            class="hover:bg-gray-50"
                            class:cursor-pointer={onRowClick}
                            on:click={() => onRowClick?.(item)}
                        >
                            {#each columns as column}
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    {#if column.component}
                                        <svelte:component 
                                            this={column.component} 
                                            value={item[column.key]} 
                                            {item} 
                                        />
                                    {:else}
                                        {item[column.key] || '-'}
                                    {/if}
                                </td>
                            {/each}
                        </tr>
                    {/each}
                {/if}
            </tbody>
        </table>
    </div>

Testing
-------

**Backend Testing**

Use Django's test framework with pytest:

.. code-block:: python

    # tests/test_models.py
    import pytest
    from django.contrib.auth.models import User
    from apps.inventory.models import Application, UserProfile
    
    @pytest.mark.django_db
    class TestApplicationModel:
        def test_create_application(self):
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123'
            )
            
            app = Application.objects.create(
                name='Test App',
                description='Test application',
                created_by=user
            )
            
            assert app.name == 'Test App'
            assert app.created_by == user
            assert app.is_active is True
        
        def test_application_str(self):
            app = Application(name='Test App')
            assert str(app) == 'Test App'
    
    # tests/test_views.py
    import pytest
    from rest_framework.test import APIClient
    from django.contrib.auth.models import User
    from apps.inventory.models import Application, UserProfile
    
    @pytest.mark.django_db
    class TestApplicationAPI:
        def setup_method(self):
            self.client = APIClient()
            self.user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123'
            )
            self.profile = UserProfile.objects.create(
                user=self.user,
                role='technician'
            )
            self.client.force_authenticate(user=self.user)
        
        def test_list_applications(self):
            Application.objects.create(
                name='Test App',
                created_by=self.user
            )
            
            response = self.client.get('/api/applications/')
            
            assert response.status_code == 200
            assert len(response.data['results']) == 1
            assert response.data['results'][0]['name'] == 'Test App'
        
        def test_create_application(self):
            data = {
                'name': 'New App',
                'description': 'New test application'
            }
            
            response = self.client.post('/api/applications/', data)
            
            assert response.status_code == 201
            assert Application.objects.filter(name='New App').exists()

**Frontend Testing**

Use Vitest and Testing Library:

.. code-block:: typescript

    // src/lib/components/DataTable.test.ts
    import { render, screen } from '@testing-library/svelte';
    import { expect, test } from 'vitest';
    import DataTable from './DataTable.svelte';
    
    test('renders empty state when no data', () => {
        render(DataTable, {
            props: {
                data: [],
                columns: [
                    { key: 'name', label: 'Name' },
                    { key: 'description', label: 'Description' }
                ]
            }
        });
        
        expect(screen.getByText('No data available')).toBeInTheDocument();
    });
    
    test('renders data rows', () => {
        const data = [
            { name: 'App 1', description: 'First app' },
            { name: 'App 2', description: 'Second app' }
        ];
        
        render(DataTable, {
            props: {
                data,
                columns: [
                    { key: 'name', label: 'Name' },
                    { key: 'description', label: 'Description' }
                ]
            }
        });
        
        expect(screen.getByText('App 1')).toBeInTheDocument();
        expect(screen.getByText('App 2')).toBeInTheDocument();
    });

**Test Configuration**

.. code-block:: javascript

    // vitest.config.js
    import { sveltekit } from '@sveltejs/kit/vite';
    import { defineConfig } from 'vitest/config';
    
    export default defineConfig({
        plugins: [sveltekit()],
        test: {
            include: ['src/**/*.{test,spec}.{js,ts}'],
            environment: 'jsdom',
            setupFiles: ['src/test-setup.ts']
        }
    });

Coding Standards
----------------

**Python Code Style**

Follow PEP 8 with these additions:

.. code-block:: python

    # Use type hints
    from typing import List, Optional, Dict, Any
    
    def get_applications(user_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get applications for a specific user.
        
        Args:
            user_id: ID of the user
            active_only: Whether to return only active applications
            
        Returns:
            List of application dictionaries
            
        Raises:
            User.DoesNotExist: If user doesn't exist
        """
        pass
    
    # Use dataclasses for data structures
    from dataclasses import dataclass
    
    @dataclass
    class ApplicationSummary:
        id: int
        name: str
        server_count: int
        is_active: bool

**TypeScript Code Style**

.. code-block:: typescript

    // Use strict TypeScript settings
    // Always define interfaces for API responses
    interface APIResponse<T> {
        status: 'success' | 'error';
        data?: T;
        error?: {
            code: string;
            message: string;
            details?: Record<string, string[]>;
        };
    }
    
    // Use const assertions for literal types
    const USER_ROLES = ["business_user", "technician", "systems_manager"] as const;
    type UserRole = typeof USER_ROLES[number];
    
    // Prefer async/await over promises
    async function fetchApplications(): Promise<Application[]> {
        try {
            const response = await apiClient.getApplications();
            return response.results;
        } catch (error) {
            console.error("Failed to fetch applications:", error);
            throw error;
        }
    }

**Git Workflow**

Use conventional commits:

.. code-block::

    feat: add user role management interface
    fix: resolve authentication token expiration issue
    docs: update API documentation for applications endpoint
    test: add unit tests for application model
    refactor: simplify permission checking logic
    style: format code according to style guide
    chore: update dependency versions

**Branch Naming**

.. code-block::

    feature/user-role-management
    bugfix/auth-token-expiration
    hotfix/security-vulnerability
    docs/api-documentation-update

Database Development
--------------------

**Migrations**

Always create migrations for model changes using the development tools:

.. code-block:: bash

    # Enter the application shell to run Django commands
    ./bin/eatcmd shell
    
    # Create migration
    python manage.py makemigrations --name=add_user_profile_model
    
    # Review migration before applying
    python manage.py sqlmigrate inventory 0001
    
    # Apply migration
    python manage.py migrate
    
    # Exit the shell
    exit

**Custom Migration Example**

.. code-block:: python

    # migrations/0002_populate_user_profiles.py
    from django.db import migrations
    from django.contrib.auth.models import User
    
    def create_user_profiles(apps, schema_editor):
        UserProfile = apps.get_model('inventory', 'UserProfile')
        
        for user in User.objects.all():
            UserProfile.objects.get_or_create(
                user=user,
                defaults={"role": "business_user"}
            )
    
    def reverse_create_user_profiles(apps, schema_editor):
        UserProfile = apps.get_model('inventory', 'UserProfile')
        UserProfile.objects.all().delete()
    
    class Migration(migrations.Migration):
        dependencies = [
            ("inventory", "0001_initial"),
        ]
        
        operations = [
            migrations.RunPython(
                create_user_profiles,
                reverse_create_user_profiles
            ),
        ]

Contributing
------------

**Pull Request Process**

1. **Create Feature Branch**
   
   .. code-block:: bash
   
       git checkout main
       git pull origin main
       git checkout -b feature/your-feature-name

2. **Make Changes**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Changes**
   
   Use the integrated testing commands to verify your changes:
   
   .. code-block:: bash
   
       # Run all tests to ensure nothing is broken
       ./bin/eatcmd test
       
       # Run backend tests specifically
       ./bin/eatcmd test --backend-only
       
       # Run frontend tests with coverage
       ./bin/eatcmd test --frontend-only --coverage

4. **Submit Pull Request**
   - Create PR against main branch
   - Include detailed description
   - Link related issues
   - Request code review

**Code Review Guidelines**

**For Reviewers:**
- Check code style and standards compliance
- Verify test coverage
- Review security implications
- Test functionality locally
- Provide constructive feedback

**For Authors:**
- Respond to all review comments
- Make requested changes
- Keep commits focused and atomic
- Update PR description if scope changes

**Release Process**

1. **Version Bump**
   
   .. code-block:: bash
   
       # Update version in multiple places
       ./scripts/bump-version.sh 0.0.2

2. **Create Release Branch**
   
   .. code-block:: bash
   
       git checkout -b release/0.0.2
       git push origin release/0.0.2

3. **Final Testing**
   - Deploy to staging environment
   - Run full test suite
   - Perform manual testing

4. **Create Release**
   
   .. code-block:: bash
   
       git tag -a v0.0.2 -m "Release version 0.0.2"
       git push origin v0.0.2

Development Tools
-----------------

**Recommended VS Code Extensions**

- Python (Microsoft)
- Pylance (Microsoft)
- Django (Baptiste Darthenay)
- Svelte for VS Code (Svelte)
- TypeScript Importer (pmneo)
- Tailwind CSS IntelliSense (Tailwind Labs)
- GitLens (GitKraken)
- Docker (Microsoft)

**VS Code Settings**

.. code-block:: json

    // .vscode/settings.json
    {
        "python.defaultInterpreterPath": "./backend/.venv/bin/python",
        "python.linting.enabled": true,
        "python.linting.pylintEnabled": true,
        "python.formatting.provider": "black",
        "typescript.preferences.importModuleSpecifier": "relative",
        "svelte.enable-ts-plugin": true,
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }

**Docker Development**

.. code-block:: yaml

    # docker-compose.dev.yml
    version: '3.8'
    
    services:
      backend:
        build: 
          context: ./backend
          target: development
        volumes:
          - ./backend:/app
          - backend_venv:/app/.venv
        environment:
          - DJANGO_DEBUG=True
          - DJANGO_RELOAD=True
        ports:
          - "8000:8000"
        command: python manage.py runserver 0.0.0.0:8000
        
      frontend:
        build:
          context: ./frontend
          target: development
        volumes:
          - ./frontend:/app
          - frontend_node_modules:/app/node_modules
        ports:
          - "5173:5173"
        command: npm run dev -- --host
    
    volumes:
      backend_venv:
      frontend_node_modules:

This development guide provides the foundation for contributing to the Enterprise Application Tracker. For specific questions or clarification, consult the team lead or create an issue in the project repository.

Command Line Tool (eatcmd)
---------------------------

The Enterprise Application Tracker includes a comprehensive command-line tool called `eatcmd` that provides a unified interface for managing all aspects of the application lifecycle. This tool is located in the `bin/` directory and requires Python 3.12+ with the Click library.

**Application Management Commands**

Use these commands to control the application lifecycle:

.. code-block:: bash

    # Start the application (runs in detached mode by default)
    ./bin/eatcmd start
    
    # Start in foreground mode for debugging
    ./bin/eatcmd start --foreground
    
    # Stop the application
    ./bin/eatcmd stop
    
    # Restart all services
    ./bin/eatcmd restart
    
    # Check the status of all containers
    ./bin/eatcmd status

**Development and Testing Commands**

The tool provides integrated testing capabilities:

.. code-block:: bash

    # Run the complete test suite (backend and frontend)
    ./bin/eatcmd test
    
    # Run only backend tests
    ./bin/eatcmd test --backend-only
    
    # Run only frontend tests
    ./bin/eatcmd test --frontend-only
    
    # Run tests with coverage reports
    ./bin/eatcmd test --coverage

**Documentation Commands**

Build project documentation using Sphinx:

.. code-block:: bash

    # Build HTML documentation (default format)
    ./bin/eatcmd docs
    
    # Clean build directory first, then build
    ./bin/eatcmd docs --clean
    
    # Build PDF documentation
    ./bin/eatcmd docs --format pdf

**Maintenance and Cleanup Commands**

Keep your development environment clean:

.. code-block:: bash

    # Stop and remove all containers, networks, and volumes
    ./bin/eatcmd clean-docker --force
    
    # Run initial project setup
    ./bin/eatcmd setup
    
    # View application logs
    ./bin/eatcmd logs --follow
    
    # Open interactive shell in application container
    ./bin/eatcmd shell

**System Information**

Get detailed information about your development environment:

.. code-block:: bash

    # Display system and application information
    ./bin/eatcmd info

The `eatcmd` tool automatically checks for required dependencies and provides helpful error messages if anything is missing. It also handles proper file permissions and security practices, ensuring that containers are properly cleaned up after testing.
