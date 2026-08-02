import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


def execute():
	if not frappe.db.exists("DocType", "Vehicle"):
		return

	make_property_setter("Vehicle", "truck_type", "reqd", 0, "Check")
	frappe.clear_cache(doctype="Vehicle")
