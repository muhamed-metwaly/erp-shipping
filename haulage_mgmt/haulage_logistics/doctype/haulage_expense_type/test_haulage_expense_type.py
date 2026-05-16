import frappe
from frappe.tests.utils import FrappeTestCase


class TestHaulageExpenseType(FrappeTestCase):
	def test_expense_type_valid_creation(self):
		# Find an expense account
		expense_account = frappe.db.get_value("Account", {"root_type": "Expense", "is_group": 0}, "name")
		if not expense_account:
			self.skipTest("No expense account found")

		exp_type = frappe.new_doc("Haulage Expense Type")
		exp_type.expense_name = "Test Fuel Expense"
		exp_type.account = expense_account
		exp_type.insert()

		self.assertEqual(exp_type.expense_name, "Test Fuel Expense")
		self.assertEqual(exp_type.account, expense_account)

	def test_expense_type_requires_account(self):
		exp_type = frappe.new_doc("Haulage Expense Type")
		exp_type.expense_name = "Test Expense No Account"

		with self.assertRaises(frappe.ValidationError):
			exp_type.insert()

	def test_expense_type_non_expense_account_rejected(self):
		# Find a non-expense account (e.g., Asset or Income)
		non_expense_account = frappe.db.get_value("Account", {"root_type": ("!=", "Expense"), "is_group": 0}, "name")
		if not non_expense_account:
			self.skipTest("No non-expense account found")

		exp_type = frappe.new_doc("Haulage Expense Type")
		exp_type.expense_name = "Test Invalid Expense"
		exp_type.account = non_expense_account

		with self.assertRaises(frappe.ValidationError):
			exp_type.insert()
