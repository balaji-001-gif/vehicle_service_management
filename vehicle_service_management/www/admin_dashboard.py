# Copyright (c) 2024, Balaji and contributors
# For license information, please see license.txt

import frappe

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.throw("Please login to access the Admin Dashboard.", frappe.PermissionError)

	if "System Manager" not in frappe.get_roles(frappe.session.user):
		frappe.throw("You do not have permission to access this page.", frappe.PermissionError)

	context.no_cache = 1
	context.title = "Admin Dashboard"

	from vehicle_service_management.api import get_admin_stats
	stats = get_admin_stats()

	context.total_customers = stats.get("total_customers", 0)
	context.total_mechanics = stats.get("total_mechanics", 0)
	context.total_enquiries = stats.get("total_enquiries", 0)
	context.total_feedback = stats.get("total_feedback", 0)
	context.recent_enquiries = stats.get("recent_enquiries", [])
