app_name = "logistic_operations_ms"
app_title = "Logistic Operations MS"
app_publisher = "Smart Touch Technologies"
app_description = "Logistics and transport operations management system for Logistics Companies"
app_email = "nickson4422@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "logistic_operations_ms",
# 		"logo": "/assets/logistic_operations_ms/logo.png",
# 		"title": "Logistic Operations MS",
# 		"route": "/logistic_operations_ms",
# 		"has_permission": "logistic_operations_ms.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/logistic_operations_ms/css/logistic_operations_ms.css"
# app_include_js = "/assets/logistic_operations_ms/js/logistic_operations_ms.js"

# include js, css files in header of web template
# web_include_css = "/assets/logistic_operations_ms/css/logistic_operations_ms.css"
# web_include_js = "/assets/logistic_operations_ms/js/logistic_operations_ms.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "logistic_operations_ms/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "logistic_operations_ms/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "logistic_operations_ms.utils.jinja_methods",
# 	"filters": "logistic_operations_ms.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "logistic_operations_ms.install.before_install"
# after_install = "logistic_operations_ms.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "logistic_operations_ms.uninstall.before_uninstall"
# after_uninstall = "logistic_operations_ms.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "logistic_operations_ms.utils.before_app_install"
# after_app_install = "logistic_operations_ms.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "logistic_operations_ms.utils.before_app_uninstall"
# after_app_uninstall = "logistic_operations_ms.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "logistic_operations_ms.notifications.get_notification_config"

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
# 		"logistic_operations_ms.tasks.all"
# 	],
# 	"daily": [
# 		"logistic_operations_ms.tasks.daily"
# 	],
# 	"hourly": [
# 		"logistic_operations_ms.tasks.hourly"
# 	],
# 	"weekly": [
# 		"logistic_operations_ms.tasks.weekly"
# 	],
# 	"monthly": [
# 		"logistic_operations_ms.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "logistic_operations_ms.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "logistic_operations_ms.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "logistic_operations_ms.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["logistic_operations_ms.utils.before_request"]
# after_request = ["logistic_operations_ms.utils.after_request"]

# Job Events
# ----------
# before_job = ["logistic_operations_ms.utils.before_job"]
# after_job = ["logistic_operations_ms.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"logistic_operations_ms.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

