"""Shared SQL helpers for haulage script reports."""

from frappe.utils import flt


def driver_date_filters():
    from frappe import _

    return [
        {
            "fieldname": "driver",
            "label": _("Driver"),
            "fieldtype": "Link",
            "options": "Driver",
            "reqd": 0,
        },
        {
            "fieldname": "from_date",
            "label": _("From date"),
            "fieldtype": "Date",
            "reqd": 0,
        },
        {
            "fieldname": "to_date",
            "label": _("To date"),
            "fieldtype": "Date",
            "reqd": 0,
        },
    ]


def build_trip_where(filters):
    conditions = []
    values = []
    if filters.get("driver"):
        conditions.append("ht.driver = %s")
        values.append(filters["driver"])
    if filters.get("from_date"):
        conditions.append("DATE(COALESCE(ht.departure_date, ht.modified)) >= %s")
        values.append(filters["from_date"])
    if filters.get("to_date"):
        conditions.append("DATE(COALESCE(ht.departure_date, ht.modified)) <= %s")
        values.append(filters["to_date"])
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    return where_clause, values


def trip_metrics_subquery(where_clause):
    """Per-trip revenue, expenses, custody, and net income for script reports."""
    return f"""
        SELECT
            ht.name AS trip,
            ht.trip_status,
            ht.driver,
            ht.truck,
            DATE(COALESCE(ht.departure_date, ht.modified)) AS trip_date,
            ht.modified AS trip_modified,
            (
                SELECT COUNT(DISTINCT s.shipping_request)
                FROM `tabHaulage Trip Shipment` s
                WHERE s.parent = ht.name
            ) AS shipment_count,
            IFNULL(rev.revenue, 0) AS revenue,
            IFNULL(exp.expenses, 0) AS expenses,
            IFNULL(cust.custody_total, 0) AS custody_total,
            IFNULL(rev.revenue, 0) - IFNULL(exp.expenses, 0) - IFNULL(cust.custody_total, 0) AS net_income
        FROM `tabHaulage Trip` ht
        LEFT JOIN (
            SELECT parent, SUM(amount) AS expenses
            FROM `tabHaulage Trip Expense`
            GROUP BY parent
        ) exp ON exp.parent = ht.name
        LEFT JOIN (
            SELECT parent, SUM(amount) AS custody_total
            FROM `tabHaulage Trip Custody`
            GROUP BY parent
        ) cust ON cust.parent = ht.name
        LEFT JOIN (
            SELECT s.parent, SUM(IFNULL(sr.agreed_price, 0)) AS revenue
            FROM `tabHaulage Trip Shipment` s
            INNER JOIN `tabShipping Request` sr ON sr.name = s.shipping_request
            GROUP BY s.parent
        ) rev ON rev.parent = ht.name
        WHERE {where_clause}
    """


def money_report_summary(data):
    """Desk summary cards for revenue / expenses / custody / net income."""
    from frappe import _

    if not data:
        return []
    revenue = sum(flt(row.get("revenue")) for row in data)
    expenses = sum(flt(row.get("expenses")) for row in data)
    custody = sum(flt(row.get("custody_total")) for row in data)
    net = sum(flt(row.get("net_income")) for row in data)
    return [
        {"label": _("Total revenue"), "value": revenue, "datatype": "Currency", "indicator": "Blue"},
        {"label": _("Total expenses"), "value": expenses, "datatype": "Currency", "indicator": "Orange"},
        {"label": _("Total custody"), "value": custody, "datatype": "Currency", "indicator": "Grey"},
        {
            "label": _("Total net income"),
            "value": net,
            "datatype": "Currency",
            "indicator": "Green" if net >= 0 else "Red",
        },
    ]


def normalize_money_rows(data):
    for row in data:
        row["revenue"] = flt(row.get("revenue"))
        row["expenses"] = flt(row.get("expenses"))
        if "custody_total" in row:
            row["custody_total"] = flt(row.get("custody_total"))
        row["net_income"] = flt(row.get("net_income"))
        if "shipment_count" in row:
            row["shipment_count"] = int(row.get("shipment_count") or 0)
        if "trip_count" in row:
            row["trip_count"] = int(row.get("trip_count") or 0)
        if "avg_net_per_trip" in row:
            row["avg_net_per_trip"] = flt(row.get("avg_net_per_trip"))
