"""
Serializers for the transactions app.

Provides serializers for Transaction model with read-only operations
since transactions are automatically generated via signals.
"""
from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Transaction model.
    
    Most fields are read-only since transactions are auto-generated.
    Includes invoice reference number for better readability.
    """
    invoice_reference = serializers.CharField(
        source='invoice.reference_number',
        read_only=True
    )
    invoice_id = serializers.IntegerField(
        source='invoice.id',
        read_only=True
    )
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True
    )
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'invoice',
            'invoice_id',
            'invoice_reference',
            'transaction_type',
            'amount',
            'transaction_date',
            'description',
            'created_by',
            'created_by_username'
        ]
        read_only_fields = [
            'id',
            'invoice',
            'invoice_id',
            'invoice_reference',
            'transaction_type',
            'amount',
            'transaction_date',
            'description',
            'created_by',
            'created_by_username'
        ]
    
    def to_representation(self, instance):
        """
        Customize output representation.
        
        Args:
            instance: Transaction instance
            
        Returns:
            dict: Serialized transaction data
        """
        representation = super().to_representation(instance)
        
        # Format amount to 2 decimal places
        if 'amount' in representation and representation['amount'] is not None:
            representation['amount'] = f"{float(representation['amount']):.2f}"
        
        return representation


class TransactionListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing transactions.
    
    Optimized for list views with minimal data.
    Shows invoice reference instead of just ID for better UX.
    """
    invoice_reference = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'invoice_reference',
            'transaction_type',
            'amount',
            'transaction_date'
        ]
        read_only_fields = fields
    
    def get_invoice_reference(self, obj):
        """
        Get invoice reference number.
        
        Args:
            obj: Transaction instance
            
        Returns:
            str: Invoice reference number
        """
        return obj.invoice.reference_number if obj.invoice else None
    
    def to_representation(self, instance):
        """
        Customize output representation.
        
        Args:
            instance: Transaction instance
            
        Returns:
            dict: Serialized transaction data
        """
        representation = super().to_representation(instance)
        
        # Format amount to 2 decimal places
        if 'amount' in representation and representation['amount'] is not None:
            representation['amount'] = f"{float(representation['amount']):.2f}"
        
        return representation


class TransactionDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for individual transaction retrieval.
    
    Includes all transaction information with nested invoice details.
    """
    invoice_reference = serializers.CharField(
        source='invoice.reference_number',
        read_only=True
    )
    invoice_customer_name = serializers.CharField(
        source='invoice.customer_name',
        read_only=True
    )
    invoice_status = serializers.CharField(
        source='invoice.status',
        read_only=True
    )
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True
    )
    created_by_email = serializers.CharField(
        source='created_by.email',
        read_only=True
    )
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'invoice_reference',
            'invoice_customer_name',
            'invoice_status',
            'transaction_type',
            'amount',
            'transaction_date',
            'description',
            'created_by_username',
            'created_by_email'
        ]
        read_only_fields = fields
    
    def to_representation(self, instance):
        """
        Customize output representation.
        
        Args:
            instance: Transaction instance
            
        Returns:
            dict: Serialized transaction data
        """
        representation = super().to_representation(instance)
        
        # Format amount to 2 decimal places
        if 'amount' in representation and representation['amount'] is not None:
            representation['amount'] = f"{float(representation['amount']):.2f}"
        
        return representation
