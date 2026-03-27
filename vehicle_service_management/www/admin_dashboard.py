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
		context.total_trips = stats.get("total_trips", 0)
		context.recent_enquiries = stats.get("recent_enquiries", [])

		# 1. Bay Utilization
		bays = frappe.get_all("Vehicle Service Bay", fields=["bay_status"])
		if bays:
			busy = len([b for b in bays if b.bay_status == "In Progress"])
			context.bay_utilization = flt((busy / len(bays)) * 100, 1)
		else:
			context.bay_utilization = 0.0

		# 2. Revenue & Profit Trends
		active_reqs = frappe.get_all("Vehicle Service Request", 
			fields=["name", "cost", "status", "mechanic"], 
			filters={"status": ["!=", "Cancelled"]})
		
		total_rev = sum(flt(r.cost) for r in active_reqs)
		total_cost_spares = 0.0
		for r in active_reqs:
			spares = frappe.get_all("Consumed Spare", filters={"parent": r.name}, fields=["amount"])
			total_cost_spares += sum(flt(s.amount) for s in spares)
		
		context.total_revenue = total_rev
		context.total_profit = total_rev - total_cost_spares
		context.profit_margin = flt((context.total_profit / total_rev * 100) if total_rev > 0 else 0, 1)

		# 3. Technician Performance
		tech_stats = {}
		for r in active_reqs:
			if r.mechanic:
				if r.mechanic not in tech_stats:
					tech_stats[r.mechanic] = {"name": "", "jobs": 0, "revenue": 0.0}
				tech_stats[r.mechanic]["jobs"] += 1
				tech_stats[r.mechanic]["revenue"] += flt(r.cost)
		
		performance_list = []
		for tech_id, tdata in tech_stats.items():
			tdata["name"] = frappe.db.get_value("Vehicle Mechanic", tech_id, "mechanic_name") or tech_id
			performance_list.append(tdata)
		
		context.technician_performance = sorted(performance_list, key=lambda x: x["revenue"], reverse=True)[:5]

		# 4. Low Stock Alerts
		context.low_stock = frappe.get_all("Item", 
			filters={"is_stock_item": 1}, 
			fields=["item_code", "item_name"], 
			limit=5)
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
		fields = ["name", "claim_status", "claim_type", "insurer", "net_payable_by_insurer", "creation", "customer", "vehicle"]
		
		# Safer check for newly added columns
		if frappe.db.has_column("Insurance Claim", "claim_intimation_date"):
			fields.append("claim_intimation_date")
		if frappe.db.has_column("Insurance Claim", "settlement_date"):
			fields.append("settlement_date")
		if frappe.db.has_column("Insurance Claim", "rejection_reason"):
			fields.append("rejection_reason")

		claims = frappe.get_all("Insurance Claim", fields=fields, order_by="creation desc")
		
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
		settled_claims = [c for c in claims if c.claim_status == "Settled" and c.get("settlement_date") and (c.get("claim_intimation_date") or c.creation)]
		total_days = 0
		for c in settled_claims:
			intimation = c.get("claim_intimation_date") or c.creation
			total_days += date_diff(c.settlement_date, intimation)
		
		context.avg_settlement_time = round(total_days / len(settled_claims), 1) if settled_claims else 0
		
		# 3. Insurer-wise ageing + rejection reasons
		insurer_stats = {}
		rejections = []
		for c in claims:
			ins = c.insurer or "Unknown"
			if ins not in insurer_stats:
				insurer_stats[ins] = {"count": 0, "total_value": 0.0, "avg_age": 0.0}
			
			insurer_stats[ins]["count"] += 1
			insurer_stats[ins]["total_value"] += flt(c.net_payable_by_insurer)
			
			if c.claim_status != "Settled":
				age = date_diff(nowdate(), (c.get("claim_intimation_date") or c.creation))
				count = insurer_stats[ins]["count"]
				insurer_stats[ins]["avg_age"] = (insurer_stats[ins]["avg_age"] * (count-1) + age) / count

			if c.claim_status == "Rejected" and c.get("rejection_reason"):
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
	elif view == "trips":
		context.trips = frappe.get_all("Vehicle Service Trip", fields=["name", "service_request", "customer", "vehicle", "trip_type", "status", "scheduled_time", "driver", "live_location"], order_by="scheduled_time desc", limit=100)
		for t in context.trips:
			t.customer_name = frappe.db.get_value("Customer", t.customer, "customer_name") or t.customer
			t.driver_name = frappe.db.get_value("Vehicle Mechanic", t.driver, "mechanic_name") or ""
			# Get vehicle info
			v = frappe.db.get_value("Vehicle Master", t.vehicle, ["make", "model"], as_dict=True)
			t.vehicle_display = f"{v.make} {v.model}" if v else t.vehicle
