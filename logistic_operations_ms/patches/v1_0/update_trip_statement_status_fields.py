import frappe


def execute():
	if not frappe.db.exists("DocType", "Trip Statement"):
		return

	frappe.db.sql(
		"""
		update `tabTrip Statement`
		set posting_status = 'Posted'
		where status = 'Posted'
			or ifnull(sales_invoice, '') != ''
		"""
	)
	frappe.db.sql(
		"""
		update `tabTrip Statement`
		set posting_status = 'Posted'
		where name in (
			select parent
			from `tabTrip Expense Item`
			where ifnull(purchase_invoice, '') != ''
		)
		"""
	)
	frappe.db.sql(
		"""
		update `tabTrip Statement`
		set posting_status = 'Not Posted'
		where ifnull(posting_status, '') = ''
		"""
	)
	frappe.db.sql(
		"""
		update `tabTrip Statement`
		set status = case
			when status = 'Closed' then 'Completed'
			else 'On Trip'
		end
		where status not in ('On Trip', 'Completed')
		"""
	)
