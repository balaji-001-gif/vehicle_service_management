# Copyright (c) 2024, Balaji and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VehicleMechanic(Document):
	def before_save(self):
		if self.user:
			self.mechanic_name = frappe.db.get_value("User", self.user, "full_name")
