import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime


class TestHaulageTripEvent(FrappeTestCase):
	def test_event_types(self):
		valid_events = ["Start", "Pause", "Resume", "Arrival", "Return"]
		trip = frappe.new_doc("Haulage Trip")

		for event_type in valid_events:
			trip.append("trip_events", {
				"event_type": event_type,
				"event_datetime": now_datetime(),
			})

		self.assertEqual(len(trip.trip_events), 5)

	def test_event_with_notes(self):
		trip = frappe.new_doc("Haulage Trip")
		trip.append("trip_events", {
			"event_type": "Start",
			"event_datetime": now_datetime(),
			"notes": "Trip started on time",
		})

		self.assertEqual(trip.trip_events[0].notes, "Trip started on time")
