import time
import functools
from flask import Blueprint, request
from database.connection import get_db
from utils.helpers import json_response, parse_int
from utils.decorators import login_required, require_permission

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

_cache = {}
_CACHE_TTL = 60


def _cached(key, ttl=_CACHE_TTL):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            now = time.time()
            if key in _cache and now - _cache[key]['ts'] < ttl:
                return _cache[key]['data']
            result = f(*args, **kwargs)
            _cache[key] = {'data': result, 'ts': now}
            return result
        return wrapper
    return decorator


@reports_bp.route('/dashboard', methods=['GET'])
@login_required
@require_permission('REPORTS')
@_cached('dashboard')
def dashboard():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COALESCE(SUM(GrandTotal), 0) FROM SalesOrder WHERE Status NOT IN ('DRAFT', 'CANCELLED')")
    total_sales = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(GrandTotal), 0) FROM PurchaseOrder WHERE Status = 'RECEIVED'")
    total_purchases = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM SalesOrder WHERE Status NOT IN ('DRAFT', 'CANCELLED') AND date(OrderDate) = date('now')")
    today_orders = cur.fetchone()[0]

    cur.execute("""
        SELECT COALESCE(SUM(GrandTotal), 0) FROM SalesOrder
        WHERE Status NOT IN ('DRAFT', 'CANCELLED') AND date(OrderDate) = date('now')
    """)
    today_sales = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM RepairOrder WHERE Status NOT IN ('DELIVERED', 'CANCELLED')
    """)
    pending_repairs = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM Inventory i
        JOIN Product p ON p.ProductId = i.ProductId
        WHERE p.IsDeleted = 0 AND i.Quantity <= p.MinStockLevel AND p.MinStockLevel > 0
    """)
    low_stock_items = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM Warranty WHERE Status = 'ACTIVE' AND EndDate >= datetime('now')
    """)
    active_warranties = cur.fetchone()[0]

    cur.execute("""
        SELECT COALESCE(SUM(Amount), 0) FROM FinancialRecord WHERE RecordType = 'EXPENSE' AND IsDeleted = 0
    """)
    total_expenses = cur.fetchone()[0]

    cur.execute("""
        SELECT p.Name, p.SKU, i.Quantity, i.AvailableQuantity,
               (SELECT COALESCE(SUM(GrandTotal), 0) FROM SalesOrderItem soi
                JOIN SalesOrder so ON so.SalesOrderId = soi.SalesOrderId
                WHERE soi.ProductId = p.ProductId AND so.Status = 'PAID') AS TotalSold
        FROM Inventory i
        JOIN Product p ON p.ProductId = i.ProductId
        WHERE p.IsDeleted = 0 AND i.Quantity <= p.MinStockLevel AND p.MinStockLevel > 0
        ORDER BY i.Quantity ASC LIMIT 10
    """)
    low_stock_details = [dict(r) for r in cur.fetchall()]

    conn.close()
    return json_response({
        'TotalSales': total_sales,
        'TotalPurchases': total_purchases,
        'TotalExpenses': total_expenses,
        'NetProfit': total_sales - total_expenses,
        'TodayOrders': today_orders,
        'TodaySales': today_sales,
        'PendingRepairs': pending_repairs,
        'LowStockItems': low_stock_items,
        'ActiveWarranties': active_warranties,
        'LowStockDetails': low_stock_details,
    })


@reports_bp.route('/dashboard/sales-timeline', methods=['GET'])
@login_required
@require_permission('REPORTS')
@_cached('sales_timeline')
def sales_timeline():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT date(OrderDate) AS Date,
               COALESCE(SUM(GrandTotal), 0) AS Total,
               COUNT(*) AS Orders
        FROM SalesOrder
        WHERE Status NOT IN ('DRAFT', 'CANCELLED')
          AND OrderDate >= datetime('now', '-30 days')
        GROUP BY date(OrderDate)
        ORDER BY Date ASC
    """)
    data = [dict(r) for r in cur.fetchall()]
    conn.close()
    return json_response(data)


