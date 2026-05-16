import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today


class TestHaulageTripCustody(FrappeTestCase):
	def test_custody_on_trip(self):
		# Create custody type
		ledger_account = frappe.db.get_value("Account", {"is_group": 0}, "name")
		if not ledger_account:
			self.skipTest("No ledger account found")

		cust_type = frappe.new_doc("Haulage Custody Type")
		cust_type.custody_name = "Test Custody Type For Trip"
		cust_type.account = ledger_account
		cust_type.insert()

		# Create trip with custody
		trip = frappe.new_doc("Haulage Trip")
		trip.append("trip_custodies", {
			"custody_type": cust_type.name,
			"amount": 1000,
			"custody_date": today(),
		})

		# Should fail without truck/driver but custody row should be valid
		self.assertEqual(len(trip.trip_custodies), 1)
		self.assertEqual(trip.trip_custodies[0].amount, 1000)
