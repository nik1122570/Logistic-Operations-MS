frappe.ui.form.on("Trip Statement", {
	refresh(frm) {
		render_trip_profit_dashboard(frm);
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

	total_revenue(frm) {
		render_trip_profit_dashboard(frm);
	},

	total_expenses(frm) {
		render_trip_profit_dashboard(frm);
	},

	gross_profit(frm) {
		render_trip_profit_dashboard(frm);
	},

	profit_margin(frm) {
		render_trip_profit_dashboard(frm);
	},
});

frappe.ui.form.on("Trip Revenue Item", {
	qty(frm, cdt, cdn) {
		calculate_revenue_amount(frm, cdt, cdn);
	},
	rate(frm, cdt, cdn) {
		calculate_revenue_amount(frm, cdt, cdn);
	},
	revenue_items_add(frm) {
		update_totals(frm);
	},
	revenue_items_remove(frm) {
		update_totals(frm);
	},
});

frappe.ui.form.on("Trip Expense Item", {
	qty(frm, cdt, cdn) {
		calculate_expense_amount(frm, cdt, cdn);
	},
	rate(frm, cdt, cdn) {
		calculate_expense_amount(frm, cdt, cdn);
	},
	expense_items_add(frm) {
		update_totals(frm);
	},
	expense_items_remove(frm) {
		update_totals(frm);
	},
});

function render_trip_profit_dashboard(frm) {
	const revenue = flt(frm.doc.total_revenue);
	const expenses = flt(frm.doc.total_expenses);
	const profit = flt(frm.doc.gross_profit);
	const margin = flt(frm.doc.profit_margin);
	const currency = frm.doc.currency;
	const total_movement = Math.max(revenue + expenses, 1);
	const revenue_width = Math.min((revenue / total_movement) * 100, 100);
	const expense_width = Math.min((expenses / total_movement) * 100, 100);
	const profit_status = profit >= 0 ? __("Profitable") : __("Loss Making");
	const profit_class = profit >= 0 ? "is-positive" : "is-negative";

	const cards = [
		{
			label: __("Revenue"),
			value: format_currency(revenue, currency),
			class_name: "revenue",
			accent: "#0f766e",
		},
		{
			label: __("Total Expenses"),
			value: format_currency(expenses, currency),
			class_name: "expenses",
			accent: "#b45309",
		},
		{
			label: __("Profit"),
			value: format_currency(profit, currency),
			class_name: profit_class,
			accent: profit >= 0 ? "#15803d" : "#b91c1c",
		},
		{
			label: __("Profit Margin"),
			value: `${format_number(margin, null, 2)}%`,
			class_name: profit_class,
			accent: profit >= 0 ? "#2563eb" : "#b91c1c",
		},
	];

	const card_html = cards
		.map(
			(card) => `
				<div class="tetax-profit-card ${card.class_name}" style="--accent: ${card.accent}">
					<div class="tetax-profit-card-label">${card.label}</div>
					<div class="tetax-profit-card-value">${card.value}</div>
				</div>
			`
		)
		.join("");

	frm.get_field("trip_profit_dashboard").$wrapper.html(`
		<style>
			.tetax-profit-dashboard {
				border: 1px solid #d8dee9;
				background: linear-gradient(135deg, #f8fafc 0%, #eef6f3 52%, #f8f1e7 100%);
				border-radius: 8px;
				padding: 14px;
				margin: 0 0 14px;
				box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
			}
			.tetax-profit-dashboard-head {
				display: flex;
				justify-content: space-between;
				gap: 12px;
				align-items: center;
				margin-bottom: 12px;
			}
			.tetax-profit-title {
				font-size: 15px;
				font-weight: 700;
				color: #172033;
			}
			.tetax-profit-route {
				color: #64748b;
				font-size: 12px;
				margin-top: 2px;
			}
			.tetax-profit-status {
				border: 1px solid rgba(15, 23, 42, 0.12);
				border-radius: 999px;
				background: #ffffff;
				color: ${profit >= 0 ? "#166534" : "#991b1b"};
				font-weight: 700;
				font-size: 12px;
				padding: 5px 10px;
				white-space: nowrap;
			}
			.tetax-profit-grid {
				display: grid;
				grid-template-columns: repeat(4, minmax(0, 1fr));
				gap: 10px;
			}
			.tetax-profit-card {
				background: rgba(255, 255, 255, 0.9);
				border: 1px solid rgba(15, 23, 42, 0.08);
				border-left: 4px solid var(--accent);
				border-radius: 8px;
				padding: 10px 12px;
				min-height: 76px;
			}
			.tetax-profit-card-label {
				font-size: 11px;
				font-weight: 700;
				text-transform: uppercase;
				color: #64748b;
				letter-spacing: 0;
			}
			.tetax-profit-card-value {
				font-size: 19px;
				line-height: 1.25;
				font-weight: 800;
				color: #172033;
				margin-top: 8px;
				overflow-wrap: anywhere;
			}
			.tetax-profit-card.is-positive .tetax-profit-card-value {
				color: #166534;
			}
			.tetax-profit-card.is-negative .tetax-profit-card-value {
				color: #991b1b;
			}
			.tetax-profit-bars {
				display: grid;
				grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
				gap: 10px;
				margin-top: 12px;
			}
			.tetax-profit-bar-label {
				display: flex;
				justify-content: space-between;
				color: #475569;
				font-size: 12px;
				font-weight: 600;
				margin-bottom: 5px;
			}
			.tetax-profit-bar-track {
				height: 8px;
				background: rgba(15, 23, 42, 0.08);
				border-radius: 999px;
				overflow: hidden;
			}
			.tetax-profit-bar-fill {
				height: 100%;
				border-radius: 999px;
			}
			.tetax-profit-bar-fill.revenue {
				background: #0f766e;
			}
			.tetax-profit-bar-fill.expenses {
				background: #b45309;
			}
			@media (max-width: 900px) {
				.tetax-profit-grid,
				.tetax-profit-bars {
					grid-template-columns: repeat(2, minmax(0, 1fr));
				}
			}
			@media (max-width: 540px) {
				.tetax-profit-dashboard-head,
				.tetax-profit-grid,
				.tetax-profit-bars {
					grid-template-columns: 1fr;
					display: grid;
				}
			}
		</style>
		<div class="tetax-profit-dashboard">
			<div class="tetax-profit-dashboard-head">
				<div>
					<div class="tetax-profit-title">${__("Trip Performance")}</div>
					<div class="tetax-profit-route">${escape_html(frm.doc.truck || __("No truck"))} / ${escape_html(
		frm.doc.route || __("No route")
	)}</div>
				</div>
				<div class="tetax-profit-status">${profit_status}</div>
			</div>
			<div class="tetax-profit-grid">${card_html}</div>
			<div class="tetax-profit-bars">
				<div>
					<div class="tetax-profit-bar-label"><span>${__("Revenue Share")}</span><span>${format_number(
		revenue_width,
		null,
		1
	)}%</span></div>
					<div class="tetax-profit-bar-track"><div class="tetax-profit-bar-fill revenue" style="width: ${revenue_width}%"></div></div>
				</div>
				<div>
					<div class="tetax-profit-bar-label"><span>${__("Expense Share")}</span><span>${format_number(
		expense_width,
		null,
		1
	)}%</span></div>
					<div class="tetax-profit-bar-track"><div class="tetax-profit-bar-fill expenses" style="width: ${expense_width}%"></div></div>
				</div>
			</div>
		</div>
	`);
}

function escape_html(value) {
	return String(value || "")
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#039;");
}

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
