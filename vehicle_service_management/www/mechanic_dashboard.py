# Copyright (c) 2024, Balaji and contributors
# For license information, please see license.txt

import frappe

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.throw("Please login to access the Mechanic Dashboard.", frappe.PermissionError)

	context.no_cache = 1
	context.title = "Mechanic Dashboard"

	from vehicle_service_management.api import get_mechanic_requests
	data = get_mechanic_requests()

	context.mechanic_name = data.get("mechanic_name", "")
	context.requests = data.get("requests", [])
	
	context.stock_items = frappe.get_all("Item", filters={"is_stock_item": 1}, fields=["name", "item_code", "item_name", "standard_rate"], order_by="item_name asc")
