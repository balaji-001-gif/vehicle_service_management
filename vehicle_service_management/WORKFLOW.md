# Workshop ERP — Internal Team Workflow Guide ⚙️

This document outlines the standard operating procedure (SOP) for the Workshop Team (Advisors, Mechanics, and Managers) to manage a vehicle's lifecycle from entry to exit using the new Workshop ERP system.

---

## 🏎️ Stage 1: Reception & Booking
**Who:** Customer or Service Advisor  
**Action:** Visit `/book-service`  
1. Fill in customer mobile and vehicle registration.
2. The system checks if the customer or vehicle exists; if not, it creates them in the **Vehicle Master**.
3. **Result:** A new `Vehicle Service Request` is created with status **Pending**.

## 💰 Stage 2: Estimation & Approval
**Who:** Service Advisor / Manager  
**Action:** Admin Dashboard (`/admin-dashboard`)  
1. Assign a **Mechanic** to the request.
2. Enter the estimated **Cost** in the Request details.
3. Update status to **Quoted**.
4. **Customer Approval:** The customer is notified (via tracking link). They must click **"Approve Rate"** on their portal.
5. **Result:** Status moves to **Approved**.

## 🔍 Stage 3: Digital Vehicle Inspection (DVI)
**Who:** Mechanic  
**Action:** Mechanic Dashboard (`/mechanic-dashboard`)  
1. On the assigned card, click **"🔍 Run Digital Inspection"**.
2. Complete the 10-point checklist (Oil, Brakes, Tires, etc.).
3. **Crucial:** Use the camera to take photos of any pre-existing damage or issues.
4. Save the report. It is now visible to the Admin as proof for the customer.

## 🛠️ Stage 4: Service Operations & Inventory
**Who:** Mechanic  
**Action:** Mechanic Dashboard  
1. Click **"Repairing"** to start the clock.
2. **Operations:** Update Bay status (e.g., General Service, Cleaning). Use **"+ Add Operation"** if extra work is found.
3. **Inventory:** Click **"+ Add Part"** to log every spare part used (Engine Oil, Brake Pads, etc.). 
   - *Note: Parts must exist in ERPNext Item Master.*
4. **Paint Shop:** If a painting bay is active, click **"🎨 Edit Paint Job"** to record paint codes and drying times.

## 🏁 Stage 5: Completion & Invoicing
**Who:** Mechanic -> Admin  
**Action:** 
1. **Mechanic:** Once work is done, click **"Repairing Done"**.
2. **Advisor:** Confirm everything is correct in the Admin Portal.
3. **Advisor:** Change status to **Released**.

## 📊 Stage 6: Automatic Backend Magic (ERP Integration)
**System Action:** Triggered instantly when status moves to **Released**.  
1. **Stock Deduction:** The system creates a native `Stock Entry (Material Issue)` for all Spare Parts logged in Stage 4. Stock is deducted (Material Issue) from the warehouse automatically.
2. **Invoicing:** A native ERPNext `Sales Invoice` is generated. It includes:
   - All Spare Parts as line items with their rates.
   - Labor cost (if specified).
   - If it's an **Insurance (Cashless)** job, the invoice is automatically restricted to the **Deductible amount** only.

## 💳 Stage 7: Payment & Feedback
**Who:** Customer  
**Action:** Tracking Portal (`/service-tracking`)  
1. Customer clicks **"Pay Now"**.
2. After payment, the status marks as **Paid** in the system.
3. **Feedback:** A 5-star rating form appears immediately for the customer to rate the service.

---

## 🛠️ Maintenance & Master Data
- **Vehicle Master:** View history of any car by searching its number in the Admin search.
- **Workshop Equipment:** Monitor Lifts and Paint Booths via the **🏗️ Equipment** tab in Admin Dashboard.
- **Insurance Claim:** Create a claim record before starting an insurance job to enable smart split-billing.
