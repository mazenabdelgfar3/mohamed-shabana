-- =============================================================================
-- COMPUTER STORE ERP - PRODUCTION PostgreSQL SCHEMA (Supabase)
-- =============================================================================
-- Target: PostgreSQL 15+
-- Design: 28 tables, 22 indexes
-- =============================================================================

-- =============================================================================
-- 1. STORE
-- =============================================================================
CREATE TABLE IF NOT EXISTS "Store" (
    "StoreId"     SERIAL PRIMARY KEY,
    "StoreUid"    TEXT    NOT NULL UNIQUE,
    "Code"        TEXT    NOT NULL UNIQUE,
    "Name"        TEXT    NOT NULL,
    "Phone"       TEXT,
    "Email"       TEXT,
    "Address"     TEXT,
    "TaxNumber"   TEXT,
    "IsActive"    INTEGER NOT NULL DEFAULT 1,
    "CreatedAt"   TIMESTAMP NOT NULL DEFAULT NOW(),
    "UpdatedAt"   TIMESTAMP,
    "IsDeleted"   INTEGER NOT NULL DEFAULT 0
);

-- =============================================================================
-- 2. EMPLOYEE
-- =============================================================================
CREATE TABLE IF NOT EXISTS "Employee" (
    "EmployeeId"      SERIAL PRIMARY KEY,
    "EmployeeUid"     TEXT    NOT NULL UNIQUE,
    "StoreId"         INTEGER NOT NULL REFERENCES "Store"("StoreId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "EmployeeCode"    TEXT    NOT NULL UNIQUE,
    "FullName"        TEXT    NOT NULL,
    "Phone"           TEXT,
    "Email"           TEXT    UNIQUE,
    "PasswordHash"    TEXT    NOT NULL,
    "LastLoginAt"     TIMESTAMP,
    "IsActive"        INTEGER NOT NULL DEFAULT 1,
    "CreatedAt"       TIMESTAMP NOT NULL DEFAULT NOW(),
    "UpdatedAt"       TIMESTAMP,
    "IsDeleted"       INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS "IX_Employee_StoreId" ON "Employee"("StoreId");

-- =============================================================================
-- 3. ROLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS "Role" (
    "RoleId"      SERIAL PRIMARY KEY,
    "RoleName"    TEXT    NOT NULL UNIQUE,
    "Permissions" TEXT,
    "IsActive"    INTEGER NOT NULL DEFAULT 1
);

-- =============================================================================
-- 4. EMPLOYEE_ROLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS "EmployeeRole" (
    "EmployeeRoleId"  SERIAL PRIMARY KEY,
    "EmployeeId"      INTEGER NOT NULL REFERENCES "Employee"("EmployeeId") ON DELETE CASCADE ON UPDATE CASCADE,
    "RoleId"          INTEGER NOT NULL REFERENCES "Role"("RoleId") ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE("EmployeeId", "RoleId")
);

CREATE INDEX IF NOT EXISTS "IX_EmployeeRole_EmployeeId" ON "EmployeeRole"("EmployeeId");

-- =============================================================================
-- 5. CUSTOMER
-- =============================================================================
CREATE TABLE IF NOT EXISTS "Customer" (
    "CustomerId"      SERIAL PRIMARY KEY,
    "CustomerUid"     TEXT    NOT NULL UNIQUE,
    "CustomerCode"    TEXT    NOT NULL UNIQUE,
    "FullName"        TEXT    NOT NULL,
    "Phone"           TEXT,
    "Email"           TEXT,
    "TaxNumber"       TEXT,
    "CreditLimit"     INTEGER NOT NULL DEFAULT 0,
    "Notes"           TEXT,
    "IsActive"        INTEGER NOT NULL DEFAULT 1,
    "CreatedAt"       TIMESTAMP NOT NULL DEFAULT NOW(),
    "UpdatedAt"       TIMESTAMP,
    "IsDeleted"       INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS "IX_Customer_FullName" ON "Customer"("FullName");

-- =============================================================================
-- 6. SUPPLIER
-- =============================================================================
CREATE TABLE IF NOT EXISTS "Supplier" (
    "SupplierId"      SERIAL PRIMARY KEY,
    "SupplierUid"     TEXT    NOT NULL UNIQUE,
    "SupplierCode"    TEXT    NOT NULL UNIQUE,
    "CompanyName"     TEXT    NOT NULL,
    "ContactPerson"   TEXT,
    "Phone"           TEXT,
    "Email"           TEXT,
    "TaxNumber"       TEXT,
    "PaymentTerms"    TEXT,
    "Notes"           TEXT,
    "IsActive"        INTEGER NOT NULL DEFAULT 1,
    "CreatedAt"       TIMESTAMP NOT NULL DEFAULT NOW(),
    "UpdatedAt"       TIMESTAMP,
    "IsDeleted"       INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS "IX_Supplier_CompanyName" ON "Supplier"("CompanyName");

-- =============================================================================
-- 7. CATEGORY
-- =============================================================================
CREATE TABLE IF NOT EXISTS "Category" (
    "CategoryId"          SERIAL PRIMARY KEY,
    "ParentCategoryId"    INTEGER REFERENCES "Category"("CategoryId") ON DELETE SET NULL ON UPDATE CASCADE,
    "Code"                TEXT    NOT NULL UNIQUE,
    "Name"                TEXT    NOT NULL,
    "Description"         TEXT,
    "IsActive"            INTEGER NOT NULL DEFAULT 1,
    "CreatedAt"           TIMESTAMP NOT NULL DEFAULT NOW(),
    "UpdatedAt"           TIMESTAMP,
    "IsDeleted"           INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS "IX_Category_ParentCategoryId" ON "Category"("ParentCategoryId");

-- =============================================================================
-- 8. BRAND
-- =============================================================================
CREATE TABLE IF NOT EXISTS "Brand" (
    "BrandId"     SERIAL PRIMARY KEY,
    "Code"        TEXT    NOT NULL UNIQUE,
    "Name"        TEXT    NOT NULL,
    "IsActive"    INTEGER NOT NULL DEFAULT 1,
    "CreatedAt"   TIMESTAMP NOT NULL DEFAULT NOW(),
    "UpdatedAt"   TIMESTAMP,
    "IsDeleted"   INTEGER NOT NULL DEFAULT 0
);

-- =============================================================================
-- 9. TAX
-- =============================================================================
CREATE TABLE IF NOT EXISTS "Tax" (
    "TaxId"      SERIAL PRIMARY KEY,
    "Code"       TEXT    NOT NULL UNIQUE,
    "Name"       TEXT    NOT NULL,
    "Rate"       REAL    NOT NULL CHECK ("Rate" >= 0),
    "IsActive"   INTEGER NOT NULL DEFAULT 1
);

-- =============================================================================
-- 10. PRODUCT
-- =============================================================================
CREATE TABLE IF NOT EXISTS "Product" (
    "ProductId"       SERIAL PRIMARY KEY,
    "ProductUid"      TEXT    NOT NULL UNIQUE,
    "CategoryId"      INTEGER REFERENCES "Category"("CategoryId") ON DELETE SET NULL ON UPDATE CASCADE,
    "BrandId"         INTEGER REFERENCES "Brand"("BrandId") ON DELETE SET NULL ON UPDATE CASCADE,
    "SupplierId"      INTEGER REFERENCES "Supplier"("SupplierId") ON DELETE SET NULL ON UPDATE CASCADE,
    "TaxId"           INTEGER REFERENCES "Tax"("TaxId") ON DELETE SET NULL ON UPDATE CASCADE,
    "SKU"             TEXT    NOT NULL UNIQUE,
    "Name"            TEXT    NOT NULL,
    "Description"     TEXT,
    "UnitOfMeasure"   TEXT    NOT NULL DEFAULT 'Piece',
    "Barcode"         TEXT    UNIQUE,
    "BarcodesAlt"     TEXT,
    "CostPrice"       INTEGER NOT NULL CHECK ("CostPrice" >= 0),
    "SellingPrice"    INTEGER NOT NULL CHECK ("SellingPrice" > 0),
    "SupplierPrice"   INTEGER,
    "MinStockLevel"   INTEGER NOT NULL DEFAULT 0,
    "MaxStockLevel"   INTEGER NOT NULL DEFAULT 0,
    "WarrantyDays"    INTEGER NOT NULL DEFAULT 0,
    "HasSerialNumbers" INTEGER NOT NULL DEFAULT 0,
    "IsActive"        INTEGER NOT NULL DEFAULT 1,
    "ImagePath"       TEXT,
    "CreatedAt"       TIMESTAMP NOT NULL DEFAULT NOW(),
    "UpdatedAt"       TIMESTAMP,
    "IsDeleted"       INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS "IX_Product_CategoryId" ON "Product"("CategoryId");
CREATE INDEX IF NOT EXISTS "IX_Product_BrandId" ON "Product"("BrandId");
CREATE INDEX IF NOT EXISTS "IX_Product_SupplierId" ON "Product"("SupplierId");
CREATE INDEX IF NOT EXISTS "IX_Product_Name" ON "Product"("Name");

-- =============================================================================
-- 11. SALES_ORDER (defined before SerialNumber due to FK dependency)
-- =============================================================================
CREATE TABLE IF NOT EXISTS "SalesOrder" (
    "SalesOrderId"    SERIAL PRIMARY KEY,
    "OrderNumber"     TEXT    NOT NULL UNIQUE,
    "StoreId"         INTEGER NOT NULL REFERENCES "Store"("StoreId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "CustomerId"      INTEGER REFERENCES "Customer"("CustomerId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "EmployeeId"      INTEGER REFERENCES "Employee"("EmployeeId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "OrderDate"       TIMESTAMP NOT NULL DEFAULT NOW(),
    "DueDate"         TIMESTAMP,
    "SubTotal"        INTEGER NOT NULL DEFAULT 0,
    "TaxAmount"       INTEGER NOT NULL DEFAULT 0,
    "DiscountAmount"  INTEGER NOT NULL DEFAULT 0,
    "GrandTotal"      INTEGER NOT NULL DEFAULT 0,
    "PaidAmount"      INTEGER NOT NULL DEFAULT 0,
    "BalanceDue"      INTEGER NOT NULL DEFAULT 0,
    "PaymentMethod"   TEXT,
    "PaymentDate"     TIMESTAMP,
    "Status"          TEXT    NOT NULL DEFAULT 'DRAFT',
    "Notes"           TEXT,
    "CreatedAt"       TIMESTAMP NOT NULL DEFAULT NOW(),
    "UpdatedAt"       TIMESTAMP,
    "CreatedBy"       INTEGER REFERENCES "Employee"("EmployeeId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "UpdatedBy"       INTEGER REFERENCES "Employee"("EmployeeId") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "IX_SalesOrder_StoreId_OrderDate" ON "SalesOrder"("StoreId", "OrderDate");
CREATE INDEX IF NOT EXISTS "IX_SalesOrder_CustomerId" ON "SalesOrder"("CustomerId");
CREATE INDEX IF NOT EXISTS "IX_SalesOrder_Status" ON "SalesOrder"("Status");

-- =============================================================================
-- 12. PURCHASE_ORDER (defined before SerialNumber due to FK dependency)
-- =============================================================================
CREATE TABLE IF NOT EXISTS "PurchaseOrder" (
    "PurchaseOrderId" SERIAL PRIMARY KEY,
    "OrderNumber"     TEXT    NOT NULL UNIQUE,
    "StoreId"         INTEGER NOT NULL REFERENCES "Store"("StoreId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "SupplierId"      INTEGER NOT NULL REFERENCES "Supplier"("SupplierId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "EmployeeId"      INTEGER REFERENCES "Employee"("EmployeeId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "OrderDate"       TIMESTAMP NOT NULL DEFAULT NOW(),
    "ExpectedDate"    TIMESTAMP,
    "SubTotal"        INTEGER NOT NULL DEFAULT 0,
    "TaxAmount"       INTEGER NOT NULL DEFAULT 0,
    "GrandTotal"      INTEGER NOT NULL DEFAULT 0,
    "PaidAmount"      INTEGER NOT NULL DEFAULT 0,
    "Status"          TEXT    NOT NULL DEFAULT 'DRAFT',
    "PaymentTerms"    TEXT,
    "Notes"           TEXT,
    "CreatedAt"       TIMESTAMP NOT NULL DEFAULT NOW(),
    "UpdatedAt"       TIMESTAMP,
    "CreatedBy"       INTEGER REFERENCES "Employee"("EmployeeId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "UpdatedBy"       INTEGER REFERENCES "Employee"("EmployeeId") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "IX_PurchaseOrder_SupplierId" ON "PurchaseOrder"("SupplierId");
CREATE INDEX IF NOT EXISTS "IX_PurchaseOrder_StoreId_OrderDate" ON "PurchaseOrder"("StoreId", "OrderDate");
CREATE INDEX IF NOT EXISTS "IX_PurchaseOrder_Status" ON "PurchaseOrder"("Status");

-- =============================================================================
-- 13. PURCHASE_ORDER_ITEM
-- =============================================================================
CREATE TABLE IF NOT EXISTS "PurchaseOrderItem" (
    "PurchaseOrderItemId" SERIAL PRIMARY KEY,
    "PurchaseOrderId"     INTEGER NOT NULL REFERENCES "PurchaseOrder"("PurchaseOrderId") ON DELETE CASCADE ON UPDATE CASCADE,
    "ProductId"           INTEGER NOT NULL REFERENCES "Product"("ProductId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "Quantity"            INTEGER NOT NULL CHECK ("Quantity" > 0),
    "ReceivedQuantity"    INTEGER NOT NULL DEFAULT 0,
    "UnitCost"            INTEGER NOT NULL CHECK ("UnitCost" > 0),
    "TaxPercent"          REAL    NOT NULL DEFAULT 0,
    "TaxAmount"           INTEGER NOT NULL DEFAULT 0,
    "LineTotal"           INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS "IX_PurchaseOrderItem_PurchaseOrderId" ON "PurchaseOrderItem"("PurchaseOrderId");

-- =============================================================================
-- 14. SALES_ORDER_ITEM (needs SalesOrder first)
-- =============================================================================
CREATE TABLE IF NOT EXISTS "SalesOrderItem" (
    "SalesOrderItemId"    SERIAL PRIMARY KEY,
    "SalesOrderId"        INTEGER NOT NULL REFERENCES "SalesOrder"("SalesOrderId") ON DELETE CASCADE ON UPDATE CASCADE,
    "ProductId"           INTEGER NOT NULL REFERENCES "Product"("ProductId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "SerialNumberId"      INTEGER,
    "Quantity"            INTEGER NOT NULL CHECK ("Quantity" > 0),
    "UnitPrice"           INTEGER NOT NULL CHECK ("UnitPrice" > 0),
    "DiscountPercent"     REAL    NOT NULL DEFAULT 0,
    "DiscountAmount"      INTEGER NOT NULL DEFAULT 0,
    "TaxPercent"          REAL    NOT NULL DEFAULT 0,
    "TaxAmount"           INTEGER NOT NULL DEFAULT 0,
    "LineTotal"           INTEGER NOT NULL DEFAULT 0,
    "WarrantyDays"        INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS "IX_SalesOrderItem_SalesOrderId" ON "SalesOrderItem"("SalesOrderId");
CREATE INDEX IF NOT EXISTS "IX_SalesOrderItem_ProductId" ON "SalesOrderItem"("ProductId");

-- =============================================================================
-- 15. SERIAL_NUMBER
-- =============================================================================
CREATE TABLE IF NOT EXISTS "SerialNumber" (
    "SerialNumberId"          SERIAL PRIMARY KEY,
    "ProductId"               INTEGER NOT NULL REFERENCES "Product"("ProductId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "SalesOrderItemId"        INTEGER REFERENCES "SalesOrderItem"("SalesOrderItemId") ON DELETE SET NULL ON UPDATE CASCADE,
    "PurchaseOrderItemId"     INTEGER REFERENCES "PurchaseOrderItem"("PurchaseOrderItemId") ON DELETE SET NULL ON UPDATE CASCADE,
    "SerialNumber"            TEXT    NOT NULL UNIQUE,
    "CurrentStatus"           TEXT    NOT NULL DEFAULT 'IN_STOCK' CHECK ("CurrentStatus" IN ('IN_STOCK','SOLD','IN_REPAIR','RETURNED','EXPIRED')),
    "WarrantyStart"           TIMESTAMP,
    "WarrantyEnd"             TIMESTAMP,
    "WarrantyStatus"          TEXT    DEFAULT 'ACTIVE' CHECK ("WarrantyStatus" IN ('ACTIVE','EXPIRED','CLAIMED','VOID')),
    "CreatedAt"               TIMESTAMP NOT NULL DEFAULT NOW(),
    "UpdatedAt"               TIMESTAMP
);

CREATE INDEX IF NOT EXISTS "IX_SerialNumber_ProductId" ON "SerialNumber"("ProductId");
CREATE INDEX IF NOT EXISTS "IX_SerialNumber_Status" ON "SerialNumber"("CurrentStatus");

-- =============================================================================
-- 16. WARRANTY
-- =============================================================================
CREATE TABLE IF NOT EXISTS "Warranty" (
    "WarrantyId"          SERIAL PRIMARY KEY,
    "WarrantyNumber"      TEXT    NOT NULL UNIQUE,
    "ProductId"           INTEGER NOT NULL REFERENCES "Product"("ProductId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "SerialNumberId"      INTEGER REFERENCES "SerialNumber"("SerialNumberId") ON DELETE SET NULL ON UPDATE CASCADE,
    "SalesOrderItemId"    INTEGER NOT NULL REFERENCES "SalesOrderItem"("SalesOrderItemId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "CustomerId"          INTEGER NOT NULL REFERENCES "Customer"("CustomerId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "StartDate"           TIMESTAMP NOT NULL,
    "EndDate"             TIMESTAMP NOT NULL,
    "Status"              TEXT    NOT NULL DEFAULT 'ACTIVE' CHECK ("Status" IN ('ACTIVE','EXPIRED','CLAIMED','VOID')),
    "WarrantyType"        TEXT    NOT NULL DEFAULT 'STORE' CHECK ("WarrantyType" IN ('MANUFACTURER','STORE','EXTENDED')),
    "OriginalDuration"    INTEGER NOT NULL,
    "Notes"               TEXT,
    "CreatedAt"           TIMESTAMP NOT NULL DEFAULT NOW(),
    "UpdatedAt"           TIMESTAMP
);

CREATE INDEX IF NOT EXISTS "IX_Warranty_SerialNumberId" ON "Warranty"("SerialNumberId");
CREATE INDEX IF NOT EXISTS "IX_Warranty_SalesOrderItemId" ON "Warranty"("SalesOrderItemId");
CREATE INDEX IF NOT EXISTS "IX_Warranty_Status" ON "Warranty"("Status");

-- =============================================================================
-- 17. SALES_RETURN
-- =============================================================================
CREATE TABLE IF NOT EXISTS "SalesReturn" (
    "SalesReturnId"   SERIAL PRIMARY KEY,
    "ReturnNumber"    TEXT    NOT NULL UNIQUE,
    "SalesOrderId"    INTEGER REFERENCES "SalesOrder"("SalesOrderId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "CustomerId"      INTEGER NOT NULL REFERENCES "Customer"("CustomerId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "ReturnDate"      TIMESTAMP NOT NULL DEFAULT NOW(),
    "Reason"          TEXT,
    "SubTotal"        INTEGER NOT NULL DEFAULT 0,
    "TaxAmount"       INTEGER NOT NULL DEFAULT 0,
    "GrandTotal"      INTEGER NOT NULL DEFAULT 0,
    "Status"          TEXT    NOT NULL DEFAULT 'DRAFT',
    "CreatedAt"       TIMESTAMP NOT NULL DEFAULT NOW(),
    "CreatedBy"       INTEGER REFERENCES "Employee"("EmployeeId") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "IX_SalesReturn_CustomerId" ON "SalesReturn"("CustomerId");

-- =============================================================================
-- 18. SALES_RETURN_ITEM
-- =============================================================================
CREATE TABLE IF NOT EXISTS "SalesReturnItem" (
    "SalesReturnItemId"   SERIAL PRIMARY KEY,
    "SalesReturnId"       INTEGER NOT NULL REFERENCES "SalesReturn"("SalesReturnId") ON DELETE CASCADE ON UPDATE CASCADE,
    "SalesOrderItemId"    INTEGER REFERENCES "SalesOrderItem"("SalesOrderItemId") ON DELETE SET NULL ON UPDATE CASCADE,
    "ProductId"           INTEGER NOT NULL REFERENCES "Product"("ProductId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "Quantity"            INTEGER NOT NULL CHECK ("Quantity" > 0),
    "UnitPrice"           INTEGER NOT NULL DEFAULT 0,
    "LineTotal"           INTEGER NOT NULL DEFAULT 0,
    "Reason"              TEXT
);

CREATE INDEX IF NOT EXISTS "IX_SalesReturnItem_ReturnId" ON "SalesReturnItem"("SalesReturnId");

-- =============================================================================
-- 19. PURCHASE_RETURN
-- =============================================================================
CREATE TABLE IF NOT EXISTS "PurchaseReturn" (
    "PurchaseReturnId" SERIAL PRIMARY KEY,
    "ReturnNumber"     TEXT    NOT NULL UNIQUE,
    "PurchaseOrderId"  INTEGER REFERENCES "PurchaseOrder"("PurchaseOrderId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "SupplierId"       INTEGER NOT NULL REFERENCES "Supplier"("SupplierId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "ReturnDate"       TIMESTAMP NOT NULL DEFAULT NOW(),
    "Reason"           TEXT,
    "SubTotal"         INTEGER NOT NULL DEFAULT 0,
    "GrandTotal"       INTEGER NOT NULL DEFAULT 0,
    "Status"           TEXT,
    "CreatedAt"        TIMESTAMP NOT NULL DEFAULT NOW(),
    "CreatedBy"        INTEGER REFERENCES "Employee"("EmployeeId") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "IX_PurchaseReturn_SupplierId" ON "PurchaseReturn"("SupplierId");

-- =============================================================================
-- 20. PURCHASE_RETURN_ITEM
-- =============================================================================
CREATE TABLE IF NOT EXISTS "PurchaseReturnItem" (
    "PurchaseReturnItemId" SERIAL PRIMARY KEY,
    "PurchaseReturnId"     INTEGER NOT NULL REFERENCES "PurchaseReturn"("PurchaseReturnId") ON DELETE CASCADE ON UPDATE CASCADE,
    "PurchaseOrderItemId"  INTEGER REFERENCES "PurchaseOrderItem"("PurchaseOrderItemId") ON DELETE SET NULL ON UPDATE CASCADE,
    "ProductId"            INTEGER NOT NULL REFERENCES "Product"("ProductId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "Quantity"             INTEGER NOT NULL CHECK ("Quantity" > 0),
    "UnitCost"             INTEGER NOT NULL DEFAULT 0,
    "LineTotal"            INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS "IX_PurchaseReturnItem_ReturnId" ON "PurchaseReturnItem"("PurchaseReturnId");

-- =============================================================================
-- 21. WAREHOUSE
-- =============================================================================
CREATE TABLE IF NOT EXISTS "Warehouse" (
    "WarehouseId" SERIAL PRIMARY KEY,
    "StoreId"     INTEGER NOT NULL REFERENCES "Store"("StoreId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "Code"        TEXT    NOT NULL UNIQUE,
    "Name"        TEXT    NOT NULL,
    "Address"     TEXT,
    "IsActive"    INTEGER NOT NULL DEFAULT 1,
    "CreatedAt"   TIMESTAMP NOT NULL DEFAULT NOW(),
    "UpdatedAt"   TIMESTAMP,
    "IsDeleted"   INTEGER NOT NULL DEFAULT 0
);

-- =============================================================================
-- 22. INVENTORY
-- =============================================================================
CREATE TABLE IF NOT EXISTS "Inventory" (
    "InventoryId"      SERIAL PRIMARY KEY,
    "WarehouseId"      INTEGER NOT NULL REFERENCES "Warehouse"("WarehouseId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "ProductId"        INTEGER NOT NULL REFERENCES "Product"("ProductId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "Quantity"         INTEGER NOT NULL DEFAULT 0 CHECK ("Quantity" >= 0),
    "ReservedQuantity" INTEGER NOT NULL DEFAULT 0 CHECK ("ReservedQuantity" >= 0),
    "AvailableQuantity" INTEGER NOT NULL DEFAULT 0 CHECK ("AvailableQuantity" >= 0),
    "UpdatedAt"        TIMESTAMP,
    UNIQUE("WarehouseId", "ProductId")
);

CREATE INDEX IF NOT EXISTS "IX_Inventory_Warehouse_Product" ON "Inventory"("WarehouseId", "ProductId");

-- =============================================================================
-- 23. STOCK_MOVEMENT
-- =============================================================================
CREATE TABLE IF NOT EXISTS "StockMovement" (
    "StockMovementId"  SERIAL PRIMARY KEY,
    "MovementNumber"   TEXT    NOT NULL UNIQUE,
    "WarehouseId"      INTEGER NOT NULL REFERENCES "Warehouse"("WarehouseId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "ProductId"        INTEGER NOT NULL REFERENCES "Product"("ProductId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "SerialNumberId"   INTEGER REFERENCES "SerialNumber"("SerialNumberId") ON DELETE SET NULL ON UPDATE CASCADE,
    "MovementType"     TEXT    NOT NULL CHECK ("MovementType" IN (
        'PURCHASE_IN','PURCHASE_RETURN_OUT',
        'SALE_OUT','SALE_RETURN_IN',
        'TRANSFER_OUT','TRANSFER_IN',
        'ADJUSTMENT_IN','ADJUSTMENT_OUT',
        'INITIAL'
    )),
    "Quantity"         INTEGER NOT NULL CHECK ("Quantity" != 0),
    "UnitCost"         INTEGER NOT NULL CHECK ("UnitCost" >= 0),
    "ReferenceType"    TEXT,
    "ReferenceId"      INTEGER,
    "ReferenceLineId"  INTEGER,
    "Notes"            TEXT,
    "CreatedAt"        TIMESTAMP NOT NULL DEFAULT NOW(),
    "CreatedBy"        INTEGER REFERENCES "Employee"("EmployeeId") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "IX_StockMovement_ProductId" ON "StockMovement"("ProductId", "CreatedAt");
CREATE INDEX IF NOT EXISTS "IX_StockMovement_WarehouseId" ON "StockMovement"("WarehouseId");
CREATE INDEX IF NOT EXISTS "IX_StockMovement_Reference" ON "StockMovement"("ReferenceType", "ReferenceId");

-- =============================================================================
-- 24. STOCK_COUNT
-- =============================================================================
CREATE TABLE IF NOT EXISTS "StockCount" (
    "StockCountId" SERIAL PRIMARY KEY,
    "CountNumber"  TEXT    NOT NULL UNIQUE,
    "WarehouseId"  INTEGER NOT NULL REFERENCES "Warehouse"("WarehouseId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "CountDate"    TIMESTAMP NOT NULL,
    "Status"       TEXT    NOT NULL DEFAULT 'DRAFT',
    "Notes"        TEXT,
    "Items"        TEXT,
    "CreatedAt"    TIMESTAMP NOT NULL DEFAULT NOW(),
    "CreatedBy"    INTEGER REFERENCES "Employee"("EmployeeId") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "IX_StockCount_WarehouseId" ON "StockCount"("WarehouseId");

-- =============================================================================
-- 25. REPAIR_ORDER
-- =============================================================================
CREATE TABLE IF NOT EXISTS "RepairOrder" (
    "RepairOrderId"   SERIAL PRIMARY KEY,
    "RepairNumber"    TEXT    NOT NULL UNIQUE,
    "StoreId"         INTEGER NOT NULL REFERENCES "Store"("StoreId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "CustomerId"      INTEGER NOT NULL REFERENCES "Customer"("CustomerId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "EmployeeId"      INTEGER REFERENCES "Employee"("EmployeeId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "SalesOrderId"    INTEGER REFERENCES "SalesOrder"("SalesOrderId") ON DELETE SET NULL ON UPDATE CASCADE,
    "WarrantyId"      INTEGER REFERENCES "Warranty"("WarrantyId") ON DELETE SET NULL ON UPDATE CASCADE,
    "DeviceType"      TEXT    NOT NULL,
    "DeviceBrand"     TEXT,
    "DeviceModel"     TEXT,
    "SerialNumber"    TEXT,
    "ReportedIssue"   TEXT    NOT NULL,
    "Status"          TEXT    NOT NULL DEFAULT 'RECEIVED',
    "Diagnosis"       TEXT,
    "StatusHistory"   TEXT,
    "DiagnosisFee"    INTEGER NOT NULL DEFAULT 0,
    "LaborFee"        INTEGER NOT NULL DEFAULT 0,
    "PartsCost"       INTEGER NOT NULL DEFAULT 0,
    "GrandTotal"      INTEGER NOT NULL DEFAULT 0,
    "ReceivedDate"    TIMESTAMP NOT NULL DEFAULT NOW(),
    "EstimatedDate"   TIMESTAMP,
    "CompletedDate"   TIMESTAMP,
    "Notes"           TEXT,
    "TechnicianName"  TEXT,
    "TechnicianPhone" TEXT,
    "CreatedAt"       TIMESTAMP NOT NULL DEFAULT NOW(),
    "UpdatedAt"       TIMESTAMP
);

CREATE INDEX IF NOT EXISTS "IX_RepairOrder_CustomerId" ON "RepairOrder"("CustomerId");
CREATE INDEX IF NOT EXISTS "IX_RepairOrder_Status" ON "RepairOrder"("Status");

-- =============================================================================
-- 26. REPAIR_PART
-- =============================================================================
CREATE TABLE IF NOT EXISTS "RepairPart" (
    "RepairPartId"    SERIAL PRIMARY KEY,
    "RepairOrderId"   INTEGER NOT NULL REFERENCES "RepairOrder"("RepairOrderId") ON DELETE CASCADE ON UPDATE CASCADE,
    "ProductId"       INTEGER NOT NULL REFERENCES "Product"("ProductId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "SerialNumberId"  INTEGER REFERENCES "SerialNumber"("SerialNumberId") ON DELETE SET NULL ON UPDATE CASCADE,
    "Quantity"        INTEGER NOT NULL CHECK ("Quantity" > 0),
    "UnitPrice"       INTEGER NOT NULL DEFAULT 0,
    "LineTotal"       INTEGER NOT NULL DEFAULT 0,
    "Notes"           TEXT
);

CREATE INDEX IF NOT EXISTS "IX_RepairPart_RepairOrderId" ON "RepairPart"("RepairOrderId");

-- =============================================================================
-- 27. FINANCIAL_RECORD
-- =============================================================================
CREATE TABLE IF NOT EXISTS "FinancialRecord" (
    "FinancialRecordId" SERIAL PRIMARY KEY,
    "RecordNumber"     TEXT    NOT NULL UNIQUE,
    "StoreId"          INTEGER NOT NULL REFERENCES "Store"("StoreId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "RecordDate"       TIMESTAMP NOT NULL DEFAULT NOW(),
    "RecordType"       TEXT    NOT NULL CHECK ("RecordType" IN ('INCOME','EXPENSE','TRANSFER')),
    "Category"         TEXT    NOT NULL,
    "Amount"           INTEGER NOT NULL CHECK ("Amount" != 0),
    "PaymentMethod"    TEXT,
    "ReferenceType"    TEXT,
    "ReferenceId"      INTEGER,
    "Description"      TEXT,
    "Notes"            TEXT,
    "CreatedAt"        TIMESTAMP NOT NULL DEFAULT NOW(),
    "CreatedBy"        INTEGER REFERENCES "Employee"("EmployeeId") ON DELETE RESTRICT ON UPDATE CASCADE,
    "IsDeleted"        INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS "IX_FinancialRecord_StoreId_RecordDate" ON "FinancialRecord"("StoreId", "RecordDate");
CREATE INDEX IF NOT EXISTS "IX_FinancialRecord_RecordType" ON "FinancialRecord"("RecordType");
CREATE INDEX IF NOT EXISTS "IX_FinancialRecord_Reference" ON "FinancialRecord"("ReferenceType", "ReferenceId");

-- =============================================================================
-- 28. AUDIT_LOG
-- =============================================================================
CREATE TABLE IF NOT EXISTS "AuditLog" (
    "AuditLogId"  SERIAL PRIMARY KEY,
    "TableName"   TEXT    NOT NULL,
    "RecordId"    INTEGER NOT NULL,
    "Action"      TEXT    NOT NULL CHECK ("Action" IN ('INSERT','UPDATE','DELETE')),
    "EmployeeId"  INTEGER REFERENCES "Employee"("EmployeeId") ON DELETE SET NULL ON UPDATE CASCADE,
    "OldValues"   TEXT,
    "NewValues"   TEXT,
    "ChangedAt"   TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS "IX_AuditLog_TableName_RecordId" ON "AuditLog"("TableName", "RecordId");
CREATE INDEX IF NOT EXISTS "IX_AuditLog_ChangedAt" ON "AuditLog"("ChangedAt");

-- =============================================================================
-- END OF SCHEMA — 28 TABLES, 22 INDEXES
-- =============================================================================
