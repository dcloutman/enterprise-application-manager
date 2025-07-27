import os
import json
import logging
from datetime import datetime
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from threading import local

# Thread-local storage for current user
_thread_local = local()

User = get_user_model()


class AuditLogger:
    """
    Centralized audit logging system for all database changes.
    Logs to file in human-readable and script-parseable format.
    """
    
    def __init__(self):
        self.setup_logger()
    
    def setup_logger(self):
        """Setup file-based audit logging"""
        # Create audit logs directory if it doesn't exist
        log_dir = getattr(settings, 'AUDIT_LOG_DIR', '/var/log/app-tracker')
        os.makedirs(log_dir, exist_ok=True)
        
        # Setup audit logger
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # File handler for audit logs
        log_file = os.path.join(log_dir, 'audit.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Custom formatter for audit logs
        formatter = AuditFormatter()
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def get_current_user(self):
        """Get current user from thread-local storage"""
        return getattr(_thread_local, 'user', None)
    
    def set_current_user(self, user):
        """Set current user in thread-local storage"""
        _thread_local.user = user
    
    def log_change(self, action, model_name, object_id, object_str, changes=None, user=None, additional_info=None):
        """
        Log a database change event
        
        Args:
            action: CREATE, UPDATE, DELETE
            model_name: Name of the model being changed
            object_id: Primary key of the object
            object_str: String representation of the object
            changes: Dictionary of field changes (for UPDATE)
            user: User making the change (optional, will try to get from thread-local)
            additional_info: Additional context information
        """
        if user is None:
            user = self.get_current_user()
        
        # Build audit entry
        audit_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': action,
            'model': model_name,
            'object_id': str(object_id),
            'object_str': str(object_str),
            'user': user.username if user else 'SYSTEM',
            'user_id': user.id if user else None,
            'changes': changes or {},
            'additional_info': additional_info or {}
        }
        
        # Log the entry
        self.logger.info(json.dumps(audit_entry, separators=(',', ':')))
    
    def log_create(self, instance, user=None):
        """Log object creation"""
        self.log_change(
            action='CREATE',
            model_name=instance._meta.label,
            object_id=instance.pk,
            object_str=str(instance),
            user=user
        )
    
    def log_update(self, instance, changes, user=None):
        """Log object update with field changes"""
        self.log_change(
            action='UPDATE',
            model_name=instance._meta.label,
            object_id=instance.pk,
            object_str=str(instance),
            changes=changes,
            user=user
        )
    
    def log_delete(self, instance, user=None):
        """Log object deletion"""
        self.log_change(
            action='DELETE',
            model_name=instance._meta.label,
            object_id=instance.pk,
            object_str=str(instance),
            user=user
        )


class AuditFormatter(logging.Formatter):
    """Custom formatter for audit log entries"""
    
    def format(self, record):
        """Format audit log entry for human readability and script parsing"""
        try:
            # Parse the JSON message
            data = json.loads(record.getMessage())
            
            # Format for human readability
            timestamp = data['timestamp']
            action = data['action']
            model = data['model']
            object_id = data['object_id']
            object_str = data['object_str']
            user = data['user']
            
            # Base log message
            message = f"[{timestamp}] {action} {model}#{object_id} by {user}: {object_str}"
            
            # Add changes for UPDATE operations
            if action == 'UPDATE' and data.get('changes'):
                changes_str = []
                for field, change in data['changes'].items():
                    old_val = change.get('old', 'None')
                    new_val = change.get('new', 'None')
                    changes_str.append(f"{field}: {old_val} -> {new_val}")
                if changes_str:
                    message += f" | Changes: {'; '.join(changes_str)}"
            
            # Add additional info if present
            if data.get('additional_info'):
                info_parts = []
                for key, value in data['additional_info'].items():
                    info_parts.append(f"{key}: {value}")
                if info_parts:
                    message += f" | Info: {'; '.join(info_parts)}"
            
            # Append JSON for script parsing (on same line)
            message += f" | JSON: {json.dumps(data, separators=(',', ':'))}"
            
            return message
            
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback for malformed entries
            return f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] AUDIT_ERROR: {record.getMessage()}"


# Global audit logger instance
audit_logger = AuditLogger()
