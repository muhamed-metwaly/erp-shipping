import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today


class TestHaulageTripExpense(FrappeTestCase):
	def test_expense_on_trip(self):
		# Create expense type
		expense_account = frappe.db.get_value("Account", {"root_type": "Expense", "is_group": 0}, "name")
		if not expense_account:
			self.skipTest("No expense account found")

		exp_type = frappe.new_doc("Haulage Expense Type")
		exp_type.expense_name = "Test Expense Type For Trip"
		exp_type.account = expense_account
		exp_type.insert()

		# Create trip with expense
		trip = frappe.new_doc("Haulage Trip")
		trip.append("trip_expenses", {
			"expense_type": exp_type.name,
			"amount": 500,
			"expense_date": today(),
		})

		# Should fail without truck/driver but expense row should be valid
		self.assertEqual(len(trip.trip_expenses), 1)
		self.assertEqual(trip.trip_expenses[0].amount, 500)
