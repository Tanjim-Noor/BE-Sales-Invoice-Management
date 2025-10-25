"""
URL configuration for the transactions app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'transactions'

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
