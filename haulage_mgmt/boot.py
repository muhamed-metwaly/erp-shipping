"""Desk / app launcher hooks (importable without circular deps)."""


def check_haulage_app_permission():
    """Show Haulage on the app switcher for logged-in desk users."""
    import frappe

    if frappe.session.user == "Guest":
        return False
    if "System Manager" in frappe.get_roles():
        return True
    if frappe.db.exists("Workspace", "Haulage Logistics"):
        return frappe.has_permission("Workspace", "read", doc="Haulage Logistics")
    return True
