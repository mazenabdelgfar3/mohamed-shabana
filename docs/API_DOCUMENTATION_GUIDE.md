# API Documentation Guide

> **Version:** 1.0  
> **Last Updated:** 2026-06-24  
> **Purpose:** Complete reference for all REST API endpoints in the ERP system

---

## Table of Contents

1. [Documentation Standards](#1-documentation-standards)
2. [Authentication Endpoints](#2-authentication-endpoints)
3. [Products Endpoints](#3-products-endpoints)
4. [Customers Endpoints](#4-customers-endpoints)
5. [Suppliers Endpoints](#5-suppliers-endpoints)
6. [Sales Endpoints](#6-sales-endpoints)
7. [Purchases Endpoints](#7-purchases-endpoints)
8. [Inventory Endpoints](#8-inventory-endpoints)
9. [Repairs Endpoints](#9-repairs-endpoints)
10. [Employees Endpoints](#10-employees-endpoints)
11. [Reports Endpoints](#11-reports-endpoints)
12. [Audit Endpoints](#12-audit-endpoints)

---

## 1. Documentation Standards

### Template for Each Endpoint

Every endpoint must be documented using the following template:

```markdown
### `{METHOD}` `{URL}`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Brief description of what this endpoint does |
| **Auth Required** | Yes / No |
| **Permission Required** | Permission name or "None" |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body** (if applicable):

```json
{...}
```

**Success Response** (`{status_code}`):

```json
{...}
```

**Error Responses**:

| Status | Condition | Message |
|--------|-----------|---------|
| 400 | Validation failure | `{"error": "حقل الاسم مطلوب"}` |
| 401 | Not authenticated | `{"error": "يجب تسجيل الدخول أولاً"}` |
| 403 | No permission | `{"error": "ليس لديك صلاحية"}` |
| 404 | Resource not found | `{"error": "لم يتم العثور على ..."}` |

**Notes:**
- Edge cases
- Performance considerations
- Related endpoints
```

### Response Schema Conventions

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | Arabic status message |
| `data` | object/array | Response payload |
| `count` | int | Total records (list endpoints) |
| `page` | int | Current page (list endpoints) |
| `pageSize` | int | Items per page (list endpoints) |

---

## 2. Authentication Endpoints

### `POST` `/api/auth/login`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Authenticate user credentials and create a server-side session |
| **Auth Required** | No |
| **Permission Required** | None (public) |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:**

```json
{
  "username": "admin",
  "password": "P@ssw0rd123"
}
```

**Success Response** (`200`):

```json
{
  "message": "تم تسجيل الدخول بنجاح",
  "data": {
    "user": {
      "id": 1,
      "username": "admin",
      "display_name": "مدير النظام",
      "role": "admin"
    }
  }
}
```

**Error Responses:**

| Status | Condition | Message |
|--------|-----------|---------|
| 400 | Missing field | `{"error": "حقل اسم المستخدم مطلوب"}` |
| 401 | Invalid credentials | `{"error": "اسم المستخدم أو كلمة المرور غير صحيحة"}` |
| 401 | Account locked | `{"error": "تم قفل الحساب. الرجاء المحاولة بعد 15 دقيقة"}` |
| 429 | Too many attempts | `{"error": "لقد تجاوزت الحد المسموح من محاولات تسجيل الدخول"}` |

**Notes:**
- Session cookie is set automatically in the response (`Set-Cookie` header)
- Session duration: 8 hours (configurable via `PERMANENT_SESSION_LIFETIME`)
- After 5 failed attempts, account is locked for 15 minutes
- Password must be hashed server-side (never sent in plain text logs)
- Always use HTTPS in production to protect credentials in transit

---

### `POST` `/api/auth/logout`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Destroy the current session and log out the user |
| **Auth Required** | Yes |
| **Permission Required** | None |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:** None

**Success Response** (`200`):

```json
{
  "message": "تم تسجيل الخروج بنجاح"
}
```

**Error Responses:**

| Status | Condition | Message |
|--------|-----------|---------|
| 401 | Not logged in | `{"error": "لم يتم تسجيل الدخول"}` |

**Notes:**
- Client should clear any locally cached user data after logout
- Session is destroyed server-side (filesystem session file is deleted)
- No request body needed

---

### `GET` `/api/auth/me`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Retrieve the currently authenticated user's profile and permissions |
| **Auth Required** | Yes |
| **Permission Required** | None |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:** None

**Success Response** (`200`):

```json
{
  "message": "تم جلب بيانات المستخدم بنجاح",
  "data": {
    "id": 1,
    "username": "admin",
    "display_name": "مدير النظام",
    "role": "admin",
    "permissions": [
      "products.view",
      "products.create",
      "products.edit",
      "products.delete",
      "sales.view",
      "sales.create",
      "sales.edit",
      "sales.delete",
      "inventory.view",
      "inventory.adjust",
      "inventory.count",
      "employees.view",
      "employees.manage",
      "reports.view",
      "audit.view",
      "settings.manage"
    ]
  }
}
```

**Error Responses:**

| Status | Condition | Message |
|--------|-----------|---------|
| 401 | Not authenticated | `{"error": "يجب تسجيل الدخول أولاً"}` |

**Notes:**
- This endpoint is called on page load to verify session validity
- Permissions list is used by frontend to show/hide UI elements
- Session timeout does not clear the cookie; this endpoint will return 401

---

## 3. Products Endpoints

### `GET` `/api/products`

| Attribute | Value |
|-----------|-------|
| **Purpose** | List all products with optional filtering, sorting, search, and pagination |
| **Auth Required** | Yes |
| **Permission Required** | `products.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `Page` | int | 1 | Page number |
| `PageSize` | int | 20 | Items per page (max 100) |
| `sort` | string | `-created_at` | Sort field; prefix `-` for descending |
| `search` | string | - | Search by name, SKU, or barcode |
| `category_id` | int | - | Filter by category |
| `brand_id` | int | - | Filter by brand |
| `tax_id` | int | - | Filter by tax rate |
| `is_active` | bool | - | Filter by active status |

**Request Body:** None

**Success Response** (`200`):

```json
{
  "message": "تم جلب المنتجات بنجاح",
  "data": [
    {
      "id": 1,
      "name": "حاسوب محمول",
      "sku": "LPT-001",
      "barcode": "6250001234567",
      "price": 150075,
      "cost_price": 125000,
      "category_id": 5,
      "category_name": "إلكترونيات",
      "brand_id": 3,
      "brand_name": "Dell",
      "tax_id": 1,
      "tax_rate": 0.15,
      "is_active": true,
      "has_stock": true,
      "stock_quantity": 25,
      "created_at": "2026-06-01T08:00:00Z",
      "updated_at": "2026-06-20T14:30:00Z"
    }
  ],
  "count": 150,
  "page": 1,
  "pageSize": 20
}
```

**Error Responses:**

| Status | Condition | Message |
|--------|-----------|---------|
| 400 | Invalid filter | `{"error": "حقل الفلترة 'invalid_field' غير مسموح به"}` |
| 401 | Not authenticated | `{"error": "يجب تسجيل الدخول أولاً"}` |
| 403 | No permission | `{"error": "ليس لديك صلاحية للوصول إلى هذا المورد"}` |

**Notes:**
- Price and cost_price are in halalas (integer). Frontend divides by 100 for display
- `stock_quantity` is computed by joining with inventory table (may be slow for large datasets — consider caching)
- To get only products with stock: add `?has_stock=1`
- Use `category_id` and `brand_id` from the categories/brands endpoints

---

### `POST` `/api/products`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Create a new product |
| **Auth Required** | Yes |
| **Permission Required** | `products.create` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:**

```json
{
  "name": "حاسوب مكتبي",
  "sku": "DKT-002",
  "barcode": "6250009876543",
  "price": 200000,
  "cost_price": 175000,
  "category_id": 5,
  "brand_id": 3,
  "tax_id": 1,
  "min_stock": 5,
  "is_active": true
}
```

**Success Response** (`201`):

```json
{
  "message": "تم إنشاء المنتج بنجاح",
  "data": {
    "id": 152
  }
}
```

**Error Responses:**

| Status | Condition | Message |
|--------|-----------|---------|
| 400 | Missing name | `{"error": "حقل اسم المنتج مطلوب"}` |
| 400 | Invalid price | `{"error": "يجب أن يكون السعر رقماً صحيحاً موجباً"}` |
| 400 | Duplicate SKU | `{"error": "رمز SKU موجود مسبقاً"}` |
| 400 | Invalid JSON | `{"error": "صيغة JSON غير صحيحة"}` |
| 403 | No permission | `{"error": "ليس لديك صلاحية لإنشاء منتجات"}` |

**Notes:**
- SKU is required and must be unique
- Barcode is optional but must be unique if provided
- Price and cost_price are in halalas (integer). Send `150075` for 1,500.75 SAR
- Category, brand, and tax must already exist (validated server-side)

---

### `GET` `/api/products/{id}`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Retrieve a single product by ID |
| **Auth Required** | Yes |
| **Permission Required** | `products.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:** None

**Success Response** (`200`):

```json
{
  "message": "تم جلب المنتج بنجاح",
  "data": {
    "id": 1,
    "name": "حاسوب محمول",
    "sku": "LPT-001",
    "barcode": "6250001234567",
    "price": 150075,
    "cost_price": 125000,
    "category_id": 5,
    "category_name": "إلكترونيات",
    "brand_id": 3,
    "brand_name": "Dell",
    "tax_id": 1,
    "tax_rate": 0.15,
    "min_stock": 5,
    "is_active": true,
    "has_stock": true,
    "stock_quantity": 25,
    "created_at": "2026-06-01T08:00:00Z",
    "updated_at": "2026-06-20T14:30:00Z"
  }
}
```

**Error Responses:**

| Status | Condition | Message |
|--------|-----------|---------|
| 400 | Invalid ID | `{"error": "معرف المنتج يجب أن يكون رقماً"}` |
| 404 | Not found | `{"error": "لم يتم العثور على المنتج"}` |
| 403 | No permission | `{"error": "ليس لديك صلاحية للوصول إلى هذا المورد"}` |

**Notes:**
- Includes category_name, brand_name, tax_rate for display convenience
- Stock quantity is the sum across all warehouses

---

### `PUT` `/api/products/{id}`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Update an existing product |
| **Auth Required** | Yes |
| **Permission Required** | `products.edit` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:**

```json
{
  "name": "حاسوب محمول - موديل 2026",
  "price": 160000,
  "is_active": true
}
```

**Success Response** (`200`):

```json
{
  "message": "تم تحديث المنتج بنجاح",
  "data": {
    "id": 1
  }
}
```

**Error Responses:**

| Status | Condition | Message |
|--------|-----------|---------|
| 400 | Invalid price | `{"error": "يجب أن يكون السعر رقماً صحيحاً موجباً"}` |
| 400 | Duplicate SKU | `{"error": "رمز SKU موجود مسبقاً"}` |
| 404 | Not found | `{"error": "لم يتم العثور على المنتج"}` |
| 403 | No permission | `{"error": "ليس لديك صلاحية لتعديل المنتجات"}` |

**Notes:**
- Only send fields that need updating (partial update)
- Changing SKU will validate uniqueness against other products
- Cannot change product ID

---

### `DELETE` `/api/products/{id}`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Soft-delete a product (set `is_active = false`) |
| **Auth Required** | Yes |
| **Permission Required** | `products.delete` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:** None

**Success Response** (`200`):

```json
{
  "message": "تم حذف المنتج بنجاح"
}
```

**Error Responses:**

| Status | Condition | Message |
|--------|-----------|---------|
| 404 | Not found | `{"error": "لم يتم العثور على المنتج"}` |
| 403 | No permission | `{"error": "ليس لديك صلاحية لحذف المنتجات"}` |
| 409 | Has transactions | `{"error": "لا يمكن حذف المنتج لأنه مرتبط بمعاملات سابقة"}` |

**Notes:**
- This is a soft-delete: `is_active` is set to `false`
- Products with existing transactions cannot be hard-deleted (database integrity)
- To hard-delete, use the database directly (not exposed via API)

---

### `GET` `/api/products/categories`

| Attribute | Value |
|-----------|-------|
| **Purpose** | List all product categories |
| **Auth Required** | Yes |
| **Permission Required** | `products.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:** None

**Success Response** (`200`):

```json
{
  "message": "تم جلب التصنيفات بنجاح",
  "data": [
    {
      "id": 1,
      "name": "إلكترونيات",
      "description": "المنتجات الإلكترونية والكهربائية"
    },
    {
      "id": 2,
      "name": "مواد غذائية",
      "description": "المواد الغذائية والمشروبات"
    }
  ]
}
```

**Error Responses:**

| Status | Condition | Message |
|--------|-----------|---------|
| 401 | Not authenticated | `{"error": "يجب تسجيل الدخول أولاً"}` |

---

### `GET` `/api/products/brands`

| Attribute | Value |
|-----------|-------|
| **Purpose** | List all product brands |
| **Auth Required** | Yes |
| **Permission Required** | `products.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:** None

**Success Response** (`200`):

```json
{
  "message": "تم جلب الماركات التجارية بنجاح",
  "data": [
    { "id": 1, "name": "Samsung" },
    { "id": 2, "name": "LG" }
  ]
}
```

---

### `GET` `/api/products/taxes`

| Attribute | Value |
|-----------|-------|
| **Purpose** | List all tax rates |
| **Auth Required** | Yes |
| **Permission Required** | `products.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:** None

**Success Response** (`200`):

```json
{
  "message": "تم جلب نسب الضريبة بنجاح",
  "data": [
    {
      "id": 1,
      "name": "ضريبة القيمة المضافة",
      "rate": 0.15,
      "is_default": true
    }
  ]
}
```

**Notes:**
- `rate` is a decimal (e.g. 0.15 = 15%)

---

## 4. Customers Endpoints

### `GET` `/api/customers`

| Attribute | Value |
|-----------|-------|
| **Purpose** | List all customers with filtering, sorting, search, pagination |
| **Auth Required** | Yes |
| **Permission Required** | `sales.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `Page` | int | 1 | Page number |
| `PageSize` | int | 20 | Items per page |
| `sort` | string | `-created_at` | Sort field |
| `search` | string | - | Search by name, phone, email |
| `is_active` | bool | - | Filter by active status |
| `phone` | string | - | Filter by phone |

**Request Body:** None

**Success Response** (`200`):

```json
{
  "message": "تم جلب العملاء بنجاح",
  "data": [
    {
      "id": 1,
      "name": "شركة الأمل للتجارة",
      "phone": "0123456789",
      "email": "info@alamal.com",
      "address": "الرياض، المملكة العربية السعودية",
      "is_active": true,
      "total_sales": 25000000,
      "created_at": "2026-01-15T09:00:00Z",
      "updated_at": "2026-06-20T14:30:00Z"
    }
  ],
  "count": 85,
  "page": 1,
  "pageSize": 20
}
```

**Notes:**
- `total_sales` is the sum of all sales order grand totals for this customer
- Sortable fields: `name`, `phone`, `email`, `created_at`, `total_sales`

---

### `POST` `/api/customers`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Create a new customer |
| **Auth Required** | Yes |
| **Permission Required** | `sales.create` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:**

```json
{
  "name": "مؤسسة النور للتجارة",
  "phone": "0567891234",
  "email": "info@alnoor.com",
  "address": "جدة، المملكة العربية السعودية"
}
```

**Success Response** (`201`):

```json
{
  "message": "تم إنشاء العميل بنجاح",
  "data": { "id": 86 }
}
```

**Error Responses:**

| Status | Condition | Message |
|--------|-----------|---------|
| 400 | Missing name | `{"error": "حقل اسم العميل مطلوب"}` |
| 400 | Invalid phone | `{"error": "رقم الجوال غير صحيح"}` |
| 400 | Duplicate phone | `{"error": "رقم الجوال موجود مسبقاً"}` |
| 400 | Invalid email | `{"error": "البريد الإلكتروني غير صحيح"}` |

---

### `GET` `/api/customers/{id}`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Retrieve a single customer by ID |
| **Auth Required** | Yes |
| **Permission Required** | `sales.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Success Response** (`200`):

```json
{
  "message": "تم جلب بيانات العميل بنجاح",
  "data": {
    "id": 1,
    "name": "شركة الأمل للتجارة",
    "phone": "0123456789",
    "email": "info@alamal.com",
    "address": "الرياض",
    "is_active": true,
    "total_sales": 25000000,
    "created_at": "2026-01-15T09:00:00Z"
  }
}
```

**Error Responses:**

| Status | Condition | Message |
|--------|-----------|---------|
| 404 | Not found | `{"error": "لم يتم العثور على العميل"}` |

---

### `PUT` `/api/customers/{id}`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Update customer information |
| **Auth Required** | Yes |
| **Permission Required** | `sales.edit` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:**

```json
{
  "name": "شركة الأمل للتجارة - فرع الرياض",
  "phone": "0555555555"
}
```

---

### `DELETE` `/api/customers/{id}`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Soft-delete a customer |
| **Auth Required** | Yes |
| **Permission Required** | `sales.delete` |
| **Content-Type** | `application/json; charset=utf-8` |

**Success Response** (`200`):

```json
{
  "message": "تم حذف العميل بنجاح"
}
```

---

## 5. Suppliers Endpoints

### `GET` `/api/suppliers`

Same structure as customers. Filters: `name`, `phone`, `email`, `is_active`.

**Success Response** (`200`):

```json
{
  "message": "تم جلب الموردين بنجاح",
  "data": [
    {
      "id": 1,
      "name": "شركة الإمداد للتوزيع",
      "phone": "0112223334",
      "email": "supply@imdad.com",
      "address": "الدمام",
      "is_active": true,
      "total_purchases": 45000000,
      "created_at": "2026-02-01T10:00:00Z"
    }
  ]
}
```

### `POST` `/api/suppliers`

```json
{
  "name": "شركة الجودة للاستيراد",
  "phone": "0577778888",
  "email": "info@aljoda.com",
  "address": "الخبر"
}
```

### `GET` `/api/suppliers/{id}`

Retrieve a single supplier.

### `PUT` `/api/suppliers/{id}`

Update supplier information.

### `DELETE` `/api/suppliers/{id}`

Soft-delete a supplier.

---

## 6. Sales Endpoints

### `GET` `/api/sales/orders`

| Attribute | Value |
|-----------|-------|
| **Purpose** | List all sales orders with filtering, sorting, search, pagination |
| **Auth Required** | Yes |
| **Permission Required** | `sales.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `Page` | int | Page number |
| `PageSize` | int | Items per page |
| `status` | string | Filter: `pending`, `completed`, `cancelled` |
| `customer_id` | int | Filter by customer |
| `date_from` | string | Filter: start date (ISO 8601) |
| `date_to` | string | Filter: end date (ISO 8601) |
| `sort` | string | Sort field (`-created_at`, `grand_total`, `status`) |
| `search` | string | Search by order ID or customer name |

**Success Response** (`200`):

```json
{
  "message": "تم جلب أوامر البيع بنجاح",
  "data": [
    {
      "id": 128,
      "customer_id": 1,
      "customer_name": "شركة الأمل للتجارة",
      "order_date": "2026-06-20T10:30:00Z",
      "status": "completed",
      "subtotal": 1500000,
      "discount": 50000,
      "tax": 217500,
      "grand_total": 1667500,
      "paid_amount": 1667500,
      "remaining_amount": 0,
      "notes": "تسليم خلال 3 أيام",
      "items": [
        {
          "product_id": 1,
          "product_name": "حاسوب محمول",
          "quantity": 10,
          "unit_price": 150075,
          "total": 1500750
        }
      ],
      "created_by": 1,
      "created_by_name": "مدير النظام",
      "created_at": "2026-06-20T10:30:00Z"
    }
  ],
  "count": 520,
  "page": 1,
  "pageSize": 20
}
```

**Notes:**
- `grand_total` = `subtotal` - `discount` + `tax`
- `remaining_amount` = `grand_total` - `paid_amount`
- Items array is included for order detail; for list endpoints, consider omitting items and providing a separate endpoint

---

### `POST` `/api/sales/orders`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Create a new sales order |
| **Auth Required** | Yes |
| **Permission Required** | `sales.create` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:**

```json
{
  "customer_id": 1,
  "order_date": "2026-06-24T10:00:00Z",
  "items": [
    {
      "product_id": 1,
      "quantity": 5,
      "unit_price": 150075
    },
    {
      "product_id": 2,
      "quantity": 3,
      "unit_price": 85000
    }
  ],
  "discount": 25000,
  "notes": "فاتورة رقم INV-001"
}
```

**Success Response** (`201`):

```json
{
  "message": "تم إنشاء أمر البيع بنجاح",
  "data": {
    "id": 129,
    "grand_total": 1014125
  }
}
```

**Error Responses:**

| Status | Condition | Message |
|--------|-----------|---------|
| 400 | Missing items | `{"error": "يجب إضافة عنصر واحد على الأقل"}` |
| 400 | Insufficient stock | `{"error": "الكمية غير متوفرة للمنتج: حاسوب محمول (المتوفر: 3، المطلوب: 5)"}` |
| 400 | Invalid customer | `{"error": "العميل غير موجود"}` |
| 422 | Discount > subtotal | `{"error": "الخصم لا يمكن أن يتجاوز إجمالي الفاتورة"}` |
| 403 | No permission | `{"error": "ليس لديك صلاحية لإنشاء أوامر بيع"}` |

**Notes:**
- Stock is automatically deducted upon order creation
- Unit_price must be provided explicitly (not taken from product table)
- The transaction is atomic: all items are created or none

---

### `GET` `/api/sales/orders/{id}`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Retrieve a single sales order with all items |
| **Auth Required** | Yes |
| **Permission Required** | `sales.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Success Response** (`200`):

```json
{
  "message": "تم جلب أمر البيع بنجاح",
  "data": {
    "id": 128,
    "customer_id": 1,
    "customer_name": "شركة الأمل للتجارة",
    "customer_phone": "0123456789",
    "order_date": "2026-06-20T10:30:00Z",
    "status": "completed",
    "subtotal": 1500000,
    "discount": 50000,
    "tax": 217500,
    "grand_total": 1667500,
    "paid_amount": 1667500,
    "remaining_amount": 0,
    "notes": "تسليم خلال 3 أيام",
    "items": [
      {
        "product_id": 1,
        "product_name": "حاسوب محمول",
        "sku": "LPT-001",
        "quantity": 10,
        "unit_price": 150075,
        "total": 1500750
      }
    ],
    "payments": [
      {
        "id": 1,
        "amount": 1000000,
        "payment_date": "2026-06-20T10:30:00Z",
        "payment_method": "cash"
      },
      {
        "id": 2,
        "amount": 667500,
        "payment_date": "2026-06-22T14:00:00Z",
        "payment_method": "bank_transfer"
      }
    ],
    "created_by": 1,
    "created_by_name": "مدير النظام",
    "created_at": "2026-06-20T10:30:00Z"
  }
}
```

---

## 7. Purchases Endpoints

### `GET` `/api/purchases/orders`

| Attribute | Value |
|-----------|-------|
| **Purpose** | List all purchase orders with filtering, sorting, search, pagination |
| **Auth Required** | Yes |
| **Permission Required** | `inventory.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Success Response** (`200`):

```json
{
  "message": "تم جلب أوامر الشراء بنجاح",
  "data": [
    {
      "id": 45,
      "supplier_id": 1,
      "supplier_name": "شركة الإمداد للتوزيع",
      "order_date": "2026-06-15T08:00:00Z",
      "status": "partially_received",
      "subtotal": 5000000,
      "discount": 100000,
      "tax": 735000,
      "grand_total": 5635000,
      "paid_amount": 3000000,
      "remaining_amount": 2635000,
      "notes": "",
      "items": [
        {
          "product_id": 1,
          "product_name": "حاسوب محمول",
          "quantity": 20,
          "received_quantity": 10,
          "unit_price": 250000,
          "total": 5000000
        }
      ],
      "created_at": "2026-06-15T08:00:00Z"
    }
  ],
  "count": 30,
  "page": 1,
  "pageSize": 20
}
```

**Notes:**
- Status values: `pending`, `partially_received`, `completed`, `cancelled`
- `received_quantity` tracks how many items have been physically received
- Filterable by `supplier_id`, `status`, `date_from`, `date_to`

---

### `POST` `/api/purchases/orders`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Create a new purchase order |
| **Auth Required** | Yes |
| **Permission Required** | `inventory.adjust` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:**

```json
{
  "supplier_id": 1,
  "order_date": "2026-06-24T10:00:00Z",
  "items": [
    {
      "product_id": 1,
      "quantity": 50,
      "unit_price": 225000
    }
  ],
  "discount": 0,
  "notes": "طلب توريد أجهزة حاسوب"
}
```

**Success Response** (`201`):

```json
{
  "message": "تم إنشاء أمر الشراء بنجاح",
  "data": {
    "id": 46
  }
}
```

**Notes:**
- Purchase orders do NOT affect inventory until items are received
- Unit_price is the purchase cost price

---

### `POST` `/api/purchases/orders/{id}/receive`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Receive items for a purchase order, updating inventory |
| **Auth Required** | Yes |
| **Permission Required** | `inventory.adjust` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:**

```json
{
  "warehouse_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 20
    }
  ]
}
```

**Success Response** (`200`):

```json
{
  "message": "تم استلام الأصناف بنجاح",
  "data": {
    "order_id": 46,
    "received_items": [
      {
        "product_id": 1,
        "quantity_received": 20,
        "quantity_remaining": 30
      }
    ]
  }
}
```

**Error Responses:**

| Status | Condition | Message |
|--------|-----------|---------|
| 400 | Exceeds order quantity | `{"error": "الكمية المستلمة تتجاوز الكمية المطلوبة للمنتج: حاسوب محمول (المتبقي: 10، المطلوب: 20)"}` |
| 400 | Invalid warehouse | `{"error": "المستودع غير موجود"}` |
| 404 | Order not found | `{"error": "لم يتم العثور على أمر الشراء"}` |
| 400 | Order cancelled | `{"error": "لا يمكن استلام طلب ملغي"}` |

**Notes:**
- Can receive items in multiple partial shipments
- Received quantity cannot exceed ordered quantity
- Inventory is updated atomically within a transaction
- Order status auto-updates to `partially_received` or `completed`

---

### `GET` `/api/purchases/orders/{id}`

Retrieve a single purchase order with all items, payments, and receive history.

---

## 8. Inventory Endpoints

### `GET` `/api/inventory/stock`

| Attribute | Value |
|-----------|-------|
| **Purpose** | List current stock levels across all warehouses |
| **Auth Required** | Yes |
| **Permission Required** | `inventory.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `Page` | int | Page number |
| `PageSize` | int | Items per page |
| `product_id` | int | Filter by product |
| `warehouse_id` | int | Filter by warehouse |
| `search` | string | Search by product name or SKU |
| `min_stock` | bool | If `1`, show only products below minimum stock |
| `sort` | string | Sort field |

**Success Response** (`200`):

```json
{
  "message": "تم جلب المخزون بنجاح",
  "data": [
    {
      "product_id": 1,
      "product_name": "حاسوب محمول",
      "sku": "LPT-001",
      "warehouse_id": 1,
      "warehouse_name": "المستودع الرئيسي",
      "quantity": 25,
      "min_stock": 5,
      "is_low_stock": false
    },
    {
      "product_id": 1,
      "product_name": "حاسوب محمول",
      "sku": "LPT-001",
      "warehouse_id": 2,
      "warehouse_name": "مستودع جدة",
      "quantity": 10,
      "min_stock": 3,
      "is_low_stock": false
    }
  ],
  "count": 200,
  "page": 1,
  "pageSize": 20
}
```

**Notes:**
- Stock is per warehouse (a product can exist in multiple warehouses)
- `is_low_stock` = `quantity < min_stock`
- Use `?min_stock=1` to get low stock alerts

---

### `GET` `/api/inventory/stock/{id}`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Get stock for a specific product across all warehouses |
| **Auth Required** | Yes |
| **Permission Required** | `inventory.view` |

**Success Response** (`200`):

```json
{
  "message": "تم جلب المخزون بنجاح",
  "data": {
    "product_id": 1,
    "product_name": "حاسوب محمول",
    "sku": "LPT-001",
    "warehouses": [
      {
        "warehouse_id": 1,
        "warehouse_name": "المستودع الرئيسي",
        "quantity": 25
      },
      {
        "warehouse_id": 2,
        "warehouse_name": "مستودع جدة",
        "quantity": 10
      }
    ],
    "total_quantity": 35
  }
}
```

---

### `POST` `/api/inventory/adjust`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Manually adjust stock level for a product in a warehouse |
| **Auth Required** | Yes |
| **Permission Required** | `inventory.adjust` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:**

```json
{
  "product_id": 1,
  "warehouse_id": 1,
  "quantity": 30,
  "reason": "تسوية جرد دوري",
  "reference_type": "inventory_adjustment",
  "reference_id": null
}
```

**Success Response** (`200`):

```json
{
  "message": "تم تعديل المخزون بنجاح",
  "data": {
    "product_id": 1,
    "warehouse_id": 1,
    "old_quantity": 25,
    "new_quantity": 30,
    "difference": 5
  }
}
```

**Notes:**
- This endpoint sets the absolute quantity (not increment)
- Audit trail: a movement record is created automatically
- Reason is required and logged for accountability
- If quantity falls below 0, the request is rejected

**Error Responses:**

| Status | Condition | Message |
|--------|-----------|---------|
| 400 | Negative quantity | `{"error": "لا يمكن أن يصبح المخزون سالباً"}` |
| 400 | Missing reason | `{"error": "الرجاء إدخال سبب التعديل"}` |
| 404 | Product not found | `{"error": "لم يتم العثور على المنتج"}` |
| 404 | Warehouse not found | `{"error": "المستودع غير موجود"}` |

---

### `POST` `/api/inventory/stock-count`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Perform a full or partial stock count and reconcile differences |
| **Auth Required** | Yes |
| **Permission Required** | `inventory.count` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:**

```json
{
  "warehouse_id": 1,
  "items": [
    {
      "product_id": 1,
      "counted_quantity": 28
    },
    {
      "product_id": 2,
      "counted_quantity": 15
    }
  ],
  "notes": "جرد شهر يونيو"
}
```

**Success Response** (`200`):

```json
{
  "message": "تم إجراء الجرد بنجاح",
  "data": {
    "warehouse_id": 1,
    "warehouse_name": "المستودع الرئيسي",
    "counted_items": 2,
    "discrepancies": 1,
    "adjustments": [
      {
        "product_id": 1,
        "product_name": "حاسوب محمول",
        "system_quantity": 25,
        "counted_quantity": 28,
        "difference": 3,
        "adjusted": true
      }
    ]
  }
}
```

**Notes:**
- `counted_quantity` is what the user physically counted
- The system adjusts stock to match the counted quantity
- Discrepancies are logged in audit trail
- Only products included in the request are adjusted

---

### `GET` `/api/inventory/movements`

| Attribute | Value |
|-----------|-------|
| **Purpose** | List inventory movement history |
| **Auth Required** | Yes |
| **Permission Required** | `inventory.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `product_id` | int | Filter by product |
| `warehouse_id` | int | Filter by warehouse |
| `type` | string | Filter by movement type |
| `date_from` | string | Start date |
| `date_to` | string | End date |
| `Page` | int | Page number |
| `PageSize` | int | Items per page |

**Movement Types:**

| Type | Description |
|------|-------------|
| `SALE_OUT` | Sold via sales order |
| `PURCHASE_IN` | Received via purchase order |
| `ADJUSTMENT` | Manual adjustment |
| `STOCK_COUNT` | Stock count reconciliation |
| `TRANSFER_OUT` | Transferred to another warehouse |
| `TRANSFER_IN` | Received from another warehouse |
| `RETURN_IN` | Customer return |
| `RETURN_OUT` | Return to supplier |

**Success Response** (`200`):

```json
{
  "message": "تم جلب حركات المخزون بنجاح",
  "data": [
    {
      "id": 5001,
      "product_id": 1,
      "product_name": "حاسوب محمول",
      "warehouse_id": 1,
      "warehouse_name": "المستودع الرئيسي",
      "type": "SALE_OUT",
      "quantity": -5,
      "reference_type": "sales_order",
      "reference_id": 128,
      "reference_number": "SO-128",
      "notes": "أمر بيع 128",
      "created_by": 1,
      "created_by_name": "مدير النظام",
      "created_at": "2026-06-20T10:30:00Z"
    }
  ],
  "count": 15000,
  "page": 1,
  "pageSize": 20
}
```

**Performance Notes:**
- This table can grow very large (millions of rows)
- Always use date range filters for performant queries
- Consider table partitioning by month or year
- Indexes on: `product_id`, `warehouse_id`, `type`, `created_at`

---

### `GET` `/api/inventory/warehouses`

| Attribute | Value |
|-----------|-------|
| **Purpose** | List all warehouses |
| **Auth Required** | Yes |
| **Permission Required** | `inventory.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Success Response** (`200`):

```json
{
  "message": "تم جلب المستودعات بنجاح",
  "data": [
    {
      "id": 1,
      "name": "المستودع الرئيسي",
      "location": "الرياض",
      "is_active": true
    },
    {
      "id": 2,
      "name": "مستودع جدة",
      "location": "جدة",
      "is_active": true
    }
  ]
}
```

---

### `POST` `/api/inventory/stock/{id}` (Delete)

| Attribute | Value |
|-----------|-------|
| **Purpose** | Delete a specific product-warehouse stock record (set quantity to 0) |
| **Auth Required** | Yes |
| **Permission Required** | `inventory.adjust` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:** None

**Success Response** (`200`):

```json
{
  "message": "تم حذف سجل المخزون بنجاح"
}
```

**Notes:**
- This sets quantity to 0 and creates an adjustment movement record
- Does not delete the product or warehouse

---

## 9. Repairs Endpoints

### `GET` `/api/repairs/orders`

| Attribute | Value |
|-----------|-------|
| **Purpose** | List all repair orders |
| **Auth Required** | Yes |
| **Permission Required** | `sales.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Success Response** (`200`):

```json
{
  "message": "تم جلب أوامر الصيانة بنجاح",
  "data": [
    {
      "id": 15,
      "customer_id": 1,
      "customer_name": "شركة الأمل للتجارة",
      "product_name": "حاسوب محمول Dell",
      "serial_number": "SN-12345-ABCDE",
      "status": "in_progress",
      "problem_description": "الشاشة لا تعمل",
      "diagnosis": "تلف في شاشة LCD",
      "technician_id": 2,
      "technician_name": "أحمد محمد",
      "estimated_cost": 150000,
      "total_cost": 175000,
      "warranty_status": "in_warranty",
      "warranty_expiry": "2027-06-01",
      "created_at": "2026-06-22T09:00:00Z"
    }
  ],
  "count": 50,
  "page": 1,
  "pageSize": 20
}
```

---

### `POST` `/api/repairs/orders`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Create a new repair order |
| **Auth Required** | Yes |
| **Permission Required** | `sales.create` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:**

```json
{
  "customer_id": 1,
  "product_name": "حاسوب محمول Dell",
  "serial_number": "SN-12345-ABCDE",
  "problem_description": "الشاشة لا تعمل والصوت مقطوع",
  "technician_id": 2,
  "estimated_cost": 150000,
  "notes": "العميل يريد الجهاز خلال أسبوع"
}
```

**Success Response** (`201`):

```json
{
  "message": "تم إنشاء أمر الصيانة بنجاح",
  "data": { "id": 16 }
}
```

---

### `POST` `/api/repairs/warranty-check`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Check warranty status for a product by serial number |
| **Auth Required** | Yes |
| **Permission Required** | `sales.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:**

```json
{
  "serial_number": "SN-12345-ABCDE"
}
```

**Success Response** (`200`):

```json
{
  "message": "تم التحقق من الضمان بنجاح",
  "data": {
    "serial_number": "SN-12345-ABCDE",
    "product_name": "حاسوب محمول Dell",
    "warranty_status": "in_warranty",
    "warranty_start": "2025-06-01",
    "warranty_end": "2027-06-01",
    "days_remaining": 342,
    "notes": "الجهاز تحت الضمان"
  }
}
```

**Error Responses:**

| Status | Condition | Message |
|--------|-----------|---------|
| 404 | Serial not found | `{"error": "الرقم التسلسلي غير موجود"}` |
| 400 | Missing serial | `{"error": "الرجاء إدخال الرقم التسلسلي"}` |

---

### `PUT` `/api/repairs/orders/{id}/status`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Update the status of a repair order |
| **Auth Required** | Yes |
| **Permission Required** | `sales.edit` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:**

```json
{
  "status": "completed",
  "diagnosis": "تم استبدال شاشة LCD",
  "total_cost": 175000,
  "notes": "تم إبلاغ العميل"
}
```

**Valid Statuses:**

| Status | Description |
|--------|-------------|
| `pending` | New repair order, awaiting diagnosis |
| `diagnosing` | Technician is diagnosing the issue |
| `waiting_parts` | Waiting for spare parts |
| `in_progress` | Repair in progress |
| `completed` | Repair completed, ready for pickup |
| `delivered` | Delivered to customer |
| `cancelled` | Cancelled |

**Success Response** (`200`):

```json
{
  "message": "تم تحديث حالة أمر الصيانة بنجاح"
}
```

---

### `POST` `/api/repairs/orders/{id}/parts`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Add spare parts used in a repair (deducts from inventory) |
| **Auth Required** | Yes |
| **Permission Required** | `sales.edit` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:**

```json
{
  "parts": [
    {
      "product_id": 50,
      "quantity": 1,
      "unit_price": 25000
    },
    {
      "product_id": 51,
      "quantity": 2,
      "unit_price": 5000
    }
  ]
}
```

**Success Response** (`200`):

```json
{
  "message": "تم إضافة قطع الغيار بنجاح",
  "data": {
    "parts_total": 35000
  }
}
```

**Notes:**
- Parts are deducted from inventory automatically
- If stock is insufficient, the entire request is rejected

---

## 10. Employees Endpoints

### `GET` `/api/employees`

| Attribute | Value |
|-----------|-------|
| **Purpose** | List all employees |
| **Auth Required** | Yes |
| **Permission Required** | `employees.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Success Response** (`200`):

```json
{
  "message": "تم جلب الموظفين بنجاح",
  "data": [
    {
      "id": 1,
      "username": "admin",
      "display_name": "مدير النظام",
      "role_id": 1,
      "role_name": "مدير النظام",
      "phone": "0500000001",
      "email": "admin@erp.com",
      "is_active": true,
      "last_login": "2026-06-24T08:00:00Z",
      "created_at": "2026-01-01T00:00:00Z"
    }
  ],
  "count": 15,
  "page": 1,
  "pageSize": 20
}
```

---

### `POST` `/api/employees`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Create a new employee with login credentials |
| **Auth Required** | Yes |
| **Permission Required** | `employees.manage` |
| **Content-Type** | `application/json; charset=utf-8` |

**Request Body:**

```json
{
  "username": "ahmed.tech",
  "password": "TempP@ss123",
  "display_name": "أحمد محمد",
  "role_id": 3,
  "phone": "0500000010",
  "email": "ahmed@erp.com"
}
```

**Success Response** (`201`):

```json
{
  "message": "تم إنشاء الموظف بنجاح",
  "data": { "id": 16 }
}
```

**Notes:**
- Password is hashed before storage (never stored in plaintext)
- Default password should be changed on first login
- Username must be unique

---

### `GET` `/api/employees/roles`

| Attribute | Value |
|-----------|-------|
| **Purpose** | List all roles with their associated permissions |
| **Auth Required** | Yes |
| **Permission Required** | `employees.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Success Response** (`200`):

```json
{
  "message": "تم جلب الأدوار بنجاح",
  "data": [
    {
      "id": 1,
      "name": "مدير النظام",
      "permissions": ["*"]
    },
    {
      "id": 2,
      "name": "مدير",
      "permissions": [
        "products.*",
        "sales.*",
        "inventory.*",
        "reports.view",
        "audit.view"
      ]
    },
    {
      "id": 3,
      "name": "محرر",
      "permissions": [
        "products.view",
        "products.create",
        "products.edit",
        "sales.view",
        "sales.create"
      ]
    },
    {
      "id": 4,
      "name": "مشاهد",
      "permissions": [
        "products.view",
        "sales.view",
        "inventory.view",
        "reports.view"
      ]
    }
  ]
}
```

---

## 11. Reports Endpoints

### `GET` `/api/reports/dashboard`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Aggregated dashboard data for the home screen |
| **Auth Required** | Yes |
| **Permission Required** | `reports.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Success Response** (`200`):

```json
{
  "message": "تم جلب بيانات لوحة التحكم بنجاح",
  "data": {
    "today_sales_count": 12,
    "today_sales_total": 12500000,
    "today_purchases_count": 3,
    "today_purchases_total": 8500000,
    "pending_repairs": 5,
    "low_stock_items": 8,
    "total_products": 150,
    "total_customers": 85,
    "total_suppliers": 20,
    "monthly_sales_chart": [
      { "month": "2026-01", "total": 15000000 },
      { "month": "2026-02", "total": 18000000 },
      { "month": "2026-03", "total": 22000000 }
    ]
  }
}
```

**Performance Notes:**
- Dashboard data is cached for 5 minutes (TTL cache) to reduce database load
- Calls `refresh_dashboard_cache()` after critical operations (sales, purchases, adjustments)
- Expensive queries (monthly chart) are pre-aggregated

---

### `GET` `/api/reports/sales-timeline`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Sales timeline data for charts (daily, weekly, monthly) |
| **Auth Required** | Yes |
| **Permission Required** | `reports.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `period` | string | `monthly` | `daily`, `weekly`, `monthly`, `yearly` |
| `date_from` | string | 30 days ago | Start date |
| `date_to` | string | today | End date |

**Success Response** (`200`):

```json
{
  "message": "تم جلب بيانات المبيعات بنجاح",
  "data": [
    {
      "period": "2026-06",
      "total": 22000000,
      "count": 45,
      "average": 488889
    }
  ]
}
```

---

### `GET` `/api/reports/sales`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Detailed sales report with totals and breakdowns |
| **Auth Required** | Yes |
| **Permission Required** | `reports.view` |

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `date_from` | string | Start date |
| `date_to` | string | End date |
| `customer_id` | int | Filter by customer |
| `status` | string | Filter by status |

**Success Response** (`200`):

```json
{
  "message": "تم جلب تقرير المبيعات بنجاح",
  "data": {
    "summary": {
      "total_orders": 520,
      "total_sales": 785000000,
      "total_discounts": 25000000,
      "total_tax": 114000000,
      "average_order_value": 1509615
    },
    "by_customer": [
      {
        "customer_id": 1,
        "customer_name": "شركة الأمل للتجارة",
        "order_count": 25,
        "total": 45000000
      }
    ],
    "by_product": [
      {
        "product_id": 1,
        "product_name": "حاسوب محمول",
        "quantity_sold": 100,
        "total_revenue": 15007500
      }
    ]
  }
}
```

---

### `GET` `/api/reports/financial`

| Attribute | Value |
|-----------|-------|
| **Purpose** | Financial report with profit/loss calculations |
| **Auth Required** | Yes |
| **Permission Required** | `reports.view` |

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `date_from` | string | 30 days ago | Start date |
| `date_to` | string | today | End date |

**Success Response** (`200`):

```json
{
  "message": "تم جلب التقرير المالي بنجاح",
  "data": {
    "revenue": 785000000,
    "cost_of_goods_sold": 525000000,
    "gross_profit": 260000000,
    "gross_margin_percent": 33.12,
    "expenses": 0,
    "net_profit": 260000000,
    "total_receivables": 12500000,
    "total_payables": 8500000,
    "net_working_capital": 4000000
  }
}
```

**Notes:**
- COGS is calculated from purchase cost prices of sold items
- Receivables = sum of remaining amounts on credit sales
- Payables = sum of remaining amounts on unpaid purchase orders

---

## 12. Audit Endpoints

### `GET` `/api/audit/logs`

| Attribute | Value |
|-----------|-------|
| **Purpose** | View audit log entries for tracking changes and actions |
| **Auth Required** | Yes |
| **Permission Required** | `audit.view` |
| **Content-Type** | `application/json; charset=utf-8` |

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `user_id` | int | Filter by user |
| `action` | string | Filter by action type |
| `resource` | string | Filter by resource type |
| `date_from` | string | Start date |
| `date_to` | string | End date |
| `Page` | int | Page number |
| `PageSize` | int | Items per page |

**Success Response** (`200`):

```json
{
  "message": "تم جلب سجل التدقيق بنجاح",
  "data": [
    {
      "id": 25000,
      "user_id": 1,
      "username": "admin",
      "action": "CREATE",
      "resource": "sales_order",
      "resource_id": 129,
      "details": "تم إنشاء أمر بيع بقيمة 1,014,125.00 ريال",
      "ip_address": "192.168.1.100",
      "created_at": "2026-06-24T10:30:00Z"
    }
  ],
  "count": 25000,
  "page": 1,
  "pageSize": 50
}
```

**Action Types:**

| Action | Description |
|--------|-------------|
| `CREATE` | Resource created |
| `UPDATE` | Resource updated |
| `DELETE` | Resource deleted |
| `LOGIN` | User logged in |
| `LOGOUT` | User logged out |
| `ADJUST` | Inventory adjustment |
| `RECEIVE` | Purchase order received |
| `STATUS_CHANGE` | Status changed |
| `EXPORT` | Data exported |

**Performance Notes:**
- Audit log can grow very quickly; consider archiving logs older than 1 year
- Always filter by date range for performant queries
- Index on: `user_id`, `action`, `resource`, `created_at`
- Long text fields (details) should be stored as TEXT with full-text search consideration

---

## Error Response Reference

### Common Error Codes

| Code | Meaning | Typical Cause |
|------|---------|---------------|
| `400` | Bad Request | Invalid JSON, missing fields, validation errors |
| `401` | Unauthorized | Session expired, not logged in |
| `403` | Forbidden | User lacks required permission |
| `404` | Not Found | Resource ID does not exist |
| `409` | Conflict | Duplicate unique field (SKU, email, etc.) |
| `422` | Unprocessable Entity | Business rule violation |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Error | Unexpected server failure |

### Standard Error Body

```json
{
  "error": "رسالة الخطأ باللغة العربية"
}
```

For validation errors with field-specific messages:

```json
{
  "error": "بيانات غير صحيحة",
  "fields": {
    "name": "حقل الاسم مطلوب",
    "price": "يجب أن يكون السعر رقماً صحيحاً موجباً",
    "sku": "رمز SKU موجود مسبقاً"
  }
}
```

---

## Endpoint Summary Table

| Method | URL | Auth | Permission |
|--------|-----|------|------------|
| POST | `/api/auth/login` | No | None |
| POST | `/api/auth/logout` | Yes | None |
| GET | `/api/auth/me` | Yes | None |
| GET | `/api/products` | Yes | `products.view` |
| POST | `/api/products` | Yes | `products.create` |
| GET | `/api/products/{id}` | Yes | `products.view` |
| PUT | `/api/products/{id}` | Yes | `products.edit` |
| DELETE | `/api/products/{id}` | Yes | `products.delete` |
| GET | `/api/products/categories` | Yes | `products.view` |
| GET | `/api/products/brands` | Yes | `products.view` |
| GET | `/api/products/taxes` | Yes | `products.view` |
| GET | `/api/customers` | Yes | `sales.view` |
| POST | `/api/customers` | Yes | `sales.create` |
| GET | `/api/customers/{id}` | Yes | `sales.view` |
| PUT | `/api/customers/{id}` | Yes | `sales.edit` |
| DELETE | `/api/customers/{id}` | Yes | `sales.delete` |
| GET | `/api/suppliers` | Yes | `inventory.view` |
| POST | `/api/suppliers` | Yes | `inventory.adjust` |
| GET | `/api/suppliers/{id}` | Yes | `inventory.view` |
| PUT | `/api/suppliers/{id}` | Yes | `inventory.adjust` |
| DELETE | `/api/suppliers/{id}` | Yes | `inventory.adjust` |
| GET | `/api/sales/orders` | Yes | `sales.view` |
| POST | `/api/sales/orders` | Yes | `sales.create` |
| GET | `/api/sales/orders/{id}` | Yes | `sales.view` |
| GET | `/api/purchases/orders` | Yes | `inventory.view` |
| POST | `/api/purchases/orders` | Yes | `inventory.adjust` |
| POST | `/api/purchases/orders/{id}/receive` | Yes | `inventory.adjust` |
| GET | `/api/purchases/orders/{id}` | Yes | `inventory.view` |
| GET | `/api/inventory/stock` | Yes | `inventory.view` |
| GET | `/api/inventory/stock/{id}` | Yes | `inventory.view` |
| DELETE | `/api/inventory/stock/{id}` | Yes | `inventory.adjust` |
| POST | `/api/inventory/adjust` | Yes | `inventory.adjust` |
| POST | `/api/inventory/stock-count` | Yes | `inventory.count` |
| GET | `/api/inventory/movements` | Yes | `inventory.view` |
| GET | `/api/inventory/warehouses` | Yes | `inventory.view` |
| GET | `/api/repairs/orders` | Yes | `sales.view` |
| POST | `/api/repairs/orders` | Yes | `sales.create` |
| POST | `/api/repairs/warranty-check` | Yes | `sales.view` |
| PUT | `/api/repairs/orders/{id}/status` | Yes | `sales.edit` |
| POST | `/api/repairs/orders/{id}/parts` | Yes | `sales.edit` |
| GET | `/api/employees` | Yes | `employees.view` |
| POST | `/api/employees` | Yes | `employees.manage` |
| GET | `/api/employees/roles` | Yes | `employees.view` |
| GET | `/api/reports/dashboard` | Yes | `reports.view` |
| GET | `/api/reports/sales-timeline` | Yes | `reports.view` |
| GET | `/api/reports/sales` | Yes | `reports.view` |
| GET | `/api/reports/financial` | Yes | `reports.view` |
| GET | `/api/audit/logs` | Yes | `audit.view` |
