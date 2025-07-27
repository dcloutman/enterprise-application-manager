from django.apps import AppConfig


class InventoryConfig(AppConfig):
    name = 'apps.inventory'
    verbose_name = 'IT Inventory Management'
    default_auto_field = 'django.db.models.BigAutoField'
    
    def ready(self):
        """Import audit signals when the app is ready"""
        try:
            from . import audit_signals
        except ImportError:
            pass
