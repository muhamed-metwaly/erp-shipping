import frappe
from frappe import _
from frappe.model.document import Document


class HaulageExpenseType(Document):
    def validate(self):
        if not self.account:
            return
        root_type = frappe.db.get_value("Account", self.account, "root_type")
        if root_type and root_type != "Expense":
            frappe.throw(
                _("The account must be an Expense account in the Chart of Accounts.")
            )
