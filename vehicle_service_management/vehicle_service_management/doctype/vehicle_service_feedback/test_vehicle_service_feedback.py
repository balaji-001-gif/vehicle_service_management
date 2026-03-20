# Copyright (c) 2024, Balaji and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestVehicleServiceFeedback(FrappeTestCase):
	def test_feedback_creation(self):
		feedback = frappe.get_doc({
			"doctype": "Vehicle Service Feedback",
			"by_customer": "_Test Customer",
			"message": "Great service, very satisfied!",
		})
		feedback.insert(ignore_permissions=True)
		self.assertEqual(feedback.message, "Great service, very satisfied!")
		feedback.delete()
