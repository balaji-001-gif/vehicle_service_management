# Copyright (c) 2024, Balaji and contributors
# For license information, please see license.txt

import frappe

no_cache = 1

def get_context(context):
	context.no_cache = 1
	
	req_name = frappe.form_dict.get('request')
	if not req_name:
		frappe.local.flags.redirect_location = "/mechanic-dashboard"
		raise frappe.Redirect
		
	# Verify request exists
	if not frappe.db.exists("Vehicle Service Request", req_name):
		context.error = "Service Request not found."
		return
		
	context.request_name = req_name
	
	# Get Request baseline
	vsr = frappe.get_doc("Vehicle Service Request", req_name)
	context.vehicle_name = getattr(vsr, "vehicle", "")
	
	if vsr.vehicle:
		v_doc = frappe.db.get_value("Vehicle Master", vsr.vehicle, ["make", "model"], as_dict=True)
		if v_doc:
			context.vehicle_name = f"{v_doc.make or ''} {v_doc.model or ''}"
	
	# Look for existing Paint Job Card
	existing_card = frappe.db.get_value("Paint Job Card", {"service_request": req_name}, "name")
	
	context.card = None
	if existing_card:
		context.card = frappe.get_doc("Paint Job Card", existing_card)
		
	# Get available Booths for assignment
	context.booths = frappe.get_all("Workshop Equipment", filters={"type": "Paint Booth"}, fields=["name", "equipment_name", "status"])
	context.insurance_claim = vsr.insurance_claim if vsr.is_insurance_job else ""
