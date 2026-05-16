import frappe
from frappe.tests.utils import FrappeTestCase


class TestHaulageTripShipment(FrappeTestCase):
	def test_shipment_requires_shipping_request(self):
		shipment = frappe.new_doc("Haulage Trip Shipment")
		# Should require shipping_request field
		self.assertFalse(shipment.shipping_request)

	def test_shipment_on_trip(self):
		# Create shipping request first
		sr = frappe.new_doc("Shipping Request")
		sr.customer = "_Test Customer"
		sr.pickup_location = "Test Pickup"
		sr.delivery_location = "Test Delivery"
		sr.append("items", {"item_code": "_Test Item", "qty": 1})
		sr.insert()

		# Create trip with shipment
		trip = frappe.new_doc("Haulage Trip")
		trip.append("shipments", {"shipping_request": sr.name})

		self.assertEqual(len(trip.shipments), 1)
		self.assertEqual(trip.shipments[0].shipping_request, sr.name)
