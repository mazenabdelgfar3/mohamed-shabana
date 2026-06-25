/* Computer Store ERP - Integrated with HTML Template */
const API = '/api';
let state = { user: null, permissions: {}, page: 'dashboard', cart: [] };
let prodPage = 1, prodCatFilter = '', prodStatusFilter = '', prodSearchQ = '';
let _debounceTimers = {};

async function apiGet(path) {
  const r = await fetch(`${API}${path}`, { credentials: 'same-origin' });
  if (!r.ok) { const e = await r.json(); throw new Error(e.error || 'خطأ في الاتصال'); }
  return r.json();
}
async function apiPost(path, body) {
  const r = await fetch(`${API}${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), credentials: 'same-origin' });
  if (!r.ok) {
    let msg = 'خطأ في الخادم - يرجى المحاولة مرة أخرى';
    try { const e = await r.json(); if (e && e.error) msg = e.error; } catch (_) {}
    throw new Error(msg);
  }
  return r.json();
}
async function apiPut(path, body) {
  const r = await fetch(`${API}${path}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), credentials: 'same-origin' });
  if (!r.ok) {
    let msg = 'خطأ في الخادم - يرجى المحاولة مرة أخرى';
    try { const e = await r.json(); if (e && e.error) msg = e.error; } catch (_) {}
    throw new Error(msg);
  }
  return r.json();
}
async function apiDelete(path) {
  const r = await fetch(`${API}${path}`, { method: 'DELETE', credentials: 'same-origin' });
  if (!r.ok) {
    let msg = 'خطأ في الخادم - يرجى المحاولة مرة أخرى';
    try { const e = await r.json(); if (e && e.error) msg = e.error; } catch (_) {}
    throw new Error(msg);
  }
  return r.json();
}

function fmtMoney(c) { return (Number(c) || 0).toLocaleString('ar-EG') + ' ج.م'; }
function fmtDate(d) { if (!d) return '-'; try { return new Date(d).toLocaleDateString('ar-EG'); } catch (_) { return d; } }
function statusBadge(s) {
  const colors = {
    PAID: '#28a745', DRAFT: '#6c757d', CANCELLED: '#dc3545',
    RECEIVED: '#ff8c00', PENDING: '#ffc107', ACTIVE: '#17a2b8',
    EXPIRED: '#dc3545', CASH: '#28a745', CARD: '#17a2b8', TRANSFER: '#ffc107',
    COMPLETED: '#2d6a4f', UNREPAIRABLE: '#dc3545', DELIVERED: '#28a745', RETURNED: '#fd7e14',
    DIAGNOSING: '#17a2b8', IN_PROGRESS: '#007bff', INCOME: '#28a745', EXPENSE: '#dc3545',
    STOPPED: '#6c757d'
  };
  const labels = {
    PAID: 'مدفوع', DRAFT: 'مسودة', CANCELLED: '❌ ملغي',
    RECEIVED: 'تم الاستلام', PENDING: '⏳ قيد التنفيذ', ACTIVE: 'نشط',
    EXPIRED: 'منتهي', CASH: 'نقدي', CARD: 'بطاقة', TRANSFER: 'تحويل', INSTAPAY: 'انستا باي',
    COMPLETED: '✔️ تم الانتهاء', UNREPAIRABLE: 'تعذر الإصلاح', DELIVERED: '✅ تم التسليم',
    RETURNED: '↩️ مرتجع',
    DIAGNOSING: 'تحت التشخيص', IN_PROGRESS: 'تحت الإصلاح', INCOME: 'إيراد', EXPENSE: 'مصروف',
    STOPPED: '⛔ موقوف'
  };
  return `<span style="background:${colors[s]||'#6c757d'};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px">${labels[s]||s}</span>`;
}


function showToast(msg, type) {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = msg;
  el.style.background = type === 'error' ? '#dc3545' : type === 'info' ? '#17a2b8' : '#28a745';
  el.style.display = 'block'; el.style.opacity = '1';
  setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.style.display = 'none', 300); }, 3000);
}

function openModal(html) {
  document.getElementById('modalBody').innerHTML = html;
  document.getElementById('modalOverlay').style.display = 'flex';
}
function closeModal() {
  document.getElementById('modalOverlay').style.display = 'none';
}

function skeletonCards(count) {
  return '<div class="skeleton-grid">' + Array(count).fill('<div class="skeleton skeleton-card"></div>').join('') + '</div>';
}
function skeletonRows(count) {
  return Array(count).fill('<div class="skeleton skeleton-row"></div>').join('');
}

// ============ NAVIGATION ============
function navigate(page) {
  state.page = page;
  if (page === 'login') {
    document.getElementById('loginPage').style.display = 'flex';
    document.getElementById('appContainer').style.display = 'none';
    return;
  }
  document.getElementById('loginPage').style.display = 'none';
  document.getElementById('appContainer').style.display = '';

  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const target = document.getElementById('page-' + page);
  if (target) target.classList.add('active');

  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelector(`.nav-item[data-page="${page}"]`)?.classList.add('active');

  renderPageContent(page);
}

async function renderPageContent(page) {
  switch (page) {
    case 'dashboard': renderDashboard(); break;
    case 'sales': renderSales(); break;
    case 'products': renderProducts(); break;
    case 'inventory': renderInventory(); break;
    case 'customers': renderCustomers(); break;
    case 'suppliers': renderSuppliers(); break;
    case 'purchases': renderPurchases(); break;
    case 'repairs': renderRepairs(); break;
    case 'reports': renderReports(); break;
    case 'expenses': renderExpensesPage(); break;
  }
}

// ============ AUTH ============
async function handleLogin(e) {
  e.preventDefault();
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;
  const errEl = document.getElementById('loginError');
  errEl.style.display = 'none';
  try {
    const res = await apiPost('/auth/login', { Email: email, Password: password });
    state.user = res.employee;
    state.permissions = res.permissions || {};
    document.getElementById('userName').textContent = state.user?.FullName || '';
    document.getElementById('statusUser').textContent = state.user?.FullName || '';
    navigate('dashboard');
  } catch (err) {
    errEl.textContent = err.message;
    errEl.style.display = 'block';
  }
}

async function handleLogout() {
  try { await apiPost('/auth/logout', {}); } catch (_) {}
  state.user = null; state.permissions = {};
  navigate('login');
}

async function checkAuth() {
  try {
    const res = await apiGet('/auth/me');
    state.user = { EmployeeId: res.EmployeeId, FullName: res.FullName, Email: res.Email };
    state.permissions = res.Permissions || {};
    document.getElementById('userName').textContent = state.user?.FullName || '';
    document.getElementById('statusUser').textContent = state.user?.FullName || '';
    navigate('dashboard');
  } catch (_) {
    navigate('login');
  }
}

// ============ DASHBOARD ============
async function renderDashboard() {
  const container = document.getElementById('dashCards');
  if (!container) return;
  container.innerHTML = skeletonCards(9);

  try {
    const d = await apiGet('/reports/dashboard');
    container.innerHTML = `
      <div class="stat-card"><div class="value">${fmtMoney(d.TotalSales)}</div><div class="label">إجمالي المبيعات (دخل)</div></div>
      <div class="stat-card"><div class="value">${fmtMoney(d.TotalPurchases)}</div><div class="label">إجمالي المشتريات</div></div>
      <div class="stat-card"><div class="value" style="color:var(--danger)">${fmtMoney(d.TotalExpenses)}</div><div class="label">إجمالي المصروفات</div></div>
      <div class="stat-card"><div class="value" style="color:${d.NetProfit >= 0 ? 'var(--success)' : 'var(--danger)'};font-weight:bold">${fmtMoney(d.NetProfit)}</div><div class="label">صافي الأرباح</div></div>
      <div class="stat-card"><div class="value">${d.TodayOrders}</div><div class="label">طلبات اليوم</div></div>
      <div class="stat-card"><div class="value">${fmtMoney(d.TodaySales)}</div><div class="label">مبيعات اليوم</div></div>
      <div class="stat-card"><div class="value">${d.PendingRepairs}</div><div class="label">صيانات معلقة</div></div>
      <div class="stat-card"><div class="value" style="color:${d.LowStockItems > 0 ? 'var(--danger)' : 'var(--success)'}">${d.LowStockItems}</div><div class="label">مخزون منخفض</div></div>
      <div class="stat-card"><div class="value">${d.ActiveWarranties}</div><div class="label">ضمانات نشطة</div></div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="empty-state"><div class="icon">⚠</div><h3>فشل التحميل</h3><p>${err.message}</p><button class="btn btn-primary" onclick="renderDashboard()">إعادة المحاولة</button></div>`;
  }

  // Sales chart
  const chartBody = document.getElementById('chartBody');
  if (chartBody) {
    chartBody.innerHTML = '<div class="skeleton skeleton-chart"></div>';
    try {
      const timeline = await apiGet('/reports/dashboard/sales-timeline');
      if (timeline.length === 0) {
        chartBody.innerHTML = '<div class="chart-empty"><i class="fas fa-chart-line" style="font-size:32px;opacity:0.4;margin-bottom:8px;display:block"></i> لم يتم تسجيل أي مبيعات في آخر 30 يوم<br><small>قم بإجراء أول عملية بيع لبدء ظهور البيانات</small></div>';
      } else {
        const maxVal = Math.max(...timeline.map(t => t.Total), 1);
        chartBody.innerHTML = '<div class="chart-bar-group">' +
          timeline.map(t => {
            const h = Math.max(4, (t.Total / maxVal) * 160);
            const date = t.Date.slice(5);
            return `<div class="chart-bar-wrapper"><div class="chart-bar" style="height:${h}px" title="${t.Date}: ${fmtMoney(t.Total)}"></div><div class="chart-bar-label">${date}</div></div>`;
          }).join('') + '</div>';
      }
    } catch (_) {
      chartBody.innerHTML = '<div class="chart-empty">تعذر تحميل الرسم البياني</div>';
    }
  }

  // Low stock warning
  if (d && d.LowStockItems > 0) {
    showToast(`⚠ يوجد ${d.LowStockItems} منتجات منخفضة المخزون`, 'info');
  }
}

// ============ POS SALES ============
let posProducts = [];
let posCustomers = [];
async function renderSales() {
  state.cart = [];
  try {
    const r = await apiGet('/products?include_deleted=0&PageSize=200');
    posProducts = r.value || r;
    posCustomers = await apiGet('/customers');
  } catch (_) { posProducts = []; posCustomers = []; }

  const phoneInput = document.getElementById('posCustomerPhone');
  const nameInput = document.getElementById('posCustomerName');
  if (phoneInput) { phoneInput.value = ''; phoneInput.readOnly = false; }
  if (nameInput) { nameInput.value = ''; nameInput.readOnly = false; }

  const listEl = document.getElementById('posPhoneList');
  if (listEl) {
    listEl.innerHTML = posCustomers.filter(c => c.Phone).map(c => `<option value="${c.Phone}">${c.FullName}</option>`).join('');
  }

  renderProductGrid();
  renderCartTable();
  updateTotals();
  loadRecentOrders();
  loadInvoiceNumber();
  renderSalesHistory();
}

