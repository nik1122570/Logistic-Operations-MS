import frappe


def execute():
	if not frappe.db.exists("DocType", "Trip Statement"):
		return

	frappe.db.sql(
		"""
		update `tabTrip Statement` statement
		inner join `tabVehicle` vehicle on vehicle.name = statement.truck
		set statement.cost_center = vehicle.cost_center
		where ifnull(statement.cost_center, '') = ''
			and ifnull(vehicle.cost_center, '') != ''
		"""
	)
