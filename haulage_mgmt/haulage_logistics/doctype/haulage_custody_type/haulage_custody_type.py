import frappe
from frappe import _
from frappe.model.document import Document


class HaulageCustodyType(Document):
    def validate(self):
        if not self.account:
            return
        if frappe.db.get_value("Account", self.account, "is_group"):
            frappe.throw(_("Please select a ledger account, not a group account."))
