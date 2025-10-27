# Sales Invoice Management Backend

A RESTful API backend system for managing sales invoices and transactions, built with Django and Django REST Framework.

## 🚀 Technology Stack

- **Framework:** Django 5.2.7
- **API Framework:** Django REST Framework 3.16.1
- **Authentication:** djangorestframework-simplejwt 5.5.1 (JWT)
- **API Documentation:** drf-spectacular 0.28.0 (Swagger)
- **CORS Handling:** django-cors-headers 4.9.0
- **Configuration Management:** python-decouple 3.8
- **Database:** PostgreSQL (with Docker)
- **Database Driver:** psycopg2-binary
- **Python Version:** 3.13+

## 📋 Features

- JWT-based authentication
- RESTful API endpoints
- Interactive API documentation (Swagger/OpenAPI)
- CORS support for frontend integration
- Modular app structure
- Environment-based configuration
- Secure settings management

## 🛠️ Installation

### Prerequisites

- Python 3.13 or higher
- pip (Python package manager)
- Git
- Docker (for PostgreSQL database)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BE-Sales-Invoice-Management
   ```

2. **Start PostgreSQL with Docker Compose**
   
   Navigate to the docker folder and start the PostgreSQL container:
   
   ```bash
   cd docker
   docker compose up -d
   ```
   
   To stop the database:
   ```bash
   docker compose down
   ```
   
   To stop and remove all data (⚠️ this will delete the database):
   ```bash
   docker compose down -v
   ```
   
   To view logs:
   ```bash
   docker compose logs -f postgres
   ```

3. **Create and activate virtual environment**
   
   **Windows (PowerShell):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   
   **macOS/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file with your configuration values (database credentials should match Docker setup).

## 🗄️ Database Migrations

After setting up the database, you need to create and apply migrations to set up the database schema.

### Initial Setup

**Apply all migrations:**
```bash
python manage.py migrate
```

This command creates all necessary database tables for the application (users, invoices, invoice items, transactions, etc.).

### Check Migration Status

**View which migrations have been applied:**
```bash
python manage.py showmigrations
```

### Create New Migrations (For Development)

**After modifying models, create migration files:**
```bash
python manage.py makemigrations
```

**Apply new migrations:**
```bash
python manage.py migrate
```

### Reset Database (⚠️ WARNING: Deletes all data)

**If you need to start fresh:**
```bash
# Stop and remove database
cd docker
docker compose down -v

# Start fresh database
docker compose up -d
cd ..

# Apply migrations
python manage.py migrate
```

## 🌱 Seeding Sample Data

The project includes a management command to populate the database with sample data for testing and demonstration purposes.

### Load Sample Data

**Seed the database with sample invoices and transactions:**
```bash
python manage.py seed_data
```

This command creates:
- **3 Users:**
  - Admin user: `username=admin`, `password=admin123`
  - Regular user 1: `username=john_doe`, `password=john123`
  - Regular user 2: `username=jane_smith`, `password=jane123`
- **10 Sample Invoices** with realistic business data
- **30+ Invoice Items** across all invoices
- **20 Transactions** (10 Sale transactions, 10 Payment transactions)
- Half of the invoices are marked as "Paid", half as "Pending"

### Clear and Reseed Data

**Clear existing invoices and transactions, then load fresh sample data:**
```bash
python manage.py seed_data --clear
```

⚠️ **Warning:** The `--clear` flag will delete all existing invoices, invoice items, and transactions. Users are preserved.

### Seed Data Behavior

- **Idempotent Users:** If users already exist, they won't be duplicated
- **Invoice Check:** If invoices exist, the command will skip creation (use `--clear` to reset)
- **Auto-transactions:** Sale and Payment transactions are created automatically via signals
- **Realistic Data:** Includes diverse business scenarios (Web Development, Cloud Services, E-commerce, Healthcare, Education, Manufacturing, etc.)

### Help Command

**View command options:**
```bash
python manage.py help seed_data
```

## 🚀 Running the Application

6. **Create a superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```
   
   Or use the seeded admin account (if you ran `seed_data`):
   - Username: `admin`
   - Password: `admin123`

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at: `http://127.0.0.1:8000/`

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI:** `http://127.0.0.1:8000/api/docs/`
- **OpenAPI Schema:** `http://127.0.0.1:8000/api/schema/`

📖 **For complete API reference, examples, and usage guide, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)**

### Quick API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/login/` | POST | Login and obtain JWT tokens |
| `/api/v1/auth/refresh/` | POST | Refresh access token |
| `/api/v1/invoices/` | GET, POST | List/Create invoices |
| `/api/v1/invoices/{id}/` | GET, PUT, PATCH, DELETE | Manage specific invoice |
| `/api/v1/invoices/{id}/pay/` | POST | Mark invoice as paid |
| `/api/v1/transactions/` | GET | List transactions (read-only) |

## 🔐 Authentication

This API uses JWT (JSON Web Token) authentication. To access protected endpoints:

1. **Login** at `/api/v1/auth/login/` with username and password
2. **Include the access token** in the Authorization header:
   ```
   Authorization: Bearer <your_access_token>
   ```
3. **Refresh token** when access token expires (after 60 minutes)

