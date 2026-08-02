frappe.ui.form.on("Trip Statement", {
	refresh(frm) {
		frm.trigger("set_queries");

		if (!frm.is_new() && frm.doc.posting_status !== "Posted") {
			frm.add_custom_button(__("Post Statement"), () => {
				frm.call("post_statement").then(() => frm.reload_doc());
			}).addClass("btn-primary");
		}

		if (frm.doc.posting_status === "Posted") {
			frm.add_custom_button(__("Update Expenses"), () => {
				show_update_expenses_dialog(frm);
			});

			frm.add_custom_button(__("Post New Expenses"), () => {
				if (frm.is_dirty()) {
					frm.save().then(() => frm.reload_doc());
					return;
				}

				frm.call("post_new_expenses").then(() => frm.reload_doc());
			}).addClass("btn-primary");

			frm.add_custom_button(__("Cancel Linked Invoices"), () => {
				frm.call("cancel_linked_invoices").then(() => frm.reload_doc());
			});
		}
	},

	set_queries(frm) {
		frm.set_query("truck", () => ({
			filters: {},
		}));

		frm.set_query("default_income_account", () => ({
			filters: {
				company: frm.doc.company,
				is_group: 0,
			},
		}));

		frm.set_query("default_expense_account", () => ({
			filters: {
				company: frm.doc.company,
				is_group: 0,
			},
		}));

		frm.set_query("cost_center", () => ({
			filters: {
				company: frm.doc.company,
				is_group: 0,
			},
		}));
	},

	truck(frm) {
		if (!frm.doc.truck) {
			frm.set_value("cost_center", null);
			return;
		}

		frappe.db.get_value("Vehicle", frm.doc.truck, "cost_center").then((response) => {
			frm.set_value("cost_center", response.message?.cost_center || null);
		});
	},
});

frappe.ui.form.on("Trip Revenue Item", {
	qty(frm, cdt, cdn) {
		calculate_revenue_amount(frm, cdt, cdn);
	},
	rate(frm, cdt, cdn) {
		calculate_revenue_amount(frm, cdt, cdn);
	},
});

frappe.ui.form.on("Trip Expense Item", {
	qty(frm, cdt, cdn) {
		calculate_expense_amount(frm, cdt, cdn);
	},
	rate(frm, cdt, cdn) {
		calculate_expense_amount(frm, cdt, cdn);
	},
});

function show_update_expenses_dialog(frm) {
	const options = (frm.doc.expense_items || [])
		.filter((row) => row.purchase_invoice)
		.map((row) => ({
			label: `${row.idx}. ${row.description || ""} | ${format_currency(row.amount, frm.doc.currency)} | ${
				row.purchase_invoice
			}`,
			value: row.name,
		}));

	if (!options.length) {
		frappe.msgprint(__("There are no posted expense rows to update."));
		return;
	}

	const dialog = new frappe.ui.Dialog({
		title: __("Update Expenses"),
		fields: [
			{
				fieldname: "expense_rows",
				fieldtype: "MultiCheck",
				label: __("Remove Expense Rows"),
				options,
				reqd: 1,
			},
		],
		primary_action_label: __("Cancel Invoices and Remove"),
		primary_action(values) {
			const selected_rows = values.expense_rows || [];
			if (!selected_rows.length) {
				frappe.msgprint(__("Select at least one expense row."));
				return;
			}

			frappe.confirm(
				__("Cancel linked Purchase Invoice(s) and remove the selected expense row(s)?"),
				() => {
					frm.call("update_expenses", { expense_rows: selected_rows }).then(() => {
						dialog.hide();
						frm.reload_doc();
					});
				}
			);
		},
	});

	dialog.show();
}

function calculate_revenue_amount(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", flt(row.qty) * flt(row.rate));
	update_totals(frm);
}

function calculate_expense_amount(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "amount", flt(row.qty) * flt(row.rate));
	update_totals(frm);
}

function update_totals(frm) {
	const revenue = (frm.doc.revenue_items || []).reduce((total, row) => total + flt(row.amount), 0);
	const expenses = (frm.doc.expense_items || []).reduce((total, row) => total + flt(row.amount), 0);
	const profit = revenue - expenses;

	frm.set_value("total_revenue", revenue);
	frm.set_value("total_expenses", expenses);
	frm.set_value("gross_profit", profit);
	frm.set_value("profit_margin", revenue ? (profit / revenue) * 100 : 0);
}
