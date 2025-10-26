from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal

User = get_user_model()


class Transaction(models.Model):
    """
    Transaction model representing financial transactions related to invoices.
    
    Tracks both Sale and Payment transactions with timestamps and descriptions.
    """
    
    TRANSACTION_TYPE_CHOICES = [
        ('Sale', 'Sale'),
        ('Payment', 'Payment'),
    ]
    
    # Relationships
    invoice = models.ForeignKey(
        'invoices.Invoice',
        on_delete=models.CASCADE,
        related_name='transactions',
        help_text="Related invoice"
    )
    
    # Transaction details
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        help_text="Type of transaction: Sale or Payment"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Transaction amount"
    )
    transaction_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Transaction timestamp"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Transaction description"
    )
    
    # Audit fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='transactions',
        help_text="User who created this transaction"
    )
    
    class Meta:
        ordering = ['-transaction_date']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=['transaction_type']),
            models.Index(fields=['-transaction_date']),
        ]
    
    def __str__(self):
        """Return transaction type with invoice reference and amount."""
        return f"{self.transaction_type} - {self.invoice.reference_number} - ${self.amount}"
    
    def clean(self):
        """
        Validate transaction data before saving.
        
        Raises:
            ValidationError: If amount is negative
        """
        super().clean()
        
        # Validate amount is non-negative
        if hasattr(self, 'amount') and self.amount < 0:
            raise ValidationError({
                'amount': 'Transaction amount cannot be negative.'
            })

