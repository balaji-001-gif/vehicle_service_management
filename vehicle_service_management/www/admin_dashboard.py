# Copyright (c) 2024, Balaji and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, getdate, nowdate, date_diff

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
		context.requests = frappe.get_all("Vehicle Service Request", fields=["name", "customer", "vehicle", "category", "status", "date", "mechanic", "cost", "payment_status", "is_insurance_job", "insurance_claim"], order_by="modified desc", limit=100)
		for r in context.requests:
			r.customer_name = frappe.db.get_value("Customer", r.customer, "customer_name") or r.customer
			r.mechanic_name = frappe.db.get_value("Vehicle Mechanic", r.mechanic, "mechanic_name") or ""
			r.service_bays = frappe.db.get_all("Vehicle Service Bay", filters={"parent": r.name}, fields=["name", "bay_name", "bay_status"], order_by="idx asc")
			
			r.vehicle_brand = ""
			r.vehicle_model = ""
			r.vehicle_no = r.vehicle or ""
			r.vehicle_name = "-"
			if r.vehicle:
				vehicle_doc = frappe.db.get_value("Vehicle Master", r.vehicle, ["make", "model", "vehicle_number"], as_dict=True)
				if vehicle_doc:
					r.vehicle_brand = vehicle_doc.make or ""
					r.vehicle_model = vehicle_doc.model or ""
					r.vehicle_no = vehicle_doc.vehicle_number or ""
					r.vehicle_name = f"{vehicle_doc.make or ''} {vehicle_doc.model or ''}".strip() or "-"
			
			if r.is_insurance_job and r.insurance_claim:
				r.insurance_claim_status = frappe.db.get_value("Insurance Claim", r.insurance_claim, "claim_status")
			else:
				r.insurance_claim_status = None
				
			# Check for Paint Job Card
			pjc = frappe.db.get_value("Paint Job Card", {"service_request": r.name}, ["name", "status"], as_dict=True)
			r.paint_job_card = pjc.name if pjc else None
			r.paint_job_status = pjc.status if pjc else None
			
			# Check for Digital Inspection
			inspection = frappe.db.get_value("Vehicle Inspection", {"service_request": r.name}, ["name", "overall_condition"], as_dict=True)
			r.inspection_report = inspection.name if inspection else None
			r.inspection_condition = inspection.overall_condition if inspection else None
	elif view == "feedback":
		context.feedback = frappe.get_all("Vehicle Service Feedback", fields=["name", "customer", "service_request", "rating", "comments", "creation"], order_by="creation desc", limit=100)
		for f in context.feedback:
			f.customer_name = frappe.db.get_value("Customer", f.customer, "customer_name") or f.customer
	elif view == "equipment":
		context.equipment = frappe.get_all("Workshop Equipment", fields=["name", "equipment_name", "type", "status", "last_maintenance_date", "next_maintenance_date"], order_by="equipment_name asc")
	elif view == "insurance":
		# 1. Insurance Claims Pipeline (by status)
		claims = frappe.get_all("Insurance Claim", fields=["name", "claim_status", "claim_type", "insurer", "net_payable_by_insurer", "creation", "claim_intimation_date", "settlement_date", "rejection_reason", "customer", "vehicle"], order_by="creation desc")
		
		for c in claims:
			c.customer_name = frappe.db.get_value("Customer", c.customer, "customer_name") or c.customer
			c.vehicle_name = frappe.db.get_value("Vehicle Master", c.vehicle, ["make", "model"], as_dict=True)
			if c.vehicle_name:
				c.vehicle_display = f"{c.vehicle_name.make} {c.vehicle_name.model}"
			else:
				c.vehicle_display = c.vehicle

		pipeline = {}
		for c in claims:
			status = c.claim_status or "Draft"
			pipeline[status] = pipeline.get(status, 0) + 1
		context.claims_pipeline = pipeline
		
		# 2. Average claim settlement time
		settled_claims = [c for c in claims if c.claim_status == "Settled" and c.settlement_date and (c.claim_intimation_date or c.creation)]
		total_days = 0
		for c in settled_claims:
			intimation = c.claim_intimation_date or c.creation
			total_days += date_diff(c.settlement_date, intimation)
		
		context.avg_settlement_time = round(total_days / len(settled_claims), 1) if settled_claims else 0
		
		# 3. Insurer-wise ageing + rejection reasons
		insurer_stats = {}
		rejections = []
		for c in claims:
			ins = c.insurer or "Unknown"
			if ins not in insurer_stats:
				insurer_stats[ins] = {"count": 0, "total_value": 0, "avg_age": 0}
			
			insurer_stats[ins]["count"] += 1
			insurer_stats[ins]["total_value"] += flt(c.net_payable_by_insurer)
			
			if c.claim_status != "Settled":
				age = date_diff(nowdate(), (c.claim_intimation_date or c.creation))
				insurer_stats[ins]["avg_age"] = (insurer_stats[ins]["avg_age"] * (insurer_stats[ins]["count"]-1) + age) / insurer_stats[ins]["count"]

			if c.claim_status == "Rejected" and c.rejection_reason:
				rejections.append({"insurer": ins, "reason": c.rejection_reason, "claim": c.name})
		
		context.insurer_stats = insurer_stats
		context.rejection_reports = rejections[:10]
		
		# 4. Cashless vs Reimbursement revenue split
		revenue_split = {"Cashless": 0, "Reimbursement": 0}
		for c in claims:
			ctype = c.claim_type or "Cashless"
			revenue_split[ctype] += flt(c.net_payable_by_insurer)
		context.revenue_split = revenue_split
		
		# 5. Outstanding reimbursements pending from insurers
		context.pending_claims = [c for c in claims if c.claim_status not in ["Settled", "Rejected"]]
		context.total_outstanding_amount = sum(flt(c.net_payable_by_insurer) for c in context.pending_claims)
		context.insurance_claims = claims
