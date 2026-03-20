# Copyright (c) 2024, Balaji and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestVehicleMechanic(FrappeTestCase):
	def test_mechanic_creation(self):
		mechanic = frappe.get_doc({
			"doctype": "Vehicle Mechanic",
			"user": "Administrator",
			"mobile": "9876543210",
			"address": "Test Address",
			"skill": "Engine Repair",
			"salary": 25000,
			"status": 1
		})
		mechanic.insert(ignore_permissions=True)
		self.assertEqual(mechanic.mobile, "9876543210")
		self.assertEqual(mechanic.skill, "Engine Repair")
		mechanic.delete()