window.onPOSPhoneKeyup = function(val) {
  const c = posCustomers.find(cust => cust.Phone && cust.Phone.trim() === val.trim());
  const nameInput = document.getElementById('posCustomerName');
  if (c && nameInput) {
    nameInput.value = c.FullName;
    nameInput.readOnly = true;
  } else if (nameInput) {
    nameInput.readOnly = false;
  }
};

window.onPOSPhoneChange = function(val) {
  onPOSPhoneKeyup(val);
};

window.switchSalesTab = function(tab, el) {
  document.querySelectorAll('#page-sales .inventory-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('#page-sales .inventory-tab-content').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
  if (tab === 'pos') {
    document.getElementById('salesTab-pos').classList.add('active');
  } else {
    document.getElementById('salesTab-history').classList.add('active');
    renderSalesHistory();
  }
};

let allSalesOrders = [];
async function renderSalesHistory() {
  const tbody = document.getElementById('salesHistoryBody');
  if (!tbody) return;
  tbody.innerHTML = skeletonRows(5);
  try {
    allSalesOrders = await apiGet('/sales/orders?limit=100');
    displaySalesHistory(allSalesOrders);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:40px;color:var(--danger)"><i class="fas fa-exclamation-triangle" style="font-size:32px;margin-bottom:8px;display:block"></i>${err.message}</td></tr>`;
  }
}

function displaySalesHistory(orders) {
  const tbody = document.getElementById('salesHistoryBody');
  if (!tbody) return;
  if (orders.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:40px">لا توجد فواتير مبيعات بعد</td></tr>';
    return;
  }
  tbody.innerHTML = orders.map(o => {
    const dt = new Date(o.OrderDate || o.CreatedAt);
    const dateStr = dt.toLocaleDateString('ar-EG');
    
    const statusOptions = [
      { val: 'PENDING', label: '⏳ قيد التنفيذ' },
      { val: 'COMPLETED', label: '✔️ تم الانتهاء' },
      { val: 'DELIVERED', label: '✅ تم التسليم' },
      { val: 'RETURNED', label: '↩️ مرتجع' },
      { val: 'CANCELLED', label: '❌ ملغي' }
    ];
    
    const selectHtml = `
      <select class="filter-select" style="padding:2px 4px;font-size:11px;margin-left:5px;width:120px" onchange="changeSalesOrderStatus(${o.SalesOrderId}, this.value)">
        ${statusOptions.map(opt => `<option value="${opt.val}" ${o.Status === opt.val ? 'selected' : ''}>${opt.label}</option>`).join('')}
      </select>
    `;

    return `
      <tr>
        <td>${o.OrderNumber}</td>
        <td>${o.CustomerName || 'عميل نقدي'}</td>
        <td>${dateStr}</td>
        <td>${fmtMoney(o.GrandTotal)}</td>
        <td>${fmtMoney(o.PaidAmount)}</td>
        <td>${statusBadge(o.Status)}</td>
        <td>
          <div style="display:flex;align-items:center;gap:5px">
            ${selectHtml}
            <button class="btn btn-sm btn-primary" onclick="viewSalesInvoice(${o.SalesOrderId})" title="عرض / طباعة"><i class="fas fa-print"></i></button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

window.filterSalesHistory = function(q) {
  if (!q) { displaySalesHistory(allSalesOrders); return; }
  const filtered = allSalesOrders.filter(o => 
    o.OrderNumber.toLowerCase().includes(q.toLowerCase()) || 
    (o.CustomerName && o.CustomerName.toLowerCase().includes(q.toLowerCase()))
  );
  displaySalesHistory(filtered);
};

window.changeSalesOrderStatus = async function(orderId, status) {
  try {
    await apiPut(`/sales/orders/${orderId}/status`, { Status: status });
    showToast('✅ تم تحديث حالة الفاتورة بنجاح');
    renderSalesHistory();
  } catch (err) {
    showToast('❌ ' + err.message, 'error');
    renderSalesHistory();
  }
};

window.viewSalesInvoice = async function(orderId) {
  try {
    const order = await apiGet(`/sales/orders/${orderId}`);
    showInvoiceModal(order);
  } catch (err) { showToast('❌ ' + err.message, 'error'); }
};

async function loadInvoiceNumber() {
  try {
    const orders = await apiGet('/sales/orders?limit=1');
    const num = orders.length ? 'SALES-' + String(orders[0].SalesOrderId + 1).padStart(6, '0') : 'SALES-000001';
    document.getElementById('invoiceNumber').textContent = num;
  } catch (_) { document.getElementById('invoiceNumber').textContent = 'SALES-000001'; }
}

function renderProductGrid() {
  const grid = document.getElementById('productGrid');
  if (!grid) return;
  if (posProducts.length === 0) {
    grid.innerHTML = '<div class="empty-state" style="padding:20px"><p>لا توجد منتجات متاحة<br><small>أضف منتجاً أولاً من قسم المنتجات</small></p></div>';
    return;
  }
  grid.innerHTML = posProducts.map(p => `
    <div class="product-card" onclick="addToCart(${p.ProductId}, '${p.Name.replace(/'/g, "\\'")}', ${p.SellingPrice})">
      <div class="product-name">${p.Name}</div>
      <div class="product-price">${fmtMoney(p.SellingPrice)}</div>
    </div>
  `).join('');
}

window.filterPOSProducts = function(val) {
  const q = (val || '').toLowerCase();
  document.querySelectorAll('.product-card').forEach(card => {
    card.style.display = card.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
  const visible = document.querySelectorAll('.product-card[style*="display: none"]').length;
  const total = document.querySelectorAll('.product-card').length;
  if (visible === total && total > 0) {
    // all hidden - show message?
  }
};

window.addToCart = function(id, name, price) {
  const existing = state.cart.find(c => c.ProductId === id);
  if (existing) { existing.Quantity++; }
  else { state.cart.push({ ProductId: id, Name: name, UnitPrice: price, Quantity: 1, DiscountPercent: 0 }); }
  renderCartTable();
  updateTotals();
};

window.removeFromCart = function(index) {
  state.cart.splice(index, 1);
  renderCartTable();
  updateTotals();
};

function renderCartTable() {
  const tbody = document.getElementById('cartBody');
  const count = document.getElementById('cartCount');
  if (!tbody) return;
  if (!state.cart.length) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:40px;color:var(--gray)"><i class="fas fa-shopping-cart" style="font-size:32px;opacity:0.3;margin-bottom:8px;display:block"></i>السلة فارغة<br><small>اختر المنتجات من الشبكة أعلاه</small></td></tr>';
    if (count) count.textContent = '0 منتجات';
    return;
  }
  tbody.innerHTML = state.cart.map((item, i) => `
    <tr>
      <td>${i + 1}</td>
      <td>${item.Name}</td>
      <td>${fmtMoney(item.UnitPrice)}</td>
      <td><input type="number" min="1" value="${item.Quantity}" style="width:60px;text-align:center" onchange="updateCartQty(${i}, this.value)"></td>
      <td>${fmtMoney(item.Quantity * item.UnitPrice)}</td>
      <td><button class="btn btn-danger btn-sm" onclick="removeFromCart(${i})"><i class="fas fa-trash"></i></button></td>
    </tr>
  `).join('');
  if (count) count.textContent = state.cart.reduce((s, c) => s + c.Quantity, 0) + ' منتجات';
}

window.updateCartQty = function(index, val) {
  const qty = parseInt(val) || 1;
  if (state.cart[index]) { state.cart[index].Quantity = Math.max(1, qty); }
  renderCartTable();
  updateTotals();
};

window.updateTotal = function() { updateTotals(); };

function updateTotals() {
  const totalEl = document.getElementById('totalAmount');
  const taxEl = document.getElementById('taxAmount');
  const netEl = document.getElementById('netAmount');
  const discEl = document.getElementById('discountInput');
  if (!totalEl) return;
  const subTotal = state.cart.reduce((s, c) => s + c.Quantity * c.UnitPrice, 0);
  const discount = parseInt(discEl?.value || 0);
  const net = Math.max(0, subTotal - discount);
  if (totalEl) totalEl.textContent = fmtMoney(net);
  if (taxEl) taxEl.textContent = fmtMoney(0);
  if (netEl) netEl.textContent = fmtMoney(net);
}

window.showPaymentModal = function() {
  if (!state.cart.length) { showToast('⚠ السلة فارغة، أضف منتجات أولاً', 'error'); return; }
  const discEl = document.getElementById('discountInput');
  const subTotal = state.cart.reduce((s, c) => s + c.Quantity * c.UnitPrice, 0);
  const discount = parseInt(discEl?.value || 0);
  const net = Math.max(0, subTotal - discount);
  openModal(`
    <div style="width:420px">
      <h3 style="margin:0 0 16px;font-size:18px">إتمام عملية البيع</h3>
      <div style="background:var(--card-bg);padding:16px;border-radius:8px;margin-bottom:16px">
        <div style="display:flex;justify-content:space-between;margin-bottom:8px"><span>الإجمالي بعد الخصم</span><span>${fmtMoney(net)} ج.م</span></div>
        <div style="display:flex;justify-content:space-between;font-size:18px;font-weight:bold;color:var(--success);border-top:2px solid var(--border);padding-top:8px"><span>المطلوب</span><span>${fmtMoney(net)} ج.م</span></div>
      </div>
      <div class="form-group"><label>نقداً</label>
        <input type="number" id="pm-cash" value="${net}" class="form-control" oninput="calcPaymentChange()">
      </div>
      <div class="form-group"><label>بطاقة</label>
        <input type="number" id="pm-card" value="0" class="form-control" oninput="calcPaymentChange()">
      </div>
      <div class="form-group"><label>انستا باي</label>
        <input type="number" id="pm-insta" value="0" class="form-control" oninput="calcPaymentChange()">
      </div>
      <div style="display:flex;justify-content:space-between;padding:8px 0;font-size:16px">
        <span>المدفوع: <strong id="pm-paid">${fmtMoney(net)}</strong> ج.م</span>
        <span>المتبقي: <strong id="pm-remaining" style="color:var(--success)">0</strong> ج.م</span>
      </div>
      <div class="modal-actions" style="margin-top:16px">
        <button type="button" class="btn btn-outline" onclick="closeModal()">إلغاء</button>
        <button type="button" class="btn btn-success btn-lg" onclick="completeSale()"><i class="fas fa-check-circle"></i> تأكيد البيع</button>
      </div>
    </div>
  `);
};

window.calcPaymentChange = function() {
  const discEl = document.getElementById('discountInput');
  const sub = state.cart.reduce((s, c) => s + c.Quantity * c.UnitPrice, 0);
  const disc = parseInt(discEl?.value || 0);
  const net = Math.max(0, sub - disc);
  const cash = parseInt(document.getElementById('pm-cash')?.value || 0);
  const card = parseInt(document.getElementById('pm-card')?.value || 0);
  const insta = parseInt(document.getElementById('pm-insta')?.value || 0);
  const paid = cash + card + insta;
  document.getElementById('pm-paid').textContent = fmtMoney(paid);
  const rem = Math.max(0, net - paid);
  const el = document.getElementById('pm-remaining');
  el.textContent = fmtMoney(rem);
  el.style.color = rem > 0 ? 'var(--danger)' : 'var(--success)';
};

window.completeSale = async function() {
  if (!state.cart.length) { showToast('⚠ السلة فارغة', 'error'); return; }
  const discEl = document.getElementById('discountInput');
  const subTotal = state.cart.reduce((s, c) => s + c.Quantity * c.UnitPrice, 0);
  const discount = parseInt(discEl?.value || 0);
  const net = Math.max(0, subTotal - discount);
  const cash = parseInt(document.getElementById('pm-cash')?.value || 0);
  const card = parseInt(document.getElementById('pm-card')?.value || 0);
  const insta = parseInt(document.getElementById('pm-insta')?.value || 0);
  const paidAmount = cash + card + insta;
  if (paidAmount <= 0) { showToast('⚠ يجب إدخال مبلغ الدفع', 'error'); return; }
  const customerPhone = document.getElementById('posCustomerPhone')?.value || '';
  const customerName = document.getElementById('posCustomerName')?.value || '';
  const methods = [];
  if (cash > 0) methods.push('cash');
  if (card > 0) methods.push('card');
  if (insta > 0) methods.push('instapay');
  let paymentMethod, paymentNotes;
  if (methods.length === 1) {
    paymentMethod = methods[0].toUpperCase();
    paymentNotes = '';
  } else {
    paymentMethod = 'SPLIT';
    const obj = {};
    if (cash > 0) obj.cash = cash;
    if (card > 0) obj.card = card;
    if (insta > 0) obj.instapay = insta;
    paymentNotes = JSON.stringify(obj);
  }
  try {
    const r = await apiPost('/sales/orders', {
      StoreId: 1,
      CustomerPhone: customerPhone.trim(),
      CustomerName: customerName.trim(),
      Items: state.cart.map(c => ({ ProductId: c.ProductId, Quantity: c.Quantity, UnitPrice: c.UnitPrice, DiscountPercent: c.DiscountPercent || 0 })),
      PaymentMethod: paymentMethod, PaidAmount: paidAmount,
      Notes: paymentNotes || '',
    });
    closeModal();
    state.cart = []; renderCartTable(); updateTotals();
    loadRecentOrders(); loadInvoiceNumber();
    showInvoiceModal(r.data || r);
    try { posCustomers = await apiGet('/customers'); } catch (_) {}
  } catch (err) { showToast('❌ ' + err.message, 'error'); }
};

function showInvoiceModal(order) {
  const items = order.Items || [];
    let cash = 0, card = 0, insta = 0;
  if (order.PaymentMethod === 'SPLIT') {
    try { const p = JSON.parse(order.Notes); cash = p.cash || 0; card = p.card || 0; insta = p.instapay || 0; } catch (_) {}
  }
  if (!cash && !card && !insta) {
    if (order.PaymentMethod === 'CARD') card = order.PaidAmount;
    else if (order.PaymentMethod === 'INSTAPAY') insta = order.PaidAmount;
    else cash = order.PaidAmount;
  }
  const payLabel = order.PaymentMethod === 'SPLIT'
    ? ['نقداً', card > 0 && 'بطاقة', insta > 0 && 'انستا باي'].filter(Boolean).join(' + ')
    : order.PaymentMethod === 'CASH' ? 'نقداً'
    : order.PaymentMethod === 'INSTAPAY' ? 'انستا باي'
    : 'بطاقة';
  const dt = new Date(order.OrderDate || order.CreatedAt);
  const dateStr = dt.toLocaleDateString('ar-EG');
  const timeStr = dt.toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' });
  const bal = (order.GrandTotal || 0) - (order.PaidAmount || 0);
  
  openModal(`
    <div style="width:620px;font-family:'Segoe UI',system-ui,sans-serif;line-height:1.6;background:#fff;padding:15px;color:#000" id="invoice-${order.SalesOrderId}">
      <!-- HEADER -->
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;padding-bottom:10px;border-bottom:1px solid #000">
        <!-- Left: Serial No -->
        <div style="color:#d32f2f;font-family:'Courier New',monospace;font-size:18px;font-weight:bold;display:flex;align-items:center;gap:4px">
          <span style="font-size:14px">No.</span>
          <span>${String(order.SalesOrderId).padStart(6, '0')}</span>
        </div>
        
        <!-- Center: Title & Owner -->
        <div style="text-align:center">
          <div style="font-size:32px;font-weight:bold;font-family:'Times New Roman',serif;margin-bottom:2px;letter-spacing:1px">فــاتــورة</div>
          <div style="font-size:18px;font-weight:bold;color:#000">م/محمد شبانة</div>
          <div style="font-size:11px;color:#475569">لصيانة وبيع أجهزة الكمبيوتر والطابعات</div>
        </div>
        
        <!-- Right: Date in Pill Shape -->
        <div style="border:2px solid #000;border-radius:20px;padding:6px 16px;font-size:12px;font-weight:bold;text-align:center;min-width:140px">
          تحريراً في: ${dateStr}
        </div>
      </div>

      <!-- CLIENT INFO (DOTTED LINE STYLE) -->
      <div style="display:flex;align-items:center;font-size:14px;font-weight:bold;margin-bottom:20px;width:100%">
        <span style="white-space:nowrap;margin-left:8px">من السيد:</span>
        <div style="border-bottom:1px dotted #000;flex-grow:1;padding:0 10px;font-size:15px;font-weight:normal;text-align:right">
          ${order.CustomerName || 'عميل نقدي'} ${order.CustomerPhone ? ' - ' + order.CustomerPhone : ''}
        </div>
      </div>

      <!-- ITEMS TABLE -->
      <table style="width:100%;border-collapse:collapse;border:2px solid #000;font-size:13px">
        <thead>
          <tr style="border-bottom:2px solid #000;background:#f8fafc">
            <th style="border-left:2px solid #000;padding:10px 8px;text-align:right;font-weight:bold;font-size:14px">البيان / Description</th>
            <th style="border-left:2px solid #000;padding:10px 8px;text-align:center;width:120px;font-weight:bold;font-size:14px">سعر الوحدة / Unit Price</th>
            <th style="padding:10px 8px;text-align:center;width:120px;font-weight:bold;font-size:14px">الإجمالي / Total</th>
          </tr>
        </thead>
        <tbody>
          ${items.map(item => `
            <tr style="border-bottom:1px solid #000;height:38px">
              <td style="border-left:2px solid #000;padding:8px;text-align:right;font-size:13px">
                ${item.ProductName || 'منتج'} ${item.Quantity > 1 ? ` (الكمية: ${item.Quantity})` : ''}
              </td>
              <td style="border-left:2px solid #000;padding:8px;text-align:center;font-size:13px">
                ${fmtMoney(item.UnitPrice)}
              </td>
              <td style="padding:8px;text-align:center;font-weight:bold;font-size:13px">
                ${fmtMoney(item.LineTotal)}
              </td>
            </tr>
          `).join('')}
          
          <!-- Pad with empty rows to match booklet style -->
          ${Array.from({ length: Math.max(0, 5 - items.length) }).map(() => `
            <tr style="border-bottom:1px solid #000;height:38px">
              <td style="border-left:2px solid #000"></td>
              <td style="border-left:2px solid #000"></td>
              <td></td>
            </tr>
          `).join('')}
        </tbody>
      </table>

      <!-- TOTALS BLOCK -->
      <div style="border:2px solid #000;border-top:none;padding:10px;display:flex;justify-content:space-between;align-items:center;font-weight:bold;font-size:13px;background:#f8fafc">
        <span>فقط وقدره: <span style="font-weight:normal;text-decoration:underline">${fmtMoney(order.GrandTotal)} جنيهاً مصرياً لا غير</span></span>
        <span style="font-size:12px;color:#475569">Only</span>
      </div>

      <!-- SIGNATURES AND SIGN-OFF -->
      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:35px;font-weight:bold;font-size:13px;padding:0 10px">
        <div>يعتمد: .......................................</div>
        <div style="font-size:11px;font-weight:normal;color:#64748b">نظام CompuManager ERP v1.0</div>
      </div>

      <!-- DEVELOPER CREDIT -->
      <div style="text-align:center;margin-top:35px;font-size:10px;color:#94a3b8;font-family:monospace;letter-spacing:0.5px">
        mazen abdelgfar - 01022234967
      </div>

      <div class="modal-actions no-print" style="margin-top:14px">
        <button class="btn btn-primary" onclick="printInvoice(${order.SalesOrderId})"><i class="fas fa-print"></i> طباعة الفاتورة</button>
        <button class="btn btn-outline" onclick="closeModal()">إغلاق</button>
      </div>
    </div>
  `);
}

window.printInvoice = function(orderId) {
  const el = document.getElementById(`invoice-${orderId}`);
  if (!el) return;
  const w = window.open('', '_blank', 'width=800,height=1000');
  w.document.write(`
    <html><head><meta charset="utf-8"><title>فاتورة - م محمد شبانه</title>
    <style>
      @page{size:A4 portrait;margin:15mm}
      *{box-sizing:border-box}
      body{font-family:'Segoe UI',system-ui,sans-serif;padding:0;margin:0;direction:rtl;font-size:13px;color:#000;background:#fff;line-height:1.6}
      .inv-wrap{width:100%;padding:10px}
      .no-print{display:none !important}
      @media print{
        .no-print{display:none !important}
        body{background:#fff;color:#000}
        .inv-wrap{width:100%;padding:0}
      }
    </style></head><body>
    <div class="inv-wrap">
      ${el.innerHTML}
    </div>
    <script>
      document.querySelectorAll('.no-print').forEach(el => el.style.display = 'none');
      window.print();
      window.close();
    <\/script>
    </body></html>
  `);
  w.document.close();
};

async function loadRecentOrders() {
  const el = document.getElementById('recent-orders');
  if (!el) return;
  try {
    const orders = await apiGet('/sales/orders?limit=5');
    if (!orders.length) {
      el.innerHTML = '<div class="empty-state" style="padding:16px"><p style="font-size:13px">لم يتم إجراء أي عملية بيع بعد</p></div>';
      return;
    }
    el.innerHTML = orders.map(o =>
      `<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #eee">
        <span>${o.OrderNumber}</span><span>${fmtMoney(o.GrandTotal)}</span>
        <span>${statusBadge(o.Status)}</span>
      </div>`
    ).join('');
  } catch (_) { el.innerHTML = ''; }
}

// ============ PRODUCTS ============
async function loadCategories() {
  try {
    const cats = await apiGet('/products/categories');
    const sel = document.getElementById('prodCategoryFilter');
    if (sel) sel.innerHTML = '<option value="">كل التصنيفات</option>' + cats.map(c => `<option value="${c.CategoryId}">${c.Name}</option>`).join('');
  } catch (_) {}
}

window.debounceSearch = function(page) {
  clearTimeout(_debounceTimers[page]);
  _debounceTimers[page] = setTimeout(() => {
    if (page === 'products') { prodPage = 1; filterProducts(); }
  }, 400);
};

window.filterProducts = function() {
  prodCatFilter = document.getElementById('prodCategoryFilter')?.value || '';
  prodStatusFilter = document.getElementById('prodStatusFilter')?.value || '';
  prodSearchQ = document.getElementById('prodSearch')?.value || '';
  prodPage = 1;
  renderProducts();
};

window.goProdPage = function(p) {
  prodPage = p;
  renderProducts();
};

async function renderProducts() {
  const tbody = document.getElementById('productsBody');
  const count = document.getElementById('productsCount');
  if (!tbody) return;
  tbody.innerHTML = skeletonRows(8);
  loadCategories();

  try {
    let url = `/products?Page=${prodPage}&PageSize=20&include_deleted=0`;
    if (prodCatFilter) url += `&CategoryId=${prodCatFilter}`;
    if (prodStatusFilter) url += `&IsActive=${prodStatusFilter}`;
    if (prodSearchQ) url += `&search=${encodeURIComponent(prodSearchQ)}`;
    const res = await apiGet(url);
    const products = res.value || [];
    const total = res.Count || 0;
    const pages = Math.ceil(total / (res.PageSize || 20));

    if (count) count.textContent = `إجمالي: ${total} منتج - صفحة ${prodPage} من ${pages || 1}`;

    if (products.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:40px"><i class="fas fa-box-open" style="font-size:32px;opacity:0.3;margin-bottom:8px;display:block"></i>${prodSearchQ || prodCatFilter ? 'لا توجد منتجات تطابق بحثك' : 'لم يتم إضافة أي منتجات بعد'}<br><small>${prodSearchQ || prodCatFilter ? 'حاول تغيير معايير البحث' : 'اضغط على "إضافة منتج" للبدء'}</small></td></tr>`;
    } else {
      tbody.innerHTML = products.map(p => `
        <tr>
          <td>${p.SKU}</td><td>${p.Name}</td><td>${p.CategoryName || '-'}</td>
          <td>${fmtMoney(p.SellingPrice)}</td><td>${p.InStock ?? '-'}</td>
          <td>${p.IsActive ? '<span style="color:var(--success)">نشط</span>' : '<span style="color:var(--danger)">غير نشط</span>'}</td>
          <td><button class="btn btn-danger btn-sm" onclick="deleteProduct(${p.ProductId})"><i class="fas fa-trash"></i></button></td>
        </tr>
      `).join('');
    }

    // Pagination nav
    const nav = document.getElementById('prodPageNav');
    if (nav) {
      if (pages <= 1) { nav.innerHTML = ''; return; }
      let html = '';
      if (prodPage > 1) html += `<button class="btn btn-sm btn-outline" onclick="goProdPage(${prodPage - 1})">‹ السابق</button>`;
      for (let p = Math.max(1, prodPage - 2); p <= Math.min(pages, prodPage + 2); p++) {
        html += `<button class="btn btn-sm ${p === prodPage ? 'btn-primary' : 'btn-outline'}" onclick="goProdPage(${p})">${p}</button>`;
      }
      if (prodPage < pages) html += `<button class="btn btn-sm btn-outline" onclick="goProdPage(${prodPage + 1})">التالي ›</button>`;
      nav.innerHTML = html;
    }
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:40px;color:var(--danger)"><i class="fas fa-exclamation-triangle" style="font-size:32px;margin-bottom:8px;display:block"></i>${err.message}<br><button class="btn btn-sm btn-primary mt-2" onclick="renderProducts()">إعادة المحاولة</button></td></tr>`;
  }
}

window.showProductModal = async function() {
  let categories = [], brands = [], taxes = [];
  try { [categories, brands, taxes] = await Promise.all([apiGet('/products/categories'), apiGet('/products/brands'), apiGet('/products/taxes')]); } catch (_) {}
  openModal(`
    <form id="product-form">
      <div class="form-row">
        <div class="form-group"><label>SKU *</label><input class="form-control" id="pf-sku" required></div>
        <div class="form-group"><label>الاسم *</label><input class="form-control" id="pf-name" required></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>التصنيف</label><select class="form-control" id="pf-category"><option value="">اختر</option>${categories.map(c => `<option value="${c.CategoryId}">${c.Name}</option>`).join('')}</select></div>
        <div class="form-group"><label>الماركة</label><select class="form-control" id="pf-brand"><option value="">اختر</option>${brands.map(b => `<option value="${b.BrandId}">${b.Name}</option>`).join('')}</select></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>سعر التكلفة</label><input class="form-control" id="pf-cost" type="number" value="0"></div>
        <div class="form-group"><label>سعر البيع *</label><input class="form-control" id="pf-price" type="number" required></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>الباركود</label><input class="form-control" id="pf-barcode"></div>
        <div class="form-group"><label>الضمان (يوم)</label><input class="form-control" id="pf-warranty" type="number" value="0"></div>
      </div>
      <div class="form-group"><label>الوصف</label><textarea class="form-control" id="pf-desc" rows="2"></textarea></div>
      <div class="modal-actions">
        <button type="button" class="btn btn-outline" onclick="closeModal()">إلغاء</button>
        <button type="submit" class="btn btn-primary">حفظ</button>
      </div>
    </form>
  `);
  document.getElementById('product-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      await apiPost('/products', {
        SKU: document.getElementById('pf-sku').value, Name: document.getElementById('pf-name').value,
        CategoryId: document.getElementById('pf-category').value || null, BrandId: document.getElementById('pf-brand').value || null,
        CostPrice: parseInt(document.getElementById('pf-cost').value) || 0, SellingPrice: parseInt(document.getElementById('pf-price').value) || 0,
        Barcode: document.getElementById('pf-barcode').value || null, WarrantyDays: parseInt(document.getElementById('pf-warranty').value) || 0,
        Description: document.getElementById('pf-desc').value || null,
      });
      showToast('✅ تم إضافة المنتج'); closeModal(); renderProducts();
    } catch (err) { showToast('❌ ' + err.message, 'error'); }
  });
};

