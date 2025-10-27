"""
Serializers for the invoices app.

Provides serializers for Invoice and InvoiceItem models with comprehensive
validation, nested serialization, and separate serializers for different operations.
"""
from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from .models import Invoice, InvoiceItem


class InvoiceItemSerializer(serializers.ModelSerializer):
    """
    Serializer for InvoiceItem model.
    
    Handles individual invoice items with automatic line_total calculation.
    Used for nested serialization within invoice serializers.
    """
    
    class Meta:
        model = InvoiceItem
        fields = [
            'id',
            'description',
            'quantity',
            'unit_price',
            'line_total',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'line_total', 'created_at', 'updated_at']
    
    def validate_quantity(self, value):
        """
        Validate that quantity is at least 1.
        
        Args:
            value: The quantity value to validate
            
        Returns:
            int: The validated quantity
            
        Raises:
            ValidationError: If quantity is less than 1
        """
        if value < 1:
            raise serializers.ValidationError(
                "Quantity must be at least 1."
            )
        return value
    
    def validate_unit_price(self, value):
        """
        Validate that unit_price is non-negative.
        
        Args:
            value: The unit_price value to validate
            
        Returns:
            Decimal: The validated unit_price
            
        Raises:
            ValidationError: If unit_price is negative
        """
        if value < 0:
            raise serializers.ValidationError(
                "Unit price cannot be negative."
            )
        return value
    
    def validate(self, attrs):
        """
        Perform object-level validation.
        
        Args:
            attrs: Dictionary of validated field values
            
        Returns:
            dict: The validated attributes
            
        Raises:
            ValidationError: If validation fails
        """
        # Ensure both quantity and unit_price are provided for new items
        if not self.instance:  # Creating new item
            if 'quantity' not in attrs:
                raise serializers.ValidationError({
                    'quantity': 'This field is required.'
                })
            if 'unit_price' not in attrs:
                raise serializers.ValidationError({
                    'unit_price': 'This field is required.'
                })
        
        return attrs


class InvoiceListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing invoices.
    
    Optimized for list views with minimal data and no nested relationships.
    All fields are read-only as this is used only for display.
    """
    
    class Meta:
        model = Invoice
        fields = [
            'id',
            'reference_number',
            'customer_name',
            'customer_email',
            'status',
            'total_amount',
            'created_at'
        ]
        read_only_fields = fields


class InvoiceDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for retrieving invoice information.
    
    Includes nested invoice items and all invoice details.
    Used for GET operations on individual invoices.
    """
    items = InvoiceItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    transactions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id',
            'reference_number',
            'customer_name',
            'customer_email',
            'customer_phone',
            'customer_address',
            'status',
            'total_amount',
            'items',
            'items_count',
            'transactions_count',
            'created_at',
            'updated_at',
            'created_by'
        ]
        read_only_fields = [
            'id',
            'status',
            'total_amount',
            'created_at',
            'updated_at',
            'created_by'
        ]
    
    def get_items_count(self, obj):
        """
        Get the count of invoice items.
        
        Args:
            obj: Invoice instance
            
        Returns:
            int: Number of items in the invoice
        """
        return obj.items.count()
    
    def get_transactions_count(self, obj):
        """
        Get the count of transactions.
        
        Args:
            obj: Invoice instance
            
        Returns:
            int: Number of transactions related to the invoice
        """
        return obj.transactions.count()


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new invoices with nested items.
    
    Handles invoice creation with automatic total calculation,
    nested item creation, and signal-triggered transaction generation.
    Returns detailed invoice representation after creation.
    """
    items = InvoiceItemSerializer(many=True)
    
    class Meta:
        model = Invoice
        fields = [
            'reference_number',
            'customer_name',
            'customer_email',
            'customer_phone',
            'customer_address',
            'items'
        ]
    
    def validate_reference_number(self, value):
        """
        Validate that reference_number is unique.
        
        Args:
            value: The reference_number to validate
            
        Returns:
            str: The validated reference_number
            
        Raises:
            ValidationError: If reference_number already exists
        """
        # Strip whitespace
        value = value.strip()
        
        # Check for empty string after stripping
        if not value:
            raise serializers.ValidationError(
                "Reference number cannot be empty or contain only whitespace."
            )
        
        # Check uniqueness
        if Invoice.objects.filter(reference_number=value).exists():
            raise serializers.ValidationError(
                f"Invoice with reference number '{value}' already exists."
            )
        
        return value
    
    def validate_customer_name(self, value):
        """
        Validate customer_name field.
        
        Args:
            value: The customer_name to validate
            
        Returns:
            str: The validated customer_name
            
        Raises:
            ValidationError: If customer_name is invalid
        """
        # Strip whitespace
        value = value.strip()
        
        # Check for empty string after stripping
        if not value:
            raise serializers.ValidationError(
                "Customer name cannot be empty or contain only whitespace."
            )
        
        return value
    
    def validate_customer_email(self, value):
        """
        Validate customer_email field.
        
        Args:
            value: The customer_email to validate
            
        Returns:
            str: The validated customer_email
            
        Raises:
            ValidationError: If customer_email is invalid
        """
        # Strip whitespace
        value = value.strip().lower()
        
        # Check for empty string after stripping
        if not value:
            raise serializers.ValidationError(
                "Customer email cannot be empty or contain only whitespace."
            )
        
        return value
    
    def validate_items(self, value):
        """
        Validate that items list has at least one item.
        
        Args:
            value: List of invoice items
            
        Returns:
            list: The validated items list
            
        Raises:
            ValidationError: If items list is empty
        """
        if not value or len(value) == 0:
            raise serializers.ValidationError(
                "Invoice must have at least one item."
            )
        
        return value
    
    def validate(self, attrs):
        """
        Perform object-level validation.
        
        Args:
            attrs: Dictionary of validated field values
            
        Returns:
            dict: The validated attributes
        """
        # Additional cross-field validation can be added here
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        """
        Create invoice with nested items.
        
        This method:
        1. Extracts items data from validated_data
        2. Creates the invoice instance
        3. Creates related invoice items
        4. Calculates and updates total_amount
        5. Sets created_by from request context
        6. Triggers 'Sale' transaction creation via signal
        
        Args:
            validated_data: Dictionary of validated data
            
        Returns:
            Invoice: The created invoice instance
        """
        # Extract items data
        items_data = validated_data.pop('items')
        
        # Get user from context
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        
        # Create invoice instance
        invoice = Invoice.objects.create(**validated_data)
        
        # Create invoice items
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        
        # Calculate and update total amount
        invoice.total_amount = invoice.calculate_total()
        invoice.save(update_fields=['total_amount'])
        
        # The 'Sale' transaction will be created automatically via signal
        
        return invoice
    
    def to_representation(self, instance) -> dict:
        """
        Return detailed invoice representation after creation.
        
        Args:
            instance: The created invoice instance
            
        Returns:
            dict: Serialized invoice data with all fields including id
        """
        return InvoiceDetailSerializer(instance, context=self.context).data  # type: ignore[return-value]


class InvoiceUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing invoices.
    
    Allows updating customer information but not invoice items or status.
    Items and status are managed through separate endpoints.
    """
    
    class Meta:
        model = Invoice
        fields = [
            'customer_name',
            'customer_email',
            'customer_phone',
            'customer_address'
        ]
    
    def validate_customer_name(self, value):
        """Validate customer_name field."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "Customer name cannot be empty or contain only whitespace."
            )
        return value
    
    def validate_customer_email(self, value):
        """Validate customer_email field."""
        value = value.strip().lower()
        if not value:
            raise serializers.ValidationError(
                "Customer email cannot be empty or contain only whitespace."
            )
        return value


class InvoicePaymentSerializer(serializers.Serializer):
    """
    Serializer for marking an invoice as paid.
    
    Validates that the invoice can be paid and handles the payment process
    including status update and Payment transaction creation.
    """
    
    def validate(self, attrs):
        """
        Validate that the invoice can be paid.
        
        Args:
            attrs: Dictionary of attributes (empty for this serializer)
            
        Returns:
            dict: The validated attributes
            
        Raises:
            ValidationError: If invoice cannot be paid
        """
        # Get the invoice instance from context
        invoice = self.instance
        
        if not invoice:
            raise serializers.ValidationError(
                "No invoice instance provided."
            )
        
        # Check if invoice status is 'Pending'
        if invoice.status != 'Pending':
            raise serializers.ValidationError(
                f"Cannot mark invoice as paid. Current status is '{invoice.status}'."
            )
        
        # Check if invoice has items
        if not invoice.items.exists():
            raise serializers.ValidationError(
                "Cannot mark invoice as paid. Invoice must have at least one item."
            )
        
        return attrs
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Mark invoice as paid.
        
        This method:
        1. Calls invoice.mark_as_paid() to update status
        2. Payment transaction is created via signal
        
        Args:
            instance: The invoice instance to update
            validated_data: Dictionary of validated data (empty)
            
        Returns:
            Invoice: The updated invoice instance
        """
        # Mark invoice as paid (this triggers the signal for Payment transaction)
        instance.mark_as_paid()
        
        return instance
    
    def to_representation(self, instance) -> dict:
        """
        Return detailed invoice representation after payment.
        
        Args:
            instance: The updated invoice instance
            
        Returns:
            dict: Serialized invoice data
        """
        return InvoiceDetailSerializer(instance, context=self.context).data  # type: ignore[return-value]
