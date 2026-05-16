import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days


class TestDriver(FrappeTestCase):
	def test_driver_valid_creation(self):
		driver = frappe.new_doc("Driver")
		driver.full_name = "Test Driver Valid"
		driver.driver_status = "Active"
		driver.insert()

		self.assertEqual(driver.driver_status, "Active")

	def test_driver_expired_license_blocked(self):
		driver = frappe.new_doc("Driver")
		driver.full_name = "Test Driver Expired"
		driver.driver_status = "Active"
		driver.license_expiry = add_days(today(), -1)

		with self.assertRaises(frappe.ValidationError):
			driver.insert()

	def test_driver_suspended_allowed(self):
		driver = frappe.new_doc("Driver")
		driver.full_name = "Test Driver Suspended"
		driver.driver_status = "Suspended"
		driver.license_expiry = add_days(today(), -1)
		driver.insert()

		self.assertEqual(driver.driver_status, "Suspended")