window.deleteProduct = async function(id) {
  if (!confirm('هل أنت متأكد من حذف هذا المنتج؟')) return;
  try { await apiDelete('/products/' + id); showToast('✅ تم الحذف'); renderProducts(); }
  catch (err) { showToast('❌ ' + err.message, 'error'); }
};

// ============ INVENTORY ============
async function renderInventory() {
  // Reset to stock tab
  const activeTab = document.querySelector('.inventory-tab.active');
  if (!activeTab) {
    const firstTab = document.querySelector('.inventory-tab');
    if (firstTab) switchInventoryTab('stock', firstTab);
  }
  const tbody = document.getElementById('inventoryBody');
  if (!tbody) return;
  tbody.innerHTML = skeletonRows(8);
  try {
    const stock = await apiGet('/inventory/stock');
    if (stock.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:40px"><i class="fas fa-warehouse" style="font-size:32px;opacity:0.3;margin-bottom:8px;display:block"></i>لا توجد بيانات مخزون بعد<br><small>بعد إضافة المنتجات وإجراء عمليات شراء، ستظهر بيانات المخزون هنا</small></td></tr>';
      return;
    }
    tbody.innerHTML = stock.map(s => `
      <tr style="${s.Quantity <= s.MinStockLevel && s.MinStockLevel > 0 ? 'background:#fff5f5' : ''}">
        <td>${s.ProductName}</td><td>${s.SKU}</td><td>${s.WarehouseName}</td>
        <td style="${s.Quantity <= s.MinStockLevel && s.MinStockLevel > 0 ? 'color:var(--danger);font-weight:700' : ''}">${s.Quantity}</td>
        <td>${s.AvailableQuantity}</td><td>${s.MinStockLevel || 0}</td>
        <td>
          <button class="btn btn-sm btn-info" onclick="showAddStockModal(${s.ProductId}, '${s.ProductName.replace(/'/g, "\\'")}', ${s.InventoryId})" title="إضافة مخزون"><i class="fas fa-plus"></i></button>
          <button class="btn btn-sm btn-danger" onclick="deleteInventory(${s.InventoryId}, '${s.ProductName.replace(/'/g, "\\'")}')" title="حذف"><i class="fas fa-trash"></i></button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:40px;color:var(--danger)"><i class="fas fa-exclamation-triangle" style="font-size:32px;margin-bottom:8px;display:block"></i>${err.message}<br><button class="btn btn-sm btn-primary mt-2" onclick="renderInventory()">إعادة المحاولة</button></td></tr>`;
  }
}

window.showAddStockModal = async function(productId, productName) {
  openModal(`
    <form id="addstock-form">
      <div class="form-group"><label>المنتج</label><input class="form-control" value="${productName}" readonly></div>
      <div class="form-group"><label>الكمية المضافة</label><input class="form-control" id="as-qty" type="number" min="1" value="1" required></div>
      <div class="form-group"><label>ملاحظات</label><input class="form-control" id="as-notes" placeholder="سبب الإضافة"></div>
      <div class="modal-actions">
        <button type="button" class="btn btn-outline" onclick="closeModal()">إلغاء</button>
        <button type="submit" class="btn btn-success">إضافة</button>
      </div>
    </form>
  `);
  document.getElementById('addstock-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      await apiPost('/inventory/adjust', {
        ProductId: productId, Quantity: parseInt(document.getElementById('as-qty').value),
        Notes: document.getElementById('as-notes').value || 'إضافة مخزون',
      });
      showToast('✅ تم إضافة المخزون'); closeModal(); renderInventory();
    } catch (err) { showToast('❌ ' + err.message, 'error'); }
  });
};

