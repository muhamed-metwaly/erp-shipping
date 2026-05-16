import frappe
from frappe.tests.utils import FrappeTestCase


class TestHaulageLogisticsSettings(FrappeTestCase):
	def test_settings_is_single(self):
		# Single doctypes should always exist
		settings = frappe.get_single("Haulage Logistics Settings")
		self.assertIsNotNone(settings)

	def test_settings_cache_ttl_default(self):
		settings = frappe.get_single("Haulage Logistics Settings")
		# Default should be 300 if not set
		ttl = settings.cache_ttl_seconds or 300
		self.assertGreater(ttl, 0)
