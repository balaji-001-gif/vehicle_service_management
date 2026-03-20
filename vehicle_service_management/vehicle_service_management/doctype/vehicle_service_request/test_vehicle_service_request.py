# Copyright (c) 2024, Balaji and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestVehicleServiceRequest(FrappeTestCase):
	def test_request_creation(self):
		request = frappe.get_doc({
			"doctype": "Vehicle Service Request",
			"customer": "_Test Customer",
			"vehicle_name": "Honda Activa",
			"vehicle_brand": "Honda",
			"vehicle_model": "Activa 6G",
			"vehicle_no": "TN-01-AB-1234",
			"category": "two wheeler without gear",
			"problem_description": "Engine overheating",
			"status": "Pending"
		})
		request.insert(ignore_permissions=True)
		self.assertEqual(request.status, "Pending")
		self.assertEqual(request.vehicle_name, "Honda Activa")
		request.delete()
