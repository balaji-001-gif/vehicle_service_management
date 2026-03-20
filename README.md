# Vehicle Service Management

A Frappe/ERPNext V15 application for managing vehicle servicing, mechanics, and service requests.

## Features

- **Vehicle Mechanic Management**: Track mechanics, their skills, salary, and active status
- **Service Request Tracking**: Create and manage vehicle service requests with status workflow (Pending → Approved → Repairing → Repairing Done → Released)
- **Customer Feedback**: Collect and manage customer feedback linked to service requests
- **ERPNext Integration**: Uses standard ERPNext Customer DocType and Attendance module

## Installation

```bash
bench get-app https://github.com/balaji-001-gif/vehicleservicemanagement.git
bench --site your-site.local install-app vehicle_service_management
bench --site your-site.local migrate
```

## DocTypes

| DocType | Description |
|---------|-------------|
| Vehicle Mechanic | Mechanics linked to Users with skill, salary, and status |
| Vehicle Service Request | Service requests with vehicle details, problem description, and assigned mechanic |
| Vehicle Service Feedback | Customer feedback linked to service requests |

## License

MIT
