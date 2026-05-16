import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class Truck(Document):
    def validate(self):
        if not (self.truck_name or "").strip():
            frappe.throw(_("Truck name is required."))
        self.truck_name = self.truck_name.strip()
        current_date = getdate(today())
        
        if self.license_end_date and getdate(self.license_end_date) < current_date:
            if self.truck_status in ("Available", "Reserved for Trip"):
                frappe.throw(_("Truck license is expired. Truck cannot be Available or Reserved for Trip."), title=_("License Expired"))
            else:
                frappe.msgprint(_("Truck license is expired."), indicator="red", title=_("License Expired"))
        
        if self.insurance_end_date and getdate(self.insurance_end_date) < current_date:
            if self.truck_status in ("Available", "Reserved for Trip"):
                frappe.throw(_("Truck insurance is expired. Truck cannot be Available or Reserved for Trip."), title=_("Insurance Expired"))
            else:
                frappe.msgprint(_("Truck insurance is expired."), indicator="orange", title=_("Insurance Expired"))
