import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days


class TestTruck(FrappeTestCase):
	def test_truck_valid_creation(self):
		truck = frappe.new_doc("Truck")
		truck.truck_name = "Test Truck Valid"
		truck.truck_status = "Available"
		truck.insert()

		self.assertEqual(truck.truck_status, "Available")

	def test_truck_expired_license_blocked(self):
		truck = frappe.new_doc("Truck")
		truck.truck_name = "Test Truck Expired License"
		truck.truck_status = "Available"
		truck.license_end_date = add_days(today(), -1)

		with self.assertRaises(frappe.ValidationError):
			truck.insert()

	def test_truck_expired_insurance_blocked(self):
		truck = frappe.new_doc("Truck")
		truck.truck_name = "Test Truck Expired Insurance"
		truck.truck_status = "Available"
		truck.insurance_end_date = add_days(today(), -1)

		with self.assertRaises(frappe.ValidationError):
			truck.insert()
