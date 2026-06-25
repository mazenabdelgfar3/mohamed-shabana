import uuid
from flask import Blueprint, request
from database.connection import get_db
from utils.helpers import json_response, error_response, success_response, parse_int
from utils.decorators import login_required, get_json_body, require_permission

products_bp = Blueprint('products', __name__, url_prefix='/api/products')


@products_bp.route('', methods=['GET'])
@login_required
@require_permission('PRODUCT_READ')
def list_products():
    conn = get_db()
    cur = conn.cursor()
    search = request.args.get('search', '')
    category_id = request.args.get('CategoryId')
    brand_id = request.args.get('BrandId')
    is_active = request.args.get('IsActive')
    include_deleted = request.args.get('include_deleted', '0') == '1'
    page = parse_int(request.args.get('Page', 1))
    page_size = parse_int(request.args.get('PageSize', 50))
    if page < 1: page = 1
    if page_size < 1: page_size = 50
    if page_size > 200: page_size = 200

    where = "WHERE 1=1"
    params = []
    if not include_deleted:
        where += " AND p.IsDeleted = 0"
    if search:
        where += " AND (p.Name LIKE ? OR p.SKU LIKE ? OR p.Barcode LIKE ?)"
        params.extend([f'%{search}%'] * 3)
    if category_id:
        where += " AND p.CategoryId = ?"
        params.append(parse_int(category_id))
    if brand_id:
        where += " AND p.BrandId = ?"
        params.append(parse_int(brand_id))
    if is_active == '1':
        where += " AND p.IsActive = 1"
    elif is_active == '0':
        where += " AND p.IsActive = 0"

    cur.execute(f"SELECT COUNT(*) FROM Product p {where}", params)
    total_count = cur.fetchone()[0]

    query = f"""
        SELECT p.*, c.Name AS CategoryName, b.Name AS BrandName,
               s.CompanyName AS SupplierName, t.Name AS TaxName, t.Rate AS TaxRate
        FROM Product p
        LEFT JOIN Category c ON c.CategoryId = p.CategoryId
        LEFT JOIN Brand b ON b.BrandId = p.BrandId
        LEFT JOIN Supplier s ON s.SupplierId = p.SupplierId
        LEFT JOIN Tax t ON t.TaxId = p.TaxId
        {where}
        ORDER BY p.Name ASC
        LIMIT ? OFFSET ?
    """
    offset = (page - 1) * page_size
    cur.execute(query, params + [page_size, offset])
    products = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response({'value': products, 'Count': total_count, 'Page': page, 'PageSize': page_size})


