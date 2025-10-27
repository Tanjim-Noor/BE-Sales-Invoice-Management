"""
Management command to seed the database with sample data.

This command creates:
- Sample users (if they don't exist)
- Sample invoices with items
- Transactions are automatically created via signals

Usage:
    python manage.py seed_data
    python manage.py seed_data --clear  # Clear existing data first
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from decimal import Decimal
from apps.invoices.models import Invoice, InvoiceItem
from apps.transactions.models import Transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with sample invoices and transactions for demo purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing invoices and transactions before seeding',
        )

    def handle(self, *args, **options):
        """Execute the seed data command."""
        
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Transaction.objects.all().delete()
            InvoiceItem.objects.all().delete()
            Invoice.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Existing data cleared'))

        self.stdout.write(self.style.MIGRATE_HEADING('Starting data seeding...'))
        
        # Create users
        users = self.create_users()
        
        # Create invoices with items
        invoices = self.create_invoices(users)
        
        # Mark some invoices as paid
        self.mark_some_paid(invoices)
        
        # Display summary
        self.display_summary()

    def create_users(self):
        """Create sample users if they don't exist."""
        self.stdout.write('Creating users...')
        
        users = []
        
        # Create admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Admin user created (username: admin, password: admin123)'))
        else:
            self.stdout.write('  • Admin user already exists')
        users.append(admin)
        
        # Create regular users
        regular_users_data = [
            {'username': 'john_doe', 'email': 'john@example.com', 'password': 'john123'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'password': 'jane123'},
        ]
        
        for user_data in regular_users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'is_staff': False,
                    'is_superuser': False,
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f'  ✓ User created: {user.username} (password: {user_data["password"]})'))
            else:
                self.stdout.write(f'  • User already exists: {user.username}')
            users.append(user)
        
        return users

    @transaction.atomic
    def create_invoices(self, users):
        """Create sample invoices with items."""
        self.stdout.write('Creating invoices...')
        
        # Check if invoices already exist
        if Invoice.objects.exists():
            self.stdout.write(self.style.WARNING('  ⚠ Invoices already exist. Use --clear to reset data.'))
            return list(Invoice.objects.all())
        
        invoices_data = [
            {
                'reference_number': 'INV-2025-001',
                'customer_name': 'ABC Corporation',
                'customer_email': 'contact@abccorp.com',
                'customer_phone': '+1-555-0101',
                'customer_address': '123 Business St, New York, NY 10001',
                'items': [
                    {'description': 'Web Development Services', 'quantity': 40, 'unit_price': '125.00'},
                    {'description': 'UI/UX Design', 'quantity': 20, 'unit_price': '100.00'},
                    {'description': 'Project Management', 'quantity': 10, 'unit_price': '150.00'},
                ]
            },
            {
                'reference_number': 'INV-2025-002',
                'customer_name': 'Tech Solutions Ltd',
                'customer_email': 'billing@techsolutions.com',
                'customer_phone': '+1-555-0102',
                'customer_address': '456 Innovation Ave, San Francisco, CA 94102',
                'items': [
                    {'description': 'Cloud Infrastructure Setup', 'quantity': 1, 'unit_price': '2500.00'},
                    {'description': 'Database Optimization', 'quantity': 15, 'unit_price': '150.00'},
                ]
            },
            {
                'reference_number': 'INV-2025-003',
                'customer_name': 'Global Enterprises Inc',
                'customer_email': 'accounts@globalent.com',
                'customer_phone': '+1-555-0103',
                'customer_address': '789 Corporate Blvd, Chicago, IL 60601',
                'items': [
                    {'description': 'Software License - Annual', 'quantity': 50, 'unit_price': '99.00'},
                    {'description': 'Technical Support Package', 'quantity': 1, 'unit_price': '1500.00'},
                ]
            },
            {
                'reference_number': 'INV-2025-004',
                'customer_name': 'StartUp Innovations',
                'customer_email': 'finance@startupinno.com',
                'customer_phone': '+1-555-0104',
                'customer_address': '321 Startup Lane, Austin, TX 78701',
                'items': [
                    {'description': 'Mobile App Development', 'quantity': 80, 'unit_price': '125.00'},
                    {'description': 'API Integration', 'quantity': 24, 'unit_price': '110.00'},
                ]
            },
            {
                'reference_number': 'INV-2025-005',
                'customer_name': 'Retail Masters Co',
                'customer_email': 'payments@retailmasters.com',
                'customer_phone': '+1-555-0105',
                'customer_address': '555 Commerce St, Los Angeles, CA 90001',
                'items': [
                    {'description': 'E-commerce Platform Setup', 'quantity': 1, 'unit_price': '3500.00'},
                    {'description': 'Payment Gateway Integration', 'quantity': 1, 'unit_price': '800.00'},
                    {'description': 'Training Sessions', 'quantity': 5, 'unit_price': '200.00'},
                ]
            },
            {
                'reference_number': 'INV-2025-006',
                'customer_name': 'Healthcare Systems LLC',
                'customer_email': 'billing@healthsys.com',
                'customer_phone': '+1-555-0106',
                'customer_address': '888 Medical Center Dr, Boston, MA 02101',
                'items': [
                    {'description': 'HIPAA Compliance Consultation', 'quantity': 30, 'unit_price': '175.00'},
                    {'description': 'Security Audit', 'quantity': 1, 'unit_price': '2000.00'},
                ]
            },
            {
                'reference_number': 'INV-2025-007',
                'customer_name': 'Education Plus Institute',
                'customer_email': 'admin@eduplus.edu',
                'customer_phone': '+1-555-0107',
                'customer_address': '999 Academic Rd, Seattle, WA 98101',
                'items': [
                    {'description': 'Learning Management System', 'quantity': 1, 'unit_price': '5000.00'},
                    {'description': 'Custom Module Development', 'quantity': 40, 'unit_price': '120.00'},
                ]
            },
            {
                'reference_number': 'INV-2025-008',
                'customer_name': 'Manufacturing Pro Corp',
                'customer_email': 'ap@mfgpro.com',
                'customer_phone': '+1-555-0108',
                'customer_address': '777 Industrial Park, Detroit, MI 48201',
                'items': [
                    {'description': 'Inventory Management System', 'quantity': 1, 'unit_price': '4000.00'},
                    {'description': 'Barcode Scanner Integration', 'quantity': 25, 'unit_price': '80.00'},
                    {'description': 'Staff Training', 'quantity': 8, 'unit_price': '150.00'},
                ]
            },
            {
                'reference_number': 'INV-2025-009',
                'customer_name': 'Digital Marketing Agency',
                'customer_email': 'accounting@digimarket.com',
                'customer_phone': '+1-555-0109',
                'customer_address': '444 Creative Blvd, Miami, FL 33101',
                'items': [
                    {'description': 'Website Redesign', 'quantity': 60, 'unit_price': '130.00'},
                    {'description': 'SEO Optimization', 'quantity': 30, 'unit_price': '100.00'},
                ]
            },
            {
                'reference_number': 'INV-2025-010',
                'customer_name': 'Financial Services Group',
                'customer_email': 'invoices@finservices.com',
                'customer_phone': '+1-555-0110',
                'customer_address': '222 Wall Street, New York, NY 10005',
                'items': [
                    {'description': 'Financial Dashboard Development', 'quantity': 100, 'unit_price': '140.00'},
                    {'description': 'Data Analytics Integration', 'quantity': 50, 'unit_price': '160.00'},
                    {'description': 'Security Implementation', 'quantity': 1, 'unit_price': '3000.00'},
                ]
            },
        ]
        
        invoices = []
        for idx, invoice_data in enumerate(invoices_data):
            # Rotate through users
            user = users[idx % len(users)]
            
            # Create invoice
            invoice = Invoice.objects.create(
                reference_number=invoice_data['reference_number'],
                customer_name=invoice_data['customer_name'],
                customer_email=invoice_data['customer_email'],
                customer_phone=invoice_data['customer_phone'],
                customer_address=invoice_data['customer_address'],
                status='Pending',
                created_by=user
            )
            
            # Create invoice items
            total = Decimal('0.00')
            for item_data in invoice_data['items']:
                item = InvoiceItem.objects.create(
                    invoice=invoice,
                    description=item_data['description'],
                    quantity=item_data['quantity'],
                    unit_price=Decimal(item_data['unit_price'])
                )
                total += item.line_total
            
            # Update invoice total
            invoice.total_amount = total
            invoice.save()
            
            invoices.append(invoice)
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created: {invoice.reference_number} - ${invoice.total_amount}'))
        
        return invoices

    def mark_some_paid(self, invoices):
        """Mark some invoices as paid."""
        self.stdout.write('Marking some invoices as paid...')
        
        # Mark first 5 invoices as paid
        paid_count = 0
        for invoice in invoices[:5]:
            invoice.mark_as_paid()
            paid_count += 1
            self.stdout.write(self.style.SUCCESS(f'  ✓ Paid: {invoice.reference_number}'))
        
        self.stdout.write(self.style.SUCCESS(f'Marked {paid_count} invoices as paid'))

    def display_summary(self):
        """Display summary of seeded data."""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('DATA SEEDING COMPLETED SUCCESSFULLY!'))
        self.stdout.write('='*60)
        
        # Count data
        user_count = User.objects.count()
        invoice_count = Invoice.objects.count()
        pending_count = Invoice.objects.filter(status='Pending').count()
        paid_count = Invoice.objects.filter(status='Paid').count()
        transaction_count = Transaction.objects.count()
        sale_count = Transaction.objects.filter(transaction_type='Sale').count()
        payment_count = Transaction.objects.filter(transaction_type='Payment').count()
        
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'  • Users: {user_count}')
        self.stdout.write(f'  • Invoices: {invoice_count} (Pending: {pending_count}, Paid: {paid_count})')
        self.stdout.write(f'  • Transactions: {transaction_count} (Sales: {sale_count}, Payments: {payment_count})')
        
        self.stdout.write(f'\n🔐 Login Credentials:')
        self.stdout.write(f'  • Admin: username=admin, password=admin123')
        self.stdout.write(f'  • User 1: username=john_doe, password=john123')
        self.stdout.write(f'  • User 2: username=jane_smith, password=jane123')
        
        self.stdout.write(f'\n🚀 Next Steps:')
        self.stdout.write(f'  1. Start server: python manage.py runserver')
        self.stdout.write(f'  2. Visit API docs: http://127.0.0.1:8000/api/docs/')
        self.stdout.write(f'  3. Login at: http://127.0.0.1:8000/api/v1/auth/login/')
        self.stdout.write(f'  4. Admin panel: http://127.0.0.1:8000/admin/')
        
        self.stdout.write('\n' + '='*60 + '\n')
