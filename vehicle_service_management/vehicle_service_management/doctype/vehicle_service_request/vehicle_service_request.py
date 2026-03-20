# Copyright (c) 2024, Balaji and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VehicleServiceRequest(Document):
	def validate(self):
		if self.cost and self.cost < 0:
			frappe.throw("Cost cannot be negative")
