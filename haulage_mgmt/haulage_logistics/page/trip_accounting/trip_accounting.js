/* Legacy route — trip accounting lives under trip-operations (section 2). */
frappe.pages["trip-accounting"].on_page_load = function () {
	frappe.route_options = { view: "accounting" };
	frappe.set_route("trip-operations");
};
