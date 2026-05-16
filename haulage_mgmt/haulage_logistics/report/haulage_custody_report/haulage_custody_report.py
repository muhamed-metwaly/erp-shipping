import frappe
from frappe import _
from frappe.utils import flt


def get_filters():
    return [
        {
            "fieldname": "custody_type",
            "label": _("Custody Type"),
            "fieldtype": "Link",
            "options": "Haulage Custody Type",
            "reqd": 0,
        },
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


def _build_where(filters):
    conditions = []
    values = []
    if filters.get("custody_type"):
        conditions.append("c.custody_type = %s")
        values.append(filters["custody_type"])
    if filters.get("driver"):
        conditions.append("ht.driver = %s")
        values.append(filters["driver"])
    if filters.get("from_date"):
        conditions.append("DATE(COALESCE(c.custody_date, ht.departure_date, ht.modified)) >= %s")
        values.append(filters["from_date"])
    if filters.get("to_date"):
        conditions.append("DATE(COALESCE(c.custody_date, ht.departure_date, ht.modified)) <= %s")
        values.append(filters["to_date"])
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    return where_clause, values


def execute(filters=None):
    filters = filters or {}
    where_clause, values = _build_where(filters)

    columns = [
        {
            "label": _("Trip No."),
            "fieldname": "trip",
            "fieldtype": "Link",
            "options": "Haulage Trip",
            "width": 130,
        },
        {"label": _("Date"), "fieldname": "custody_date", "fieldtype": "Date", "width": 100},
        {"label": _("Driver"), "fieldname": "driver", "fieldtype": "Link", "options": "Driver", "width": 120},
        {
            "label": _("Custody Type"),
            "fieldname": "custody_type",
            "fieldtype": "Link",
            "options": "Haulage Custody Type",
            "width": 140,
        },
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 110},
        {"label": _("Custody Holder"), "fieldname": "party", "fieldtype": "Data", "width": 120},
        {"label": _("Remarks"), "fieldname": "remarks", "fieldtype": "Data", "width": 160},
    ]

    if not frappe.db.table_exists("Haulage Trip Custody"):
        return columns, []

    data = frappe.db.sql(
        f"""
        SELECT
            ht.name AS trip,
            c.custody_date,
            ht.driver,
            c.custody_type,
            c.amount,
            c.party,
            c.remarks
        FROM `tabHaulage Trip Custody` c
        INNER JOIN `tabHaulage Trip` ht ON ht.name = c.parent
        WHERE {where_clause}
        ORDER BY c.custody_date DESC, ht.name DESC, c.idx
        """,
        tuple(values),
        as_dict=True,
    )
    for row in data:
        row["amount"] = flt(row.get("amount"))
    total = sum(flt(row.get("amount")) for row in data)
    report_summary = (
        [{"label": _("Total custody"), "value": total, "datatype": "Currency", "indicator": "Blue"}]
        if data
        else []
    )
    return columns, data, None, None, report_summary
