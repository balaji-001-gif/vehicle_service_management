app_name = "vehicle_service_management"
app_title = "Vehicle Service Management"
app_publisher = "Balaji"
app_description = "Vehicle Service Management app for ERPNext V15"
app_email = "balaji@example.com"
app_license = "MIT"

# Required Apps
required_apps = ["frappe", "erpnext"]

# Website Route Rules
# -------------------
website_route_rules = [
	{"from_route": "/service-tracking", "to_route": "service_tracking"},
	{"from_route": "/admin-dashboard", "to_route": "admin_dashboard"},
	{"from_route": "/mechanic-dashboard", "to_route": "mechanic_dashboard"},
	{"from_route": "/book-service", "to_route": "book_service"},
]

# Guest access for the tracking API
guest_title = "Vehicle Service Management"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/vehicle_service_management/css/vehicle_service_management.css"
# app_include_js = "/assets/vehicle_service_management/js/vehicle_service_management.js"

# include js, css files in header of web template
# web_include_css = "/assets/vehicle_service_management/css/vehicle_service_management.css"
# web_include_js = "/assets/vehicle_service_management/js/vehicle_service_management.js"

# Installation
# ------------

# before_install = "vehicle_service_management.install.before_install"
# after_install = "vehicle_service_management.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "vehicle_service_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"vehicle_service_management.tasks.all"
# 	],
# 	"daily": [
# 		"vehicle_service_management.tasks.daily"
# 	],
# 	"hourly": [
# 		"vehicle_service_management.tasks.hourly"
# 	],
# 	"weekly": [
# 		"vehicle_service_management.tasks.weekly"
# 	],
# 	"monthly": [
# 		"vehicle_service_management.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "vehicle_service_management.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "vehicle_service_management.event.get_events"
# }

# Jinja
# ----------

# jinja = {
# 	"methods": "vehicle_service_management.utils.jinja_methods",
# 	"filters": "vehicle_service_management.utils.jinja_filters"
# }

# Fixtures
# ----------

# fixtures = []
