"""Desk page API: trip operations list and trip accounting list (single hub)."""

import frappe
from frappe import _
from frappe.utils import getdate

from haulage_mgmt.haulage_logistics.report.report_utils import (
    normalize_money_rows,
    trip_metrics_subquery,
)
from haulage_mgmt.haulage_logistics.trip_financials import get_trip_financial_summary


@frappe.whitelist()
def get_trip_operations_list(status=None):
    """Operational list: trip, status, driver, truck, date."""
    if not frappe.has_permission("Haulage Trip", "read"):
        frappe.throw(_("You do not have permission to read trips."), frappe.PermissionError)
    return _trip_hub_rows(status, include_financials=False)


@frappe.whitelist()
def get_all_trips_hub(status=None):
    """Unified All Trips list: status, driver, truck, date, revenue, expenses, custody, net."""
    if not frappe.has_permission("Haulage Trip", "read"):
        frappe.throw(_("You do not have permission to read trips."), frappe.PermissionError)
    try:
        return _trip_hub_rows(status, include_financials=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "haulage_mgmt: get_all_trips_hub SQL failed")
        return _trip_hub_rows_python(status)


def _trip_hub_rows(status=None, include_financials=False):
    if include_financials:
        conditions = ["1=1"]
        values = []
        if status:
            conditions.append("ht.trip_status = %s")
            values.append(status)
        where = " AND ".join(conditions)
        rows = frappe.db.sql(
            f"""
            SELECT *
            FROM ({trip_metrics_subquery(where)}) AS fin
            ORDER BY fin.trip_modified DESC, fin.trip DESC
            LIMIT 500
            """,
            tuple(values),
            as_dict=True,
        )
        normalize_money_rows(rows)
        return rows

    filters = {}
    if status:
        filters["trip_status"] = status
    rows = frappe.get_all(
        "Haulage Trip",
        filters=filters,
        fields=["name", "trip_status", "truck", "driver", "departure_date", "modified"],
        order_by="modified desc",
        limit_page_length=500,
    )
    for row in rows:
        row["trip"] = row.name
        dt = row.departure_date or row.modified
        row["trip_date"] = getdate(dt) if dt else None
    return rows


def _trip_hub_rows_python(status=None):
    """Reliable fallback when SQL metrics query fails (e.g. missing child tables)."""
    filters = {}
    if status:
        filters["trip_status"] = status
    rows = frappe.get_all(
        "Haulage Trip",
        filters=filters,
        fields=["name", "trip_status", "truck", "driver", "departure_date", "modified"],
        order_by="modified desc",
        limit_page_length=500,
    )
    out = []
    for row in rows:
        fin = get_trip_financial_summary(row.name)
        dt = row.departure_date or row.modified
        out.append(
            {
                "trip": row.name,
                "trip_status": row.trip_status,
                "driver": row.driver,
                "truck": row.truck,
                "trip_date": getdate(dt) if dt else None,
                "trip_modified": row.modified,
                "revenue": fin.get("total_revenue", 0),
                "expenses": fin.get("total_expenses", 0),
                "custody_total": fin.get("total_custody", 0),
                "net_income": fin.get("net_income", 0),
            }
        )
    normalize_money_rows(out)
    return out


@frappe.whitelist()
def get_trip_accounting_list(status=None):
    """Accounting list: revenue, expenses, custody, net income per trip."""
    if not frappe.has_permission("Haulage Trip", "read"):
        frappe.throw(_("You do not have permission to read trips."), frappe.PermissionError)
    conditions = ["1=1"]
    values = []
    if status:
        conditions.append("ht.trip_status = %s")
        values.append(status)

    where = " AND ".join(conditions)
    rows = frappe.db.sql(
        f"""
        SELECT *
        FROM ({trip_metrics_subquery(where)}) AS fin
        ORDER BY fin.trip_date DESC, fin.trip DESC
        LIMIT 500
        """,
        tuple(values),
        as_dict=True,
    )
    normalize_money_rows(rows)
    return rows


@frappe.whitelist()
def get_trip_accounting_detail(trip_name):
    """Financial breakdown for accounting form and print summary."""
    trip_name = (trip_name or "").strip()
    if not trip_name:
        frappe.throw(_("Trip name is required."), title=_("Missing Parameter"))
    if not frappe.has_permission("Haulage Trip", "read", doc=trip_name):
        frappe.throw(_("You do not have permission to read this trip."), frappe.PermissionError)
    return get_trip_financial_summary(trip_name)
