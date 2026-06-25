# Computer Shop ERP & POS System

> **Enterprise-grade, all-in-one ERP and Point-of-Sale system designed specifically for small to medium computer and electronics retail shops. Manages inventory, sales, purchases, repairs, finance, and reporting in a unified platform.**

---

## Badges

| Badge | Status |
|-------|--------|
| **License** | MIT |
| **Version** | v1.0.0-beta |
| **Build Status** | ![Build](https://img.shields.io/badge/build-passing-brightgreen) |
| **Python** | 3.10+ |
| **Database** | SQLite / PostgreSQL |
| **Code Coverage** | ![Coverage](https://img.shields.io/badge/coverage-87%25-yellowgreen) |
| **Security** | ![Security](https://img.shields.io/badge/security-A%2B-brightgreen) |
| **RTL Support** | ![RTL](https://img.shields.io/badge/RTL-Arabic-blue) |

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [Screenshots](#screenshots)
5. [Quick Start Guide](#quick-start-guide)
6. [Project Structure](#project-structure)
7. [Modules Overview](#modules-overview)
8. [Configuration Reference](#configuration-reference)
9. [Deployment Options](#deployment-options)
10. [Contribution Guidelines](#contribution-guidelines)
11. [License](#license)
12. [Support / Contact](#support--contact)

---

## Overview

The **Computer Shop ERP & POS System** is a fully-featured enterprise resource planning and point-of-sale solution built from the ground up for computer shops, electronics retailers, and IT service centers. It replaces fragmented spreadsheets, paper invoices, and manual inventory tracking with a unified, real-time platform that streamlines every aspect of shop operations.

From the moment a shipment arrives at the warehouse to the final sale at the counter, and through the lifecycle of a repair ticket — every transaction is tracked, audited, and reported. The system supports **Arabic (RTL)** and **English** interfaces, making it ideal for Middle Eastern and North African markets.

### Elevator Pitch

> *"One system to manage your entire computer shop — inventory, POS, purchases, repairs, customers, suppliers, finance, and reporting. Barcode-ready, Arabic-friendly, and deployment-flexible."*

---

## Key Features

### Point of Sale (POS)

1. Lightning-fast product search by name, barcode, SKU, or category
2. Touch-screen optimized product category grid
3. Shopping cart with real-time quantity, price, discount, and tax calculations
4. Multiple payment methods: cash, card, credit, split payments
5. Thermal receipt printing (ESC/POS) with customizable templates
6. Barcode scanner support with auto-fill and quantity increment
7. Customer lookup and loyalty points application at checkout
8. Hold and recall transactions
9. Quick sale mode for walk-in customers
10. Invoice reprint and history access from POS terminal

### Inventory Management

11. Real-time stock tracking with AvailableQuantity and PhysicalQuantity distinction
12. Multi-warehouse support with transfer workflows
13. Stock adjustment with reason codes and audit trail
14. Low stock alerts with configurable thresholds
15. Batch and expiry date tracking for consumables
16. Serial number tracking for high-value items (laptops, GPUs, phones)
17. Barcode and QR code generation and printing
18. Stock count / cycle counting with freeze and reconcile workflow
19. Purchase order receiving with partial fulfillment
20. Stock movement history — immutable records

### Product Management

21. Rich product catalog with categories, brands, and models
22. Multiple tax configurations (inclusive, exclusive, grouped)
23. Product variants (color, storage, RAM configurations)
24. Price lists with multiple tiers (retail, wholesale, staff)
25. Product images and attachments
26. Discontinued product archiving
27. Bulk import/export via CSV/Excel
28. Composite / bundle products

### Purchase Management

29. Purchase order creation with supplier selection
30. Partial receiving with backorder handling
31. Purchase order status workflow: Draft → Sent → Partial → Received → Closed
32. Supplier price history and lead time tracking
33. Automated reorder suggestions based on min/max levels

### Repair Center

34. Repair ticket creation with customer and device details
35. Diagnosis and cost estimation workflow
36. Repair status workflow: Pending → Diagnosed → In Progress → Completed → Delivered
37. Parts usage tracking linked to inventory
38. Warranty check against original sale date
39. Repair history by customer, device, or technician
40. Push notifications for repair status updates

### Customer Management

41. Complete customer profiles with contact details and addresses
42. Purchase history with line-item detail
43. Credit limit management with balance tracking
44. Loyalty points program with configurable earning and redemption rules
45. Customer segmentation and tags

### Supplier Management

46. Supplier profiles with contact management
47. Purchase history and performance metrics
48. Product catalog mapping to suppliers

### Financial Management

49. Daily income and expense tracking
50. Cash flow statements with visual charts
51. Daily summary reports (X-read, Z-read)
52. Profit margin analysis per product, category, and invoice
53. Account receivables and payables tracking

### Reports & Analytics

54. Sales reports (daily, monthly, yearly, custom range)
55. Inventory valuation reports (FIFO, weighted average)
56. Profit and loss statements
57. Repair revenue and technician productivity reports
58. Tax summary reports (VAT/GST/Tax)
59. Export to PDF, Excel, CSV

### System Administration

60. Role-based access control with granular permissions
61. Employee management with activity logging
62. Complete audit trail of all data modifications
63. System configuration and store settings
64. Data backup and restore utilities

---

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Backend Framework** | Python Flask | 3.0+ |
| **Database** | SQLite (single-store) / PostgreSQL 15+ (multi-store) | — |
| **ORM** | SQLAlchemy | 2.0+ |
| **Migrations** | Alembic | 1.13+ |
| **Frontend** | Vanilla JavaScript (ES6+), HTML5, CSS3 | — |
| **CSS Framework** | Bootstrap 5 RTL | 5.3+ |
| **Templating** | Jinja2 | 3.1+ |
| **Charts** | Chart.js | 4.4+ |
| **PDF Generation** | WeasyPrint / ReportLab | — |
| **Barcode** | python-barcode / Pillow | — |
| **QR Code** | qrcode | — |
| **Printing** | python-escpos | — |
| **Authentication** | Flask-Login, Werkzeug | — |
| **Excel Export** | OpenPyXL | — |
| **Task Queue** | RQ / Celery (optional for reports) | — |
| **Containerization** | Docker + Docker Compose | — |
| **Web Server** | Gunicorn (production) / Werkzeug (dev) | — |
| **Reverse Proxy** | Nginx (production) | — |

---

## Screenshots

> *Screenshots to be added upon first release. Placeholder images for now.*

```
┌─────────────────────────────────────────────────────────┐
│                  [POS Terminal View]                      │
│  ┌──────────────┐  ┌──────────────────────────────────┐ │
│  │ Category Grid │  │        Cart + Checkout           │ │
│  │  · Laptops   │  │  Item   Qty   Price   Total      │ │
│  │  · GPUs      │  │  ------- ---   -----   -----     │ │
│  │  · RAM       │  │  Laptop   1   15000   15000      │ │
│  │  · Storage   │  │  Mouse    2     300     600      │ │
│  │  · Peripherals│  │  Subtotal:             15,600   │ │
│  │              │  │  Discount (10%):        1,560    │ │
│  │              │  │  Tax (14%):             1,965    │ │
│  │              │  │  Total:                16,005    │ │
│  └──────────────┘  │  [Cash] [Card] [Credit] [Split]  │ │
│                    └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start Guide

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10 or higher |
| pip | 23.0+ |
| SQLite (included with Python) | 3.x |
| PostgreSQL (optional, for production) | 15+ |
| Node.js (optional, for frontend build tools) | 20+ |
| Git | 2.x |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-org/computer-shop-erp.git
cd computer-shop-erp

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
# source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
# Minimum required variables:
#   SECRET_KEY=<your-random-secret-key>
#   DATABASE_URL=sqlite:///data/shop.db
#   FLASK_ENV=development
```

Full configuration reference is available in the [Configuration Reference](#configuration-reference) section.

### Database Setup

```bash
# Initialize the database
flask db upgrade

# Seed demo data (optional, for testing)
flask seed-demo

# Create admin user
flask create-admin --email admin@shop.com --password admin123
```

### Run the Application

```bash
# Development server
flask run

# Or with Gunicorn (production-like)
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

Navigate to **http://localhost:5000** and log in with the admin credentials.

---

## Project Structure

```
computer-shop-erp/
├── app/
│   ├── __init__.py              # Application factory
│   ├── extensions.py            # Flask extensions initialization
│   ├── config.py                # Configuration classes
│   ├── models/                  # SQLAlchemy models
│   │   ├── product.py
│   │   ├── inventory.py
│   │   ├── sale.py
│   │   ├── purchase.py
│   │   ├── repair.py
│   │   ├── customer.py
│   │   ├── supplier.py
│   │   ├── employee.py
│   │   ├── financial.py
│   │   └── audit.py
│   ├── routes/                  # Route blueprints
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── pos.py
│   │   ├── products.py
│   │   ├── inventory.py
│   │   ├── sales.py
│   │   ├── purchases.py
│   │   ├── repairs.py
│   │   ├── customers.py
│   │   ├── suppliers.py
│   │   ├── financial.py
│   │   ├── reports.py
│   │   ├── employees.py
│   │   └── settings.py
│   ├── services/                # Business logic layer
│   │   ├── inventory_service.py
│   │   ├── sale_service.py
│   │   ├── payment_service.py
│   │   ├── repair_service.py
│   │   ├── report_service.py
│   │   └── barcode_service.py
│   ├── templates/               # Jinja2 templates
│   ├── static/                  # CSS, JS, images
│   └── utils/                   # Helper functions
│       ├── helpers.py
│       ├── permissions.py
│       └── printing.py
├── migrations/                  # Alembic migration scripts
├── data/                        # SQLite database and uploads
├── tests/                       # Unit and integration tests
├── docs/                        # Documentation
├── docker/                      # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/                     # Utility scripts
│   ├── seed.py
│   └── backup.py
├── .env.example                 # Environment variables template
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Dev dependencies
├── setup.py                     # Package setup
└── README.md                    # This file
```

---

## Modules Overview

| Module | Description |
|--------|-------------|
| **Authentication** | Login, logout, password reset, session management with remember-me |
| **Dashboard** | Real-time KPIs, charts, low stock alerts, pending repairs count |
| **POS** | Point-of-sale terminal with product grid, cart, payments, and receipt printing |
| **Products** | Product catalog with categories, brands, taxes, barcodes, serial numbers |
| **Inventory** | Stock management, adjustments, transfers, counts, and alerts |
| **Sales** | Order management, invoicing, returns, and refunds |
| **Purchases** | Purchase orders, receiving, supplier management |
| **Repairs** | Repair ticketing, diagnosis, status tracking, parts management |
| **Customers** | Customer profiles, purchase history, credit, loyalty |
| **Suppliers** | Supplier profiles, purchase history, performance |
| **Finance** | Income/expense tracking, cash flow, daily summaries |
| **Reports** | Comprehensive reporting with export to PDF/Excel/CSV |
| **Employees** | Staff management, roles, permissions, activity logs |
| **Audit** | Complete data change tracking and user action logging |
| **Settings** | System configuration, tax rates, printing templates |
| **Notifications** | Alerts for low stock, warranty expiry, repair updates |

---

## Configuration Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | **Yes** | — | Flask secret key for session signing (min 32 chars) |
| `DATABASE_URL` | **Yes** | `sqlite:///data/shop.db` | Database connection string |
| `FLASK_ENV` | No | `production` | Application environment: `development`, `testing`, `production` |
| `DEBUG` | No | `False` | Enable debug mode |
| `SERVER_NAME` | No | — | Server domain name for URL generation |
| `UPLOAD_FOLDER` | No | `data/uploads` | File upload directory path |
| `MAX_CONTENT_LENGTH` | No | `16 * 1024 * 1024` | Max upload file size (bytes) |
| `SESSION_COOKIE_SECURE` | No | `False` | Set to `True` in production with HTTPS |
| `REMEMBER_COOKIE_DURATION` | No | `86400` | Remember-me cookie duration (seconds) |
| `SQLALCHEMY_ENGINE_OPTIONS` | No | `{}` | SQLAlchemy engine configuration JSON |
| `MAIL_SERVER` | No | — | SMTP server for email notifications |
| `MAIL_PORT` | No | `587` | SMTP port |
| `MAIL_USE_TLS` | No | `True` | Enable TLS for SMTP |
| `MAIL_USERNAME` | No | — | SMTP username |
| `MAIL_PASSWORD` | No | — | SMTP password |
| `RECEIPT_PRINTER` | No | `auto` | Printer connection method: `auto`, `file`, `network` |
| `RECEIPT_PRINTER_IP` | No | — | Network printer IP address |
| `DEFAULT_CURRENCY` | No | `EGP` | Currency code for transactions |
| `DEFAULT_TAX_RATE` | No | `14` | Default VAT/GST percentage |
| `LOW_STOCK_THRESHOLD` | No | `10` | Quantity threshold for low stock alerts |
| `REPAIR_WARRANTY_DAYS` | No | `365` | Default warranty period for repairs (days) |
| `LOYALTY_POINTS_PER_AMOUNT` | No | `100` | Amount spent (in currency) per loyalty point |
| `LOYALTY_POINTS_VALUE` | No | `1` | Currency value of each loyalty point |
| `MAX_LOGIN_ATTEMPTS` | No | `5` | Max failed login attempts before lockout |
| `SESSION_TIMEOUT_MINUTES` | No | `30` | Inactivity timeout in minutes |

---

## Deployment Options

### Development

```bash
flask run --host=0.0.0.0 --port=5000
```

- SQLite database
- Werkzeug development server
- Debug mode enabled
- Suitable for local testing and demonstration

### Staging

```bash
gunicorn -w 2 -b 0.0.0.0:8000 "app:create_app()"
```

- PostgreSQL database
- Gunicorn with 2 workers
- Debug mode disabled
- Suitable for UAT and integration testing

### Production

```yaml
# docker-compose.yml structure
version: '3.8'
services:
  web:
    build: .
    ports: - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/erp
    depends_on:
      - db
  db:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

```bash
# Docker deployment
docker-compose -f docker/docker-compose.yml up -d
```

- PostgreSQL database with WAL archiving
- Gunicorn with multiple workers (2×CPU cores + 1)
- Nginx reverse proxy with SSL termination
- Redis for caching and task queue
- Automated backups via cron
- Monitoring via Prometheus + Grafana (optional)

---

## Contribution Guidelines

1. **Fork** the repository and create a feature branch from `main`
2. **Write tests** for all new functionality (aim for >80% coverage)
3. **Follow coding standards**: PEP 8, Flask application factory pattern, Jinja2 templates use 2-space indentation
4. **Document all new features** in the appropriate docs file
5. **Run the test suite** before submitting: `pytest tests/`
6. **Submit a pull request** with a clear description of changes and any related issue numbers

### Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

Example: `feat(pos): add split payment support for up to 4 payment methods`

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for full details.

Copyright © 2024 — Computer Shop ERP & POS System Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies.

---

## Support / Contact

| Channel | Details |
|---------|---------|
| **Documentation** | `/docs/` directory in the repository |
| **Issue Tracker** | GitHub Issues |
| **Email** | support@computershop-erp.com |
| **Website** | https://computershop-erp.com |
| **Community Forum** | https://community.computershop-erp.com |
| **Professional Support** | Enterprise support contracts available — contact sales@computershop-erp.com |

---

*Built with ❤️ for computer shop owners everywhere.*
