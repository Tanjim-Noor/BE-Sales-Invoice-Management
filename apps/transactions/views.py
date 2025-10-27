"""
ViewSets for the transactions app.

Provides read-only API endpoints for Transaction management including:
- List and retrieve operations (no create/update/delete)
- Advanced filtering by transaction_type, invoice, and date range
- Query optimization with select_related
- JWT authentication and permissions
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.dateparse import parse_date
from django.db.models import Q
import logging

from .models import Transaction
from .serializers import (
    TransactionListSerializer,
    TransactionSerializer,
    TransactionDetailSerializer
)
from .pagination import CustomPageNumberPagination

# Configure logger
logger = logging.getLogger(__name__)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing transactions (read-only).
    
    Transactions are automatically created via signals and cannot be
    manually created, updated, or deleted through the API.
    
    Provides:
    - JWT authentication required on all endpoints
    - Optimized queries to prevent N+1 problems
    - Advanced filtering by transaction_type, invoice, and date range
    - Ordering by transaction_date and other fields
    - Pagination with 10 items per page
    
    Endpoints:
    - GET /api/v1/transactions/ - List all transactions (paginated)
    - GET /api/v1/transactions/{id}/ - Retrieve transaction details
    
    Query Parameters:
    - transaction_type: Filter by type (Sale or Payment)
    - invoice_id: Filter by invoice ID
    - date_after: Filter transactions after this date (YYYY-MM-DD)
    - date_before: Filter transactions before this date (YYYY-MM-DD)
    - ordering: Order results (e.g., -transaction_date, amount)
    - page: Page number for pagination
    - page_size: Items per page (default: 10)
    
    Examples:
    - GET /api/v1/transactions/?transaction_type=Sale
    - GET /api/v1/transactions/?invoice_id=5
    - GET /api/v1/transactions/?date_after=2024-01-01&date_before=2024-12-31
    - GET /api/v1/transactions/?ordering=-transaction_date
    """
    
    queryset = Transaction.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    
    # Ordering configuration
    ordering_fields = ['transaction_date', 'amount', 'transaction_type']
    ordering = ['-transaction_date']  # Default ordering
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on the action.
        
        Returns:
            Serializer class:
            - TransactionListSerializer for 'list' action
            - TransactionDetailSerializer for 'retrieve' action
        """
        if self.action == 'list':
            return TransactionListSerializer
        elif self.action == 'retrieve':
            return TransactionDetailSerializer
        return TransactionSerializer
    
    def get_queryset(self):
        """
        Get optimized queryset with filtering.
        
        Optimizations:
        - Uses select_related() for invoice and created_by to prevent N+1 queries
        - Applies custom filters for transaction_type, invoice, and date range
        
        Returns:
            QuerySet: Filtered and optimized transaction queryset
        """
        queryset = Transaction.objects.select_related('invoice', 'created_by')
        
        # Filter by transaction type
        transaction_type = self.request.query_params.get('transaction_type', None)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        # Filter by invoice ID
        invoice_id = self.request.query_params.get('invoice_id', None)
        if invoice_id:
            try:
                invoice_id = int(invoice_id)
                queryset = queryset.filter(invoice_id=invoice_id)
            except ValueError:
                # Invalid invoice_id format, return empty queryset
                logger.warning(f"Invalid invoice_id format: {invoice_id}")
                queryset = queryset.none()
        
        # Date range filters
        date_after = self.request.query_params.get('date_after', None)
        if date_after:
            parsed_date = parse_date(date_after)
            if parsed_date:
                queryset = queryset.filter(transaction_date__date__gte=parsed_date)
        
        date_before = self.request.query_params.get('date_before', None)
        if date_before:
            parsed_date = parse_date(date_before)
            if parsed_date:
                queryset = queryset.filter(transaction_date__date__lte=parsed_date)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        List transactions with pagination and filtering.
        
        Overridden to add custom logging.
        
        Returns:
            Response: Paginated list of transactions
        """
        logger.debug(f"Transaction list requested by user {request.user.username}")
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve transaction details.
        
        Overridden to add custom logging.
        
        Returns:
            Response: Transaction details
        """
        instance = self.get_object()
        logger.debug(
            f"Transaction {instance.id} retrieved by user {request.user.username}"
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
        logger.error(f"Exception in TransactionViewSet: {str(exc)}", exc_info=True)
        return super().handle_exception(exc)

