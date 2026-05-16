import frappe
from frappe.tests.utils import FrappeTestCase


class TestShippingRequest(FrappeTestCase):
	def test_sr_requires_items(self):
		sr = frappe.new_doc("Shipping Request")
		sr.customer = "_Test Customer"
		sr.pickup_location = "Test Pickup"
		sr.delivery_location = "Test Delivery"

		with self.assertRaises(frappe.ValidationError):
			sr.insert()

	def test_sr_requires_pickup_location(self):
		sr = frappe.new_doc("Shipping Request")
		sr.customer = "_Test Customer"
		sr.delivery_location = "Test Delivery"
		sr.append("items", {"item_code": "_Test Item", "qty": 1})

		with self.assertRaises(frappe.ValidationError):
			sr.insert()

	def test_sr_requires_delivery_location(self):
		sr = frappe.new_doc("Shipping Request")
		sr.customer = "_Test Customer"
		sr.pickup_location = "Test Pickup"
		sr.append("items", {"item_code": "_Test Item", "qty": 1})

		with self.assertRaises(frappe.ValidationError):
			sr.insert()

	def test_sr_delivery_date_before_loading_date(self):
		sr = frappe.new_doc("Shipping Request")
		sr.customer = "_Test Customer"
		sr.pickup_location = "Test Pickup"
		sr.delivery_location = "Test Delivery"
		sr.required_loading_date = "2026-06-01"
		sr.expected_delivery_date = "2026-05-01"
		sr.append("items", {"item_code": "_Test Item", "qty": 1})

		with self.assertRaises(frappe.ValidationError):
			sr.insert()

	def test_sr_valid_creation(self):
		sr = frappe.new_doc("Shipping Request")
		sr.customer = "_Test Customer"
		sr.pickup_location = "Test Pickup"
		sr.delivery_location = "Test Delivery"
		sr.append("items", {"item_code": "_Test Item", "qty": 1})
		sr.insert()

		self.assertEqual(sr.request_status, "New")
		self.assertEqual(len(sr.items), 1)