window.deleteInventory = async function(inventoryId, productName) {
  if (!confirm('هل أنت متأكد من حذف مخزون "' + productName + '"؟')) return;
  try { await apiDelete('/inventory/stock/' + inventoryId); showToast('✅ تم الحذف'); renderInventory(); }
  catch (err) { showToast('❌ ' + err.message, 'error'); }
};

window.showAdjustModal = async function() {
  let products = [];
  let currentStock = [];
  try { 
    products = (await apiGet('/products?PageSize=200')).value || []; 
    currentStock = await apiGet('/inventory/stock');
  } catch (_) {}
  openModal(`
    <form id="adjust-form">
      <div class="form-group"><label>المنتج المراد تسويته *</label>
        <select class="form-control" id="adj-product-id" onchange="onReconcileProductChange(this.value)" required>
          <option value="">اختر منتج</option>
          ${products.map(p => `<option value="${p.ProductId}">${p.Name} (${p.SKU})</option>`).join('')}
        </select>
      </div>
      <div style="background:var(--card-bg);padding:10px;border-radius:6px;margin-bottom:12px;display:none" id="recon-info">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px">
          <span>الكمية الحالية بالنظام:</span><strong id="recon-system-qty">0</strong>
        </div>
        <div style="display:flex;justify-content:space-between;color:var(--primary)" id="recon-diff-row">
          <span>الفرق الذي سيتم تسجيله:</span><strong id="recon-diff-qty">0</strong>
        </div>
      </div>
      <div class="form-group"><label>الكمية الفعلية المقاسة بالمخزن *</label>
        <input class="form-control" id="adj-actual-qty" type="number" oninput="calcReconcileDiff()" required disabled>
      </div>
      <div class="form-group"><label>سبب التسوية / ملاحظات</label>
        <input class="form-control" id="adj-notes" placeholder="مثال: جرد دوري، عجز في المخزن، الخ">
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-outline" onclick="closeModal()">إلغاء</button>
        <button type="submit" class="btn btn-info" id="recon-submit-btn" disabled>تأكيد تسوية المخزون</button>
      </div>
    </form>
  `);
  
  window.onReconcileProductChange = function(productId) {
    const infoBox = document.getElementById('recon-info');
    const actualInput = document.getElementById('adj-actual-qty');
    const submitBtn = document.getElementById('recon-submit-btn');
    if (!productId) {
      infoBox.style.display = 'none';
      actualInput.disabled = true;
      submitBtn.disabled = true;
      return;
    }
    const item = currentStock.find(s => s.ProductId == productId);
    const systemQty = item ? item.Quantity : 0;
    document.getElementById('recon-system-qty').textContent = systemQty;
    actualInput.disabled = false;
    actualInput.value = systemQty;
    submitBtn.disabled = false;
    infoBox.style.display = 'block';
    calcReconcileDiff();
  };
  
  window.calcReconcileDiff = function() {
    const systemQty = parseInt(document.getElementById('recon-system-qty').textContent || 0);
    const actualQty = parseInt(document.getElementById('adj-actual-qty').value || 0);
    const diff = actualQty - systemQty;
    const diffEl = document.getElementById('recon-diff-qty');
    const diffRow = document.getElementById('recon-diff-row');
    diffEl.textContent = (diff > 0 ? '+' : '') + diff;
    if (diff > 0) {
      diffRow.style.color = 'var(--success)';
    } else if (diff < 0) {
      diffRow.style.color = 'var(--danger)';
    } else {
      diffRow.style.color = 'var(--text)';
    }
  };

  document.getElementById('adjust-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const productId = parseInt(document.getElementById('adj-product-id').value);
    const systemQty = parseInt(document.getElementById('recon-system-qty').textContent || 0);
    const actualQty = parseInt(document.getElementById('adj-actual-qty').value || 0);
    const diff = actualQty - systemQty;
    
    if (diff === 0) {
      showToast('⚠ لا يوجد فرق لتسويته');
      return;
    }
    
    try {
      await apiPost('/inventory/adjust', {
        ProductId: productId, 
        Quantity: diff,
        Notes: document.getElementById('adj-notes').value || 'تسوية مخزون',
      });
      showToast('✅ تمت التسوية بنجاح'); closeModal(); renderInventory();
    } catch (err) { showToast('❌ ' + err.message, 'error'); }
  });
};

