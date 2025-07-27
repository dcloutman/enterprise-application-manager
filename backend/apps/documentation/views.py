import os
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from mimetypes import guess_type


class DocumentationPermissionMixin:
    """Mixin to check documentation access permissions"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin:login')
        
        # Check if user has documentation access
        if hasattr(request.user, 'profile'):
            if not request.user.profile.can_access_documentation():
                return render(request, 'documentation/access_denied.html', {
                    'user': request.user
                })
        else:
            return render(request, 'documentation/access_denied.html', {
                'user': request.user,
                'error': 'User profile not found. Contact your system administrator.'
            })
        
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
@method_decorator(cache_control(max_age=300), name='dispatch')  # Cache for 5 minutes
class DocumentationView(DocumentationPermissionMixin, TemplateView):
    """Serve Sphinx-generated documentation"""
    
    def get(self, request, path=''):
        """Serve documentation files with proper access control"""
        
        # Default to index.html if no path provided
        if not path or path == '/':
            path = 'index.html'
        
        # Remove leading slash if present
        if path.startswith('/'):
            path = path[1:]
        
        # Security: prevent directory traversal
        if '..' in path or path.startswith('/'):
            raise Http404("Invalid path")
        
        # Build full path to documentation files
        docs_root = os.path.join(settings.BASE_DIR, '..', 'docs', '_build', 'html')
        file_path = os.path.join(docs_root, path)
        
        # Ensure the file exists and is within the docs directory
        if not os.path.exists(file_path) or not os.path.commonpath([docs_root, file_path]).startswith(docs_root):
            raise Http404("Documentation file not found")
        
        # Determine content type
        content_type, _ = guess_type(file_path)
        if content_type is None:
            if path.endswith('.html'):
                content_type = 'text/html'
            elif path.endswith('.css'):
                content_type = 'text/css'
            elif path.endswith('.js'):
                content_type = 'application/javascript'
            else:
                content_type = 'application/octet-stream'
        
        # Read and serve the file
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            response = HttpResponse(content, content_type=content_type)
            
            # Add security headers for HTML files
            if content_type == 'text/html':
                response['X-Frame-Options'] = 'SAMEORIGIN'
                response['X-Content-Type-Options'] = 'nosniff'
            
            return response
            
        except IOError:
            raise Http404("Could not read documentation file")


@login_required
def documentation_index(request):
    """Main documentation index view"""
    # Check permissions using the same logic as DocumentationView
    if hasattr(request.user, 'profile'):
        if not request.user.profile.can_access_documentation():
            return render(request, 'documentation/access_denied.html', {
                'user': request.user
            })
    else:
        return render(request, 'documentation/access_denied.html', {
            'user': request.user,
            'error': 'User profile not found. Contact your system administrator.'
        })
    
    # Redirect to the main documentation file
    return redirect('documentation:file', path='index.html')


@login_required 
def documentation_access_status(request):
    """API endpoint to check user's documentation access status"""
    has_access = False
    role = "Unknown"
    is_admin = False
    
    if hasattr(request.user, 'profile'):
        has_access = request.user.profile.can_access_documentation()
        role = request.user.profile.get_role_display()
        is_admin = request.user.profile.role == 'application_admin'
    
    return HttpResponse(
        f"User: {request.user.username}\n"
        f"Role: {role}\n"
        f"Documentation Access: {'Yes' if has_access else 'No'}\n"
        f"Admin (Non-revokable): {'Yes' if is_admin else 'No'}",
        content_type='text/plain'
    )
