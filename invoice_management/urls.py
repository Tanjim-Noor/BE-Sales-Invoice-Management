"""
URL configuration for invoice_management project.

This module defines the main URL routing structure for the Sales Invoice Management API.
It implements API versioning (v1), includes authentication endpoints, and provides
comprehensive API documentation using drf-spectacular.

API Structure:
    /admin/                          - Django admin interface
    /api/v1/invoices/               - Invoice management endpoints
    /api/v1/transactions/           - Transaction viewing endpoints
    /api/v1/auth/login/             - JWT token obtain (login)
    /api/v1/auth/refresh/           - JWT token refresh
    /api/schema/                     - OpenAPI schema (JSON/YAML)
    /api/docs/                       - Swagger UI interactive documentation
    /                                - Redirects to API documentation

Authentication:
    All API endpoints require JWT authentication.
    Obtain token via POST to /api/v1/auth/login/ with username and password.
    Include token in requests: Authorization: Bearer <access_token>

"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [
    # Admin Interface
    path('admin/', admin.site.urls),
    
    # API Documentation Endpoints
    
    # OpenAPI schema generation endpoint (JSON/YAML)
    path(
        'api/schema/',
        SpectacularAPIView.as_view(),
        name='schema'
    ),
    
    # Swagger UI - Interactive API documentation
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
    

    # JWT Authentication Endpoints
    
    # Obtain JWT token pair (access + refresh) by providing username and password
    path(
        'api/v1/auth/login/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    
    # Refresh access token using refresh token
    path(
        'api/v1/auth/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    

    # API v1 Endpoints
    
    # Invoice management endpoints
    path(
        'api/v1/invoices/',
        include('apps.invoices.urls', namespace='invoices')
    ),
    
    # Transaction viewing endpoints
    path(
        'api/v1/transactions/',
        include('apps.transactions.urls', namespace='transactions')
    ),
    
    # Redirect root URL to API documentation
    path(
        '',
        RedirectView.as_view(url='/api/docs/', permanent=False),
        name='api-root'
    ),
]