window.toggleLowStock = function(cb) {
  document.querySelectorAll('#inventoryBody tr').forEach(tr => {
    if (cb.checked) { tr.style.display = tr.style.background ? '' : 'none'; }
    else { tr.style.display = ''; }
  });
};

// ============ CUSTOMERS ============
async function renderCustomers() {
  const tbody = document.getElementById('customersBody');
  if (!tbody) return;
  tbody.innerHTML = skeletonRows(6);
  try {
    const customers = await apiGet('/customers');
    if (customers.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:40px"><i class="fas fa-users" style="font-size:32px;opacity:0.3;margin-bottom:8px;display:block"></i>لم يتم إضافة أي عملاء بعد<br><small>اضغط على "إضافة عميل" لإضافة عميل جديد</small></td></tr>';
      return;
    }
    tbody.innerHTML = customers.map(c => `
      <tr>
        <td>${c.CustomerCode}</td>
        <td>${c.FullName}</td>
        <td>${c.Phone || '-'}</td>
        <td>${fmtMoney(c.TotalPurchases || 0)}</td>
        <td><button class="btn btn-danger btn-sm" onclick="deleteCustomer(${c.CustomerId})"><i class="fas fa-trash"></i></button></td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:40px;color:var(--danger)"><i class="fas fa-exclamation-triangle" style="font-size:32px;margin-bottom:8px;display:block"></i>${err.message}<br><button class="btn btn-sm btn-primary mt-2" onclick="renderCustomers()">إعادة المحاولة</button></td></tr>`;
  }
}

window.showCustomerModal = function() {
  openModal(`
    <form id="customer-form">
      <div class="form-group"><label>الاسم *</label><input class="form-control" id="cf-name" required></div>
      <div class="form-row">
        <div class="form-group"><label>الهاتف</label><input class="form-control" id="cf-phone"></div>
        <div class="form-group"><label>البريد</label><input class="form-control" id="cf-email" type="email"></div>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-outline" onclick="closeModal()">إلغاء</button>
        <button type="submit" class="btn btn-primary">حفظ</button>
      </div>
    </form>
  `);
  document.getElementById('customer-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      await apiPost('/customers', {
        FullName: document.getElementById('cf-name').value, Phone: document.getElementById('cf-phone').value,
        Email: document.getElementById('cf-email').value,
      });
      showToast('✅ تم إضافة العميل'); closeModal(); renderCustomers();
    } catch (err) { showToast('❌ ' + err.message, 'error'); }
  });
};

window.deleteCustomer = async function(id) {
  if (!confirm('هل أنت متأكد من حذف هذا العميل؟')) return;
  try { await apiDelete('/customers/' + id); showToast('✅ تم الحذف'); renderCustomers(); }
  catch (err) { showToast('❌ ' + err.message, 'error'); }
};





// ============ SUPPLIERS ============
async function renderSuppliers() {
  const tbody = document.getElementById('suppliersBody');
  if (!tbody) return;
  tbody.innerHTML = skeletonRows(6);
  try {
    const suppliers = await apiGet('/suppliers');
    if (suppliers.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:40px"><i class="fas fa-industry" style="font-size:32px;opacity:0.3;margin-bottom:8px;display:block"></i>لم يتم إضافة أي موردين بعد<br><small>اضغط على "إضافة مورد" لإضافة مورد جديد</small></td></tr>';
      return;
    }
    tbody.innerHTML = suppliers.map(s => `
      <tr>
        <td>${s.SupplierCode}</td><td>${s.CompanyName}</td><td>${s.ContactPerson || '-'}</td>
        <td>${s.Phone || '-'}</td><td>${fmtMoney(s.TotalPurchases || 0)}</td>
        <td><button class="btn btn-danger btn-sm" onclick="deleteSupplier(${s.SupplierId})"><i class="fas fa-trash"></i></button></td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:40px;color:var(--danger)"><i class="fas fa-exclamation-triangle" style="font-size:32px;margin-bottom:8px;display:block"></i>${err.message}<br><button class="btn btn-sm btn-primary mt-2" onclick="renderSuppliers()">إعادة المحاولة</button></td></tr>`;
  }
}

window.showSupplierModal = function() {
  openModal(`
    <form id="supplier-form">
      <div class="form-group"><label>اسم الشركة *</label><input class="form-control" id="sf-company" required></div>
      <div class="form-row">
        <div class="form-group"><label>جهة الاتصال</label><input class="form-control" id="sf-contact"></div>
        <div class="form-group"><label>الهاتف</label><input class="form-control" id="sf-phone"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>البريد</label><input class="form-control" id="sf-email" type="email"></div>
        <div class="form-group"><label>الرقم الضريبي</label><input class="form-control" id="sf-tax"></div>
      </div>
      <div class="form-group"><label>شروط الدفع</label><input class="form-control" id="sf-terms" placeholder="NET30"></div>
      <div class="modal-actions">
        <button type="button" class="btn btn-outline" onclick="closeModal()">إلغاء</button>
        <button type="submit" class="btn btn-primary">حفظ</button>
      </div>
    </form>
  `);
  document.getElementById('supplier-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      await apiPost('/suppliers', {
        CompanyName: document.getElementById('sf-company').value, ContactPerson: document.getElementById('sf-contact').value,
        Phone: document.getElementById('sf-phone').value, Email: document.getElementById('sf-email').value,
        TaxNumber: document.getElementById('sf-tax').value, PaymentTerms: document.getElementById('sf-terms').value,
      });
      showToast('✅ تم إضافة المورد'); closeModal(); renderSuppliers();
    } catch (err) { showToast('❌ ' + err.message, 'error'); }
  });
};

window.deleteSupplier = async function(id) {
  if (!confirm('هل أنت متأكد من حذف هذا المورد؟')) return;
  try { await apiDelete('/suppliers/' + id); showToast('✅ تم الحذف'); renderSuppliers(); }
  catch (err) { showToast('❌ ' + err.message, 'error'); }
};

// ============ PURCHASES ============
async function renderPurchases() {
  const tbody = document.getElementById('purchasesBody');
  if (!tbody) return;
  tbody.innerHTML = skeletonRows(6);
  try {
    const orders = await apiGet('/purchases/orders');
    if (orders.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:40px"><i class="fas fa-shopping-cart" style="font-size:32px;opacity:0.3;margin-bottom:8px;display:block"></i>لم يتم إنشاء أي أوامر شراء بعد<br><small>اضغط على "أمر شراء جديد" لبدء عملية شراء</small></td></tr>';
      return;
    }
    tbody.innerHTML = orders.map(o => `
      <tr>
        <td>${o.OrderNumber}</td><td>${o.SupplierName || '-'}</td>
        <td>${fmtMoney(o.GrandTotal)}</td><td>${statusBadge(o.Status)}</td>
        <td>${fmtDate(o.OrderDate)}</td>
        <td>${o.Status !== 'RECEIVED' && o.Status !== 'CANCELLED' ? `<button class="btn btn-success btn-sm" onclick="receivePO(${o.PurchaseOrderId})">استلام</button>` : ''}</td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:40px;color:var(--danger)"><i class="fas fa-exclamation-triangle" style="font-size:32px;margin-bottom:8px;display:block"></i>${err.message}<br><button class="btn btn-sm btn-primary mt-2" onclick="renderPurchases()">إعادة المحاولة</button></td></tr>`;
  }
}

window.showPurchaseModal = async function() {
  let suppliers = [], products = [];
  try { [suppliers, products] = await Promise.all([apiGet('/suppliers'), apiGet('/products?PageSize=200')]); } catch (_) {}
  products = products.value || products || [];
  window._poItems = [];
  openModal(`
    <form id="po-form">
      <div class="form-group"><label>المورد *</label>
        <select class="form-control" id="po-supplier" required>
          <option value="">اختر المورد</option>
          ${suppliers.map(s => `<option value="${s.SupplierId}">${s.CompanyName}</option>`).join('')}
        </select>
      </div>
      <div class="form-group">
        <label>إضافة منتج</label>
        <select class="form-control" id="po-product-select" onchange="addPOItem()">
          <option value="">اختر منتج</option>
          ${products.map(p => `<option value="${p.ProductId}" data-cost="${p.CostPrice || 0}">${p.Name} - ${fmtMoney(p.CostPrice)}</option>`).join('')}
        </select>
      </div>
      <div id="po-items-list"><p style="color:var(--text-secondary)">لم يتم إضافة منتجات بعد</p></div>
      <div class="modal-actions">
        <button type="button" class="btn btn-outline" onclick="closeModal()">إلغاء</button>
        <button type="submit" class="btn btn-primary">إنشاء الأمر</button>
      </div>
    </form>
  `);
  document.getElementById('po-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const sid = document.getElementById('po-supplier').value;
    if (!sid || !window._poItems.length) { showToast('⚠ يرجى اختيار المورد وإضافة منتجات', 'error'); return; }
    try {
      await apiPost('/purchases/orders', { SupplierId: parseInt(sid), Items: window._poItems, Notes: '' });
      showToast('✅ تم إنشاء أمر الشراء'); closeModal(); renderPurchases();
    } catch (err) { showToast('❌ ' + err.message, 'error'); }
  });
};

