from django.utils.deprecation import MiddlewareMixin
from .audit import audit_logger


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware to capture the current user for audit logging.
    Sets the user in thread-local storage so audit logs can identify who made changes.
    """
    
    def process_request(self, request):
        """Capture the current user from the request"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            audit_logger.set_current_user(request.user)
        else:
            audit_logger.set_current_user(None)
        return None
    
    def process_response(self, request, response):
        """Clean up thread-local storage"""
        audit_logger.set_current_user(None)
        return response
    
    def process_exception(self, request, exception):
        """Clean up thread-local storage on exception"""
        audit_logger.set_current_user(None)
        return None
