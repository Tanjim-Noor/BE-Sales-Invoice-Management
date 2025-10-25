"""
Django signals for the transactions app.
This will be used for automatic transaction creation when invoices are created.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
