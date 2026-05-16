import frappe
from frappe import _

from haulage_mgmt.haulage_logistics.report.report_utils import (
    build_trip_where,
    driver_date_filters,
    money_report_summary,
    normalize_money_rows,
    trip_metrics_subquery,
)


def execute(filters=None):
    filters = filters or {}
    where_clause, values = build_trip_where(filters)
    trip_sql = trip_metrics_subquery(where_clause)

    columns = [
        {
            "label": _("Trip No."),
            "fieldname": "trip",
            "fieldtype": "Link",
            "options": "Haulage Trip",
            "width": 140,
        },
        {"label": _("Date"), "fieldname": "trip_date", "fieldtype": "Date", "width": 100},
        {"label": _("Status"), "fieldname": "trip_status", "fieldtype": "Data", "width": 100},
        {"label": _("Driver"), "fieldname": "driver", "fieldtype": "Link", "options": "Driver", "width": 120},
        {"label": _("Truck"), "fieldname": "truck", "fieldtype": "Link", "options": "Truck", "width": 120},
        {"label": _("Shipment count"), "fieldname": "shipment_count", "fieldtype": "Int", "width": 110},
        {"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 110},
        {"label": _("Expenses"), "fieldname": "expenses", "fieldtype": "Currency", "width": 110},
        {"label": _("Custody"), "fieldname": "custody_total", "fieldtype": "Currency", "width": 110},
        {"label": _("Net income"), "fieldname": "net_income", "fieldtype": "Currency", "width": 110},
    ]

    data = frappe.db.sql(
        f"""
        SELECT
            trip, trip_date, trip_status, driver, truck,
            shipment_count, revenue, expenses, custody_total, net_income
        FROM ({trip_sql}) AS tm
        ORDER BY trip_date DESC, trip_modified DESC
        """,
        tuple(values),
        as_dict=True,
    )
    normalize_money_rows(data)
    return columns, data, None, None, money_report_summary(data)


def get_filters():
    return driver_date_filters()
