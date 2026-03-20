# Copyright (c) 2024, Balaji and contributors
# For license information, please see license.txt

import frappe

no_cache = 1


def get_context(context):
	context.no_cache = 1
	context.title = "Track Your Vehicle Service"

	# Check if a search_term was passed via query string
	search_term = frappe.form_dict.get("q", "")
	context.search_term = search_term
	context.results = []

	if search_term:
		from vehicle_service_management.api import get_service_status
		context.results = get_service_status(search_term)