For detailed authentication examples, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md#authentication)

## 📁 Project Structure

```
BE-Sales-Invoice-Management/
├── invoice_management/        # Project configuration
│   ├── settings.py           # Django settings
│   ├── urls.py               # Main URL configuration
│   ├── wsgi.py               # WSGI configuration
│   └── asgi.py               # ASGI configuration
├── apps/                      # Django applications
│   ├── invoices/             # Invoice management app
│   │   ├── models.py         # Invoice and InvoiceItem models
│   │   ├── views.py          # Invoice API endpoints
│   │   ├── serializers.py    # Invoice serializers
│   │   ├── signals.py        # Signal handlers
│   │   ├── admin.py          # Admin interface
│   │   ├── tests/            # Test files
│   │   └── management/
│   │       └── commands/
│   │           └── seed_data.py  # Seed data command
│   └── transactions/         # Transaction management app
│       ├── models.py         # Transaction model
│       ├── views.py          # Transaction API endpoints
│       ├── serializers.py    # Transaction serializers
│       └── admin.py          # Admin interface
├── docker/                    # Docker configuration
│   └── docker-compose.yml    # PostgreSQL setup
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # This file
└── API_DOCUMENTATION.md      # Complete API reference
```

## 💼 Business Rules

### Invoice Management
- ✅ Each invoice must have a **unique reference number**
- ✅ Invoice must have **at least one item**
- ✅ **Total amount is auto-calculated** from items (quantity × unit_price)
- ✅ Only **Pending invoices** can be marked as Paid
- ✅ **Sale transaction** is created automatically when invoice is created

### Payment Processing
- ✅ Payment is only allowed for invoices in **'Pending' status**
- ✅ **Payment transaction** is created automatically when invoice is marked as paid
- ✅ Transaction amount always matches invoice total_amount
- ✅ Cannot mark already paid invoices as paid again

### Security
- ✅ All API endpoints require **JWT authentication**
- ✅ Users can only create/modify invoices when authenticated
- ✅ Created resources are linked to the authenticated user
- ✅ Admin panel access requires staff/superuser privileges

## 🧪 Running Tests

The project includes comprehensive test coverage for invoice creation and payment workflows.

### Run All Tests

```bash
python manage.py test
```

### Run Tests for Specific App

```bash
# Test invoices app only
python manage.py test apps.invoices.tests

# Test transactions app only
python manage.py test apps.transactions.tests
```

### Run Tests with Verbose Output

```bash
python manage.py test --verbosity=2
```

### Run Specific Test Case or Method

```bash
# Run specific test class
python manage.py test apps.invoices.tests.InvoiceTestCase

# Run specific test method
python manage.py test apps.invoices.tests.InvoiceTestCase.test_create_invoice_with_valid_data
```

### Test Coverage

The test suite covers:
- ✅ Invoice creation with valid data
- ✅ Invoice creation validation (requires items)
- ✅ Invoice creation requires authentication
- ✅ Sale transaction created automatically
- ✅ Invoice payment workflow
- ✅ Payment transaction created automatically
- ✅ Cannot pay already paid invoice
- ✅ Payment requires authentication

**Note:** Django automatically creates and destroys a test database for each test run. No need to configure a separate test database.

## 🔧 Configuration

Key environment variables in `.env`:

- `SECRET_KEY` - Django secret key (keep secure!)
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Allowed host/domain names
- `DATABASE_NAME` - PostgreSQL database name
- `DATABASE_USER` - PostgreSQL database user
- `DATABASE_PASSWORD` - PostgreSQL database password
- `DATABASE_HOST` - PostgreSQL database host (localhost for local development)
- `DATABASE_PORT` - PostgreSQL database port (5432)
- `CORS_ALLOWED_ORIGINS` - Allowed CORS origins

## 🎯 Quick Start Guide

After installation, follow these steps to get started:

1. **Start PostgreSQL database:**
   ```bash
   cd docker
   docker compose up -d
   cd ..
   ```

2. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Load sample data:**
   ```bash
   python manage.py seed_data
   ```

4. **Start the server:**
   ```bash
   python manage.py runserver
   ```

5. **Access the application:**
   - API Documentation: http://127.0.0.1:8000/api/docs/
   - Admin Panel: http://127.0.0.1:8000/admin/

6. **Login credentials (from seed data):**
   - Admin: `username=admin`, `password=admin123`
   - User 1: `username=john_doe`, `password=john123`
   - User 2: `username=jane_smith`, `password=jane123`

## 🎨 Admin Interface

Access the Django admin panel at: **http://127.0.0.1:8000/admin/**

**Features:**
- Manage invoices with inline item editing
- View and filter transactions
- Bulk action to mark multiple invoices as paid
- Search invoices by reference number or customer name
- Filter by status and date
- User management


## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker ps

# Start PostgreSQL if stopped
cd docker && docker compose up -d

# View database logs
docker compose logs -f postgres
```

### Migration Issues
```bash
# Check migration status
python manage.py showmigrations

# Apply migrations
python manage.py migrate

# If issues persist, reset database (⚠️ deletes all data)
cd docker && docker compose down -v
docker compose up -d
cd .. && python manage.py migrate
```