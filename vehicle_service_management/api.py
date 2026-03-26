# Copyright (c) 2024, Balaji and contributors
# For license information, please see license.txt

import frappe


@frappe.whitelist(allow_guest=True)
def get_service_status(search_term=None):
	"""
	Fetch vehicle service requests by vehicle number or customer mobile.
	Returns a list of matching requests with status info.
	"""
	if not search_term:
		return []

	search_term = search_term.strip()

	# Search by vehicle number
	results = frappe.db.get_all(
		"Vehicle Service Request",
		filters={"vehicle": ["like", f"%{search_term}%"]},
		fields=[
			"name", "vehicle", "category", "problem_description",
			"status", "date", "cost", "customer", "mechanic", "payment_status", "quotation_approved"
		],
		order_by="modified desc",
		limit=10
	)

	if not results:
		# Find customers whose mobile matches
		mechanics_or_customers = frappe.db.sql("""
			SELECT vsr.name, vsr.vehicle,
				vsr.category, vsr.problem_description,
				vsr.status, vsr.date, vsr.cost, vsr.customer, vsr.mechanic, vsr.payment_status, vsr.quotation_approved
			FROM `tabVehicle Service Request` vsr
			LEFT JOIN `tabCustomer` c ON c.name = vsr.customer
			WHERE c.mobile_no LIKE %(search)s
			ORDER BY vsr.modified DESC
			LIMIT 10
		""", {"search": f"%{search_term}%"}, as_dict=True)

		if mechanics_or_customers:
			results = mechanics_or_customers

	# Add workflow station info to each result
	stations = ["Pending", "Quoted", "Approved", "Repairing", "Repairing Done", "Released"]
	for r in results:
		r["has_feedback"] = frappe.db.exists("Vehicle Service Feedback", {"service_request": r.name})
		current_index = stations.index(r.get("status", "Pending")) if r.get("status") in stations else 0
		r["stations"] = []
		for i, station in enumerate(stations):
			r["stations"].append({
				"name": station,
				"completed": i < current_index,
				"current": i == current_index,
				"pending": i > current_index,
				"index": i
			})
		r["service_bays"] = frappe.db.get_all("Vehicle Service Bay", filters={"parent": r.name}, fields=["name", "bay_name", "bay_status"], order_by="idx asc")
		r["customer_name"] = frappe.db.get_value("Customer", r.get("customer"), "customer_name") or r.get("customer", "")
		r["mechanic_name"] = frappe.db.get_value("Vehicle Mechanic", r.get("mechanic"), "mechanic_name") or ""
		
		# Inject Vehicle Master details for template compatibility
		r["vehicle_brand"] = ""
		r["vehicle_model"] = ""
		r["vehicle_no"] = r.get("vehicle") or ""
		r["vehicle_name"] = "-"
		if r.get("vehicle"):
			vehicle_doc = frappe.db.get_value("Vehicle Master", r.get("vehicle"), ["make", "model", "vehicle_number", "fuel_type"], as_dict=True)
			if vehicle_doc:
				r["vehicle_brand"] = vehicle_doc.make or ""
				r["vehicle_model"] = vehicle_doc.model or ""
				r["vehicle_no"] = vehicle_doc.vehicle_number or ""
				r["vehicle_name"] = f"{vehicle_doc.make or ''} {vehicle_doc.model or ''}".strip() or "-"

	return results


