"""
Django signals for the invoices app.

Handles automatic transaction creation and invoice total calculation.
"""
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from apps.invoices.models import Invoice, InvoiceItem
from apps.transactions.models import Transaction


@receiver(pre_delete, sender=InvoiceItem)
def prevent_last_item_deletion(sender, instance, **kwargs):
    """
    Prevent deletion of the last item in an invoice.
    
    Args:
        sender: The model class (InvoiceItem)
        instance: The actual instance being deleted
        **kwargs: Additional signal arguments
    
    Raises:
        ValidationError: If attempting to delete the last item
    """
    invoice = instance.invoice
    
    # Check if this is the last item
    if invoice.items.count() <= 1:
        raise ValidationError(
            'Cannot delete the last item from an invoice. '
            'Each invoice must have at least one item.'
        )


@receiver(post_save, sender=InvoiceItem)
@receiver(post_delete, sender=InvoiceItem)
def update_invoice_total(sender, instance, **kwargs):
    """
    Automatically recalculate invoice total when items are added, updated, or deleted.
    
    Args:
        sender: The model class (InvoiceItem)
        instance: The actual instance being saved/deleted
        **kwargs: Additional signal arguments
    """
    invoice = instance.invoice
    
    # Recalculate total from all invoice items
    total = invoice.calculate_total()
    
    # Update invoice total_amount if it has changed
    if invoice.total_amount != total:
        invoice.total_amount = total
        invoice.save(update_fields=['total_amount', 'updated_at'])


@receiver(post_save, sender=Invoice)
def create_sale_transaction(sender, instance, created, **kwargs):
    """
    Automatically create a 'Sale' transaction when a new invoice is created.
    
    Args:
        sender: The model class (Invoice)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional signal arguments
    """
    if created:
        # Create a Sale transaction for the newly created invoice
        Transaction.objects.create(
            invoice=instance,
            transaction_type='Sale',
            amount=instance.total_amount,
            description=f"Sale transaction for invoice {instance.reference_number}",
            created_by=instance.created_by
        )


@receiver(pre_save, sender=Invoice)
def create_payment_transaction(sender, instance, **kwargs):
    """
    Automatically create a 'Payment' transaction when invoice status changes to 'Paid'.
    
    Args:
        sender: The model class (Invoice)
        instance: The actual instance being saved
        **kwargs: Additional signal arguments
    """
    # Only process if this is an existing invoice (has pk)
    if instance.pk:
        try:
            # Get the previous state of the invoice
            old_invoice = Invoice.objects.get(pk=instance.pk)
            
            # Check if status is changing from Pending to Paid
            if old_invoice.status == 'Pending' and instance.status == 'Paid':
                # Create a Payment transaction (will be created after save completes)
                # We'll use post_save for this to ensure the status is saved first
                instance._create_payment_transaction = True
        except Invoice.DoesNotExist:
            # New invoice, do nothing
            pass


@receiver(post_save, sender=Invoice)
def handle_payment_transaction(sender, instance, created, **kwargs):
    """
    Create Payment transaction after invoice status is changed to Paid.
    
    Args:
        sender: The model class (Invoice)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional signal arguments
    """
    # Check if we need to create a payment transaction
    if hasattr(instance, '_create_payment_transaction') and instance._create_payment_transaction:
        Transaction.objects.create(
            invoice=instance,
            transaction_type='Payment',
            amount=instance.total_amount,
            description=f"Payment received for invoice {instance.reference_number}",
            created_by=instance.created_by
        )
        # Clean up the flag
        delattr(instance, '_create_payment_transaction')

