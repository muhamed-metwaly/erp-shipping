"""Desk / app launcher hooks (importable without circular deps)."""


def check_haulage_app_permission():
    """Show Haulage on the app switcher for logged-in desk users."""
    import frappe

    if frappe.session.user == "Guest":
        return False
    if "System Manager" in frappe.get_roles():
        return True
    ws_exists = frappe.db.get_cached_value("Workspace", "Haulage Logistics", "name")
    if ws_exists:
        return frappe.has_permission("Workspace", "read", doc="Haulage Logistics")
    return True
