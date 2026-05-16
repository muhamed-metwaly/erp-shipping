import frappe


def _first_company_name():
    rows = frappe.get_all("Company", pluck="name", order_by="creation asc", limit=1)
    return rows[0] if rows else None


def before_migrate():
    """Backfill SR locations; truck/driver name columns; clear legacy tables; Fleet Manager role."""
    _migrate_shipping_route_to_sr_locations()
    _prepare_truck_name_column()
    if frappe.db.exists("DocType", "Shipment Preparation"):
        try:
            frappe.db.sql("DELETE FROM `tabShipment Preparation`")
        except Exception:
            frappe.log_error(frappe.get_traceback(), "haulage_mgmt: clear Shipment Preparation")
    if frappe.db.exists("Role", "Fleet Manager"):
        return
    doc = frappe.new_doc("Role")
    doc.role_name = "Fleet Manager"
    doc.desk_access = 1
    doc.insert(ignore_permissions=True)


def after_install():
    """Run once on first install: create custom fields and ensure Fleet Manager role."""
    _create_custom_fields()
    if frappe.db.exists("Role", "Fleet Manager"):
        return
    doc = frappe.new_doc("Role")
    doc.role_name = "Fleet Manager"
    doc.desk_access = 1
    doc.insert(ignore_permissions=True)


def _migrate_shipping_route_to_sr_locations():
    """Before schema sync: add pickup/delivery columns if missing and copy from tabShipping Route."""
    if not frappe.db.exists("DocType", "Shipping Request"):
        return
    if not frappe.db.has_column("Shipping Request", "pickup_location"):
        try:
            frappe.db.add_column("Shipping Request", "pickup_location", "Data")
        except Exception:
            frappe.log_error(frappe.get_traceback(), "haulage_mgmt: add_column pickup_location")
    if not frappe.db.has_column("Shipping Request", "delivery_location"):
        try:
            frappe.db.add_column("Shipping Request", "delivery_location", "Data")
        except Exception:
            frappe.log_error(frappe.get_traceback(), "haulage_mgmt: add_column delivery_location")
    if not frappe.db.exists("DocType", "Shipping Route"):
        return
    if not frappe.db.has_column("Shipping Request", "shipping_route"):
        return
    try:
        frappe.db.sql(
            """
            UPDATE `tabShipping Request` sr
            INNER JOIN `tabShipping Route` r ON r.name = sr.shipping_route
            SET
                sr.pickup_location = COALESCE(NULLIF(TRIM(sr.pickup_location), ''), r.loading_city),
                sr.delivery_location = COALESCE(NULLIF(TRIM(sr.delivery_location), ''), r.delivery_city)
            WHERE IFNULL(sr.shipping_route, '') != ''
            """
        )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "haulage_mgmt: copy Shipping Route into SR locations")


def after_migrate():
    """Purge replaced desk artifacts; backfill Company on legacy trips."""
    _create_custom_fields()
    _migrate_truck_and_driver_document_names()
    _migrate_truck_busy_to_reserved()
    _purge_legacy_haulage_reports()
    _purge_legacy_haulage_print_formats()
    if not frappe.db.exists("DocType", "Haulage Trip"):
        return
    company = _first_company_name()
    if not company:
        return
    frappe.db.sql(
        """
        UPDATE `tabHaulage Trip`
        SET company = %s
        WHERE IFNULL(company, '') = ''
        """,
        (company,),
    )


def _prepare_truck_name_column():
    """Add truck_name before schema sync; seed from license plate or legacy document name."""
    if not frappe.db.exists("DocType", "Truck"):
        return
    if not frappe.db.has_column("Truck", "truck_name"):
        try:
            frappe.db.add_column("Truck", "truck_name", "Data")
        except Exception:
            frappe.log_error(frappe.get_traceback(), "haulage_mgmt: add_column truck_name")
            return
    try:
        frappe.db.sql(
            """
            UPDATE `tabTruck`
            SET truck_name = COALESCE(
                NULLIF(TRIM(truck_name), ''),
                NULLIF(TRIM(license_plate), ''),
                name
            )
            WHERE IFNULL(TRIM(truck_name), '') = ''
            """
        )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "haulage_mgmt: backfill truck_name")


def _migrate_truck_and_driver_document_names():
    """Rename legacy series IDs (TRUCK-.#### / DRV-.####) to human-readable names."""
    if frappe.db.exists("DocType", "Truck") and frappe.db.has_column("Truck", "truck_name"):
        _rename_fleet_docs_to_name_field("Truck", "truck_name")
    if frappe.db.exists("DocType", "Driver") and frappe.db.has_column("Driver", "full_name"):
        _rename_fleet_docs_to_name_field("Driver", "full_name")


def _rename_fleet_docs_to_name_field(doctype, name_field):
    rows = frappe.get_all(doctype, fields=["name", name_field], order_by="creation asc")
    for row in rows:
        target = (row.get(name_field) or "").strip()
        if not target or row.name == target:
            continue
        if frappe.db.exists(doctype, target):
            frappe.log_error(
                title=f"haulage_mgmt: skip rename {doctype}",
                message=f"Cannot rename {row.name} to {target}: name already exists.",
            )
            continue
        try:
            frappe.rename_doc(doctype, row.name, target, force=True, merge=False)
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"haulage_mgmt: rename {doctype} {row.name} -> {target}",
            )


