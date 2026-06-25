# Functional Requirements — Computer Shop ERP & POS System

> **Version:** 1.0.0-beta  
> **Document Status:** Final  
> **Requirement Prefix:** FR-001  
> **Last Updated:** June 2026

---

## Table of Contents

1. [Requirement Identification](#requirement-identification)
2. [Authentication Module](#authentication-module)
3. [Dashboard Module](#dashboard-module)
4. [Product Management](#product-management)
5. [Inventory Management](#inventory-management)
6. [POS System](#pos-system)
7. [Sales Management](#sales-management)
8. [Purchase Management](#purchase-management)
9. [Customer Management](#customer-management)
10. [Supplier Management](#supplier-management)
11. [Repair Center](#repair-center)
12. [Financial Module](#financial-module)
13. [Reporting Module](#reporting-module)
14. [Employee Management](#employee-management)
15. [Audit System](#audit-system)
16. [Notification System](#notification-system)
17. [Barcode/QR Generation and Printing](#barcodeqr-generation-and-printing)
18. [File Storage](#file-storage)
19. [AI Features](#ai-features)

---

## Requirement Identification

The following numbering scheme is used throughout this document:

| Prefix | Range | Module |
|--------|-------|--------|
| FR-001-001 | 001-020 | Authentication |
| FR-001-021 | 021-035 | Dashboard |
| FR-001-036 | 036-065 | Product Management |
| FR-001-066 | 066-090 | Inventory Management |
| FR-001-091 | 091-120 | POS System |
| FR-001-121 | 121-140 | Sales Management |
| FR-001-141 | 141-160 | Purchase Management |
| FR-001-161 | 161-180 | Customer Management |
| FR-001-181 | 181-190 | Supplier Management |
| FR-001-191 | 191-215 | Repair Center |
| FR-001-216 | 216-235 | Financial Module |
| FR-001-236 | 236-260 | Reporting Module |
| FR-001-261 | 261-275 | Employee Management |
| FR-001-276 | 276-285 | Audit System |
| FR-001-286 | 286-295 | Notification System |
| FR-001-296 | 296-305 | Barcode/QR Generation |
| FR-001-306 | 306-310 | File Storage |
| FR-001-311 | 311-320 | AI Features |

---

## Authentication Module

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-001** | The system MUST provide a login page at `/auth/login` accessible to unauthenticated users, accepting `username` and `password` fields, with CSRF protection enabled | Critical | None |
| **FR-001-002** | The system MUST authenticate users against the `employees` table using bcrypt password hashing (12 salt rounds) | Critical | FR-001-001 |
| **FR-001-003** | The system MUST redirect authenticated users to their home page based on role (dashboard for admin/manager, POS for cashier, repairs for technician) | High | FR-001-002 |
| **FR-001-004** | The system MUST display a flash message on failed login attempts (Arabic/English localized) and increment `failed_login_attempts` counter | Medium | FR-001-002 |
| **FR-001-005** | The system MUST lock the user account after 5 consecutive failed login attempts, showing "Account locked. Contact administrator." | High | FR-001-004 |
| **FR-001-006** | The system MUST provide a password reset flow: `/auth/forgot-password` collects email, sends time-limited token (15 minutes), `/auth/reset-password/:token` accepts new password | High | FR-001-002 |
| **FR-001-007** | The system MUST manage user sessions with Flask-Login; session timeout after 30 minutes of inactivity (configurable via `SESSION_TIMEOUT_MINUTES`) | Critical | FR-001-002 |
| **FR-001-008** | The system MUST support "Remember Me" via persistent cookie, lasting 7 days by default (`REMEMBER_COOKIE_DURATION`) | Medium | FR-001-007 |
| **FR-001-009** | The system MUST enforce password complexity: minimum 8 characters, at least one uppercase, one lowercase, one digit, and one special character | High | FR-001-002 |
| **FR-001-010** | The system MUST prevent password reuse — the last 5 passwords must be unique | Medium | FR-001-009 |
| **FR-001-011** | The system MUST provide a logout endpoint `/auth/logout` that clears the session, deletes the remember-me cookie, and redirects to login | Critical | FR-001-007 |
| **FR-001-012** | The system MUST display the current user's name, role, and a logout button in the navigation bar on all authenticated pages | Low | FR-001-007 |
| **FR-001-013** | The system MUST track and display last login timestamp and IP address on successful login | Low | FR-001-002 |
| **FR-001-014** | The system MUST support concurrent session detection — if a user logs in from a new device, optionally notify or terminate older session | Medium | FR-001-007 |
| **FR-001-015** | The system MUST provide rate limiting on the login endpoint: maximum 5 attempts per IP per minute, returning HTTP 429 after exceeded | High | FR-001-001 |
| **FR-001-016** | The system MUST use HTTP-only, Secure (in production), SameSite=Lax cookies for session management | Critical | FR-001-007 |
| **FR-001-017** | The system MUST validate user-agent consistency during a session (optional: flag changes but not block) | Low | FR-001-007 |
| **FR-001-018** | The system MUST allow administrators to manually unlock user accounts from the employee management interface | High | FR-001-005 |
| **FR-001-019** | The system MUST provide a "Change Password" feature for authenticated users accessible from the profile menu | Medium | FR-001-007 |
| **FR-001-020** | All authentication events (login success, login failure, logout, password reset, account lock) MUST be logged to AuditLog with timestamp, user ID, IP address, and User-Agent | Critical | FR-001-002 |

### Authentication Checklist

- [x] Login page with CSRF protection
- [x] bcrypt password hashing (12 rounds)
- [x] Role-based home page redirection
- [x] Failed attempt counting and display
- [x] Account lockout after 5 failures
- [x] Password reset with email token (15-min expiry)
- [x] Session timeout after inactivity
- [x] Remember-me cookie (7 days)
- [x] Password complexity enforcement
- [x] Password history (last 5)
- [ ] Logout clears all session data
- [ ] User info in navigation bar
- [ ] Last login tracking
- [ ] Concurrent session detection
- [ ] Login rate limiting (5/min/IP)
- [ ] Secure cookie attributes
- [ ] Manual unlock by admin
- [ ] Change password from profile
- [ ] Full audit logging

---

## Dashboard Module

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-021** | The system MUST display a role-aware dashboard as the authenticated home page, showing KPI cards relevant to the user's permissions | Critical | FR-001-007 |
| **FR-001-022** | The dashboard MUST show KPI cards: Today's Sales, Transaction Count, Active Repairs, Low Stock Items, and Today's Net Cash Flow | High | FR-001-091, FR-001-191, FR-001-066 |
| **FR-001-023** | Each KPI card MUST update via AJAX polling every 60 seconds without full page reload | Medium | FR-001-022 |
| **FR-001-024** | The dashboard MUST display a line chart of daily sales for the last 7 days using Chart.js, with tooltip on hover showing exact values | Medium | FR-001-121 |
| **FR-001-025** | The dashboard MUST display a bar chart of top 10 best-selling products by quantity for the current month | Medium | FR-001-121 |
| **FR-001-026** | The dashboard MUST show a table of products below the low-stock threshold with a "Create PO" action button | High | FR-001-066 |
| **FR-001-027** | The dashboard MUST show a table of pending repair tickets with Ticket ID, Customer Name, Device, Status, Days Open | Medium | FR-001-191 |
| **FR-001-028** | The dashboard MUST display a quick action toolbar: New Sale, New Purchase Order, New Repair Ticket, Stock Count | Low | FR-001-091, FR-001-141, FR-001-191 |
| **FR-001-029** | The dashboard MUST show a cash flow indicator: today's cash in, cash out, net position with green/red color coding | Medium | FR-001-216 |
| **FR-001-030** | The dashboard MUST display current date/time and store name in the header area | Low | None |
| **FR-001-031** | The dashboard MUST support a date range selector for KPI data (Today, This Week, This Month, Custom Range) | Medium | FR-001-022 |
| **FR-001-032** | The dashboard MUST show a doughnut chart of payment method distribution for the selected period | Low | FR-001-121 |
| **FR-001-033** | The dashboard MUST display recent transactions (last 10) with timestamp, customer, amount, and status | Low | FR-001-121 |
| **FR-001-034** | The dashboard MUST show pending purchase orders count (Sent or Partial) as a clickable KPI navigating to filtered purchase list | Medium | FR-001-141 |
| **FR-001-035** | The dashboard MUST refresh all data on explicit refresh action with a loading indicator | Low | FR-001-022 |

### Dashboard Checklist

- [x] Role-aware KPI cards with real-time values
- [x] AJAX polling every 60 seconds
- [x] 7-day sales trend line chart (Chart.js)
- [x] Top 10 products bar chart
- [x] Low stock table with create PO action
- [x] Pending repairs table with view action
- [x] Quick action toolbar
- [x] Cash flow indicator (in/out/net)
- [x] Date/time and store name in header
- [x] Date range selector for KPIs
- [ ] Payment method distribution chart
- [ ] Recent transactions list (last 10)
- [ ] Pending PO count KPI
- [ ] Manual refresh with loading indicator

---

## Product Management

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-036** | The system MUST provide CRUD operations for products (Create, Read, Update, Archive) via `/products/*` routes | Critical | None |
| **FR-001-037** | Product creation form MUST include: name, description, category, brand, SKU (unique), barcode (unique), cost price, retail price, wholesale price, tax rate, unit, image, active toggle | Critical | FR-001-036 |
| **FR-001-038** | The system MUST enforce SKU uniqueness — duplicate SKU rejected with error message | Critical | FR-001-037 |
| **FR-001-039** | The system MUST enforce barcode uniqueness — duplicate barcode rejected with error message | Critical | FR-001-037 |
| **FR-001-040** | Product categories: CRUD with name, description, parent category (hierarchy up to 3 levels), image, active toggle | Medium | FR-001-037 |
| **FR-001-041** | Product brands: CRUD with name (unique), description, logo upload | Low | FR-001-037 |
| **FR-001-042** | Tax configuration: CRUD with name, rate (percentage), type (inclusive/exclusive), active toggle | High | FR-001-037 |
| **FR-001-043** | Product variants: base product with variant SKUs (e.g., iPhone 15 — 128GB/256GB/512GB) each with own price and stock | High | FR-001-037 |
| **FR-001-044** | Composite/bundle products: contain multiple component items sold at a package price | Medium | FR-001-037 |
| **FR-001-045** | On sale of a bundle product, the system MUST decrement stock for each component item | High | FR-001-044, FR-001-091 |
| **FR-001-046** | Serial number tracking: each serialized unit has a unique serial number recorded at stock-in and assigned at sale | High | FR-001-037, FR-001-066 |
| **FR-001-047** | Product list view with advanced filtering: by category, brand, active status, stock status, and search by name/SKU/barcode | Medium | FR-001-036 |
| **FR-001-048** | Product list supports bulk actions: activate, deactivate, export to CSV/Excel | Medium | FR-001-047 |
| **FR-001-049** | Product detail view shows: all fields, current stock by warehouse, stock movement history (20), sales history (20), purchase history (10), serial numbers | Medium | FR-001-036 |
| **FR-001-050** | Product image upload with automatic thumbnail generation (max 2 MB, JPEG/PNG, 2048×2048 max) | Low | FR-001-037 |
| **FR-001-051** | Bulk product import via CSV/Excel with template download, field validation, error report generation | High | FR-001-036 |
| **FR-001-052** | Bulk product export to CSV/Excel with selected columns | Low | FR-001-047 |
| **FR-001-053** | Price history tracking: every price change recorded with old/new value, reason, and user | Medium | FR-001-037 |
| **FR-001-054** | Multiple price tiers: retail (default), wholesale, and staff price per product | Medium | FR-001-037 |
| **FR-001-055** | POS MUST use appropriate price tier based on selected customer type | High | FR-001-054, FR-001-091 |
| **FR-001-056** | Product deactivation (soft): deactivated products hidden from POS but retained in records | Medium | FR-001-037 |
| **FR-001-057** | Deactivation warning if product has active stock or open orders (but allow action) | Medium | FR-001-056 |
| **FR-001-058** | Auto barcode generation (EAN-13 or Code 128) if not provided manually | Medium | FR-001-037 |
| **FR-001-059** | Barcode label preview and print after product save | Low | FR-001-058 |
| **FR-001-060** | Product tags/labels for custom grouping and filtering | Low | FR-001-036 |
| **FR-001-061** | Reorder point and reorder quantity fields per product | Medium | FR-001-037 |
| **FR-001-062** | Min/max stock levels per product per warehouse | Medium | FR-001-061, FR-001-066 |
| **FR-001-063** | Track created_by and updated_by for each product | Medium | FR-001-036 |
| **FR-001-064** | Prevent hard deletion of products with associated transactions (soft delete only) | High | FR-001-036 |
| **FR-001-065** | Master product catalog shared across stores; prices and stock levels per-store | High | FR-001-037, FR-001-066 |

### Product Management Checklist

- [x] Product CRUD with all required fields
- [x] SKU uniqueness enforcement
- [x] Barcode uniqueness enforcement
- [x] Category hierarchy (3 levels) CRUD
- [x] Brand CRUD
- [x] Tax configuration CRUD
- [x] Product variants support
- [x] Composite/bundle products
- [x] Bundle stock decrement logic
- [ ] Serial number tracking
- [ ] Product list with advanced filters
- [ ] Bulk actions (activate/deactivate/export)
- [ ] Product detail with stock/sales/purchase history
- [ ] Image upload with thumbnail generation
- [ ] CSV/Excel bulk import with error report
- [ ] Bulk export
- [ ] Price history tracking
- [ ] Multiple price tiers
- [ ] POS uses correct price tier
- [ ] Soft deactivation
- [ ] Deactivation warnings
- [ ] Auto barcode generation
- [ ] Barcode label preview/print
- [ ] Product tags
- [ ] Reorder point and quantity
- [ ] Min/max stock levels by warehouse
- [ ] Created/updated by tracking
- [ ] Soft delete prevention
- [ ] Master product for multi-store

---

## Inventory Management

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-066** | The system MUST track inventory at the product-warehouse level: PhysicalQuantity, AvailableQuantity, CommittedQuantity, IncomingQuantity | Critical | FR-001-037, FR-001-085 |
| **FR-001-067** | Stock-in functionality: receiving products via PO or direct stock-in, recording quantity, cost, batch, expiry, serial numbers | Critical | FR-001-066, FR-001-141 |
| **FR-001-068** | Stock-out for internal use/samples/write-offs with reason codes and approval | High | FR-001-066 |
| **FR-001-069** | Stock transfers between warehouses with workflow: Initiate → Approve → Complete | High | FR-001-066 |
| **FR-001-070** | Stock adjustments with reason code, count sheet reference, and supervisor approval | Critical | FR-001-066 |
| **FR-001-071** | Cycle counting: create count sheet, enter quantities, generate variance report | High | FR-001-066 |
| **FR-001-072** | Full physical inventory: freeze movements, print sheets, enter counts, reconcile, approve | High | FR-001-071 |
| **FR-001-073** | Real-time stock levels per product per warehouse with drill-down to movement history | High | FR-001-066 |
| **FR-001-074** | Stock movement history with filters: date range, type, product, warehouse, user; CSV export | Medium | FR-001-066 |
| **FR-001-075** | Stock movements are immutable — no edit/delete. Corrections require reversal transaction referencing original | Critical | FR-001-066 |
| **FR-001-076** | Batch tracking: products received in batches; oldest batch suggested for picking (FIFO) | Medium | FR-001-067 |
| **FR-001-077** | Expiry date tracking: products near expiry (threshold configurable, default 30 days) flagged | Medium | FR-001-067 |
| **FR-001-078** | Block sale of expired products (if expiry date exists and past expiry) | High | FR-001-077 |
| **FR-001-079** | Warehouse CRUD: name, code, address, active status | Medium | FR-001-066 |
| **FR-001-080** | Storage locations within warehouse; products assigned to specific locations | Low | FR-001-079 |
| **FR-001-081** | Inventory valuation using FIFO (First In, First Out) method | Medium | FR-001-066 |
| **FR-001-082** | Inventory valuation using Weighted Average Cost method as alternative | Low | FR-001-081 |
| **FR-001-083** | Low stock alert when AvailableQuantity ≤ reorder_point — on dashboard and notifications | High | FR-001-061 |
| **FR-001-084** | Automated reorder suggestions: products below reorder point listed with suggested quantity | Medium | FR-001-083 |
| **FR-001-085** | Multi-warehouse support: each store has one or more warehouses with independent stock tracking | High | FR-001-066 |
| **FR-001-086** | Inventory freeze during physical stock count — no movements allowed for counted warehouse | High | FR-001-072 |
| **FR-001-087** | Stock report: product name, SKU, warehouse, physical qty, available qty, committed qty, incoming qty, cost value, retail value | Medium | FR-001-066 |
| **FR-001-088** | Stock turnover rate per product (COGS / Average Inventory) | Low | FR-001-081 |
| **FR-001-089** | All inventory transactions logged in AuditLog with product, warehouse, qty change, before/after, reason, user, IP, timestamp | Critical | FR-001-075 |
| **FR-001-090** | Barcode scanning support for stock-in, stock-out, stock count, and transfers | High | FR-001-067, FR-001-296 |

### Inventory Checklist

- [x] Multi-warehouse quantity tracking (Physical, Available, Committed, Incoming)
- [x] Stock-in (PO receiving and direct)
- [x] Stock-out (internal use, write-off with approval)
- [x] Stock transfer workflow
- [x] Stock adjustment with reason and approval
- [x] Cycle counting with variance report
- [x] Full physical inventory with freeze/unfreeze
- [x] Real-time stock display with movement drill-down
- [x] Stock movement history with filters and export
- [x] Immutable stock movements
- [ ] Batch tracking
- [ ] Expiry date tracking and alerts
- [ ] Block sale of expired products
- [ ] Warehouse CRUD
- [ ] Storage locations within warehouse
- [ ] FIFO inventory valuation
- [ ] Weighted average cost valuation
- [ ] Low stock alerts
- [ ] Reorder suggestions
- [ ] Multi-warehouse per store
- [ ] Inventory freeze for stock count
- [ ] Stock report (qty × value)
- [ ] Stock turnover analysis
- [ ] Full audit logging for inventory
- [ ] Barcode scanning support

---

## POS System

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-091** | The POS terminal MUST load in under 2 seconds at `/pos` for users with `pos:access` permission | Critical | FR-001-007 |
| **FR-001-092** | POS interface: left panel with product grid, category filter buttons, product cards (image, name, price, stock badge) | Critical | FR-001-037 |
| **FR-001-093** | Real-time search by name/SKU/barcode with debounce (300ms) | Critical | FR-001-092 |
| **FR-001-094** | Barcode scanner input followed by ENTER auto-finds product and adds to cart (or increments) | Critical | FR-001-093 |
| **FR-001-095** | Cart panel: line items with product name, unit price, quantity (+/-), line total, discount, remove button | Critical | FR-001-091 |
| **FR-001-096** | Cart running totals: subtotal, discount total, tax total (per rate), grand total | Critical | FR-001-095 |
| **FR-001-097** | Per-line discounts (% or fixed). Cashier needs `pos:discount` permission; >threshold (15%) requires manager PIN | High | FR-001-095, FR-001-261 |
| **FR-001-098** | Per-invoice discounts on subtotal with same permission checks | High | FR-001-097 |
| **FR-001-099** | Tax calculated per line item based on product's assigned tax rate, not on total (BR-005) | High | FR-001-095 |
| **FR-001-100** | Customer selection modal: name, phone, email, credit balance, loyalty points | High | FR-001-161 |
| **FR-001-101** | Warning and block if customer credit exceeds credit limit (BR-006) | High | FR-001-100 |
| **FR-001-102** | Apply customer loyalty points as discount at checkout | Medium | FR-001-100 |
| **FR-001-103** | Payment methods: Cash, Card, Credit Account, Split (up to 4 methods) | Critical | FR-001-091 |
| **FR-001-104** | Cash payment: enter amount tendered, system calculates and displays change due | Critical | FR-001-103 |
| **FR-001-105** | Split payment: distribute total across payment methods; each partial amount validated | High | FR-001-103 |
| **FR-001-106** | Credit account: sale recorded against customer credit; balance increases by sale amount | High | FR-001-103 |
| **FR-001-107** | On payment: (a) decrement stock, (b) generate invoice number, (c) record finance, (d) update loyalty points, (e) print receipt, (f) open cash drawer | Critical | FR-001-091 to FR-001-106 |
| **FR-001-108** | Invoice number format: `INV-YYYYMMDD-XXXXX` (daily resetting sequential) | High | FR-001-107 |
| **FR-001-109** | Success screen: invoice number, total, change (if cash), "New Sale" button | Medium | FR-001-107 |
| **FR-001-110** | Hold cart: saves current cart state with customer name and note | Medium | FR-001-095 |
| **FR-001-111** | Recall cart: display held carts list, restore selected cart | Medium | FR-001-110 |
| **FR-001-112** | Validate sale quantity ≤ AvailableQuantity at time of cart addition | Critical | FR-001-095 |
| **FR-001-113** | Block quantity increase if AvailableQuantity reaches zero — "Insufficient Stock" message | High | FR-001-112 |
| **FR-001-114** | Walk-in customer option for quick sales without registration | Medium | FR-001-091 |
| **FR-001-115** | Receipt reprinting for last transaction and any within current shift | Low | FR-001-107 |
| **FR-001-116** | POS session lock with PIN to resume | Medium | FR-001-091 |
| **FR-001-117** | Offline mode: queue transactions locally (IndexedDB), sync when online | High | None |
| **FR-001-118** | Connection status indicator: green (online), yellow (intermittent), red (offline) | Medium | FR-001-117 |
| **FR-001-119** | Configurable receipt templates: header (shop info), footer (policy), print options (thermal/A4) | Low | FR-001-107 |
| **FR-001-120** | All POS transactions logged in AuditLog with user, customer, products, quantities, prices, payment, invoice, timestamp | Critical | FR-001-107 |

### POS Checklist

- [x] Fast load (<2 seconds)
- [x] Product grid with category filters
- [x] Real-time search (debounce 300ms)
- [x] Barcode scanner auto-add
- [x] Cart with line items and controls
- [x] Running totals (subtotal, discount, tax, grand total)
- [x] Per-line and per-invoice discounts with permission checks
- [x] Tax per line item
- [x] Customer selection modal
- [x] Credit limit validation
- [x] Loyalty points application
- [x] Multiple payment methods
- [x] Cash change calculation
- [x] Split payment validation
- [x] Credit account recording
- [x] Complete sale processing
- [x] Sequential invoice number (daily reset)
- [x] Success screen display
- [x] Hold cart / Recall cart
- [x] AvailableQuantity validation
- [x] Insufficient stock block
- [x] Walk-in customer option
- [ ] Receipt reprint
- [ ] POS session lock with PIN
- [ ] Offline mode with queue and sync
- [ ] Connection status indicator
- [ ] Configurable receipt templates
- [ ] Full audit logging

---

## Sales Management

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-121** | Sales order list at `/sales` with filters: date range, status, customer, cashier, payment method, search by invoice number | Critical | FR-001-107 |
| **FR-001-122** | Sales order detail: invoice number, date/time, customer info, cashier, line items, tax breakdown, payment summary, status timeline | Critical | FR-001-121 |
| **FR-001-123** | Status workflow: Draft → Confirmed → Paid → Delivered → Refunded | High | FR-001-121 |
| **FR-001-124** | Returns/refunds: select original invoice, return items (qty ≤ original), process refund | High | FR-001-122 |
| **FR-001-125** | On refund: increase stock, create credit note/cash refund, reverse finance, adjust loyalty points | High | FR-001-124 |
| **FR-001-126** | Returns MUST reference original invoice (BR-007) | High | FR-001-124 |
| **FR-001-127** | Returns within 30 days of original sale (BR-007) | High | FR-001-126 |
| **FR-001-128** | Partial returns allowed — multiple return transactions per sale | Medium | FR-001-124 |
| **FR-001-129** | Status change history with timestamp, user, notes | Medium | FR-001-123 |
| **FR-001-130** | Email invoice as PDF attachment to customer | Low | FR-001-122 |
| **FR-001-131** | Bulk invoice printing for date range or invoice range | Low | FR-001-122 |
| **FR-001-132** | Sales cancellation (Draft/Confirmed only) — releases CommittedQuantity | Medium | FR-001-123 |
| **FR-001-133** | Cancelled orders preserved with status "Cancelled" — not deleted | Medium | FR-001-132 |
| **FR-001-134** | Display payment status: Unpaid, Partial, Paid with balance due | High | FR-001-121 |
| **FR-001-135** | Partial payment collection on Confirmed orders — tracks balance due | High | FR-001-134 |
| **FR-001-136** | Credit note document for return transactions with unique number | Medium | FR-001-124 |
| **FR-001-137** | COGS tracking per line item for profit calculation | High | FR-001-107 |
| **FR-001-138** | Sales quotes: create, convert to order, expiry date tracking | Medium | None |
| **FR-001-139** | Sales list export to CSV/Excel/PDF | Low | FR-001-121 |
| **FR-001-140** | All sales operations logged in AuditLog | Critical | FR-001-121 |

### Sales Checklist

- [x] Sales order list with filters and search
- [x] Sales order detail with full info and timeline
- [x] Status workflow
- [x] Returns/refunds with original invoice
- [x] Stock increase on return
- [x] Credit note / cash refund
- [x] Financial reversal
- [x] Loyalty points adjustment
- [x] 30-day return window
- [x] Partial returns
- [x] Status change history
- [ ] Email invoice as PDF
- [ ] Bulk invoice printing
- [ ] Sales cancellation (Draft/Confirmed only)
- [ ] Cancelled orders preserved
- [ ] Payment status display
- [ ] Partial payment collection
- [ ] Credit note generation
- [ ] COGS tracking
- [ ] Sales quotes with conversion
- [ ] Export to CSV/Excel/PDF
- [ ] Full audit logging

---

## Purchase Management

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-141** | PO creation: supplier selection, line items (product, qty, unit cost), expected delivery, notes, status = Draft | Critical | FR-001-181 |
| **FR-001-142** | PO status workflow: Draft → Sent → Partial → Received → Closed | Critical | FR-001-141 |
| **FR-001-143** | On sending PO: record sent timestamp, print PO document | Medium | FR-001-142 |
| **FR-001-144** | Goods receiving: for each line, enter received qty (≤ ordered), batch, expiry, serial numbers | Critical | FR-001-142 |
| **FR-001-145** | On receiving: increase stock, update IncomingQuantity, update PO status | Critical | FR-001-144 |
| **FR-001-146** | If received qty < ordered qty: create backorder for remaining | High | FR-001-145 |
| **FR-001-147** | If received qty > ordered qty: block with error | High | FR-001-145 |
| **FR-001-148** | Over-receiving tolerance: allow up to 5% above ordered (configurable) | Low | FR-001-147 |
| **FR-001-149** | PO list with filters: supplier, status, date range | Medium | FR-001-141 |
| **FR-001-150** | PO detail: supplier info, line items with ordered/received/balance, status timeline, receiving history | High | FR-001-149 |
| **FR-001-151** | PO duplication from existing PO | Low | FR-001-141 |
| **FR-001-152** | Supplier price history: last 10 purchase prices per product-supplier | Medium | FR-001-141 |
| **FR-001-153** | Email PO to supplier as PDF | Low | FR-001-141 |
| **FR-001-154** | PO cancellation (Draft/Sent only) — preserved as "Cancelled" | Medium | FR-001-142 |
| **FR-001-155** | Block cancellation if items already received | High | FR-001-154 |
| **FR-001-156** | Purchase returns: return defective items to supplier, generate debit note | Medium | FR-001-141 |
| **FR-001-157** | On purchase return: decrease stock, record transaction, generate debit note | High | FR-001-156 |
| **FR-001-158** | Reorder suggestions: products below reorder point with supplier, last price, suggested qty | Medium | FR-001-084 |
| **FR-001-159** | Supplier lead time tracking (days from PO Sent to first Receiving) | Low | FR-001-142 |
| **FR-001-160** | All purchase operations logged in AuditLog | Critical | FR-001-141 |

### Purchase Checklist

- [x] PO creation with supplier and line items
- [x] Status workflow
- [x] PO document printing
- [x] Goods receiving
- [x] Stock increase on receiving
- [x] Backorder creation
- [x] Over-receiving blocked
- [x] Over-receiving tolerance
- [x] PO list with filters
- [x] PO detail with receiving history
- [ ] PO duplication
- [ ] Supplier price history
- [ ] PO email as PDF
- [ ] PO cancellation (Draft/Sent only)
- [ ] Cancellation blocked if received
- [ ] Purchase returns with debit note
- [ ] Stock decrease on return
- [ ] Reorder suggestions
- [ ] Lead time tracking
- [ ] Full audit logging

---

## Customer Management

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-161** | Customer CRUD at `/customers/*` | Critical | None |
| **FR-001-162** | Customer fields: name, phone (unique), secondary phone, email, address, tax number, credit limit, current balance (auto), loyalty points, notes, active | Critical | FR-001-161 |
| **FR-001-163** | Enforce unique phone numbers | High | FR-001-162 |
| **FR-001-164** | Customer list: search by name/phone/email, filter by city, tags, credit status, active | High | FR-001-161 |
| **FR-001-165** | Customer detail: profile, purchase history, repair history, credit transactions, loyalty history | High | FR-001-164 |
| **FR-001-166** | Credit tracking: credit sales increase balance, payments decrease | High | FR-001-162 |
| **FR-001-167** | Credit aging report: customers by overdue days (1-30, 31-60, 61-90, 90+) | Medium | FR-001-166 |
| **FR-001-168** | Credit payment recording: date, amount, method, reference | High | FR-001-166 |
| **FR-001-169** | Loyalty points: configurable earning rate and redemption rate | Medium | FR-001-162 |
| **FR-001-170** | Display loyalty points balance on profile and POS customer selection | Low | FR-001-169 |
| **FR-001-171** | Customer tags: create, assign, filter | Low | FR-001-161 |
| **FR-001-172** | Customer segmentation: filter by total purchases, avg order value, last purchase, tags | Medium | FR-001-161 |
| **FR-001-173** | Customer import from CSV/Excel with field mapping | Medium | FR-001-161 |
| **FR-001-174** | Customer export to CSV/Excel | Low | FR-001-164 |
| **FR-001-175** | Duplicate detection: warn if phone/email exists | Medium | FR-001-163 |
| **FR-001-176** | Soft delete only for customers with associated records | High | FR-001-161 |
| **FR-001-177** | Merge customers feature for handling duplicates | Medium | FR-001-176 |
| **FR-001-178** | Customer purchase statistics: total purchases, spent, avg order, last purchase, preferred category | Low | FR-001-165 |
| **FR-001-179** | Automated notifications: repair ready, warranty reminder, birthday | Low | FR-001-286 |
| **FR-001-180** | All customer modifications logged in AuditLog | Critical | FR-001-161 |

### Customer Checklist

- [x] Customer CRUD with all fields
- [x] Unique phone enforcement
- [x] Customer list with search and filters
- [x] Customer detail with purchase/repair/credit history
- [x] Credit tracking
- [x] Credit aging report
- [x] Customer credit payment recording
- [x] Loyalty points (earning and redemption)
- [x] Loyalty points display
- [x] Customer tags
- [x] Customer segmentation
- [ ] CSV/Excel import
- [ ] CSV/Excel export
- [ ] Duplicate detection
- [ ] Soft delete only
- [ ] Merge customers
- [ ] Purchase statistics
- [ ] Automated notifications
- [ ] Full audit logging

---

## Supplier Management

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-181** | Supplier CRUD at `/suppliers/*` | Critical | None |
| **FR-001-182** | Supplier fields: company name (unique), contact person, phone, email, address, tax number, payment terms (COD, Net 15/30/60/90), bank details, notes, active | Critical | FR-001-181 |
| **FR-001-183** | Supplier list: search by name/phone/email, filter by active status, city | High | FR-001-181 |
| **FR-001-184** | Supplier detail: profile, PO history, product catalog, performance metrics (on-time rate, lead time, accuracy) | High | FR-001-183 |
| **FR-001-185** | Multiple contacts per supplier (name, phone, email, role) | Low | FR-001-181 |
| **FR-001-186** | Performance tracking: on-time delivery rate, average lead time, order accuracy | Medium | FR-001-184 |
| **FR-001-187** | Supplier product mapping — associate products with suppliers | Medium | FR-001-181 |
| **FR-001-188** | Supplier import/export via CSV/Excel | Low | FR-001-181 |
| **FR-001-189** | Soft deactivate only for suppliers with active/historical POs | High | FR-001-181 |
| **FR-001-190** | All supplier modifications logged in AuditLog | Critical | FR-001-181 |

### Supplier Checklist

- [x] Supplier CRUD with all fields
- [x] Unique company name enforcement
- [x] Supplier list with search and filters
- [x] Supplier detail with PO history and product catalog
- [x] Performance metrics
- [x] Multiple contacts per supplier
- [ ] Supplier product mapping
- [ ] CSV/Excel import/export
- [ ] Soft deactivate only
- [ ] Full audit logging

---

## Repair Center

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-191** | Repair ticket creation: customer, device type/brand/model, serial/IMEI, reported issue with photo attachment, status = Pending | Critical | FR-001-161 |
| **FR-001-192** | Strict status workflow: Pending → Diagnosed → AwaitingApproval → InProgress → Completed → Delivered | Critical | FR-001-191 |
| **FR-001-193** | Each status transition: timestamp, user, notes recorded | High | FR-001-192 |
| **FR-001-194** | AwaitingApproval → Pending allowed (customer rejects estimate) | Medium | FR-001-192 |
| **FR-001-195** | Diagnosis screen: findings, estimated cost (labor + parts), estimated completion date | High | FR-001-192 |
| **FR-001-196** | Print cost estimate for customer approval | Medium | FR-001-195 |
| **FR-001-197** | Parts usage from inventory: select product, qty, price; system validates stock, decrements on use | High | FR-001-191 |
| **FR-001-198** | Labor charges: technician hourly rate × hours worked, manual override | Medium | FR-001-191 |
| **FR-001-199** | Warranty check: by serial number against original sale date; if in warranty, may auto-apply no-charge | High | FR-001-191 |
| **FR-001-200** | Repair detail: customer info, device, issue, diagnosis, parts, labor, total cost, payment status, timeline, attachments | High | FR-001-191 |
| **FR-001-201** | Repair list with filters: status, technician, customer, date range, device | High | FR-001-191 |
| **FR-001-202** | Ticket assignment to specific technician | Medium | FR-001-191 |
| **FR-001-203** | Internal notes (staff only) and customer notes (on invoice) | Medium | FR-001-200 |
| **FR-001-204** | File attachments on repairs: customer photos, diagnostic reports, technician photos | Medium | FR-001-191 |
| **FR-001-205** | Payment status: Unpaid, Partial, Paid — collected at delivery | High | FR-001-192 |
| **FR-001-206** | CANNOT transition to Delivered if Unpaid or Partial (BR-002) | High | FR-001-205 |
| **FR-001-207** | Technician dashboard: assigned tickets grouped by status with counts and aging | Medium | FR-001-201 |
| **FR-001-208** | Repair revenue report: labor + parts by technician, by date range | Low | FR-001-236 |
| **FR-001-209** | Threaded comments on tickets (internal/external) | Low | FR-001-191 |
| **FR-001-210** | Unique repair ticket number: `RPR-YYYYMMDD-XXXXX` | Medium | FR-001-191 |
| **FR-001-211** | Technician time tracking: start/end time, billable hours | Low | FR-001-191 |
| **FR-001-212** | Customer notification when repair Completed (SMS/email) | Low | FR-001-286 |
| **FR-001-213** | Warranty check on serial number: lookup original sale date, calculate warranty status | High | FR-001-199 |
| **FR-001-214** | In-warranty repairs auto-set labor+parts to zero or flag "Warranty — No Charge" | Medium | FR-001-213 |
| **FR-001-215** | All repair operations logged in AuditLog | Critical | FR-001-191 |

### Repair Checklist

- [x] Repair ticket creation with device details
- [x] Strict status workflow (6 states)
- [x] Status transition recording
- [x] Re-diagnosis flow
- [x] Diagnosis screen with cost estimation
- [x] Print cost estimate
- [x] Parts usage from inventory
- [x] Labor charge tracking
- [x] Warranty check by serial number
- [x] Repair detail with full info
- [x] Repair list with filters
- [ ] Technician assignment
- [ ] Internal and customer notes
- [ ] File attachments
- [ ] Payment status tracking
- [ ] Block delivery if unpaid
- [ ] Technician dashboard
- [ ] Repair revenue report
- [ ] Ticket comments
- [ ] Unique repair number
- [ ] Technician time tracking
- [ ] Customer notifications
- [ ] Warranty auto-apply
- [ ] Full audit logging

---

## Financial Module

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-216** | Automatic financial recording from sales, purchases, and repairs | Critical | FR-001-107, FR-001-145, FR-001-205 |
| **FR-001-217** | Manual income entry: date, amount, category, description, reference, attachment | High | None |
| **FR-001-218** | Manual expense entry: date, amount, category, description, reference, attachment, payment method | High | None |
| **FR-001-219** | Expense categories CRUD: name, type (operating, COGS, admin), active | Medium | FR-001-218 |
| **FR-001-220** | X-Read: total sales, discounts, tax, payment breakdown, expenses, opening/closing cash | High | FR-001-216 |
| **FR-001-221** | Z-Read: same as X-Read but resets counters, saves snapshot | High | FR-001-220 |
| **FR-001-222** | Cash flow statement: inflows/outflows by category, opening balance, net change, closing balance | High | FR-001-216, FR-001-217, FR-001-218 |
| **FR-001-223** | P&L statement: Revenue — COGS — Expenses = Net Profit | High | FR-001-216 |
| **FR-001-224** | Accounts receivable aging (1-30, 31-60, 61-90, 90+) | Medium | FR-001-166 |
| **FR-001-225** | Accounts payable: amounts due to suppliers | Medium | FR-001-141 |
| **FR-001-226** | Financial period locking: no posting to closed periods | High | None |
| **FR-001-227** | No deletion of financial records — voiding only (BR-011) | Critical | FR-001-216 |
| **FR-001-228** | Voiding: requires reason, creates reversal, original with status "Voided" | Critical | FR-001-227 |
| **FR-001-229** | Transaction log: date, description, type, category, amount, user, reference | High | FR-001-216 |
| **FR-001-230** | Transaction log filters: date range, type, category, user, reference search | Medium | FR-001-229 |
| **FR-001-231** | CSV/Excel export of transaction log and all financial reports | Low | FR-001-229 |
| **FR-001-232** | All monetary values stored as integers in smallest currency unit (piasters) (BR-016) | Critical | FR-001-216 |
| **FR-001-233** | Monetary values display formatted with decimal separator and currency symbol | Critical | FR-001-232 |
| **FR-001-234** | Opening cash balance per store per day — cashier entry at shift start | Low | FR-001-220 |
| **FR-001-235** | All financial operations logged in AuditLog | Critical | FR-001-216 |

### Financial Checklist

- [x] Automatic recording from sales/purchases/repairs
- [x] Manual income/expense entry
- [x] Expense categories CRUD
- [x] X-Read / Z-Read
- [x] Cash flow statement
- [x] P&L statement
- [x] Accounts receivable aging
- [x] Accounts payable
- [x] Period locking
- [x] No deletion (void only)
- [ ] Voiding with reversal
- [ ] Transaction log with filters
- [ ] CSV/Excel export
- [ ] Monetary values as integers
- [ ] Formatted display
- [ ] Opening cash balance
- [ ] Full audit logging

---

## Reporting Module

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-236** | Reporting dashboard at `/reports` with categorized report list | High | All modules |
| **FR-001-237** | Sales reports: Summary, by Product, Category, Cashier, Customer, Payment Method | High | FR-001-121 |
| **FR-001-238** | Financial reports: P&L, Cash Flow, Tax Summary, Expense by Category | High | FR-001-216 |
| **FR-001-239** | Inventory reports: Valuation, Stock Movement, Low Stock, Dead Stock (90d), Count Variance | High | FR-001-066 |
| **FR-001-240** | Repair reports: Summary, Technician Productivity, Parts Usage, Warranty Claims | High | FR-001-191 |
| **FR-001-241** | Customer reports: Purchase History, Top Customers, Segmentation, Credit Aging | Medium | FR-001-161 |
| **FR-001-242** | Supplier reports: Performance, Purchase History, Supply Analysis | Medium | FR-001-181 |
| **FR-001-243** | Employee reports: Activity Log, Cashier Performance, Technician Productivity | Medium | FR-001-261 |
| **FR-001-244** | All reports support configurable date range (default: current month) | High | FR-001-236 |
| **FR-001-245** | All reports exportable to PDF, Excel (XLSX), CSV | High | FR-001-236 |
| **FR-001-246** | Reports display in tabular format and charts (bar, line, pie) where applicable | Medium | FR-001-236 |
| **FR-001-247** | Scheduled report generation: daily/weekly/monthly email to recipients | Medium | None |
| **FR-001-248** | Period comparison: current vs. previous with variance | Low | FR-001-237 |
| **FR-001-249** | Drill-down: click aggregate values to see underlying transactions | Medium | FR-001-237 |
| **FR-001-250** | Reports respect user role permissions | Critical | FR-001-236, FR-001-261 |
| **FR-001-251** | Report caching for frequently-run reports (24-hour cache) | Low | FR-001-236 |
| **FR-001-252** | Report preview: first 50 rows before full generation | Low | FR-001-236 |
| **FR-001-253** | Custom report filters beyond date range | Medium | FR-001-236 |
| **FR-001-254** | Generation progress indicator for large datasets | Low | FR-001-236 |
| **FR-001-255** | Budget vs. Actual comparison report | Low | None |
| **FR-001-256** | PDF report template customization (logo, header, footer) | Low | FR-001-245 |
| **FR-001-257** | Tax reports in local tax authority format (configurable) | Medium | FR-001-238 |
| **FR-001-258** | One-click dashboard export to summary PDF | Low | FR-001-236 |
| **FR-001-259** | Z-Read historical snapshots stored | Low | FR-001-221 |
| **FR-001-260** | All report generation events logged in AuditLog | Medium | FR-001-236 |

### Reporting Checklist

- [x] Reporting dashboard with categorized reports
- [x] Sales reports (summary, by product, category, cashier, customer, payment)
- [x] Financial reports (P&L, cash flow, tax, expenses)
- [x] Inventory reports (valuation, movement, low stock, dead stock, variance)
- [x] Repair reports (summary, technician, parts, warranty)
- [x] Customer/supplier/employee reports
- [x] Configurable date range
- [x] Export to PDF, Excel, CSV
- [x] Tabular and chart display
- [ ] Scheduled report generation (email)
- [ ] Period comparison with variance
- [ ] Drill-down to transactions
- [ ] Role-based data access
- [ ] Report caching
- [ ] Report preview
- [ ] Custom filters
- [ ] Generation progress
- [ ] Budget vs. actual
- [ ] PDF template customization
- [ ] Tax authority format
- [ ] Dashboard export
- [ ] Z-Read snapshots
- [ ] Audit logging

---

## Employee Management

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-261** | Employee CRUD at `/employees/*` (Admin/Super Admin only) | Critical | FR-001-007 |
| **FR-001-262** | Employee fields: name, username (unique), email (unique), phone, role, password (complexity rules), active | Critical | FR-001-261 |
| **FR-001-263** | Predefined roles: Super Admin, Admin, Manager, Cashier, Senior Cashier, Inventory Clerk, Technician, Accountant, Procurement, Viewer | High | FR-001-261 |
| **FR-001-264** | Granular permission flags per role covering all major operations | High | FR-001-263 |
| **FR-001-265** | Custom role creation with custom permission sets | Medium | FR-001-264 |
| **FR-001-266** | Permission enforcement on every route and action — HTTP 403 for unauthorized | Critical | FR-001-264 |
| **FR-001-267** | Employee list: name, username, email, role, active, last login, created date | Medium | FR-001-261 |
| **FR-001-268** | Employee detail: profile, role, permissions, activity log (50), login history | Medium | FR-001-267 |
| **FR-001-269** | Employee deactivation (soft): cannot log in, historical data preserved | High | FR-001-261 |
| **FR-001-270** | Password change requires current password verification | High | FR-001-019 |
| **FR-001-271** | Only Super Admin can reset another employee's password (with force-change flag) | High | FR-001-270 |
| **FR-001-272** | Employee activity tracking: every action with timestamp, IP, details | Critical | FR-001-261 |
| **FR-001-273** | Time-off tracking: leave requests with approval workflow | Low | FR-001-261 |
| **FR-001-274** | Shift management: shift assignment, clock in/out, attendance report | Low | FR-001-261 |
| **FR-001-275** | All employee operations logged in AuditLog | Critical | FR-001-261 |

### Employee Checklist

- [x] Employee CRUD (Admin/Super Admin only)
- [x] Unique username and email
- [x] Predefined roles (10 roles)
- [x] Granular permission flags
- [ ] Custom role creation
- [x] Route/action permission enforcement
- [x] Employee list with details
- [x] Employee detail with activity log
- [x] Soft deactivation
- [x] Password change requires current password
- [x] Super Admin password reset
- [ ] Activity tracking
- [ ] Time-off tracking
- [ ] Shift management
- [x] Full audit logging

---

## Audit System

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-276** | The system MUST maintain an `audit_log` table recording all data modifications | Critical | All modules |
| **FR-001-277** | Each entry: timestamp (UTC), user ID, username, action (CREATE/UPDATE/DELETE/VOID/LOGIN/LOGOUT), entity type, entity ID, old values (JSON), new values (JSON), IP address, User-Agent, request URL | Critical | FR-001-276 |
| **FR-001-278** | Audit log is append-only — no deletion or modification of existing entries | Critical | FR-001-277 |
| **FR-001-279** | Audit log view at `/audit` with filters: date range, user, entity type, action | High | FR-001-277 |
| **FR-001-280** | Audit log search: by entity ID, user, keywords in change data | Medium | FR-001-279 |
| **FR-001-281** | Audit log export to CSV/Excel | Low | FR-001-279 |
| **FR-001-282** | Audit log retention: minimum 5 years (configurable); older entries archived | Medium | FR-001-278 |
| **FR-001-283** | Audit log MUST be backed up as part of regular database backup | Critical | FR-001-282 |
| **FR-001-284** | Audit log MUST NOT be truncated without explicit admin action and logging of the truncation | High | FR-001-278 |
| **FR-001-285** | Read operations on sensitive data (customer PII, financial records) MAY be optionally logged | Medium | FR-001-277 |

### Audit Checklist

- [x] Audit_log table with all required fields
- [x] Append-only (no modification/deletion)
- [x] Audit log view with filters
- [ ] Search capability
- [ ] Export to CSV/Excel
- [ ] Retention policy (5 years)
- [ ] Backup inclusion
- [ ] Truncation protection
- [ ] Optional read logging

---

## Notification System

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-286** | The system MUST provide an in-app notification system visible from the navigation bar | High | None |
| **FR-001-287** | Notifications for low stock: product name, current qty, reorder point | High | FR-001-083 |
| **FR-001-288** | Notifications for warranty expiry: customer, product, expiry date | Medium | FR-001-069 |
| **FR-001-289** | Notifications for overdue repairs: repair ticket, customer, days overdue | High | FR-001-191 |
| **FR-001-290** | Notifications for purchase order overdue: PO number, supplier, expected date | Medium | FR-001-141 |
| **FR-001-291** | Notifications appear as a badge count on the bell icon in the navbar | High | FR-001-286 |
| **FR-001-292** | Clicking a notification navigates to the relevant record | Medium | FR-001-291 |
| **FR-001-293** | Notifications support mark-as-read and mark-all-as-read | Medium | FR-001-286 |
| **FR-001-294** | Email notifications for critical events: password reset, low stock, repair ready | Medium | None |
| **FR-001-295** | Notification preferences per user: configure which events trigger notifications | Low | FR-001-286 |

### Notification Checklist

- [x] In-app notification system with bell icon
- [x] Low stock notifications
- [ ] Warranty expiry notifications
- [x] Overdue repair notifications
- [ ] Overdue PO notifications
- [x] Badge count on navbar
- [x] Click navigates to record
- [ ] Mark as read / mark all as read
- [ ] Email notifications
- [ ] User notification preferences

---

## Barcode/QR Generation and Printing

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-296** | Generate EAN-13 barcodes for products without a manually entered barcode | High | FR-001-037 |
| **FR-001-297** | Generate QR codes for products encoding: product ID, name, price, SKU | Medium | FR-001-037 |
| **FR-001-298** | Barcode label printing: single label per product from product detail page | High | FR-001-296 |
| **FR-001-299** | Bulk barcode label printing: select products, define quantity per label, print | Medium | FR-001-298 |
| **FR-001-300** | Barcode label template configuration: label size, font, fields to include | Low | FR-001-298 |
| **FR-001-301** | Generate QR codes for invoices: encode invoice URL for customer scanning | Low | FR-001-107 |
| **FR-001-302** | Generate QR codes for repair tickets: encode ticket URL for tracking | Low | FR-001-191 |
| **FR-001-303** | Barcode supports Code 128 format as an alternative to EAN-13 | Medium | FR-001-296 |
| **FR-001-304** | Barcode images render in PNG format at 300 DPI for print quality | Medium | FR-001-296 |
| **FR-001-305** | Barcode scanning at POS auto-detects barcode format and finds product | Critical | FR-001-094, FR-001-296 |

### Barcode Checklist

- [x] EAN-13 barcode generation
- [ ] QR code generation
- [x] Single label printing
- [ ] Bulk label printing
- [ ] Label template configuration
- [ ] Invoice QR codes
- [ ] Repair ticket QR codes
- [ ] Code 128 support
- [x] 300 DPI rendering
- [x] POS barcode scanning

---

## File Storage

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-306** | The system MUST support file uploads for product images, repair attachments, and invoice PDFs | Medium | None |
| **FR-001-307** | Uploaded files stored in `data/uploads/` organized by entity type (products, repairs, invoices) | Medium | FR-001-306 |
| **FR-001-308** | File type validation: allowed types (JPEG, PNG, PDF, DOCX) with max size 16 MB (configurable) | Medium | FR-001-306 |
| **FR-001-309** | File names sanitized: remove special characters, add UUID prefix to prevent collision | Medium | FR-001-306 |
| **FR-001-310** | File access restricted: only authenticated users with appropriate permissions can access files | High | FR-001-306, FR-001-266 |

### File Storage Checklist

- [x] File upload support for products, repairs, invoices
- [x] Organized directory structure
- [ ] File type and size validation
- [ ] File name sanitization
- [ ] Access control on file serving

---

## AI Features

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| **FR-001-311** | Sales forecasting: AI model (Prophet/ARIMA) predicts daily sales for next 30 days based on historical data | Medium | FR-001-121 |
| **FR-001-312** | Forecast visualization: line chart showing historical sales + forecasted sales with confidence intervals | Low | FR-001-311 |
| **FR-001-313** | Stock prediction: AI suggests reorder quantities based on sales velocity, lead time, and seasonality | Medium | FR-001-084, FR-001-311 |
| **FR-001-314** | Anomaly detection: flag unusual sales patterns (potential fraud, data entry errors) | Low | FR-001-121 |
| **FR-001-315** | Repair diagnosis suggestions: knowledge base of common issues matched to symptoms using keyword analysis | Low | FR-001-191 |
| **FR-001-316** | Customer churn prediction: identify customers who haven't purchased in 90+ days with re-engagement suggestions | Low | FR-001-161 |
| **FR-001-317** | AI model training runs weekly via background task (RQ/Celery) | Low | FR-001-311 |
| **FR-001-318** | Model performance metrics displayed: MAE, RMSE, forecast accuracy percentage | Low | FR-001-317 |
| **FR-001-319** | All AI features have a manual override — predictions are suggestions only | Medium | FR-001-311 |
| **FR-001-320** | AI features phase: delivered in Phase 2 (see roadmap); v1.0 ships without AI | Low | None |

### AI Checklist

- [ ] Sales forecasting (30-day)
- [ ] Forecast visualization with confidence intervals
- [ ] Stock prediction with reorder suggestions
- [ ] Anomaly detection
- [ ] Repair diagnosis suggestions
- [ ] Customer churn prediction
- [ ] Weekly model training
- [ ] Model performance metrics
- [ ] Manual override for AI suggestions
- [ ] Deferred to Phase 2

---

*This document is maintained by the Product Management team. For questions or corrections, contact product@computershop-erp.com.*
