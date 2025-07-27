from django.db import models
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.contenttypes.models import ContentType
from .audit import audit_logger
import json


class AuditMixin(models.Model):
    """
    Mixin to add audit logging capabilities to Django models.
    Automatically tracks all field changes and logs them.
    """
    
    class Meta:
        abstract = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store original field values for change detection
        self._original_values = {}
        if self.pk:
            self._store_original_values()
    
    def _store_original_values(self):
        """Store original field values for change detection"""
        for field in self._meta.fields:
            if hasattr(self, field.name):
                value = getattr(self, field.name)
                # Convert to JSON-serializable format
                if hasattr(value, 'pk'):  # Foreign key
                    self._original_values[field.name] = value.pk if value else None
                elif hasattr(value, 'isoformat'):  # DateTime
                    self._original_values[field.name] = value.isoformat() if value else None
                else:
                    self._original_values[field.name] = value
    
    def get_field_changes(self):
        """Get dictionary of changed fields with old and new values"""
        if not hasattr(self, '_original_values'):
            return {}
        
        changes = {}
        for field in self._meta.fields:
            field_name = field.name
            if hasattr(self, field_name):
                current_value = getattr(self, field_name)
                
                # Convert current value to comparable format
                if hasattr(current_value, 'pk'):  # Foreign key
                    current_comparable = current_value.pk if current_value else None
                elif hasattr(current_value, 'isoformat'):  # DateTime
                    current_comparable = current_value.isoformat() if current_value else None
                else:
                    current_comparable = current_value
                
                original_value = self._original_values.get(field_name)
                
                if current_comparable != original_value:
                    # Format values for display
                    old_display = self._format_field_value(field, original_value)
                    new_display = self._format_field_value(field, current_comparable)
                    
                    changes[field_name] = {
                        'old': old_display,
                        'new': new_display
                    }
        
        return changes
    
    def _format_field_value(self, field, value):
        """Format field value for display in audit logs"""
        if value is None:
            return 'NULL'
        
        # Handle foreign keys
        if isinstance(field, models.ForeignKey) and value:
            try:
                related_obj = field.related_model.objects.get(pk=value)
                return f"{value} ({str(related_obj)})"
            except (field.related_model.DoesNotExist, AttributeError):
                return str(value)
        
        # Handle boolean fields
        if isinstance(field, models.BooleanField):
            return 'True' if value else 'False'
        
        # Handle choice fields
        if hasattr(field, 'choices') and field.choices:
            choice_dict = dict(field.choices)
            return f"{value} ({choice_dict.get(value, 'Unknown')})"
        
        # Truncate long text fields
        str_value = str(value)
        if len(str_value) > 100:
            return str_value[:97] + '...'
        
        return str_value


# Signal handlers for automatic audit logging
@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    """Store original values before save for change detection"""
    if hasattr(instance, '_original_values'):
        # This is an update - original values already stored
        pass
    else:
        # This might be a create or update without mixin
        if instance.pk:
            try:
                original = sender.objects.get(pk=instance.pk)
                instance._original_values = {}
                for field in instance._meta.fields:
                    if hasattr(original, field.name):
                        value = getattr(original, field.name)
                        if hasattr(value, 'pk'):
                            instance._original_values[field.name] = value.pk if value else None
                        elif hasattr(value, 'isoformat'):
                            instance._original_values[field.name] = value.isoformat() if value else None
                        else:
                            instance._original_values[field.name] = value
            except sender.DoesNotExist:
                instance._original_values = {}


@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    """Log model saves (create/update)"""
    # Skip audit logging for certain models
    if should_skip_audit(sender):
        return
    
    if created:
        audit_logger.log_create(instance)
    else:
        # Log update with changes
        if hasattr(instance, 'get_field_changes'):
            changes = instance.get_field_changes()
        else:
            changes = {}
        
        if changes:  # Only log if there are actual changes
            audit_logger.log_update(instance, changes)
    
    # Store new values as original for future changes
    if hasattr(instance, '_store_original_values'):
        instance._store_original_values()


@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    """Log model deletions"""
    # Skip audit logging for certain models
    if should_skip_audit(sender):
        return
    
    audit_logger.log_delete(instance)


def should_skip_audit(model_class):
    """Determine if a model should be skipped from audit logging"""
    # Skip Django's built-in models
    skip_apps = ['auth', 'contenttypes', 'sessions', 'admin']
    if model_class._meta.app_label in skip_apps:
        return True
    
    # Skip migration-related models
    if 'migration' in model_class.__name__.lower():
        return True
    
    # Add any other models to skip here
    skip_models = []
    if model_class.__name__ in skip_models:
        return True
    
    return False
