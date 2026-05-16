import frappe
from frappe.tests.utils import FrappeTestCase


class TestHaulageTrip(FrappeTestCase):
	def setUp(self):
		# Create test truck
		if not frappe.db.exists("Truck", "Test Truck"):
			truck = frappe.new_doc("Truck")
			truck.truck_name = "Test Truck"
			truck.truck_status = "Available"
			truck.insert(ignore_permissions=True)

		# Create test driver
		if not frappe.db.exists("Driver", "Test Driver"):
			driver = frappe.new_doc("Driver")
			driver.full_name = "Test Driver"
			driver.driver_status = "Active"
			driver.insert(ignore_permissions=True)

		# Create test shipping request
		if not frappe.db.exists("Shipping Request", "Test SR"):
			sr = frappe.new_doc("Shipping Request")
			sr.customer = "_Test Customer"
			sr.pickup_location = "Test Pickup"
			sr.delivery_location = "Test Delivery"
			sr.request_status = "New"
			sr.append("items", {"item_code": "_Test Item", "qty": 1})
			sr.name = "Test SR"
			sr.insert(ignore_permissions=True)

	def test_create_trip_with_shipment(self):
		trip = frappe.new_doc("Haulage Trip")
		trip.truck = "Test Truck"
		trip.driver = "Test Driver"
		trip.append("shipments", {"shipping_request": "Test SR"})
		trip.insert()

		self.assertEqual(trip.trip_status, "Preparing")
		self.assertEqual(len(trip.shipments), 1)

	def test_trip_requires_shipment(self):
		trip = frappe.new_doc("Haulage Trip")
		trip.truck = "Test Truck"
		trip.driver = "Test Driver"

		with self.assertRaises(frappe.ValidationError):
			trip.insert()

	def test_duplicate_shipment_rejected(self):
		trip = frappe.new_doc("Haulage Trip")
		trip.truck = "Test Truck"
		trip.driver = "Test Driver"
		trip.append("shipments", {"shipping_request": "Test SR"})
		trip.append("shipments", {"shipping_request": "Test SR"})

		with self.assertRaises(frappe.ValidationError):
			trip.insert()