@frappe.whitelist()
def get_admin_stats():
	"""
	Get dashboard statistics for admin panel.
	Returns total counts and recent enquiries.
	"""
	total_customers = frappe.db.count("Customer")
	total_mechanics = frappe.db.count("Vehicle Mechanic")
	total_enquiries = frappe.db.count("Vehicle Service Request")
	total_feedback = frappe.db.count("Vehicle Service Feedback")

	recent_enquiries = frappe.db.get_all(
		"Vehicle Service Request",
		fields=[
			"name", "customer", "vehicle", "category", "problem_description",
			"status", "date", "mechanic", "payment_status", "quotation_approved"
		],
		order_by="creation desc",
		limit=20
	)

	for r in recent_enquiries:
		r["customer_name"] = frappe.db.get_value("Customer", r.get("customer"), "customer_name") or r.get("customer", "")
		r["mechanic_name"] = frappe.db.get_value("Vehicle Mechanic", r.get("mechanic"), "mechanic_name") or ""
		
		# Inject Vehicle Master details for template compatibility
		r["vehicle_brand"] = ""
		r["vehicle_model"] = ""
		r["vehicle_no"] = r.get("vehicle") or ""
		r["vehicle_name"] = "-"
		if r.get("vehicle"):
			vehicle_doc = frappe.db.get_value("Vehicle Master", r.get("vehicle"), ["make", "model", "vehicle_number", "fuel_type"], as_dict=True)
			if vehicle_doc:
				r["vehicle_brand"] = vehicle_doc.make or ""
				r["vehicle_model"] = vehicle_doc.model or ""
				r["vehicle_no"] = vehicle_doc.vehicle_number or ""
				r["vehicle_name"] = f"{vehicle_doc.make or ''} {vehicle_doc.model or ''}".strip() or "-"

	return {
		"total_customers": total_customers,
		"total_mechanics": total_mechanics,
		"total_enquiries": total_enquiries,
		"total_feedback": total_feedback,
		"recent_enquiries": recent_enquiries
	}


@frappe.whitelist()
def get_mechanic_requests():
	"""
	Get service requests assigned to the logged-in mechanic.
	"""
	user = frappe.session.user
	mechanic = frappe.db.get_value("Vehicle Mechanic", {"user": user}, "name")

	if not mechanic:
		return {"requests": [], "mechanic_name": ""}

	mechanic_name = frappe.db.get_value("Vehicle Mechanic", mechanic, "mechanic_name") or ""

	requests = frappe.db.get_all(
		"Vehicle Service Request",
		filters={"mechanic": mechanic},
		fields=[
			"name", "customer", "vehicle", "category", "problem_description",
			"status", "date", "cost", "payment_status", "quotation_approved"
		],
		order_by="modified desc",
		limit=50
	)

	stations = ["Pending", "Quoted", "Approved", "Repairing", "Repairing Done", "Released"]
	for r in requests:
		r["customer_name"] = frappe.db.get_value("Customer", r.get("customer"), "customer_name") or r.get("customer", "")
		current_index = stations.index(r.get("status", "Pending")) if r.get("status") in stations else 0
		r["stations"] = []
		for i, station in enumerate(stations):
			r["stations"].append({
				"name": station,
				"completed": i < current_index,
				"current": i == current_index,
				"pending": i > current_index,
			})
		r["service_bays"] = frappe.db.get_all("Vehicle Service Bay", filters={"parent": r.name}, fields=["name", "bay_name", "bay_status"], order_by="idx asc")
		
		# Inject Vehicle Master details for template compatibility
		r["vehicle_brand"] = ""
		r["vehicle_model"] = ""
		r["vehicle_no"] = r.get("vehicle") or ""
		r["vehicle_name"] = "-"
		if r.get("vehicle"):
			vehicle_doc = frappe.db.get_value("Vehicle Master", r.get("vehicle"), ["make", "model", "vehicle_number", "fuel_type"], as_dict=True)
			if vehicle_doc:
				r["vehicle_brand"] = vehicle_doc.make or ""
				r["vehicle_model"] = vehicle_doc.model or ""
				r["vehicle_no"] = vehicle_doc.vehicle_number or ""
				r["vehicle_name"] = f"{vehicle_doc.make or ''} {vehicle_doc.model or ''}".strip() or "-"

	return {"requests": requests, "mechanic_name": mechanic_name}


