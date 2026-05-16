frappe.provide("haulage_mgmt.trip");

haulage_mgmt.trip.ACCOUNTING_ROUTE_FLAG = "haulage_accounting_entry";
haulage_mgmt.trip.ACCOUNTING_RELOAD_KEY = "haulage_trip_accounting_reload";

haulage_mgmt.trip.open_trip = function (trip_name) {
	frappe.set_route("Form", "Haulage Trip", trip_name);
};

haulage_mgmt.trip.open_accounting = function (trip_name) {
	frappe.route_options = { [haulage_mgmt.trip.ACCOUNTING_ROUTE_FLAG]: 1 };
	frappe.set_route("Form", "Haulage Trip", trip_name);
};

haulage_mgmt.trip.open_hub = function (view) {
	frappe.route_options = view ? { view } : {};
	frappe.set_route("trip-operations");
};

haulage_mgmt.trip.enter_accounting_mode = function (frm) {
	if (!frm || !frm.doc.name) {
		return;
	}
	frm._haulage_accounting_entry = true;
};

haulage_mgmt.trip.mark_accounting_reload = function (frm) {
	if (!frm || !frm.doc.name) {
		return;
	}
	try {
		sessionStorage.setItem(haulage_mgmt.trip.ACCOUNTING_RELOAD_KEY, frm.doc.name);
	} catch (e) {
		/* private browsing */
	}
};

haulage_mgmt.trip.consume_accounting_reload = function (frm) {
	if (!frm || !frm.doc.name) {
		return false;
	}
	try {
		const pending = sessionStorage.getItem(haulage_mgmt.trip.ACCOUNTING_RELOAD_KEY);
		if (pending && pending === frm.doc.name) {
			frm._haulage_accounting_entry = true;
			sessionStorage.removeItem(haulage_mgmt.trip.ACCOUNTING_RELOAD_KEY);
			return true;
		}
		sessionStorage.removeItem(haulage_mgmt.trip.ACCOUNTING_RELOAD_KEY);
	} catch (e) {
		/* ignore */
	}
	return false;
};

haulage_mgmt.trip.sync_accounting_mode_from_route = function (frm) {
	if (!frm || frm.is_new()) {
		if (frm) {
			frm._haulage_accounting_entry = false;
		}
		return;
	}
	if (frappe.route_options && frappe.route_options[haulage_mgmt.trip.ACCOUNTING_ROUTE_FLAG]) {
		haulage_mgmt.trip.enter_accounting_mode(frm);
		return;
	}
	if (!frm._haulage_accounting_entry) {
		haulage_mgmt.trip.consume_accounting_reload(frm);
	}
};

haulage_mgmt.trip.is_accounting_entry = function (frm) {
	return Boolean(frm && frm._haulage_accounting_entry && !frm.is_new());
};

haulage_mgmt.trip.run_status_action = function (trip_name, action, options = {}) {
	const { confirm_message, on_success, freeze_message } = options;
	const run = () => {
		frappe.call({
			method: "haulage_mgmt.haulage_logistics.api.set_trip_status",
			args: { trip_name, action },
			freeze: true,
			freeze_message: freeze_message || __("Updating trip status..."),
			callback(r) {
				if (r.exc) {
					return;
				}
				if (on_success) {
					on_success(r.message);
					return;
				}
				frappe.show_alert({
					message: __("Trip status updated"),
					indicator: "green",
				});
			},
		});
	};
	if (confirm_message) {
		frappe.confirm(confirm_message, run);
		return;
	}
	run();
};

/** Which status actions to show for a trip row or form doc. */
haulage_mgmt.trip.status_actions_for = function (trip_status) {
	const status = trip_status || "Preparing";
	const actions = [];
	if (status === "Preparing" || status === "Paused") {
		actions.push({ action: "start", label: __("Start trip"), btn_class: "btn-primary" });
	}
	if (status === "Started") {
		actions.push({ action: "pause", label: __("Pause trip"), btn_class: "btn-default" });
	}
	if (status === "Started" || status === "Paused") {
		actions.push({
			action: "arrive",
			label: __("Trip arrival"),
			btn_class: "btn-success",
			confirm: __("Mark this trip as completed (arrival)?"),
		});
	}
	if (status !== "Completed" && status !== "Cancelled") {
		actions.push({
			action: "cancel",
			label: __("Cancel trip"),
			btn_class: "btn-danger",
			confirm: __("Cancel this trip? Linked shipping requests will return to Goods Prepared."),
		});
	}
	return actions;
};
