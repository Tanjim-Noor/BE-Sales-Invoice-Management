"""
ViewSets for the invoices app.

Provides comprehensive API endpoints for Invoice management including:
- CRUD operations on invoices
- Custom pay invoice action
- Advanced filtering, searching, and ordering
- Query optimization with select_related and prefetch_related
- JWT authentication and permissions
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Prefetch
from django.utils.dateparse import parse_date
from decimal import Decimal
import logging

from .models import Invoice, InvoiceItem
from .serializers import (
    InvoiceListSerializer,
    InvoiceDetailSerializer,
    InvoiceCreateSerializer,
    InvoiceUpdateSerializer,
    InvoicePaymentSerializer
)
from .pagination import InvoicePagination

# Configure logger
logger = logging.getLogger(__name__)


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing invoices.
    
    Provides complete CRUD operations for invoices with:
    - JWT authentication required on all endpoints
    - Optimized queries to prevent N+1 problems
    - Advanced filtering by status, date range, and customer
    - Full-text search on reference number, customer name, and email
    - Ordering by created_at, total_amount, and other fields
    - Pagination with 10 items per page
    - Custom action for marking invoices as paid
    
    Endpoints:
    - GET /api/v1/invoices/ - List all invoices (paginated)
    - POST /api/v1/invoices/ - Create new invoice
    - GET /api/v1/invoices/{id}/ - Retrieve invoice details
    - PUT /api/v1/invoices/{id}/ - Update invoice (full update)
    - PATCH /api/v1/invoices/{id}/ - Partial update invoice
    - DELETE /api/v1/invoices/{id}/ - Delete invoice
    - POST /api/v1/invoices/{id}/pay/ - Mark invoice as paid
    
    Query Parameters:
    - status: Filter by status (Pending or Paid)
    - created_after: Filter invoices created after this date (YYYY-MM-DD)
    - created_before: Filter invoices created before this date (YYYY-MM-DD)
    - customer_name: Filter by customer name (partial match)
    - customer_email: Filter by customer email (partial match)
    - search: Search in reference_number, customer_name, customer_email
    - ordering: Order results (e.g., -created_at, total_amount)
    - page: Page number for pagination
    - page_size: Items per page (default: 10)
    
    Examples:
    - GET /api/v1/invoices/?status=Pending
    - GET /api/v1/invoices/?created_after=2024-01-01&created_before=2024-12-31
    - GET /api/v1/invoices/?search=John&ordering=-total_amount
    - POST /api/v1/invoices/{id}/pay/
    """
    
    queryset = Invoice.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = InvoicePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Search configuration
    search_fields = ['reference_number', 'customer_name', 'customer_email']
    
    # Ordering configuration
    ordering_fields = ['created_at', 'updated_at', 'total_amount', 'reference_number']
    ordering = ['-created_at']  # Default ordering
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on the action.
        
        Returns:
            Serializer class:
            - InvoiceListSerializer for 'list' action
            - InvoiceDetailSerializer for 'retrieve' action
            - InvoiceCreateSerializer for 'create' action
            - InvoiceUpdateSerializer for 'update' and 'partial_update' actions
            - InvoicePaymentSerializer for 'pay' action
        """
        if self.action == 'list':
            return InvoiceListSerializer
        elif self.action == 'retrieve':
            return InvoiceDetailSerializer
        elif self.action == 'create':
            return InvoiceCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return InvoiceUpdateSerializer
        elif self.action == 'pay':
            return InvoicePaymentSerializer
        return InvoiceDetailSerializer
    
    def get_queryset(self):
        """
        Get optimized queryset with filtering.
        
        Optimizations:
        - Uses select_related() for created_by to prevent N+1 queries
        - Uses prefetch_related() for items and transactions
        - Applies custom filters for status, date range, and customer
        
        Returns:
            QuerySet: Filtered and optimized invoice queryset
        """
        queryset = Invoice.objects.select_related('created_by').prefetch_related(
            Prefetch('items', queryset=InvoiceItem.objects.all()),
            'transactions'
        )
        
        # Apply custom filters from query parameters
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Date range filters
        created_after = self.request.query_params.get('created_after', None)
        if created_after:
            date_after = parse_date(created_after)
            if date_after:
                queryset = queryset.filter(created_at__date__gte=date_after)
        
        created_before = self.request.query_params.get('created_before', None)
        if created_before:
            date_before = parse_date(created_before)
            if date_before:
                queryset = queryset.filter(created_at__date__lte=date_before)
        
        # Customer filters
        customer_name = self.request.query_params.get('customer_name', None)
        if customer_name:
            queryset = queryset.filter(customer_name__icontains=customer_name)
        
        customer_email = self.request.query_params.get('customer_email', None)
        if customer_email:
            queryset = queryset.filter(customer_email__icontains=customer_email)
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Create invoice and set created_by to current user.
        
        The serializer handles:
        - Creating invoice with nested items
        - Auto-calculating total_amount from items
        - Triggering 'Sale' transaction creation via signal
        
        Args:
            serializer: InvoiceCreateSerializer instance
        """
        invoice = serializer.save()
        logger.info(
            f"Invoice {invoice.reference_number} created by user {self.request.user.username}"
        )
    
    def perform_update(self, serializer):
        """
        Update invoice and log the action.
        
        Args:
            serializer: InvoiceUpdateSerializer instance
        """
        invoice = serializer.save()
        logger.info(
            f"Invoice {invoice.reference_number} updated by user {self.request.user.username}"
        )
    
    def perform_destroy(self, instance):
        """
        Delete invoice and log the action.
        
        Args:
            instance: Invoice instance to delete
        """
        reference_number = instance.reference_number
        instance.delete()
        logger.info(
            f"Invoice {reference_number} deleted by user {self.request.user.username}"
        )
    
    @action(detail=True, methods=['post'], url_path='pay')
    def pay(self, request, pk=None):
        """
        Mark an invoice as paid.
        
        Custom action to process invoice payment. This endpoint:
        1. Validates the invoice exists and is in 'Pending' status
        2. Marks the invoice as paid by calling mark_as_paid()
        3. Creates a 'Payment' transaction automatically via signal
        4. Returns updated invoice details with success message
        
        URL: POST /api/v1/invoices/{id}/pay/
        
        Request Body: {} (empty - no additional data required)
        
        Response (200 OK):
        {
            "status": "success",
            "message": "Invoice INV-001 has been marked as paid successfully.",
            "data": {
                "id": 1,
                "reference_number": "INV-001",
                "customer_name": "John Doe",
                "status": "Paid",
                ...
            }
        }
        
        Error Responses:
        - 400 Bad Request: If invoice is already paid or has validation errors
        - 404 Not Found: If invoice doesn't exist
        
        Args:
            request: HTTP request object
            pk: Invoice primary key
            
        Returns:
            Response: Success or error response
        """
        try:
            invoice = self.get_object()
        except Invoice.DoesNotExist:
            logger.warning(f"Payment attempt on non-existent invoice with ID {pk}")
            return Response(
                {
                    'status': 'error',
                    'message': 'Invoice not found.',
                    'details': f'No invoice exists with ID {pk}.'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Use the payment serializer for validation
        serializer = self.get_serializer(instance=invoice, data={})
        
        if serializer.is_valid():
            # Mark invoice as paid (this also creates Payment transaction via signal)
            updated_invoice = serializer.save()
            
            logger.info(
                f"Invoice {updated_invoice.reference_number} marked as paid by user {request.user.username}"
            )
            
            return Response(
                {
                    'status': 'success',
                    'message': f'Invoice {updated_invoice.reference_number} has been marked as paid successfully.',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        else:
            logger.warning(
                f"Failed payment attempt on invoice {invoice.reference_number}: {serializer.errors}"
            )
            return Response(
                {
                    'status': 'error',
                    'message': 'Cannot mark invoice as paid.',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def list(self, request, *args, **kwargs):
        """
        List invoices with pagination and filtering.
        
        Overridden to add custom logging.
        
        Returns:
            Response: Paginated list of invoices
        """
        logger.debug(f"Invoice list requested by user {request.user.username}")
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve invoice details.
        
        Overridden to add custom logging.
        
        Returns:
            Response: Invoice details
        """
        instance = self.get_object()
        logger.debug(
            f"Invoice {instance.reference_number} retrieved by user {request.user.username}"
        )
        return super().retrieve(request, *args, **kwargs)
    
    def handle_exception(self, exc):
        """
        Handle exceptions and return appropriate responses.
        
        Args:
            exc: Exception instance
            
        Returns:
            Response: Error response with appropriate status code
        """
        logger.error(f"Exception in InvoiceViewSet: {str(exc)}", exc_info=True)
        return super().handle_exception(exc)