@frappe.whitelist()
def update_request_status(request_name, new_status):
	"""
	Allow mechanics to update the status of their assigned requests.
	"""
	user = frappe.session.user
	mechanic = frappe.db.get_value("Vehicle Mechanic", {"user": user}, "name")

	doc = frappe.get_doc("Vehicle Service Request", request_name)

	# Only the assigned mechanic or System Manager can update
	is_admin = "System Manager" in frappe.get_roles(user)
	if doc.mechanic != mechanic and not is_admin:
		frappe.throw("You are not authorized to update this request.")

	valid_statuses = ["Pending", "Quoted", "Approved", "Repairing", "Repairing Done", "Released"]
	if new_status not in valid_statuses:
		frappe.throw(f"Invalid status: {new_status}")

	if not is_admin:
		# Mechanics can only set 'Repairing' and 'Repairing Done'
		if new_status not in ["Repairing", "Repairing Done"]:
			frappe.throw("Mechanics can only update status to 'Repairing' or 'Repairing Done'.")

	if new_status == "Released" and doc.status != "Released":
		# Generate standard ERPNext Sales Invoice
		if doc.cost and doc.cost > 0:
			create_sales_invoice(doc)

	doc.status = new_status
	doc.save(ignore_permissions=True)
	frappe.db.commit()

	return {"status": "success", "new_status": new_status}


@frappe.whitelist(allow_guest=True)
def process_payment(request_name):
	"""
	Process a native payment (mark as Paid).
	"""
	doc = frappe.get_doc("Vehicle Service Request", request_name)
	if doc.payment_status == "Paid":
		frappe.throw("This service request is already paid.")
	
	doc.payment_status = "Paid"
	doc.save(ignore_permissions=True)
	
	# If invoice exists, generate a Payment Entry
	si_name = frappe.db.get_value("Sales Invoice", {"po_no": doc.name, "docstatus": 1}, "name")
	if si_name:
		create_payment_entry(si_name)

	frappe.db.commit()

	return {"status": "success"}

def create_sales_invoice(doc):
	"""Helper to generate a native ERPNext Sales Invoice linked to our Custom Service Request"""
	existing_si = frappe.db.get_value("Sales Invoice", {"po_no": doc.name, "docstatus": 1}, "name")
	if existing_si:
		return existing_si
		
	# Ensure basic service item exists
	if not frappe.db.exists("Item", "Vehicle Service"):
		item = frappe.get_doc({
			"doctype": "Item",
			"item_code": "Vehicle Service",
			"item_name": "Vehicle Service",
			"item_group": "Services",
			"is_stock_item": 0,
			"stock_uom": "Nos"
		})
		item.insert(ignore_permissions=True)
		
	# Handle Insurance Split Billing
	customer_liability = doc.cost
	if doc.is_insurance_job and doc.insurance_claim:
		claim = frappe.get_doc("Insurance Claim", doc.insurance_claim)
		if claim.claim_type == "Cashless" and claim.deductible_amount is not None:
			customer_liability = claim.deductible_amount

	if customer_liability <= 0:
		return None  # Nothing for customer to pay directly

	si = frappe.get_doc({
		"doctype": "Sales Invoice",
		"customer": doc.customer,
		"po_no": doc.name, 
		"items": [{
			"item_code": "Vehicle Service",
			"qty": 1,
			"rate": customer_liability,
			"description": f"Service for {doc.vehicle} - {doc.problem_description}"
		}]
	})
	si.flags.ignore_permissions = True
	si.insert()
	si.submit()
	return si.name

def create_payment_entry(si_name):
	"""Helper to record native ERPNext Payment Entry against Invoice"""
	try:
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
		pe = get_payment_entry("Sales Invoice", si_name, bank_account=None)
		pe.reference_no = si_name
		pe.reference_date = frappe.utils.today()
		pe.flags.ignore_permissions = True
		pe.insert()
		pe.submit()
	except ImportError:
		# If user doesn't have ERPNext installed, bypass
		pass


