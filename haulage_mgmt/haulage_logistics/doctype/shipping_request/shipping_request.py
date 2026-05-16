import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today

class ShippingRequest(Document):
    def validate(self):
        if not self.company:
            self.company = frappe.defaults.get_user_default("Company")
        if not (self.pickup_location or "").strip():
            frappe.throw(_("Pickup location is required."))
        if not (self.delivery_location or "").strip():
            frappe.throw(_("Delivery location is required."))
        if self.required_loading_date and self.expected_delivery_date:
            if getdate(self.expected_delivery_date) < getdate(self.required_loading_date):
                frappe.throw(
                    _("Expected delivery date cannot be before the required loading date.")
                )
        # Validate items child table
        if not self.get("items"): # This should prevent saving if no items, making stock integration meaningful
            frappe.throw(_("At least one item must be added to the shipping request."))
        for item in self.get("items"):
            if not item.item_code:
                frappe.throw(_("Item Code is required for all items."))
            if not item.qty or item.qty <= 0:
                frappe.throw(_("Quantity must be a positive number for all items."))

    def on_update(self):
        if self.flags.skip_delivery_note_creation:
            return
        old_doc = self.get_doc_before_save()
        if old_doc and old_doc.request_status != self.request_status:
            if self.request_status == "Out for Delivery":
                self._handle_out_for_delivery_status()
            elif self.request_status == "Delivered":
                self._handle_delivered_status()
            elif self.request_status == "Cancelled":
                self._handle_cancelled_status()

    def _handle_out_for_delivery_status(self):
        if self.delivery_note:
            return
        if not frappe.db.exists("DocType", "Delivery Note"):
            return
        if not self.get("items"):
            frappe.throw(_("Cannot create Delivery Note: No items in Shipping Request."))

        dn = frappe.new_doc("Delivery Note")
        dn.customer = self.customer
        dn.company = self.company or frappe.defaults.get_user_default("Company")
        if not dn.company:
            companies = frappe.get_all("Company", pluck="name", limit=1)
            dn.company = companies[0] if companies else None
        if not dn.company:
             frappe.throw(_("No company set for Delivery Note."))

        dn.posting_date = today()
        dn.set_warehouse = (
            frappe.get_cached_value("Company", dn.company, "default_warehouse")
            or frappe.db.get_value("Warehouse", {"company": dn.company, "is_group": 0}, "name")
        )
        if not dn.set_warehouse:
            frappe.throw(_("Please set a default warehouse for company {0} or configure one in Haulage Logistics Settings.").format(dn.company))

        dn.is_return = 0
        dn.customer_address = frappe.db.get_value("Customer", self.customer, "customer_primary_address")
        dn.shipping_address_name = dn.customer_address
        dn.from_warehouse = dn.set_warehouse

        dn.remarks = _("Delivery Note for Shipping Request: {0}").format(self.name)
        if frappe.get_meta("Delivery Note").has_field("custom_shipping_request"):
            dn.set("custom_shipping_request", self.name)

        for item_data in self.items:
            dn.append(
                "items",
                {
                    "item_code": item_data.item_code,
                    "qty": item_data.qty,
                    "uom": item_data.uom or frappe.db.get_value("Item", item_data.item_code, "stock_uom"),
                    "warehouse": dn.set_warehouse, # All items from same warehouse for this simple version
                    "rate": frappe.db.get_value("Item", item_data.item_code, "standard_rate") or 0, # Or pull from sales order if linked
                },
            )
        
        try:
            dn.insert(ignore_permissions=True)
            frappe.db.set_value("Shipping Request", self.name, "delivery_note", dn.name)
            self.delivery_note = dn.name
            frappe.msgprint(_("Delivery Note {0} created as draft.").format(dn.name), indicator="blue")
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), _("Failed to create Delivery Note for Shipping Request {0}").format(self.name))
            frappe.throw(_("Failed to create Delivery Note: {0}").format(e))

    def _handle_delivered_status(self):
        if self.delivery_note and frappe.db.exists("Delivery Note", self.delivery_note):
            dn = frappe.get_doc("Delivery Note", self.delivery_note)
            if dn.docstatus == 0: # If draft
                try:
                    dn.submit()
                    frappe.msgprint(_("Delivery Note {0} submitted.").format(dn.name), indicator="green")
                except Exception as e:
                    frappe.log_error(frappe.get_traceback(), _("Failed to submit Delivery Note {0} for Shipping Request {1}").format(dn.name, self.name))
                    frappe.throw(_("Failed to submit Delivery Note: {0}").format(e))
            elif dn.docstatus == 2: # If cancelled, can't submit
                frappe.throw(_("Linked Delivery Note {0} is cancelled and cannot be submitted.").format(dn.name))

    def _handle_cancelled_status(self):
        if self.delivery_note and frappe.db.exists("Delivery Note", self.delivery_note):
            dn = frappe.get_doc("Delivery Note", self.delivery_note)
            if dn.docstatus == 0: # If draft, can cancel
                try:
                    dn.cancel()
                    frappe.msgprint(_("Delivery Note {0} cancelled.").format(dn.name), indicator="red")
                except Exception as e:
                    frappe.log_error(frappe.get_traceback(), _("Failed to cancel Delivery Note {0} for Shipping Request {1}").format(dn.name, self.name))
                    frappe.throw(_("Failed to cancel Delivery Note: {0}").format(e))
            elif dn.docstatus == 1:
                frappe.throw(
                    _("Linked Delivery Note {0} is already submitted. Please cancel it manually before cancelling this request.").format(dn.name),
                    title=_("Cannot Cancel")
                )
