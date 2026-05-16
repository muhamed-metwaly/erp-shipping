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
        {"label": _("Driver"), "fieldname": "driver", "fieldtype": "Link", "options": "Driver", "width": 160},
        {"label": _("Trip count"), "fieldname": "trip_count", "fieldtype": "Int", "width": 100},
        {"label": _("Shipment count"), "fieldname": "shipment_count", "fieldtype": "Int", "width": 110},
        {"label": _("Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 120},
        {"label": _("Expenses"), "fieldname": "expenses", "fieldtype": "Currency", "width": 120},
        {"label": _("Custody"), "fieldname": "custody_total", "fieldtype": "Currency", "width": 120},
        {"label": _("Net income"), "fieldname": "net_income", "fieldtype": "Currency", "width": 120},
        {
            "label": _("Avg net per trip"),
            "fieldname": "avg_net_per_trip",
            "fieldtype": "Currency",
            "width": 120,
        },
    ]

    data = frappe.db.sql(
        f"""
        SELECT
            tm.driver AS driver,
            COUNT(*) AS trip_count,
            SUM(tm.shipment_count) AS shipment_count,
            SUM(tm.revenue) AS revenue,
            SUM(tm.expenses) AS expenses,
            SUM(tm.custody_total) AS custody_total,
            SUM(tm.net_income) AS net_income,
            CASE WHEN COUNT(*) > 0 THEN SUM(tm.net_income) / COUNT(*) ELSE 0 END AS avg_net_per_trip
        FROM ({trip_sql}) AS tm
        WHERE IFNULL(tm.driver, '') != ''
        GROUP BY tm.driver
        ORDER BY SUM(tm.revenue) DESC, tm.driver
        """,
        tuple(values),
        as_dict=True,
    )
    normalize_money_rows(data)
    return columns, data, None, None, money_report_summary(data)


def get_filters():
    return driver_date_filters()
