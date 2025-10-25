from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.transactions'
    verbose_name = 'Transactions Management'
    
    def ready(self):
        """Import signals when app is ready."""
        import apps.transactions.signals  # noqa