window.addPOItem = function() {
  const sel = document.getElementById('po-product-select');
  if (!sel || !sel.value) return;
  const pid = parseInt(sel.value);
  const opt = sel.options[sel.selectedIndex];
  const cost = parseInt(opt.dataset.cost) || 0;
  if (window._poItems.find(x => x.ProductId === pid)) { showToast('⚠ المنتج موجود بالفعل', 'info'); sel.value = ''; return; }
  window._poItems.push({ ProductId: pid, Quantity: 1, UnitCost: cost });
  sel.value = '';
  renderPOItems();
};

function renderPOItems() {
  const el = document.getElementById('po-items-list');
  if (!el) return;
  if (!window._poItems.length) { el.innerHTML = '<p style="color:var(--text-secondary)">لم يتم إضافة منتجات بعد</p>'; return; }
  el.innerHTML = '<table><tr><th>المنتج</th><th>الكمية</th><th>سعر الوحدة</th><th></th></tr>' +
    window._poItems.map((item, i) =>
      `<tr>
        <td>منتج #${item.ProductId}</td>
        <td><input style="width:60px" type="number" min="1" value="${item.Quantity}" onchange="window._poItems[${i}].Quantity=parseInt(this.value)||1"></td>
        <td><input style="width:100px" type="number" value="${item.UnitCost}" onchange="window._poItems[${i}].UnitCost=parseInt(this.value)||0"></td>
        <td><button class="btn btn-danger btn-sm" onclick="window._poItems.splice(${i},1);renderPOItems()">×</button></td>
      </tr>`
    ).join('') + '</table>';
}

window.receivePO = async function(id) {
  if (!confirm('هل تريد استلام هذا الأمر؟')) return;
  try { await apiPost('/purchases/orders/' + id + '/receive', {}); showToast('✅ تم الاستلام'); renderPurchases(); }
  catch (err) { showToast('❌ ' + err.message, 'error'); }
};

// ============ REPAIRS ============
async function renderRepairs() {
  const tbody = document.getElementById('repairsBody');
  if (!tbody) return;
  tbody.innerHTML = skeletonRows(6);
  try {
    const repairs = await apiGet('/repairs/orders');
    if (repairs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:40px"><i class="fas fa-tools" style="font-size:32px;opacity:0.3;margin-bottom:8px;display:block"></i>لا توجد طلبات صيانة بعد<br><small>اضغط على "طلب صيانة جديد" لإضافة طلب</small></td></tr>';
      return;
    }
    tbody.innerHTML = repairs.map(r => `
      <tr>
        <td><a href="#" style="color:var(--primary);font-weight:600;text-decoration:none;" onclick="event.preventDefault(); showRepairDetailModal(${r.RepairOrderId})">${r.RepairNumber}</a></td><td>${r.CustomerName || '-'}</td>
        <td>${r.DeviceType || '-'} ${r.DeviceBrand || ''}</td>
        <td>${statusBadge(r.Status)}</td>
        <td>${fmtDate(r.ReceivedDate)}</td>
        <td>
          <select class="filter-select" style="padding:2px 4px;font-size:11px;width:130px" onchange="changeRepairStatus(${r.RepairOrderId}, this.value)">
            <option value="RECEIVED" ${r.Status === 'RECEIVED' ? 'selected' : ''}>⏳ تم الاستلام</option>
            <option value="DIAGNOSING" ${r.Status === 'DIAGNOSING' ? 'selected' : ''}>تحت التشخيص</option>
            <option value="IN_PROGRESS" ${r.Status === 'IN_PROGRESS' ? 'selected' : ''}>تحت الإصلاح</option>
            <option value="COMPLETED" ${r.Status === 'COMPLETED' ? 'selected' : ''}>✔️ تم الانتهاء</option>
            <option value="UNREPAIRABLE" ${r.Status === 'UNREPAIRABLE' ? 'selected' : ''}>❌ لم يتم التصليح</option>
            <option value="STOPPED" ${r.Status === 'STOPPED' ? 'selected' : ''}>⛔ وقف صيانة</option>
            <option value="DELIVERED" ${r.Status === 'DELIVERED' ? 'selected' : ''}>✅ تم التسليم</option>
          </select>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:40px;color:var(--danger)"><i class="fas fa-exclamation-triangle" style="font-size:32px;margin-bottom:8px;display:block"></i>${err.message}<br><button class="btn btn-sm btn-primary mt-2" onclick="renderRepairs()">إعادة المحاولة</button></td></tr>`;
  }
}

window.showRepairModal = async function() {
  let customers = [];
  try { customers = await apiGet('/customers'); } catch (_) {}

  window.onRepairPhoneKeyup = function(val) {
    const c = customers.find(cust => cust.Phone && cust.Phone.trim() === val.trim());
    const nameInput = document.getElementById('rf-customer-name');
    if (c && nameInput) {
      nameInput.value = c.FullName;
      nameInput.readOnly = true;
    } else if (nameInput) {
      nameInput.readOnly = false;
    }
  };

  window.onRepairPhoneChange = function(val) {
    onRepairPhoneKeyup(val);
  };

  openModal(`
    <form id="repair-form">
      <div class="form-row" style="display:flex; gap:10px;">
        <div class="form-group" style="flex:1;">
          <label>رقم هاتف العميل *</label>
          <input type="text" list="repairPhoneList" class="form-control" id="rf-customer-phone" placeholder="أدخل رقم الهاتف" onkeyup="onRepairPhoneKeyup(this.value)" onchange="onRepairPhoneChange(this.value)" required>
          <datalist id="repairPhoneList">
            ${customers.filter(c => c.Phone).map(c => `<option value="${c.Phone}">${c.FullName}</option>`).join('')}
          </datalist>
        </div>
        <div class="form-group" style="flex:1.2;">
          <label>اسم العميل *</label>
          <input type="text" class="form-control" id="rf-customer-name" placeholder="اسم العميل" required>
        </div>
      </div>
      
      <div class="form-row">
        <div class="form-group"><label>نوع الجهاز</label>
          <select class="form-control" id="rf-type">
            <option value="LAPTOP">لابتوب</option><option value="PC">كمبيوتر</option>
            <option value="PRINTER">طابعة</option><option value="MONITOR">شاشة</option><option value="OTHER">أخرى</option>
          </select>
        </div>
        <div class="form-group"><label>الماركة</label><input class="form-control" id="rf-brand"></div>
      </div>
      <div class="form-row">
        <div class="form-group"><label>الموديل</label><input class="form-control" id="rf-model"></div>
        <div class="form-group"><label>الرقم التسلسلي</label><input class="form-control" id="rf-serial"></div>
      </div>
      <div class="form-row" style="display:flex; gap:10px;">
        <div class="form-group" style="flex:1;"><label>اسم الفني المسؤول</label><input class="form-control" id="rf-tech-name" placeholder="اسم الفني"></div>
        <div class="form-group" style="flex:1;"><label>رقم هاتف الفني</label><input class="form-control" id="rf-tech-phone" placeholder="رقم هاتف الفني"></div>
      </div>
      <div class="form-group"><label>العطل *</label><textarea class="form-control" id="rf-issue" rows="3" required></textarea></div>
      <div class="modal-actions">
        <button type="button" class="btn btn-outline" onclick="closeModal()">إلغاء</button>
        <button type="submit" class="btn btn-primary">إنشاء</button>
      </div>
    </form>
  `);

  document.getElementById('repair-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      await apiPost('/repairs/orders', {
        StoreId: 1,
        CustomerPhone: document.getElementById('rf-customer-phone').value,
        CustomerName: document.getElementById('rf-customer-name').value,
        DeviceInfo: JSON.stringify({
          DeviceType: document.getElementById('rf-type').value,
          DeviceBrand: document.getElementById('rf-brand').value,
          DeviceModel: document.getElementById('rf-model').value,
          SerialNumber: document.getElementById('rf-serial').value,
        }),
        ReportedIssue: document.getElementById('rf-issue').value,
        TechnicianName: document.getElementById('rf-tech-name').value || '',
        TechnicianPhone: document.getElementById('rf-tech-phone').value || '',
      });
      showToast('✅ تم تسجيل طلب الصيانة');
      closeModal();
      renderRepairs();
    } catch (err) {
      showToast('❌ ' + err.message, 'error');
    }
  });
};

