import uuid
from database.connection import get_db
from services.stock_engine import record_movement, check_stock_for_sale
from services.audit_service import log_action


def create_sales_order(store_id, customer_id, employee_id, items, payment_method=None,
                       paid_amount=0, notes=None, customer_name=None, customer_phone=None):
    if not items:
        raise ValueError("يجب إضافة عنصر واحد على الأقل")

    # Pre-validate stock availability for ALL items before any DB writes
    check_stock_for_sale(1, items)

    conn = get_db()
    cur = conn.cursor()

    if not customer_id:
        if customer_phone and customer_phone.strip():
            phone_clean = customer_phone.strip()
            cur.execute("SELECT CustomerId FROM Customer WHERE Phone = ? AND IsDeleted = 0 LIMIT 1", (phone_clean,))
            row = cur.fetchone()
            if row:
                customer_id = row['CustomerId']
            else:
                name_clean = customer_name.strip() if customer_name else "عميل جديد"
                uid = str(uuid.uuid4())
                code = f"CUS-{uuid.uuid4().hex[:8].upper()}"
                cur.execute("""
                    INSERT INTO Customer (CustomerUid, CustomerCode, FullName, Phone)
                    VALUES (?, ?, ?, ?)
                """, (uid, code, name_clean, phone_clean))
                customer_id = cur.lastrowid

    order_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
    order_date = "datetime('now')"

    sub_total = 0
    total_tax = 0
    total_discount = 0

    line_items = []
    for item in items:
        cur.execute("""
            SELECT p.ProductId, p.Name, p.SellingPrice, p.WarrantyDays
            FROM Product p
            WHERE p.ProductId = ?
        """, (item['ProductId'],))
        product = cur.fetchone()
        if not product:
            raise ValueError(f"المنتج {item['ProductId']} غير موجود")

        qty = item['Quantity']
        unit_price = item.get('UnitPrice', product['SellingPrice'])
        discount_pct = item.get('DiscountPercent', 0)

        discount_amt = int(unit_price * qty * discount_pct / 100)
        line_total = unit_price * qty - discount_amt

        sub_total += unit_price * qty
        total_discount += discount_amt

        line_items.append({
            'ProductId': product['ProductId'],
            'ProductName': product['Name'],
            'Quantity': qty,
            'UnitPrice': unit_price,
            'DiscountPercent': discount_pct,
            'DiscountAmount': discount_amt,
            'TaxPercent': 0,
            'TaxAmount': 0,
            'LineTotal': line_total,
            'WarrantyDays': product['WarrantyDays'],
        })

    grand_total = sub_total - total_discount + total_tax
    balance_due = grand_total - paid_amount

    cur.execute("""
        INSERT INTO SalesOrder
            (OrderNumber, StoreId, CustomerId, EmployeeId,
             OrderDate, SubTotal, TaxAmount, DiscountAmount,
             GrandTotal, PaidAmount, BalanceDue, PaymentMethod,
             PaymentDate, Status, Notes, CreatedBy, UpdatedBy)
        VALUES (?, ?, ?, ?, datetime('now'),
                ?, ?, ?, ?, ?, ?, ?,
                CASE WHEN ? > 0 THEN datetime('now') ELSE NULL END,
                'DRAFT', ?, ?, ?)
    """, (order_number, store_id, customer_id, employee_id,
          sub_total, total_tax, total_discount,
          grand_total, paid_amount, balance_due, payment_method,
          paid_amount, notes, employee_id, employee_id))

    sales_order_id = cur.lastrowid

    for li in line_items:
        cur.execute("""
            INSERT INTO SalesOrderItem
                (SalesOrderId, ProductId, Quantity, UnitPrice,
                 DiscountPercent, DiscountAmount, TaxPercent, TaxAmount,
                 LineTotal, WarrantyDays)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (sales_order_id, li['ProductId'], li['Quantity'], li['UnitPrice'],
              li['DiscountPercent'], li['DiscountAmount'],
              li['TaxPercent'], li['TaxAmount'], li['LineTotal'],
              li['WarrantyDays']))

    if paid_amount >= grand_total:
        order_status = 'COMPLETED'
    else:
        order_status = 'PENDING'
    cur.execute("UPDATE SalesOrder SET Status = ? WHERE SalesOrderId = ?",
                (order_status, sales_order_id))

    for li in line_items:
        record_movement(
            warehouse_id=1,
            product_id=li['ProductId'],
            movement_type='SALE_OUT',
            quantity=-li['Quantity'],
            unit_cost=0,
            reference_type='SalesOrder',
            reference_id=sales_order_id,
            created_by=employee_id,
            _conn=conn,
            product_name=li['ProductName'],
        )

    if paid_amount > 0:
        record_number = f"FR-{uuid.uuid4().hex[:8].upper()}"
        cur.execute("""
            INSERT INTO FinancialRecord
                (RecordNumber, StoreId, RecordDate, RecordType, Category,
                 Amount, PaymentMethod, ReferenceType, ReferenceId, Description, CreatedBy)
            VALUES (?, ?, datetime('now'), 'INCOME', 'مبيعات',
                    ?, ?, 'SalesOrder', ?, ?, ?)
        """, (record_number, store_id, paid_amount, payment_method,
              sales_order_id, f"فاتورة مبيعات #{order_number}", employee_id))

    log_action('SalesOrder', sales_order_id, 'INSERT', employee_id, new_values={
        'OrderNumber': order_number, 'GrandTotal': grand_total, 'Status': order_status
    }, _conn=conn)

    cur.execute("""
        SELECT so.*, c.FullName AS CustomerName, c.Phone AS CustomerPhone,
               e.FullName AS EmployeeName, s.Name AS StoreName
        FROM SalesOrder so
        LEFT JOIN Customer c ON c.CustomerId = so.CustomerId
        LEFT JOIN Employee e ON e.EmployeeId = so.EmployeeId
        LEFT JOIN Store s ON s.StoreId = so.StoreId
        WHERE so.SalesOrderId = ?
    """, (sales_order_id,))
    order = dict(cur.fetchone())

    cur.execute("""
        SELECT soi.*, p.Name AS ProductName, p.SKU
        FROM SalesOrderItem soi
        JOIN Product p ON p.ProductId = soi.ProductId
        WHERE soi.SalesOrderId = ?
    """, (sales_order_id,))
    order['Items'] = [dict(r) for r in cur.fetchall()]

    conn.commit()
    return order


def get_sales_orders(limit=50, status=None, customer_id=None, from_date=None, to_date=None):
    conn = get_db()
    cur = conn.cursor()
    query = """
        SELECT so.*, c.FullName AS CustomerName, e.FullName AS EmployeeName
        FROM SalesOrder so
        LEFT JOIN Customer c ON c.CustomerId = so.CustomerId
        LEFT JOIN Employee e ON e.EmployeeId = so.EmployeeId
        WHERE 1=1
    """
    params = []
    if status:
        statuses = [s.strip() for s in status.split(',')]
        if len(statuses) == 1:
            query += " AND so.Status = ?"
            params.append(statuses[0])
        else:
            placeholders = ','.join('?' * len(statuses))
            query += f" AND so.Status IN ({placeholders})"
            params.extend(statuses)
    if customer_id:
        query += " AND so.CustomerId = ?"
        params.append(customer_id)
    if from_date:
        query += " AND so.OrderDate >= ?"
        params.append(from_date)
    if to_date:
        query += " AND so.OrderDate <= ?"
        params.append(to_date)
    query += " ORDER BY so.CreatedAt DESC LIMIT ?"
    params.append(limit)
    cur.execute(query, params)
    return [dict(r) for r in cur.fetchall()]


def update_sales_order_status(sales_order_id, new_status, employee_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT Status, GrandTotal, PaidAmount, PaymentMethod, OrderNumber, StoreId 
        FROM SalesOrder WHERE SalesOrderId = ? AND IsDeleted = 0
    """, (sales_order_id,))
    order = cur.fetchone()
    if not order:
        conn.close()
        raise ValueError("الفاتورة غير موجودة")

    old_status = order['Status']
    if old_status == new_status:
        conn.close()
        return {"message": "الحالة مطابقة للحالة الحالية", "Status": old_status}

    allowed = ['PENDING', 'COMPLETED', 'DELIVERED', 'RETURNED', 'CANCELLED']
    if new_status not in allowed:
        conn.close()
        raise ValueError("حالة غير صالحة")

    # Get items
    cur.execute("""
        SELECT ProductId, Quantity, UnitPrice FROM SalesOrderItem WHERE SalesOrderId = ?
    """, (sales_order_id,))
    items = cur.fetchall()

    # Determine if we need to adjust stock
    was_active = old_status in ['PENDING', 'COMPLETED', 'DELIVERED', 'PAID', 'PARTIALLY_PAID', 'CONFIRMED']
    is_active = new_status in ['PENDING', 'COMPLETED', 'DELIVERED']

    if was_active and not is_active:
        # Restore stock (add quantity back)
        for item in items:
            record_movement(
                warehouse_id=1,
                product_id=item['ProductId'],
                movement_type='SALE_RETURN',
                quantity=item['Quantity'],
                unit_cost=0,
                reference_type='SalesOrder',
                reference_id=sales_order_id,
                created_by=employee_id,
                _conn=conn
            )
        # Record compensating expense if paid_amount > 0
        if order['PaidAmount'] > 0:
            record_number = f"FR-{uuid.uuid4().hex[:8].upper()}"
            category = 'مرتجع مبيعات' if new_status == 'RETURNED' else 'مبيعات ملغاة'
            cur.execute("""
                INSERT INTO FinancialRecord
                    (RecordNumber, StoreId, RecordDate, RecordType, Category,
                     Amount, PaymentMethod, ReferenceType, ReferenceId, Description, CreatedBy)
                VALUES (?, ?, datetime('now'), 'EXPENSE', ?,
                        ?, ?, 'SalesOrder', ?, ?, ?)
            """, (record_number, order['StoreId'], category,
                  order['PaidAmount'], order['PaymentMethod'],
                  sales_order_id, f"مرتجع/إلغاء فاتورة مبيعات #{order['OrderNumber']}", employee_id))

    elif not was_active and is_active:
        # Deduct stock (check availability first)
        stock_items = [{'ProductId': item['ProductId'], 'Quantity': item['Quantity']} for item in items]
        check_stock_for_sale(1, stock_items)
        
        for item in items:
            record_movement(
                warehouse_id=1,
                product_id=item['ProductId'],
                movement_type='SALE_OUT',
                quantity=-item['Quantity'],
                unit_cost=0,
                reference_type='SalesOrder',
                reference_id=sales_order_id,
                created_by=employee_id,
                _conn=conn
            )
        # Record compensating income
        if order['PaidAmount'] > 0:
            record_number = f"FR-{uuid.uuid4().hex[:8].upper()}"
            cur.execute("""
                INSERT INTO FinancialRecord
                    (RecordNumber, StoreId, RecordDate, RecordType, Category,
                     Amount, PaymentMethod, ReferenceType, ReferenceId, Description, CreatedBy)
                VALUES (?, ?, datetime('now'), 'INCOME', 'مبيعات',
                        ?, ?, 'SalesOrder', ?, ?, ?)
            """, (record_number, order['StoreId'], order['PaidAmount'], order['PaymentMethod'],
                  sales_order_id, f"إعادة تفعيل فاتورة مبيعات #{order['OrderNumber']}", employee_id))

    # Update status in DB
    cur.execute("UPDATE SalesOrder SET Status = ?, UpdatedBy = ?, UpdatedAt = datetime('now') WHERE SalesOrderId = ?",
                (new_status, employee_id, sales_order_id))

    log_action('SalesOrder', sales_order_id, 'UPDATE', employee_id, new_values={
        'Status': new_status
    }, _conn=conn)

    conn.commit()
    conn.close()
    return {"message": "تم تحديث حالة الفاتورة بنجاح", "Status": new_status}
