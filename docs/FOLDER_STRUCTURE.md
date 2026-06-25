# Folder Structure — ERP POS System

> **Version:** 1.0  
> **Last Updated:** 2026-06-24  
> **Audience:** All Developers, DevOps, New Team Members

---

## Table of Contents

1. [Complete Directory Tree](#1-complete-directory-tree)
2. [Root Files](#2-root-files)
3. [docs/ Directory](#3-docs-directory)
4. [database/ Directory](#4-database-directory)
5. [routes/ Directory](#5-routes-directory)
6. [services/ Directory](#6-services-directory)
7. [utils/ Directory](#7-utils-directory)
8. [static/ Directory](#8-static-directory)
9. [templates/ Directory](#9-templates-directory)
10. [flask_session/ Directory](#10-flask_session-directory)
11. [Docker Configuration](#11-docker-configuration)
12. [File Naming Conventions](#12-file-naming-conventions)
13. [Import Map](#13-import-map)
14. [New Module Checklist](#14-new-module-checklist)
15. [Refactoring Guidelines](#15-refactoring-guidelines)

---

## 1. Complete Directory Tree

```
erp-system/
│
├── app.py                          # Application factory & entry point
├── config.py                       # Configuration classes (dev, test, prod)
├── .env                            # Environment variables (gitignored)
├── requirements.txt                # Python package dependencies
├── Dockerfile                      # Docker image definition
├── docker-compose.yml              # Multi-container orchestration
├── .gitignore                      # Git ignore rules
├── README.md                       # Project overview & setup guide
│
├── docs/                           # System documentation
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── SOFTWARE_ARCHITECTURE.md
│   ├── FOLDER_STRUCTURE.md
│   └── CODING_STANDARDS.md
│
├── database/                       # Database layer
│   ├── connection.py               # Connection management (get_db, close_db)
│   ├── schema.sql                  # Complete DDL schema
│   ├── seed.py                     # Seed data (demo/default records)
│   └── migrations/                 # Database migration scripts (future)
│       └── 001_initial_schema.sql
│
├── routes/                         # Flask blueprints (presentation/API layer)
│   ├── __init__.py                 # Empty (package marker)
│   ├── auth.py                     # Authentication & authorization
│   ├── products.py                 # Product CRUD & barcode management
│   ├── customers.py                # Customer management
│   ├── suppliers.py                # Supplier management
│   ├── sales.py                    # Sales order processing
│   ├── purchases.py                # Purchase order processing
│   ├── inventory.py                # Stock management & adjustments
│   ├── repairs.py                  # Repair order management
│   ├── employees.py                # Employee & schedule management
│   ├── reports.py                  # Reporting & analytics
│   └── audit.py                    # Audit log viewer & search
│
├── services/                       # Business logic layer
│   ├── __init__.py                 # Service registry & exports
│   ├── auth_service.py             # User authentication, password hashing, sessions
│   ├── sales_service.py            # Sales creation, refunds, holds, history
│   ├── purchase_service.py         # Purchase orders, receiving, supplier returns
│   ├── stock_engine.py             # Stock management: deduction, addition, transfer
│   ├── audit_service.py            # Audit logging: events, search, export
│   ├── repair_service.py           # Repair lifecycle: intake, diagnosis, completion
│   ├── warranty_service.py         # Warranty validation & claim processing
│   └── accounting_service.py       # Financial calculations, tax, P&L reports
│
├── utils/                          # Shared utilities & cross-cutting concerns
│   ├── __init__.py                 # Empty (package marker)
│   ├── decorators.py               # login_required, require_permission, cache_response
│   └── helpers.py                  # Validation, formatting, cache, error responses
│
├── static/                         # Static assets (served by Nginx in prod)
│   ├── css/
│   │   ├── style.css               # Main stylesheet
│   │   ├── print.css               # Print-specific styles (receipts, reports)
│   │   └── dark.css                # Dark mode theme (optional)
│   └── js/
│       ├── app.js                  # Global application state & utilities
│       ├── sales.js                # Sales page interactivity
│       ├── inventory.js            # Inventory management UI
│       └── reports.js              # Report filtering & chart rendering
│
├── templates/                      # Jinja2 HTML templates
│   ├── base.html                   # Base template (layout, nav, flash messages)
│   ├── index.html                  # Dashboard / home page
│   ├── components/                 # Reusable template components
│   │   ├── pagination.html         # Pagination component
│   │   ├── search_bar.html         # Search bar with filters
│   │   ├── modal.html              # Generic modal dialog
│   │   ├── confirm_dialog.html     # Confirmation dialog
│   │   └── flash_messages.html     # Flash message renderer
│   ├── auth/                       # Authentication templates
│   │   ├── login.html
│   │   ├── change_password.html
│   │   └── reset_password.html
│   ├── products/                   # Product management templates
│   │   ├── list.html
│   │   ├── create.html
│   │   ├── edit.html
│   │   ├── detail.html
│   │   └── import.html
│   ├── customers/                  # Customer management templates
│   │   ├── list.html
│   │   ├── create.html
│   │   ├── edit.html
│   │   └── detail.html
│   ├── suppliers/                  # Supplier management templates
│   │   ├── list.html
│   │   ├── create.html
│   │   ├── edit.html
│   │   └── detail.html
│   ├── sales/                      # Sales templates
│   │   ├── new.html                # POS terminal (main cashier view)
│   │   ├── complete.html           # Sale confirmation & receipt
│   │   ├── detail.html             # Sale detail view
│   │   ├── history.html            # Sales history with filters
│   │   └── refund.html             # Refund processing
│   ├── purchases/                  # Purchase order templates
│   │   ├── list.html
│   │   ├── new.html
│   │   ├── receive.html            # Receiving goods against PO
│   │   └── detail.html
│   ├── inventory/                  # Inventory templates
│   │   ├── stock_levels.html
│   │   ├── adjust.html
│   │   ├── transfer.html
│   │   ├── count.html              # Physical inventory count
│   │   └── history.html
│   ├── repairs/                    # Repair order templates
│   │   ├── list.html
│   │   ├── new.html
│   │   ├── detail.html
│   │   └── complete.html
│   ├── employees/                  # Employee management templates
│   │   ├── list.html
│   │   ├── create.html
│   │   ├── edit.html
│   │   ├── schedule.html
│   │   └── clock.html              # Clock in/out interface
│   ├── reports/                    # Report templates
│   │   ├── daily_sales.html
│   │   ├── inventory_reports.html
│   │   ├── profit_loss.html
│   │   ├── tax_report.html
│   │   └── custom_report.html
│   ├── audit/                      # Audit log templates
│   │   ├── log.html
│   │   └── search.html
│   └── errors/                     # Error page templates
│       ├── 400.html
│       ├── 403.html
│       ├── 404.html
│       └── 500.html
│
└── flask_session/                  # Server-side session files (gitignored)
                                    # Created at runtime by Flask-Session
```

---

## 2. Root Files

### `app.py` — Application Factory

**Purpose**: Application entry point. Creates and configures the Flask application instance.

**Contents**:
- `create_app()` function that returns a configured Flask app
- Registration of all blueprints with URL prefixes
- Registration of error handlers (400, 403, 404, 500)
- Registration of database teardown (`close_db`)
- Security headers middleware (CSP, HSTS, X-Frame-Options)
- Request timing and logging middleware
- `if __name__ == "__main__"` block for development server

**Relationships**:
- Imports `config` for configuration
- Imports all `routes.*` blueprints
- Imports `database.connection.init_app` for teardown
- The application factory pattern allows creating multiple instances (for testing, different configurations)

```python
# app.py structure (conceptual)

from flask import Flask

def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    from database.connection import init_app as init_db
    init_db(app)

    # Register blueprints
    from routes.auth import auth_bp
    # ... register all blueprints

    # Register error handlers
    register_error_handlers(app)

    # Register middleware
    register_middleware(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
```

**Key Design Decisions**:
- Factory pattern enables testing with different configs
- Blueprints are registered here so they can be independently unit-tested
- Error handlers are centralized, not scattered across blueprints

---

### `config.py` — Configuration Classes

**Purpose**: Centralized configuration management using Python classes.

**Contents**:

```python
import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration shared by all environments."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = os.path.join(BASE_DIR, "flask_session")
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_USE_SIGNER = True
    DATABASE_PATH = os.path.join(BASE_DIR, "database", "erp.db")
    DB_CACHE_SIZE_MB = 64
    WTF_CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_TYPE = "filesystem"
    DATABASE_PATH = os.path.join(BASE_DIR, "database", "erp_dev.db")


class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = ":memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    SESSION_TYPE = "redis"
    SESSION_REDIS = os.environ.get("REDIS_URL", "redis://localhost:6379")
    DATABASE_PATH = os.environ.get(
        "DATABASE_URL",
        os.path.join(BASE_DIR, "database", "erp.db")
    )


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
```

**Relationships**:
- Used by `app.py` to configure the Flask app
- Used by `database/connection.py` for `DATABASE_PATH`
- Used by session configuration
- Environment variable `FLASK_ENV` selects the active config

---

### `.env` — Environment Variables

**Purpose**: Local environment configuration. **Never committed to git.**

**Contents**:

```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///database/erp.db
REDIS_URL=
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
BACKUP_ENCRYPTION_KEY=
BACKUP_S3_BUCKET=
BACKUP_S3_ACCESS_KEY=
BACKUP_S3_SECRET_KEY=
```

**Security Notes**:
- The `.env` file is listed in `.gitignore`
- Production secrets are injected via Docker secrets or CI/CD variables
- `SECRET_KEY` must be at least 32 bytes of random data: `python -c "import secrets; print(secrets.token_hex(32))"`

---

### `requirements.txt` — Python Dependencies

**Purpose**: Pinned dependencies for reproducible builds.

```
Flask>=3.0,<4.0
Flask-Session>=0.8,<1.0
Flask-WTF>=1.2,<2.0
WTForms>=3.1,<4.0
python-escpos>=3.1,<4.0
Pillow>=10.0,<11.0
qrcode>=7.4,<8.0
gunicorn>=22.0,<23.0
psycopg2-binary>=2.9,<3.0
redis>=5.0,<6.0
python-dotenv>=1.0,<2.0
bcrypt>=4.1,<5.0
pyotp>=2.9,<3.0
python-barcode>=0.15,<1.0
openpyxl>=3.1,<4.0
reportlab>=4.1,<5.0
```

**Dependency Categories**:
| Package | Version | Purpose |
|---------|---------|---------|
| `Flask` | 3.x | Web framework |
| `Flask-Session` | 0.8+ | Server-side sessions |
| `Flask-WTF` | 1.2+ | CSRF protection + form handling |
| `python-escpos` | 3.1+ | Thermal receipt printer ESC/POS protocol |
| `Pillow` | 10+ | Image processing for barcode labels |
| `qrcode` | 7.4+ | QR code generation for receipts |
| `gunicorn` | 22+ | Production WSGI server |
| `psycopg2-binary` | 2.9+ | PostgreSQL adapter |
| `redis` | 5+ | Redis client for production sessions |
| `bcrypt` | 4.1+ | Password hashing |
| `pyotp` | 2.9+ | TOTP for MFA |
| `openpyxl` | 3.1+ | Excel import/export |
| `reportlab` | 4.1+ | PDF invoice generation |

---

### `.gitignore`

**Purpose**: Prevent committing secrets, generated files, and OS artifacts.

```
# Environment
.env
*.env.local

# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
venv/

# Database
*.db
*.sqlite3
database/migrations/*.pyc

# Session files
flask_session/*

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Docker
.dockerignore
```

---

### `README.md`

**Purpose**: Project entry point for new developers. Contains setup instructions, architecture overview, and links to detailed docs.

**Contents**:
- Project description and features
- Quick start guide (5 commands to get running)
- Prerequisites (Python 3.12+, Docker)
- Development setup steps
- Configuration guide
- Deployment instructions
- Links to `docs/` for detailed documentation

---

## 3. docs/ Directory

**Purpose**: Centralized documentation for all aspects of the system.

| File | Audience | Lines | Covers |
|------|----------|-------|--------|
| `SYSTEM_ARCHITECTURE.md` | Architects, DevOps | 400+ | C4 diagrams, deployment, security, HA, DR, scalability |
| `SOFTWARE_ARCHITECTURE.md` | Developers, Tech Leads | 400+ | Layers, modules, request flow, patterns, caching, error handling |
| `FOLDER_STRUCTURE.md` | All developers | 250+ | Every file explained, import map, conventions |
| `CODING_STANDARDS.md` | All developers | 300+ | PEP 8, naming, docstrings, testing, security, code review |

**Maintenance Rules**:
- Docs are part of the repo and must be updated with code changes
- Any architectural decision must be documented in the relevant file
- Code review checklist includes "Are docs updated?"
- Outdated docs are worse than no docs — update or delete

---

## 4. database/ Directory

### `database/connection.py` — Database Connection Manager

**Purpose**: Manages database connection lifecycle per-request using Flask's application context.

**Key Functions**:

| Function | Purpose |
|----------|---------|
| `get_db()` | Returns the database connection for the current request. Creates one if it doesn't exist |
| `close_db(error)` | Closes the connection at the end of the request. Registered as `teardown_appcontext` |
| `init_app(app)` | Registers `close_db` with the Flask app |

**Key Behaviors**:
- Connection is stored in `g.db` (Flask application context) — one connection per request
- SQLite PRAGMAs are set on every new connection: WAL mode, foreign keys, busy timeout, cache size
- Row factory is `sqlite3.Row` for dict-like access
- No connection pooling needed for SQLite (single writer mode is fine)
- For PostgreSQL, `psycopg2.pool.ThreadedConnectionPool` is used instead

**Edge Cases Handled**:
- If `close_db` is called twice, the second call is a no-op
- If the database file doesn't exist, SQLite creates it automatically (development)
- If the database is locked, `busy_timeout = 5000` causes it to wait 5 seconds before raising an error
- Connection errors are logged and re-raised as `RuntimeError`

---

### `database/schema.sql` — Database Schema

**Purpose**: Complete DDL for all tables, indexes, triggers, and views.

**Contents** (conceptual — exact schema is defined in the file):

```sql
-- Core tables
CREATE TABLE users (...);
CREATE TABLE roles (...);
CREATE TABLE user_roles (...);
CREATE TABLE permissions (...);

-- Products
CREATE TABLE categories (...);
CREATE TABLE products (...);
CREATE TABLE product_prices (...);
CREATE TABLE barcodes (...);

-- Customers & Suppliers
CREATE TABLE customers (...);
CREATE TABLE suppliers (...);

-- Sales
CREATE TABLE sales (...);
CREATE TABLE sale_items (...);
CREATE TABLE payments (...);
CREATE TABLE holds (...);

-- Purchases
CREATE TABLE purchase_orders (...);
CREATE TABLE purchase_items (...);
CREATE TABLE receiving_reports (...);

-- Inventory
CREATE TABLE store_stock (...);
CREATE TABLE stock_movements (...);
CREATE TABLE stock_transfers (...);
CREATE TABLE inventory_counts (...);

-- Repairs
CREATE TABLE repairs (...);
CREATE TABLE repair_parts (...);
CREATE TABLE warranties (...);

-- Employees
CREATE TABLE employees (...);
CREATE TABLE attendance (...);
CREATE TABLE employee_schedules (...);

-- Audit
CREATE TABLE audit_log (...);

-- System
CREATE TABLE store_config (...);
CREATE TABLE backup_log (...);
```

**Key Design Decisions**:
- All tables use `INTEGER PRIMARY KEY` (SQLite auto-increment)
- Timestamps use TEXT with ISO 8601 format (SQLite has no native datetime type)
- Monetary values use REAL with application-level Decimal handling (or NUMERIC with PostgreSQL)
- All foreign keys are indexed
- Soft deletes via `active` boolean column where appropriate
- Audit log is a separate table, not a trigger-based system (simpler, more portable)

---

### `database/seed.py` — Seed Data

**Purpose**: Populate the database with initial/default data for development and demo.

**Seeded Data**:
- Admin user (username: `admin`, password: `admin123` — **change in production**)
- Default roles and permissions (Admin, Manager, Cashier)
- 2-3 demo product categories (Electronics, Accessories, Services)
- 10-15 demo products with realistic names and prices
- 2-3 demo customers
- 1 demo supplier
- Store configuration defaults (tax rate, currency, store name)

**Relationship**: Run once after schema creation. Can be run multiple times (idempotent via `INSERT OR IGNORE`).

---

### `database/migrations/` — Migration Scripts

**Purpose**: Future database migrations for schema changes.

**Current State**: Empty directory with one initial migration file.

**Naming Convention**: `{sequence_number}_{description}.sql`

```
001_initial_schema.sql
002_add_user_preferences.sql
003_add_loyalty_points.sql
```

**Migration Philosophy**:
- For v1.0, schema changes are made directly to `schema.sql`
- When the system is in production with real data, migrations are required
- No migration framework is used yet (simplicity). Simple version-tracked SQL files
- A `schema_version` table tracks applied migrations

---

## 5. routes/ Directory

**Purpose**: Presentation/API layer. Flask blueprints that handle HTTP request/response.

### `routes/__init__.py`

**Purpose**: Package marker. Empty file.

---

### `routes/auth.py` — Authentication Blueprint

**Purpose**: User login, logout, password management, session handling.

**Routes**:

| Route | Methods | Description |
|-------|---------|-------------|
| `/auth/login` | GET, POST | Login form and authentication |
| `/auth/logout` | POST | Session destruction |
| `/auth/change-password` | GET, POST | Password change (authenticated) |
| `/auth/reset-password` | GET, POST | Password reset via email |
| `/auth/profile` | GET | View current user profile |

**Key Behaviors**:
- Login rate-limited: 5 attempts per IP per 15 minutes (`limits` from Flask-Limiter)
- Failed login logged to audit log
- Successful login updates `last_login` timestamp
- Logout clears session server-side

**Edge Cases**:
- Already logged-in user accessing login page → redirect to dashboard
- Session expired during long operation → redirect to login, preserve intended URL in `next` param
- Account locked after 5 failures → show lockout message with remaining time

---

### `routes/products.py` — Products Blueprint

**Purpose**: Product catalog management.

**Routes**:

| Route | Methods | Description |
|-------|---------|-------------|
| `/products` | GET | Product list with pagination, search, filter |
| `/products/create` | GET, POST | Create new product |
| `/products/<id>/edit` | GET, POST | Edit existing product |
| `/products/<id>` | GET | Product detail view |
| `/products/<id>/delete` | POST | Soft-delete product |
| `/products/import` | GET, POST | Bulk import from CSV/Excel |
| `/products/export` | GET | Export products to CSV |
| `/products/barcode/<barcode>` | GET | Lookup product by barcode (AJAX) |
| `/products/search` | GET | JSON search for autocomplete (AJAX) |

**Key Behaviors**:
- Barcode lookup returns JSON for POS scanning
- Search endpoint returns limited fields (id, name, barcode, price, stock)
- Product create/edit validates SKU uniqueness server-side
- Import processes 500 rows per batch with progress feedback

**Edge Cases**:
- Barcode scanned that doesn't exist → show "Product not found" with option to create
- Duplicate SKU in import → skip that row, report error in summary
- Product with existing sales cannot be hard-deleted → soft delete only
- Stock display shows current, committed (in active sales), and available quantities

---

### `routes/customers.py` — Customers Blueprint

**Purpose**: Customer management.

**Routes**: `LIST`, `CREATE`, `EDIT`, `DETAIL`, `SEARCH` (AJAX)

**Edge Cases**:
- Customer with linked sales cannot be deleted → soft delete with `active = 0`
- Duplicate phone number → warn but allow (same family sharing a phone)
- Customer search returns max 20 results for autocomplete performance

---

### `routes/suppliers.py` — Suppliers Blueprint

**Purpose**: Supplier management.

**Routes**: `LIST`, `CREATE`, `EDIT`, `DETAIL`

**Edge Cases**:
- Deactivating a supplier with pending POs → warn manager before deactivation
- Supplier product count displayed in list view for reference

---

### `routes/sales.py` — Sales Blueprint

**Purpose**: Point-of-sale operations.

**Routes**:

| Route | Methods | Description |
|-------|---------|-------------|
| `/sales/new` | GET, POST | POS terminal — new sale |
| `/sales/<id>/complete` | GET, POST | Complete/confirm sale |
| `/sales/<id>/receipt` | GET | Print receipt |
| `/sales/<id>/email` | POST | Email receipt to customer |
| `/sales/<id>/refund` | GET, POST | Process refund |
| `/sales/<id>` | GET | Sale detail |
| `/sales/history` | GET | Filterable sales history |
| `/sales/hold` | POST | Hold current sale |
| `/sales/holds` | GET | View held sales |
| `/sales/resume/<hold_id>` | GET | Resume held sale |

**Key Behaviors**:
- POS terminal (`/sales/new`) is a single-page interface with item search, cart, payment
- Item addition via barcode scan or search autocomplete
- Multiple payment methods per sale (cash + card split)
- Hold/resume saves incomplete sale to database with 30-minute expiry
- Receipt printing via `python-escpos` to configured printer
- All prices displayed with store currency symbol

**Edge Cases**:
- Sale in progress when session times out → sale discarded, warning shown on next login
- Barcode scanner inputs faster than JS can process → debounce scanner input (200ms buffer)
- Negative total after discounts → validation prevents total below zero
- Split payment that overpays → validation catches mismatch
- Held sale expired (30 min) → show as expired, cannot resume, must create new sale

---

### `routes/purchases.py` — Purchases Blueprint

**Purpose**: Purchase order management.

**Routes**: `LIST`, `NEW`, `RECEIVE`, `DETAIL`

**Key Behaviors**:
- Purchase order creation based on low-stock alerts or manual entry
- Receiving goods updates stock and records actual quantities received
- Partial receiving supported (receive 50 of 100 ordered)
- Price variance between PO and actual flagged for manager review

**Edge Cases**:
- Received quantity exceeds ordered → require manager override
- Product discontinued before receipt → allow but flag
- Supplier delivers substitute product → manual override, new line item

---

### `routes/inventory.py` — Inventory Blueprint

**Purpose**: Stock management and adjustments.

**Routes**: `STOCK_LEVELS`, `ADJUST`, `TRANSFER`, `COUNT`, `HISTORY`

**Key Behaviors**:
- Stock adjustment requires reason code and optional manager approval
- Transfers between stores (multi-store mode)
- Physical inventory count with variance reporting
- Stock movement history with date range filters

**Edge Cases**:
- Adjustment to zero stock → confirmation dialog required
- Count variance > 5% → auto-flag for manager review
- Transfer to non-existent store → validation error
- Concurrent count entries → last write wins with audit trail

---

### `routes/repairs.py` — Repairs Blueprint

**Purpose**: Repair order management for service businesses.

**Routes**: `LIST`, `NEW`, `DETAIL`, `COMPLETE`

**Key Behaviors**:
- Repair intake: customer info, device details, reported issue, initial diagnosis
- Status tracking: received → diagnosed → awaiting parts → in repair → complete → ready for pickup
- Part usage deducted from inventory
- Labor costs tracked separately from parts
- Customer notification on status changes (future: SMS/email)

**Edge Cases**:
- Customer picks up without repair being marked complete → process requires completion first
- Parts needed not in stock → place purchase order automatically (optional)
- Repair abandoned by customer → set to abandoned after 90 days, notify manager

---

### `routes/employees.py` — Employees Blueprint

**Purpose**: Employee management and attendance.

**Routes**: `LIST`, `CREATE`, `EDIT`, `SCHEDULE`, `CLOCK`

**Key Behaviors**:
- Employee profiles with contact info, role, hire date
- Clock in/out with geolocation (optional) and IP logging
- Schedule management with shift templates
- Attendance reports with late arrivals, early departures, absences

**Edge Cases**:
- Employee clocked in from two locations simultaneously → flag for investigation
- Missed clock out → auto-clock out at midnight (configurable)
- Schedule conflict → warn when assigning overlapping shifts

---

### `routes/reports.py` — Reports Blueprint

**Purpose**: Business reporting and analytics.

**Routes**: `DAILY_SALES`, `INVENTORY_REPORTS`, `PROFIT_LOSS`, `TAX_REPORT`, `CUSTOM_REPORT`

**Key Behaviors**:
- All reports filterable by date range, store, category
- Reports cached with 5-minute TTL for performance
- CSV export option on all reports
- PDF export for formal reports (invoices, P&L)
- Custom report builder: select columns, filters, grouping, sorting

**Edge Cases**:
- Report with no data in date range → show empty state, not an error
- Large date range (1 year) → show warning, suggest shorter range if > 100K rows
- Real-time report vs cached → manual refresh button clears cache for current user

---

### `routes/audit.py` — Audit Blueprint

**Purpose**: Audit log viewer.

**Routes**: `LOG`, `SEARCH`, `EXPORT`

**Key Behaviors**:
- Read-only interface (audit logs are immutable)
- Filters: event type, user, date range, resource type
- Search by user ID, resource ID, or event details
- Export to CSV for compliance purposes
- Paginated with 100 rows per page

**Edge Cases**:
- Attempt to delete audit log → 403 Forbidden (no delete endpoint exists)
- Search in 1M+ records → indexed by `(created_at, event_type, user_id)`, search limited to 30-day range by default

---

## 6. services/ Directory

**Purpose**: Business logic layer. All domain rules and data transformations live here.

### `services/__init__.py` — Service Registry

**Purpose**: Creates singleton service instances and exports them for import by routes.

**Pattern**: Lazy initialization with dependency injection:

```python
from services.auth_service import AuthService
from services.sales_service import SalesService
from services.stock_engine import StockEngine
from services.audit_service import AuditService

# Singleton instances with explicit dependency injection
_stock_engine = None
_audit_service = None


def get_stock_engine() -> StockEngine:
    global _stock_engine
    if _stock_engine is None:
        _stock_engine = StockEngine()
    return _stock_engine


def get_audit_service() -> AuditService:
    global _audit_service
    if _audit_service is None:
        _audit_service = AuditService()
    return _audit_service


# Convenience imports for route files
stock_engine = get_stock_engine()
audit_service = get_audit_service()
sales_service = SalesService(stock_engine=stock_engine)
```

**Why singletons?** Services are stateless — no instance data that changes between requests. Creating a new instance per request adds GC pressure with no benefit.

---

### `services/auth_service.py` — Authentication Service

**Purpose**: User authentication, password hashing, session management.

**Key Functions**:

| Function | Description |
|----------|-------------|
| `authenticate(username, password)` | Verify credentials. Returns user dict or raises ValueError |
| `hash_password(password)` | Generate bcrypt hash with cost factor 12 |
| `verify_password(password, hash)` | Check password against hash |
| `change_password(user_id, old_password, new_password)` | Validate old, update to new. Invalidates other sessions |
| `reset_password(email)` | Generate reset token, send email |
| `get_user_permissions(user_id)` | Return list of permission strings for RBAC |
| `record_login_attempt(username, success, ip)` | Log attempt, check lockout status |

**Edge Cases**:
- Password hash migration: if detecting old hash format, re-hash on next login
- Account lockout: 5 failed attempts → locked for 15 minutes. Tracked by username + IP
- Concurrent logins: same user logs in from two terminals. Both sessions active. Only invalidated on password change

---

### `services/sales_service.py` — Sales Service

**Purpose**: Sales creation, refund, hold/resume, history.

**Key Functions**:

| Function | Description | Involves Transaction? |
|----------|-------------|----------------------|
| `create_sale(cashier_id, customer_id, items, payments)` | Process complete sale | Yes |
| `refund_sale(sale_id, cashier_id, reason)` | Full refund of a sale | Yes |
| `partial_refund(sale_id, item_ids, cashier_id, reason)` | Return specific items | Yes |
| `hold_sale(sale_data)` | Save incomplete sale to holds table | Yes |
| `resume_sale(hold_id)` | Load held sale, delete hold record | Yes |
| `get_sale_detail(sale_id)` | Full sale with items, payments | No |
| `search_sales(filters, page)` | Paginated, filterable sale history | No |
| `get_daily_summary(date, store_id)` | Aggregated daily totals | No |

---

### `services/purchase_service.py` — Purchase Service

**Purpose**: Purchase order lifecycle management.

**Key Functions**:

| Function | Description | Transaction? |
|----------|-------------|--------------|
| `create_purchase_order(supplier_id, items, user_id)` | Create PO with expected items | Yes |
| `receive_goods(po_id, received_items, user_id)` | Record receipt, update stock | Yes |
| `close_purchase_order(po_id)` | Mark PO as completed | Yes |
| `get_pending_orders()` | Open POs not yet fully received | No |
| `get_supplier_performance(supplier_id)` | On-time delivery stats | No |

---

### `services/stock_engine.py` — Stock Engine

**Purpose**: Core inventory management with atomic operations.

**Key Functions**:

| Function | Description | Transaction? |
|----------|-------------|--------------|
| `check_availability(product_id, quantity, store_id, cursor)` | Check if stock >= quantity. Returns available count or False | No (uses existing TX) |
| `deduct(product_id, quantity, store_id, cursor, reference_type, reference_id)` | Deduct stock atomically. Raises ValueError if insufficient | No (uses existing TX) |
| `add(product_id, quantity, store_id, cursor, reference_type, reference_id)` | Add stock (receiving, return, adjustment) | No (uses existing TX) |
| `transfer(product_id, from_store, to_store, quantity, user_id)` | Transfer between stores | Yes |
| `adjust(product_id, store_id, new_quantity, reason, user_id)` | Set stock to specific value | Yes |
| `get_stock_level(product_id, store_id)` | Current stock level | No |
| `get_low_stock_items(threshold, store_id)` | Items below reorder point | No |

**Critical Design**: `deduct()` and `add()` accept an existing cursor from the caller's transaction. This ensures stock operations are part of the same transaction as the sale or purchase that triggers them.

```python
def deduct(self, product_id, quantity, store_id, cursor,
           reference_type="sale", reference_id=None):
    """
    Atomically deduct stock. Must be called within an active transaction.
    The cursor is provided by the caller who owns the transaction.
    """
    cursor.execute(
        "UPDATE store_stock SET quantity = quantity - ? "
        "WHERE product_id = ? AND store_id = ? AND quantity >= ?",
        (quantity, product_id, store_id, quantity)
    )
    if cursor.rowcount == 0:
        raise ValueError(f"Insufficient stock for product {product_id}")

    # Record movement for audit
    cursor.execute("""
        INSERT INTO stock_movements
            (product_id, store_id, quantity_change, reference_type,
             reference_id, created_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (product_id, store_id, -quantity, reference_type, reference_id))
```

---

### `services/audit_service.py` — Audit Service

**Purpose**: Immutable audit logging for all data modifications.

**Key Functions**: `log_event()`, `get_events()`, `export_events()` (see Software Architecture section for full detail)

---

### `services/repair_service.py` — Repair Service

**Purpose**: Repair order management.

**Key Functions**:

| Function | Description | Transaction? |
|----------|-------------|--------------|
| `create_repair(customer_id, device, issue, cashier_id)` | Intake a new repair | Yes |
| `update_status(repair_id, status, user_id)` | Change repair status | Yes |
| `add_part(repair_id, part_id, quantity, user_id)` | Use parts from inventory | Yes |
| `complete_repair(repair_id, resolution, labor_cost, user_id)` | Mark as complete | Yes |
| `get_customer_history(customer_id)` | All repairs for a customer | No |

**Repair Status Flow**:
```
Received → Diagnosed → Awaiting Parts → In Repair → Complete → Ready for Pickup → Picked Up
```

---

### `services/warranty_service.py` — Warranty Service

**Purpose**: Warranty validation and claim processing.

**Key Functions**: `validate_warranty(product_id, sale_date, current_date)`, `register_warranty(sale_id, product_id, duration_days)`, `process_claim(repair_id, warranty_id)`

---

### `services/accounting_service.py` — Accounting Service

**Purpose**: Financial calculations and reports.

**Key Functions**: `calculate_profit_loss(start_date, end_date)`, `calculate_tax_liability(start_date, end_date)`, `get_cost_of_goods_sold(start_date, end_date)`, `get_revenue_by_category(start_date, end_date)`

---

## 7. utils/ Directory

**Purpose**: Shared utilities used across routes and services.

### `utils/__init__.py`

**Purpose**: Package marker. Empty.

---

### `utils/decorators.py` — Decorators

**Purpose**: Middleware decorators for route protection and behavior.

**Decorators Provided**:

| Decorator | Purpose | Applied To |
|-----------|---------|------------|
| `login_required` | Redirects to login if not authenticated | All routes except auth |
| `require_permission(perm)` | 403 if user lacks specific permission | Routes needing authorization |
| `cache_response(ttl)` | Cache GET responses for TTL seconds | Report routes, product list |
| `ajax_required` | 400 if request is not XMLHttpRequest | AJAX-only endpoints |
| `api_endpoint` | Wraps route to return JSON with error handling | API endpoints |
| `rate_limit(max_per_second)` | Throttle requests (future) | Login route, API endpoints |
| `validate_csrf` | CSRF token validation | POST/PUT/DELETE routes (auto via Flask-WTF) |

See Software Architecture document for full implementation details.

---

### `utils/helpers.py` — Helper Functions

**Purpose**: Shared utility functions used across the codebase.

**Functions Provided**:

| Function | Category | Description |
|----------|----------|-------------|
| `validate_currency(amount)` | Validation | Ensure value is a valid currency amount (2 decimal places, non-negative) |
| `validate_phone(phone)` | Validation | Validate phone number format (configurable per country) |
| `validate_email(email)` | Validation | Basic email format validation |
| `sanitize_string(text)` | Sanitization | Strip HTML tags, limit length, trim whitespace |
| `format_currency(amount, symbol)` | Formatting | Display amount with currency symbol and 2 decimals |
| `format_date(date, format)` | Formatting | Format date string for display |
| `format_datetime(dt)` | Formatting | Display datetime in localized format |
| `generate_sku(name, category)` | Generation | Create SKU from product name initials + category code |
| `generate_barcode()` | Generation | Generate EAN-13 barcode number |
| `slugify(text)` | Generation | Create URL-friendly slug from text |
| `paginate(page, per_page, total)` | Pagination | Calculate pagination metadata (has_prev, has_next, pages) |
| `error_response(message, code, details)` | Error | Standardized error response (see Software Architecture) |
| `TTLCache` | Caching | Simple TTL-based in-memory cache class |
| `get_client_ip()` | Network | Extract client IP from request headers (handles proxies) |
| `is_ajax_request()` | Network | Check if request is AJAX |

---

## 8. static/ Directory

**Purpose**: Static assets served directly to the browser.

### `static/css/style.css` — Main Stylesheet

**Purpose**: All visual styling for the ERP system.

**Organization** (by section):
1. CSS Custom Properties (variables) — colors, spacing, font sizes
2. Reset / Base styles
3. Typography
4. Layout — grid, flexbox utilities
5. Navigation — sidebar, top bar
6. Form elements — inputs, buttons, selects
7. Tables — sortable, striped, responsive
8. Cards and panels
9. Modal dialogs
10. Flash messages / notifications
11. POS terminal layout
12. Print styles
13. Responsive breakpoints
14. Animations and transitions

**CSS Methodology**: BEM-like naming with single hyphens:
```css
/* Block */
.card { ... }
/* Element */
.card__header { ... }
.card__body { ... }
/* Modifier */
.card--highlighted { ... }
.card--compact { ... }
```

**Approximate Size**: 1500-2000 lines, minified to ~30 KB in production.

---

### `static/css/print.css` — Print Stylesheet

**Purpose**: Styles for printed receipts and reports.

**Key Rules**:
- Hide navigation, buttons, modals
- Receipt-specific: small font, monospace for itemized lists
- Page break handling for multi-page reports
- No background colors (printer ink conservation)

---

### `static/js/app.js` — Main JavaScript

**Purpose**: Global application state, initialization, shared utilities.

**Contents**:
- `ERP` global state object (see Software Architecture section)
- `document.addEventListener('DOMContentLoaded', ERP.init)`
- Fetch wrapper with CSRF token injection
- Form serialization utility
- Debounce/throttle utilities for scanner input
- Currency formatting
- Notification display
- Keyboard shortcut registration

**Key Design Decisions**:
- Single `ERP` global namespace (no module bundler needed)
- Event-driven state changes via CustomEvent
- localStorage for pending sale persistence (survives refresh)
- No jQuery dependency — vanilla JS only

---

### `static/js/sales.js` — Sales Page Scripts

**Purpose**: POS terminal interactivity.

**Contents**:
- Barcode scanner input handling (200ms buffer to handle fast scanners)
- Product search autocomplete with debounce (300ms)
- Cart management: add, remove, update quantity
- Line item discount entry
- Payment method handling (cash, card, split)
- Total calculation with auto-recalculation
- Hold/resume UI management

---

### `static/js/inventory.js` — Inventory Management Scripts

**Purpose**: Inventory count and adjustment interactivity.

**Contents**:
- Barcode lookup for count entry
- Variance highlighting (expected vs actual)
- Batch count entry mode (keyboard-first)
- Transfer form with store selector

---

### `static/js/reports.js` — Reports Scripts

**Purpose**: Report interaction and visualization.

**Contents**:
- Date range picker initialization
- Chart rendering (simple canvas-based bar/line charts, or Chart.js if added)
- Table sorting by column
- Export button handlers
- Report parameter form management

---

## 9. templates/ Directory

**Purpose**: Jinja2 HTML templates for server-rendered pages.

### `templates/base.html` — Base Template

**Purpose**: Layout template extended by all pages.

**Contents**:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    {% block head %}
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ERP POS System{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block extra_head %}{% endblock %}
    </head>
<body>
    {% block sidebar %}{% include 'components/navigation.html' %}{% endblock %}
    <main>
        {% include 'components/flash_messages.html' %}
        {% block content %}{% endblock %}
    </main>
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
    {% block extra_scripts %}{% endblock %}
</body>
</html>
```

**Blocks Available for Extension**:

| Block | Purpose | Required? |
|-------|---------|-----------|
| `title` | Page title | Optional (default: "ERP POS System") |
| `head` | Head section content | Optional |
| `extra_head` | Additional CSS/links | Optional |
| `sidebar` | Navigation sidebar | Optional (empty by default) |
| `content` | Main page content | **Required** |
| `extra_scripts` | Page-specific JavaScript | Optional |

---

### Template Subdirectories

Each subdirectory corresponds to a blueprint and contains templates for that module's routes.

**Template Naming Convention**:

| Route | Template | Convention |
|-------|----------|------------|
| `GET /products` | `products/list.html` | `{module}/list.html` |
| `GET /products/create` | `products/create.html` | `{module}/create.html` |
| `GET /products/<id>/edit` | `products/edit.html` | `{module}/edit.html` |
| `GET /products/<id>` | `products/detail.html` | `{module}/detail.html` |
| POST variants | Same template (with errors) | Same as GET |

**Component Patterns**:

`components/pagination.html`:
```html
{% macro pagination(page, per_page, total, endpoint) %}
{% set total_pages = ((total - 1) / per_page) | int + 1 if total > 0 else 1 %}
<nav class="pagination" aria-label="Pagination">
    <a href="{{ url_for(endpoint, page=page-1, **kwargs) }}" class="pagination__prev"
       {% if page <= 1 %}aria-disabled="true" tabindex="-1"{% endif %}>
        Previous
    </a>
    {% for p in range(1, total_pages + 1) %}
        {% if p == page %}
            <span class="pagination__current">{{ p }}</span>
        {% elif p <= 3 or p > total_pages - 2 or (p >= page - 1 and p <= page + 1) %}
            <a href="{{ url_for(endpoint, page=p, **kwargs) }}" class="pagination__link">{{ p }}</a>
        {% elif p == page - 2 or p == page + 2 %}
            <span class="pagination__ellipsis">...</span>
        {% endif %}
    {% endfor %}
    <a href="{{ url_for(endpoint, page=page+1, **kwargs) }}" class="pagination__next"
       {% if page >= total_pages %}aria-disabled="true" tabindex="-1"{% endif %}>
        Next
    </a>
</nav>
{% endmacro %}
```

---

## 10. flask_session/ Directory

**Purpose**: Server-side session file storage when using `SESSION_TYPE = "filesystem"` (development).

**Behavior**:
- Created automatically by Flask-Session when the app starts
- Each session is a file named `<session_id>.session`
- Files are deleted when session expires or user logs out
- **Never commit this directory** — listed in `.gitignore`
- In production, use Redis instead of filesystem sessions

---

## 11. Docker Configuration

### `Dockerfile` — Application Image

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libusb-1.0-0-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 erp && chown -R erp:erp /app
USER erp

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", \
     "--access-logfile", "-", "--error-logfile", "-", \
     "app:create_app()"]
```

### `docker-compose.yml` — Multi-Container Setup

See `SYSTEM_ARCHITECTURE.md` for the full Docker Compose configuration with PostgreSQL, Redis, and Nginx.

**Profiles**:

| Profile | Command | Services |
|---------|---------|----------|
| Development | `docker compose up` | Flask (dev mode), SQLite |
| Production | `docker compose --profile prod up` | Flask (gunicorn), PostgreSQL, Redis, Nginx |
| Testing | `docker compose run --rm test` | Flask (test config), SQLite in-memory |

---

## 12. File Naming Conventions

| Category | Convention | Examples |
|----------|------------|----------|
| Python files | `snake_case.py` | `sales_service.py`, `stock_engine.py` |
| SQL files | `snake_case.sql` | `schema.sql`, `001_initial_schema.sql` |
| HTML templates | `snake_case.html` | `create_product.html`, `daily_sales.html` |
| CSS files | `snake_case.css` | `style.css`, `print.css` |
| JS files | `snake_case.js` | `app.js`, `sales.js` |
| Markdown docs | `UPPER_SNAKE_CASE.md` | `SYSTEM_ARCHITECTURE.md`, `CODING_STANDARDS.md` |
| Config files | `snake_case` | `docker-compose.yml`, `.gitignore` |
| Docker files | PascalCase | `Dockerfile` |

---

## 13. Import Map

### Route → Service Dependencies

```
routes/auth.py       → services.auth_service
routes/products.py   → services.stock_engine
routes/customers.py  → services.sales_service, services.accounting_service
routes/suppliers.py  → services.purchase_service, services.accounting_service
routes/sales.py      → services.sales_service, services.stock_engine,
                       services.accounting_service, services.audit_service,
                       services.repair_service
routes/purchases.py  → services.purchase_service, services.stock_engine,
                       services.accounting_service, services.audit_service
routes/inventory.py  → services.stock_engine, services.audit_service
routes/repairs.py    → services.repair_service, services.warranty_service,
                       services.audit_service
routes/employees.py  → services.auth_service, services.audit_service
routes/reports.py    → services.sales_service, services.purchase_service,
                       services.accounting_service, services.stock_engine,
                       services.repair_service
routes/audit.py      → services.audit_service
```

### Service → Utility Dependencies

```
All services → database.connection (get_db)
All services → utils.helpers (validation, formatting)
All services → utils.decorators (decorators are applied in routes, not services)
```

---

## 14. New Module Checklist

When adding a new feature module, follow this checklist:

- [ ] **Add route file**: Create `routes/{module}.py` with blueprint, all CRUD routes, decorators
- [ ] **Register blueprint**: Add `app.register_blueprint(...)` in `app.py`
- [ ] **Add service file**: Create `services/{module}_service.py` with business logic
- [ ] **Register service**: Add singleton instance in `services/__init__.py`
- [ ] **Add templates**: Create `templates/{module}/` with `list.html`, `create.html`, `edit.html`, `detail.html`
- [ ] **Update schema**: Add tables to `database/schema.sql`
- [ ] **Add permissions**: Include new permission strings in `database/seed.py`
- [ ] **Add navigation**: Update sidebar template to include link to new module
- [ ] **Add tests**: Create `tests/test_{module}.py` (future test directory)
- [ ] **Add audit events**: Register new event types in `AuditService.EVENT_TYPES`
- [ ] **Document**: Update relevant doc files in `docs/`

---

## 15. Refactoring Guidelines

### When to Refactor

- A route file exceeds 500 lines → extract logic to service layer
- A service file exceeds 400 lines → consider splitting into sub-services
- A template exceeds 300 lines → extract components into `templates/components/`
- A JavaScript file exceeds 400 lines → split into module-specific files
- A function exceeds 50 lines → extract helper functions
- Repeated SQL patterns 3+ times → create reusable query function in service

### Refactoring Process

1. Write tests for the existing behavior (characterize tests)
2. Make the change
3. Run tests to verify behavior is preserved
4. Update imports in all files that reference the changed module
5. Run the full test suite
6. Update documentation

### Dead Code Removal

- If a route is not linked from any navigation element, check if it's used externally before removing
- If a service function has zero callers, remove it
- If a template is not rendered by any route, remove it
- Use `git log -- <file>` to check if dead code was intentional

---

> **Document Maintainer**: Principal Software Architect  
> **Review Cycle**: Quarterly  
> **Next Review**: 2026-09-24
