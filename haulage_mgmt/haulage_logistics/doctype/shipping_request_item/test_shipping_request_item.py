import frappe
from frappe.tests.utils import FrappeTestCase


class TestShippingRequestItem(FrappeTestCase):
	def test_item_requires_item_code(self):
		item = frappe.new_doc("Shipping Request Item")
		# Should require item_code field
		self.assertFalse(item.item_code)

	def test_item_on_shipping_request(self):
		# Create shipping request with item
		sr = frappe.new_doc("Shipping Request")
		sr.customer = "_Test Customer"
		sr.pickup_location = "Test Pickup"
		sr.delivery_location = "Test Delivery"
		sr.append("items", {
			"item_code": "_Test Item",
			"qty": 5,
		})
		sr.insert()

		self.assertEqual(len(sr.items), 1)
		self.assertEqual(sr.items[0].item_code, "_Test Item")
		self.assertEqual(sr.items[0].qty, 5)