window.showRepairDetailModal = async function(repairOrderId) {
  let r = null;
  let products = [];
  try {
    r = await apiGet('/repairs/orders/' + repairOrderId);
    products = (await apiGet('/products?PageSize=200')).value || [];
  } catch (err) {
    showToast('❌ خطأ في جلب البيانات: ' + err.message, 'error');
    return;
  }

  const parts = r.Parts || [];

  window.onPartProductChange = function(productId) {
    const select = document.getElementById('ap-product-id');
    const priceInput = document.getElementById('ap-price');
    if (!productId) {
      priceInput.value = '';
      return;
    }
    const selectedOption = select.options[select.selectedIndex];
    const price = selectedOption.getAttribute('data-price');
    priceInput.value = price || 0;
  };

  function statusBadgeText(status) {
    switch (status) {
      case 'DELIVERED': return 'تم التسليم';
      case 'COMPLETED': return 'تم التصليح';
      case 'IN_PROGRESS': return 'تحت الإصلاح';
      case 'DIAGNOSING': return 'تحت التشخيص';
      case 'RECEIVED': return 'تم الاستلام';
      case 'UNREPAIRABLE': return 'لم يتم التصليح';
      case 'STOPPED': return 'وقف صيانة';
      default: return status;
    }
  }

  openModal(`
    <div style="padding:10px; text-align:right;">
      <h3 style="margin-top:0; margin-bottom:15px; border-bottom:1px solid var(--border-color); padding-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
        <span><i class="fas fa-wrench" style="color:var(--primary); margin-left:8px;"></i>طلب صيانة رقم ${r.RepairNumber}</span>
        <span class="badge ${r.Status === 'DELIVERED' ? 'badge-success' : 'badge-warning'}">${statusBadgeText(r.Status)}</span>
      </h3>
      
      <div style="display:flex; gap:20px; flex-wrap:wrap;">
        <!-- Left Column: Details -->
        <div style="flex:1.2; min-width:300px; background:var(--card-bg); padding:15px; border-radius:8px; border:1px solid var(--border-color);">
          <h4 style="margin-top:0; margin-bottom:12px; color:var(--primary); border-bottom:1px solid var(--border-color); padding-bottom:6px;">بيانات العميل والجهاز</h4>
          <div style="margin-bottom:8px;"><strong>اسم العميل:</strong> <span>${r.CustomerName || 'غير معروف'}</span></div>
          <div style="margin-bottom:8px;"><strong>جهاز:</strong> <span>${r.DeviceType} ${r.DeviceBrand} ${r.DeviceModel}</span></div>
          <div style="margin-bottom:8px;"><strong>الرقم التسلسلي:</strong> <code>${r.SerialNumber || '-'}</code></div>
          ${r.TechnicianName ? `<div style="margin-bottom:8px;"><strong>الفني المسؤول:</strong> <span>${r.TechnicianName} ${r.TechnicianPhone ? `(${r.TechnicianPhone})` : ''}</span></div>` : ''}
          <div style="margin-bottom:8px;"><strong>المشكلة المسجلة:</strong> <p style="background:var(--body-bg); padding:8px; border-radius:4px; margin:4px 0; font-size:13px;">${r.ReportedIssue}</p></div>
          <div style="margin-bottom:8px;"><strong>ملاحظات الاستلام:</strong> <p style="background:var(--body-bg); padding:8px; border-radius:4px; margin:4px 0; font-size:13px;">${r.Notes || 'لا توجد'}</p></div>
        </div>
        
        <!-- Right Column: Financials & Parts -->
        <div style="flex:1.5; min-width:350px; display:flex; flex-direction:column; gap:15px;">
          <!-- Financial Breakdown -->
          <div style="background:var(--card-bg); padding:15px; border-radius:8px; border:1px solid var(--border-color);">
            <h4 style="margin-top:0; margin-bottom:12px; color:var(--primary); border-bottom:1px solid var(--border-color); padding-bottom:6px;">الرسوم والمالية</h4>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
              <div><strong>رسوم الفحص:</strong> ${fmtMoney(r.DiagnosisFee)} ج.م</div>
              <div><strong>رسوم الإصلاح:</strong> ${fmtMoney(r.LaborFee)} ج.م</div>
              <div><strong>تكلفة قطع الغيار:</strong> ${fmtMoney(r.PartsCost)} ج.م</div>
              <div style="font-weight:bold; color:var(--success);"><strong>الإجمالي الكلي:</strong> ${fmtMoney(r.GrandTotal)} ج.م</div>
            </div>
          </div>
          
          <!-- Parts Table -->
          <div style="background:var(--card-bg); padding:15px; border-radius:8px; border:1px solid var(--border-color);">
            <h4 style="margin-top:0; margin-bottom:12px; color:var(--primary); border-bottom:1px solid var(--border-color); padding-bottom:6px;">قطع الغيار ومستلزمات الصيانة من المخزون</h4>
            <table style="width:100%; font-size:12px; margin-bottom:10px; border-collapse:collapse;">
              <thead>
                <tr style="border-bottom:1px solid var(--border-color);">
                  <th style="text-align:right; padding:6px 0;">البيان (السلعة)</th>
                  <th style="text-align:center;">الكمية</th>
                  <th style="text-align:left;">الأسعار</th>
                  <th style="text-align:left;">الإجمالي</th>
                </tr>
              </thead>
              <tbody>
                ${parts.length === 0 ? '<tr><td colspan="4" style="text-align:center; padding:15px; color:var(--gray);">لم يتم استخدام قطع غيار من المخزون بعد</td></tr>' : 
                  parts.map(p => `
                    <tr style="border-bottom:1px dashed var(--border-color);">
                      <td style="padding:6px 0;">${p.ProductName} <small style="color:var(--gray); display:block;">${p.SKU}</small></td>
                      <td style="text-align:center;">${p.Quantity}</td>
                      <td style="text-align:left;">${fmtMoney(p.UnitPrice)} ج.م</td>
                      <td style="text-align:left; font-weight:600;">${fmtMoney(p.LineTotal)} ج.م</td>
                    </tr>
                  `).join('')
                }
              </tbody>
            </table>

            <!-- Add Part Form -->
            <form id="add-part-form" style="background:var(--body-bg); padding:10px; border-radius:6px; margin-top:10px; border:1px dashed var(--border-color);">
              <h5 style="margin-top:0; margin-bottom:8px; font-size:13px; color:var(--text);"><i class="fas fa-plus"></i> إضافة قطعة غيار من المخزون</h5>
              <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:8px;">
                <select class="form-control" id="ap-product-id" onchange="onPartProductChange(this.value)" style="flex:2; height:32px; font-size:12px;" required>
                  <option value="">اختر السلعة من المخزن...</option>
                  ${products.map(p => `<option value="${p.ProductId}" data-price="${p.SellingPrice}">${p.Name} (${p.SKU}) [المتوفر: ${p.Quantity || 0}]</option>`).join('')}
                </select>
                <input type="number" class="form-control" id="ap-qty" value="1" min="1" placeholder="الكمية" style="flex:0.5; height:32px; font-size:12px; text-align:center;" required>
                <input type="number" class="form-control" id="ap-price" placeholder="السعر" style="flex:0.8; height:32px; font-size:12px; text-align:center;" required>
              </div>
              <div style="display:flex; justify-content:flex-end;">
                <button type="submit" class="btn btn-sm btn-success" style="padding:4px 12px; font-size:12px;"><i class="fas fa-plus"></i> إضافة وصرف من المخزن</button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="modal-actions" style="margin-top:20px; border-top:1px solid var(--border-color); padding-top:12px;">
        <button type="button" class="btn btn-outline" onclick="closeModal()">إغلاق</button>
      </div>
    </div>
  `);

  document.getElementById('add-part-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const productId = parseInt(document.getElementById('ap-product-id').value);
    const qty = parseInt(document.getElementById('ap-qty').value);
    const price = parseFloat(document.getElementById('ap-price').value);
    try {
      await apiPost('/repairs/orders/' + repairOrderId + '/parts', {
        ProductId: productId,
        Quantity: qty,
        UnitPrice: price,
        Notes: 'صرف قطعة غيار للصيانة'
      });
      showToast('✅ تم إضافة قطعة الغيار وخصمها من المخزن بنجاح');
      closeModal();
      showRepairDetailModal(repairOrderId);
      renderRepairs();
    } catch (err) {
      showToast('❌ ' + err.message, 'error');
    }
  });
};

window.updateRepairStatus = async function(id) {
  try {
    const orders = await apiGet('/repairs/orders');
    const r = orders.find(o => o.RepairOrderId === id);
    if (!r) return;

    if (r.Status === 'RECEIVED') {
      if (!confirm('هل تريد تغيير الحالة إلى "تحت التشخيص"؟')) return;
      await apiPut('/repairs/orders/' + id + '/status', { Status: 'DIAGNOSING' });
      showToast('✅ تم تحديث الحالة'); renderRepairs();
    } else if (r.Status === 'DIAGNOSING') {
      if (!confirm('هل تريد تغيير الحالة إلى "تحت الإصلاح"؟')) return;
      await apiPut('/repairs/orders/' + id + '/status', { Status: 'IN_PROGRESS' });
      showToast('✅ تم تحديث الحالة'); renderRepairs();
    } else if (r.Status === 'IN_PROGRESS') {
      // Show modal to choose outcome: Repaired vs Not Repaired
      openModal(`
        <div style="padding:15px;text-align:center">
          <h4 style="margin-bottom:15px;color:#1e293b"><i class="fas fa-tools" style="color:#007bff;margin-left:8px"></i>تحديث نتيجة الصيانة</h4>
          <p style="color:#64748b;margin-bottom:25px">يرجى اختيار حالة صيانة الجهاز لتحديث السجل:</p>
          <div style="display:flex;gap:10px;margin-top:20px;justify-content:center;flex-wrap:wrap">
            <button class="btn btn-success" style="padding:10px 15px" onclick="confirmRepairOutcome(${id}, 'COMPLETED')"><i class="fas fa-check-circle" style="margin-left:5px"></i> تم التصليح</button>
            <button class="btn btn-danger" style="padding:10px 15px" onclick="confirmRepairOutcome(${id}, 'UNREPAIRABLE')"><i class="fas fa-times-circle" style="margin-left:5px"></i> لم يتم التصليح</button>
            <button class="btn btn-secondary" style="padding:10px 15px;background:#6c757d;color:#fff;border:none;border-radius:4px" onclick="confirmRepairOutcome(${id}, 'STOPPED')"><i class="fas fa-hand-paper" style="margin-left:5px"></i> وقف صيانة</button>
          </div>
          <div style="margin-top:25px">
            <button class="btn btn-outline" onclick="closeModal()">إلغاء</button>
          </div>
        </div>
      `);
    } else if (r.Status === 'COMPLETED' || r.Status === 'UNREPAIRABLE' || r.Status === 'STOPPED') {
      if (!confirm('هل تم تسليم الجهاز للعميل؟ سيتم تغيير الحالة إلى "تم التسليم".')) return;
      await apiPut('/repairs/orders/' + id + '/status', { Status: 'DELIVERED' });
      showToast('✅ تم تحديث الحالة'); renderRepairs();
    } else {
      showToast('⚠ طلب الصيانة منتهي ومسلّم بالفعل');
    }
  } catch (err) { showToast('❌ ' + err.message, 'error'); }
};

window.confirmRepairOutcome = async function(id, status) {
  try {
    await apiPut('/repairs/orders/' + id + '/status', { Status: status });
    showToast('✅ تم تحديث الحالة بنجاح');
    closeModal();
    renderRepairs();
  } catch (err) { showToast('❌ ' + err.message, 'error'); }
};


// ============ REPORTS ============
async function renderReports() {
  const cards = document.getElementById('reportCards');
  const salesBody = document.getElementById('reportSalesBody');
  if (!cards || !salesBody) return;
  cards.innerHTML = skeletonCards(4);
  salesBody.innerHTML = skeletonRows(5);
  try {
    const [dashboard, sales, fin] = await Promise.all([
      apiGet('/reports/dashboard'), apiGet('/reports/sales'), apiGet('/reports/financial'),
    ]);
    const totalIncome = fin.Summary?.INCOME || dashboard.TotalSales || 0;
    const totalExpenses = fin.Summary?.EXPENSE || 0;
    const netProfit = totalIncome - totalExpenses;
    
    cards.innerHTML = `
      <div class="stat-card"><div class="value">${fmtMoney(totalIncome)}</div><div class="label">إجمالي المبيعات (دخل)</div></div>
      <div class="stat-card"><div class="value">${fmtMoney(dashboard.TotalPurchases)}</div><div class="label">إجمالي المشتريات</div></div>
      <div class="stat-card"><div class="value" style="color:var(--danger)">${fmtMoney(totalExpenses)}</div><div class="label">إجمالي المصروفات</div></div>
      <div class="stat-card"><div class="value" style="color:${netProfit >= 0 ? 'var(--success)' : 'var(--danger)'};font-weight:800">${fmtMoney(netProfit)}</div><div class="label">صافي الأرباح</div></div>
    `;
    
    salesBody.innerHTML = (sales.DailySales || []).length
      ? sales.DailySales.map(d => `<tr><td>${d.Date}</td><td>${d.OrderCount}</td><td>${fmtMoney(d.TotalAmount)}</td><td>${fmtMoney(d.PaidAmount)}</td></tr>`).join('')
      : '<tr><td colspan="4" style="text-align:center;padding:40px"><i class="fas fa-chart-line" style="font-size:32px;opacity:0.3;margin-bottom:8px;display:block"></i>لا توجد بيانات مبيعات بعد<br><small>بمجرد إجراء أول عملية بيع، ستظهر البيانات هنا</small></td></tr>';

    const expensesBody = document.getElementById('expensesTableBody');
    if (expensesBody) {
      const expenses = (fin.Records || []).filter(r => r.RecordType === 'EXPENSE');
      expensesBody.innerHTML = expenses.length
        ? expenses.map(e => {
            const dt = new Date(e.RecordDate || e.CreatedAt);
            const dateStr = dt.toLocaleDateString('ar-EG') + ' ' + dt.toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' });
            return `
              <tr>
                <td>${e.RecordNumber}</td>
                <td>${e.Description || e.Category || '-'}</td>
                <td style="color:var(--danger);font-weight:bold">${fmtMoney(e.Amount)} ج.م</td>
                <td>${dateStr}</td>
                <td>${e.CreatedByName || '-'}</td>
              </tr>
            `;
          }).join('')
        : '<tr><td colspan="5" style="text-align:center;padding:40px">لا توجد مصاريف مسجلة بعد</td></tr>';
    }
  } catch (err) {
    cards.innerHTML = `<div class="empty-state" style="padding:20px"><div class="icon">⚠</div><p>${err.message}</p><button class="btn btn-sm btn-primary" onclick="renderReports()">إعادة المحاولة</button></div>`;
    salesBody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--danger)">' + err.message + '</td></tr>';
  }
}

