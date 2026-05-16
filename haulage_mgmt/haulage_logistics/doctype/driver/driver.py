import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class Driver(Document):
    def validate(self):
        if not (self.full_name or "").strip():
            frappe.throw(_("Driver name is required."))
        self.full_name = self.full_name.strip()
        if self.license_expiry and getdate(self.license_expiry) < getdate(today()):
            # If license is expired, ensure driver is not active.
            # A driver cannot legally operate with an expired license.
            if self.driver_status == "Active":
                frappe.throw(_("Driver license is expired. Driver cannot be set to Active."), title=_("License Expired"))
            else:
                frappe.msgprint(_("Driver license is expired. Consider changing status to Suspended."), indicator="red", title=_("License Expired"))