def _migrate_truck_busy_to_reserved():
    """Rename legacy truck status Busy -> Reserved for Trip on existing rows."""
    if not frappe.db.exists("DocType", "Truck"):
        return
    frappe.db.sql(
        "UPDATE `tabTruck` SET truck_status = %s WHERE truck_status = %s",
        ("Reserved for Trip", "Busy"),
    )


def _purge_legacy_haulage_print_formats():
    """Remove replaced trip print formats (merged into Operations + Summary)."""
    if not frappe.db.exists("DocType", "Print Format"):
        return
    for pf in (
        "Haulage Trip Dispatch",
        "Haulage Trip Shipments Sheet",
    ):
        if not frappe.db.exists("Print Format", pf):
            continue
        try:
            frappe.delete_doc("Print Format", pf, force=True, ignore_permissions=True)
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"haulage_mgmt: purge legacy print format {pf}")


def _purge_legacy_haulage_reports():
    """Remove replaced script reports so desk links stay valid after upgrades."""
    if not frappe.db.exists("DocType", "Report"):
        return
    for report in (
        "Trip Financial Summary",
        "Driver Performance",
        "Truck Performance",
        "Haulage Operations Summary",
    ):
        if not frappe.db.exists("Report", report):
            continue
        try:
            frappe.delete_doc("Report", report, force=True, ignore_permissions=True)
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"haulage_mgmt: purge legacy report {report}")


def before_uninstall():
    """Remove desk artifacts, custom role, and legacy DocTypes so the site stays clean."""
    _uninstall_remove_haulage_todos()
    _uninstall_remove_workspace()
    _uninstall_remove_pages()
    _uninstall_remove_reports()
    _uninstall_remove_print_formats()
    _uninstall_remove_legacy_doctypes()
    _uninstall_remove_fleet_manager_role()
    _uninstall_remove_module_def()


def after_uninstall():
    """Final cache clear after Frappe drops app DocTypes."""
    try:
        frappe.clear_cache()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "haulage_mgmt after_uninstall: clear_cache")


def _uninstall_delete_doc(doctype, name):
    if not name or not frappe.db.exists(doctype, name):
        return
    try:
        frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"haulage_mgmt uninstall: delete {doctype} {name}",
        )


def _uninstall_remove_fleet_manager_role():
    role = "Fleet Manager"
    if not frappe.db.exists("Role", role):
        return
    frappe.db.sql("DELETE FROM `tabHas Role` WHERE role=%s", (role,))
    _uninstall_delete_doc("Role", role)


def _uninstall_remove_workspace():
    _uninstall_delete_doc("Workspace", "Haulage Logistics")


def _uninstall_remove_pages():
    for page in (
        "trip-operations",
        "trip-accounting",
        "trip-accounting-entry",
    ):
        _uninstall_delete_doc("Page", page)


def _uninstall_remove_reports():
    for report in (
        "Haulage Driver Report",
        "Haulage Trip Report",
        "Haulage Truck Report",
        "Haulage Custody Report",
        "Trip Financial Summary",
        "Driver Performance",
        "Truck Performance",
        "Haulage Operations Summary",
    ):
        _uninstall_delete_doc("Report", report)


def _uninstall_remove_print_formats():
    for pf in (
        "Haulage Trip Operations",
        "Haulage Trip Summary",
        "Haulage Trip Dispatch",
        "Haulage Trip Shipments Sheet",
    ):
        _uninstall_delete_doc("Print Format", pf)


def _uninstall_remove_legacy_doctypes():
    """DocTypes removed from the app in older versions but may still exist on the site."""
    for dt in ("Shipment Preparation", "Shipping Route"):
        if not frappe.db.exists("DocType", dt):
            continue
        _uninstall_delete_doc("DocType", dt)


def _uninstall_remove_module_def():
    _uninstall_delete_doc("Module Def", "Haulage Logistics")


def _uninstall_remove_haulage_todos():
    if not frappe.db.exists("DocType", "ToDo"):
        return
    try:
        frappe.db.sql(
            "DELETE FROM `tabToDo` WHERE description LIKE %s",
            ("Haulage%",),
        )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "haulage_mgmt uninstall: ToDo cleanup")


def _create_custom_fields():
    custom_fields = [
        {
            "dt": "Delivery Note",
            "fieldname": "custom_shipping_request",
            "fieldtype": "Link",
            "label": "Shipping Request",
            "options": "Shipping Request",
            "insert_after": "customer",
            "read_only": 1,
            "hidden": 0,
            "print_hide": 1,
        },
    ]
    for cf in custom_fields:
        full_name = f"{cf['dt']}-{cf['fieldname']}"
        if frappe.db.exists("Custom Field", full_name):
            continue
        try:
            doc = frappe.get_doc({
                "doctype": "Custom Field",
                **cf,
            })
            doc.insert(ignore_permissions=True)
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"haulage_mgmt: create custom field {full_name}",
            )
