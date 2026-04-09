import frappe
from frappe.utils import add_days, nowdate

def populate():
    print("Starting Demo Data Population...")
    
    # 1. Ensure a basic Customer exists
    if not frappe.db.exists("Customer", "Demo Customer"):
        frappe.get_doc({
            "doctype": "Customer",
            "customer_name": "Demo Customer",
            "customer_group": "All Customer Groups",
            "territory": "All Territories",
            "customer_type": "Individual"
        }).insert(ignore_permissions=True)
    
    # 2. Workshop Equipment
    equipment = [
        {"name": "Hydraulic Lift A1", "type": "2-Post Lift", "status": "Available"},
        {"name": "Hydraulic Lift B2", "type": "4-Post Lift", "status": "In Use"},
        {"name": "Premium Paint Booth", "type": "Paint Booth", "status": "Under Maintenance"},
        {"name": "Smart Wheel Aligner", "type": "Wheel Aligner", "status": "Available"}
    ]
    for eq in equipment:
        if not frappe.db.exists("Workshop Equipment", eq["name"]):
            frappe.get_doc({
                "doctype": "Workshop Equipment",
                "equipment_name": eq["name"],
                "type": eq["type"],
                "status": eq["status"]
            }).insert()
            print(f"Created Equipment: {eq['name']}")

    # 3. Service Packages
    packages = [
        {"name": "Standard Petrol Service", "model": "Sedan"},
        {"name": "Electric Bike Checkup", "model": "EV Bike"},
        {"name": "Premium Detailing & Polish", "model": "All Models"}
    ]
    for pkg in packages:
        if not frappe.db.exists("Service Package", pkg["name"]):
            frappe.get_doc({
                "doctype": "Service Package",
                "package_name": pkg["name"],
                "vehicle_model": pkg["model"],
                "description": f"Standard maintenance package for {pkg['model']}"
            }).insert()
            print(f"Created Package: {pkg['name']}")

    # 4. Vehicles
    vehicles = [
        {"number": "MH-12-PA-1234", "make": "Toyota", "model": "Innova", "fuel": "Diesel", "mileage": 45000},
        {"number": "KA-05-EV-9999", "make": "Tesla", "model": "Model 3", "fuel": "Electric (EV)", "mileage": 1200},
        {"number": "DL-01-BK-5555", "make": "Honda", "model": "Activa", "fuel": "Petrol", "mileage": 15000}
    ]
    for v in vehicles:
        if not frappe.db.exists("Vehicle Master", v["number"]):
            frappe.get_doc({
                "doctype": "Vehicle Master",
                "vehicle_number": v["number"],
                "make": v["make"],
                "model": v["model"],
                "fuel_type": v["fuel"],
                "current_mileage": v["mileage"],
                "customer": "Demo Customer"
            }).insert()
            print(f"Created Vehicle: {v['number']}")

    # 5. Mechanics (Linking to Administrator)
    mechanics = [
        {"name": "John Master Mechanic", "mobile": "9876543210", "skill": "Engine Specialist"},
        {"name": "Alice Paint Pro", "mobile": "9988776655", "skill": "Body & Paint Work"}
    ]
    for m in mechanics:
        if not frappe.db.exists("Vehicle Mechanic", {"user": "Administrator"}): # Simulating multiple mechanics for demo
             # In a real scenario, each mechanic would have a unique user.
             # For demo purposes, we check if at least one exists.
             pass
        
        # We try to create at least one demo mechanic record
        if not frappe.db.exists("Vehicle Mechanic", m["name"]):
            try:
                frappe.get_doc({
                    "doctype": "Vehicle Mechanic",
                    "user": "Administrator",
                    "mechanic_name": m["name"],
                    "mobile": m["mobile"],
                    "skill": m["skill"],
                    "status": 1
                }).insert()
                print(f"Created Mechanic: {m['name']}")
            except frappe.DuplicateEntryError:
                pass

    # 6. Service Requests
    if frappe.db.exists("Vehicle Master", "MH-12-PA-1234"):
        request = frappe.get_doc({
            "doctype": "Vehicle Service Request",
            "customer": "Demo Customer",
            "vehicle": "MH-12-PA-1234",
            "date": nowdate(),
            "status": "Repairing",
            "problem_description": "Engine making strange noise when idling.",
            "category": "four wheeler"
        })
        request.insert(ignore_if_duplicate=True)
        print("Created Sample Service Request")

    # 7. Inspections
    if frappe.db.exists("Vehicle Master", "KA-05-EV-9999"):
        inspection = frappe.get_doc({
            "doctype": "Vehicle Inspection",
            "vehicle": "KA-05-EV-9999",
            "date": nowdate(),
            "inspector": "Administrator"
        })
        inspection.insert(ignore_if_duplicate=True)
        print("Created Sample Inspection Report")

    frappe.db.commit()
    print("Demo Data Population Complete!")

if __name__ == "__main__":
    populate()