@reports_bp.route('/sales', methods=['GET'])
@login_required
@require_permission('REPORTS')
def sales_report():
    conn = get_db()
    cur = conn.cursor()
    from_date = request.args.get('FromDate')
    to_date = request.args.get('ToDate')

    query = """
        SELECT date(so.OrderDate) AS Date,
               COUNT(*) AS OrderCount,
               COALESCE(SUM(so.GrandTotal), 0) AS TotalAmount,
               COALESCE(SUM(so.PaidAmount), 0) AS PaidAmount
        FROM SalesOrder so
        WHERE so.Status NOT IN ('DRAFT', 'CANCELLED')
    """
    params = []
    if from_date:
        query += " AND so.OrderDate >= ?"
        params.append(from_date)
    if to_date:
        query += " AND so.OrderDate <= ?"
        params.append(to_date)
    query += " GROUP BY date(so.OrderDate) ORDER BY Date DESC LIMIT 30"
    cur.execute(query, params)
    daily = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT c.FullName, COUNT(*) AS OrderCount,
               COALESCE(SUM(so.GrandTotal), 0) AS TotalSpent
        FROM SalesOrder so
        JOIN Customer c ON c.CustomerId = so.CustomerId
        WHERE so.Status NOT IN ('DRAFT', 'CANCELLED')
        GROUP BY so.CustomerId
        ORDER BY TotalSpent DESC LIMIT 10
    """)
    top_customers = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT p.Name, p.SKU, COUNT(*) AS SoldCount,
               COALESCE(SUM(soi.Quantity), 0) AS TotalQuantity,
               COALESCE(SUM(soi.LineTotal), 0) AS TotalRevenue
        FROM SalesOrderItem soi
        JOIN SalesOrder so ON so.SalesOrderId = soi.SalesOrderId
        JOIN Product p ON p.ProductId = soi.ProductId
        WHERE so.Status NOT IN ('DRAFT', 'CANCELLED')
        GROUP BY soi.ProductId
        ORDER BY TotalQuantity DESC LIMIT 10
    """)
    top_products = [dict(r) for r in cur.fetchall()]

    conn.close()
    return json_response({
        'DailySales': daily,
        'TopCustomers': top_customers,
        'TopProducts': top_products,
    })


@reports_bp.route('/financial', methods=['GET'])
@login_required
@require_permission('REPORTS')
def financial_report():
    from services.accounting_service import get_cash_flow, get_financial_records
    from_date = request.args.get('FromDate')
    to_date = request.args.get('ToDate')
    cash_flow = get_cash_flow(from_date=from_date, to_date=to_date)
    records = get_financial_records(from_date=from_date, to_date=to_date, limit=200)
    return json_response({'Summary': cash_flow, 'Records': records})


@reports_bp.route('/financial', methods=['POST'])
@login_required
@require_permission('REPORTS')
def add_expense():
    from services.accounting_service import record_transaction
    from utils.helpers import error_response, success_response
    from utils.decorators import get_json_body
    from flask import session
    
    data = get_json_body()
    amount = parse_int(data.get('Amount', 0))
    description = data.get('Description', '').strip()
    category = data.get('Category', 'مصاريف عامة').strip()
    
    if not amount or amount <= 0:
        return error_response('المبلغ مطلوب ويجب أن يكون أكبر من الصفر')
    if not description:
        return error_response('وصف المصروف مطلوب')
        
    employee_id = session.get('EmployeeId')
    try:
        record_id = record_transaction(
            store_id=1,
            record_type='EXPENSE',
            category=category,
            amount=amount,
            description=description,
            created_by=employee_id
        )
        return success_response('تم تسجيل المصروف بنجاح', {'FinancialRecordId': record_id})
    except Exception as e:
        return error_response(str(e))
