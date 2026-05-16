/* Redirect legacy entry route to trip operations hub (accounting view). */
frappe.pages["trip-accounting-entry"].on_page_load = function () {
	const trip = (frappe.route_options && frappe.route_options.trip) || null;
	if (trip) {
		frappe.route_options = { haulage_accounting_entry: 1 };
		frappe.set_route("Form", "Haulage Trip", trip);
		return;
	}
	frappe.route_options = { view: "accounting" };
	frappe.set_route("trip-operations");
};
