import uuid

from database.connection import get_db, is_postgres
from services.auth_service import hash_password


def seed_data():
    """Seed initial data only if the Store table is empty."""
    conn = get_db()
    cur  = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM \"Store\"" if is_postgres() else "SELECT COUNT(*) FROM Store")
    count = cur.fetchone()[0]
    if count > 0:
        # Already seeded – nothing to do
        return

    print("[seed] Seeding database with clean initial setup …")

    # -----------------------------------------------------------------
    # 1. Store
    # -----------------------------------------------------------------
    store_uid = str(uuid.uuid4())
    cur.execute(
        'INSERT INTO "Store" ("StoreUid","Code","Name","Phone","Email","Address","TaxNumber") '
        "VALUES (?, 'MAIN', 'الفرع الرئيسي', '0123456789', 'info@computerstore.com', "
        "'شارع الجمهورية', '123456789')",
        (store_uid,)
    )

    # -----------------------------------------------------------------
    # 2. Admin employee
    # -----------------------------------------------------------------
    admin_pwd = hash_password('admin123')
    admin_uid = str(uuid.uuid4())
    cur.execute(
        'INSERT INTO "Employee" ("EmployeeUid","StoreId","EmployeeCode","FullName","Phone","Email","PasswordHash") '
        "VALUES (?, 1, 'ADMIN', 'مدير النظام', '0111111111', 'admin@store.com', ?)",
        (admin_uid, admin_pwd)
    )

    # -----------------------------------------------------------------
    # 3. Roles
    # -----------------------------------------------------------------
    roles = [
        ('Admin',
         '{"SALES_CREATE":true,"SALES_READ":true,"PURCHASE_CREATE":true,"PURCHASE_READ":true,'
         '"INVENTORY_READ":true,"INVENTORY_WRITE":true,"REPAIR_READ":true,"REPAIR_WRITE":true,'
         '"EMPLOYEE_READ":true,"EMPLOYEE_WRITE":true,"REPORTS":true,"SETTINGS":true,'
         '"PRODUCT_READ":true,"PRODUCT_CREATE":true,"PRODUCT_WRITE":true,"PRODUCT_DELETE":true,'
         '"CUSTOMER_READ":true,"CUSTOMER_WRITE":true,"CUSTOMER_DELETE":true,'
         '"SUPPLIER_READ":true,"SUPPLIER_WRITE":true,"SUPPLIER_DELETE":true}'),
        ('Cashier',
         '{"SALES_CREATE":true,"SALES_READ":true,"CUSTOMER_READ":true,"CUSTOMER_WRITE":true,'
         '"INVENTORY_READ":true,"PRODUCT_READ":true}'),
        ('Technician',
         '{"REPAIR_READ":true,"REPAIR_WRITE":true,"INVENTORY_READ":true,'
         '"PRODUCT_READ":true,"CUSTOMER_READ":true}'),
        ('Viewer',
         '{"SALES_READ":true,"INVENTORY_READ":true,"REPAIR_READ":true,'
         '"REPORTS":true,"PRODUCT_READ":true,"CUSTOMER_READ":true}'),
    ]
    for name, permissions in roles:
        cur.execute(
            'INSERT INTO "Role" ("RoleName","Permissions") VALUES (?, ?)',
            (name, permissions)
        )

    cur.execute('INSERT INTO "EmployeeRole" ("EmployeeId","RoleId") VALUES (1, 1)')

    # -----------------------------------------------------------------
    # 4. Categories
    # -----------------------------------------------------------------
    categories = [
        ('HARDWARE',    'أجهزة',            None),
        ('COMPONENTS',  'قطع غيار',          None),
        ('PERIPHERALS', 'ملحقات',            None),
        ('SOFTWARE',    'برمجيات',           None),
        ('NETWORK',     'شبكات',             None),
        ('ACCESSORIES', 'اكسسوارات',         None),
        ('PC',          'أجهزة كمبيوتر',     'HARDWARE'),
        ('LAPTOP',      'لابتوب',            'HARDWARE'),
        ('PRINTER',     'طابعات',            'PERIPHERALS'),
        ('MONITOR',     'شاشات',             'PERIPHERALS'),
        ('CPU',         'معالجات',           'COMPONENTS'),
        ('RAM',         'ذاكرة',             'COMPONENTS'),
        ('STORAGE',     'تخزين',             'COMPONENTS'),
    ]
    for code, name, parent_code in categories:
        parent_id = None
        if parent_code:
            cur.execute('SELECT "CategoryId" FROM "Category" WHERE "Code" = ?', (parent_code,))
            row = cur.fetchone()
            if row:
                parent_id = row[0]
        cur.execute(
            'INSERT INTO "Category" ("Code","Name","ParentCategoryId") VALUES (?, ?, ?)',
            (code, name, parent_id)
        )

    # -----------------------------------------------------------------
    # 5. Brands
    # -----------------------------------------------------------------
    brands = [
        ('INTEL',    'Intel'),
        ('AMD',      'AMD'),
        ('NVIDIA',   'NVIDIA'),
        ('ASUS',     'Asus'),
        ('HP',       'HP'),
        ('DELL',     'Dell'),
        ('LENOVO',   'Lenovo'),
        ('SAMSUNG',  'Samsung'),
        ('KINGSTON', 'Kingston'),
        ('LOGITECH', 'Logitech'),
    ]
    for code, name in brands:
        cur.execute('INSERT INTO "Brand" ("Code","Name") VALUES (?, ?)', (code, name))

    # -----------------------------------------------------------------
    # 6. Tax
    # -----------------------------------------------------------------
    cur.execute(
        'INSERT INTO "Tax" ("Code","Name","Rate") VALUES (?, ?, ?)',
        ('VAT_15', 'ضريبة قيمة مضافة 15%', 15.0)
    )

    # -----------------------------------------------------------------
    # 7. Main warehouse
    # -----------------------------------------------------------------
    cur.execute(
        'INSERT INTO "Warehouse" ("StoreId","Code","Name") VALUES (1, ?, ?)',
        ('MAIN', 'المخزن الرئيسي')
    )

    # -----------------------------------------------------------------
    # 8. Sample customers
    # -----------------------------------------------------------------
    sample_customers = [
        ('CUS-SAMPLE-01', 'أحمد محمد',       '01000000001'),
        ('CUS-SAMPLE-02', 'علي حسن',          '01000000002'),
        ('CUS-SAMPLE-03', 'محمود خالد',       '01000000003'),
        ('CUS-SAMPLE-04', 'محمد عبد الله',    '01000000004'),
        ('CUS-SAMPLE-05', 'كريم سيد',         '01000000005'),
        ('CUS-SAMPLE-06', 'إبراهيم رضا',      '01000000006'),
    ]
    for code, name, phone in sample_customers:
        uid = str(uuid.uuid4())
        cur.execute(
            'INSERT INTO "Customer" ("CustomerUid","CustomerCode","FullName","Phone") '
            'VALUES (?, ?, ?, ?)',
            (uid, code, name, phone)
        )

    conn.commit()
    conn.close()
    print("[seed] Clean initial setup seeded successfully.")
    print("[seed]    Login -> admin@store.com / admin123")
