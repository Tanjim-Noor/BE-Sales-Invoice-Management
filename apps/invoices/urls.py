"""
URL configuration for the invoices app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'invoices'

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
