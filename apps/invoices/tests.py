"""
Tests for the invoices app.

Focuses on invoice creation and payment workflows as required by the PRD.
Tests cover:
- Invoice creation with valid data
- Invoice creation validation
- Authentication requirements
- Transaction creation (Sale and Payment)
- Payment workflow
- Payment validation
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from decimal import Decimal

from apps.invoices.models import Invoice, InvoiceItem
from apps.transactions.models import Transaction


class InvoiceTestCase(APITestCase):
    """
    Base test case for invoice-related tests.
    
    Provides common setup for authenticated API testing with JWT.
    """
    
    def setUp(self):
        """
        Set up test data and authentication.
        
        Creates a test user and obtains JWT token for authenticated requests.
        """
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Authenticate and get JWT token
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_create_invoice_with_valid_data(self):
        """Test creating an invoice with valid data."""
        data = {
            'reference_number': 'INV-001',
            'customer_name': 'John Doe',
            'customer_email': 'john@example.com',
            'items': [
                {
                    'description': 'Product A',
                    'quantity': 2,
                    'unit_price': '50.00'
                },
                {
                    'description': 'Product B',
                    'quantity': 1,
                    'unit_price': '75.00'
                }
            ]
        }
        
        response = self.client.post('/api/v1/invoices/', data, format='json')
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # The create serializer only returns the fields it accepts (no id, no total_amount)
        # So we need to check the fields that are actually in the response
        self.assertEqual(response.data['reference_number'], 'INV-001')
        self.assertEqual(response.data['customer_name'], 'John Doe')
        self.assertEqual(response.data['customer_email'], 'john@example.com')
        self.assertEqual(len(response.data['items']), 2)
        
        # Verify invoice was created in database with correct calculated total
        self.assertEqual(Invoice.objects.count(), 1)
        invoice = Invoice.objects.first()
        self.assertEqual(invoice.reference_number, 'INV-001')
        self.assertEqual(invoice.total_amount, Decimal('175.00'))
        self.assertEqual(invoice.status, 'Pending')
        self.assertEqual(invoice.items.count(), 2)
    
    def test_create_invoice_creates_sale_transaction(self):
        """Test that creating an invoice automatically creates a Sale transaction."""
        data = {
            'reference_number': 'INV-002',
            'customer_name': 'Jane Smith',
            'customer_email': 'jane@example.com',
            'items': [
                {
                    'description': 'Service A',
                    'quantity': 1,
                    'unit_price': '100.00'
                }
            ]
        }
        
        response = self.client.post('/api/v1/invoices/', data, format='json')
        
        # Assert invoice created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Get invoice from database (response doesn't include id in create serializer)
        invoice = Invoice.objects.get(reference_number='INV-002')
        
        # Assert Sale transaction was created
        transactions = Transaction.objects.filter(
            invoice=invoice,
            transaction_type='Sale'
        )
        self.assertEqual(transactions.count(), 1)
        
        sale_transaction = transactions.first()
        self.assertEqual(sale_transaction.amount, Decimal('100.00'))
        self.assertEqual(sale_transaction.transaction_type, 'Sale')
        self.assertEqual(sale_transaction.created_by, self.user)
    
    def test_create_invoice_without_items(self):
        """Test that creating an invoice without items fails."""
        data = {
            'reference_number': 'INV-003',
            'customer_name': 'Bob Johnson',
            'customer_email': 'bob@example.com',
            'items': []
        }
        
        response = self.client.post('/api/v1/invoices/', data, format='json')
        
        # Assert validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data)
        
        # Verify no invoice was created
        self.assertEqual(Invoice.objects.count(), 0)
    
    def test_create_invoice_requires_authentication(self):
        """Test that creating an invoice requires authentication."""
        # Remove authentication
        self.client.credentials()
        
        data = {
            'reference_number': 'INV-004',
            'customer_name': 'Test User',
            'customer_email': 'test@example.com',
            'items': [
                {
                    'description': 'Item',
                    'quantity': 1,
                    'unit_price': '10.00'
                }
            ]
        }
        
        response = self.client.post('/api/v1/invoices/', data, format='json')
        
        # Assert unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify no invoice was created
        self.assertEqual(Invoice.objects.count(), 0)
    
    def test_pay_pending_invoice(self):
        """Test paying a pending invoice successfully."""
        # Create an invoice first
        invoice = Invoice.objects.create(
            reference_number='INV-005',
            customer_name='Alice Brown',
            customer_email='alice@example.com',
            status='Pending',
            total_amount=Decimal('150.00'),
            created_by=self.user
        )
        InvoiceItem.objects.create(
            invoice=invoice,
            description='Product X',
            quantity=1,
            unit_price=Decimal('150.00')
        )
        
        # Pay the invoice
        response = self.client.post(f'/api/v1/invoices/{invoice.id}/pay/')
        
        # Assert payment successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('marked as paid successfully', response.data['message'])
        
        # Assert invoice status updated
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, 'Paid')
    
    def test_payment_creates_payment_transaction(self):
        """Test that paying an invoice creates a Payment transaction."""
        # Create an invoice
        invoice = Invoice.objects.create(
            reference_number='INV-006',
            customer_name='Charlie Davis',
            customer_email='charlie@example.com',
            status='Pending',
            total_amount=Decimal('200.00'),
            created_by=self.user
        )
        InvoiceItem.objects.create(
            invoice=invoice,
            description='Product Y',
            quantity=2,
            unit_price=Decimal('100.00')
        )
        
        # Pay the invoice
        response = self.client.post(f'/api/v1/invoices/{invoice.id}/pay/')
        
        # Assert payment successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Assert Payment transaction was created
        payment_transactions = Transaction.objects.filter(
            invoice=invoice,
            transaction_type='Payment'
        )
        self.assertEqual(payment_transactions.count(), 1)
        
        payment_transaction = payment_transactions.first()
        self.assertEqual(payment_transaction.amount, Decimal('200.00'))
        self.assertEqual(payment_transaction.transaction_type, 'Payment')
        self.assertEqual(payment_transaction.created_by, self.user)
    
    def test_cannot_pay_already_paid_invoice(self):
        """Test that paying an already paid invoice fails."""
        # Create a paid invoice
        invoice = Invoice.objects.create(
            reference_number='INV-007',
            customer_name='Diana Evans',
            customer_email='diana@example.com',
            status='Paid',
            total_amount=Decimal('100.00'),
            created_by=self.user
        )
        InvoiceItem.objects.create(
            invoice=invoice,
            description='Product Z',
            quantity=1,
            unit_price=Decimal('100.00')
        )
        
        # Try to pay again
        response = self.client.post(f'/api/v1/invoices/{invoice.id}/pay/')
        
        # Assert error response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        
        # Verify invoice status remains Paid
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, 'Paid')
    
    def test_payment_requires_authentication(self):
        """Test that paying an invoice requires authentication."""
        # Create an invoice
        invoice = Invoice.objects.create(
            reference_number='INV-008',
            customer_name='Eve Foster',
            customer_email='eve@example.com',
            status='Pending',
            total_amount=Decimal('50.00'),
            created_by=self.user
        )
        InvoiceItem.objects.create(
            invoice=invoice,
            description='Product W',
            quantity=1,
            unit_price=Decimal('50.00')
        )
        
        # Remove authentication
        self.client.credentials()
        
        # Try to pay
        response = self.client.post(f'/api/v1/invoices/{invoice.id}/pay/')
        
        # Assert unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify invoice status remains Pending
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, 'Pending')
