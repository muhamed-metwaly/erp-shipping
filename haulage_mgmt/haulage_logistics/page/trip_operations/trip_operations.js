frappe.provide("haulage_mgmt.trip_ops");

haulage_mgmt.trip_ops.flt = (v) => (frappe.utils && frappe.utils.flt ? frappe.utils.flt(v) : parseFloat(v) || 0);

function trip_ops_ensure_hub() {
	if (typeof haulage_mgmt === "undefined") {
		frappe.provide("haulage_mgmt");
	}
	return Boolean(haulage_mgmt.trip && haulage_mgmt.trip.status_actions_for);
}

frappe.pages["trip-operations"].on_page_load = function (wrapper) {
	try {
		const page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("All Trips"),
			single_column: true,
		});
		page.trip_operations = new TripOperationsHub(page);
	} catch (e) {
		console.error(e);
		$(wrapper).html(
			`<div class="text-danger padded">${__(
				"Could not load All Trips page. Run bench build --app haulage_mgmt and clear cache.",
			)}</div>`,
		);
	}
};

frappe.pages["trip-operations"].on_page_show = function (wrapper) {
	if (wrapper.page && wrapper.page.trip_operations) {
		wrapper.page.trip_operations.refresh();
	}
};

class TripOperationsHub {
	constructor(page) {
		this.page = page;
		if (!trip_ops_ensure_hub()) {
			this.page.main.html(
				`<div class="alert alert-warning">${__(
					"Trip scripts not loaded. Run: bench build --app haulage_mgmt, bench --site [yoursite] clear-cache, then hard-refresh (Ctrl+Shift+R).",
				)}</div>`,
			);
			return;
		}
		this.make_toolbar();
		this.make_filters();
		this.$body = $('<div class="trip-operations-hub"></div>').appendTo(this.page.main);
		this.refresh();
	}

	make_toolbar() {
		this.page.add_inner_button(__("New Haulage Trip"), () => frappe.new_doc("Haulage Trip"));
	}

	make_filters() {
		this.page.add_field({
			fieldtype: "Select",
			fieldname: "trip_status",
			label: __("Status"),
			options: haulage_mgmt.i18n
				? haulage_mgmt.i18n.trip_status_filter_options()
				: "\nPreparing\nStarted\nPaused\nCompleted\nCancelled",
			change: () => this.refresh(),
		});
		this.page.add_inner_button(__("Refresh"), () => this.refresh());
	}

	refresh() {
		if (!this.$body || !trip_ops_ensure_hub()) {
			return;
		}
		const status = this.page.fields_dict.trip_status?.get_value();
		this.$body.html(`<p class="text-muted">${__("Loading trips...")}</p>`);
		frappe.call({
			method:
				"haulage_mgmt.haulage_logistics.page.trip_operations.trip_operations.get_all_trips_hub",
			args: { status: status || null },
			freeze: true,
			freeze_message: __("Loading trips..."),
			callback: (r) => {
				if (r.exc) {
					let msg = __("Could not load trips.");
					this.show_error(msg);
					return;
				}
				try {
					this.render(r.message || []);
				} catch (err) {
					console.error(err);
					this.show_error(__("Could not display trip list."));
				}
			},
			error: () => this.show_error(__("Server error while loading trips.")),
		});
	}

	show_error(msg) {
		const text = frappe.utils.strip_html(String(msg || __("Error")));
		this.$body.html(`<div class="alert alert-danger">${frappe.utils.escape_html(text)}</div>`);
	}

	status_badge(status) {
		return haulage_mgmt.i18n ? haulage_mgmt.i18n.status_badge(status) : __(status || "");
	}

	status_actions_html(trip, trip_status) {
		const actions = haulage_mgmt.trip.status_actions_for(trip_status);
		let html = "";
		for (const act of actions) {
			const cls = act.btn_class || "btn-default";
			html += `<button type="button" class="btn btn-xs ${cls} trip-ops-status"
				data-trip="${trip}" data-action="${act.action}" data-status="${frappe.utils.escape_html(
				trip_status || "Preparing",
			)}">${act.label}</button> `;
		}
		return html || `<span class="text-muted">${__("No actions")}</span>`;
	}

