# Copyright (c) 2024, Balaji and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

no_cache = 1

def get_context(context):
    context.no_cache = 1
    user = frappe.session.user
    
    # Defaults
    context.customer_name = frappe.session.user_fullname or "Guest"
    context.active_request = None
    context.history = []
    context.vehicle = None
    
    if user == "Guest":
        return context

    # Find customer linked to this user
    customer = frappe.db.get_value("Customer", {"custom_user": user}, "name")
    if not customer:
        # Fallback: check by email if the above custom link isn't set
        customer = frappe.db.get_value("Customer", {"email_id": user}, "name")
        
    if not customer:
        return context

    # 1. Fetch Active Request (In Progress)
    active = frappe.db.get_all(
        "Vehicle Service Request",
        filters={"customer": customer, "status": ["not in", ["Released", "Cancelled"]]},
        fields=["name", "vehicle", "status", "problem_description", "mechanic", "creation"],
        order_by="creation desc",
        limit=1
    )
    if active:
        req = active[0]
        # Calculate progress % based on status
        stations = ["Pending", "Quoted", "Approved", "Repairing", "Repairing Done", "Released"]
        current_idx = stations.index(req.status) if req.status in stations else 0
        req.progress = int((current_idx / (len(stations)-1)) * 100)
        
        # Get mechanic name
        if req.mechanic:
            req.mechanic_name = frappe.db.get_value("Vehicle Mechanic", req.mechanic, "mechanic_name")
        
        context.active_request = req

    # 2. Fetch Service History
    context.history = frappe.db.get_all(
        "Vehicle Service Request",
        filters={"customer": customer, "status": "Released"},
        fields=["name", "vehicle", "problem_description", "date", "cost", "status"],
        order_by="date desc",
        limit=5
    )

    # 3. Fetch Primary Vehicle Stats
    vehicle_id = frappe.db.get_value("Vehicle Master", {"customer": customer}, "name")
    if vehicle_id:
        context.vehicle = frappe.get_doc("Vehicle Master", vehicle_id)

    return context
