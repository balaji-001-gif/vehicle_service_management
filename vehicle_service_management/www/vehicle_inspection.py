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
	req_doc = frappe.get_doc("Vehicle Service Request", req_name)
	context.request = req_doc
	context.vehicle_name = "-"
	
	if req_doc.vehicle:
		v_doc = frappe.db.get_value("Vehicle Master", req_doc.vehicle, ["make", "model"], as_dict=True)
		if v_doc:
			context.vehicle_name = f"{v_doc.make or ''} {v_doc.model or ''}"
			
	# Check for existing inspection
	inspection_name = frappe.db.get_value("Vehicle Inspection", {"service_request": req_name}, "name")
	context.inspection = None
	if inspection_name:
		context.inspection = frappe.get_doc("Vehicle Inspection", inspection_name)
		
	# Standard Checklist for new inspections
	context.standard_items = [
		"Engine Oil Level & Quality",
		"Brake Fluid Level",
		"Coolant Level",
		"Tire Pressure & Tread Depth",
		"Battery Voltage & Terminals",
		"Brake Pad Thickness",
		"Wiper Blades & Fluid",
		"Exterior Lights (Headlamps, Indicators)",
		"Body Scratches & Dents Check",
		"Undercarriage Inspection"
	]
