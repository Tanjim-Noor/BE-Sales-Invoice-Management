from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.contrib import messages
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    """
    Inline admin for InvoiceItem to allow editing items directly on Invoice page.
    """
    model = InvoiceItem
    extra = 1  # Show one empty form for adding new items
    min_num = 1  # Require at least one item
    fields = ('description', 'quantity', 'unit_price', 'line_total')
    readonly_fields = ('line_total',)  # Line total is auto-calculated
    
    def get_queryset(self, request):
        """Optimize queries by selecting related invoice."""
        qs = super().get_queryset(request)
        return qs.select_related('invoice')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """
    Admin interface for Invoice model with comprehensive display and filtering.
    """
    # List page configuration
    list_display = (
        'reference_number',
        'customer_name',
        'customer_email',
        'status_badge',
        'total_amount_display',
        'items_count',
        'created_at',
        'created_by',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('reference_number', 'customer_name', 'customer_email')
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    # Detail page configuration
    readonly_fields = ('total_amount', 'created_at', 'updated_at', 'created_by')
    
    fieldsets = (
        ('Customer Information', {
            'fields': (
                'customer_name',
                'customer_email',
                'customer_phone',
                'customer_address',
            ),
        }),
        ('Invoice Details', {
            'fields': (
                'reference_number',
                'status',
                'total_amount',
            ),
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
                'created_by',
            ),
            'classes': ('collapse',),  # Make this section collapsible
        }),
    )
    
    inlines = [InvoiceItemInline]
    
    # Custom actions
    actions = ['mark_as_paid']
    
    def get_queryset(self, request):
        """Optimize queries with select_related and annotate."""
        qs = super().get_queryset(request)
        return qs.select_related('created_by').annotate(
            num_items=Count('items')
        )
    
    @admin.display(description='Status', ordering='status')
    def status_badge(self, obj):
        """Display status with color-coded badge."""
        if obj.status == 'Paid':
            color = '#28a745'  # Green
        else:
            color = '#ffc107'  # Yellow
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.status
        )
    
    @admin.display(description='Total Amount', ordering='total_amount')
    def total_amount_display(self, obj):
        """Display total amount with currency symbol."""
        formatted_amount = '${:,.2f}'.format(float(obj.total_amount))
        return format_html('<strong>{}</strong>', formatted_amount)
    
    @admin.display(description='Items', ordering='num_items')
    def items_count(self, obj):
        """Display number of items in the invoice."""
        return obj.num_items if hasattr(obj, 'num_items') else obj.items.count()
    
    @admin.action(description='Mark selected invoices as paid')
    def mark_as_paid(self, request, queryset):
        """
        Custom action to mark selected invoices as paid.
        Only processes invoices with 'Pending' status.
        """
        # Filter only pending invoices
        pending_invoices = queryset.filter(status='Pending')
        
        if not pending_invoices.exists():
            self.message_user(
                request,
                'No pending invoices selected. Only pending invoices can be marked as paid.',
                level=messages.WARNING
            )
            return
        
        # Check each invoice has items
        invoices_without_items = []
        invoices_to_update = []
        
        for invoice in pending_invoices:
            if not invoice.items.exists():
                invoices_without_items.append(invoice.reference_number)
            else:
                invoices_to_update.append(invoice)
        
        # Report invoices without items
        if invoices_without_items:
            self.message_user(
                request,
                f'Cannot mark invoices as paid (no items): {", ".join(invoices_without_items)}',
                level=messages.ERROR
            )
        
        # Update valid invoices
        updated_count = 0
        for invoice in invoices_to_update:
            try:
                invoice.mark_as_paid()
                updated_count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'Error marking invoice {invoice.reference_number} as paid: {str(e)}',
                    level=messages.ERROR
                )
        
        if updated_count > 0:
            self.message_user(
                request,
                f'Successfully marked {updated_count} invoice(s) as paid. Payment transactions created automatically.',
                level=messages.SUCCESS
            )
    
    def save_model(self, request, obj, form, change):
        """Automatically set created_by field to current user."""
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        """Make reference_number readonly when editing existing invoice."""
        readonly_fields = list(self.readonly_fields)
        if obj:  # Editing existing invoice
            readonly_fields.append('reference_number')
        return tuple(readonly_fields)


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    """
    Admin interface for InvoiceItem model.
    Primarily for viewing; items should be edited through Invoice inline.
    """
    list_display = (
        'invoice',
        'description',
        'quantity',
        'unit_price',
        'line_total_display',
        'created_at',
    )
    list_filter = ('invoice__status', 'created_at')
    search_fields = ('description', 'invoice__reference_number')
    list_per_page = 25
    readonly_fields = ('line_total', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Item Details', {
            'fields': (
                'invoice',
                'description',
                'quantity',
                'unit_price',
                'line_total',
            ),
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queries with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('invoice', 'invoice__created_by')
    
    @admin.display(description='Line Total', ordering='line_total')
    def line_total_display(self, obj):
        """Display line total with currency symbol."""
        formatted_amount = '${:,.2f}'.format(float(obj.line_total))
        return format_html('<strong>{}</strong>', formatted_amount)
