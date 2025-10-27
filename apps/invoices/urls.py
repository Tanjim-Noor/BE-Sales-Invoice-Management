"""
URL configuration for the invoices app.

This module configures URL routing for invoice-related API endpoints using
Django REST Framework's DefaultRouter. The router automatically generates
standard RESTful URL patterns for the InvoiceViewSet.

Generated URL Patterns:
    - GET    /api/v1/invoices/           - List all invoices (paginated)
    - POST   /api/v1/invoices/           - Create new invoice
    - GET    /api/v1/invoices/{id}/      - Retrieve invoice details
    - PUT    /api/v1/invoices/{id}/      - Full update of invoice
    - PATCH  /api/v1/invoices/{id}/      - Partial update of invoice
    - DELETE /api/v1/invoices/{id}/      - Delete invoice
    - POST   /api/v1/invoices/{id}/pay/  - Custom action to mark invoice as paid

URL Naming Convention:
    - invoices:invoice-list     - List and create endpoints
    - invoices:invoice-detail   - Retrieve, update, delete endpoints
    - invoices:invoice-pay      - Custom pay action endpoint

All endpoints require JWT authentication.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet

# Define app namespace for URL reversal
app_name = 'invoices'

router = DefaultRouter()

# Register InvoiceViewSet with the router
router.register(
    r'',
    InvoiceViewSet,
    basename='invoice'
)

urlpatterns = router.urls