window.changeRepairStatus = async function(orderId, status) {
  try {
    await apiPut(`/repairs/orders/${orderId}/status`, { Status: status });
    showToast('✅ تم تحديث حالة الصيانة بنجاح');
    renderRepairs();
  } catch (err) {
    showToast('❌ ' + err.message, 'error');
    renderRepairs();
  }
};

window.switchReportsTab = function(tab, el) {
  document.querySelectorAll('#page-reports .inventory-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('#page-reports .inventory-tab-content').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
  if (tab === 'dashboard') {
    document.getElementById('reportsTab-dashboard').classList.add('active');
  } else {
    document.getElementById('reportsTab-expenses').classList.add('active');
  }
};

window.showAddExpenseModal = function() {
  openModal(`
    <form id="expense-form">
      <div style="padding:5px">
        <h3 style="margin:0 0 16px;font-size:18px"><i class="fas fa-wallet" style="margin-left:8px;color:var(--primary)"></i>تسجيل مصروف جديد</h3>
        <div class="form-group">
          <label>اسم المصروف / البيان *</label>
          <input type="text" id="exp-desc" class="form-control" placeholder="مثال: فاتورة كهرباء، إيجار، أدوات نظافة" required>
        </div>
        <div class="form-group">
          <label>المبلغ (ج.م) *</label>
          <input type="number" id="exp-amount" min="1" class="form-control" placeholder="0" required>
        </div>
        <div class="form-group">
          <label>التصنيف</label>
          <select id="exp-category" class="form-control">
            <option value="مصاريف تشغيلية">مصاريف تشغيلية</option>
            <option value="إيجار وصيانة">إيجار وصيانة</option>
            <option value="فواتير ومرافق">فواتير ومرافق</option>
            <option value="نثريات وبوفيه">نثريات وبوفيه</option>
            <option value="رواتب وأجور">رواتب وأجور</option>
            <option value="أخرى">أخرى</option>
          </select>
        </div>
        <div class="modal-actions" style="margin-top:20px">
          <button type="button" class="btn btn-outline" onclick="closeModal()">إلغاء</button>
          <button type="submit" class="btn btn-primary">تسجيل المصروف</button>
        </div>
      </div>
    </form>
  `);

  document.getElementById('expense-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const desc = document.getElementById('exp-desc').value;
    const amount = parseInt(document.getElementById('exp-amount').value);
    const category = document.getElementById('exp-category').value;
    
    try {
      await apiPost('/reports/financial', {
        Description: desc,
        Amount: amount,
        Category: category
      });
      showToast('✅ تم تسجيل المصروف بنجاح');
      closeModal();
      if (state.page === 'expenses') renderExpensesPage();
      else if (state.page === 'reports') renderReports();
      else if (state.page === 'dashboard') renderDashboard();
    } catch (err) {
      showToast('❌ ' + err.message, 'error');
    }
  });
};

// ============ FILTER TABLE ============
window.filterTable = function(page) {
  const searchId = { products: 'productsBody', inventory: 'inventoryBody', customers: 'customersBody', suppliers: 'suppliersBody' }[page];
  const input = document.querySelector(`#page-${page} .search-input-wrapper input`);
  if (!input || !searchId) return;
  const q = input.value.toLowerCase();
  document.querySelectorAll(`#${searchId} tr`).forEach(tr => {
    tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
};

// ============ DARK MODE ============
window.toggleTheme = function() {
    const html = document.documentElement;
    const btn = document.getElementById('themeToggle');
    const isDark = html.getAttribute('data-theme') === 'dark';
    if (isDark) {
        html.removeAttribute('data-theme');
        btn.innerHTML = '<i class="fas fa-moon"></i>';
        localStorage.setItem('theme', 'light');
    } else {
        html.setAttribute('data-theme', 'dark');
        btn.innerHTML = '<i class="fas fa-sun"></i>';
        localStorage.setItem('theme', 'dark');
    }
};
(function initTheme() {
    const saved = localStorage.getItem('theme');
    const btn = document.getElementById('themeToggle');
    if (saved === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (btn) btn.innerHTML = '<i class="fas fa-sun"></i>';
    }
})();

// ============ INVENTORY TABS ============
window.switchInventoryTab = function(tab, el) {
    document.querySelectorAll('.inventory-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.inventory-tab-content').forEach(c => c.classList.remove('active'));
    el.classList.add('active');
    document.getElementById('invTab-' + tab).classList.add('active');
    if (tab === 'movements') renderStockMovements();
};

window.filterStockMovements = function(val) {
    const q = (val || '').toLowerCase();
    document.querySelectorAll('#stockMovementsBody tr').forEach(tr => {
        tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
};

async function renderStockMovements() {
    const tbody = document.getElementById('stockMovementsBody');
    if (!tbody) return;
    tbody.innerHTML = skeletonRows(8);
    try {
        const movements = await apiGet('/inventory/movements?limit=100');
        if (!movements.length) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:40px"><i class="fas fa-history" style="font-size:32px;opacity:0.3;margin-bottom:8px;display:block"></i>لا توجد حركات مخزون بعد<br><small>عند إجراء عمليات بيع أو شراء أو تسوية، ستظهر هنا</small></td></tr>';
            return;
        }
        tbody.innerHTML = movements.map(m => {
            const typeColors = { 'SALE_OUT': 'var(--danger)', 'PURCHASE_IN': 'var(--success)', 'ADJUSTMENT_IN': 'var(--info)', 'ADJUSTMENT_OUT': 'var(--warning)' };
            const typeLabels = { 'SALE_OUT': 'بيع', 'PURCHASE_IN': 'مشتريات', 'ADJUSTMENT_IN': 'إضافة', 'ADJUSTMENT_OUT': 'خصم' };
            return `<tr>
                <td>${fmtDate(m.CreatedAt)}</td>
                <td>${m.ProductName || '-'}</td>
                <td><span style="color:${typeColors[m.MovementType] || 'var(--text-secondary)'};font-weight:600">${typeLabels[m.MovementType] || m.MovementType}</span></td>
                <td style="color:${m.Quantity > 0 ? 'var(--success)' : 'var(--danger)'};font-weight:600">${m.Quantity > 0 ? '+' : ''}${m.Quantity}</td>
                <td>${m.ReferenceType || '-'} ${m.ReferenceId || ''}</td>
                <td>${m.CreatedByName || '-'}</td>
            </tr>`;
        }).join('');
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:40px;color:var(--danger)"><i class="fas fa-exclamation-triangle" style="font-size:32px;margin-bottom:8px;display:block"></i>${err.message}<br><button class="btn btn-sm btn-primary mt-2" onclick="renderStockMovements()">إعادة المحاولة</button></td></tr>`;
    }
}

// ============ SORTABLE TABLES ============
document.addEventListener('click', function(e) {
    const th = e.target.closest('th.sortable');
    if (!th) return;
    const table = th.closest('table');
    const tbody = table.querySelector('tbody');
    if (!tbody) return;
    const colIdx = Array.from(th.parentNode.children).indexOf(th);
    const key = th.dataset.sort || '';
    const isAsc = th.classList.contains('asc');
    th.parentNode.querySelectorAll('th.sortable').forEach(t => { if (t !== th) { t.classList.remove('asc', 'desc'); } });
    th.classList.toggle('asc', !isAsc);
    th.classList.toggle('desc', isAsc);
    const rows = Array.from(tbody.querySelectorAll('tr'));
    if (!rows.length || rows[0].children.length <= colIdx) return;
    rows.sort((a, b) => {
        let va = a.children[colIdx]?.textContent.trim() || '';
        let vb = b.children[colIdx]?.textContent.trim() || '';
        const na = parseFloat(va.replace(/[^0-9.-]/g, ''));
        const nb = parseFloat(vb.replace(/[^0-9.-]/g, ''));
        if (!isNaN(na) && !isNaN(nb)) { va = na; vb = nb; }
        if (va < vb) return isAsc ? -1 : 1;
        if (va > vb) return isAsc ? 1 : -1;
        return 0;
    });
    rows.forEach(r => tbody.appendChild(r));
});

// ============ SYNC / CLOCK ============
window.syncData = function(btn) {
  btn.classList.add('rotating');
  renderPageContent(state.page);
  setTimeout(() => btn.classList.remove('rotating'), 1000);
};

function updateClock() {
  const el = document.getElementById('statusTime');
  if (el) el.textContent = new Date().toLocaleTimeString('ar-EG');
  const dt = document.getElementById('datetime');
  if (dt) dt.textContent = new Date().toLocaleString('ar-EG');
}
setInterval(updateClock, 1000);
updateClock();

// ============ INIT ============
document.getElementById('loginForm').addEventListener('submit', handleLogin);
document.querySelectorAll('.nav-item').forEach(el => {
  el.addEventListener('click', function() {
    const page = this.dataset.page;
    if (page) navigate(page);
  });
});
checkAuth();


async function renderExpensesPage() {
  const tbody = document.getElementById('expensesTableBody');
  if (!tbody) return;
  tbody.innerHTML = skeletonRows(5);
  try {
    const fin = await apiGet('/reports/financial');
    const expenses = (fin.Records || []).filter(r => r.RecordType === 'EXPENSE');
    tbody.innerHTML = expenses.length
      ? expenses.map(e => {
          const dt = new Date(e.RecordDate || e.CreatedAt);
          const dateStr = dt.toLocaleDateString('ar-EG') + ' ' + dt.toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' });
          return `
            <tr>
              <td>${e.RecordNumber}</td>
              <td>${e.Description || e.Category || '-'}</td>
              <td style="color:var(--danger);font-weight:bold">${fmtMoney(e.Amount)} ج.م</td>
              <td>${dateStr}</td>
              <td>${e.CreatedByName || '-'}</td>
            </tr>
          `;
        }).join('')
      : '<tr><td colspan="5" style="text-align:center;padding:40px">لا توجد مصاريف مسجلة بعد</td></tr>';
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:40px;color:var(--danger)">${err.message}</td></tr>`;
  }
}