@frappe.whitelist(allow_guest=True)
def book_service(customer_name, mobile, vehicle_name, vehicle_brand, vehicle_model,
				 vehicle_no, category, problem_description, fuel_type="Petrol", insurance_expiry=None, puc_expiry=None):
	"""
	Allow customers to book a service request from the online portal.
	Creates or finds a Customer record, creates a Vehicle Master, and issues the Request.
	"""
	if not all([customer_name, mobile, vehicle_brand, vehicle_model,
				vehicle_no, problem_description]):
		frappe.throw("All fields are required.")

	# Find or create customer
	existing = frappe.db.get_value("Customer", {"mobile_no": mobile}, "name")
	if existing:
		customer = existing
	else:
		cust_doc = frappe.get_doc({
			"doctype": "Customer",
			"customer_name": customer_name,
			"customer_type": "Individual",
			"mobile_no": mobile
		})
		cust_doc.insert(ignore_permissions=True)
		customer = cust_doc.name

	# Find or create Vehicle Master
	existing_vehicle = frappe.db.get_value("Vehicle Master", {"vehicle_number": vehicle_no}, "name")
	if existing_vehicle:
		vehicle_id = existing_vehicle
	else:
		veh_doc = frappe.get_doc({
			"doctype": "Vehicle Master",
			"vehicle_number": vehicle_no,
			"make": vehicle_brand,
			"model": vehicle_model,
			"fuel_type": fuel_type,
			"customer": customer,
			"insurance_expiry": insurance_expiry,
			"puc_expiry": puc_expiry
		})
		veh_doc.insert(ignore_permissions=True)
		vehicle_id = veh_doc.name

	# Create service request
	req = frappe.get_doc({
		"doctype": "Vehicle Service Request",
		"customer": customer,
		"vehicle": vehicle_id,
		"category": category,
		"problem_description": problem_description,
		"status": "Pending"
	})
	req.insert(ignore_permissions=True)
	frappe.db.commit()

	return {
		"status": "success",
		"request_id": req.name,
		"message": f"Service request {req.name} created successfully!"
	}


@frappe.whitelist(allow_guest=True)
def approve_quotation(request_name):
	"""
	Allow customers to explicitly approve the quotation cost.
	"""
	doc = frappe.get_doc("Vehicle Service Request", request_name)
	if doc.quotation_approved:
		return {"status": "success"}
	
	doc.quotation_approved = 1
	doc.status = "Approved"
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	
	return {"status": "success"}


@frappe.whitelist(allow_guest=True)
def submit_feedback(request_name, rating, comments):
	"""
	Allow customers to submit auto-feedback after payment.
	"""
	doc = frappe.get_doc("Vehicle Service Request", request_name)
	if not rating:
		frappe.throw("Rating is required.")

	if frappe.db.exists("Vehicle Service Feedback", {"service_request": request_name}):
		frappe.throw("Feedback already submitted for this request.")

	fb = frappe.get_doc({
		"doctype": "Vehicle Service Feedback",
		"service_request": request_name,
		"customer": doc.customer,
		"rating": rating,
		"comments": comments
	})
	fb.insert(ignore_permissions=True)
	frappe.db.commit()
	
	return {"status": "success"}


@frappe.whitelist()
def update_bay_status(request_name, bay_id, bay_status):
	"""
	Allows mechanics to update a specific bay status within a vehicle service request.
	"""
	user = frappe.session.user
	mechanic = frappe.db.get_value("Vehicle Mechanic", {"user": user}, "name")
	doc = frappe.get_doc("Vehicle Service Request", request_name)
	
	is_admin = "System Manager" in frappe.get_roles(user)
	if doc.mechanic != mechanic and not is_admin:
		frappe.throw("You are not authorized to update this request.")

	updated = False
	for bay in doc.service_bays:
		if bay.name == bay_id:
			bay.bay_status = bay_status
			updated = True
			break
			
	if not updated:
		frappe.throw(f"Bay {bay_id} not found in this request.")
		
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"status": "success"}


@frappe.whitelist()
def add_service_bay(request_name, bay_name):
	"""
	Allows mechanics to dynamically add an operation to a vehicle service request.
	"""
	user = frappe.session.user
	mechanic = frappe.db.get_value("Vehicle Mechanic", {"user": user}, "name")
	doc = frappe.get_doc("Vehicle Service Request", request_name)
	
	is_admin = "System Manager" in frappe.get_roles(user)
	if doc.mechanic != mechanic and not is_admin:
		frappe.throw("You are not authorized to modify this request.")

	doc.append("service_bays", {
		"bay_name": bay_name,
		"bay_status": "Pending"
	})
	
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"status": "success"}
