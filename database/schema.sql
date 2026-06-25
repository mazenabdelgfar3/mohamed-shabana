-- =============================================================================
-- COMPUTER STORE ERP - PRODUCTION SQLite SCHEMA
-- =============================================================================
-- Target: SQLite 3.x
-- Design: 28 tables, 22 indexes, INTEGER PK, StockMovement-driven
-- =============================================================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
PRAGMA cache_size = -8000;
PRAGMA synchronous = NORMAL;
PRAGMA temp_store = MEMORY;
PRAGMA busy_timeout = 3000;

-- =============================================================================
-- 1. STORE
-- =============================================================================
CREATE TABLE IF NOT EXISTS Store (
    StoreId     INTEGER PRIMARY KEY AUTOINCREMENT,
    StoreUid    TEXT    NOT NULL UNIQUE,
    Code        TEXT    NOT NULL UNIQUE,
    Name        TEXT    NOT NULL,
    Phone       TEXT,
    Email       TEXT,
    Address     TEXT,
    TaxNumber   TEXT,
    IsActive    INTEGER NOT NULL DEFAULT 1,
    CreatedAt   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UpdatedAt   TEXT,
    IsDeleted   INTEGER NOT NULL DEFAULT 0
);

-- =============================================================================
-- 2. EMPLOYEE
-- =============================================================================
CREATE TABLE IF NOT EXISTS Employee (
    EmployeeId      INTEGER PRIMARY KEY AUTOINCREMENT,
    EmployeeUid     TEXT    NOT NULL UNIQUE,
    StoreId         INTEGER NOT NULL REFERENCES Store(StoreId) ON DELETE RESTRICT ON UPDATE CASCADE,
    EmployeeCode    TEXT    NOT NULL UNIQUE,
    FullName        TEXT    NOT NULL,
    Phone           TEXT,
    Email           TEXT    UNIQUE,
    PasswordHash    TEXT    NOT NULL,
    LastLoginAt     TEXT,
    IsActive        INTEGER NOT NULL DEFAULT 1,
    CreatedAt       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UpdatedAt       TEXT,
    IsDeleted       INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS IX_Employee_StoreId ON Employee(StoreId);

-- =============================================================================
-- 3. ROLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS Role (
    RoleId      INTEGER PRIMARY KEY AUTOINCREMENT,
    RoleName    TEXT    NOT NULL UNIQUE,
    Permissions TEXT,
    IsActive    INTEGER NOT NULL DEFAULT 1
);

-- =============================================================================
-- 4. EMPLOYEE_ROLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS EmployeeRole (
    EmployeeRoleId  INTEGER PRIMARY KEY AUTOINCREMENT,
    EmployeeId      INTEGER NOT NULL REFERENCES Employee(EmployeeId) ON DELETE CASCADE ON UPDATE CASCADE,
    RoleId          INTEGER NOT NULL REFERENCES Role(RoleId) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE(EmployeeId, RoleId)
);

CREATE INDEX IF NOT EXISTS IX_EmployeeRole_EmployeeId ON EmployeeRole(EmployeeId);

-- =============================================================================
-- 5. CUSTOMER
-- =============================================================================
CREATE TABLE IF NOT EXISTS Customer (
    CustomerId      INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerUid     TEXT    NOT NULL UNIQUE,
    CustomerCode    TEXT    NOT NULL UNIQUE,
    FullName        TEXT    NOT NULL,
    Phone           TEXT,
    Email           TEXT,
    TaxNumber       TEXT,
    CreditLimit     INTEGER NOT NULL DEFAULT 0,
    Notes           TEXT,
    IsActive        INTEGER NOT NULL DEFAULT 1,
    CreatedAt       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UpdatedAt       TEXT,
    IsDeleted       INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS IX_Customer_FullName ON Customer(FullName);

-- =============================================================================
-- 6. SUPPLIER
-- =============================================================================
CREATE TABLE IF NOT EXISTS Supplier (
    SupplierId      INTEGER PRIMARY KEY AUTOINCREMENT,
    SupplierUid     TEXT    NOT NULL UNIQUE,
    SupplierCode    TEXT    NOT NULL UNIQUE,
    CompanyName     TEXT    NOT NULL,
    ContactPerson   TEXT,
    Phone           TEXT,
    Email           TEXT,
    TaxNumber       TEXT,
    PaymentTerms    TEXT,
    Notes           TEXT,
    IsActive        INTEGER NOT NULL DEFAULT 1,
    CreatedAt       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UpdatedAt       TEXT,
    IsDeleted       INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS IX_Supplier_CompanyName ON Supplier(CompanyName);

-- =============================================================================
-- 7. CATEGORY
-- =============================================================================
CREATE TABLE IF NOT EXISTS Category (
    CategoryId          INTEGER PRIMARY KEY AUTOINCREMENT,
    ParentCategoryId    INTEGER REFERENCES Category(CategoryId) ON DELETE SET NULL ON UPDATE CASCADE,
    Code                TEXT    NOT NULL UNIQUE,
    Name                TEXT    NOT NULL,
    Description         TEXT,
    IsActive            INTEGER NOT NULL DEFAULT 1,
    CreatedAt           TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UpdatedAt           TEXT,
    IsDeleted           INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS IX_Category_ParentCategoryId ON Category(ParentCategoryId);

-- =============================================================================
-- 8. BRAND
-- =============================================================================
CREATE TABLE IF NOT EXISTS Brand (
    BrandId     INTEGER PRIMARY KEY AUTOINCREMENT,
    Code        TEXT    NOT NULL UNIQUE,
    Name        TEXT    NOT NULL,
    IsActive    INTEGER NOT NULL DEFAULT 1,
    CreatedAt   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UpdatedAt   TEXT,
    IsDeleted   INTEGER NOT NULL DEFAULT 0
);

-- =============================================================================
-- 9. TAX
-- =============================================================================
CREATE TABLE IF NOT EXISTS Tax (
    TaxId      INTEGER PRIMARY KEY AUTOINCREMENT,
    Code       TEXT    NOT NULL UNIQUE,
    Name       TEXT    NOT NULL,
    Rate       REAL    NOT NULL CHECK (Rate >= 0),
    IsActive   INTEGER NOT NULL DEFAULT 1
);

-- =============================================================================
-- 10. PRODUCT
-- =============================================================================
CREATE TABLE IF NOT EXISTS Product (
    ProductId       INTEGER PRIMARY KEY AUTOINCREMENT,
    ProductUid      TEXT    NOT NULL UNIQUE,
    CategoryId      INTEGER REFERENCES Category(CategoryId) ON DELETE SET NULL ON UPDATE CASCADE,
    BrandId         INTEGER REFERENCES Brand(BrandId) ON DELETE SET NULL ON UPDATE CASCADE,
    SupplierId      INTEGER REFERENCES Supplier(SupplierId) ON DELETE SET NULL ON UPDATE CASCADE,
    TaxId           INTEGER REFERENCES Tax(TaxId) ON DELETE SET NULL ON UPDATE CASCADE,
    SKU             TEXT    NOT NULL UNIQUE,
    Name            TEXT    NOT NULL,
    Description     TEXT,
    UnitOfMeasure   TEXT    NOT NULL DEFAULT 'Piece',
    Barcode         TEXT    UNIQUE,
    BarcodesAlt     TEXT,
    CostPrice       INTEGER NOT NULL CHECK (CostPrice >= 0),
    SellingPrice    INTEGER NOT NULL CHECK (SellingPrice > 0),
    SupplierPrice   INTEGER,
    MinStockLevel   INTEGER NOT NULL DEFAULT 0,
    MaxStockLevel   INTEGER NOT NULL DEFAULT 0,
    WarrantyDays    INTEGER NOT NULL DEFAULT 0,
    HasSerialNumbers INTEGER NOT NULL DEFAULT 0,
    IsActive        INTEGER NOT NULL DEFAULT 1,
    ImagePath       TEXT,
    CreatedAt       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UpdatedAt       TEXT,
    IsDeleted       INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS IX_Product_CategoryId ON Product(CategoryId);
CREATE INDEX IF NOT EXISTS IX_Product_BrandId ON Product(BrandId);
CREATE INDEX IF NOT EXISTS IX_Product_SupplierId ON Product(SupplierId);
CREATE INDEX IF NOT EXISTS IX_Product_Name ON Product(Name);

-- =============================================================================
-- 11. SERIAL_NUMBER
-- =============================================================================
CREATE TABLE IF NOT EXISTS SerialNumber (
    SerialNumberId          INTEGER PRIMARY KEY AUTOINCREMENT,
    ProductId               INTEGER NOT NULL REFERENCES Product(ProductId) ON DELETE RESTRICT ON UPDATE CASCADE,
    SalesOrderItemId        INTEGER REFERENCES SalesOrderItem(SalesOrderItemId) ON DELETE SET NULL ON UPDATE CASCADE,
    PurchaseOrderItemId     INTEGER REFERENCES PurchaseOrderItem(PurchaseOrderItemId) ON DELETE SET NULL ON UPDATE CASCADE,
    SerialNumber            TEXT    NOT NULL UNIQUE,
    CurrentStatus           TEXT    NOT NULL DEFAULT 'IN_STOCK' CHECK (CurrentStatus IN ('IN_STOCK','SOLD','IN_REPAIR','RETURNED','EXPIRED')),
    WarrantyStart           TEXT,
    WarrantyEnd             TEXT,
    WarrantyStatus          TEXT    DEFAULT 'ACTIVE' CHECK (WarrantyStatus IN ('ACTIVE','EXPIRED','CLAIMED','VOID')),
    CreatedAt               TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UpdatedAt               TEXT
);

CREATE INDEX IF NOT EXISTS IX_SerialNumber_ProductId ON SerialNumber(ProductId);
CREATE INDEX IF NOT EXISTS IX_SerialNumber_Status ON SerialNumber(CurrentStatus);

-- =============================================================================
-- 12. SALES_ORDER
-- =============================================================================
CREATE TABLE IF NOT EXISTS SalesOrder (
    SalesOrderId    INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderNumber     TEXT    NOT NULL UNIQUE,
    StoreId         INTEGER NOT NULL REFERENCES Store(StoreId) ON DELETE RESTRICT ON UPDATE CASCADE,
    CustomerId      INTEGER REFERENCES Customer(CustomerId) ON DELETE RESTRICT ON UPDATE CASCADE,
    EmployeeId      INTEGER REFERENCES Employee(EmployeeId) ON DELETE RESTRICT ON UPDATE CASCADE,
    OrderDate       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    DueDate         TEXT,
    SubTotal        INTEGER NOT NULL DEFAULT 0,
    TaxAmount       INTEGER NOT NULL DEFAULT 0,
    DiscountAmount  INTEGER NOT NULL DEFAULT 0,
    GrandTotal      INTEGER NOT NULL DEFAULT 0,
    PaidAmount      INTEGER NOT NULL DEFAULT 0,
    BalanceDue      INTEGER NOT NULL DEFAULT 0,
    PaymentMethod   TEXT,
    PaymentDate     TEXT,
    Status          TEXT    NOT NULL DEFAULT 'DRAFT',
    Notes           TEXT,
    CreatedAt       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UpdatedAt       TEXT,
    CreatedBy       INTEGER REFERENCES Employee(EmployeeId) ON DELETE RESTRICT ON UPDATE CASCADE,
    UpdatedBy       INTEGER REFERENCES Employee(EmployeeId) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS IX_SalesOrder_StoreId_OrderDate ON SalesOrder(StoreId, OrderDate);
CREATE INDEX IF NOT EXISTS IX_SalesOrder_CustomerId ON SalesOrder(CustomerId);
CREATE INDEX IF NOT EXISTS IX_SalesOrder_Status ON SalesOrder(Status);

-- =============================================================================
-- 13. SALES_ORDER_ITEM
-- =============================================================================
CREATE TABLE IF NOT EXISTS SalesOrderItem (
    SalesOrderItemId    INTEGER PRIMARY KEY AUTOINCREMENT,
    SalesOrderId        INTEGER NOT NULL REFERENCES SalesOrder(SalesOrderId) ON DELETE CASCADE ON UPDATE CASCADE,
    ProductId           INTEGER NOT NULL REFERENCES Product(ProductId) ON DELETE RESTRICT ON UPDATE CASCADE,
    SerialNumberId      INTEGER REFERENCES SerialNumber(SerialNumberId) ON DELETE SET NULL ON UPDATE CASCADE,
    Quantity            INTEGER NOT NULL CHECK (Quantity > 0),
    UnitPrice           INTEGER NOT NULL CHECK (UnitPrice > 0),
    DiscountPercent     REAL    NOT NULL DEFAULT 0,
    DiscountAmount      INTEGER NOT NULL DEFAULT 0,
    TaxPercent          REAL    NOT NULL DEFAULT 0,
    TaxAmount           INTEGER NOT NULL DEFAULT 0,
    LineTotal           INTEGER NOT NULL DEFAULT 0,
    WarrantyDays        INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS IX_SalesOrderItem_SalesOrderId ON SalesOrderItem(SalesOrderId);
CREATE INDEX IF NOT EXISTS IX_SalesOrderItem_ProductId ON SalesOrderItem(ProductId);

-- =============================================================================
-- 14. SALES_RETURN
-- =============================================================================
CREATE TABLE IF NOT EXISTS SalesReturn (
    SalesReturnId   INTEGER PRIMARY KEY AUTOINCREMENT,
    ReturnNumber    TEXT    NOT NULL UNIQUE,
    SalesOrderId    INTEGER REFERENCES SalesOrder(SalesOrderId) ON DELETE RESTRICT ON UPDATE CASCADE,
    CustomerId      INTEGER NOT NULL REFERENCES Customer(CustomerId) ON DELETE RESTRICT ON UPDATE CASCADE,
    ReturnDate      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    Reason          TEXT,
    SubTotal        INTEGER NOT NULL DEFAULT 0,
    TaxAmount       INTEGER NOT NULL DEFAULT 0,
    GrandTotal      INTEGER NOT NULL DEFAULT 0,
    Status          TEXT    NOT NULL DEFAULT 'DRAFT',
    CreatedAt       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    CreatedBy       INTEGER REFERENCES Employee(EmployeeId) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS IX_SalesReturn_CustomerId ON SalesReturn(CustomerId);

-- =============================================================================
-- 15. SALES_RETURN_ITEM
-- =============================================================================
CREATE TABLE IF NOT EXISTS SalesReturnItem (
    SalesReturnItemId   INTEGER PRIMARY KEY AUTOINCREMENT,
    SalesReturnId       INTEGER NOT NULL REFERENCES SalesReturn(SalesReturnId) ON DELETE CASCADE ON UPDATE CASCADE,
    SalesOrderItemId    INTEGER REFERENCES SalesOrderItem(SalesOrderItemId) ON DELETE SET NULL ON UPDATE CASCADE,
    ProductId           INTEGER NOT NULL REFERENCES Product(ProductId) ON DELETE RESTRICT ON UPDATE CASCADE,
    Quantity            INTEGER NOT NULL CHECK (Quantity > 0),
    UnitPrice           INTEGER NOT NULL DEFAULT 0,
    LineTotal           INTEGER NOT NULL DEFAULT 0,
    Reason              TEXT
);

CREATE INDEX IF NOT EXISTS IX_SalesReturnItem_ReturnId ON SalesReturnItem(SalesReturnId);

-- =============================================================================
-- 16. PURCHASE_ORDER
-- =============================================================================
CREATE TABLE IF NOT EXISTS PurchaseOrder (
    PurchaseOrderId INTEGER PRIMARY KEY AUTOINCREMENT,
    OrderNumber     TEXT    NOT NULL UNIQUE,
    StoreId         INTEGER NOT NULL REFERENCES Store(StoreId) ON DELETE RESTRICT ON UPDATE CASCADE,
    SupplierId      INTEGER NOT NULL REFERENCES Supplier(SupplierId) ON DELETE RESTRICT ON UPDATE CASCADE,
    EmployeeId      INTEGER REFERENCES Employee(EmployeeId) ON DELETE RESTRICT ON UPDATE CASCADE,
    OrderDate       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    ExpectedDate    TEXT,
    SubTotal        INTEGER NOT NULL DEFAULT 0,
    TaxAmount       INTEGER NOT NULL DEFAULT 0,
    GrandTotal      INTEGER NOT NULL DEFAULT 0,
    PaidAmount      INTEGER NOT NULL DEFAULT 0,
    Status          TEXT    NOT NULL DEFAULT 'DRAFT',
    PaymentTerms    TEXT,
    Notes           TEXT,
    CreatedAt       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UpdatedAt       TEXT,
    CreatedBy       INTEGER REFERENCES Employee(EmployeeId) ON DELETE RESTRICT ON UPDATE CASCADE,
    UpdatedBy       INTEGER REFERENCES Employee(EmployeeId) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS IX_PurchaseOrder_SupplierId ON PurchaseOrder(SupplierId);
CREATE INDEX IF NOT EXISTS IX_PurchaseOrder_StoreId_OrderDate ON PurchaseOrder(StoreId, OrderDate);
CREATE INDEX IF NOT EXISTS IX_PurchaseOrder_Status ON PurchaseOrder(Status);

-- =============================================================================
-- 17. PURCHASE_ORDER_ITEM
-- =============================================================================
CREATE TABLE IF NOT EXISTS PurchaseOrderItem (
    PurchaseOrderItemId INTEGER PRIMARY KEY AUTOINCREMENT,
    PurchaseOrderId     INTEGER NOT NULL REFERENCES PurchaseOrder(PurchaseOrderId) ON DELETE CASCADE ON UPDATE CASCADE,
    ProductId           INTEGER NOT NULL REFERENCES Product(ProductId) ON DELETE RESTRICT ON UPDATE CASCADE,
    Quantity            INTEGER NOT NULL CHECK (Quantity > 0),
    ReceivedQuantity    INTEGER NOT NULL DEFAULT 0,
    UnitCost            INTEGER NOT NULL CHECK (UnitCost > 0),
    TaxPercent          REAL    NOT NULL DEFAULT 0,
    TaxAmount           INTEGER NOT NULL DEFAULT 0,
    LineTotal           INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS IX_PurchaseOrderItem_PurchaseOrderId ON PurchaseOrderItem(PurchaseOrderId);

-- =============================================================================
-- 18. PURCHASE_RETURN
-- =============================================================================
CREATE TABLE IF NOT EXISTS PurchaseReturn (
    PurchaseReturnId INTEGER PRIMARY KEY AUTOINCREMENT,
    ReturnNumber     TEXT    NOT NULL UNIQUE,
    PurchaseOrderId  INTEGER REFERENCES PurchaseOrder(PurchaseOrderId) ON DELETE RESTRICT ON UPDATE CASCADE,
    SupplierId       INTEGER NOT NULL REFERENCES Supplier(SupplierId) ON DELETE RESTRICT ON UPDATE CASCADE,
    ReturnDate       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    Reason           TEXT,
    SubTotal         INTEGER NOT NULL DEFAULT 0,
    GrandTotal       INTEGER NOT NULL DEFAULT 0,
    Status           TEXT,
    CreatedAt        TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    CreatedBy        INTEGER REFERENCES Employee(EmployeeId) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS IX_PurchaseReturn_SupplierId ON PurchaseReturn(SupplierId);

-- =============================================================================
-- 19. PURCHASE_RETURN_ITEM
-- =============================================================================
CREATE TABLE IF NOT EXISTS PurchaseReturnItem (
    PurchaseReturnItemId INTEGER PRIMARY KEY AUTOINCREMENT,
    PurchaseReturnId     INTEGER NOT NULL REFERENCES PurchaseReturn(PurchaseReturnId) ON DELETE CASCADE ON UPDATE CASCADE,
    PurchaseOrderItemId  INTEGER REFERENCES PurchaseOrderItem(PurchaseOrderItemId) ON DELETE SET NULL ON UPDATE CASCADE,
    ProductId            INTEGER NOT NULL REFERENCES Product(ProductId) ON DELETE RESTRICT ON UPDATE CASCADE,
    Quantity             INTEGER NOT NULL CHECK (Quantity > 0),
    UnitCost             INTEGER NOT NULL DEFAULT 0,
    LineTotal            INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS IX_PurchaseReturnItem_ReturnId ON PurchaseReturnItem(PurchaseReturnId);

-- =============================================================================
-- 20. WAREHOUSE
-- =============================================================================
CREATE TABLE IF NOT EXISTS Warehouse (
    WarehouseId INTEGER PRIMARY KEY AUTOINCREMENT,
    StoreId     INTEGER NOT NULL REFERENCES Store(StoreId) ON DELETE RESTRICT ON UPDATE CASCADE,
    Code        TEXT    NOT NULL UNIQUE,
    Name        TEXT    NOT NULL,
    Address     TEXT,
    IsActive    INTEGER NOT NULL DEFAULT 1,
    CreatedAt   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UpdatedAt   TEXT,
    IsDeleted   INTEGER NOT NULL DEFAULT 0
);

-- =============================================================================
-- 21. INVENTORY
-- =============================================================================
CREATE TABLE IF NOT EXISTS Inventory (
    InventoryId      INTEGER PRIMARY KEY AUTOINCREMENT,
    WarehouseId      INTEGER NOT NULL REFERENCES Warehouse(WarehouseId) ON DELETE RESTRICT ON UPDATE CASCADE,
    ProductId        INTEGER NOT NULL REFERENCES Product(ProductId) ON DELETE RESTRICT ON UPDATE CASCADE,
    Quantity         INTEGER NOT NULL DEFAULT 0 CHECK (Quantity >= 0),
    ReservedQuantity INTEGER NOT NULL DEFAULT 0 CHECK (ReservedQuantity >= 0),
    AvailableQuantity INTEGER NOT NULL DEFAULT 0 CHECK (AvailableQuantity >= 0),
    UpdatedAt        TEXT,
    UNIQUE(WarehouseId, ProductId)
);

CREATE INDEX IF NOT EXISTS IX_Inventory_Warehouse_Product ON Inventory(WarehouseId, ProductId);

-- =============================================================================
-- 22. STOCK_MOVEMENT  ← THE SOURCE OF TRUTH
-- =============================================================================
CREATE TABLE IF NOT EXISTS StockMovement (
    StockMovementId  INTEGER PRIMARY KEY AUTOINCREMENT,
    MovementNumber   TEXT    NOT NULL UNIQUE,
    WarehouseId      INTEGER NOT NULL REFERENCES Warehouse(WarehouseId) ON DELETE RESTRICT ON UPDATE CASCADE,
    ProductId        INTEGER NOT NULL REFERENCES Product(ProductId) ON DELETE RESTRICT ON UPDATE CASCADE,
    SerialNumberId   INTEGER REFERENCES SerialNumber(SerialNumberId) ON DELETE SET NULL ON UPDATE CASCADE,
    MovementType     TEXT    NOT NULL CHECK (MovementType IN (
        'PURCHASE_IN','PURCHASE_RETURN_OUT',
        'SALE_OUT','SALE_RETURN_IN',
        'TRANSFER_OUT','TRANSFER_IN',
        'ADJUSTMENT_IN','ADJUSTMENT_OUT',
        'INITIAL'
    )),
    Quantity         INTEGER NOT NULL CHECK (Quantity != 0),
    UnitCost         INTEGER NOT NULL CHECK (UnitCost >= 0),
    ReferenceType    TEXT,
    ReferenceId      INTEGER,
    ReferenceLineId  INTEGER,
    Notes            TEXT,
    CreatedAt        TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    CreatedBy        INTEGER REFERENCES Employee(EmployeeId) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS IX_StockMovement_ProductId ON StockMovement(ProductId, CreatedAt);
CREATE INDEX IF NOT EXISTS IX_StockMovement_WarehouseId ON StockMovement(WarehouseId);
CREATE INDEX IF NOT EXISTS IX_StockMovement_Reference ON StockMovement(ReferenceType, ReferenceId);

-- =============================================================================
-- 23. STOCK_COUNT
-- =============================================================================
CREATE TABLE IF NOT EXISTS StockCount (
    StockCountId INTEGER PRIMARY KEY AUTOINCREMENT,
    CountNumber  TEXT    NOT NULL UNIQUE,
    WarehouseId  INTEGER NOT NULL REFERENCES Warehouse(WarehouseId) ON DELETE RESTRICT ON UPDATE CASCADE,
    CountDate    TEXT    NOT NULL,
    Status       TEXT    NOT NULL DEFAULT 'DRAFT',
    Notes        TEXT,
    Items        TEXT,
    CreatedAt    TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    CreatedBy    INTEGER REFERENCES Employee(EmployeeId) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS IX_StockCount_WarehouseId ON StockCount(WarehouseId);

-- =============================================================================
-- 24. REPAIR_ORDER
-- =============================================================================
CREATE TABLE IF NOT EXISTS RepairOrder (
    RepairOrderId   INTEGER PRIMARY KEY AUTOINCREMENT,
    RepairNumber    TEXT    NOT NULL UNIQUE,
    StoreId         INTEGER NOT NULL REFERENCES Store(StoreId) ON DELETE RESTRICT ON UPDATE CASCADE,
    CustomerId      INTEGER NOT NULL REFERENCES Customer(CustomerId) ON DELETE RESTRICT ON UPDATE CASCADE,
    EmployeeId      INTEGER REFERENCES Employee(EmployeeId) ON DELETE RESTRICT ON UPDATE CASCADE,
    SalesOrderId    INTEGER REFERENCES SalesOrder(SalesOrderId) ON DELETE SET NULL ON UPDATE CASCADE,
    WarrantyId      INTEGER REFERENCES Warranty(WarrantyId) ON DELETE SET NULL ON UPDATE CASCADE,
    DeviceType      TEXT    NOT NULL,
    DeviceBrand     TEXT,
    DeviceModel     TEXT,
    SerialNumber    TEXT,
    ReportedIssue   TEXT    NOT NULL,
    Status          TEXT    NOT NULL DEFAULT 'RECEIVED',
    Diagnosis       TEXT,
    StatusHistory   TEXT,
    DiagnosisFee    INTEGER NOT NULL DEFAULT 0,
    LaborFee        INTEGER NOT NULL DEFAULT 0,
    PartsCost       INTEGER NOT NULL DEFAULT 0,
    GrandTotal      INTEGER NOT NULL DEFAULT 0,
    ReceivedDate    TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    EstimatedDate   TEXT,
    CompletedDate   TEXT,
    Notes           TEXT,
    TechnicianName  TEXT,
    TechnicianPhone TEXT,
    CreatedAt       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UpdatedAt       TEXT
);

CREATE INDEX IF NOT EXISTS IX_RepairOrder_CustomerId ON RepairOrder(CustomerId);
CREATE INDEX IF NOT EXISTS IX_RepairOrder_Status ON RepairOrder(Status);

-- =============================================================================
-- 25. REPAIR_PART
-- =============================================================================
CREATE TABLE IF NOT EXISTS RepairPart (
    RepairPartId    INTEGER PRIMARY KEY AUTOINCREMENT,
    RepairOrderId   INTEGER NOT NULL REFERENCES RepairOrder(RepairOrderId) ON DELETE CASCADE ON UPDATE CASCADE,
    ProductId       INTEGER NOT NULL REFERENCES Product(ProductId) ON DELETE RESTRICT ON UPDATE CASCADE,
    SerialNumberId  INTEGER REFERENCES SerialNumber(SerialNumberId) ON DELETE SET NULL ON UPDATE CASCADE,
    Quantity        INTEGER NOT NULL CHECK (Quantity > 0),
    UnitPrice       INTEGER NOT NULL DEFAULT 0,
    LineTotal       INTEGER NOT NULL DEFAULT 0,
    Notes           TEXT
);

CREATE INDEX IF NOT EXISTS IX_RepairPart_RepairOrderId ON RepairPart(RepairOrderId);

-- =============================================================================
-- 26. WARRANTY
-- =============================================================================
CREATE TABLE IF NOT EXISTS Warranty (
    WarrantyId          INTEGER PRIMARY KEY AUTOINCREMENT,
    WarrantyNumber      TEXT    NOT NULL UNIQUE,
    ProductId           INTEGER NOT NULL REFERENCES Product(ProductId) ON DELETE RESTRICT ON UPDATE CASCADE,
    SerialNumberId      INTEGER REFERENCES SerialNumber(SerialNumberId) ON DELETE SET NULL ON UPDATE CASCADE,
    SalesOrderItemId    INTEGER NOT NULL REFERENCES SalesOrderItem(SalesOrderItemId) ON DELETE RESTRICT ON UPDATE CASCADE,
    CustomerId          INTEGER NOT NULL REFERENCES Customer(CustomerId) ON DELETE RESTRICT ON UPDATE CASCADE,
    StartDate           TEXT    NOT NULL,
    EndDate             TEXT    NOT NULL,
    Status              TEXT    NOT NULL DEFAULT 'ACTIVE' CHECK (Status IN ('ACTIVE','EXPIRED','CLAIMED','VOID')),
    WarrantyType        TEXT    NOT NULL DEFAULT 'STORE' CHECK (WarrantyType IN ('MANUFACTURER','STORE','EXTENDED')),
    OriginalDuration    INTEGER NOT NULL,
    Notes               TEXT,
    CreatedAt           TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UpdatedAt           TEXT
);

CREATE INDEX IF NOT EXISTS IX_Warranty_SerialNumberId ON Warranty(SerialNumberId);
CREATE INDEX IF NOT EXISTS IX_Warranty_SalesOrderItemId ON Warranty(SalesOrderItemId);
CREATE INDEX IF NOT EXISTS IX_Warranty_Status ON Warranty(Status);

-- =============================================================================
-- 27. FINANCIAL_RECORD
-- =============================================================================
CREATE TABLE IF NOT EXISTS FinancialRecord (
    FinancialRecordId INTEGER PRIMARY KEY AUTOINCREMENT,
    RecordNumber     TEXT    NOT NULL UNIQUE,
    StoreId          INTEGER NOT NULL REFERENCES Store(StoreId) ON DELETE RESTRICT ON UPDATE CASCADE,
    RecordDate       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    RecordType       TEXT    NOT NULL CHECK (RecordType IN ('INCOME','EXPENSE','TRANSFER')),
    Category         TEXT    NOT NULL,
    Amount           INTEGER NOT NULL CHECK (Amount != 0),
    PaymentMethod    TEXT,
    ReferenceType    TEXT,
    ReferenceId      INTEGER,
    Description      TEXT,
    Notes            TEXT,
    CreatedAt        TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    CreatedBy        INTEGER REFERENCES Employee(EmployeeId) ON DELETE RESTRICT ON UPDATE CASCADE,
    IsDeleted        INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS IX_FinancialRecord_StoreId_RecordDate ON FinancialRecord(StoreId, RecordDate);
CREATE INDEX IF NOT EXISTS IX_FinancialRecord_RecordType ON FinancialRecord(RecordType);
CREATE INDEX IF NOT EXISTS IX_FinancialRecord_Reference ON FinancialRecord(ReferenceType, ReferenceId);

-- =============================================================================
-- 28. AUDIT_LOG
-- =============================================================================
CREATE TABLE IF NOT EXISTS AuditLog (
    AuditLogId  INTEGER PRIMARY KEY AUTOINCREMENT,
    TableName   TEXT    NOT NULL,
    RecordId    INTEGER NOT NULL,
    Action      TEXT    NOT NULL CHECK (Action IN ('INSERT','UPDATE','DELETE')),
    EmployeeId  INTEGER REFERENCES Employee(EmployeeId) ON DELETE SET NULL ON UPDATE CASCADE,
    OldValues   TEXT,
    NewValues   TEXT,
    ChangedAt   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS IX_AuditLog_TableName_RecordId ON AuditLog(TableName, RecordId);
CREATE INDEX IF NOT EXISTS IX_AuditLog_ChangedAt ON AuditLog(ChangedAt);

-- =============================================================================
-- END OF SCHEMA — 30 TABLES
-- =============================================================================
