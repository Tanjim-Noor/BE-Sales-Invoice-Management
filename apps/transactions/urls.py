"""
URL configuration for the transactions app.

This module configures URL routing for transaction-related API endpoints using
Django REST Framework's DefaultRouter. The router automatically generates
read-only URL patterns for the TransactionViewSet.

Generated URL Patterns:
    - GET /api/v1/transactions/     - List all transactions (paginated)
    - GET /api/v1/transactions/{id}/ - Retrieve transaction details

Note: Transactions are read-only and automatically created via signals.
No create, update, or delete endpoints are available.

URL Naming Convention:
    - transactions:transaction-list   - List endpoint
    - transactions:transaction-detail - Retrieve endpoint

All endpoints require JWT authentication.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet

# Define app namespace for URL reversal
app_name = 'transactions'

router = DefaultRouter()

# Register TransactionViewSet with the router
router.register(
    r'',
    TransactionViewSet,
    basename='transaction'
)

urlpatterns = router.urls
