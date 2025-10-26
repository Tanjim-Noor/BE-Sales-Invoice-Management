from django.contrib import admin
from django.utils.html import format_html
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin interface for Transaction model.
    Transactions are mostly auto-generated, so most fields are readonly.
    """
    # List page configuration
    list_display = (
        'transaction_type_badge',
        'invoice_link',
        'amount_display',
        'transaction_date',
        'created_by',
        'description_truncated',
    )
    list_filter = ('transaction_type', 'transaction_date')
    search_fields = ('invoice__reference_number', 'description')
    list_per_page = 25
    date_hierarchy = 'transaction_date'
    ordering = ('-transaction_date',)
    
    # Detail page configuration
    readonly_fields = (
        'invoice',
        'transaction_type',
        'amount',
        'transaction_date',
        'description',
        'created_by',
    )
    
    fieldsets = (
        ('Transaction Details', {
            'fields': (
                'invoice',
                'transaction_type',
                'amount',
                'transaction_date',
                'description',
            ),
        }),
        ('Metadata', {
            'fields': (
                'created_by',
            ),
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queries with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('invoice', 'created_by')
    
    @admin.display(description='Invoice', ordering='invoice__reference_number')
    def invoice_link(self, obj):
        """Display invoice as a clickable link to the related invoice."""
        from django.urls import reverse
        from django.utils.html import format_html
        
        if obj.invoice:
            url = reverse('admin:invoices_invoice_change', args=[obj.invoice.pk])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.invoice.reference_number
            )
        return '-'
    
    @admin.display(description='Type', ordering='transaction_type')
    def transaction_type_badge(self, obj):
        """Display transaction type with color-coded badge."""
        if obj.transaction_type == 'Sale':
            color = '#007bff'  # Blue
        else:  # Payment
            color = '#28a745'  # Green
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.transaction_type
        )
    
    @admin.display(description='Amount', ordering='amount')
    def amount_display(self, obj):
        """Display amount with currency symbol."""
        formatted_amount = '${:,.2f}'.format(float(obj.amount))
        return format_html('<strong>{}</strong>', formatted_amount)
    
    @admin.display(description='Description')
    def description_truncated(self, obj):
        """Display truncated description."""
        if obj.description:
            if len(obj.description) > 50:
                return obj.description[:50] + '...'
            return obj.description
        return '-'
    
    def has_add_permission(self, request):
        """
        Disable manual creation of transactions through admin.
        Transactions are created automatically via signals.
        """
        return False
    
    def has_delete_permission(self, request, obj=None):
        """
        Disable deletion of transactions through admin for data integrity.
        """
        return False
    
    def save_model(self, request, obj, form, change):
        """Automatically set created_by field to current user."""
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
