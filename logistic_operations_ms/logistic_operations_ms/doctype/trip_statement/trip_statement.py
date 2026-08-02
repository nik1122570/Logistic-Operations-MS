import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import flt, nowdate


class TripStatement(Document):
	def autoname(self):
		if self.truck and self.route:
			self.name = self.get_trip_statement_name()
			return

		self.name = make_autoname("TTS-.YYYY.-.#####")

	def validate(self):
		self.set_default_currency()
		self.set_vehicle_cost_center()
		self.calculate_totals()
		self.validate_posted_statement_changes()

	def on_update(self):
		self.auto_post_new_expenses()

	def set_default_currency(self):
		if not self.currency and self.company:
			self.currency = frappe.get_cached_value("Company", self.company, "default_currency")

	def set_vehicle_cost_center(self):
		if self.truck:
			self.cost_center = frappe.get_cached_value("Vehicle", self.truck, "cost_center")

	def refresh_vehicle_cost_center_for_posting(self):
		self.set_vehicle_cost_center()
		if self.truck and not self.cost_center:
			frappe.throw(_("Set a Cost Center on Vehicle {0} before posting.").format(self.truck))

	def get_trip_statement_name(self):
		base_name = f"{self.truck} {self.route}".strip()
		if not frappe.db.exists("Trip Statement", base_name):
			return base_name

		counter = 2
		while frappe.db.exists("Trip Statement", f"{base_name} {counter}"):
			counter += 1

		return f"{base_name} {counter}"

	def calculate_totals(self):
		total_revenue = 0
		total_expenses = 0

		for row in self.revenue_items:
			row.amount = flt(row.qty) * flt(row.rate)
			total_revenue += flt(row.amount)

		for row in self.expense_items:
			row.amount = flt(row.qty) * flt(row.rate)
			total_expenses += flt(row.amount)

		self.total_revenue = total_revenue
		self.total_expenses = total_expenses
		self.gross_profit = total_revenue - total_expenses
		self.profit_margin = (self.gross_profit / total_revenue * 100) if total_revenue else 0

	def validate_posted_statement_changes(self):
		if self.is_new() or self.posting_status != "Posted":
			return

		previous = self.get_doc_before_save()
		if not previous or previous.posting_status != "Posted":
			return

		if self.get_table_signature("revenue_items") != previous.get_table_signature("revenue_items"):
			frappe.throw(_("Revenue rows are locked after posting. Cancel the Sales Invoice if they must change."))

		if not self.flags.allow_expense_update:
			self.validate_posted_expense_rows(previous)

	def validate_posted_expense_rows(self, previous):
		current_rows = {row.name: row for row in self.expense_items if row.name}

		for old_row in previous.expense_items:
			if not old_row.purchase_invoice:
				continue

			current_row = current_rows.get(old_row.name)
			if not current_row:
				frappe.throw(_("Expense row {0} is already linked to a Purchase Invoice and cannot be removed.").format(old_row.idx))

			if self.get_expense_row_signature(current_row) != self.get_expense_row_signature(old_row):
				frappe.throw(
					_("Expense row {0} is already linked to Purchase Invoice {1} and cannot be edited.").format(
						old_row.idx,
						old_row.purchase_invoice,
					)
				)

		for row in self.expense_items:
			if row.name not in {old_row.name for old_row in previous.expense_items} and row.purchase_invoice:
				frappe.throw(_("New expense rows cannot be manually linked to a Purchase Invoice."))

	def get_table_signature(self, table_fieldname):
		table_fields = {
			"revenue_items": ("description", "item_code", "qty", "rate", "amount", "income_account"),
			"expense_items": (
				"description",
				"item_code",
				"qty",
				"rate",
				"amount",
				"expense_account",
				"purchase_invoice",
			),
		}

		return [
			tuple(row.get(fieldname) for fieldname in table_fields[table_fieldname])
			for row in self.get(table_fieldname)
		]

	def get_expense_row_signature(self, row):
		return (
			row.description,
			row.item_code,
			flt(row.qty),
			flt(row.rate),
			flt(row.amount),
			row.expense_account,
			row.purchase_invoice,
		)

	@frappe.whitelist()
	def post_statement(self):
		if self.posting_status == "Posted":
			frappe.throw(_("Trip Statement {0} is already posted.").format(self.name))

		self.validate_for_posting()
		self.calculate_totals()

		sales_invoice = self.create_sales_invoice()
		purchase_invoices = self.create_purchase_invoices()

		self.sales_invoice = sales_invoice.name if sales_invoice else None
		self.posting_status = "Posted"
		self.save(ignore_permissions=True)

		frappe.msgprint(
			_("Trip Statement posted. Created {0} Sales Invoice and {1} Purchase Invoice(s).").format(
				1 if sales_invoice else 0,
				len(purchase_invoices),
			)
		)

		return {
			"sales_invoice": self.sales_invoice,
			"purchase_invoices": [invoice.name for invoice in purchase_invoices],
			"total_revenue": self.total_revenue,
			"total_expenses": self.total_expenses,
			"gross_profit": self.gross_profit,
			"profit_margin": self.profit_margin,
		}

	@frappe.whitelist()
	def post_new_expenses(self):
		if self.posting_status != "Posted":
			frappe.throw(_("Post the Trip Statement first before posting additional expenses."))

		self.validate_for_posting()
		purchase_invoices = self.create_purchase_invoices()
		if not purchase_invoices:
			frappe.throw(_("There are no new expense rows to post."))

		self.calculate_totals()
		self.save(ignore_permissions=True)

		frappe.msgprint(
			_("Created {0} additional Purchase Invoice(s). Profitability has been updated.").format(
				len(purchase_invoices)
			)
		)

		return {
			"purchase_invoices": [invoice.name for invoice in purchase_invoices],
			"total_expenses": self.total_expenses,
			"gross_profit": self.gross_profit,
			"profit_margin": self.profit_margin,
		}

	@frappe.whitelist()
	def update_expenses(self, expense_rows):
		if self.posting_status != "Posted":
			frappe.throw(_("Only posted Trip Statements can update posted expenses."))

		if isinstance(expense_rows, str):
			expense_rows = json.loads(expense_rows)

		if not expense_rows:
			frappe.throw(_("Select at least one expense row to remove."))

		expense_rows = set(expense_rows)
		rows_by_name = {row.name: row for row in self.expense_items}
		selected_rows = [rows_by_name[row_name] for row_name in expense_rows if row_name in rows_by_name]

		if len(selected_rows) != len(expense_rows):
			frappe.throw(_("Some selected expense rows were not found. Please refresh and try again."))

		self.validate_selected_expense_invoices(selected_rows, expense_rows)
		self.cancel_expense_purchase_invoices(selected_rows)
		self.set("expense_items", [row for row in self.expense_items if row.name not in expense_rows])
		self.calculate_totals()
		self.flags.allow_expense_update = True
		self.flags.skip_auto_post_new_expenses = True
		self.save(ignore_permissions=True)

		return {
			"removed_rows": len(selected_rows),
			"total_expenses": self.total_expenses,
			"gross_profit": self.gross_profit,
			"profit_margin": self.profit_margin,
		}

	def validate_selected_expense_invoices(self, selected_rows, selected_row_names):
		selected_invoices = {row.purchase_invoice for row in selected_rows if row.purchase_invoice}

		for invoice in selected_invoices:
			linked_rows = [row for row in self.expense_items if row.purchase_invoice == invoice]
			if any(row.name not in selected_row_names for row in linked_rows):
				frappe.throw(
					_(
						"Purchase Invoice {0} is linked to more than one expense row. Select all rows linked to this invoice."
					).format(invoice)
				)

	def cancel_expense_purchase_invoices(self, selected_rows):
		for invoice_name in sorted({row.purchase_invoice for row in selected_rows if row.purchase_invoice}):
			invoice = frappe.get_doc("Purchase Invoice", invoice_name)
			if invoice.docstatus == 1:
				invoice.cancel()
			elif invoice.docstatus == 0:
				invoice.delete()

	def auto_post_new_expenses(self):
		if self.flags.skip_auto_post_new_expenses:
			return

		if self.posting_status != "Posted" or not self.get_unposted_expense_items():
			return

		self.validate_for_posting()
		self.create_purchase_invoices()
		self.calculate_totals()
		self.flags.skip_auto_post_new_expenses = True
		self.save(ignore_permissions=True)

	def validate_for_posting(self):
		if not self.company:
			frappe.throw(_("Company is required before posting."))

		self.refresh_vehicle_cost_center_for_posting()

		if not self.revenue_items and not self.expense_items:
			frappe.throw(_("Add at least one revenue or expense row before posting."))

		if self.revenue_items and not self.customer:
			frappe.throw(_("Customer is required when posting revenue."))

		if self.expense_items and not self.supplier:
			frappe.throw(_("Supplier is required when posting expenses."))

		for row in self.revenue_items:
			if not row.description:
				frappe.throw(_("Description is required for every revenue row."))
			if not flt(row.qty):
				frappe.throw(_("Quantity is required for revenue row {0}.").format(row.idx))
			if not flt(row.rate):
				frappe.throw(_("Rate is required for revenue row {0}.").format(row.idx))
			if not row.item_code and not self.default_revenue_item:
				frappe.throw(_("Set a Revenue Item on row {0} or set Default Revenue Item.").format(row.idx))

		for row in self.expense_items:
			if not row.description:
				frappe.throw(_("Description is required for every expense row."))
			if not flt(row.qty):
				frappe.throw(_("Quantity is required for expense row {0}.").format(row.idx))
			if not flt(row.rate):
				frappe.throw(_("Rate is required for expense row {0}.").format(row.idx))
			if not row.item_code and not self.default_expense_item:
				frappe.throw(_("Set an Expense Item on row {0} or set Default Expense Item.").format(row.idx))

	def create_sales_invoice(self):
		if not self.revenue_items:
			return None

		invoice = frappe.new_doc("Sales Invoice")
		invoice.company = self.company
		invoice.customer = self.customer
		invoice.currency = self.currency
		invoice.posting_date = self.posting_date or nowdate()
		invoice.due_date = self.due_date or self.posting_date or nowdate()
		invoice.set_posting_time = 1
		invoice.remarks = _("Created from Trip Statement {0}").format(self.name)

		if self.cost_center:
			invoice.cost_center = self.cost_center

		for row in self.revenue_items:
			item = {
				"item_code": row.item_code or self.default_revenue_item,
				"description": row.description,
				"qty": flt(row.qty),
				"rate": flt(row.rate),
			}
			if row.income_account or self.default_income_account:
				item["income_account"] = row.income_account or self.default_income_account
			if self.cost_center:
				item["cost_center"] = self.cost_center
			invoice.append("items", item)

		invoice.insert(ignore_permissions=True)
		if self.submit_linked_invoices:
			invoice.submit()

		return invoice

	def create_purchase_invoices(self):
		unposted_expense_items = self.get_unposted_expense_items()

		if not unposted_expense_items:
			return []

		invoices = []
		for row in unposted_expense_items:
			invoice = frappe.new_doc("Purchase Invoice")
			invoice.company = self.company
			invoice.supplier = self.supplier
			invoice.currency = self.currency
			invoice.posting_date = self.posting_date or nowdate()
			invoice.set_posting_time = 1
			invoice.bill_date = self.posting_date or nowdate()
			invoice.bill_no = f"{self.name}-{row.idx}-{self.supplier}"[:140]
			invoice.remarks = _("Created from Trip Statement {0}, expense row {1}").format(self.name, row.idx)

			if self.cost_center:
				invoice.cost_center = self.cost_center

			item = {
				"item_code": row.item_code or self.default_expense_item,
				"description": row.description,
				"qty": flt(row.qty),
				"rate": flt(row.rate),
			}
			if row.expense_account or self.default_expense_account:
				item["expense_account"] = row.expense_account or self.default_expense_account
			if self.cost_center:
				item["cost_center"] = self.cost_center
			invoice.append("items", item)

			invoice.insert(ignore_permissions=True)
			if self.submit_linked_invoices:
				invoice.submit()

			row.purchase_invoice = invoice.name
			invoices.append(invoice)

		return invoices

	def get_unposted_expense_items(self):
		return [row for row in self.expense_items if not row.purchase_invoice]

	@frappe.whitelist()
	def cancel_linked_invoices(self):
		if self.posting_status != "Posted":
			frappe.throw(_("Only posted Trip Statements can have linked invoices cancelled."))

		linked_docs = []
		if self.sales_invoice:
			linked_docs.append(("Sales Invoice", self.sales_invoice))

		for row in self.expense_items:
			if row.purchase_invoice:
				linked_docs.append(("Purchase Invoice", row.purchase_invoice))

		for doctype, name in sorted(set(linked_docs)):
			doc = frappe.get_doc(doctype, name)
			if doc.docstatus == 1:
				doc.cancel()

		self.sales_invoice = None
		for row in self.expense_items:
			row.purchase_invoice = None
		self.posting_status = "Not Posted"
		self.save(ignore_permissions=True)

		return True
