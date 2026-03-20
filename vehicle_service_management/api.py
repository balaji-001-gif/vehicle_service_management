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
		filters={"vehicle_no": ["like", f"%{search_term}%"]},
		fields=[
			"name", "vehicle_name", "vehicle_brand", "vehicle_model",
			"vehicle_no", "category", "problem_description",
			"status", "date", "cost", "customer", "mechanic"
		],
		order_by="modified desc",
		limit=10
	)

	# If no results by vehicle number, try customer mobile
	if not results:
		# Find customers whose mobile matches
		mechanics_or_customers = frappe.db.sql("""
			SELECT vsr.name, vsr.vehicle_name, vsr.vehicle_brand, vsr.vehicle_model,
				vsr.vehicle_no, vsr.category, vsr.problem_description,
				vsr.status, vsr.date, vsr.cost, vsr.customer, vsr.mechanic
			FROM `tabVehicle Service Request` vsr
			LEFT JOIN `tabCustomer` c ON c.name = vsr.customer
			WHERE c.mobile_no LIKE %(search)s
			ORDER BY vsr.modified DESC
			LIMIT 10
		""", {"search": f"%{search_term}%"}, as_dict=True)

		if mechanics_or_customers:
			results = mechanics_or_customers

	# Add workflow station info to each result
	stations = ["Pending", "Approved", "Repairing", "Repairing Done", "Released"]
	for r in results:
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
		r["customer_name"] = frappe.db.get_value("Customer", r.get("customer"), "customer_name") or r.get("customer", "")
		r["mechanic_name"] = frappe.db.get_value("Vehicle Mechanic", r.get("mechanic"), "mechanic_name") or ""

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
			"name", "customer", "vehicle_name", "category",
			"vehicle_model", "vehicle_brand", "problem_description",
			"status", "date", "mechanic"
		],
		order_by="creation desc",
		limit=20
	)

	for r in recent_enquiries:
		r["customer_name"] = frappe.db.get_value("Customer", r.get("customer"), "customer_name") or r.get("customer", "")
		r["mechanic_name"] = frappe.db.get_value("Vehicle Mechanic", r.get("mechanic"), "mechanic_name") or ""

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
			"name", "customer", "vehicle_name", "vehicle_brand", "vehicle_model",
			"vehicle_no", "category", "problem_description",
			"status", "date", "cost"
		],
		order_by="modified desc",
		limit=50
	)

	stations = ["Pending", "Approved", "Repairing", "Repairing Done", "Released"]
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
	if doc.mechanic != mechanic and "System Manager" not in frappe.get_roles(user):
		frappe.throw("You are not authorized to update this request.")

	valid_statuses = ["Pending", "Approved", "Repairing", "Repairing Done", "Released"]
	if new_status not in valid_statuses:
		frappe.throw(f"Invalid status: {new_status}")

	doc.status = new_status
	doc.save(ignore_permissions=True)
	frappe.db.commit()

	return {"status": "success", "new_status": new_status}


@frappe.whitelist(allow_guest=True)
def book_service(customer_name, mobile, vehicle_name, vehicle_brand, vehicle_model,
				 vehicle_no, category, problem_description):
	"""
	Allow customers to book a service request from the online portal.
	Creates or finds a Customer record and creates a Vehicle Service Request.
	"""
	if not all([customer_name, mobile, vehicle_name, vehicle_brand, vehicle_model,
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

	# Create service request
	req = frappe.get_doc({
		"doctype": "Vehicle Service Request",
		"customer": customer,
		"vehicle_name": vehicle_name,
		"vehicle_brand": vehicle_brand,
		"vehicle_model": vehicle_model,
		"vehicle_no": vehicle_no,
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