	render(rows) {
		if (!rows.length) {
			this.$body.html(`<p class="text-muted">${__("No trips found.")}</p>`);
			return;
		}

		const fmt = (v) => frappe.format(v, { fieldtype: "Currency" });
		let html = `<p class="text-muted">${__(
			"Manage trips: change status here, open the trip for shipments, or open Accounting for revenue, expenses and custody.",
		)}</p>
		<div class="table-responsive">
		<table class="table table-bordered table-hover trip-ops-table">
			<thead><tr>
				<th>${__("Trip")}</th>
				<th>${__("Status")}</th>
				<th>${__("Date")}</th>
				<th>${__("Driver")}</th>
				<th>${__("Truck")}</th>
				<th class="text-right">${__("Revenue")}</th>
				<th class="text-right">${__("Expenses")}</th>
				<th class="text-right">${__("Custody")}</th>
				<th class="text-right">${__("Net income")}</th>
				<th>${__("Trip actions")}</th>
				<th></th>
			</tr></thead><tbody>`;

		for (const row of rows) {
			const trip = frappe.utils.escape_html(row.trip || row.name);
			const status = row.trip_status || "Preparing";
			const net = haulage_mgmt.trip_ops.flt(row.net_income);
			const net_class = net < 0 ? "text-danger" : "text-success";

			html += `<tr class="trip-ops-row" data-trip="${trip}" data-status="${frappe.utils.escape_html(status)}">
				<td><a href="#" class="trip-ops-open" data-trip="${trip}"><b>${trip}</b></a></td>
				<td>${this.status_badge(status)}</td>
				<td>${frappe.utils.escape_html(row.trip_date || "")}</td>
				<td>${frappe.utils.escape_html(row.driver || "")}</td>
				<td>${frappe.utils.escape_html(row.truck || "")}</td>
				<td class="text-right">${fmt(row.revenue)}</td>
				<td class="text-right">${fmt(row.expenses)}</td>
				<td class="text-right">${fmt(row.custody_total)}</td>
				<td class="text-right ${net_class}"><b>${fmt(net)}</b></td>
				<td class="trip-ops-actions">${this.status_actions_html(trip, status)}</td>
				<td class="text-nowrap">
					<button type="button" class="btn btn-xs btn-default trip-ops-open" data-trip="${trip}">${__(
						"Open",
					)}</button>
					<button type="button" class="btn btn-xs btn-primary trip-ops-acct" data-trip="${trip}">${__(
						"Accounting",
					)}</button>
				</td>
			</tr>`;
		}
		html += `</tbody></table></div>`;
		this.$body.html(html);
		this.bind_events();
	}

	bind_events() {
		const hub = this;

		this.$body.find(".trip-ops-open").on("click", function (e) {
			e.preventDefault();
			e.stopPropagation();
			haulage_mgmt.trip.open_trip($(this).data("trip"));
		});

		this.$body.find(".trip-ops-acct").on("click", function (e) {
			e.preventDefault();
			e.stopPropagation();
			haulage_mgmt.trip.open_accounting($(this).data("trip"));
		});

		this.$body.find(".trip-ops-status").on("click", function (e) {
			e.preventDefault();
			e.stopPropagation();
			const $btn = $(this);
			const trip = $btn.data("trip");
			const action = $btn.data("action");
			const row_status = $btn.data("status");
			const act = (haulage_mgmt.trip.status_actions_for(row_status) || []).find(
				(a) => a.action === action,
			);
			haulage_mgmt.trip.run_status_action(trip, action, {
				confirm_message: act && act.confirm ? act.confirm : null,
				on_success: () => hub.refresh(),
			});
		});

		this.$body.find(".trip-ops-row").on("click", function (e) {
			if ($(e.target).closest("a, button").length) {
				return;
			}
			haulage_mgmt.trip.open_trip($(this).data("trip"));
		});
	}
}
