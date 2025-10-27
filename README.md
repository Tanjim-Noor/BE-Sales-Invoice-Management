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

6. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at: `http://127.0.0.1:8000/`

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI:** `http://127.0.0.1:8000/api/schema/swagger-ui/`
- **ReDoc:** `http://127.0.0.1:8000/api/schema/redoc/`
- **OpenAPI Schema:** `http://127.0.0.1:8000/api/schema/`

## 🔐 Authentication

This API uses JWT (JSON Web Token) authentication. To access protected endpoints:

1. Obtain access and refresh tokens via the login endpoint
2. Include the access token in the Authorization header:
   ```
   Authorization: Bearer <your_access_token>
   ```

## 📁 Project Structure

```
BE-Sales-Invoice-Management/
├── invoice_management/        # Project configuration
│   ├── __init__.py
│   ├── settings.py           # Django settings
│   ├── urls.py               # Main URL configuration
│   ├── wsgi.py               # WSGI configuration
│   └── asgi.py               # ASGI configuration
├── apps/                      # Django applications
│   └── __init__.py
├── venv/                      # Virtual environment
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

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
