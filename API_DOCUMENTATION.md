# API Documentation

Complete API reference for the Sales Invoice Management System.

## Table of Contents
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints Overview](#endpoints-overview)
- [Authentication Endpoints](#authentication-endpoints)
- [Invoice Endpoints](#invoice-endpoints)
- [Transaction Endpoints](#transaction-endpoints)
- [Error Responses](#error-responses)
- [Business Rules](#business-rules)

---

## Base URL

**Local Development:**
```
http://127.0.0.1:8000
```

**Interactive API Documentation:**
- Swagger UI: http://127.0.0.1:8000/api/docs/
- OpenAPI Schema: http://127.0.0.1:8000/api/schema/

---

## Authentication

This API uses **JWT (JSON Web Token)** authentication. All endpoints except login require authentication.

### How to Authenticate

1. **Obtain tokens** by logging in
2. **Include access token** in the Authorization header:
   ```
   Authorization: Bearer <your_access_token>
   ```

### Token Lifecycle
- **Access Token:** Expires after 60 minutes
- **Refresh Token:** Expires after 1 day
- Use refresh token to obtain new access token without re-login

---

## Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| **Authentication** |
| POST | `/api/v1/auth/login/` | Obtain JWT tokens | No |
| POST | `/api/v1/auth/refresh/` | Refresh access token | No |
| **Invoices** |
| GET | `/api/v1/invoices/` | List all invoices | Yes |
| POST | `/api/v1/invoices/` | Create new invoice | Yes |
| GET | `/api/v1/invoices/{id}/` | Get invoice details | Yes |
| PUT | `/api/v1/invoices/{id}/` | Update invoice (full) | Yes |
| PATCH | `/api/v1/invoices/{id}/` | Update invoice (partial) | Yes |
| DELETE | `/api/v1/invoices/{id}/` | Delete invoice | Yes |
| POST | `/api/v1/invoices/{id}/pay/` | Mark invoice as paid | Yes |
| **Transactions** |
| GET | `/api/v1/transactions/` | List all transactions | Yes |
| GET | `/api/v1/transactions/{id}/` | Get transaction details | Yes |

---

## Authentication Endpoints

### 1. Login (Obtain JWT Tokens)

**Endpoint:** `POST /api/v1/auth/login/`

**Description:** Authenticate user and obtain access and refresh tokens.

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Success Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Example (curl):**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "No active account found with the given credentials"
}
```

---

### 2. Refresh Access Token

**Endpoint:** `POST /api/v1/auth/refresh/`

**Description:** Obtain a new access token using refresh token.

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Success Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Example (curl):**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

---

## Invoice Endpoints

### 1. List Invoices

**Endpoint:** `GET /api/v1/invoices/`

**Description:** Get paginated list of all invoices with filtering and search.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status: `Pending` or `Paid` |
| `created_after` | date | Filter invoices created after date (YYYY-MM-DD) |
| `created_before` | date | Filter invoices created before date (YYYY-MM-DD) |
| `customer_name` | string | Filter by customer name (partial match) |
| `customer_email` | string | Filter by customer email (partial match) |
| `search` | string | Search in reference_number, customer_name, customer_email |
| `ordering` | string | Order by field (prefix with `-` for descending) |
| `page` | integer | Page number (default: 1) |
| `page_size` | integer | Items per page (default: 10) |

**Example Requests:**

```bash
# Get all invoices
curl -X GET http://127.0.0.1:8000/api/v1/invoices/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by status
curl -X GET "http://127.0.0.1:8000/api/v1/invoices/?status=Pending" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Search by customer
curl -X GET "http://127.0.0.1:8000/api/v1/invoices/?search=ABC" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by date range
curl -X GET "http://127.0.0.1:8000/api/v1/invoices/?created_after=2025-01-01&created_before=2025-12-31" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Order by total amount (descending)
curl -X GET "http://127.0.0.1:8000/api/v1/invoices/?ordering=-total_amount" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Success Response (200 OK):**
```json
{
  "count": 10,
  "next": "http://127.0.0.1:8000/api/v1/invoices/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "reference_number": "INV-2025-001",
      "customer_name": "ABC Corporation",
      "customer_email": "contact@abccorp.com",
      "status": "Paid",
      "total_amount": "8500.00",
      "created_at": "2025-10-27T10:30:00Z",
      "updated_at": "2025-10-27T10:35:00Z"
    }
  ]
}
```

---

### 2. Create Invoice

**Endpoint:** `POST /api/v1/invoices/`

**Description:** Create a new invoice with items. A "Sale" transaction is created automatically.

**Request Body:**
```json
{
  "reference_number": "INV-2025-100",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1-555-0199",
  "customer_address": "123 Main St, City, State 12345",
  "items": [
    {
      "description": "Web Development Services",
      "quantity": 40,
      "unit_price": "125.00"
    },
    {
      "description": "UI/UX Design",
      "quantity": 20,
      "unit_price": "100.00"
    }
  ]
}
```

**Field Validations:**
- `reference_number`: Required, unique, max 50 characters
- `customer_name`: Required, max 200 characters
- `customer_email`: Required, valid email format
- `customer_phone`: Optional, max 20 characters
- `customer_address`: Optional
- `items`: Required, minimum 1 item
  - `description`: Required, max 500 characters
  - `quantity`: Required, minimum 1
  - `unit_price`: Required, minimum 0.00

**Example (curl):**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/invoices/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reference_number": "INV-2025-100",
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "customer_phone": "+1-555-0199",
    "customer_address": "123 Main St, City, State 12345",
    "items": [
      {
        "description": "Web Development Services",
        "quantity": 40,
        "unit_price": "125.00"
      },
      {
        "description": "UI/UX Design",
        "quantity": 20,
        "unit_price": "100.00"
      }
    ]
  }'
```

**Success Response (201 Created):**
```json
{
  "id": 11,
  "reference_number": "INV-2025-100",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1-555-0199",
  "customer_address": "123 Main St, City, State 12345",
  "status": "Pending",
  "total_amount": "7000.00",
  "items": [
    {
      "id": 21,
      "description": "Web Development Services",
      "quantity": 40,
      "unit_price": "125.00",
      "line_total": "5000.00"
    },
    {
      "id": 22,
      "description": "UI/UX Design",
      "quantity": 20,
      "unit_price": "100.00",
      "line_total": "2000.00"
    }
  ],
  "created_by": 1,
  "created_at": "2025-10-27T12:00:00Z",
  "updated_at": "2025-10-27T12:00:00Z"
}
```

**Error Response (400 Bad Request):**
```json
{
  "reference_number": [
    "Invoice with this reference number already exists."
  ],
  "items": [
    "Invoice must have at least one item."
  ]
}
```

---

### 3. Get Invoice Details

**Endpoint:** `GET /api/v1/invoices/{id}/`

**Description:** Retrieve detailed information about a specific invoice.

**Example:**
```bash
curl -X GET http://127.0.0.1:8000/api/v1/invoices/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "reference_number": "INV-2025-001",
  "customer_name": "ABC Corporation",
  "customer_email": "contact@abccorp.com",
  "customer_phone": "+1-555-0101",
  "customer_address": "123 Business St, New York, NY 10001",
  "status": "Paid",
  "total_amount": "8500.00",
  "items": [
    {
      "id": 1,
      "description": "Web Development Services",
      "quantity": 40,
      "unit_price": "125.00",
      "line_total": "5000.00"
    },
    {
      "id": 2,
      "description": "UI/UX Design",
      "quantity": 20,
      "unit_price": "100.00",
      "line_total": "2000.00"
    },
    {
      "id": 3,
      "description": "Project Management",
      "quantity": 10,
      "unit_price": "150.00",
      "line_total": "1500.00"
    }
  ],
  "transactions": [
    {
      "id": 1,
      "transaction_type": "Sale",
      "amount": "8500.00",
      "transaction_date": "2025-10-27T10:30:00Z"
    },
    {
      "id": 6,
      "transaction_type": "Payment",
      "amount": "8500.00",
      "transaction_date": "2025-10-27T10:35:00Z"
    }
  ],
  "created_by": 1,
  "created_at": "2025-10-27T10:30:00Z",
  "updated_at": "2025-10-27T10:35:00Z"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

### 4. Update Invoice (Full Update)

**Endpoint:** `PUT /api/v1/invoices/{id}/`

**Description:** Fully update an invoice. All fields must be provided.

**Request Body:**
```json
{
  "reference_number": "INV-2025-001-UPDATED",
  "customer_name": "ABC Corporation Ltd",
  "customer_email": "newcontact@abccorp.com",
  "customer_phone": "+1-555-0199",
  "customer_address": "456 New Address St, New York, NY 10002",
  "items": [
    {
      "description": "Updated Service",
      "quantity": 50,
      "unit_price": "150.00"
    }
  ]
}
```

**Example:**
```bash
curl -X PUT http://127.0.0.1:8000/api/v1/invoices/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

### 5. Update Invoice (Partial Update)

**Endpoint:** `PATCH /api/v1/invoices/{id}/`

**Description:** Partially update an invoice. Only provided fields will be updated.

**Request Body (Example):**
```json
{
  "customer_phone": "+1-555-9999",
  "customer_address": "New address only"
}
```

**Example:**
```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/invoices/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_phone": "+1-555-9999"
  }'
```

---

### 6. Delete Invoice

**Endpoint:** `DELETE /api/v1/invoices/{id}/`

**Description:** Delete an invoice and all related items and transactions.

**Example:**
```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/invoices/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Success Response (204 No Content):**
```
(Empty response body)
```

---

### 7. Pay Invoice

**Endpoint:** `POST /api/v1/invoices/{id}/pay/`

**Description:** Mark an invoice as paid. A "Payment" transaction is created automatically.

**Request Body:**
```json
{}
```
_(Empty body - no additional data required)_

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/invoices/1/pay/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Success Response (200 OK):**
```json
{
  "status": "success",
  "message": "Invoice INV-2025-001 has been marked as paid successfully.",
  "data": {
    "id": 1,
    "reference_number": "INV-2025-001",
    "customer_name": "ABC Corporation",
    "status": "Paid",
    "total_amount": "8500.00",
    ...
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "status": "error",
  "message": "Cannot mark invoice as paid.",
  "details": {
    "error": [
      "Cannot mark invoice as paid. Current status is 'Paid'."
    ]
  }
}
```

---

## Transaction Endpoints

### 1. List Transactions

**Endpoint:** `GET /api/v1/transactions/`

**Description:** Get paginated list of all transactions (read-only).

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `transaction_type` | string | Filter by type: `Sale` or `Payment` |
| `invoice_id` | integer | Filter by invoice ID |
| `date_after` | date | Filter transactions after date (YYYY-MM-DD) |
| `date_before` | date | Filter transactions before date (YYYY-MM-DD) |
| `ordering` | string | Order by field (prefix with `-` for descending) |
| `page` | integer | Page number (default: 1) |
| `page_size` | integer | Items per page (default: 10) |

**Example Requests:**

```bash
# Get all transactions
curl -X GET http://127.0.0.1:8000/api/v1/transactions/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by type
curl -X GET "http://127.0.0.1:8000/api/v1/transactions/?transaction_type=Sale" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by invoice
curl -X GET "http://127.0.0.1:8000/api/v1/transactions/?invoice_id=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by date range
curl -X GET "http://127.0.0.1:8000/api/v1/transactions/?date_after=2025-10-01&date_before=2025-10-31" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Success Response (200 OK):**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "transaction_type": "Sale",
      "amount": "8500.00",
      "invoice": {
        "id": 1,
        "reference_number": "INV-2025-001"
      },
      "transaction_date": "2025-10-27T10:30:00Z"
    },
    {
      "id": 6,
      "transaction_type": "Payment",
      "amount": "8500.00",
      "invoice": {
        "id": 1,
        "reference_number": "INV-2025-001"
      },
      "transaction_date": "2025-10-27T10:35:00Z"
    }
  ]
}
```

---

### 2. Get Transaction Details

**Endpoint:** `GET /api/v1/transactions/{id}/`

**Description:** Retrieve detailed information about a specific transaction.

**Example:**
```bash
curl -X GET http://127.0.0.1:8000/api/v1/transactions/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "transaction_type": "Sale",
  "amount": "8500.00",
  "invoice": {
    "id": 1,
    "reference_number": "INV-2025-001",
    "customer_name": "ABC Corporation",
    "status": "Paid",
    "total_amount": "8500.00"
  },
  "created_by": 1,
  "transaction_date": "2025-10-27T10:30:00Z",
  "created_at": "2025-10-27T10:30:00Z"
}
```

---

## Error Responses

### Common HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 OK | Request successful |
| 201 Created | Resource created successfully |
| 204 No Content | Request successful, no content to return |
| 400 Bad Request | Invalid request data or validation error |
| 401 Unauthorized | Authentication required or token invalid |
| 403 Forbidden | Authenticated but not authorized |
| 404 Not Found | Resource not found |
| 500 Internal Server Error | Server error |

### Error Response Format

**Validation Error (400):**
```json
{
  "field_name": [
    "Error message for this field"
  ],
  "another_field": [
    "Another error message"
  ]
}
```

**Authentication Error (401):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Not Found Error (404):**
```json
{
  "detail": "Not found."
}
```

---

## Business Rules

### Invoice Rules
1. **Unique Reference Numbers**: Each invoice must have a unique `reference_number`
2. **Minimum Items**: Invoice must have at least one item
3. **Auto-calculation**: `total_amount` is automatically calculated from items
4. **Status Transition**: Only `Pending` invoices can be marked as `Paid`
5. **No Direct Total Edit**: Cannot manually set `total_amount` - calculated from items

### Transaction Rules
1. **Auto-creation**: Transactions are created automatically via signals
2. **Read-only**: Cannot create, update, or delete transactions via API
3. **Sale Transaction**: Created automatically when invoice is created
4. **Payment Transaction**: Created automatically when invoice is marked as paid
5. **Amount Match**: Transaction amount always matches invoice `total_amount`

### Authentication Rules
1. **Token Required**: All endpoints except login require JWT token
2. **Token Expiry**: Access token expires after 60 minutes
3. **Refresh Token**: Use refresh token to get new access token
4. **User Association**: Created resources are linked to authenticated user

### Data Validation Rules
1. **Email Format**: Must be valid email format
2. **Positive Amounts**: `unit_price` and `quantity` must be positive
3. **Non-empty Strings**: Required text fields cannot be empty
4. **Date Format**: Dates must be in ISO 8601 format (YYYY-MM-DD)

---

## Rate Limiting

Currently, no rate limiting is implemented. This may be added in production.

---

## Pagination

All list endpoints use pagination:
- **Default page size**: 10 items
- **Max page size**: 100 items
- Use `page` parameter to navigate
- Use `page_size` parameter to adjust items per page

**Example:**
```
/api/v1/invoices/?page=2&page_size=20
```

---

## Testing the API

### Using Swagger UI (Recommended)

1. Visit http://127.0.0.1:8000/api/docs/
2. Click "Authorize" button
3. Enter: `Bearer YOUR_ACCESS_TOKEN`
4. Test any endpoint interactively

### Using curl

See examples throughout this documentation.

### Using Postman

1. Import the OpenAPI schema from http://127.0.0.1:8000/api/schema/
2. Set Authorization to Bearer Token
3. Add your access token
4. Test endpoints

---

## Support

For issues or questions:
- Check the [README.md](README.md) for setup instructions
- Review error messages carefully
- Ensure authentication token is valid
- Verify request data matches field validations

---

**Last Updated:** October 27, 2025
