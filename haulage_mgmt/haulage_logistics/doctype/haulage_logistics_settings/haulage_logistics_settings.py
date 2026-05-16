import frappe
from frappe import _
from frappe.model.document import Document


class HaulageLogisticsSettings(Document):
    def validate(self):
        if self.default_freight_item:
            if not frappe.db.exists("Item", self.default_freight_item):
                frappe.throw(_("Default Freight Item does not exist."))
        if self.trip_expense_credit_account:
            root = frappe.get_cached_value("Account", self.trip_expense_credit_account, "root_type")
            if root == "Expense":
                frappe.throw(
                    _("The credit account for trip expenses must not be an Expense account.")
                )
