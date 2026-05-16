# haulage_mgmt — Haulage Management for Frappe / ERPNext

Custom Frappe app (**`haulage_mgmt`**) for fleet haulage companies: master data, customer shipping requests, trip operations, per-trip financial allocation (revenue, expenses, custody), ERPNext billing, and operational reports.

**Repository:** [shaasie-solutions/newapp](https://github.com/shaasie-solutions/newapp)  
**Version:** see `haulage_mgmt/__init__.py` and Git tags (e.g. `v0.1.28`).  
**Requires:** [ERPNext](https://erpnext.com/) on the site.

---

## فكرة التطبيق (نظرة عامة)

التطبيق يغطي دورة عمل شركة نقل بري:

1. **البيانات الأساسية** — شاحنات، سائقون، أنواع مصروفات، أنواع عهد، عملاء، إعدادات الربط مع ERPNext.
2. **طلبات الشحن** — طلب من العميل (مواقع الاستلام والتسليم يدوياً، سعر متفق عليه، حالة الطلب).
3. **تشغيل رحلات الشحن** — رحلة تشغيلية: شاحنة، سائق، جدول شحنات (طلبات مرتبطة بالرحلة)، طباعة أوراق التشغيل. **لا تظهر المحاسبة هنا** لتبقى الشاشة بسيطة للميدان.
4. **حساب الرحلات** — قائمة مالية لكل الرحلات، ثم **ورقة حساب** لكل رحلة: ملخص إيراد من أسعار الطلبات، جدول **تخصيص مصروفات**، جدول **تخصيص عهد**، أزرار فاتورة مبيعات وقيد مصروفات (مسودة).
5. **التقارير** — تحليل حسب السائق، الرحلة، الشاحنة، أو سطور العهد، مع فلاتر تاريخ وسائق.

**صافي دخل الرحلة** (في القائمة والتقارير وورقة الحساب):

```text
Net income = Revenue − Expenses − Custody
```

- **Revenue:** مجموع `agreed_price` من طلبات الشحن المرتبطة بالرحلة (من جدول الشحنات).
- **Expenses:** مجموع مبالغ جدول `trip_expenses` على الرحلة.
- **Custody:** مجموع مبالغ جدول `trip_custodies` على الرحلة (عهد سائق/عهدة تشغيلية وليست بالضرورة قيداً محاسبياً فورياً).

---

## Application concept (English)

| Layer | What it does |
|--------|----------------|
| **Master data** | Trucks (name = document ID), drivers, expense types (with GL account), custody types, customers (ERPNext), settings |
| **Shipping requests** | Customer order: pickup/delivery text, agreed price, status synced when linked to trips |
| **Trip operations** | **All Trips** hub: operations list + accounting list; trip form with action buttons; two print formats |
| **ERPNext billing** | Draft **Sales Invoice** per shipment; draft **Journal Entry** for trip expenses (from settings) |
| **Reports** | Driver / trip / truck aggregates; custody line report |

---

## Install (Bench)

```bash
cd /path/to/frappe-bench
bench get-app https://github.com/shaasie-solutions/newapp.git --branch v0.1.29

bench --site yoursite.com install-app haulage_mgmt
bench --site yoursite.com migrate
bench build --app haulage_mgmt
bench --site yoursite.com clear-cache
```

Desk: **`/desk/haulage-logistics`** or app tile **Haulage Management**.

After code updates (you often reinstall the app):

```bash
bench --site yoursite.com uninstall-app haulage_mgmt
bench --site yoursite.com install-app haulage_mgmt
bench --site yoursite.com migrate
bench --site yoursite.com clear-cache
bench build --app haulage_mgmt
```

Hard-refresh the browser (**Ctrl+Shift+R**).

### Uninstall (clean removal)

To remove the app from a site **without leaving desk links, roles, or legacy pages**:

```bash
bench --site yoursite.com uninstall-app haulage_mgmt
bench --site yoursite.com clear-cache
```

This runs `before_uninstall` / `after_uninstall` hooks that remove:

- **Fleet Manager** role and user role assignments  
- **Haulage Logistics** workspace  
- Custom **pages** (All Trips, trip accounting redirects)  
- **Reports** and **print formats** (current and legacy names)  
- Legacy **DocTypes** if still on the site (**Shipment Preparation**, **Shipping Route**)  
- Fleet expiry **ToDo** reminders created by the app  

Frappe then drops all **Haulage** DocTypes and their data (trips, trucks, drivers, shipping requests, settings, etc.).

To remove the app from the bench entirely:

```bash
bench remove-app haulage_mgmt
```

### Arabic interface

1. Site language (optional): `bench --site yoursite.com set-config language ar`
2. Each user: **My Settings** → **Language** → **العربية**
3. After app update: `bench build --app haulage_mgmt` and `bench --site yoursite.com clear-cache`

Trip statuses, request statuses, truck/driver statuses, list views, reports, and custom pages use `haulage_mgmt/translations/ar.csv`. Values stay in English in the database; labels display in Arabic.

---

## Workspace layout (Haulage Logistics)

| # | Section (EN) | العربية | Contents |
|---|----------------|---------|----------|
| — | Master data | البيانات الأساسية | Truck, Driver, Haulage Expense Type, Haulage Custody Type, Customer, Haulage Logistics Settings |
| 1 | Shipping requests | طلبات الشحن | **Shipping Request** |
| 2 | Trip operations | تشغيل رحلات الشحن | **All Trips** hub (operations list + trip accounting), **New Haulage Trip**, action buttons on each trip |
| — | Reports | التقارير | Driver, Trip, Truck, Custody script reports |

---

## DocTypes and relationships

```text
Haulage Logistics Settings (Single)
    ├── default_freight_item → Item (Sales Invoice)
    └── trip_expense_credit_account → Account (Journal Entry credit)

Truck ──────────────┐
Driver ─────────────┼──► Haulage Trip
Company ────────────┘         │
                              ├── child: Haulage Trip Shipment → Shipping Request
                              ├── child: Haulage Trip Expense → Haulage Expense Type
                              ├── child: Haulage Trip Custody → Haulage Custody Type
                              └── trip_journal_entry → Journal Entry (optional)

Shipping Request ──► Customer (ERPNext)
                  └── agreed_price, pickup_location, delivery_location, request_status
```

### Main documents

| DocType | Role |
|---------|------|
| **Truck** | Fleet unit; name = `truck_name`; photo; status (Available, Reserved for Trip, Maintenance, Stopped) |
| **Driver** | Name = `full_name`; photo; Active/Inactive |
| **Shipping Request** | Customer shipment order; status driven by linked trip |
| **Haulage Trip** | Operational trip + (hidden) accounting child tables |
| **Haulage Expense Type** | Expense category + expense account for JE |
| **Haulage Custody Type** | Custody category (operational tracking) |

### Shipping request statuses (synced from trip)

| Trip status | Request status (typical) |
|-------------|---------------------------|
| Preparing | Goods Prepared |
| Started / Paused | Out for Delivery |
| Completed | Delivered |
| Cancelled | Goods Prepared |

---

## User workflows

### A. Setup (once)

1. **Haulage Logistics Settings:** company defaults, default freight **Item**, trip expense **credit account**.
2. Create **Trucks**, **Drivers**, **Haulage Expense Type** (with accounts), **Haulage Custody Type**.
3. Use ERPNext **Customer** records.

### B. Operations

1. Create **Shipping Request** (customer, locations, agreed price).
2. Create **Haulage Trip** (truck, driver, add shipment lines = shipping requests).
3. Use **Trip actions** on the trip form: **Start trip**, **Pause trip**, **Trip arrival**, **Cancel trip** (or open from **All Trips** list).
4. Print **Trip operations sheet** (shipments) or **Trip summary** (status, revenue, expenses, custody, net income).

### C. Trip accounting (same section 2)

1. Open **All Trips** → toolbar **Trip accounting** (or legacy route `trip-accounting` redirects here).
2. Filter by status if needed → click trip or **Open sheet**.
3. Accounting form shows:
   - Read-only header (trip, truck, driver, date)
   - **Revenue summary** (HTML from server)
   - **Expense allocation** grid — add rows, **Save**
   - **Custody allocation** grid — add rows, **Save**
4. **Revenue → Create Sales Invoice for shipment** (draft SI from agreed price).
5. **Accounting → Create expense journal (draft)** (groups expenses by account; links `trip_journal_entry`).

Operational trip form has a **Trip accounting** button that opens the same accounting mode.

### D. Reports

| Report | Grouping | Filters |
|--------|----------|---------|
| Haulage Driver Report | Per driver | Driver (optional), from/to date |
| Haulage Trip Report | Per trip | Same |
| Haulage Truck Report | Per truck | Same (trips filtered by driver if set) |
| Haulage Custody Report | Per custody line | Custody type, driver, dates |

Default period: current month. Summary cards show period totals where applicable.

---

## Repository structure

```text
newapp/
├── haulage_mgmt/
│   ├── hooks.py
│   ├── install.py              # migrations, workspace sync, legacy purge
│   ├── boot.py
│   ├── haulage_logistics/
│   │   ├── api.py              # set_trip_status, SI, journal entry
│   │   ├── trip_status.py      # status transitions (start/pause/arrive/cancel)
│   │   ├── trip_financials.py  # revenue / expenses / custody (single source)
│   │   ├── haulage_i18n.js     # shared status labels (desk JS)
│   │   ├── doctype/            # DocTypes + list views + haulage_trip.js
│   │   ├── page/
│   │   │   ├── trip_operations/    # main hub (operations + accounting lists)
│   │   │   ├── trip_accounting/    # re-exports API (compat)
│   │   │   └── trip_accounting_entry/  # redirect only
│   │   ├── report/             # report_utils.py, report_common.js, 4 reports
│   │   ├── print_format/       # Haulage Trip Operations | Haulage Trip Summary
│   │   └── workspace/
│   └── translations/ar.csv
├── README.md
└── CHANGELOG.md
```

### Code organization principles

- **One financial source:** `trip_financials.py` for list, form HTML, and print summary.
- **One trip hub:** `trip-operations` page (legacy `trip-accounting` URL redirects).
- **Status via buttons only:** `trip_status.py` + `api.set_trip_status` (no manual select on form).
- **Two prints per trip:** operations sheet (shipments) and summary (status + money).
- **after_migrate** removes obsolete reports, print formats, and duplicate desk pages.

---

## Whitelisted API

| Method | Purpose |
|--------|---------|
| `haulage_mgmt.haulage_logistics.api.create_sales_invoice_from_shipment` | Draft SI for one shipment on a trip |
| `haulage_mgmt.haulage_logistics.api.create_trip_expense_journal_entry` | Draft JE from `trip_expenses`; sets `trip_journal_entry` |
| `haulage_mgmt.haulage_logistics.api.set_trip_status` | Trip action: `start`, `pause`, `arrive`, `cancel` |
| `haulage_mgmt.haulage_logistics.page.trip_operations.trip_operations.get_trip_operations_list` | All trips list for operations desk |
| `haulage_mgmt.haulage_logistics.page.trip_operations.trip_operations.get_trip_accounting_list` | Trip accounting list (hub) |
| `haulage_mgmt.haulage_logistics.page.trip_operations.trip_operations.get_trip_operations_list` | Operations list (hub) |
| `haulage_mgmt.haulage_logistics.page.trip_operations.trip_operations.get_trip_accounting_detail` | Trip financial breakdown |
| `haulage_mgmt.haulage_logistics.page.trip_accounting.trip_accounting.get_trip_accounting_detail` | Revenue lines + totals for accounting form |

---

## Roles

- **System Manager** — full access  
- **Fleet Manager** — trips, requests, accounting page, reports  

---

## Technical notes (trip accounting UI)

- Accounting fields are **`hidden: 1` in DocType JSON** so the operational form stays clean even before JS runs.
- **Accounting mode** is entered via `frappe.route_options.haulage_accounting_entry` (from list or **Trip accounting** button).
- After **Save** in accounting mode, the layout is re-applied; a one-shot `sessionStorage` flag helps recover accounting mode after a full page reload.
- Child tables **`trip_expenses`** and **`trip_custodies`** are refreshed when the accounting layout is shown.

---

## License

MIT — see `license.txt`.