@products_bp.route('/<int:product_id>', methods=['GET'])
@login_required
@require_permission('PRODUCT_READ')
def get_product(product_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.*, c.Name AS CategoryName, b.Name AS BrandName,
               s.CompanyName AS SupplierName, t.Name AS TaxName, t.Rate AS TaxRate
        FROM Product p
        LEFT JOIN Category c ON c.CategoryId = p.CategoryId
        LEFT JOIN Brand b ON b.BrandId = p.BrandId
        LEFT JOIN Supplier s ON s.SupplierId = p.SupplierId
        LEFT JOIN Tax t ON t.TaxId = p.TaxId
        WHERE p.ProductId = ?
    """, (product_id,))
    product = cur.fetchone()
    conn.close()
    if not product:
        return error_response('المنتج غير موجود', 404)
    return json_response(dict(product))


@products_bp.route('', methods=['POST'])
@login_required
@require_permission('PRODUCT_CREATE')
def create_product():
    data = get_json_body()
    required = ['SKU', 'Name', 'SellingPrice']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return error_response(f'الحقول مطلوبة: {", ".join(missing)}')

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT ProductId FROM Product WHERE SKU = ?", (data['SKU'],))
    if cur.fetchone():
        conn.close()
        return error_response('SKU موجود بالفعل')

    barcode = data.get('Barcode')
    if barcode:
        cur.execute("SELECT ProductId FROM Product WHERE Barcode = ?", (barcode,))
        if cur.fetchone():
            conn.close()
            return error_response('الباركود موجود بالفعل')

    pid = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO Product
            (ProductUid, CategoryId, BrandId, SupplierId, TaxId,
             SKU, Name, Description, UnitOfMeasure, Barcode,
             CostPrice, SellingPrice, WarrantyDays, HasSerialNumbers,
             MinStockLevel, MaxStockLevel, IsActive)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (pid,
          parse_int(data.get('CategoryId')) or None,
          parse_int(data.get('BrandId')) or None,
          parse_int(data.get('SupplierId')) or None,
          parse_int(data.get('TaxId')) or None,
          data['SKU'], data['Name'], data.get('Description'),
          data.get('UnitOfMeasure', 'Piece'),
          barcode,
          parse_int(data.get('CostPrice', 0)),
          parse_int(data['SellingPrice']),
          parse_int(data.get('WarrantyDays', 0)),
          1 if data.get('HasSerialNumbers') else 0,
          parse_int(data.get('MinStockLevel', 0)),
          parse_int(data.get('MaxStockLevel', 0))))

    product_id = cur.lastrowid
    conn.commit()
    conn.close()
    return success_response('تم إنشاء المنتج', {'ProductId': product_id}, 201)


@products_bp.route('/<int:product_id>', methods=['PUT'])
@login_required
@require_permission('PRODUCT_WRITE')
def update_product(product_id):
    data = get_json_body()
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT ProductId FROM Product WHERE ProductId = ?", (product_id,))
    if not cur.fetchone():
        conn.close()
        return error_response('المنتج غير موجود', 404)

    fields = ['CategoryId', 'BrandId', 'SupplierId', 'TaxId', 'SKU', 'Name',
              'Description', 'UnitOfMeasure', 'Barcode', 'CostPrice',
              'SellingPrice', 'WarrantyDays', 'MinStockLevel', 'MaxStockLevel',
              'IsActive']
    updates = []
    params = []
    for f in fields:
        if f in data:
            if f in ('CategoryId', 'BrandId', 'SupplierId', 'TaxId',
                     'CostPrice', 'SellingPrice', 'WarrantyDays',
                     'MinStockLevel', 'MaxStockLevel'):
                val = parse_int(data[f]) or 0 if data[f] else None
            elif f == 'IsActive':
                val = 1 if data[f] else 0
            else:
                val = data[f]
            updates.append(f"{f} = ?")
            params.append(val)

    if updates:
        updates.append("UpdatedAt = datetime('now')")
        cur.execute(f"UPDATE Product SET {', '.join(updates)} WHERE ProductId = ?",
                    params + [product_id])
        conn.commit()

    conn.close()
    return success_response('تم تحديث المنتج')


@products_bp.route('/<int:product_id>', methods=['DELETE'])
@login_required
@require_permission('PRODUCT_DELETE')
def delete_product(product_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE Product SET IsDeleted = 1, UpdatedAt = datetime('now') WHERE ProductId = ?",
                (product_id,))
    conn.commit()
    conn.close()
    return success_response('تم حذف المنتج')


@products_bp.route('/categories', methods=['GET'])
@login_required
@require_permission('PRODUCT_READ')
def list_categories():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.*, p.Name AS ParentName
        FROM Category c
        LEFT JOIN Category p ON p.CategoryId = c.ParentCategoryId
        WHERE c.IsDeleted = 0
        ORDER BY c.Name ASC
    """)
    categories = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response(categories)


@products_bp.route('/brands', methods=['GET'])
@login_required
@require_permission('PRODUCT_READ')
def list_brands():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Brand WHERE IsDeleted = 0 ORDER BY Name ASC")
    brands = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response(brands)


@products_bp.route('/taxes', methods=['GET'])
@login_required
@require_permission('PRODUCT_READ')
def list_taxes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Tax WHERE IsActive = 1")
    taxes = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response(taxes)
