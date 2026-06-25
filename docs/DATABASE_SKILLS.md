# Database Skills Guide — ERP System

> **Version:** 1.0  
> **Last Updated:** 2026-06-24  
> **Target Database:** SQLite 3.x (WAL mode, with migration path to PostgreSQL)  
> **Audience:** Backend developers, database administrators, DevOps

---

## Table of Contents

1. [SQLite Expertise](#1-sqlite-expertise)
2. [Query Optimization](#2-query-optimization)
3. [Schema Design](#3-schema-design)
4. [Transaction Management](#4-transaction-management)
5. [Migration Strategy](#5-migration-strategy)
6. [Backup Strategies](#6-backup-strategies)
7. [Performance Monitoring](#7-performance-monitoring)
8. [Common Anti-Patterns](#8-common-anti-patterns)
9. [Security](#9-security)
10. [Appendix](#10-appendix)

---

## 1. SQLite Expertise

### 1.1 WAL Mode (Write-Ahead Log)

```sql
PRAGMA journal_mode = WAL;
```

**Why WAL?** WAL mode allows concurrent reads while a write is in progress. In an ERP system where reporting queries run alongside transaction processing, this is critical.

| Feature | WAL | DELETE (Default) | MEMORY |
|---------|-----|-------------------|--------|
| Concurrent reads during write | Yes | No | No |
| Read performance | Excellent | Good | Best |
| Write performance | Good | Fair | Best |
| Crash safety | Full (checkpoint) | Full | None |
| Disk space | WAL file grows | Minimal | None |

**WAL Checkpointing:**

```sql
-- Manual checkpoint (blocks until complete)
PRAGMA wal_checkpoint(TRUNCATE);

-- Passive checkpoint (allows concurrent reads)
PRAGMA wal_checkpoint(PASSIVE);
```

**Best Practice:** Set `wal_autocheckpoint` to 1000 (default) and schedule checkpoints during low-traffic windows.

### 1.2 PRAGMA Optimization

Optimal startup PRAGMAs for this ERP system:

```python
# Application startup — connection configuration
PRAGMA journal_mode = WAL;           -- WAL mode for concurrency
PRAGMA synchronous = NORMAL;         -- Balance safety/speed (FULL for financial-critical)
PRAGMA cache_size = -64000;          -- 64 MB cache (-N means N KB)
PRAGMA busy_timeout = 5000;          -- Wait 5s before failing on lock
PRAGMA foreign_keys = ON;            -- Enforce FK constraints
PRAGMA temp_store = MEMORY;          -- Temp tables in memory
PRAGMA mmap_size = 268435456;        -- 256 MB memory-mapped I/O
PRAGMA page_size = 4096;             -- 4 KB pages (balanced for HDD/SSD)
PRAGMA auto_vacuum = INCREMENTAL;    -- Control vacuum instead of auto
```

**PRAGMA Reference Table:**

| PRAGMA | Recommended Value | Rationale |
|--------|-------------------|-----------|
| `journal_mode` | `WAL` | Concurrent read/write for live ERP |
| `synchronous` | `NORMAL` | 2x faster than FULL, safe with WAL |
| `cache_size` | `-64000` | Reduces disk I/O for repeated queries |
| `busy_timeout` | `5000` | Prevents immediate lock failures |
| `foreign_keys` | `ON` | Must be set per-connection |
| `temp_store` | `MEMORY` | Faster temp table sorting |
| `mmap_size` | `268435456` | Speeds up large index scans |
| `page_size` | `4096` | Default; 8192 for larger databases |
| `auto_vacuum` | `INCREMENTAL` | Avoids sudden size changes |
| `recursive_triggers` | `ON` | Needed for cascade operations |

### 1.3 Row Factory

Use a row factory for dict-like access (Python example):

```python
import sqlite3

def dict_factory(cursor, row):
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))

conn = sqlite3.connect("erp.db")
conn.row_factory = dict_factory
```

**Why:** ERP queries often return 20–50 columns. Accessing by name (`row["FullName"]`) is far more maintainable than positional (`row[3]`).

**Edge Case — Memory Overhead:** For bulk exports (>10K rows), use `sqlite3.Row` (tuple-like with name access) instead of dict to reduce memory by ~40%.

```python
conn.row_factory = sqlite3.Row  # Lighter than dict_factory for bulk
```

### 1.4 Connection Pooling

SQLite does not support concurrent writes from multiple connections. However, connection pooling is still valuable for read operations.

**Recommended Pattern — Read/Write Split:**

```python
from queue import Queue
import sqlite3
import threading

class SQLitePool:
    def __init__(self, db_path, size=5, is_writer=False):
        self._db_path = db_path
        self._size = size
        self._is_writer = is_writer
        self._pool = Queue(maxsize=size)
        self._lock = threading.Lock()

        for _ in range(size):
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA foreign_keys = ON")
            if is_writer:
                conn.execute("PRAGMA synchronous = FULL")
            else:
                conn.execute("PRAGMA synchronous = NORMAL")
            self._pool.put(conn)

    def acquire(self, timeout=5.0):
        return self._pool.get(timeout=timeout)

    def release(self, conn):
        self._pool.put(conn)

# Single writer, multiple readers
writer_pool = SQLitePool("erp.db", size=1, is_writer=True)
reader_pool = SQLitePool("erp.db", size=10, is_writer=False)
```

**Critical — Write Serialization:** Use a single writer connection (or a mutex) to serialize all writes. Two concurrent writes will result in `SQLITE_BUSY`.

### 1.5 Type Affinities

SQLite uses type *affinities*, not strict types:

| Type Affinity | Declared Types | Behavior |
|---------------|----------------|----------|
| TEXT | `CHAR`, `CLOB`, `TEXT` | Stores as string |
| NUMERIC | `NUMERIC`, `DECIMAL`, `BOOLEAN`, `DATE` | Numeric if possible |
| INTEGER | `INT`, `BIGINT`, `INTEGER` | 1, 2, 3, 4, 6, or 8 bytes |
| REAL | `REAL`, `DOUBLE`, `FLOAT` | 8-byte IEEE float |
| BLOB | `BLOB`, no type specified | Exact byte-for-byte |

**Best Practice:** Always declare explicit types and validate on insert — SQLite will NOT reject a string in an INTEGER column.

---

## 2. Query Optimization

### 2.1 Parameterized Queries

```python
# ❌ BAD — SQL injection risk + no query cache
cursor.execute(f"SELECT * FROM Product WHERE SKU = '{user_input}'")

# ✅ GOOD — parameterized
cursor.execute("SELECT * FROM Product WHERE SKU = ?", (user_input,))

# ✅ Named parameters (preferred for >5 params)
cursor.execute("""
    INSERT INTO SalesOrder
        (OrderNumber, StoreId, CustomerId, EmployeeId,
         SubTotal, TaxAmount, GrandTotal, Status)
    VALUES
        (:order_num, :store_id, :customer_id, :emp_id,
         :subtotal, :tax, :grand_total, :status)
""", {
    "order_num": "SO-2026-0001",
    "store_id": 1,
    "customer_id": 42,
    "emp_id": 7,
    "subtotal": 100.00,
    "tax": 14.00,
    "grand_total": 114.00,
    "status": "Draft"
})
```

**Performance Benefit:** SQLite caches query plans for parameterized queries. Repeated execution skips the parsing/planning step.

### 2.2 EXPLAIN QUERY PLAN

```sql
EXPLAIN QUERY PLAN
SELECT p.Name, p.SKU, i.Quantity
FROM Product p
JOIN Inventory i ON i.ProductId = p.ProductId
WHERE p.CategoryId = 5;
```

**Output Interpretation:**

```
id  parent  notused  detail
--  ------  -------  ------
3   0       0        SEARCH TABLE Product USING INDEX idx_product_category (CategoryId=?)
5   0       0        SEARCH TABLE Inventory USING INDEX idx_inventory_product (ProductId=?)
```

**Red Flags to Watch For:**

| EXPLAIN Output Sign | Problem | Fix |
|---------------------|---------|-----|
| `SCAN TABLE` (no index) | Full table scan | Add appropriate index |
| `USING TEMP B-TREE FOR ORDER BY` | Sorting not indexed | Composite index with sort column |
| `USING TEMP B-TREE FOR GROUP BY` | Grouping not indexed | Covering index for group columns |
| `SCAN TABLE * (size ~N)` | Sequential scan of large table | Index + WHERE clause |
| `OPEN LEFT` (correlated subquery) | Potential N+1 | Rewrite as JOIN |

**Real ERP Example — Detecting a Missing Index:**

```sql
-- Slow query (takes 2.3s on 500K orders)
EXPLAIN QUERY PLAN
SELECT * FROM SalesOrder WHERE OrderDate >= '2026-01-01';

-- Result: SCAN TABLE SalesOrder (~500000 rows)
-- Fix:
CREATE INDEX idx_salesorder_orderdate ON SalesOrder(OrderDate);

-- After: SEARCH TABLE SalesOrder USING INDEX idx_salesorder_orderdate (OrderDate>?)
-- Query now takes 0.03s
```

### 2.3 Index Usage Best Practices

```sql
-- Single-column indexes for foreign keys
CREATE INDEX idx_product_category ON Product(CategoryId);
CREATE INDEX idx_product_brand ON Product(BrandId);
CREATE INDEX idx_inventory_warehouse ON Inventory(WarehouseId);
CREATE INDEX idx_stockmovement_product ON StockMovement(ProductId);

-- Composite indexes for common query patterns
CREATE INDEX idx_salesorder_store_date ON SalesOrder(StoreId, OrderDate DESC);
CREATE INDEX idx_salesorder_customer ON SalesOrder(CustomerId, OrderDate DESC);
CREATE INDEX idx_stockmovement_ref ON StockMovement(ReferenceType, ReferenceId);

-- Partial indexes for filtered queries
CREATE INDEX idx_active_products ON Product(ProductId) WHERE IsActive = 1;
CREATE INDEX idx_pending_orders ON SalesOrder(SalesOrderId) WHERE Status = 'Pending';

-- Covering indexes (all columns needed by query are in the index)
CREATE INDEX idx_product_listing ON Product(CategoryId, SKU, Name, SellingPrice);
```

---

## 3. Schema Design

### 3.1 Normalization (3NF)

This ERP schema follows Third Normal Form (3NF):

1. **1NF:** All columns are atomic (no repeating groups, each cell has one value)
2. **2NF:** All non-key columns depend on the full primary key (surrogate keys ensure this)
3. **3NF:** No transitive dependencies (e.g., `Product.CategoryName` would violate 3NF — we store `CategoryId` and join)

**Normalization Example — Product:**

```
Product (ProductId, ..., CategoryId, BrandId, SupplierId, TaxId)
├── Category (CategoryId, Name, ...)
├── Brand (BrandId, Name, ...)
├── Supplier (SupplierId, CompanyName, ...)
└── Tax (TaxId, Rate, ...)
```

### 3.2 Denormalization for Reporting

Strategic denormalizations in this schema:

| Table | Denormalized Field | Reason |
|-------|-------------------|--------|
| `SalesOrder` | `SubTotal`, `TaxAmount`, `DiscountAmount`, `GrandTotal` | Avoid recomputing on every read |
| `SalesOrderItem` | `LineTotal` | Same — computed once at insert time |
| `PurchaseOrder` | `SubTotal`, `TaxAmount`, `GrandTotal` | Same |
| `Inventory` | `AvailableQuantity`, `ReservedQuantity` | Avoid costly aggregations at read time |
| `RepairOrder` | `DiagnosisFee`, `LaborFee`, `PartsCost`, `GrandTotal` | Stored computed totals |

**When to Denormalize:**

- When the computed value changes infrequently (e.g., once per order)
- When read volume vastly exceeds write volume
- When the computation requires joining 3+ tables
- When real-time aggregation would degrade user experience

**Risk:** Denormalized data can become stale. Mitigate by:
- Recomputing on every UPDATE to the source data
- Using triggers to keep denormalized fields in sync
- Periodically running validation queries (e.g., `SELECT * FROM SalesOrder WHERE GrandTotal != computed_grand_total`)

### 3.3 Data Types Decision Matrix

| Domain | SQLite Type | Stored Format | Example |
|--------|-------------|---------------|---------|
| Monetary amounts | `REAL` | `100.50` | `CostPrice`, `SellingPrice` |
| Quantities | `INTEGER` | `42` | `Quantity`, `WarrantyDays` |
| Percentages | `REAL` | `0.14` (14%) | `TaxPercent`, `DiscountPercent` |
| Dates | `TEXT` (ISO 8601) | `'2026-06-24'` | `OrderDate`, `CreatedAt` |
| Timestamps | `TEXT` (ISO 8601) | `'2026-06-24T14:30:00Z'` | `UpdatedAt` |
| Booleans | `INTEGER` | `0` or `1` | `IsActive`, `IsDeleted` |
| JSON | `TEXT` | `'{"key":"val"}'` | `Diagnosis`, `Items` |
| UUIDs | `TEXT` | `'550e8400-e29b-41d4-a716-446655440000'` | `ProductUid` |
| Phone numbers | `TEXT` | `'+201234567890'` | `Phone` |
| Serial numbers | `TEXT` | `'SN-2026-A00001'` | `SerialNumber` |

---

## 4. Transaction Management

### 4.1 Implicit vs. Explicit Transactions

**Implicit (dangerous for ERP):**

```python
# Each cursor.execute() is its own transaction — BAD for multi-step operations
cursor.execute("UPDATE Inventory SET Quantity = Quantity - 1 WHERE ProductId = ?", (pid,))
# If the next line crashes, inventory is inconsistent
cursor.execute("INSERT INTO StockMovement (...) VALUES (...)")
```

**Explicit (correct approach):**

```python
try:
    conn.execute("BEGIN TRANSACTION")
    cursor.execute("UPDATE Inventory SET Quantity = Quantity - 1 WHERE ProductId = ?", (pid,))
    cursor.execute("INSERT INTO StockMovement (...) VALUES (...)", (...))
    cursor.execute("UPDATE SalesOrderItem SET SerialNumberId = ? WHERE ...", (sn_id,))
    conn.commit()
except Exception:
    conn.rollback()
    raise
```

### 4.2 Savepoints (Nested Transactions)

Savepoints allow partial rollback within a larger transaction.

```python
conn.execute("BEGIN TRANSACTION")
try:
    # Batch processing 100 orders
    for order in orders:
        savepoint = f"sp_{order['id']}"
        conn.execute(f"SAVEPOINT {savepoint}")
        try:
            process_order(conn, order)
            conn.execute(f"RELEASE SAVEPOINT {savepoint}")
        except Exception:
            conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
            log_error(f"Order {order['id']} failed, continuing batch")
            continue
    conn.commit()
except Exception:
    conn.rollback()
```

**Use Case:** Bulk import of 1000 purchase orders — if order #42 has a bad SKU, roll back just that one and proceed.

### 4.3 Transaction Isolation Levels

SQLite only supports **SERIALIZABLE** isolation (the strictest). This means:

- `BEGIN IMMEDIATE` — Acquires a write lock immediately. Use when you know you'll write.
- `BEGIN EXCLUSIVE` — Acquires exclusive access. Use during batch updates.
- `BEGIN DEFERRED` (default) — Acquires read lock, upgrades to write on first write. Risk: deadlock under high concurrency.

```python
# For any write-heavy operation:
conn.execute("BEGIN IMMEDIATE TRANSACTION")
```

### 4.4 Transaction Boundaries for ERP Operations

| Operation | Transaction Scope | Rollback Risk |
|-----------|-------------------|---------------|
| Create SalesOrder | Order header + items + inventory deduction | High — partial inventory deduction |
| Record StockCount | Count items + adjustment movements | Medium — inconsistent stock |
| Create PurchaseOrder | Order header + items (no inventory yet) | Low |
| Receive PurchaseOrder | Update items + inventory + movements | High — partial receipt |
| Create RepairOrder | Order + initial diagnosis | Low |
| Complete Repair | Parts usage + labor + inventory deduction | High |

---

## 5. Migration Strategy

### 5.1 Schema Versioning

Maintain a `SchemaVersion` table:

```sql
CREATE TABLE SchemaVersion (
    VersionId    INTEGER PRIMARY KEY AUTOINCREMENT,
    Version      TEXT NOT NULL UNIQUE,       -- e.g., '1.0.23'
    Description  TEXT,
    ScriptName   TEXT,                        -- 'migrations/v1.0.23.sql'
    Checksum     TEXT,                        -- SHA256 of migration file
    AppliedBy    TEXT,                        -- Employee username
    AppliedAt    TEXT DEFAULT (datetime('now'))
);
```

### 5.2 Incremental Migration Pattern

Directory structure:
```
migrations/
├── v1.0.0_initial.sql
├── v1.0.1_add_product_warranty.sql
├── v1.0.2_add_repair_tables.sql
├── v1.0.3_add_indexes.sql
├── v1.0.4_add_audit_log.sql
└── v1.0.5_add_financial_records.sql
```

**Migration Runner Logic:**

```python
def run_migrations(conn, migrations_dir="migrations"):
    conn.row_factory = sqlite3.Row
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='SchemaVersion'")
    if not cur.fetchone():
        conn.executescript("""
            CREATE TABLE SchemaVersion (
                VersionId INTEGER PRIMARY KEY AUTOINCREMENT,
                Version TEXT NOT NULL UNIQUE,
                Description TEXT,
                ScriptName TEXT,
                Checksum TEXT,
                AppliedBy TEXT,
                AppliedAt TEXT DEFAULT (datetime('now'))
            );
        """)

    applied = set(r["Version"] for r in conn.execute("SELECT Version FROM SchemaVersion").fetchall())

    for file in sorted(os.listdir(migrations_dir)):
        version = extract_version_from_filename(file)
        if version in applied:
            continue

        script_path = os.path.join(migrations_dir, file)
        with open(script_path, "r", encoding="utf-8") as f:
            script = f.read()

        checksum = hashlib.sha256(script.encode()).hexdigest()

        try:
            conn.execute("BEGIN IMMEDIATE TRANSACTION")
            conn.executescript(script)
            conn.execute("""
                INSERT INTO SchemaVersion (Version, Description, ScriptName, Checksum, AppliedBy)
                VALUES (?, ?, ?, ?, ?)
            """, (version, extract_description(file), file, checksum, get_current_user()))
            conn.commit()
            print(f"Applied migration: {file}")
        except Exception as e:
            conn.rollback()
            print(f"FAILED migration: {file} — {e}")
            raise
```

### 5.3 Migration Design Principles

1. **Idempotent when possible:** Use `CREATE IF NOT EXISTS`, `DROP IF EXISTS`
2. **Never modify a migration after it's been applied** — create a new one
3. **One logical change per migration file**
4. **Include both schema and data migrations** (e.g., backfill new columns)
5. **Test rollback scripts** for critical migrations
6. **Lock the database before running migrations** in production

### 5.4 Complex Migration Example — Adding a Non-Null Column

```sql
-- Step 1: Add nullable
ALTER TABLE Product ADD COLUMN Barcode TEXT;

-- Step 2: Backfill existing rows (in batches for large tables)
UPDATE Product SET Barcode = 'BC-' || CAST(ProductId AS TEXT) WHERE Barcode IS NULL;

-- Step 3: Make NOT NULL + add unique index
CREATE UNIQUE INDEX idx_product_barcode ON Product(Barcode) WHERE Barcode IS NOT NULL;

-- Step 4 (PostgreSQL path): ALTER TABLE Product ALTER COLUMN Barcode SET NOT NULL;
-- SQLite does not support ALTER COLUMN — requires CREATE TABLE AS
```

---

## 6. Backup Strategies

### 6.1 .backup Command (Online Backup)

```bash
# Using sqlite3 CLI (safe while app is running)
sqlite3 "file:erp.db?mode=ro" ".backup 'C:\backups\erp_20260624.db'"
```

**Python equivalent:**

```python
def backup_database(src_path, dst_path):
    src = sqlite3.connect(src_path)
    dst = sqlite3.connect(dst_path)
    with dst:
        src.backup(dst, pages=1000)  # 1000 pages per iteration
    src.close()
    dst.close()
```

### 6.2 VACUUM INTO (SQLite 3.27+)

Creates a compacted copy (vacuum + backup in one step):

```sql
VACUUM INTO 'C:\backups\erp_compacted.db';
```

**Advantages:** Defragments the database while backing up. Produces a smaller file.

### 6.3 File Copy (Cold Backup)

```bash
# Only safe if application is stopped or in WAL mode
copy "C:\data\erp.db" "C:\backups\erp_cold.db"
copy "C:\data\erp-wal" "C:\backups\erp-wal"  # Must also copy WAL + SHM
copy "C:\data\erp-shm" "C:\backups\erp-shm"
```

**WARNING:** In WAL mode, you must copy all three files (`erp.db`, `erp-wal`, `erp-shm`). Missing any file corrupts the backup.

### 6.4 Backup Strategy Matrix

| Strategy | Online? | Speed | Integrity | Best For |
|----------|---------|-------|-----------|----------|
| `.backup` | Yes | Medium | High — consistent snapshot | Hourly/daily live backups |
| `VACUUM INTO` | Yes | Slow | High + compacted | Weekly full backup |
| File copy (cold) | No | Fast | Guaranteed | Maintenance window |
| SQL dump | Yes | Very slow | High | Cross-version migration |
| WAL checkpoint + copy | Yes | Fast | Medium | Quick snapshot |

### 6.5 Backup Schedule Recommendation

```
Hourly:     .backup to local disk
Daily:      VACUUM INTO to network share
Weekly:     File copy to cloud storage + WAL checkpoint
Monthly:    SQL dump for cross-version portability
```

---

## 7. Performance Monitoring

### 7.1 Query Timing Decorator

```python
import time
import logging
import sqlite3

logger = logging.getLogger("db.performance")

def timed_query(conn, sql, params=None, threshold=0.1):
    start = time.perf_counter()
    cur = conn.execute(sql, params or [])
    elapsed = time.perf_counter() - start
    if elapsed > threshold:
        logger.warning(f"SLOW QUERY ({elapsed:.3f}s): {sql[:200]} | params={params}")
    return cur
```

### 7.2 Connection Monitoring

```python
class MonitoredConnection:
    def __init__(self, conn, name="default"):
        self._conn = conn
        self._name = name
        self._query_count = 0
        self._total_time = 0.0
        self._start_time = time.time()

    def execute(self, sql, params=None):
        start = time.perf_counter()
        result = self._conn.execute(sql, params or [])
        elapsed = time.perf_counter() - start
        self._query_count += 1
        self._total_time += elapsed
        return result

    def report(self):
        uptime = time.time() - self._start_time
        return {
            "name": self._name,
            "uptime_seconds": uptime,
            "query_count": self._query_count,
            "total_time": f"{self._total_time:.3f}s",
            "avg_time": f"{self._total_time / max(self._query_count, 1) * 1000:.1f}ms",
            "qps": f"{self._query_count / max(uptime, 1):.1f}"
        }
```

### 7.3 SQLite Built-in Monitoring

```sql
-- Query plan cache stats
PRAGMA stats;

-- Database page count and page size
SELECT page_count, page_size, page_count * page_size AS total_bytes
FROM pragma_page_count, pragma_page_size;

-- Schema size (approximate)
SELECT
    name AS table_name,
    pageno AS pages,
    pageno * 4096 AS bytes
FROM pragma_page_count
JOIN sqlite_master ON sqlite_master.name = pragma_page_count.name;

-- WAL file size
PRAGMA wal_checkpoint;
```

### 7.4 Slow Query Log Thresholds

| Query Type | Warning Threshold | Critical Threshold |
|------------|-------------------|--------------------|
| Simple lookup (PK) | >50ms | >200ms |
| JOIN (2–3 tables) | >200ms | >500ms |
| Report query (5+ tables) | >1s | >3s |
| Bulk insert (100 rows) | >500ms | >2s |
| Migration script | >5s | >30s |

---

## 8. Common Anti-Patterns

### 8.1 N+1 Query Problem

**The Anti-Pattern:**

```python
# N+1: 1 query for orders + N queries for items
orders = conn.execute("SELECT * FROM SalesOrder WHERE Status = 'Pending'").fetchall()
for order in orders:  # If 100 orders, this runs 100 more queries!
    items = conn.execute("SELECT * FROM SalesOrderItem WHERE SalesOrderId = ?",
                         (order["SalesOrderId"],)).fetchall()
```

**Total:** 1 + 100 = 101 queries

**The Fix:**

```python
# Single JOIN query
rows = conn.execute("""
    SELECT so.*, soi.*
    FROM SalesOrder so
    JOIN SalesOrderItem soi ON soi.SalesOrderId = so.SalesOrderId
    WHERE so.Status = 'Pending'
    ORDER BY so.SalesOrderId
""").fetchall()
```

**Total:** 1 query

**When N+1 Is Acceptable:** If the "N" is small (N <= 5) and the child table is very large, two separate queries may be faster than a JOIN on an unindexed FK.

### 8.2 Missing Indexes

**Symptoms:**
- Queries that were fast become slow as data grows
- `EXPLAIN QUERY PLAN` shows `SCAN TABLE`
- High disk I/O on simple lookups

**Detection Query:**

```sql
-- Find missing indexes (heuristic — queries that do table scans)
SELECT
    m.name AS table_name,
    p.count AS row_count
FROM sqlite_master m
JOIN (
    SELECT COUNT(*) AS count, 'Product' AS name FROM Product
    UNION ALL SELECT COUNT(*), 'SalesOrder' FROM SalesOrder
    UNION ALL SELECT COUNT(*), 'Inventory' FROM Inventory
    -- ... all tables
) p ON p.name = m.name
WHERE m.type = 'table'
ORDER BY p.count DESC;
```

### 8.3 Over-Indexing

**The Anti-Pattern:**

```sql
-- Too many indexes on the same table
CREATE INDEX idx_salesorder_status ON SalesOrder(Status);
CREATE INDEX idx_salesorder_status_date ON SalesOrder(Status, OrderDate);
CREATE INDEX idx_salesorder_date_status ON SalesOrder(OrderDate, Status);
CREATE INDEX idx_salesorder_store_status ON SalesOrder(StoreId, Status);
CREATE INDEX idx_salesorder_status_store ON SalesOrder(Status, StoreId);
```

**Problems:**
- Every INSERT/UPDATE/DELETE must update all indexes (write slowdown)
- Increased disk usage (indexes can be larger than the table)
- Query planner may choose a suboptimal index

**Fix:** Analyze actual query patterns and keep only the most useful indexes. Drop indexes that are prefixes of composite indexes.

### 8.4 Using SELECT * in Production

```python
# ❌ BAD: Retrieves all columns
rows = conn.execute("SELECT * FROM Product WHERE CategoryId = ?", (cat_id,)).fetchall()

# ✅ GOOD: Only needed columns
rows = conn.execute("SELECT ProductId, SKU, Name, SellingPrice FROM Product WHERE CategoryId = ?",
                    (cat_id,)).fetchall()
```

**Impact:** `SELECT *` on a 50-column table with 100K rows transfers ~50MB unnecessarily. It also breaks if columns are added later.

### 8.5 Implicit Type Conversion

```sql
-- ❌ BAD: String compared to integer
SELECT * FROM Product WHERE ProductId = '42';  -- SQLite converts both to TEXT

-- ✅ GOOD: Proper type
SELECT * FROM Product WHERE ProductId = 42;
```

The implicit conversion prevents index usage and can produce incorrect results.

### 8.6 Not Using VACUUM

SQLite does not reclaim disk space when data is deleted. Over time, the database file grows with empty pages.

**Anti-Pattern:** Deleting 1M old stock movements but never running VACUUM → database remains at 2GB when actual data is 500MB.

**Fix:** Schedule `PRAGMA incremental_vacuum(N)` or `VACUUM` during maintenance windows.

### 8.7 Anti-Pattern Quick Reference

| Anti-Pattern | Symptom | Solution |
|-------------|---------|----------|
| N+1 queries | Page loads slowly, many small queries | Use JOIN or batch loading |
| Missing indexes | Table scans on large tables | Add indexes on WHERE/JOIN columns |
| Over-indexing | Slow writes, large file size | Analyze usage, remove unused indexes |
| `SELECT *` | Excessive data transfer | Specify columns explicitly |
| Implicit type conv. | Index not used, wrong results | Cast to correct type |
| No VACUUM | File size grows unbounded | Schedule periodic VACUUM |
| Autocommit mode | Partial updates on crash | Use explicit transactions |
| String date comparison | Cannot use date functions | Store dates as ISO 8601 TEXT |
| Unclosed connections | SQLITE_BUSY errors | Use context managers |

---

## 9. Security

### 9.1 Parameterized Queries (Mandatory)

```python
# ❌ NEVER DO THIS
cursor.execute(f"SELECT * FROM Employee WHERE Email = '{email}'")

# ✅ ALWAYS DO THIS
cursor.execute("SELECT * FROM Employee WHERE Email = ?", (email,))
```

**Why:** SQL injection is the #1 vulnerability in database applications. Parameterized queries ensure user input is treated as data, not executable SQL.

### 9.2 Input Validation

```python
def validate_and_insert_product(conn, data):
    # Type validation
    if not isinstance(data.get("CostPrice"), (int, float)):
        raise ValueError("CostPrice must be numeric")
    if data["CostPrice"] < 0:
        raise ValueError("CostPrice cannot be negative")

    # Length validation
    if len(data.get("SKU", "")) > 50:
        raise ValueError("SKU exceeds maximum length of 50")

    # Enum validation (whitelist approach)
    valid_uom = {"piece", "kg", "meter", "box", "liter"}
    if data.get("UnitOfMeasure") not in valid_uom:
        raise ValueError(f"UnitOfMeasure must be one of: {valid_uom}")

    # Execute with parameterized query
    conn.execute("""
        INSERT INTO Product (SKU, Name, CostPrice, SellingPrice, UnitOfMeasure, CategoryId)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data["SKU"], data["Name"], data["CostPrice"],
          data["SellingPrice"], data["UnitOfMeasure"], data["CategoryId"]))
```

### 9.3 Least Privilege Principle

```sql
-- Separate databases or schemas for different access levels
-- (SQLite: use file-level permissions + application-level authorization)

-- Read-only role — only SELECT
CREATE VIEW vw_report_sales AS
SELECT ... FROM SalesOrder WHERE Status = 'Completed';

-- Application enforces:
-- - Cashiers: INSERT/UPDATE SalesOrder, SELECT Product, SELECT Inventory
-- - Warehouse: INSERT/UPDATE StockMovement, UPDATE Inventory
-- - Managers: SELECT all reports
-- - Admins: Full DDL access
```

**Implementation in Application Code:**

```python
class PermissionChecker:
    PERMISSIONS = {
        "sales:create": ["SalesManager", "Cashier"],
        "inventory:adjust": ["WarehouseManager", "Admin"],
        "reports:view": ["SalesManager", "WarehouseManager", "Accountant", "Admin"],
        "users:manage": ["Admin"],
    }

    def check(self, employee_roles, permission_code):
        allowed_roles = self.PERMISSIONS.get(permission_code, [])
        return any(role in allowed_roles for role in employee_roles)
```

### 9.4 Encryption at Rest

SQLite does not natively support encryption. Options:

1. **SQLite Encryption Extension (SEE)** — commercial, transparent encryption
2. **sqlcipher** — open-source, encrypts page-by-page
3. **Application-level encryption** — encrypt sensitive fields before storage

```python
import hashlib
from cryptography.fernet import Fernet

# Application-level field encryption
key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_sensitive(value: str) -> bytes:
    return cipher.encrypt(value.encode())

def decrypt_sensitive(value: bytes) -> str:
    return cipher.decrypt(value).decode()

# Usage: encrypt before INSERT, decrypt after SELECT
conn.execute("UPDATE Employee SET PasswordHash = ? WHERE EmployeeId = ?",
             (encrypt_sensitive(password_hash), emp_id))
```

### 9.5 Audit Logging

```sql
CREATE TABLE AuditLog (
    LogId      INTEGER PRIMARY KEY AUTOINCREMENT,
    TableName  TEXT NOT NULL,
    RecordId   INTEGER NOT NULL,
    Action     TEXT NOT NULL CHECK (Action IN ('INSERT','UPDATE','DELETE')),
    EmployeeId INTEGER NOT NULL,
    OldValues  TEXT,           -- JSON of old values (for UPDATE/DELETE)
    NewValues  TEXT,           -- JSON of new values (for INSERT/UPDATE)
    IpAddress  TEXT,
    UserAgent  TEXT,
    CreatedAt  TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_audit_table_record ON AuditLog(TableName, RecordId);
CREATE INDEX idx_audit_employee ON AuditLog(EmployeeId);
CREATE INDEX idx_audit_action ON AuditLog(Action);
```

**Trigger-Based Audit (for critical tables):**

```sql
CREATE TRIGGER trg_audit_product_update
AFTER UPDATE ON Product
BEGIN
    INSERT INTO AuditLog (TableName, RecordId, Action, EmployeeId, OldValues, NewValues)
    VALUES (
        'Product',
        NEW.ProductId,
        'UPDATE',
        -- EmployeeId must be set via application context (e.g. PRAGMA or temp table)
        COALESCE((SELECT Value FROM AppContext WHERE Key = 'CurrentEmployeeId'), 0),
        json_object(
            'Name', OLD.Name, 'SKU', OLD.SKU,
            'CostPrice', OLD.CostPrice, 'SellingPrice', OLD.SellingPrice,
            'IsActive', OLD.IsActive
        ),
        json_object(
            'Name', NEW.Name, 'SKU', NEW.SKU,
            'CostPrice', NEW.CostPrice, 'SellingPrice', NEW.SellingPrice,
            'IsActive', NEW.IsActive
        )
    );
END;
```

### 9.6 Security Checklist

- [ ] All queries use parameterized inputs (no string interpolation)
- [ ] Passwords hashed with bcrypt (not stored as plain text or MD5)
- [ ] JSON fields validated against schema before storage
- [ ] Foreign keys enforced (`PRAGMA foreign_keys = ON`)
- [ ] Database file permissions restrict OS-level access (e.g., `chmod 600`)
- [ ] Backup files encrypted
- [ ] Audit log captures all destructive operations
- [ ] Input length/size limits enforced at application layer
- [ ] Timeout for idle connections
- [ ] Rate limiting on login endpoints (Prev)

---

## 10. Appendix

### 10.1 Python SQLite Utility Module (Template)

```python
"""erp_db.py — ERP Database Utility"""
import sqlite3
import threading
import time
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class ERPDatabase:
    def __init__(self, db_path: str, pool_size: int = 5):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._pool = [self._create_connection() for _ in range(pool_size)]

    def _create_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 5000")
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.execute("PRAGMA cache_size = -64000")
        conn.execute("PRAGMA mmap_size = 268435456")
        return conn

    @contextmanager
    def get_conn(self, write: bool = False):
        if write:
            with self._lock:
                conn = self._create_connection()
                try:
                    conn.execute("BEGIN IMMEDIATE")
                    yield conn
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise
                finally:
                    conn.close()
        else:
            conn = self._pool.pop()
            try:
                yield conn
            finally:
                self._pool.append(conn)

    def execute(self, sql: str, params=None, write: bool = False):
        with self.get_conn(write=write) as conn:
            return conn.execute(sql, params or [])

    def fetchone(self, sql: str, params=None):
        with self.get_conn(write=False) as conn:
            return conn.execute(sql, params or []).fetchone()

    def fetchall(self, sql: str, params=None):
        with self.get_conn(write=False) as conn:
            return conn.execute(sql, params or []).fetchall()
```

### 10.2 Useful SQLite CLI Commands

```bash
# Open database
sqlite3 erp.db

# Show all tables
.tables

# Show schema for a table
.schema Product

# Show indexes
.indices Product

# Analyze query
EXPLAIN QUERY PLAN SELECT ...;

# Enable headers and column mode for readable output
.headers on
.mode column

# Import CSV
.import --csv data.csv TempTable

# Export to CSV
.headers on
.mode csv
.output products.csv
SELECT * FROM Product;
.output stdout

# Timing
.timer on

# Database info
.dbinfo
```

### 10.3 Recommended Reading

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQLite Query Planning](https://www.sqlite.org/optoverview.html)
- [SQLite WAL Mode](https://www.sqlite.org/wal.html)
- [Use The Index, Luke](https://use-the-index-luke.com/) — SQL indexing guide
- [High Performance SQLite](https://stackoverflow.com/questions/784173) — StackOverflow compilation
