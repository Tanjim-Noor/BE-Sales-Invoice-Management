from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal

User = get_user_model()


class Invoice(models.Model):
    """
    Invoice model representing a sales invoice with customer information.
    
    Tracks invoice status, totals, and maintains relationships with invoice items.
    """
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ]
    
    # Primary fields
    reference_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique invoice reference number"
    )
    
    # Customer information
    customer_name = models.CharField(
        max_length=200,
        help_text="Customer's full name"
    )
    customer_email = models.EmailField(
        help_text="Customer's email address"
    )
    customer_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Customer's phone number"
    )
    customer_address = models.TextField(
        blank=True,
        null=True,
        help_text="Customer's address"
    )
    
    # Invoice details
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        help_text="Invoice status"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total invoice amount"
    )
    
    # Audit fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Invoice creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='invoices',
        help_text="User who created this invoice"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        indexes = [
            models.Index(fields=['reference_number']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        """Return the invoice reference number as string representation."""
        return self.reference_number
    
    def clean(self):
        """
        Validate invoice data before saving.
        
        Raises:
            ValidationError: If total_amount is negative or invoice has no items
        """
        super().clean()
        
        # Validate total_amount is not negative
        if self.total_amount < 0:
            raise ValidationError({
                'total_amount': 'Total amount cannot be negative.'
            })
        
        # Validate invoice has at least one item (only for existing invoices)
        if self.pk and not self.items.exists():
            raise ValidationError(
                'Invoice must have at least one item.'
            )
    
    def calculate_total(self):
        """
        Calculate total amount from all invoice items.
        
        Returns:
            Decimal: Sum of all invoice item line totals, or 0 if no items exist
        """
        if not self.pk:
            # Invoice hasn't been saved yet, return 0
            return Decimal('0.00')
        
        total = sum(item.line_total for item in self.items.all())
        return Decimal(str(total)) if total else Decimal('0.00')
    
    def can_be_paid(self):
        """
        Check if invoice can be marked as paid.
        
        Returns:
            bool: True if status is 'Pending', False otherwise
        """
        return self.status == 'Pending'
    
    def mark_as_paid(self):
        """
        Mark invoice as paid.
        
        Updates status to 'Paid' and saves the instance.
        This will trigger the signal to create a Payment transaction.
        
        Raises:
            ValidationError: If invoice is already paid or has no items
        """
        if not self.can_be_paid():
            raise ValidationError('Invoice is already paid.')
        
        # Ensure invoice has at least one item before marking as paid
        if not self.items.exists():
            raise ValidationError(
                'Cannot mark invoice as paid. Invoice must have at least one item.'
            )
        
        self.status = 'Paid'
        self.save(update_fields=['status', 'updated_at'])


class InvoiceItem(models.Model):
    """
    Invoice item model representing individual line items in an invoice.
    
    Automatically calculates line total based on quantity and unit price.
    """
    
    # Relationships
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Related invoice"
    )
    
    # Item details
    description = models.CharField(
        max_length=255,
        help_text="Item description"
    )
    quantity = models.PositiveIntegerField(
        help_text="Item quantity (must be at least 1)"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per unit"
    )
    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Calculated line total (quantity × unit_price)"
    )
    
    # Audit fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Item creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )
    
    class Meta:
        ordering = ['id']
        verbose_name = 'Invoice Item'
        verbose_name_plural = 'Invoice Items'
    
    def __str__(self):
        """Return item description with invoice reference."""
        return f"{self.description} - {self.invoice.reference_number}"
    
    def clean(self):
        """
        Validate invoice item data before saving.
        
        Raises:
            ValidationError: If quantity < 1 or unit_price is negative
        """
        super().clean()
        
        # Validate quantity is at least 1
        if hasattr(self, 'quantity') and self.quantity < 1:
            raise ValidationError({
                'quantity': 'Quantity must be at least 1.'
            })
        
        # Validate unit_price is non-negative
        if hasattr(self, 'unit_price') and self.unit_price < 0:
            raise ValidationError({
                'unit_price': 'Unit price cannot be negative.'
            })
    
    def calculate_line_total(self):
        """
        Calculate line total from quantity and unit price.
        
        Returns:
            Decimal: quantity × unit_price
        """
        return Decimal(str(self.quantity)) * self.unit_price
    
    def save(self, *args, **kwargs):
        """
        Override save to auto-calculate line_total before saving.
        """
        # Auto-calculate line_total
        self.line_total = self.calculate_line_total()
        
        super().save(*args, **kwargs)
