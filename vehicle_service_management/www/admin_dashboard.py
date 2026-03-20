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
	context.title = "Admin Portal"

	view = frappe.form_dict.get("view", "dashboard")
	context.view = view

	if view == "dashboard":
		from vehicle_service_management.api import get_admin_stats
		stats = get_admin_stats()
		context.total_customers = stats.get("total_customers", 0)
		context.total_mechanics = stats.get("total_mechanics", 0)
		context.total_enquiries = stats.get("total_enquiries", 0)
		context.total_feedback = stats.get("total_feedback", 0)
		context.recent_enquiries = stats.get("recent_enquiries", [])
	elif view == "customers":
		context.customers = frappe.get_all("Customer", fields=["name", "customer_name", "mobile_no", "customer_type", "email_id"], order_by="modified desc", limit=100)
	elif view == "mechanics":
		context.mechanics = frappe.get_all("Vehicle Mechanic", fields=["name", "mechanic_name", "status"], order_by="modified desc")
	elif view == "requests":
		context.requests = frappe.get_all("Vehicle Service Request", fields=["name", "customer", "vehicle_name", "category", "status", "date", "mechanic", "cost", "payment_status"], order_by="modified desc", limit=100)
		for r in context.requests:
			r.customer_name = frappe.db.get_value("Customer", r.customer, "customer_name") or r.customer
			r.mechanic_name = frappe.db.get_value("Vehicle Mechanic", r.mechanic, "mechanic_name") or ""
	elif view == "feedback":
		context.feedback = frappe.get_all("Vehicle Service Feedback", fields=["name", "customer", "service_request", "rating", "comments", "creation"], order_by="creation desc", limit=100)
		for f in context.feedback:
			f.customer_name = frappe.db.get_value("Customer", f.customer, "customer_name") or f.customer
