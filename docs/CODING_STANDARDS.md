# Coding Standards — ERP POS System

> **Version:** 1.0  
> **Last Updated:** 2026-06-24  
> **Audience:** All Developers  
> **Enforcement:** Code Review, Linters (ruff, eslint)

---

## Table of Contents

1. [Python Coding Standards](#1-python-coding-standards)
2. [JavaScript Coding Standards](#2-javascript-coding-standards)
3. [HTML / CSS Standards](#3-html--css-standards)
4. [File and Directory Naming Conventions](#4-file-and-directory-naming-conventions)
5. [Import Ordering Rules](#5-import-ordering-rules)
6. [Docstring Requirements](#6-docstring-requirements)
7. [Type Hinting Requirements](#7-type-hinting-requirements)
8. [Error Handling Patterns](#8-error-handling-patterns)
9. [Logging Standards](#9-logging-standards)
10. [Comment Standards](#10-comment-standards)
11. [Code Review Checklist](#11-code-review-checklist)
12. [Git Commit Message Conventions](#12-git-commit-message-conventions)
13. [Testing Standards](#13-testing-standards)
14. [Security Coding Practices](#14-security-coding-practices)
15. [Database Access Patterns](#15-database-access-patterns)
16. [API Response Format Standards](#16-api-response-format-standards)
17. [Code Organization Within Files](#17-code-organization-within-files)

---

## 1. Python Coding Standards

### 1.1 PEP 8 Compliance

All Python code MUST comply with PEP 8, enforced via `ruff` with the following project-specific overrides:

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "D", "UP", "B", "SIM", "ARG", "C4", "T20"]
ignore = [
    "D203",  # 1 blank line required before class docstring
    "D213",  # Multi-line docstring summary should start at second line
    "D406",  # Section name should end with a newline
]

[tool.ruff.format]
quote-style = "double"
```

### 1.2 Naming Conventions

| Construct | Convention | Example | Notes |
|-----------|------------|---------|-------|
| **Module/File** | `snake_case` | `sales_service.py` | Short, descriptive |
| **Class** | `PascalCase` | `SalesService`, `TTLCache` | Nouns or noun phrases |
| **Function/Method** | `snake_case` | `create_sale()`, `get_db()` | Verbs or verb phrases |
| **Variable** | `snake_case` | `product_name`, `sale_items` | Clear, descriptive |
| **Constant** | `UPPER_SNAKE_CASE` | `MAX_LOGIN_ATTEMPTS`, `DEFAULT_TAX_RATE` | Module-level constants only |
| **Private attribute** | `_leading_underscore` | `_cache`, `_validate_input()` | Implementation details |
| **Dunder methods** | `__dunder__` | `__init__`, `__repr__` | Only standard Python dunders |
| **Type variable** | `T`, `TKey`, `TValue` | `T = TypeVar("T")` | Single letter or descriptive |
| **Exception** | `PascalCase` + `Error` suffix | `StockError`, `ValidationError` | Clear, descriptive |

### 1.3 Line Length and Wrapping

- Maximum line length: **100 characters**
- Line continuation: use parentheses for implicit continuation, NOT backslashes

```python
# GOOD — implicit continuation
cursor.execute(
    "SELECT id, name, unit_price, stock, category_id "
    "FROM products WHERE category = ? AND active = 1 "
    "ORDER BY name LIMIT ? OFFSET ?",
    (category, limit, offset),
)

# BAD — backslash continuation
cursor.execute("SELECT id, name, unit_price FROM products " + \
               "WHERE category = ? AND active = 1")
```

### 1.4 Indentation

- **4 spaces** per indentation level. No tabs.
- Continuation lines align with the opening delimiter:

```python
# Aligned with opening delimiter
result = some_function(
    argument_one, argument_two,
    argument_three, argument_four,
)

# Hanging indent (4 spaces deeper)
result = some_function(
    argument_one, argument_two,
    argument_three, argument_four,
)
```

### 1.5 Blank Lines

- **Two blank lines** between top-level definitions (classes, functions)
- **One blank line** between methods within a class
- **One blank line** between logical sections within a function (sparingly)

```python
import os
import sys


class SalesService:
    ...

    def create_sale(self):
        ...

    def refund_sale(self):
        ...


class StockEngine:
    ...
```

### 1.6 String Quotes

- Double quotes for strings that are likely to contain single quotes (e.g., contractions)
- Single quotes for strings that contain double quotes (e.g., JSON-like strings)
- Consistency within a file: prefer double quotes unless single quotes avoid escaping

```python
# Double quotes preferred
name = "Ahmed's Electronics"
error = f"Product {product_id} not found"

# Single quotes when string contains double quotes
html = '<div class="product-card">'
```

### 1.7 Boolean Comparisons

```python
# GOOD
if stock > 0:
if not user:
if user is None:
if items:
if len(items) == 0:

# BAD
if stock != 0:
if user == False:
if user == None:
if len(items) > 0:
if items != []:
```

### 1.8 `is` vs `==`

```python
# Use is for None, True, False
if user is None:
if enabled is True:

# Use == for value comparison
if user.role == "admin":
```

### 1.9 List/Dict Comprehensions

```python
# GOOD — simple comprehensions
active_products = [p for p in products if p["active"]]
names = {p["id"]: p["name"] for p in products}

# BAD — complex comprehensions (use for loop instead)
# items = [process(x) for x in data if x["status"] == "active" and x["count"] > 0 and validate(x)]
```

---

## 2. JavaScript Coding Standards

### 2.1 Language Version

- **ES6+** (ECMAScript 2015+). No transpilation — modern browsers support ES6 natively.
- Use `const` and `let`. Never use `var`.

### 2.2 Naming Conventions

| Construct | Convention | Example |
|-----------|------------|---------|
| **Variable** | `camelCase` | `productName`, `saleItems` |
| **Function** | `camelCase` | `addItem()`, `formatCurrency()` |
| **Class** | `PascalCase` | `SalesPage`, `ProductSearch` |
| **Global object** | `UPPER_SNAKE_CASE` | `ERP` (singleton), `API_ENDPOINTS` |
| **Event handler** | `handle` prefix | `handleClick()`, `handleScan()` |
| **Private method** | `_leadingUnderscore` | `_validateInput()` |
| **Constants** | `UPPER_SNAKE_CASE` | `SCAN_TIMEOUT_MS`, `MAX_ITEMS` |

### 2.3 Semicolons

- **Required**. Use semicolons at the end of every statement.
- Rationale: avoids ambiguity and minification errors.

```javascript
// GOOD
const items = [];
items.push(product);
processData(items);

// BAD
const items = []
items.push(product)
processData(items)
```

### 2.4 Async/Await

- Use `async/await` for asynchronous operations. Avoid raw `.then()` chains.
- Handle errors with `try/catch` in async functions.

```javascript
// GOOD
async function loadProducts(category) {
    try {
        const response = await fetch(`/api/products?category=${encodeURIComponent(category)}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        ERP.notify('error', `Failed to load products: ${error.message}`);
        return [];
    }
}

// BAD
function loadProducts(category) {
    return fetch(`/api/products?category=${category}`)
        .then(response => response.json())
        .then(data => { /* ... */ })
        .catch(error => { /* ... */ });
}
```

### 2.5 Strict Equality

- Always use `===` and `!==`. Never use `==` or `!=`.

```javascript
// GOOD
if (item.quantity === 0) { ... }
if (response.status !== 200) { ... }

// BAD
if (item.quantity == 0) { ... }
if (response.status != 200) { ... }
```

### 2.6 Variable Declarations

- One variable per declaration statement.

```javascript
// GOOD
const product = getProduct(id);
const quantity = product.stock;

// BAD
const product = getProduct(id), quantity = product.stock;
```

### 2.7 Template Literals

- Use template literals instead of string concatenation.

```javascript
// GOOD
const url = `/products/${productId}/edit`;
const message = `Product ${name} (SKU: ${sku}) — $${price}`;

// BAD
const url = '/products/' + productId + '/edit';
const message = 'Product ' + name + ' (SKU: ' + sku + ') — $' + price;
```

### 2.8 Arrow Functions

- Prefer arrow functions for callbacks and short functions.
- Use block body `{}` when function body has multiple statements.

```javascript
// GOOD
items.map(item => item.price * item.quantity);
items.filter(item => item.quantity > 0);

items.forEach(item => {
    const total = item.price * item.quantity;
    grandTotal += total;
});

// BAD
items.map(function(item) { return item.price * item.quantity; });
```

### 2.9 Object Destructuring

```javascript
// GOOD
const { name, unitPrice, stock } = product;
const [first, ...rest] = items;

function processSale({ cashierId, items, payments }) {
    // ...
}

// BAD
const name = product.name;
const price = product.unitPrice;
const stock = product.stock;
```

### 2.10 Event Handling

- Use `addEventListener`, not inline `onclick` attributes.
- Remove event listeners when they are no longer needed.

```javascript
// GOOD
document.getElementById('search-input')
    .addEventListener('input', debounce(handleSearch, 300));

// BAD
<button onclick="handleClick()">Click</button>
```

---

## 3. HTML / CSS Standards

### 3.1 Semantic HTML

- Use semantic HTML5 elements: `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>`
- Use `<h1>` through `<h6>` for headings in hierarchy
- Use `<table>` for tabular data, not for layout
- Use `<button>` for actions, `<a>` for navigation
- Every form input must have a `<label>` element (accessibility)

```html
<!-- GOOD -->
<nav aria-label="Main navigation">
    <ul>
        <li><a href="/sales/new">New Sale</a></li>
        <li><a href="/products">Products</a></li>
    </ul>
</nav>

<!-- BAD -->
<div class="nav">
    <span onclick="location.href='/sales/new'">New Sale</span>
</div>
```

### 3.2 BEM-like CSS Naming

- **Block**: the component name (`product-card`, `sale-form`)
- **Element**: a part of the block (`product-card__header`, `sale-form__input`)
- **Modifier**: a variant of the block/element (`product-card--featured`, `sale-form__input--error`)
- Use single hyphen between words in block/element names

```css
/* Block */
.product-card {
    border: 1px solid #ddd;
    padding: 16px;
}

/* Element */
.product-card__header {
    font-weight: bold;
    margin-bottom: 8px;
}

.product-card__price {
    color: #2e7d32;
    font-size: 1.2em;
}

/* Modifier */
.product-card--featured {
    border-color: #ff6f00;
    background-color: #fff8e1;
}

.product-card__price--discounted {
    color: #c62828;
    text-decoration: line-through;
}
```

### 3.3 CSS Organization

Properties within a rule should be ordered:

1. **Positioning**: `position`, `top`, `right`, `bottom`, `left`, `z-index`
2. **Box model**: `display`, `flex`, `grid`, `width`, `height`, `margin`, `padding`, `border`
3. **Typography**: `font`, `line-height`, `color`, `text-align`
4. **Visual**: `background`, `box-shadow`, `border-radius`, `opacity`
5. **Animation**: `transition`, `transform`, `animation`
6. **Misc**: `cursor`, `overflow`, `visibility`

```css
.button {
    /* Positioning */
    position: relative;
    z-index: 1;

    /* Box model */
    display: inline-flex;
    align-items: center;
    height: 40px;
    padding: 0 16px;
    border: 1px solid #1976d2;
    border-radius: 4px;

    /* Typography */
    font-family: inherit;
    font-size: 14px;
    font-weight: 500;
    color: #ffffff;

    /* Visual */
    background-color: #1976d2;
    cursor: pointer;

    /* Animation */
    transition: background-color 0.2s ease;
}

.button:hover {
    background-color: #1565c0;
}
```

### 3.4 Responsive Design

- Use CSS Grid for page layout, Flexbox for component layout
- Breakpoints defined as CSS custom properties
- Mobile-first: base styles are for mobile, media queries add desktop styles

```css
:root {
    --breakpoint-sm: 576px;
    --breakpoint-md: 768px;
    --breakpoint-lg: 992px;
    --breakpoint-xl: 1200px;
}

/* Mobile first: single column */
.sales-layout {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
}

/* Tablet: two columns */
@media (min-width: 768px) {
    .sales-layout {
        grid-template-columns: 1fr 1fr;
    }
}

/* Desktop: three columns */
@media (min-width: 992px) {
    .sales-layout {
        grid-template-columns: 1fr 1fr 1fr;
    }
}
```

### 3.5 Accessibility

- All images must have `alt` text
- All form inputs must have associated `<label>` with `for` attribute
- Color contrast ratio must be at least 4.5:1 for normal text
- Focus indicators must be visible (do not remove `outline` without providing alternative)
- Use `aria-label` and `aria-describedby` where appropriate
- Interactive elements must be keyboard-accessible

---

## 4. File and Directory Naming Conventions

### 4.1 Python Files

| Type | Pattern | Example |
|------|---------|---------|
| Route blueprint | `snake_case.py` | `sales.py`, `products.py` |
| Service module | `snake_case.py` | `sales_service.py`, `stock_engine.py` |
| Utility module | `snake_case.py` | `decorators.py`, `helpers.py` |
| Database module | `snake_case.py` | `connection.py`, `seed.py` |
| Schema definition | `snake_case.sql` | `schema.sql` |
| Migration | `{n}_{description}.sql` | `001_add_customer_loyalty.sql` |

### 4.2 Frontend Files

| Type | Pattern | Example |
|------|---------|---------|
| HTML template | `snake_case.html` | `create_product.html` |
| CSS file | `snake_case.css` | `style.css`, `print.css` |
| JavaScript file | `snake_case.js` | `app.js`, `sales.js` |

### 4.3 Documentation Files

| Type | Pattern | Example |
|------|---------|---------|
| Architecture docs | `UPPER_SNAKE_CASE.md` | `SYSTEM_ARCHITECTURE.md` |
| User guides | `snake_case.md` | `getting_started.md` |

### 4.4 Configuration Files

| Type | Pattern | Example |
|------|---------|---------|
| Python config | `snake_case.py` | `config.py` |
| Docker config | PascalCase | `Dockerfile` |
| Compose config | `kebab-case.yml` | `docker-compose.yml` |
| Git config | dotfile | `.gitignore` |

---

## 5. Import Ordering Rules

### 5.1 Python Import Order

Imports must be grouped in the following order, with a blank line between groups:

1. **Standard library** (`os`, `sys`, `datetime`, `json`, `functools`, `logging`)
2. **Third-party packages** (`flask`, `bcrypt`, `python_escpos`)
3. **Application modules** (`database.connection`, `utils.decorators`, `services.sales_service`)

Within each group, imports are sorted alphabetically by module name.

```python
# Standard library
import functools
import json
import logging
import os
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Any

# Third-party
from flask import Blueprint, request, render_template, redirect, url_for, flash, g
from werkzeug.exceptions import Forbidden

# Application
from database.connection import get_db
from services.sales_service import SalesService
from utils.decorators import login_required, require_permission
from utils.helpers import validate_currency, format_date
```

### 5.2 Import Style Rules

- Prefer `import module` over `from module import ...` for standard library modules used multiple times
- Prefer `from module import ...` for third-party packages where you only need specific names
- Avoid `from module import *` — it pollutes the namespace and makes code unclear
- Absolute imports only. No relative imports (`from ..services import ...` is banned)

### 5.3 JavaScript Import Order

Not applicable in vanilla JS (no ES modules). When modules are added in the future:

```javascript
// 1. Standard library (none available in browser JS)
// 2. Third-party (if using CDN or npm)
// 3. Application modules
import { ERP } from './app.js';
import { formatCurrency } from './utils.js';
```

---

## 6. Docstring Requirements

### 6.1 Google-Style Docstrings

All public modules, classes, functions, and methods **MUST** have docstrings following the Google style.

```python
def create_sale(
    cashier_id: int,
    items: list[SaleItem],
    payments: list[dict],
    customer_id: Optional[int] = None,
) -> SaleResult:
    """
    Create a new sale with stock deduction and payment recording.

    This function validates stock availability for all items, calculates
    totals including tax, records the sale and payments, and deducts
    inventory. All operations are atomic within a single transaction.

    Args:
        cashier_id: User ID of the cashier processing the sale.
        items: List of SaleItem dataclasses representing products sold.
            Each item must have product_id, quantity, unit_price, and
            optional discount fields.
        payments: List of payment dicts. Each dict must contain:
            - method (str): "cash", "card", "credit", or "split"
            - amount (float): Payment amount
            - reference (str, optional): Transaction reference number
        customer_id: Optional customer ID for loyalty tracking.

    Returns:
        SaleResult dataclass containing:
        - sale_id: Database ID of the new sale
        - total: Grand total including tax
        - items_count: Number of unique line items
        - timestamp: When the sale was completed

    Raises:
        ValueError: If any item has insufficient stock, payment total
            doesn't match sale total, or the sale contains no items.
        RuntimeError: If a database error occurs during processing.
            The transaction is rolled back before raising.

    Example:
        >>> service = SalesService()
        >>> result = service.create_sale(
        ...     cashier_id=1,
        ...     items=[SaleItem(product_id=5, quantity=2, unit_price=Decimal("19.99"))],
        ...     payments=[{"method": "cash", "amount": 45.58}],
        ... )
        >>> result.sale_id
        142
    """
```

### 6.2 Minimum Docstring Requirements

| Construct | Docstring Required? | Minimum Content |
|-----------|-------------------|-----------------|
| Module (file) | Yes (first line) | One-line description of the module's purpose |
| Public class | Yes | Description, usage notes if non-obvious |
| Public method | Yes | Description, Args, Returns, Raises |
| Private method | No | Optional (comment only if non-obvious) |
| Route function | Yes | Description, form fields expected, templates rendered |
| Decorator | Yes | Description, Args (including decorated function), behavior |
| Configuration class | Yes | Description of what this config is for |
| Exception class | No | Optional (name should be self-explanatory) |

### 6.3 Module-Level Docstrings

Every Python file must have a module-level docstring as the first statement:

```python
"""
Authentication service for the ERP POS system.

Handles user login, logout, password hashing, session management,
and role-based access control (RBAC) permission resolution.

Typical usage:
    from services.auth_service import AuthService
    service = AuthService()
    user = service.authenticate("username", "password")
"""
```

### 6.4 Inline Comments

- Use comments to explain **why**, not **what** (the code shows what)
- Comments should be complete sentences with proper punctuation
- Place comments on the line above the code they explain, not at the end of the line

```python
# GOOD — explains why this approach is taken
# Use a single SQL query instead of N+1 to avoid performance issues
# when rendering the product list with category names.
cursor.execute("""
    SELECT p.*, c.name AS category_name
    FROM products p
    LEFT JOIN categories c ON c.id = p.category_id
    WHERE p.active = 1
""")

# BAD — states the obvious
# Execute SQL query to select all active products
cursor.execute("SELECT * FROM products WHERE active = 1")
```

---

## 7. Type Hinting Requirements

### 7.1 When Type Hints Are Required

| Location | Required? | Notes |
|----------|-----------|-------|
| All function parameters | **Yes** | Every parameter must have a type hint |
| All return values | **Yes** | Every function must have a return type (use `None` if no return) |
| Module-level variables | **Yes** | Constants and module-level singletons |
| Class instance variables | **Yes** | All `__init__` attributes must be typed |
| Local variables | No | Optional, but encouraged for complex types |

### 7.2 Type Hint Syntax

```python
from typing import Optional, Union, Any, Callable
from decimal import Decimal
from datetime import datetime, date
from collections.abc import Sequence, Mapping

# Basic types
def get_product(name: str, active: bool = True) -> Optional[dict]:
    ...

# Lists and dicts with typed contents
def search_products(
    query: str,
    page: int = 1,
    per_page: int = 50,
) -> tuple[list[dict], int]:
    ...

# Optional vs Union
def process_sale(
    customer_id: Optional[int] = None,  # Preferred: can be None
    payment_method: Union[str, list[str]] = "cash",  # Union when multiple non-None types
) -> None:
    ...

# Callable
def validate_input(
    data: dict,
    validator: Callable[[dict], list[str]],
) -> bool:
    ...

# Type aliases for complex types
ProductData = dict[str, Union[str, int, float, None]]
ValidationErrors = dict[str, str]
```

### 7.3 Dataclasses for Structured Data

Use `@dataclass` for structured data that crosses layer boundaries:

```python
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime


@dataclass
class SaleItem:
    product_id: int
    quantity: int
    unit_price: Decimal
    discount_percent: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")


@dataclass
class SaleResult:
    sale_id: int
    total: Decimal
    items_count: int
    timestamp: datetime
    items: list[SaleItem] = field(default_factory=list)
```

### 7.4 Type Checking With pyright/mypy

```toml
# pyproject.toml
[tool.pyright]
typeCheckingMode = "basic"
include = ["app.py", "routes", "services", "utils", "database"]
exclude = ["flask_session", "migrations"]
```

---

## 8. Error Handling Patterns

### 8.1 Try/Except Specificity

```python
# GOOD — catch specific exceptions
try:
    sale_id = sales_service.create_sale(cashier_id, items, payments)
except ValueError as e:
    flash(str(e), "error")
    return render_template("sales/new.html", error=str(e), ...)
except RuntimeError as e:
    logger.exception("Database error during sale creation")
    flash("A system error occurred. Please try again.", "error")
    return render_template("sales/new.html", ...)

# BAD — bare except catches everything, including KeyboardInterrupt
try:
    sale_id = sales_service.create_sale(cashier_id, items, payments)
except:
    flash("An error occurred", "error")
```

### 8.2 Error Raising Patterns

```python
# GOOD — raise with specific message
def deduct_stock(self, product_id, quantity, cursor):
    cursor.execute(
        "UPDATE store_stock SET quantity = quantity - ? "
        "WHERE product_id = ? AND quantity >= ?",
        (quantity, product_id, quantity),
    )
    if cursor.rowcount == 0:
        current = cursor.execute(
            "SELECT quantity FROM store_stock WHERE product_id = ?",
            (product_id,),
        ).fetchone()
        available = current["quantity"] if current else 0
        raise ValueError(
            f"Insufficient stock for product {product_id}. "
            f"Requested {quantity}, available {available}."
        )

# BAD — generic error with no context
def deduct_stock(self, product_id, quantity, cursor):
    if quantity > self.get_stock(product_id):
        raise ValueError("Not enough stock")
```

### 8.3 Error Handling in Routes

```python
@products_bp.route("/create", methods=["GET", "POST"])
@login_required
@require_permission("products.edit")
def create_product():
    if request.method == "POST":
        try:
            data = parse_product_form(request.form)
            errors = validate_product(data)
            if errors:
                return render_template("products/create.html", errors=errors, data=data)

            product_id = product_service.create_product(data)
            flash(f"Product '{data['name']}' created successfully.", "success")
            return redirect(url_for("products.list_products"))

        except ValueError as e:
            # Business rule violation — show the message to the user
            flash(str(e), "error")
            return render_template("products/create.html", errors={"general": str(e)}, data=data)

        except Exception:
            # Unexpected error — log details, show generic message
            logger.exception("Failed to create product")
            flash("An unexpected error occurred. Please try again.", "error")
            return render_template("products/create.html", errors={}, data=data)

    return render_template("products/create.html", errors={}, data={})
```

### 8.4 Error Handling in Services

```python
class PurchaseService:
    def receive_goods(self, po_id: int, received_items: list[dict], user_id: int) -> dict:
        """
        Record receipt of goods against a purchase order.
        """
        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute("BEGIN TRANSACTION")

            # Verify PO exists and is open
            cursor.execute(
                "SELECT status FROM purchase_orders WHERE id = ?",
                (po_id,)
            )
            po = cursor.fetchone()
            if not po:
                raise ValueError(f"Purchase order {po_id} not found.")
            if po["status"] != "open":
                raise ValueError(
                    f"Cannot receive against PO {po_id}: "
                    f"status is '{po['status']}', expected 'open'."
                )

            # Process each received item
            for item in received_items:
                # ... stock engine add, PO item update

            cursor.execute(
                "UPDATE purchase_orders SET status = 'received', "
                "received_at = datetime('now'), received_by = ? WHERE id = ?",
                (user_id, po_id)
            )

            db.commit()
            logger.info(f"PO {po_id} received by user {user_id}")
            return {"po_id": po_id, "items_received": len(received_items)}

        except ValueError:
            db.rollback()
            raise  # Re-raise business rule violations to the route

        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to receive PO {po_id}")
            raise RuntimeError(f"Failed to receive purchase order: {e}") from e
```

### 8.5 Error Handling Rules Summary

| Rule | Description |
|------|-------------|
| **Be specific** | Catch `ValueError`, `RuntimeError`, `PermissionError`. Never bare `except:` |
| **Log before re-raise** | Log the error with `logger.exception()` before re-raising |
| **Never swallow** | If you catch an exception, either log it, re-raise it, or handle it. Never silently ignore |
| **User messages** | Show generic messages to users. Log the detailed error |
| **Rollback on error** | Always rollback database transactions in except blocks |
| **Re-raise for routes** | Services raise; routes catch and display |
| **Don't use errors for control flow** | Validate before processing. Use errors for truly exceptional situations |

---

## 9. Logging Standards

### 9.1 When to Use `print()` vs `logging`

| Use Case | Method | Reason |
|----------|--------|--------|
| Quick debugging during development | `print()` | Temporary only. Remove before commit |
| Application events | `logging.info()` | User login, sale created, product updated |
| Warnings | `logging.warning()` | Low stock alert, slow query, configuration issue |
| Errors | `logging.error()` | Database failure, network timeout, validation failure |
| Unexpected errors | `logging.exception()` | Errors in except blocks (includes traceback) |
| Debug details | `logging.debug()` | Function entry/exit, variable values (disabled in prod) |
| Printed output | `print()` | **Never committed**. Use logging for all permanent output |

### 9.2 Logger Configuration

```python
# config.py
import logging

def configure_logging(app):
    log_level = logging.DEBUG if app.debug else logging.INFO
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    log_file = app.config.get("LOG_FILE", "logs/erp.log")

    # File handler with rotation
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setFormatter(logging.Formatter(log_format))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))

    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)

    # SQLite queries logging (debug only)
    if app.debug:
        logging.getLogger("database.connection").setLevel(logging.DEBUG)
```

### 9.3 Logger Usage Per Module

```python
# Every module creates its own logger
import logging
logger = logging.getLogger(__name__)


class SalesService:
    def create_sale(self, ...):
        logger.info(f"Creating sale: cashier={cashier_id}, items={len(items)}")

        try:
            # ... processing
            logger.debug(f"Stock deducted for {len(items)} items")
        except ValueError as e:
            logger.warning(f"Sale validation failed: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error creating sale")
            raise RuntimeError("Failed to create sale") from e

        logger.info(f"Sale {sale_id} created successfully, total={grand_total}")
```

### 9.4 Log Level Guidelines

| Level | When to Use |
|-------|-------------|
| **DEBUG** | Detailed information for diagnosing problems. Function entry/exit, variable values, query timings. Disabled in production. |
| **INFO** | Confirmation that things are working. Key business events: user login, sale created, product added, backup completed. |
| **WARNING** | Something unexpected happened but the application can continue. Low stock, slow query (>500ms), config fallback. |
| **ERROR** | A problem that prevents a specific operation but the app continues. Database failure, payment gateway timeout, email send failure. |
| **CRITICAL** | The application cannot continue. Database corruption, disk full, configuration missing. |

### 9.5 What NOT to Log

- **NEVER** log passwords, password hashes, or security secrets
- **NEVER** log full credit card numbers (log last 4 digits only if needed)
- **NEVER** log `SECRET_KEY`, `BACKUP_ENCRYPTION_KEY`, or API keys
- **NEVER** log session tokens or CSRF tokens
- Log personally identifiable information (PII) only when necessary for audit compliance

---

## 10. Comment Standards

### 10.1 When to Comment

| Situation | Should You Comment? | Example |
|-----------|---------------------|---------|
| Complex algorithm | **Yes** — explain the approach | Explanation of a tax calculation with multiple brackets |
| Business rule | **Yes** — explain the rule | "Discounts over 50% require manager approval per store policy" |
| Workaround | **Yes** — explain why | "Workaround for SQLite limitation: using subquery instead of JOIN" |
| Non-obvious decision | **Yes** — explain the rationale | "Using float instead of Decimal here because SQLite returns floats" |
| Obvious code | **No** — code is self-documenting | `stock = stock - quantity` needs no comment |
| Bad code | **No** — refactor instead of commenting | Don't comment "This is slow", fix it |
| TODO | **Minimal** — must have ticket number | `# TODO(ERP-1234): Add caching here` |

### 10.2 Comment Format

```python
# Single-line comment — starts with # and a space at the current indentation.
# For multi-line comments, use # at the start of each line.
# They should be grammatically correct sentences.

# GOOD
# Tax is calculated before discounts per country regulations.
# This ensures the tax base is the full price, not the discounted price.
total_tax = calculate_tax(subtotal)

# BAD
# calculate tax
total_tax = calculate_tax(subtotal)
```

### 10.3 TODO Comments

```python
# Format: # TODO(ticket-number): Description
# NEVER: # TODO: fix this

# GOOD
# TODO(ERP-456): Implement progressive tax brackets
#   Current implementation uses flat 14% VAT rate.
#   Some jurisdictions have tiered VAT rates based on product category.

# BAD
# TODO: add caching
```

---

## 11. Code Review Checklist

### 11.1 Pre-Submit Checklist (Author)

Before submitting code for review, the author must verify:

- [ ] Code follows PEP 8 (ruff passes with project config)
- [ ] Type hints are present on all function signatures
- [ ] Docstrings are present on all public functions/classes
- [ ] No `print()` statements remain (use logging instead)
- [ ] No `TODO` without a ticket number
- [ ] No commented-out code blocks
- [ ] No bare `except:` — only specific exception types
- [ ] All SQL queries use parameterized queries (no f-strings in SQL)
- [ ] No secrets or credentials in code
- [ ] Log messages don't contain PII beyond what's necessary
- [ ] Tests pass (when test suite exists)
- [ ] `ruff check .` passes with no errors

### 11.2 Review Checklist (Reviewer)

- [ ] **Correctness**: Does the code do what it's supposed to?
- [ ] **Edge cases**: Are edge cases handled? (empty results, null values, concurrency)
- [ ] **Error handling**: Are errors caught, logged, and reported to the user appropriately?
- [ ] **Security**: Are all inputs validated? Are SQL queries parameterized? Is XSS prevented?
- [ ] **Performance**: Are there N+1 queries? Are database queries indexed? Is caching appropriate?
- [ ] **Maintainability**: Is the code readable? Are functions single-purpose? Are magic numbers avoided?
- [ ] **Consistency**: Does the code follow project conventions and patterns?
- [ ] **Tests**: Are there tests for the new code? Do existing tests still pass?
- [ ] **Documentation**: Are relevant docs updated? (docs/ files, docstrings)

### 11.3 Review Response Times

| Change Size | Examples | Max Review Time |
|-------------|----------|-----------------|
| Small (1-50 lines) | Bug fix, simple change | 1 business day |
| Medium (50-300 lines) | New route, service method | 2 business days |
| Large (300-1000 lines) | New module, significant refactor | 3 business days |
| X-Large (1000+ lines) | New feature, architecture change | 5 business days (split into smaller PRs) |

---

## 12. Git Commit Message Conventions

### 12.1 Commit Message Format

```
<type>(<scope>): <short summary> (max 72 chars)

<body> (optional, wrap at 72 chars)

<footer> (optional)
```

### 12.2 Types

| Type | When to Use | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(sales): add partial refund functionality` |
| `fix` | Bug fix | `fix(products): handle null barcode in search` |
| `refactor` | Code change that doesn't fix or add | `refactor(auth): extract password validation to helper` |
| `perf` | Performance improvement | `perf(reports): add index to daily_sales query` |
| `test` | Adding or fixing tests | `test(sales): add tests for refund edge cases` |
| `docs` | Documentation only | `docs: add caching strategy to architecture doc` |
| `style` | Formatting, missing semicolons, etc. | `style: fix ruff W293 blank line warnings` |
| `chore` | Build, deps, CI config | `chore: update Flask to 3.1.0` |
| `ci` | CI/CD changes | `ci: add ruff linting to GitHub Actions` |
| `sec` | Security fix | `sec: prevent XSS in product description field` |

### 12.3 Scopes

| Scope | Module |
|-------|--------|
| `auth` | Authentication routes and service |
| `sales` | Sales routes and service |
| `products` | Product routes and service |
| `inventory` | Inventory routes and stock engine |
| `purchases` | Purchase routes and service |
| `customers` | Customer routes |
| `suppliers` | Supplier routes |
| `repairs` | Repair routes and service |
| `employees` | Employee routes |
| `reports` | Report routes |
| `audit` | Audit routes and service |
| `db` | Database schema, connection, migrations |
| `config` | Configuration files |
| `docker` | Docker setup |
| `docs` | Documentation files |
| `ui` | Templates, CSS, JavaScript |

### 12.4 Commit Message Examples

```
feat(sales): implement partial refund with item selection

Add the ability to refund specific items from a sale rather
than requiring a full refund. Selected items are restocked,
and a new credit note is generated.

Closes ERP-234
```

```
fix(products): handle null supplier_id in product list

Products without a supplier were crashing the list view
because supplier.name was accessed on None. Now checks
for null and displays "N/A".

Fixes ERP-567
```

```
refactor(db): extract transaction helpers to connection module

Reduces code duplication across services by providing
`transaction()` context manager that handles begin/commit/
rollback automatically.
```

### 12.5 Commit Rules

- First line is max **72 characters**
- Use imperative mood: "Add", "Fix", "Refactor" (not "Added", "Fixed", "Refactored")
- Body explains **why** the change was made, not **what** changed (git diff shows what)
- Reference issue/ticket numbers in footer
- One commit = one logical change. Squash before merge if needed

---

## 13. Testing Standards

### 13.1 Test Framework

- **pytest** for all Python tests
- Test files in `tests/` directory (to be created)
- Naming: `test_{module}.py`

### 13.2 Test Naming Conventions

| Pattern | Example |
|---------|---------|
| `test_{function}_{scenario}_{expected}` | `test_create_sale_with_valid_data_returns_sale_result` |
| `test_{function}_{error_case}` | `test_create_sale_with_insufficient_stock_raises_error` |
| `Test{Class}` | `TestSalesService` |

### 13.3 Test Structure (Arrange-Act-Assert)

```python
class TestSalesService:
    """Tests for SalesService."""

    def test_create_sale_with_valid_data_returns_sale_result(self):
        # Arrange
        service = SalesService()
        cashier_id = 1
        items = [SaleItem(product_id=5, quantity=2, unit_price=Decimal("19.99"))]
        payments = [{"method": "cash", "amount": 45.58}]

        # Act
        result = service.create_sale(cashier_id, None, items, payments)

        # Assert
        assert result.sale_id > 0
        assert result.total == Decimal("45.58")
        assert result.items_count == 1

    def test_create_sale_with_insufficient_stock_raises_error(self):
        # Arrange
        service = SalesService()
        items = [SaleItem(product_id=999, quantity=9999, unit_price=Decimal("10.00"))]
        payments = [{"method": "cash", "amount": 99990.00}]

        # Act & Assert
        with pytest.raises(ValueError, match="Insufficient stock"):
            service.create_sale(1, None, items, payments)
```

### 13.4 Testing Guidelines

| Aspect | Requirement |
|--------|-------------|
| **Coverage** | Minimum 80% for service layer, 60% for routes |
| **Unit tests** | Test services in isolation (mock database) |
| **Integration tests** | Test routes end-to-end with test database |
| **Edge cases** | Test empty inputs, null values, boundary conditions |
| **Security tests** | Test SQL injection attempts, XSS in input fields |
| **Performance tests** | Future: benchmark critical paths (sales, search) |

### 13.5 Fixtures

```python
import pytest
from app import create_app


@pytest.fixture
def app():
    """Create test app with in-memory database."""
    app = create_app("testing")
    with app.app_context():
        from database.connection import get_db
        db = get_db()
        with open("database/schema.sql") as f:
            db.executescript(f.read())
        yield app


@pytest.fixture
def client(app):
    """Test client for route testing."""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Authenticate as admin and return session cookie."""
    client.post("/auth/login", data={
        "username": "admin",
        "password": "admin123",
    })
    return {"Cookie": client.cookie_jar._cookies["localhost.local"]["/"]["session"].value}
```

---

## 14. Security Coding Practices

### 14.1 SQL Injection Prevention

```python
# GOOD — parameterized query
cursor.execute(
    "SELECT * FROM products WHERE name = ? AND category_id = ?",
    (product_name, category_id)
)

# GOOD — parameterized with IN clause (dynamic placeholders)
placeholders = ",".join("?" * len(product_ids))
cursor.execute(
    f"SELECT * FROM products WHERE id IN ({placeholders})",
    product_ids
)

# BAD — string formatting in SQL
cursor.execute(
    f"SELECT * FROM products WHERE name = '{product_name}'"
)

# BAD — string concatenation in SQL
cursor.execute(
    "SELECT * FROM products WHERE name = '" + product_name + "'"
)
```

### 14.2 XSS Prevention

```python
# GOOD — Jinja2 auto-escapes by default
# Template: {{ product.name }}  →  &lt;script&gt;alert(1)&lt;/script&gt;

# GOOD — explicit escaping for user-generated content
from markupsafe import escape
safe_name = escape(user_input)

# BAD — using |safe on untrusted content
# Template: {{ product.description|safe }}  ← Only use if description is trusted HTML

# GOOD — use |safe only on trusted content (generated by the system)
render_template("products/list.html", system_generated_html=html_str|safe)

# JavaScript: prefer textContent over innerHTML
// GOOD
document.getElementById('product-name').textContent = product.name;

// BAD
document.getElementById('product-name').innerHTML = product.name;
```

### 14.3 CSRF Prevention

```python
# All forms must include CSRF token
# Flask-WTF handles this automatically when using:

# 1. In template
<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
</form>

# 2. In route (automatic with Flask-WTF)
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# 3. For AJAX requests, include CSRF token in header
// JavaScript
fetch('/api/sales', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify(data),
});
```

### 14.4 Password Handling

```python
# GOOD — bcrypt hashing
import bcrypt

def hash_password(password: str) -> str:
    """Hash password with bcrypt (cost factor 12)."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash."""
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8")
    )

# BAD — plain text password storage (never)
# BAD — MD5 or SHA1 hashing
# BAD — custom encryption/decryption
```

### 14.5 Session Security

```python
# config.py
class ProductionConfig(Config):
    SESSION_COOKIE_HTTPONLY = True   # Prevent JS access to session cookie
    SESSION_COOKIE_SECURE = True     # HTTPS only
    SESSION_COOKIE_SAMESITE = "Lax"  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
```

### 14.6 File Upload Security

```python
# config.py
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload

# Route handler
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Validate uploaded file
file = request.files.get("image")
if file and allowed_file(file.filename):
    # Sanitize filename (remove path separators, etc.)
    safe_filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, safe_filename))
else:
    flash("Invalid file type. Allowed: PNG, JPG, GIF, PDF", "error")
```

### 14.7 Output Encoding

- All user-supplied data rendered in HTML is auto-escaped by Jinja2
- For JSON APIs, ensure proper `Content-Type: application/json` headers
- For CSV export, sanitize fields that begin with `=` to prevent CSV injection:

```python
def sanitize_csv_field(value: str) -> str:
    """Prevent CSV injection by prefixing dangerous values."""
    if value and value[0] in ("=", "+", "-", "@", "\t", "\n"):
        return "'" + value
    return value
```

---

## 15. Database Access Patterns

### 15.1 Connection Management

```python
# database/connection.py
import sqlite3
from flask import g, current_app

def get_db() -> sqlite3.Connection:
    """Get database connection for current request context."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE_PATH"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode = WAL")
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    """Close database connection at request end."""
    db = g.pop("db", None)
    if db is not None:
        db.close()
```

### 15.2 Parameterized Query Patterns

```python
# SELECT with parameters
cursor.execute(
    "SELECT id, name, unit_price, stock FROM products "
    "WHERE category_id = ? AND active = ? "
    "ORDER BY name LIMIT ? OFFSET ?",
    (category_id, 1, limit, offset),
)

# INSERT with RETURNING
cursor.execute(
    "INSERT INTO products (name, sku, unit_price, cost_price, category_id) "
    "VALUES (?, ?, ?, ?, ?) RETURNING id",
    (name, sku, unit_price, cost_price, category_id),
)
product_id = cursor.fetchone()["id"]

# UPDATE with affected rows check
cursor.execute(
    "UPDATE store_stock SET quantity = quantity - ? "
    "WHERE product_id = ? AND store_id = ? AND quantity >= ?",
    (quantity, product_id, store_id, quantity),
)
if cursor.rowcount == 0:
    raise ValueError("Insufficient stock")

# DELETE with foreign key safety check
cursor.execute(
    "DELETE FROM suppliers WHERE id = ? AND "
    "(SELECT COUNT(*) FROM products WHERE supplier_id = ?) = 0",
    (supplier_id, supplier_id),
)

# Bulk INSERT (500 at a time for performance)
cursor.executemany(
    "INSERT INTO products (name, sku, unit_price, category_id) "
    "VALUES (?, ?, ?, ?)",
    product_batch,
)
```

### 15.3 Transaction Patterns

```python
# Context manager pattern for readability
class transaction:
    """Context manager for database transactions."""
    def __enter__(self):
        self.db = get_db()
        self.db.execute("BEGIN TRANSACTION")
        return self.db.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()
        else:
            self.db.commit()

# Usage
with transaction() as cursor:
    cursor.execute("INSERT INTO sales ...")
    cursor.execute("UPDATE products SET stock = ...")
# Auto-commits on success, auto-rollbacks on exception
```

### 15.4 Query Performance Patterns

```python
# BAD — N+1 queries
for product in products:
    cursor.execute(
        "SELECT name FROM categories WHERE id = ?",
        (product["category_id"],)
    )
    category = cursor.fetchone()
    product["category_name"] = category["name"]

# GOOD — JOIN query
cursor.execute("""
    SELECT p.*, c.name AS category_name
    FROM products p
    LEFT JOIN categories c ON c.id = p.category_id
    WHERE p.active = 1
""")

# BAD — fetching all rows when you only need count
all_products = cursor.execute("SELECT * FROM products").fetchall()
count = len(all_products)

# GOOD — count query
count = cursor.execute("SELECT COUNT(*) FROM products").fetchone()[0]

# GOOD — paginated query with total count
cursor.execute(
    "SELECT COUNT(*) FROM products WHERE active = 1",
)
total = cursor.fetchone()[0]

cursor.execute(
    "SELECT * FROM products WHERE active = 1 "
    "ORDER BY name LIMIT ? OFFSET ?",
    (per_page, (page - 1) * per_page),
)
products = [dict(row) for row in cursor.fetchall()]
```

---

## 16. API Response Format Standards

### 16.1 Success Response (AJAX)

```json
{
    "success": true,
    "data": {
        "sale_id": 142,
        "total": 45.58,
        "items_count": 2,
        "timestamp": "2026-06-24T14:30:00"
    }
}
```

### 16.2 Error Response (AJAX)

```json
{
    "success": false,
    "error": "Insufficient stock for product #42. Requested 5, available 2.",
    "code": "INSUFFICIENT_STOCK",
    "details": {
        "product_id": 42,
        "requested": 5,
        "available": 2
    }
}
```

### 16.3 Validation Error Response

```json
{
    "success": false,
    "error": "Validation failed",
    "code": "VALIDATION_ERROR",
    "fields": {
        "name": "Product name is required",
        "unit_price": "Unit price must be a positive number",
        "sku": "SKU must be under 50 characters"
    }
}
```

### 16.4 Pagination Response

```json
{
    "success": true,
    "data": [
        { "id": 1, "name": "Product A" },
        { "id": 2, "name": "Product B" }
    ],
    "pagination": {
        "page": 1,
        "per_page": 50,
        "total": 234,
        "total_pages": 5,
        "has_prev": false,
        "has_next": true
    }
}
```

### 16.5 Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `INSUFFICIENT_STOCK` | 400 | Not enough inventory |
| `DUPLICATE_ENTRY` | 409 | Unique constraint violation |
| `NOT_FOUND` | 404 | Resource not found |
| `PERMISSION_DENIED` | 403 | User lacks required permission |
| `UNAUTHORIZED` | 401 | Not authenticated |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## 17. Code Organization Within Files

### 17.1 Python File Structure

Every Python file should follow this order:

```python
"""
Module docstring — one line description.

Detailed description if needed.
"""

# === 1. Imports ===
# Standard library
import json
import logging
import os
from datetime import datetime
from typing import Optional

# Third-party
from flask import Blueprint, request, render_template

# Application
from database.connection import get_db
from utils.decorators import login_required

logger = logging.getLogger(__name__)


# === 2. Module-level constants ===
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 50


# === 3. Exception classes (if any) ===
class StockError(Exception):
    """Raised when stock operations fail."""
    pass


# === 4. Public classes ===
class StockEngine:
    """Core inventory management engine."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def check_availability(self, product_id: int, quantity: int) -> bool:
        """Check if sufficient stock exists."""
        ...


# === 5. Private helper functions ===
def _calculate_tax(subtotal: float) -> float:
    """Calculate tax amount (internal helper)."""
    return subtotal * 0.14


# === 6. Public functions ===
def get_stock_engine() -> StockEngine:
    """Factory function to create StockEngine instance."""
    ...
```

### 17.2 Route File Structure

```python
"""
Product management routes.

Provides CRUD endpoints for the product catalog including
barcode lookup, bulk import/export, and search.
"""

# Imports (grouped as above)
import logging
from flask import Blueprint, render_template, request, jsonify

from database.connection import get_db
from utils.decorators import login_required, require_permission
from services import product_service

logger = logging.getLogger(__name__)

# Blueprint definition
products_bp = Blueprint("products", __name__, url_prefix="/products")


# Route functions (GET before POST, list before detail)
@products_bp.route("/")
@login_required
@require_permission("products.view")
def list_products():
    ...


@products_bp.route("/<int:product_id>")
@login_required
@require_permission("products.view")
def get_product(product_id):
    ...


@products_bp.route("/create", methods=["GET", "POST"])
@login_required
@require_permission("products.edit")
def create_product():
    ...


@products_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("products.edit")
def edit_product(product_id):
    ...


# AJAX endpoints at the bottom
@products_bp.route("/search")
@login_required
def search_products():
    ...


@products_bp.route("/barcode/<barcode>")
@login_required
def lookup_barcode(barcode):
    ...
```

### 17.3 Service File Structure

```python
"""
Sales service for the ERP POS system.

Handles sale creation, refunds, holds, and sales history.
All data-modifying operations use explicit transactions.
"""

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from database.connection import get_db, transaction
from services.stock_engine import StockEngine
from services.audit_service import AuditService

logger = logging.getLogger(__name__)


@dataclass
class SaleItem:
    product_id: int
    quantity: int
    unit_price: Decimal
    discount_percent: Decimal = Decimal("0")


@dataclass
class SaleResult:
    sale_id: int
    total: Decimal
    items_count: int


class SalesService:
    """Handles all sales-related business logic."""

    def __init__(self, stock_engine: StockEngine = None):
        self.stock_engine = stock_engine or StockEngine()

    def create_sale(self, ...) -> SaleResult:
        ...

    def refund_sale(self, ...) -> SaleResult:
        ...

    def search_sales(self, ...) -> tuple[list[dict], int]:
        ...

    def _validate_sale_input(self, ...) -> None:
        ...

    @staticmethod
    def _calculate_tax(subtotal: Decimal) -> Decimal:
        ...
```

### 17.4 JavaScript File Structure

```javascript
/**
 * ERP POS System — Sales Page Scripts
 *
 * Handles POS terminal interactivity: barcode scanning,
 * product search, cart management, and payment processing.
 */

// === 1. Constants ===
const SCAN_TIMEOUT_MS = 200;
const SEARCH_DEBOUNCE_MS = 300;

// === 2. Module-level state ===
let scannerBuffer = '';
let scannerTimer = null;

// === 3. Public API ===
export const SalesPage = {
    init() {
        this.setupScanner();
        this.setupSearch();
        this.setupKeyboardShortcuts();
    },

    addItem(product) {
        // ...
    },

    removeItem(productId) {
        // ...
    },
};

// === 4. Private functions ===
function handleScan(input) {
    // Process barcode input
}

function setupScanner() {
    document.addEventListener('keypress', (event) => {
        // ...
    });
}

// === 5. Initialization ===
document.addEventListener('DOMContentLoaded', () => SalesPage.init());
```

### 17.5 CSS File Structure

```css
/*
 * ERP POS System — Main Stylesheet
 *
 * 1. CSS Custom Properties
 * 2. Reset / Base
 * 3. Typography
 * 4. Layout
 * 5. Navigation
 * 6. Forms
 * 7. Tables
 * 8. Cards / Panels
 * 9. Modals
 * 10. Flash Messages
 * 11. POS Terminal
 * 12. Print
 * 13. Responsive
 */

/* === 1. Custom Properties === */
:root {
    --color-primary: #1976d2;
    --color-primary-dark: #1565c0;
    --color-danger: #d32f2f;
    --color-success: #388e3c;
    --color-warning: #f57c00;
    --color-bg: #f5f5f5;
    --color-surface: #ffffff;
    --color-text: #212121;
    --color-text-secondary: #757575;
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    --font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    --border-radius: 4px;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.1);
    --shadow-md: 0 2px 8px rgba(0,0,0,0.15);
}

/* === 2. Reset / Base === */
*, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}
```

---

> **Document Maintainer**: Principal Software Architect  
> **Review Cycle**: Quarterly  
> **Enforcement**: `ruff`, Code Review, Automated CI  
> **Next Review**: 2026-09-24
