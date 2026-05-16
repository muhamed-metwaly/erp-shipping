import frappe
from frappe.tests.utils import FrappeTestCase


class TestHaulageCustodyType(FrappeTestCase):
	def test_custody_type_valid_creation(self):
		# Find a ledger account (not group)
		ledger_account = frappe.db.get_value("Account", {"is_group": 0}, "name")
		if not ledger_account:
			self.skipTest("No ledger account found")

		cust_type = frappe.new_doc("Haulage Custody Type")
		cust_type.custody_name = "Test Driver Advance"
		cust_type.account = ledger_account
		cust_type.insert()

		self.assertEqual(cust_type.custody_name, "Test Driver Advance")
		self.assertEqual(cust_type.account, ledger_account)

	def test_custody_type_requires_account(self):
		cust_type = frappe.new_doc("Haulage Custody Type")
		cust_type.custody_name = "Test Custody No Account"

		with self.assertRaises(frappe.ValidationError):
			cust_type.insert()

	def test_custody_type_group_account_rejected(self):
		# Find a group account
		group_account = frappe.db.get_value("Account", {"is_group": 1}, "name")
		if not group_account:
			self.skipTest("No group account found")

		cust_type = frappe.new_doc("Haulage Custody Type")
		cust_type.custody_name = "Test Invalid Custody"
		cust_type.account = group_account

		with self.assertRaises(frappe.ValidationError):
			cust_type.insert()
